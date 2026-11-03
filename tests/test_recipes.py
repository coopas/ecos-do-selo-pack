from pathlib import Path

import recipes

DUMP = Path(__file__).parent / "fixtures" / "recipe_dump.json"


def test_for_output_finds_recipe():
    r = recipes.load(DUMP)
    found = r.for_output("ecos:chave_crepuscular")
    assert [x["id"] for x in found] == ["ecos:gate/twilight_key"]
    assert r.for_output("minecraft:stone") == []


def test_by_id():
    assert recipes.load(DUMP).by_id("minecraft:white_bed")["type"] == "minecraft:crafting_shaped"


def test_input_ids_flatten_tags():
    r = recipes.load(DUMP)
    assert recipes.input_ids(r.by_id("minecraft:white_bed")) == {"minecraft:white_wool", "#minecraft:planks"}


def test_load_accepts_wrapped_object(tmp_path):
    import json
    p = tmp_path / "d.json"
    p.write_text(json.dumps({"recipes": json.loads(DUMP.read_text())}))
    assert recipes.load(p).by_id("minecraft:white_bed") is not None


def test_real_recipe_dump_is_complete():
    import json
    import pytest
    from paths import BUILD
    p = BUILD / "recipe_dump.json"
    if not p.exists():
        pytest.skip("sem build/recipe_dump.json")
    d = json.loads(p.read_text(encoding="utf-8"))
    assert d["errors"] == []
    assert len(d["recipes"]) > 40000
    assert recipes.load(p).for_output("ad_astra:nasa_workbench")
