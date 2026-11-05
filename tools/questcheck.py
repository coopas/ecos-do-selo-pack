"""Valida as quests (quests/src/*.yaml) contra os dumps reais do jogo.

Estrutural (check/main_check): IDs existem; task não exige variante específica quando há tag (pedido do usuário:
"qualquer cama"); grafo sem ciclo e tudo alcançável a partir do Prólogo; ordem dos atos; recompensa e texto curto.

Jornada (check_progress/main_progress): cada quest é julgada no ponto em que o jogador está, com o motor de fecho
(tools/closure.py). Dimensões abertas = Overworld + as de dimension_unlocks cuja quest é ancestral, a própria quest
ou de um capítulo de ato menor (nada trava a dimensão; ramo de ato anterior já pode ter sido feito); seed = itens de task e recompensas dos ancestrais + drops de chefe das tasks de kill ancestrais +
boss_quest_drops. Erro: item/tag fora do fecho. Aviso: só por veio fundo antes de deep_ok_from_act, ou só por receita
do GregTech acima do act_tier do ato.

CLI: python tools/questcheck.py [--relatorio] imprime os dois e sai 1 com erro estrutural ou de jornada (aviso não
falha). --relatorio grava build/questcheck_progresso.txt (por capítulo, na ordem das quests: "nível | path | msg").
"""
import argparse
import dataclasses
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

import closure
import ecosdata
import progression
import questgen
import recipes
import registry
from paths import BUILD, ROOT

START = "prologo/despertar"
MAX_DESC_LINES = 4
NATURALS = ROOT / "quests" / "naturals.yaml"
VARIANTS = ROOT / "quests" / "variant_tags.yaml"
PROGRESSION = ROOT / "quests" / "progression.yaml"
REPORT = BUILD / "questcheck_progresso.txt"
OVERWORLD = "minecraft:overworld"


@dataclass(frozen=True)
class Finding:
    path: str
    level: str  # "erro" | "aviso"
    msg: str

    def __str__(self) -> str:
        return f"{self.path}: {self.msg}"


def _reward_items(quest: dict) -> set[str]:
    out = set()
    for r in quest.get("rewards", []):
        if "item" in r:
            out.add(r["item"])
        if "coins" in r:
            out.add(questgen.COIN)
    return out


def _texture_exists(rl: str) -> bool:
    from paths import PACK
    ns, path = rl.split(":", 1)
    return (PACK / "kubejs" / "assets" / ns / path).exists()


def _icon_errors(chapters, reg) -> list[str]:
    """Ícones de capítulo/quest e artes: item que existe no registro ou imagem que existe no resource pack."""
    errs = []
    def ok(icon: str) -> bool:
        return _texture_exists(icon) if icon.endswith(".png") else icon in reg.items
    for c in chapters:
        if not ok(c.icon):
            errs.append(f"{c.slug}: ícone do capítulo {c.icon} não existe")
        for q in c.quests:
            if q.get("icon") and not ok(q["icon"]):
                errs.append(f"{c.slug}/{q['slug']}: ícone {q['icon']} não existe")
            if q.get("image") and not _texture_exists(q["image"]):
                errs.append(f"{c.slug}/{q['slug']}: imagem {q['image']} não existe")
    return errs


def _graph(chapters, errs: list[str] | None = None):
    """(path -> (capítulo, quest), path -> [deps resolvidas]); dep que não resolve vai para errs."""
    quests = {f"{c.slug}/{q['slug']}": (c, q) for c in chapters for q in c.quests}
    known = set(quests)
    deps: dict[str, list[str]] = {}
    for path, (c, q) in quests.items():
        deps[path] = []
        for d in q.get("deps", []):
            try:
                deps[path].append(questgen.resolve_dep(d, c.slug, known))
            except questgen.QuestError as e:
                if errs is not None:
                    errs.append(f"{path}: {e}")
    return quests, deps


def check(chapters, reg, rec, naturals: dict, variant_tags: list[str], boss_drops: dict, prog=None) -> list[str]:
    """Erros estruturais; com `prog`, também os erros de jornada (check_progress) como "<path>: <msg>"."""
    errs: list[str] = []
    errs += _icon_errors(chapters, reg)
    quests, deps = _graph(chapters, errs)

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
            elif "tag" in t:
                tag = t["tag"]
                if not reg.has_tag(tag):
                    errs.append(f"{path}: tag #{tag} não existe")
            elif "kill" in t and not reg.has_entity(t["kill"]):
                errs.append(f"{path}: entidade {t['kill']} não existe")
            elif "dimension" in t and t["dimension"] not in reg.dimensions:
                errs.append(f"{path}: dimensão {t['dimension']} não existe")
        for r in q.get("rewards", []):
            if "item" in r and not reg.has_item(r["item"]):
                errs.append(f"{path}: recompensa {r['item']} não existe")
    if prog is not None:
        errs += [str(f) for f in check_progress(chapters, reg, rec, prog, naturals, boss_drops) if f.level == "erro"]
    return errs


