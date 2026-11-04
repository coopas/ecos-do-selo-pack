"""Task 10: ritual do Occultism invoca o Arauto do Eco reforçado; a morte entrega o Eco do Arauto (escolha do desfecho)."""
import json
import re

import pytest

import recipes
from paths import BUILD, PACK

RITUAL = PACK / "kubejs/data/ecos/recipes/ritual_entidade.json"


def test_ritual_recipe_file():
    r = json.loads(RITUAL.read_text(encoding="utf-8"))
    assert r["type"] == "occultism:ritual"
    assert r["ritual_type"] == "occultism:summon"
    assert r["activation_item"] == {"item": "ecos:artefato_selo"}
    assert r["entity_to_summon"] == "cataclysm:the_harbinger"
    assert "ecos_final" in r["entity_nbt"]["Tags"]
    assert r["ingredients"]


def test_ending_items_declared():
    items = {i["id"] for i in json.loads((PACK / "kubejs/ecos/items.json").read_text(encoding="utf-8"))["items"]}
    assert {"ecos:eco_do_arauto", "ecos:selo_restaurado", "ecos:poder_absorvido"} <= items


def test_ritual_recipe_loaded():
    p = BUILD / "recipe_dump.json"
    if not p.exists():
        pytest.skip("sem build/recipe_dump.json")
    r = recipes.load(p).by_id("ecos:ritual_entidade")
    assert r is not None, "ritual não carregou no jogo"
    assert r["type"] == "occultism:ritual"


def _health(lines, tag):
    """Última leitura de Health impressa por `data get` para a entidade com CustomName ECOS_<tag>."""
    found = None
    for line in lines:
        m = re.search(rf"ECOS_{tag} has the following entity data: ([0-9.]+)f", line)
        if m:
            found = float(m.group(1))
    return found


def _measure(cmds):
    import boot_test
    problems = boot_test.server(console=cmds)
    assert problems == []
    return boot_test.LAST_CONSOLE


@pytest.mark.ingame
def test_final_boss_ingame():
    """Tag ecos_final: recebe 1/3 do dano e causa 1,5×. Golens sem armadura e sem gravidade isolam a regra;
    o Arauto de verdade só prova que a morte deixa o Eco do Arauto."""
    out = _measure([
        "forceload add 0 0",
        "kill @e[type=cataclysm:the_harbinger]",  # o mundo de teste persiste entre execuções
        "kill @e[type=minecraft:iron_golem]",
        "kill @e[type=minecraft:item]",
        'summon minecraft:iron_golem 0 200 0 {NoAI:1b,NoGravity:1b,Tags:["ecos_final"],CustomName:\'"ECOS_A"\'}',
        'summon minecraft:iron_golem 4 200 0 {NoAI:1b,NoGravity:1b,CustomName:\'"ECOS_B"\'}',
        'summon minecraft:iron_golem 8 200 0 {NoAI:1b,NoGravity:1b,CustomName:\'"ECOS_C"\'}',
        'summon minecraft:iron_golem 12 200 0 {NoAI:1b,NoGravity:1b,CustomName:\'"ECOS_D"\'}',
        "say aguardando",
        "damage @e[name=ECOS_A,limit=1] 9 minecraft:generic",
        "damage @e[name=ECOS_B,limit=1] 9 minecraft:generic",
        "damage @e[name=ECOS_C,limit=1] 10 minecraft:mob_attack by @e[name=ECOS_A,limit=1]",
        "damage @e[name=ECOS_D,limit=1] 10 minecraft:mob_attack by @e[name=ECOS_B,limit=1]",
        "data get entity @e[name=ECOS_A,limit=1] Health",
        "data get entity @e[name=ECOS_B,limit=1] Health",
        "data get entity @e[name=ECOS_C,limit=1] Health",
        "data get entity @e[name=ECOS_D,limit=1] Health",
        'summon cataclysm:the_harbinger 0 200 8 {NoAI:1b,NoGravity:1b,Tags:["ecos_final"]}',
        "say aguardando",
        "kill @e[type=cataclysm:the_harbinger]",
        "say aguardando",
        'execute if entity @e[type=item,nbt={Item:{id:"ecos:eco_do_arauto"}}] run say ECOS_FINAL_OK',
    ])
    hp = {k: _health(out, k) for k in "ABCD"}
    assert None not in hp.values(), out[-30:]
    assert 100 - hp["A"] == pytest.approx(3, abs=0.01)    # 9 ÷ 3
    assert 100 - hp["B"] == pytest.approx(9, abs=0.01)
    assert 100 - hp["C"] == pytest.approx(15, abs=0.01)   # 10 × 1,5
    assert 100 - hp["D"] == pytest.approx(10, abs=0.01)
    assert any("ECOS_FINAL_OK" in line for line in out), out[-30:]


def test_final_chain_cannot_be_stranded():
    """Usar o Artefato/Eco antes de abrir a quest não pode travar o final: as tasks aceitam a prova seguinte."""
    import questgen
    q = {f"{c.slug}/{x['slug']}": x for c in questgen.load_sources() for x in c.quests}
    assert q["final/arauto"]["tasks"] == [{"tag": "ecos:prova_arauto"}]
    assert q["ato5/artefato"]["tasks"] == [{"tag": "ecos:prova_artefato"}]
    assert "final/chamado" not in q["final/arauto"]["deps"] and "chamado" not in q["final/arauto"]["deps"]
    tags = json.loads((PACK / "kubejs/ecos/tags.json").read_text(encoding="utf-8"))["item"]
    assert set(tags["ecos:prova_arauto"]["set"]) == {"ecos:eco_do_arauto", "ecos:selo_restaurado", "ecos:poder_absorvido"}
    assert "ecos:artefato_selo" in tags["ecos:prova_artefato"]["set"]
