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


def test_real_dump_reads_record_recipes():
    """Receitas em record (Ad Astra nasa_workbench) expõem resultado/ingredientes como métodos."""
    import pytest
    from paths import BUILD
    p = BUILD / "recipe_dump.json"
    if not p.exists():
        pytest.skip("sem build/recipe_dump.json")
    rec = recipes.load(p)
    for tier in range(1, 5):
        found = rec.for_output(f"ad_astra:tier_{tier}_rocket")
        assert found, f"foguete T{tier} sem receita no dump"
        assert any(r["inputs"] for r in found), f"foguete T{tier} sem ingredientes"


def test_old_dump_gets_defaults_for_new_fields():
    r = recipes.load(DUMP).by_id("minecraft:white_bed")
    assert r["fluid_inputs"] == [] and r["fluid_outputs"] == []
    assert r["eut"] == 0 and r["ebf_temp"] == 0


def test_fluid_producers(tmp_path):
    import json
    p = tmp_path / "d.json"
    p.write_text(json.dumps({"recipes": [
        {"id": "gtceu:distillery/x", "type": "gtceu:distillery", "outputs": [], "inputs": [],
         "fluid_inputs": [["minecraft:water"]], "fluid_outputs": ["gtceu:distilled_water"], "eut": 16, "ebf_temp": 0},
        {"id": "minecraft:stick", "type": "minecraft:crafting_shaped", "outputs": ["minecraft:stick"], "inputs": []},
    ]}))
    rec = recipes.load(p)
    assert [r["id"] for r in rec.fluid_producers("gtceu:distilled_water")] == ["gtceu:distillery/x"]
    assert rec.fluid_producers("minecraft:lava") == []
    assert rec.by_id("gtceu:distillery/x")["eut"] == 16
