"""Layout do livro de quests: sem linhas de dependência cruzando e sem linha passando por cima de quest."""
import pytest

import layoutcheck
import questgen

def chapter(quests, slug="cap"):
    return questgen.Chapter.from_dict({"chapter": slug, "title": "T", "icon": "minecraft:stone", "group": "atos",
                                       "act": 0, "quests": quests})


def q(slug, deps=()):
    return {"slug": slug, "title": slug, "deps": list(deps), "tasks": [{"checkmark": True}]}


def test_crossing_counter():
    c = chapter([q("a"), q("b"), q("c", ["b"]), q("d", ["a"])])
    pos = {"a": (0, 0), "b": (0, 2), "c": (2, 0), "d": (2, 2)}
    assert layoutcheck.crossings(c, pos) == 1
    pos_ok = {"a": (0, 0), "b": (0, 2), "c": (2, 2), "d": (2, 0)}
    assert layoutcheck.crossings(c, pos_ok) == 0


def test_shared_endpoint_is_not_a_crossing():
    c = chapter([q("a"), q("b", ["a"]), q("c", ["a"])])
    assert layoutcheck.crossings(c, {"a": (0, 0), "b": (2, 1), "c": (2, -1)}) == 0


def test_line_over_quest_counter():
    c = chapter([q("a"), q("b"), q("c", ["a"])])
    pos = {"a": (0, 0), "b": (1.5, 0.2), "c": (3, 0)}
    assert layoutcheck.lines_over_quests(c, pos) == 1
    pos["b"] = (1.5, 2)
    assert layoutcheck.lines_over_quests(c, pos) == 0


def test_cross_chapter_dep_not_counted():
    c = chapter([q("a"), q("b"), q("c", ["b", "outro/x"]), q("d", ["a", "outro/y"])])
    pos = {"a": (0, 0), "b": (0, 2), "c": (2, 0), "d": (2, 2)}
    assert layoutcheck.crossings(c, pos) == 1
    c2 = chapter([q("a"), q("b", ["outro/a"])])
    assert layoutcheck.crossings(c2, {"a": (0, 0), "b": (2, 0)}) == 0
    assert layoutcheck.lines_over_quests(chapter([q("a"), q("b"), q("c", ["outro/a"])]),
                                         {"a": (0, 0), "b": (1.5, 0), "c": (3, 0)}) == 0


def test_layout_long_edge_does_not_cross_quest():
    # a->b->c->d e a->d: a aresta longa não pode passar por b nem c.
    c = chapter([q("a"), q("b", ["a"]), q("c", ["b"]), q("d", ["c", "a"])])
    pos = questgen.layout(c)
    assert layoutcheck.lines_over_quests(c, pos) == 0
    assert pos["a"][0] < pos["b"][0] < pos["c"][0] < pos["d"][0]


@pytest.mark.parametrize("c", questgen.load_sources(), ids=lambda c: c.slug)
def test_all_chapters_clean(c):
    pos = questgen.layout(c)
    lim = layoutcheck.limits(c.slug)
    assert layoutcheck.crossings(c, pos) <= lim[0]
    assert layoutcheck.lines_over_quests(c, pos) <= lim[1]
    assert layoutcheck.long_edges(c, pos) <= lim[2]
    assert layoutcheck.max_edge_length(c, pos) <= lim[3]


@pytest.mark.parametrize("c", [c for c in questgen.load_sources() if not any("x" in q for q in c.quests)],
                         ids=lambda c: c.slug)
def test_auto_layout_reads_left_to_right(c):
    pos = questgen.layout(c)
    slugs = {q["slug"] for q in c.quests}
    for q in c.quests:
        for d in q.get("deps", []):
            if d in slugs:
                assert pos[d][0] < pos[q["slug"]][0], (d, q["slug"])
        kids = [k["slug"] for k in c.quests if q["slug"] in k.get("deps", [])]
        if not any(d in slugs for d in q.get("deps", [])):
            # sem dependência local: coluna 0, ou logo antes do filho mais próximo se ele está longe
            near_kid = min((pos[k][0] for k in kids), default=None)
            assert pos[q["slug"]][0] == 0 or pos[q["slug"]][0] == near_kid - questgen.GRID, q["slug"]


def test_long_edges_counter():
    c = chapter([q("a"), q("b", ["a"]), q("c", ["a"])])
    pos = {"a": (0, 0), "b": (3, 0), "c": (12, 0)}
    assert layoutcheck.long_edges(c, pos, max_len=10.5) == 1
    assert layoutcheck.long_edges(c, pos, max_len=12) == 0
    assert layoutcheck.max_edge_length(c, pos) == 12
    assert layoutcheck.limits("sem_entrada") == (0, 0, 0, layoutcheck.MAX_EDGE)


def test_no_redundant_local_dependency():
    """Dep local D de Q é redundante se D já é ancestral de outra dep de Q (o FTB exige as deps em cadeia): só
    desenharia mais uma linha. Ancestrais pelo grafo inteiro, deps entre capítulos incluídas."""
    chapters = questgen.load_sources()
    deps = {f"{c.slug}/{x['slug']}": [d if "/" in d else f"{c.slug}/{d}" for d in x.get("deps", [])]
            for c in chapters for x in c.quests}
    memo: dict[str, set] = {}

    def anc(p):
        if p not in memo:
            memo[p] = set()
            memo[p] = {a for d in deps.get(p, []) for a in {d} | anc(d)}
        return memo[p]

    bad = [(p, d) for p, ds in deps.items() for d in ds
           if d.split("/")[0] == p.split("/")[0] and any(d in anc(e) for e in ds if e != d)]
    assert bad == []
