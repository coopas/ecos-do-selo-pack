from pathlib import Path

import pytest

import ecosdata
import registry
from paths import BUILD

FIX = Path(__file__).parent / "fixtures" / "ecos"


def test_referenced_ids_collects_all_sections():
    refs = ecosdata.load(FIX).referenced_ids()
    assert {"minecraft:white_bed", "create:precision_mechanism", "ecos:fragmento_eco"} <= refs["item"]
    assert "minecraft:planks" in refs["item_tag"]
    assert "twilightforest:portal/activator" in refs["item_tag"]
    assert "aether:aether_portal_blocks" in refs["block_tag"]
    assert refs["entity"] == {"twilightforest:lich"}


def test_ecos_items_listed():
    assert ecosdata.load(FIX).item_ids() == {"ecos:fragmento_eco"}


def test_all_ids_exist():
    dump = BUILD / "registry_dump.json"
    if not dump.exists():
        pytest.skip("sem build/registry_dump.json (rode boot_test.py server --dev)")
    reg = registry.load(dump)
    data = ecosdata.load()
    refs = data.referenced_ids()
    own = data.item_ids()
    missing = [i for i in refs["item"] if not (reg.has_item(i) or i in own)]
    missing += ["#" + t for t in refs["item_tag"] if not reg.has_tag(t) and not _is_set_target(data, "item", t)]
    missing += ["block#" + t for t in refs["block_tag"] if not reg.has_block_tag(t)]
    missing += ["entity:" + e for e in refs["entity"] if not reg.has_entity(e)]
    assert missing == []


def _is_set_target(data, kind, tag):
    return tag in data.tags.get(kind, {})
