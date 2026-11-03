"""Valida as quests (quests/src/*.yaml) contra os dumps reais do jogo.

Regras: IDs existem; item é obtível (receita no dump, natural, drop de chefe ou recompensa de quest
anterior); task não exige variante específica quando há tag (pedido do usuário: "qualquer cama");
grafo sem ciclo e tudo alcançável a partir do Prólogo; ordem dos atos; recompensa e texto curto.
"""
import sys
from pathlib import Path

import yaml

import ecosdata
import questgen
import recipes
import registry
from paths import BUILD, ROOT

START = "prologo/despertar"
MAX_DESC_LINES = 4
NATURALS = ROOT / "quests" / "naturals.yaml"
VARIANTS = ROOT / "quests" / "variant_tags.yaml"


def _flatten(naturals: dict, reg) -> set[str]:
    out = set()
    for items in naturals.values():
        for i in items or []:
            out |= reg.tag_items(i) if i.startswith("#") else {i}
    return out


def _reward_items(quest: dict) -> set[str]:
    out = set()
    for r in quest.get("rewards", []):
        if "item" in r:
            out.add(r["item"])
        if "coins" in r:
            out.add(questgen.COIN)
    return out


def check(chapters, reg, rec, naturals: dict, variant_tags: list[str], boss_drops: dict) -> list[str]:
    errs: list[str] = []
    natural = _flatten(naturals, reg) | set(boss_drops.values())
    quests = {f"{c.slug}/{q['slug']}": (c, q) for c in chapters for q in c.quests}
    known = set(quests)

    deps: dict[str, list[str]] = {}
    for path, (c, q) in quests.items():
        deps[path] = []
        for d in q.get("deps", []):
            try:
                deps[path].append(questgen.resolve_dep(d, c.slug, known))
            except questgen.QuestError as e:
                errs.append(f"{path}: {e}")

    # ciclos (DFS com cores)
    color: dict[str, int] = {}
    has_cycle = False

    def visit(n: str, stack: list[str]):
        nonlocal has_cycle
        color[n] = 1
        for m in deps.get(n, []):
            if color.get(m) == 1:
                has_cycle = True
                errs.append(f"ciclo de dependências: {' -> '.join(stack + [n, m])}")
            elif color.get(m) is None:
                visit(m, stack + [n])
        color[n] = 2

    for n in quests:
        if color.get(n) is None:
            visit(n, [])

    # alcançabilidade a partir do início (seguindo dependentes)
    dependents: dict[str, set[str]] = {n: set() for n in quests}
    for n, ds in deps.items():
        for d in ds:
            dependents.setdefault(d, set()).add(n)
    if START not in quests:
        errs.append(f"quest inicial {START} não existe")
    else:
        seen, todo = {START}, [START]
        while todo:
            for m in dependents.get(todo.pop(), ()):
                if m not in seen and all(d in seen or d == m for d in deps[m]):
                    seen.add(m)
                    todo.append(m)
        for n in quests:
            if n not in seen:
                errs.append(f"{n}: inalcançável a partir de {START}")

    def ancestors(n: str) -> set[str]:
        out, todo = set(), list(deps.get(n, []))
        while todo:
            m = todo.pop()
            if m not in out:
                out.add(m)
                todo.extend(deps.get(m, []))
        return out

    def obtainable(item: str, path: str) -> bool:
        if rec.for_output(item) or item in natural:
            return True
        return any(item in _reward_items(quests[a][1]) for a in (ancestors(path) if not has_cycle else ()))

    variant_members = {t: reg.tag_items(t) for t in variant_tags}

    for path, (c, q) in quests.items():
        if not q.get("title"):
            errs.append(f"{path}: sem título")
        desc = q.get("desc", [])
        if not desc:
            errs.append(f"{path}: sem descrição")
        if len(desc) > MAX_DESC_LINES:
            errs.append(f"{path}: descrição com {len(desc)} linhas (máx {MAX_DESC_LINES}; use página de diário)")
        if not q.get("rewards"):
            errs.append(f"{path}: sem recompensa")
        for d in deps.get(path, []):
            dc = quests[d][0]
            if dc.act > c.act:
                errs.append(f"{path}: viola ordem dos atos (ato {c.act} depende de {d}, ato {dc.act})")
        for t in q.get("tasks", []):
            if "item" in t:
                item = t["item"]
                if not reg.has_item(item):
                    errs.append(f"{path}: item {item} não existe")
                    continue
                if not q.get("allow_exact"):
                    for tag, members in variant_members.items():
                        if item in members:
                            errs.append(f"{path}: {item} é variante; use a tag #{tag} (ou allow_exact com motivo)")
                if not obtainable(item, path):
                    errs.append(f"{path}: {item} não é obtível (sem receita, não é natural nem recompensa anterior)")
            elif "tag" in t:
                tag = t["tag"]
                if not reg.has_tag(tag):
                    errs.append(f"{path}: tag #{tag} não existe")
                elif not any(rec.for_output(m) or m in natural for m in reg.tag_items(tag)):
                    errs.append(f"{path}: nenhum item da tag #{tag} é obtível")
            elif "kill" in t and not reg.has_entity(t["kill"]):
                errs.append(f"{path}: entidade {t['kill']} não existe")
            elif "dimension" in t and t["dimension"] not in reg.dimensions:
                errs.append(f"{path}: dimensão {t['dimension']} não existe")
        for r in q.get("rewards", []):
            if "item" in r and not reg.has_item(r["item"]):
                errs.append(f"{path}: recompensa {r['item']} não existe")
    return errs


def main_check() -> list[str]:
    naturals = yaml.safe_load(NATURALS.read_text(encoding="utf-8")) or {}
    variants = yaml.safe_load(VARIANTS.read_text(encoding="utf-8")) or []
    return check(questgen.load_sources(), registry.load(BUILD / "registry_dump.json"),
                 recipes.load(BUILD / "recipe_dump.json"), naturals, variants, ecosdata.load().boss_drops)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    problems = main_check()
    for p in problems:
        print(p)
    print("OK" if not problems else f"{len(problems)} problemas")
    sys.exit(1 if problems else 0)
