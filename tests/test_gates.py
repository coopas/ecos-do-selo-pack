"""Travas dos portais (Atos I–III) verificadas contra os dumps reais (build/*.json)."""
import pytest

import ecosdata
import recipes
import registry
from paths import BUILD


@pytest.fixture(scope="module")
def reg():
    p = BUILD / "registry_dump.json"
    if not p.exists():
        pytest.skip("sem dump")
    return registry.load(p)


@pytest.fixture(scope="module")
def rec():
    p = BUILD / "recipe_dump.json"
    if not p.exists():
        pytest.skip("sem dump")
    return recipes.load(p)


def only_recipe(rec, output):
    found = rec.for_output(output)
    assert len(found) == 1, [r["id"] for r in found]
    assert found[0]["id"].startswith("ecos:"), found[0]["id"]
    return recipes.input_ids(found[0])


def test_twilight_activator_is_only_key(reg):
    assert reg.tag_items("#twilightforest:portal/activator") == {"ecos:chave_crepuscular"}


def test_twilight_key_needs_create(rec):
    assert "create:precision_mechanism" in only_recipe(rec, "ecos:chave_crepuscular")


def test_undergarden_catalyst_single_recipe_needs_floresta(rec):
    ins = only_recipe(rec, "undergarden:catalyst")
    assert {"ecos:fragmento_selo_floresta", "ars_nouveau:source_gem", "gtceu:lv_electric_pump"} <= ins


def test_chave_celeste_needs_profundezas(rec):
    ins = only_recipe(rec, "ecos:chave_celeste")
    assert {"ecos:fragmento_selo_profundezas", "gtceu:mv_emitter"} <= ins


def test_zeal_lighter_single_recipe_needs_profundezas(rec):
    ins = only_recipe(rec, "blue_skies:zeal_lighter")
    assert {"ecos:fragmento_selo_profundezas", "gtceu:mv_emitter"} <= ins


def test_gate_outputs_have_no_other_recipe(rec):
    for r in ecosdata.load().all_recipes():
        if r.get("replace_output"):
            only_recipe(rec, r["output"])


def test_heart_of_the_deep_still_obtainable(reg):
    assert reg.has_item("deeperdarker:heart_of_the_deep")


def test_recipe_counts_match_data(rec):
    for r in ecosdata.load().all_recipes():
        found = rec.by_id(r["id"])
        assert found is not None, r["id"]
        assert found["outputs"] == [r["output"]]
