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
