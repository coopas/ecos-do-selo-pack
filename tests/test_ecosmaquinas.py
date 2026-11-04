"""Mod ecosmaquinas: jar no pack, nomes em PT, receitas da era certa, blocos registrados e constantes com perda."""
import json
import re
import zipfile

import pytest

import registry
from paths import BUILD, PACK, ROOT

JAR = PACK / "mods" / "ecosmaquinas-1.0.0.jar"
SRC = ROOT / "tools" / "ecosmaquinas" / "src" / "ecos" / "maquinas" / "EcosMaquinas.java"
IDS = ["ecosmaquinas:motor_vapor", "ecosmaquinas:dinamo_cinetico_ulv",
       "ecosmaquinas:dinamo_cinetico_lv", "ecosmaquinas:saida_vapor"]
NOMES = ["Motor a Vapor do Eco", "Dínamo Cinético (ULV)", "Dínamo Cinético (LV)", "Saída de Vapor"]
# Tiers acima de LV: nada disso pode aparecer numa receita do mod (era do vapor/LV).
_TIERS = "mv|hv|ev|iv|luv|zpm|uv|uhv|uev|uiv|uxv|opv|max"
ALTO = re.compile(rf"^gtceu:({_TIERS})_")
ALTO_TAG = re.compile(rf"[:/_]({_TIERS})($|[/_])")  # ex.: gtceu:circuits/mv
DUMP = BUILD / "registry_dump.json"


def _jar():
    assert JAR.exists(), JAR
    return zipfile.ZipFile(JAR)


def _receitas():
    with _jar() as z:
        nomes = [n for n in z.namelist() if n.startswith("data/ecosmaquinas/recipes/") and n.endswith(".json")]
        return {n: json.loads(z.read(n).decode("utf-8")) for n in nomes}


def _ingredientes(rec):
    for ing in rec.get("key", {}).values():
        for alt in (ing if isinstance(ing, list) else [ing]):
            yield alt


def test_jar_in_pack():
    assert JAR.exists()
    index = (PACK / "index.toml").read_text(encoding="utf-8")
    assert 'file = "mods/ecosmaquinas-1.0.0.jar"' in index


def test_lang_pt():
    with _jar() as z:
        lang = json.loads(z.read("assets/ecosmaquinas/lang/pt_br.json").decode("utf-8"))
    for nome in NOMES:
        assert nome in lang.values(), nome
    for id_ in IDS:
        assert lang.get("block." + id_.replace(":", ".")), id_


def test_recipes_era():
    rs = _receitas()
    saidas = {r["result"]["item"] for r in rs.values()}
    assert saidas == set(IDS)
    for nome, rec in rs.items():
        for alt in _ingredientes(rec):
            item = alt.get("item", "")
            assert not ALTO.match(item), (nome, item)
            assert not ALTO_TAG.search(alt.get("tag", "")), (nome, alt)
    # sanidade do próprio filtro
    assert ALTO_TAG.search("gtceu:circuits/mv") and ALTO.match("gtceu:mv_electric_motor")
    assert not ALTO_TAG.search("forge:plates/wrought_iron") and not ALTO.match("gtceu:lv_machine_hull")


def test_jar_assets_complete():
    """Cada bloco tem blockstate, modelo de item, loot table e textura dentro do jar."""
    with _jar() as z:
        nomes = set(z.namelist())
    for id_ in IDS:
        b = id_.split(":")[1]
        for p in (f"assets/ecosmaquinas/blockstates/{b}.json", f"assets/ecosmaquinas/models/item/{b}.json",
                  f"data/ecosmaquinas/loot_tables/blocks/{b}.json"):
            assert p in nomes, p
    assert any(n.startswith("assets/ecosmaquinas/textures/block/") and n.endswith(".png") for n in nomes)


def test_blocks_registered():
    if not DUMP.exists():
        pytest.skip("sem build/registry_dump.json")
    reg = registry.load(DUMP)
    for id_ in IDS:
        assert reg.has_item(id_), id_


def test_recipe_ingredients_exist():
    if not DUMP.exists():
        pytest.skip("sem build/registry_dump.json")
    reg = registry.load(DUMP)
    for nome, rec in _receitas().items():
        for alt in _ingredientes(rec):
            if "item" in alt:
                assert reg.has_item(alt["item"]), (nome, alt)
            else:
                assert reg.tag_items(alt["tag"]), (nome, alt)


