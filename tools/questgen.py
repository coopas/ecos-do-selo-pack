"""Gera as quests do FTB Quests (SNBT) a partir de quests/src/*.yaml.

Formatos de campo lidos do jar do FTB Quests 2001 (ver quests/FORMAT.md) e do item-filtro do
FTB Filter System (descoberto em jogo com makeTagFilter: tests/fixtures/tag_filter.json).
"""
import hashlib
import json
import shutil
from dataclasses import dataclass, field
from pathlib import Path

import yaml

import snbt
from paths import PACK, ROOT

SRC = ROOT / "quests" / "src"
OUT = PACK / "config" / "ftbquests" / "quests"
QUEST_TAGS = PACK / "kubejs" / "ecos" / "quest_tags.json"
COIN = "ecos:fragmento_eco"
GROUPS = {"atos": "Atos", "caminhos": "Caminhos", "loja": "Loja", "diario": "Diário"}


class QuestError(ValueError):
    pass


def quest_id(path: str) -> str:
    """16 hex determinísticos; bit mais alto zerado (long positivo no FTB Quests)."""
    n = int(hashlib.sha1(path.encode("utf-8")).hexdigest()[:16], 16) & 0x7FFFFFFFFFFFFFFF
    return f"{n or 1:016X}"


@dataclass
class Chapter:
    slug: str
    title: str
    icon: str
    group: str
    act: int
    quests: list = field(default_factory=list)
    order: int = 0

    @classmethod
    def from_dict(cls, d: dict, order: int = 0) -> "Chapter":
        return cls(d["chapter"], d["title"], d["icon"], d.get("group", "atos"), int(d.get("act", 0)),
                   list(d.get("quests", [])), order)


def load_sources(directory: Path = SRC) -> list[Chapter]:
    files = sorted(directory.glob("*.yaml"))
    return [Chapter.from_dict(yaml.safe_load(f.read_text(encoding="utf-8")), i) for i, f in enumerate(files)]


def item_stack(item_id: str) -> dict:
    return {"Count": snbt.Byte(1), "id": item_id}


def tag_filter_stack(tag: str) -> dict:
    return {"Count": snbt.Byte(1), "id": "ftbfiltersystem:smart_filter",
            "tag": {"ftbfiltersystem:filter": f"ftbfiltersystem:item_tag({tag})"}}


def _task(t: dict, tid: str) -> dict:
    if "item" in t:
        return {"id": tid, "type": "item", "item": item_stack(t["item"]), "count": snbt.Long(t.get("count", 1))}
    if "tag" in t:
        return {"id": tid, "type": "item", "item": tag_filter_stack(t["tag"]), "count": snbt.Long(t.get("count", 1))}
    if "kill" in t:
        return {"id": tid, "type": "kill", "entity": t["kill"], "value": snbt.Long(t.get("count", 1))}
    if "dimension" in t:
        return {"id": tid, "type": "dimension", "dimension": t["dimension"]}
    if t.get("checkmark"):
        return {"id": tid, "type": "checkmark"}
    raise QuestError(f"task desconhecida: {t}")


def table_long(table_slug: str) -> snbt.Long:
    return snbt.Long(int(quest_id(f"table:{table_slug}"), 16))


def _reward(r: dict, rid: str, tables: dict) -> dict:
    if "coins" in r:
        return {"id": rid, "type": "item", "item": item_stack(COIN), "count": int(r["coins"])}
    if "item" in r:
        return {"id": rid, "type": "item", "item": item_stack(r["item"]), "count": int(r.get("count", 1))}
    if "xp_levels" in r:
        return {"id": rid, "type": "xp_levels", "xp_levels": int(r["xp_levels"])}
    if "loot" in r:
        if r["loot"] not in tables:
            raise QuestError(f"reward table desconhecida: {r['loot']}")
        return {"id": rid, "type": "loot", "table_id": table_long(r["loot"])}
    raise QuestError(f"recompensa desconhecida: {r}")


def resolve_dep(dep: str, chapter: str, known: set[str]) -> str:
    path = dep if "/" in dep else f"{chapter}/{dep}"
    if path not in known:
        raise QuestError(f"dependência inexistente: {dep} (em {chapter})")
    return path


def all_paths(chapters: list[Chapter]) -> set[str]:
    return {f"{c.slug}/{q['slug']}" for c in chapters for q in c.quests}


def used_tags(chapters: list[Chapter]) -> set[str]:
    return {t["tag"] for c in chapters for q in c.quests for t in q.get("tasks", []) if "tag" in t}


def build(chapters: list[Chapter], tables: dict) -> dict[str, str]:
    known = all_paths(chapters)
    files: dict[str, str] = {}
    groups = sorted({c.group for c in chapters})
    files["chapter_groups.snbt"] = snbt.dumps({"chapter_groups": [
        {"id": quest_id(f"group:{g}"), "title": GROUPS.get(g, g)} for g in groups]}) + "\n"
    files["data.snbt"] = snbt.dumps({
        "version": 13, "title": "Ecos do Selo", "icon": "ecos:artefato_selo",
        "default_reward_team": False, "default_consume_items": False, "default_quest_shape": "circle",
        "progression_mode": "linear", "show_lock_icons": True, "drop_loot_crates": False,
    }) + "\n"
    for c in chapters:
        quests = []
        for q in c.quests:
            path = f"{c.slug}/{q['slug']}"
            quest = {
                "id": quest_id(path), "title": q["title"], "description": list(q.get("desc", [])),
                "x": float(q.get("x", 0)), "y": float(q.get("y", 0)),
                "dependencies": [quest_id(resolve_dep(d, c.slug, known)) for d in q.get("deps", [])],
                "tasks": [_task(t, quest_id(f"{path}#t{i}")) for i, t in enumerate(q.get("tasks", []))],
                "rewards": [_reward(r, quest_id(f"{path}#r{i}"), tables) for i, r in enumerate(q.get("rewards", []))],
            }
            if q.get("shape"):
                quest["shape"] = q["shape"]
            if q.get("icon"):
                quest["icon"] = q["icon"]
            if q.get("repeatable"):
                quest["can_repeat"] = True
            quests.append(quest)
        files[f"chapters/{c.slug}.snbt"] = snbt.dumps({
            "id": quest_id(f"chapter:{c.slug}"), "group": quest_id(f"group:{c.group}"), "order_index": c.order,
            "filename": c.slug, "title": c.title, "icon": c.icon, "default_quest_shape": "",
            "default_hide_dependency_lines": False, "quests": quests, "quest_links": [], "images": [],
        }) + "\n"
    return files


def write(out: Path = OUT, chapters: list[Chapter] | None = None, tables: dict | None = None) -> int:
    chapters = load_sources() if chapters is None else chapters
    files = build(chapters, tables or {})
    if out.exists():
        shutil.rmtree(out)
    for rel, text in files.items():
        p = out / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    QUEST_TAGS.write_text(json.dumps({"tags": sorted(used_tags(chapters))}, indent=1) + "\n", encoding="utf-8")
    return sum(len(c.quests) for c in chapters)


if __name__ == "__main__":
    n = write()
    print(f"{n} quests geradas em {OUT}")
