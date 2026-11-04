from pathlib import Path

import pytest

import questcheck
import questgen
import recipes
import registry

FIX = Path(__file__).parent / "fixtures"
REG = registry.load(FIX / "registry_dump.json")
REC = recipes.load(FIX / "recipe_dump.json")
NATURALS = {"ores": ["minecraft:oak_log"]}
VARIANTS = ["minecraft:beds"]


def ch(quests, slug="prologo", act=0):
    return questgen.Chapter.from_dict({"chapter": slug, "title": "T", "icon": "minecraft:oak_log",
                                       "group": "atos", "act": act, "quests": quests})


def q(slug, tasks=None, rewards=None, **kw):
    base = {"slug": slug, "title": slug, "desc": ["d"],
            "tasks": tasks if tasks is not None else [{"checkmark": True}],
            "rewards": rewards if rewards is not None else [{"xp_levels": 1}]}
    base.update(kw)
    return base


def run(chapters):
    return questcheck.check(chapters, REG, REC, NATURALS, VARIANTS, boss_drops={})


def start():
    return q("despertar")


def test_valid_minimal_ok():
    assert run([ch([start(), q("b", deps=["despertar"], tasks=[{"tag": "minecraft:beds"}])])]) == []


def test_missing_item_reported():
    errs = run([ch([start(), q("x", deps=["despertar"], tasks=[{"item": "mod:nao_existe"}])])])
    assert any("mod:nao_existe" in e and "não existe" in e for e in errs)


def test_unobtainable_item_reported():
    # existe no registro, sem receita, não é natural nem recompensa
    errs = run([ch([start(), q("x", deps=["despertar"], tasks=[{"item": "minecraft:red_bed"}],
                                allow_exact="teste")])])
    assert any("minecraft:red_bed" in e and "obtível" in e for e in errs)


def test_reward_of_earlier_quest_counts_as_obtainable():
    chapters = [ch([start(), q("dá", deps=["despertar"], rewards=[{"item": "minecraft:red_bed"}]),
                    q("pede", deps=["dá"], tasks=[{"item": "minecraft:red_bed"}], allow_exact="teste")])]
    assert run(chapters) == []


def test_red_bed_exact_rejected():
    errs = run([ch([start(), q("x", deps=["despertar"], tasks=[{"item": "minecraft:red_bed"}])])])
    assert any("#minecraft:beds" in e for e in errs)


def test_allow_exact_with_reason_ok():
    chapters = [ch([start(), q("dá", deps=["despertar"], rewards=[{"item": "minecraft:red_bed"}]),
                    q("x", deps=["dá"], tasks=[{"item": "minecraft:red_bed"}], allow_exact="lore: cama do diário")])]
    assert run(chapters) == []


def test_cycle_reported():
    errs = run([ch([start(), q("a", deps=["despertar", "b"]), q("b", deps=["a"])])])
    assert any("ciclo" in e for e in errs)


def test_unreachable_reported():
    errs = run([ch([start(), q("solta", deps=[])])])
    assert any("inalcançável" in e and "solta" in e for e in errs)


def test_act_order_violation_reported():
    errs = run([ch([start()]), ch([q("tarde", deps=["prologo/despertar"])], slug="ato3", act=3),
                ch([q("cedo", deps=["ato3/tarde"])], slug="ato1", act=1)])
    assert any("ordem dos atos" in e and "ato1/cedo" in e for e in errs)


def test_quest_without_reward_reported():
    errs = run([ch([start(), q("x", deps=["despertar"], rewards=[])])])
    assert any("sem recompensa" in e for e in errs)


def test_long_description_reported():
    errs = run([ch([start(), q("x", deps=["despertar"], desc=["1", "2", "3", "4", "5"])])])
    assert any("linhas" in e for e in errs)


def test_missing_dimension_and_entity_reported():
    errs = run([ch([start(), q("x", deps=["despertar"], tasks=[{"dimension": "x:y"}, {"kill": "x:z"}])])])
    assert any("x:y" in e for e in errs) and any("x:z" in e for e in errs)


def test_real_quests_pass():
    from paths import BUILD
    if not (BUILD / "registry_dump.json").exists():
        pytest.skip("sem dump")
    assert questcheck.main_check() == []


def test_natural_tag_entries_expand():
    chapters = [ch([start(), q("x", deps=["despertar"], tasks=[{"item": "minecraft:red_bed"}], allow_exact="t")])]
    errs = questcheck.check(chapters, REG, REC, {"plants": ["#minecraft:beds"]}, VARIANTS, boss_drops={})
    assert errs == []


def test_missing_icon_and_image_reported():
    errs = run([ch([start(), q("x", deps=["despertar"], icon="mod:sem_icone", image="ecos:textures/gui/quests/nada.png")])])
    assert any("ícone mod:sem_icone" in e for e in errs)
    assert any("imagem ecos:textures/gui/quests/nada.png" in e for e in errs)
