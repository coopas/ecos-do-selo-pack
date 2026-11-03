import pytest

import recipes
from paths import BUILD

CROSS = [
    ("irons_spellbooks:inscription_table", "#forge:plates/steel"),
    ("ars_nouveau:imbuement_chamber", "create:andesite_alloy"),
    ("occultism:sacrificial_bowl", "#forge:ingots/brass"),
    ("ae2:inscriber", "gtceu:lv_electric_piston"),
    ("ae2:controller", "gtceu:mv_robot_arm"),
    ("waystones:waystone", "ars_nouveau:source_gem"),
    ("create:mechanical_crafter", "ars_nouveau:source_gem"),  # arcane_essence não tem receita (só loot)
    ("sophisticatedbackpacks:backpack", "create:andesite_alloy"),
]


@pytest.fixture(scope="module")
def rec():
    p = BUILD / "recipe_dump.json"
    if not p.exists():
        pytest.skip("sem dump")
    return recipes.load(p)


@pytest.mark.parametrize("output,foreign", CROSS)
def test_cross_recipes(rec, output, foreign):
    found = rec.for_output(output)
    assert [r["id"] for r in found] == [f"ecos:cross/{output.split(':')[1]}"]
    assert foreign in recipes.input_ids(found[0])
