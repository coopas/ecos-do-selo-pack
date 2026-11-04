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
TABLES_SRC = ROOT / "quests" / "reward_tables.yaml"
LORE = ROOT / "docs" / "lore.md"
BOOK_PAGE_CHARS = 230
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


def item_stack(item_id: str, tag: dict | None = None) -> dict:
    stack = {"Count": snbt.Byte(1), "id": item_id}
    if tag:
        stack["tag"] = tag
    return stack


def lore_pages() -> dict[int, str]:
    import re
    parts = re.split(r"^### Página (\d+)[^\n]*\n", LORE.read_text(encoding="utf-8"), flags=re.M)
    pages = {}
    for i in range(1, len(parts), 2):
        body = parts[i + 1].split("\n## ")[0].strip()
        pages[int(parts[i])] = body
    return pages


def diary_book(n: int) -> dict:
    """Página n da lore (docs/lore.md) como livro escrito de Ilse Varrow."""
    text = lore_pages()[n]
    chunks, current = [], ""
    for line in text.splitlines():
        if current and len(current) + len(line) + 1 > BOOK_PAGE_CHARS:
            chunks.append(current)
            current = line
        else:
            current = f"{current}\n{line}" if current else line
    chunks.append(current)
    return item_stack("minecraft:written_book", {
        "title": f"Diário — Página {n}", "author": "Ilse Varrow", "generation": 0,
        "pages": [json.dumps({"text": c}, ensure_ascii=False) for c in chunks]})


def crate_stack(table_slug: str) -> dict:
    return item_stack("ftbquests:lootcrate", {"type": table_slug})


def load_tables(path: Path = TABLES_SRC) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) if path.exists() else {}


def build_table(slug: str, t: dict) -> dict:
    return {
        "id": quest_id(f"table:{slug}"), "title": t["title"], "filename": slug, "icon": "ftbquests:lootcrate",
        "loot_size": int(t.get("loot_size", 1)), "empty_weight": snbt.Float(0.0), "use_title": True,
        "rewards": [{"id": quest_id(f"table:{slug}#e{i}"), "type": "item", "item": item_stack(e["item"]),
                     "count": int(e.get("count", 1)), "weight": snbt.Float(float(e["weight"]))}
                    for i, e in enumerate(t["entries"])],
        "loot_crate": {"string_id": slug, "item_name": t["title"], "color": int(t["color"]), "glow": slug != "comum",
                       "drops": {"passive": 0, "monster": 0, "boss": 0}},
    }


def tag_filter_stack(tag: str) -> dict:
    return {"Count": snbt.Byte(1), "id": "ftbfiltersystem:smart_filter",
            "tag": {"ftbfiltersystem:filter": f"ftbfiltersystem:item_tag({tag})"}}


def _task(t: dict, tid: str) -> dict:
    if "item" in t:
        task = {"id": tid, "type": "item", "item": item_stack(t["item"]), "count": snbt.Long(t.get("count", 1))}
        if t.get("consume"):
            task["consume_items"] = True
        return task
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
    if "crate" in r:
        if r["crate"] not in tables:
            raise QuestError(f"caixa desconhecida: {r['crate']}")
        return {"id": rid, "type": "item", "item": crate_stack(r["crate"]), "count": int(r.get("count", 1))}
    if "page" in r:
        return {"id": rid, "type": "item", "item": diary_book(int(r["page"])), "count": 1}
    if "loot" in r:
        if r["loot"] not in tables:
            raise QuestError(f"reward table desconhecida: {r['loot']}")
        return {"id": rid, "type": "loot", "table_id": table_long(r["loot"])}
    raise QuestError(f"recompensa desconhecida: {r}")


GRID = 1.5


def layout(c: "Chapter") -> dict[str, tuple[float, float]]:
    """Posição de cada quest: x/y explícitos vencem; senão coluna = profundidade de dependência local,
    linha = ordem dentro da coluna (centralizada)."""
    local = {q["slug"]: [d for d in q.get("deps", []) if "/" not in d] for q in c.quests}
    depth: dict[str, int] = {}

    def d(slug: str, seen=()) -> int:
        if slug in depth:
            return depth[slug]
        if slug in seen:
            return 0
        parents = [p for p in local.get(slug, []) if p in local]
        depth[slug] = 0 if not parents else 1 + max(d(p, seen + (slug,)) for p in parents)
        return depth[slug]

    columns: dict[int, list[str]] = {}
    for q in c.quests:
        columns.setdefault(d(q["slug"]), []).append(q["slug"])
    pos = {}
    for col, slugs in columns.items():
        for i, slug in enumerate(slugs):
            pos[slug] = (col * GRID, (i - (len(slugs) - 1) / 2) * GRID)
    for q in c.quests:
        if "x" in q and "y" in q:
            pos[q["slug"]] = (float(q["x"]), float(q["y"]))
    return pos


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
    for slug, t in tables.items():
        files[f"reward_tables/{slug}.snbt"] = snbt.dumps(build_table(slug, t)) + "\n"
    for c in chapters:
        quests = []
        pos = layout(c)
        for q in c.quests:
            path = f"{c.slug}/{q['slug']}"
            quest = {
                "id": quest_id(path), "title": q["title"], "description": list(q.get("desc", [])),
                "x": pos[q["slug"]][0], "y": pos[q["slug"]][1],
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
    files = build(chapters, load_tables() if tables is None else tables)
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
