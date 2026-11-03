import pytest

import recipes
from paths import BUILD

FRAGS = {"ecos:fragmento_selo_floresta", "ecos:fragmento_selo_profundezas",
         "ecos:fragmento_selo_ceus", "ecos:fragmento_selo_estrelas"}


@pytest.fixture(scope="module")
def rec():
    p = BUILD / "recipe_dump.json"
    if not p.exists():
        pytest.skip("sem dump")
    return recipes.load(p)


def only(rec, output):
    found = rec.for_output(output)
    assert len(found) == 1 and found[0]["id"].startswith("ecos:"), [r["id"] for r in found]
    return recipes.input_ids(found[0])


def test_nasa_workbench_single_needs_ev(rec):
    assert {"ecos:fragmento_selo_ceus", "gtceu:ev_robot_arm", "gtceu:ev_emitter"} <= only(rec, "ad_astra:nasa_workbench")


def test_philosophers_stone_single_and_late(rec):
    assert {"ecos:fragmento_selo_estrelas", "gtceu:luv_field_generator"} <= only(rec, "projecte:philosophers_stone")


def test_artefato_needs_all_fragments(rec):
    ins = only(rec, "ecos:artefato_selo")
    assert FRAGS | {"projecte:philosophers_stone", "gtceu:zpm_field_generator"} <= ins


def test_projecte_no_bypass(rec):
    for r in rec.all:
        outs = [o for o in r["outputs"] if o.startswith("projecte:")]
        if not outs or outs == ["projecte:philosophers_stone"]:
            continue
        flat = recipes.input_ids(r)
        assert any(i.lstrip("#").startswith("projecte:") for i in flat), (r["id"], sorted(flat))
