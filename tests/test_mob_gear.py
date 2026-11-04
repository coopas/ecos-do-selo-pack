import json
import re

import pytest

import registry
from paths import BUILD, PACK

EQUIP = PACK / "config" / "improvedmobs" / "equipment.json"


def test_equipment_list_is_vanilla_and_tiered():
    d = json.loads(EQUIP.read_text(encoding="utf-8"))
    slots = {k: v for k, v in d.items() if k != "__comment"}
    assert set(slots) == {"MAINHAND", "OFFHAND", "HEAD", "CHEST", "LEGS", "FEET"}
    for slot, items in slots.items():
        assert items, slot
        for item, (weight, quality) in items.items():
            assert item.startswith("minecraft:"), item
            assert isinstance(weight, int) and weight >= 0 and quality >= 0, item
            if "diamond" in item or "netherite" in item:
                assert weight == 0, f"{item} não pode aparecer na dificuldade 0"
        # na dificuldade 0 sempre há o que sortear
        assert sum(w for w, _ in items.values()) > 0, slot
    banned = {"minecraft:lava_bucket", "minecraft:tnt", "minecraft:ender_pearl", "minecraft:flint_and_steel"}
    assert not banned & {i for v in slots.values() for i in v}


def test_equipment_ids_exist():
    dump = BUILD / "registry_dump.json"
    if not dump.exists():
        pytest.skip("sem build/registry_dump.json (rode boot_test.py server --dev)")
    reg = registry.load(dump)
    d = json.loads(EQUIP.read_text(encoding="utf-8"))
    for slot, items in d.items():
        if slot != "__comment":
            for item in items:
                assert reg.has_item(item), item


def test_backpack_spawn_forced_off():
    js = (PACK / "kubejs" / "server_scripts" / "05_ecos_mob_gear.js").read_text(encoding="utf-8")
    assert "entityBackpackAdditions" in js and "chance.set(0.0)" in js


@pytest.mark.ingame
def test_mobs_spawn_without_modded_gear_ingame():
    import boot_test
    cmds = ["forceload add 0 0", "gamerule doDaylightCycle false", "gamerule maxEntityCramming 0", "time set midnight", "weather clear",
            "improvedmobs difficulty set 250", "kill @e[type=!player]"]
    cmds += ["execute positioned 8 0 8 positioned over world_surface run summon minecraft:zombie ~ ~ ~ {NoAI:1b,NoGravity:1b,PersistenceRequired:1b}"] * 60
    cmds += ["execute positioned 8 0 8 positioned over world_surface run summon minecraft:skeleton ~ ~ ~ {NoAI:1b,NoGravity:1b,PersistenceRequired:1b}"] * 20
    cmds += ["say ECOS_WAIT", "execute if entity @e[type=zombie]", "execute if entity @e[type=skeleton]",
             "kubejs custom_command ecos_gear_check"]
    problems = boot_test.server(dev=True, console=cmds)
    assert problems == [], problems
    lines = [l for l in boot_test.LAST_CONSOLE if "ECOS_GEAR" in l]
    assert lines, boot_test.LAST_CONSOLE[-15:]
    m = re.search(r"total=(\d+) equipped=(\d+) bad=\[(.*?)\]", lines[-1])
    total, equipped, bad = int(m[1]), int(m[2]), m[3]
    assert total >= 60, (lines[-1], [l for l in boot_test.LAST_CONSOLE if "count" in l])
    assert equipped > total // 3, lines[-1]  # dificuldade 250: o Improved Mobs está equipando
    assert bad == "", lines[-1]
    log = (BUILD / "server" / "logs" / "kubejs" / "server.log").read_text(encoding="utf-8", errors="replace")
    assert re.search(r"mochilas em mobs: chance=0(\.0)?\s*$", log, re.M)
    cfg = (BUILD / "server" / "world" / "serverconfig" / "sophisticatedbackpacks-server.toml").read_text()
    assert re.search(r"^\s*chance = 0\.0\s*$", cfg, re.M), "config do mundo não foi corrigida"
