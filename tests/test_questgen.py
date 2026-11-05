import json
from pathlib import Path

import pytest

import questgen
import snbt
from paths import BUILD

FIX = Path(__file__).parent / "fixtures"


def chapter(quests, slug="cap", act=0):
    return questgen.Chapter.from_dict({"chapter": slug, "title": "T", "icon": "minecraft:stone", "group": "atos",
                                       "act": act, "quests": quests})


def q(slug, **kw):
    base = {"slug": slug, "title": slug, "desc": ["d"], "x": 0, "y": 0, "tasks": [{"checkmark": True}],
            "rewards": [{"xp_levels": 1}]}
    base.update(kw)
    return base


def test_quest_id_stable():
    assert questgen.quest_id("a/b") == questgen.quest_id("a/b")
    assert questgen.quest_id("a/b") != questgen.quest_id("a/c")
    assert len(questgen.quest_id("a/b")) == 16 and questgen.quest_id("a/b") == questgen.quest_id("a/b").upper()


def test_tag_task_uses_filter_item():
    fixture = json.loads((FIX / "tag_filter.json").read_text())
    stack = questgen.tag_filter_stack("minecraft:beds")
    assert stack["id"] == fixture["id"]
    assert stack["tag"] == fixture["tag"]
    assert snbt.dumps(stack["Count"]) == "1b"


def test_deps_resolve_local_and_cross_chapter():
    a = chapter([q("x")], slug="a")
    b = chapter([q("y", deps=["a/x"]), q("z", deps=["y"])], slug="b")
    files = questgen.build([a, b], {})
    text = files["chapters/b.snbt"]
    assert questgen.quest_id("a/x") in text and questgen.quest_id("b/y") in text


def test_cross_chapter_deps_are_named_in_description():
    """O FTB não desenha a linha de dependência entre capítulos: sem o aviso, a quest parece travada à toa."""
    a = questgen.Chapter.from_dict({"chapter": "a", "title": "Caminho A", "icon": "minecraft:stone", "group": "atos",
                                    "act": 0, "quests": [q("x", title="Engrenagem")]})
    b = chapter([q("y", title="Bronze", deps=["a/x"]), q("z", deps=["y", "a/x"]), q("w")], slug="b")
    text = questgen.build([a, b], {})["chapters/b.snbt"]
    assert '"Antes, conclua: «Engrenagem» (Caminho A)"' in text
    assert '"Antes, conclua: «Bronze», «Engrenagem» (Caminho A)"' in text   # mesmo capítulo vai sem o nome dele
    assert text.count("Antes, conclua") == 2                                 # w não tem dependência


def test_unknown_dep_raises():
    with pytest.raises(questgen.QuestError):
        questgen.build([chapter([q("y", deps=["nada"])])], {})


def test_ftbquests_loaded_counts():
    p = BUILD / "quest_selftest.json"
    if not p.exists():
        pytest.skip("sem selftest")
    d = json.loads(p.read_text(encoding="utf-8"))
    chapters = questgen.load_sources()
    assert d["chapters"] == len(chapters)
    assert len(d["quests"]) == sum(len(c.quests) for c in chapters)
    for c in chapters:
        for quest in c.quests:
            loaded = d["quests"][questgen.quest_id(questgen.id_base(c.slug, quest))]
            assert quest["title"] in loaded["quest"]
            assert len(loaded["tasks"]) == len(quest.get("tasks", []))
            assert len(loaded["rewards"]) == len(quest.get("rewards", []))


def test_tasks_and_rewards_roundtrip():
    p = BUILD / "quest_selftest.json"
    if not p.exists():
        pytest.skip("sem selftest")
    d = json.loads(p.read_text(encoding="utf-8"))
    for c in questgen.load_sources():
        for quest in c.quests:
            loaded = d["quests"][questgen.quest_id(questgen.id_base(c.slug, quest))]
            for src, got in zip(quest.get("tasks", []), loaded["tasks"]):
                if "item" in src:
                    assert src["item"] in got["data"], got
                if "tag" in src:
                    assert f"item_tag({src['tag']})" in got["data"], got
                if "kill" in src:
                    assert src["kill"] in got["data"], got
                if "dimension" in src:
                    assert src["dimension"] in got["data"], got
            for src, got in zip(quest.get("rewards", []), loaded["rewards"]):
                if "coins" in src:
                    assert questgen.COIN in got["data"], got
                if "loot" in src:
                    assert got["table_ok"] is True, got


def test_tag_filters_match_ingame():
    p = BUILD / "quest_selftest.json"
    if not p.exists():
        pytest.skip("sem selftest")
    d = json.loads(p.read_text(encoding="utf-8"))
    used = questgen.used_tags(questgen.load_sources())
    assert used <= set(d["filters"])
    for tag in used:
        f = d["filters"][tag]
        assert f["members_fail"] == [] and f["members_ok"] > 0 and f["outsider_matches"] is False, tag


