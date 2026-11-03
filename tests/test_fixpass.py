"""Correções da revisão final do Plano 2."""
import json
import re

import pytest

import ecosdata
import registry
from paths import BUILD, PACK

TRAVEL = PACK / "kubejs" / "ecos" / "travel.json"
SERVER_SCRIPTS = PACK / "kubejs" / "server_scripts"


def reg():
    p = BUILD / "registry_dump.json"
    if not p.exists():
        pytest.skip("sem dump")
    return registry.load(p)


def test_travel_requires_celestial_key():
    rules = json.loads(TRAVEL.read_text(encoding="utf-8"))["require"]
    assert rules == {
        "aether:the_aether": "ecos:chave_celeste",
        "blue_skies:everbright": "ecos:chave_celeste",
        "blue_skies:everdawn": "ecos:chave_celeste",
    }


def test_aether_frame_back_to_default():
    # o portal de retorno do Aether é gerado em glowstone; a moldura não pode exigir outro bloco
    assert "aether:aether_portal_blocks" not in ecosdata.load().tags.get("block", {})
    assert "minecraft:glowstone" in reg().block_tag_blocks("aether:aether_portal_blocks")


def test_chave_celeste_replaces_pedra():
    ids = ecosdata.load().item_ids()
    assert "ecos:chave_celeste" in ids and "ecos:pedra_celeste" not in ids


BANNED = {"projecte:philosophers_stone", "projecte:transmutation_table", "projecte:low_covalence_dust",
          "projecte:medium_covalence_dust", "projecte:high_covalence_dust", "projecte:collector_mk1",
          "projecte:relay_mk1", "undergarden:catalyst", "blue_skies:zeal_lighter", "ad_astra:nasa_workbench"}


def test_uncrafting_banned_for_gates():
    banned = reg().tag_items("#twilightforest:banned_uncraftables")
    assert (BANNED | ecosdata.load().item_ids()) <= banned


def test_data_scripts_fail_loudly():
    for f in SERVER_SCRIPTS.glob("*.js"):
        text = f.read_text(encoding="utf-8")
        if "JsonIO.read('kubejs/ecos/" in text:
            assert not re.search(r"JsonIO\.read\([^)]*\)\s*\|\|", text), f.name
            assert "throw" in text, f.name


def test_fragments_fire_resistant():
    for i in ecosdata.load().items:
        if i["id"].startswith("ecos:fragmento_selo_"):
            assert i.get("fire_resistant") is True, i["id"]


@pytest.mark.ingame
def test_fragment_survives_lava_ingame():
    import boot_test
    problems = boot_test.server(console=[
        "forceload add 0 0",
        "fill 0 99 0 0 99 0 minecraft:lava",
        'summon item 0 99 0 {Item:{id:"ecos:fragmento_selo_estrelas",Count:1b}}',
        "say ECOS_WAIT",
        'execute if entity @e[type=item,nbt={Item:{id:"ecos:fragmento_selo_estrelas"}}] run say ECOS_LAVA_OK',
    ])
    assert problems == []
    assert any("ECOS_LAVA_OK" in l for l in boot_test.LAST_CONSOLE), boot_test.LAST_CONSOLE[-15:]