# ---------- jornada ----------

def _topo(quests: dict, deps: dict) -> list[str]:
    """Ordem topológica (Kahn) seguindo a ordem das quests; quem está em ciclo fica de fora (o estrutural acusa)."""
    indeg = {n: len(set(deps[n])) for n in quests}
    dependents: dict[str, list[str]] = {n: [] for n in quests}
    for n in quests:
        for d in set(deps[n]):
            dependents[d].append(n)
    ready = [n for n in quests if indeg[n] == 0]
    out = []
    while ready:
        n = ready.pop(0)
        out.append(n)
        for m in dependents[n]:
            indeg[m] -= 1
            if indeg[m] == 0:
                ready.append(m)
    return out


def _tier_name(tier) -> str:
    return "sem GregTech elétrico" if tier == "none" else str(tier).upper()


def check_progress(chapters, reg, rec, prog, naturals: dict | None = None,
                   boss_drops: dict | None = None) -> list[Finding]:
    """Julga cada quest no ponto da jornada (ver docstring do módulo). Achados na ordem dos capítulos e das quests.

    `naturals` substitui prog.naturals quando dado; `boss_drops` = entidade -> item (ecosdata)."""
    if naturals is not None and naturals is not prog.naturals:
        prog = dataclasses.replace(prog, naturals=naturals)
    boss_drops = boss_drops or {}
    idx = closure.index_for(prog, rec, reg)
    quests, deps = _graph(chapters)
    order = _topo(quests, deps)
    unlock_of = dict(prog.dimension_unlocks)
    opens: dict[str, set[str]] = {}
    for dim, qpath in unlock_of.items():
        opens.setdefault(qpath, set()).add(dim)
    # nada no jogo trava a dimensão além da própria quest: um ramo de ato anterior já pode ter sido feito
    unlock_act = {d: quests[qp][0].act for d, qp in unlock_of.items() if qp in quests}

    gains: dict[str, set[str]] = {}  # o que a quest deixa na mão de quem vem depois
    gdims: dict[str, set[str]] = {}  # dimensões que ela abre
    for path, (c, q) in quests.items():
        g = _reward_items(q) | set(prog.boss_quest_drops.get(path, []))
        dims = set(opens.get(path, ()))
        for t in q.get("tasks", []):
            if "item" in t:
                g.add(t["item"])
            elif "kill" in t and t["kill"] in boss_drops:
                g.add(boss_drops[t["kill"]])
            elif "dimension" in t and t["dimension"] not in unlock_of:
                dims.add(t["dimension"])  # dimensão sem trava (sem quest em dimension_unlocks): abre ao visitar
        gains[path], gdims[path] = g, dims

    anc: dict[str, set[str]] = {}
    for n in order:
        a: set[str] = set()
        for d in deps[n]:
            a |= anc[d] | {d}
        anc[n] = a

    base: dict[tuple, closure.Reach] = {}
    memo: dict[tuple, closure.Reach] = {}

    def reach(seed: set[str], dims: frozenset, deep_ok: bool = True, cap: float = closure.INF) -> closure.Reach:
        flags = (dims, deep_ok, cap)
        if flags not in base:
            base[flags] = closure.reach(set(), set(dims), prog, rec, reg, exclude_deep=not deep_ok, max_eut=cap,
                                        index=idx)
        rest = frozenset(seed - base[flags].items)  # o que já sai do mundo não muda o fecho
        if not rest:
            return base[flags]
        key = (rest, flags)
        if key not in memo:
            memo[key] = closure.reach(set(rest), set(dims), prog, rec, reg, exclude_deep=not deep_ok, max_eut=cap,
                                      index=idx)
        return memo[key]

    found: dict[str, list[Finding]] = {}
    for path in order:
        c, q = quests[path]
        here = anc[path] | {path}
        dims = frozenset({OVERWORLD} | {d for a in here for d in gdims[a]}
                         | {d for d, act in unlock_act.items() if act < c.act})
        seed = set(prog.boss_quest_drops.get(path, []))
        for a in anc[path]:
            seed |= gains[a]
        tier = prog.act_tier.get(c.act)
        cap = closure.max_eut_for(tier) if tier is not None else closure.INF
        out: list[Finding] = []
        r = None
        for t in q.get("tasks", []):
            if "dimension" in t:
                d = t["dimension"]
                if d in unlock_of and d not in dims:
                    out.append(Finding(path, "erro", f"dimensão {d} ainda fechada neste ponto (abre em {unlock_of[d]})"))
                continue
            if "item" in t:
                if not reg.has_item(t["item"]):
                    continue  # o estrutural acusa
                label, members = t["item"], {t["item"]}
            elif "tag" in t:
                if not reg.has_tag(t["tag"]):
                    continue
                label, members = "#" + t["tag"].lstrip("#"), set(reg.tag_items(t["tag"]))
            else:
                continue
            r = r or reach(seed, dims)
            if members.isdisjoint(r.items):
                why = closure.explain(label, r, set(dims), prog, rec, reg, index=idx)
                out.append(Finding(path, "erro", f"{label} impossível neste ponto (falta: {why})"))
                continue
            if c.act < prog.deep_ok_from_act and members.isdisjoint(reach(seed, dims, deep_ok=False).items):
                out.append(Finding(path, "aviso", f"{label} só vem de veio fundo (y < 0) neste ponto; o fundo do "
                                                  f"deepslate é esperado a partir do ato {prog.deep_ok_from_act}"))
            if cap < closure.INF:
                rc = reach(seed, dims, cap=cap)
                if members.isdisjoint(rc.items):
                    why = closure.explain(label, rc, set(dims), prog, rec, reg, index=idx, max_eut=cap)
                    out.append(Finding(path, "aviso", f"{label} só sai com receita do GregTech acima do esperado no "
                                                      f"ato {c.act} ({_tier_name(tier)}): {why}"))
        found[path] = out
    return [f for path in quests for f in found.get(path, [])]


