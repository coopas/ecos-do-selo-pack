from pathlib import Path

import registry

DUMP = Path(__file__).parent / "fixtures" / "registry_dump.json"


def reg():
    return registry.load(DUMP)


def test_has_item():
    assert reg().has_item("create:mechanical_press")


def test_unknown_item_false():
    assert not reg().has_item("create:does_not_exist")


def test_has_tag_with_hash():
    r = reg()
    assert r.has_tag("#minecraft:beds") and r.has_tag("minecraft:beds")
    assert not r.has_tag("#minecraft:nope")


def test_tag_items_beds():
    assert {"minecraft:red_bed", "minecraft:white_bed"} <= reg().tag_items("#minecraft:beds")


def test_fluid_and_entity():
    r = reg()
    assert r.has_fluid("minecraft:water") and r.has_entity("minecraft:zombie")
    assert not r.has_fluid("minecraft:lava_x")


def test_block_tag_lookup():
    r = reg()
    assert r.has_block_tag("#aether:aether_portal_blocks")
    assert r.block_tag_blocks("aether:aether_portal_blocks") == {"minecraft:glowstone"}
    assert not r.has_block_tag("x:y")


def test_old_dump_has_empty_progression_fields():
    r = reg()
    assert r.pickaxe_tiers == {} and r.block_tiers == {} and r.gt_veins == []


def test_progression_fields_load(tmp_path):
    import json
    d = json.loads(DUMP.read_text(encoding="utf-8"))
    d["pickaxe_tiers"] = {"minecraft:iron_pickaxe": 2}
    d["block_tiers"] = {"minecraft:obsidian": 3}
    d["gt_veins"] = [{"id": "gtceu:diamond_vein", "dims": ["minecraft:overworld"], "min_y": -55, "max_y": -30,
                      "weight": 40, "materials": ["diamond", "graphite"]}]
    p = tmp_path / "r.json"
    p.write_text(json.dumps(d))
    r = registry.load(p)
    assert r.pickaxe_tiers == {"minecraft:iron_pickaxe": 2}
    assert r.block_tiers == {"minecraft:obsidian": 3}
    assert r.gt_veins[0]["materials"] == ["diamond", "graphite"]