def test_auto_layout_by_dependency_depth():
    c = chapter([q("a"), q("b", deps=["a"]), q("c", deps=["a"]), q("d", deps=["b", "c"])], slug="l")
    del c.quests[0]["x"], c.quests[0]["y"]
    for quest in c.quests:
        quest.pop("x", None)
        quest.pop("y", None)
    pos = questgen.layout(c)
    # coluna = profundidade local (GRID por coluna); y contínuo, irmãos separados por pelo menos uma quest
    assert [pos[s][0] for s in "abcd"] == [0, questgen.GRID, questgen.GRID, 2 * questgen.GRID]
    assert abs(pos["b"][1] - pos["c"][1]) >= 1.4


def test_explicit_position_wins():
    c = chapter([q("a", x=7, y=-3)], slug="l")
    assert questgen.layout(c)["a"] == (7.0, -3.0)


def test_tag_tasks_accept_members_ingame():
    """A task do FTB Quests (ItemTask.test) aceita um membro da tag e recusa pedra.
    Sem adaptador registrado, o FTB Quests compara com o próprio item smart_filter e nada casa."""
    import json
    from paths import BUILD
    p = BUILD / "quest_selftest.json"
    if not p.exists():
        pytest.skip("sem build/quest_selftest.json (rode o boot dev)")
    probes = json.loads(p.read_text(encoding="utf-8")).get("task_probes")
    assert probes, "selftest não testou as tasks"
    bad = {k: v for k, v in probes.items() if not v["member_ok"] or v["outsider_ok"]}
    assert not bad, list(bad.items())[:5]


def test_kill_tasks_map_boss_to_task_ids():
    """Mapa entidade → ids das tasks de kill, lido pelo script que credita todos os jogadores perto do chefe."""
    m = questgen.kill_tasks(questgen.load_sources())
    assert questgen.quest_id("ato1/naga#t0") in m["twilightforest:naga"]
    assert questgen.quest_id("ato2/o_cego#t0") in m["minecraft:warden"]
    assert all(isinstance(v, list) and v for v in m.values())



def test_filter_adapter_is_java_not_kubejs():
    """O adaptador de filtros roda no thread de render do cliente: em KubeJS o Rhino crashava ao abrir o livro."""
    from paths import PACK
    assert (PACK / "mods/ecosbridge-1.0.0.jar").exists()
    for js in (PACK / "kubejs").rglob("*.js"):
        assert "registerFilterAdapter" not in js.read_text(encoding="utf-8"), js


def test_icons_survive_ftbquests_load_ingame():
    """Depois de carregado pelo FTB Quests, o capítulo ainda tem o custom_icon com a imagem, e a quest o item."""
    import json
    from paths import BUILD
    p = BUILD / "quest_selftest.json"
    if not p.exists():
        pytest.skip("sem build/quest_selftest.json (rode o boot dev)")
    d = json.loads(p.read_text(encoding="utf-8"))
    ch = d["chapter_data"]["ato1"]
    assert "ftbquests:custom_icon" in ch and "ecos:textures/gui/chapters/ato1.png" in ch, ch[:300]
    q = d["quests"][questgen.quest_id("ato1/inicio")]["quest"]
    assert '"create:cogwheel"' in q, q[:300]


def test_legacy_id_keeps_old_ids():
    old = chapter([q("x", tasks=[{"checkmark": True}, {"kill": "minecraft:warden"}], rewards=[{"xp_levels": 1}])], slug="a")
    old_files = questgen.build([old], {})
    moved = chapter([q("novo", legacy_id="a/x", tasks=[{"checkmark": True}, {"kill": "minecraft:warden"}],
                       rewards=[{"xp_levels": 1}]), q("dep", deps=["novo"])], slug="b")
    text = questgen.build([moved], {})["chapters/b.snbt"]
    for suffix in ("", "#t0", "#t1", "#r0"):
        assert questgen.quest_id("a/x" + suffix) in text
        assert questgen.quest_id("b/novo" + suffix) not in text
    assert text.count(questgen.quest_id("a/x")) == 2  # a quest e a dependência da quest "dep"
    assert questgen.kill_tasks([moved])["minecraft:warden"] == [questgen.quest_id("a/x#t1")]
    assert questgen.kill_tasks([old])["minecraft:warden"] == [questgen.quest_id("a/x#t1")]
    assert questgen.quest_id("a/x") in old_files["chapters/a.snbt"]


def test_published_ids_still_generated():
    """Todo id publicado (quest/task/reward/capítulo/tabela) continua sendo gerado; sumir = jogadores perdem progresso."""
    import re
    published = {ln.strip() for ln in (Path(__file__).parent / "fixtures" / "published_ids.txt").read_text(encoding="utf-8").splitlines() if ln.strip()}
    built = questgen.build(questgen.load_sources(), questgen.load_tables())
    now = set()
    for text in built.values():
        now |= set(re.findall(r'\bid: "?([0-9A-F]{16})"?', text))
    assert sorted(published - now) == []