def write_report(chapters, findings: list[Finding], out: Path = REPORT) -> None:
    """Relatório da revisão: um bloco por capítulo (ordem dos capítulos e das quests), linha "nível | path | msg"."""
    by_path: dict[str, list[Finding]] = {}
    for f in findings:
        by_path.setdefault(f.path, []).append(f)
    lines: list[str] = []
    total = {"erro": 0, "aviso": 0}
    for c in chapters:
        fs = [f for q in c.quests for f in by_path.get(f"{c.slug}/{q['slug']}", [])]
        if not fs:
            continue
        n = {lv: sum(f.level == lv for f in fs) for lv in total}
        for lv in total:
            total[lv] += n[lv]
        lines.append(f"== {c.slug}: {c.title} (ato {c.act}) — {n['erro']} erros, {n['aviso']} avisos ==")
        lines += [f"{f.level} | {f.path} | {f.msg}" for f in fs]
        lines.append("")
    lines.append(f"Total: {total['erro']} erros, {total['aviso']} avisos")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")


# ---------- pack real ----------

_LOADED: dict = {}


def _load():
    """Fontes, dumps e progressão do pack real (os dumps são lidos uma vez por processo)."""
    if "reg" not in _LOADED:
        _LOADED["reg"] = registry.load(BUILD / "registry_dump.json")
        _LOADED["rec"] = recipes.load(BUILD / "recipe_dump.json")
    return questgen.load_sources(), _LOADED["reg"], _LOADED["rec"], progression.load(PROGRESSION, NATURALS)


def main_check() -> list[str]:
    """Só os erros estruturais do pack real."""
    variants = yaml.safe_load(VARIANTS.read_text(encoding="utf-8")) or []
    chapters, reg, rec, prog = _load()
    return check(chapters, reg, rec, prog.naturals, variants, ecosdata.load().boss_drops)


def main_progress() -> list[Finding]:
    """Achados de jornada do pack real."""
    chapters, reg, rec, prog = _load()
    return check_progress(chapters, reg, rec, prog, prog.naturals, ecosdata.load().boss_drops)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Valida as quests (estrutura e jornada do jogador).")
    ap.add_argument("--relatorio", action="store_true", help="grava build/questcheck_progresso.txt")
    args = ap.parse_args(argv)
    problems = main_check()
    for p in problems:
        print(p)
    findings = main_progress()
    for f in findings:
        print(f"{f.level}: {f}")
    n_err = sum(f.level == "erro" for f in findings)
    if args.relatorio:
        write_report(questgen.load_sources(), findings)
        print(f"relatório: {REPORT}")
    print(f"estrutural: {'OK' if not problems else f'{len(problems)} problemas'}; "
          f"jornada: {n_err} erros, {len(findings) - n_err} avisos")
    return 1 if problems or n_err else 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
