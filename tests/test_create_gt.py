import json

import pytest

import gen_create_gt
import registry
from paths import BUILD, PACK

CREATE_GT = PACK / "kubejs" / "ecos" / "create_gt.json"


def _fixture_reg():
    items = {"gtceu:raw_hematite", "gtceu:crushed_hematite_ore", "gtceu:purified_hematite_ore",
             "gtceu:raw_rubber_dust", "gtceu:bronze_ingot", "gtceu:red_alloy_ingot",
             "gtceu:tin_alloy_ingot", "gtceu:cupronickel_ingot", "gtceu:invar_ingot",
             "gtceu:iron_plate", "minecraft:iron_ingot"}
    tags = {"forge:raw_materials/hematite": {"gtceu:raw_hematite"},
            "forge:ingots/iron": {"minecraft:iron_ingot"}, "forge:ingots/copper": {"minecraft:copper_ingot"},
            "forge:ingots/tin": {"gtceu:tin_ingot"}, "forge:ingots/nickel": {"gtceu:nickel_ingot"},
            "forge:dusts/redstone": {"minecraft:redstone"}}
    return registry.Registry(items=items, item_tags=tags)


def _results(r):
    return r["results"]


def test_crushing_yield_below_gt():
    d = gen_create_gt.build(_fixture_reg())
    rec = d["crushing"]["hematite"]
    assert rec["ingredients"] == [{"tag": "forge:raw_materials/hematite"}]
    main, extra = _results(rec)
    assert main == {"item": "gtceu:crushed_hematite_ore", "count": 1}
    assert extra == {"item": "gtceu:crushed_hematite_ore", "chance": 0.3}
    assert d["splashing"]["hematite"]["results"] == [{"item": "gtceu:purified_hematite_ore", "count": 1}]


def test_skips_material_without_purified():
    d = gen_create_gt.build(_fixture_reg())
    assert "rubber_dust" not in d["crushing"]
    assert list(d["crushing"]) == ["hematite"]


def test_mixing_values():
    m = gen_create_gt.build(_fixture_reg())["mixing"]
    bronze = m["bronze"]
    assert bronze["heatRequirement"] == "heated"
    assert bronze["results"] == [{"item": "gtceu:bronze_ingot", "count": 4}]
    tags = [i["tag"] for i in bronze["ingredients"]]
    assert sorted(tags) == ["forge:ingots/copper"] * 3 + ["forge:ingots/tin"]
    red = m["red_alloy"]
    assert red["results"] == [{"item": "gtceu:red_alloy_ingot", "count": 1}]
    assert sorted(i["tag"] for i in red["ingredients"]) == ["forge:dusts/redstone"] * 4 + ["forge:ingots/copper"]
    assert m["invar"]["results"][0]["count"] == 3
    assert m["tin_alloy"]["results"][0]["count"] == 2
    assert m["cupronickel"]["results"][0]["count"] == 2


def test_pressing_skips_existing_create_recipe():
    reg = _fixture_reg()
    assert "iron" in gen_create_gt.build(reg)["pressing"]
    recipes = [{"id": "create:pressing/iron_ingot", "type": "create:pressing",
                "outputs": ["create:iron_sheet"], "inputs": [["minecraft:iron_ingot"]]}]
    assert "iron" not in gen_create_gt.build(reg, recipes)["pressing"]


def test_gravel_keeps_original_outputs_and_adds_redstone():
    g = gen_create_gt.build(_fixture_reg())["gravel"]
    res = _results(g)
    assert {"item": "minecraft:sand", "count": 1} in res
    assert {"item": "minecraft:redstone", "chance": 0.1} in res
    assert any(r["item"] == "minecraft:flint" for r in res)
    assert g["ingredients"] == [{"item": "minecraft:gravel"}]


def _reg():
    dump = BUILD / "registry_dump.json"
    if not dump.exists():
        pytest.skip("sem build/registry_dump.json (rode boot_test.py server --dev)")
    return registry.load(dump)


def _ids(node):
    if isinstance(node, dict):
        if "item" in node:
            yield "item", node["item"]
        if "tag" in node:
            yield "tag", node["tag"]
        for v in node.values():
            yield from _ids(v)
    elif isinstance(node, list):
        for v in node:
            yield from _ids(v)


def test_generated_file_ids_exist():
    reg = _reg()
    d = json.loads(CREATE_GT.read_text(encoding="utf-8"))
    assert len(d["crushing"]) >= 100
    for kind, v in _ids(d):
        assert (reg.has_item(v) if kind == "item" else reg.has_tag(v)), v


@pytest.mark.ingame
def test_create_gt_in_recipe_dump():
    import boot_test
    problems = boot_test.server(dev=True)
    assert problems == [], problems
    dump = BUILD / "recipe_dump.json"
    if not dump.exists():
        pytest.skip("sem build/recipe_dump.json")
    R = {r["id"]: r for r in json.loads(dump.read_text(encoding="utf-8"))["recipes"]}
    d = json.loads(CREATE_GT.read_text(encoding="utf-8"))
    c = R["ecos:create_gt/crushing/hematite"]
    assert c["type"] == "create:crushing" and ["#forge:raw_materials/hematite"] in c["inputs"]
    assert c["outputs"] == ["gtceu:crushed_hematite_ore"]
    # o recipe_dump só lista saídas sem chance: a redstone do cascalho (chance 0.1) não aparece nele,
    # então confere-se que a receita nova existe, a original sumiu e o JSON carrega a redstone
    assert "create:crushing/gravel" not in R
    assert R["ecos:create_gt/gravel"]["outputs"] == ["minecraft:sand"]
    assert {"item": "minecraft:redstone", "chance": 0.1} in d["gravel"]["results"]
    assert R["ecos:create_gt/mixing/bronze"]["type"] == "create:mixing"
    expected = sum(len(d[k]) for k in ("crushing", "splashing", "pressing", "mixing")) + 1
    assert sum(k.startswith("ecos:create_gt/") for k in R) == expected
