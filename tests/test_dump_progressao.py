"""Provas de que o dump dev traz o que a simulação do jogador precisa (entradas do GT, EU, veios, picaretas).

Só leem build/registry_dump.json e build/recipe_dump.json: rode antes `python tools/build_server.py` e
`python tools/boot_test.py server --dev` (o boot dev copia os dumps frescos para build/).
"""
from fnmatch import fnmatchcase

import pytest

import progression
import recipes
import registry
from paths import BUILD, ROOT


def _rec() -> recipes.Recipes:
    p = BUILD / "recipe_dump.json"
    if not p.exists():
        pytest.skip("sem build/recipe_dump.json (rode o boot dev)")
    return recipes.load(p)


def _reg() -> registry.Registry:
    p = BUILD / "registry_dump.json"
    if not p.exists():
        pytest.skip("sem build/registry_dump.json (rode o boot dev)")
    return registry.load(p)


@pytest.mark.ingame
def test_gt_inputs_filled():
    gt = [r for r in _rec().all if r["id"].startswith("gtceu:")]
    assert len(gt) > 10000
    vazias = [r["id"] for r in gt if not r["inputs"] and not r["fluid_inputs"]]
    assert len(vazias) < 0.05 * len(gt), (len(vazias), vazias[:20])


@pytest.mark.ingame
def test_gt_eut():
    mac = [r for r in _rec().all if r["id"].startswith("gtceu:macerator/")]
    assert mac
    assert any(1 <= r["eut"] <= 32 for r in mac), [(r["id"], r["eut"]) for r in mac[:10]]
    assert all(r["eut"] >= 0 for r in mac)


@pytest.mark.ingame
def test_ebf_temp():
    ebf = [r for r in _rec().all if r["id"].startswith("gtceu:electric_blast_furnace/")]
    assert any(r["ebf_temp"] >= 1000 for r in ebf), [(r["id"], r["ebf_temp"]) for r in ebf[:10]]


@pytest.mark.ingame
def test_gt_fluids():
    rec = _rec()
    assert rec.fluid_producers("gtceu:oxygen"), "nenhuma receita produz oxigênio"
    assert any(r["fluid_inputs"] for r in rec.all if r["id"].startswith("gtceu:electrolyzer/"))


@pytest.mark.ingame
def test_pickaxe_tiers():
    reg = _reg()
    t = reg.pickaxe_tiers
    assert t["minecraft:wooden_pickaxe"] == 0
    assert t["minecraft:stone_pickaxe"] == 1
    assert t["minecraft:iron_pickaxe"] == 2
    assert t["minecraft:diamond_pickaxe"] == 3
    assert t["minecraft:netherite_pickaxe"] == 4
    assert reg.block_tiers["minecraft:obsidian"] == 3


@pytest.mark.ingame
def test_diamond_vein():
    veios = [v for v in _reg().gt_veins if "diamond" in v["materials"]]
    assert veios
    assert any("minecraft:overworld" in v["dims"] and v["max_y"] < 0 for v in veios), veios


@pytest.mark.ingame
def test_gt_chanced_outputs():
    """Saídas com chance do GT entram em outputs. Caldeiras e geradores (ignored_types) só fazem EU: ficam de fora."""
    ignorados = progression.load(ROOT / "quests" / "progression.yaml").ignored_types
    gt = [r for r in _rec().all if r["id"].startswith("gtceu:")
          and not any(fnmatchcase(r["type"], pat) for pat in ignorados)]
    vazias = [r["id"] for r in gt if not r["outputs"] and not r["fluid_outputs"]]
    assert len(vazias) < 50, (len(vazias), vazias[:20])
    sifter = [r for r in gt if r["id"].startswith("gtceu:sifter/")]
    assert any(o.startswith(("gtceu:flawless_", "gtceu:exquisite_")) for r in sifter for o in r["outputs"]),         [(r["id"], r["outputs"]) for r in sifter[:5]]


@pytest.mark.ingame
def test_inputs_filled_all_mods():
    todas = _rec().all
    vazia = lambda r: not r["inputs"] and not r["fluid_inputs"]  # noqa: E731
    vazias = [r for r in todas if vazia(r)]
    assert len(vazias) < 150, (len(vazias), sorted({r["type"] for r in vazias}))
    smithing = [r["id"] for r in todas if r["type"] == "minecraft:smithing_transform" and vazia(r)]
    assert smithing == []
    ars = [r for r in todas if r["type"].startswith("ars_nouveau:")]
    assert ars
    assert sum(map(vazia, ars)) < 0.1 * len(ars), [r["id"] for r in ars if vazia(r)][:20]


@pytest.mark.ingame
def test_gt_vein_errors_empty():
    import json
    p = BUILD / "registry_dump.json"
    if not p.exists():
        pytest.skip("sem build/registry_dump.json (rode o boot dev)")
    d = json.loads(p.read_text(encoding="utf-8"))
    if "gt_vein_errors" not in d:
        pytest.skip("dump sem gt_vein_errors (dump antigo)")
    assert d["gt_vein_errors"] == []
