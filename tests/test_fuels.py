import csv
import json
import re

import pytest

import registry
from paths import BUILD, PACK, ROOT

FUELS = PACK / "kubejs" / "ecos" / "fuels.json"


def _fuels():
    return json.loads(FUELS.read_text(encoding="utf-8"))


def _reg():
    dump = BUILD / "registry_dump.json"
    if not dump.exists():
        pytest.skip("sem build/registry_dump.json (rode boot_test.py server --dev)")
    return registry.load(dump)


def test_cdg_in_manifest():
    rows = list(csv.DictReader((ROOT / "tools" / "mods.csv").read_text(encoding="utf-8").splitlines()))
    row = [r for r in rows if r["id"] == "createdieselgenerators"]
    assert row and row[0]["side"] == "both"
    assert (PACK / "mods" / "create-diesel-generators.pw.toml").exists()


def test_fuels_ids_exist():
    reg = _reg()
    d = _fuels()
    for tag, fluids in d["fluid_tags"].items():
        assert reg.has_fluid_tag(tag), tag
        for f in fluids:
            assert reg.has_fluid(f), f
    for section in ("gt_combustion_clones", "gt_distillation_clones"):
        for src, dst in d[section].items():
            assert reg.has_fluid(src) and reg.has_fluid(dst), (src, dst)


def test_fuel_tags_merged():
    reg = _reg()
    for tag, gt, cdg in (("forge:diesel", "gtceu:diesel", "createdieselgenerators:diesel"),
                         ("forge:gasoline", "gtceu:gasoline", "createdieselgenerators:gasoline")):
        members = reg.fluid_tag_fluids(tag)
        assert gt in members and cdg in members, (tag, members)


@pytest.mark.ingame
def test_fuel_crossing_ingame():
    import boot_test
    problems = boot_test.server(dev=True, console=["kubejs custom_command ecos_fuel_check"])
    assert problems == [], problems
    lines = [l for l in boot_test.LAST_CONSOLE if "ECOS_FUEL " in l]
    assert lines, boot_test.LAST_CONSOLE[-15:]
    m = re.search(r"ECOS_FUEL receitas=(\d+) esperadas=(\d+) tags_ok=(\w+) missing=\[(.*?)\]", lines[-1])
    assert m, lines[-1]
    n, expected = int(m[1]), int(m[2])
    assert expected >= len(_fuels()["gt_combustion_clones"]), lines[-1]  # 4 de combustão + destilação clonada
    assert n == expected, lines[-1]
    assert m[3] == "true" and m[4] == "", lines[-1]