def _feedback(linhas, pos):
    """Valores de `data get block <pos> <caminho>` no console, em ordem (ex.: '...has the following block data: 512.0f')."""
    alvo = re.compile(rf"{pos.replace(' ', ', ')}.*has the following block data: (-?[\d.]+)f")
    return [float(m[1]) for l in linhas if (m := alvo.search(l))]


@pytest.mark.ingame
def test_maquinas_colocam_e_recarregam_ingame():
    """Os 4 blocos são colocados (um com NBT vazio), o dínamo LV entra na rede do Create com o impacto registrado,
    e tudo volta do disco depois de reiniciar o servidor (mundo existente), sem erro no log."""
    import boot_test
    base = ["forceload add 0 0"]
    lugar = ["setblock 2 300 2 ecosmaquinas:motor_vapor[facing=up]", "setblock 2 301 2 create:shaft[axis=y]",
             "setblock 3 300 2 ecosmaquinas:dinamo_cinetico_ulv{}",
             "setblock 4 300 2 ecosmaquinas:dinamo_cinetico_lv[facing=south]",
             "setblock 4 300 3 create:creative_motor[facing=north]",
             "setblock 5 300 2 ecosmaquinas:saida_vapor"]
    medir = ["say ECOS_WAIT", "data get block 4 300 2 Speed", "data get block 4 300 2 Network.AddedStress",
             "data get block 4 300 2 Network.Stress", "data get block 2 300 2 Speed"]
    problems = boot_test.server(console=base + lugar + medir)
    assert problems == [], problems
    c1 = list(boot_test.LAST_CONSOLE)
    # creative motor a 16 RPM; impacto LV registrado = 32 SU/RPM -> 512 SU na rede
    assert [abs(v) for v in _feedback(c1, "4 300 2")] == [16.0, 32.0, 512.0], c1[-14:]  # sentido não importa
    assert _feedback(c1, "2 300 2") == [0.0], c1[-14:]  # motor sem vapor: 0 RPM

    checar = [f"execute if block {p} {b}" for p, b in (("2 300 2", "ecosmaquinas:motor_vapor"),
              ("3 300 2", "ecosmaquinas:dinamo_cinetico_ulv"), ("4 300 2", "ecosmaquinas:dinamo_cinetico_lv"),
              ("5 300 2", "ecosmaquinas:saida_vapor"))]
    limpar = [f"setblock {p} minecraft:air" for p in ("2 301 2", "2 300 2", "3 300 2", "4 300 3", "4 300 2", "5 300 2")]
    problems = boot_test.server(console=base + ["say ECOS_WAIT"] + checar + ["data get block 4 300 2 Network.Stress"]
                                + limpar + ["forceload remove 0 0"])
    assert problems == [], problems
    c2 = list(boot_test.LAST_CONSOLE)
    assert sum("Test passed" in l for l in c2) == 4, c2[-15:]
    assert _feedback(c2, "4 300 2") == [512.0], c2[-15:]


def _constantes():
    txt = SRC.read_text(encoding="utf-8")
    m = re.search(r"class Constantes\s*\{(.*?)\n\s*\}", txt, re.S)
    assert m, "EcosMaquinas.Constantes não encontrada"
    return {k: int(v) for k, v in re.findall(r"int\s+([A-Z_]+)\s*=\s*(\d+)\s*;", m.group(1))}


def test_constantes_perda():
    c = _constantes()
    assert c == {"SU_POR_MB_VAPOR": 24, "SU_POR_EU": 64, "MOTOR_RPM": 32, "MOTOR_MAX_MB_T": 80,
                 "SAIDA_MB_T_POR_NIVEL": 6, "DINAMO_ULV_IMPACTO": 8, "DINAMO_LV_IMPACTO": 32}
    # GregTech: 2 mB de vapor = 1 EU. Pelo ciclo motor -> dínamo, 2 mB têm de render <= 0,75 EU (perda >= 25 %).
    assert c["SU_POR_MB_VAPOR"] * 2 / c["SU_POR_EU"] <= 0.75
