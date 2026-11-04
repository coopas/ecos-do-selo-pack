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
            loaded = d["quests"][questgen.quest_id(f"{c.slug}/{quest['slug']}")]
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
            loaded = d["quests"][questgen.quest_id(f"{c.slug}/{quest['slug']}")]
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
    assert pos["a"][0] < pos["b"][0] == pos["c"][0] < pos["d"][0]
    assert pos["b"][1] != pos["c"][1]


def test_explicit_position_wins():
    c = chapter([q("a", x=7, y=-3)], slug="l")
    assert questgen.layout(c)["a"] == (7.0, -3.0)
