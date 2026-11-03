import json
from pathlib import Path

import pytest

import gen_emc
import registry
from paths import BUILD, PACK

FIX = Path(__file__).parent / "fixtures"
CUSTOM = PACK / "config" / "ProjectE" / "custom_emc.json"


def test_build_entries_only_gtceu():
    sample = json.loads((FIX / "emc_entry.json").read_text())
    entries = gen_emc.build_entries(["gtceu:a", "minecraft:dirt", "gtceu:b"])
    assert entries == [{**sample, "item": "gtceu:a"}, {**sample, "item": "gtceu:b"}]
    assert all(e["emc"] == 0 for e in entries)


def test_custom_emc_covers_all_gtceu():
    dump = BUILD / "registry_dump.json"
    if not dump.exists():
        pytest.skip("sem dump")
    gt = {i for i in registry.load(dump).items if i.startswith("gtceu:")}
    data = json.loads(CUSTOM.read_text(encoding="utf-8"))
    covered = {e["item"] for e in data["entries"] if e["emc"] == 0}
    assert gt <= covered


def test_no_gtceu_item_has_emc_ingame():
    dump = BUILD / "registry_dump.json"
    if not dump.exists():
        pytest.skip("sem dump")
    d = json.loads(dump.read_text(encoding="utf-8"))
    assert "emc_gtceu_nonzero" in d, "dump sem campo de EMC (rode boot_test.py server --dev)"
    assert d["emc_gtceu_nonzero"] == []
    assert d["emc_sanity_dirt"] > 0  # prova que a consulta de EMC funciona
