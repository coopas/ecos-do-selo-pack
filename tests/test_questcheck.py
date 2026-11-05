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


def test_missing_icon_and_image_reported():
    errs = run([ch([start(), q("x", deps=["despertar"], icon="mod:sem_icone", image="ecos:textures/gui/quests/nada.png")])])
    assert any("ícone mod:sem_icone" in e for e in errs)
    assert any("imagem ecos:textures/gui/quests/nada.png" in e for e in errs)


# ---------- jornada: check_progress julga cada quest no ponto em que o jogador está ----------

import progression  # noqa: E402

OW = "minecraft:overworld"


def jreg(**kw) -> registry.Registry:
    base = dict(items={"minecraft:raw_iron", "gtceu:raw_hematite", "minecraft:diamond", "x:a", "x:b", "x:c",
                       "x:nether_thing", "x:dust", "x:ore", "gtceu:lv_macerator", "gtceu:mv_macerator",
                       "gtceu:lv_steam_turbine"},
                item_tags={"forge:raw_materials/iron": {"minecraft:raw_iron"},
                           "ecos:minerios_de_ferro": {"minecraft:raw_iron", "gtceu:raw_hematite"},
                           "x:ab": {"x:a", "x:b"}, "forge:gems/diamond": {"minecraft:diamond"}},
                dimensions={OW, "minecraft:the_nether"}, entities={"x:boss"})
    base.update(kw)
    return registry.Registry(**base)


def jprog(naturals=None, **kw) -> progression.Progression:
    base = dict(naturals=naturals if naturals is not None else {OW: ["gtceu:raw_hematite", "x:a"]},
                manual_types=["minecraft:crafting_shaped"], dimension_unlocks={"minecraft:the_nether": "prologo/nether"},
                eu_sources=["gtceu:lv_steam_turbine"], deep_ok_from_act=1,
                act_tier={0: "none", 1: "lv", 2: "mv", 3: "ev", 4: "luv", 5: "uv"})
    base.update(kw)
    return progression.Progression(**base)


def jrun(chapters, recs=(), p=None, g=None, boss_drops=None):
    p = p or jprog()
    return questcheck.check_progress(chapters, g or jreg(), recipes.Recipes(list(recs)), p, p.naturals, boss_drops or {})


def errors(findings, level="erro"):
    return [f for f in findings if f.level == level]


def test_finding_shape():
    f = jrun([ch([start(), q("x", deps=["despertar"], tasks=[{"item": "x:c"}])])])
    assert len(f) == 1
    assert f[0].path == "prologo/x" and f[0].level == "erro"
    assert "x:c impossível neste ponto (falta:" in f[0].msg


def test_tag_task_needs_one_member():
    assert jrun([ch([start(), q("x", deps=["despertar"], tasks=[{"tag": "x:ab"}])])]) == []


def test_reward_of_ancestor_is_seed():
    ok = [ch([start(), q("dá", deps=["despertar"], rewards=[{"item": "x:c"}]), q("pede", deps=["dá"], tasks=[{"item": "x:c"}])])]
    assert jrun(ok) == []
    side = [ch([start(), q("dá", deps=["despertar"], rewards=[{"item": "x:c"}]),
                q("pede", deps=["despertar"], tasks=[{"item": "x:c"}])])]
    assert [f.path for f in errors(jrun(side))] == ["prologo/pede"]


def test_task_item_of_ancestor_is_seed():
    """Item de task de ancestral já está na mão: o erro aparece uma vez, não em cascata."""
    chapters = [ch([start(), q("a", deps=["despertar"], tasks=[{"item": "x:c"}]), q("b", deps=["a"], tasks=[{"item": "x:c"}])])]
    assert [f.path for f in errors(jrun(chapters))] == ["prologo/a"]


def test_boss_drop_of_ancestor_kill_is_seed():
    chapters = [ch([start(), q("mata", deps=["despertar"], tasks=[{"kill": "x:boss"}]),
                    q("usa", deps=["mata"], tasks=[{"item": "x:c"}]), q("cedo", deps=["despertar"], tasks=[{"item": "x:c"}])])]
    assert [f.path for f in errors(jrun(chapters, boss_drops={"x:boss": "x:c"}))] == ["prologo/cedo"]


def test_boss_quest_drop_seeds_itself_and_descendants():
    """Chefe invocado sem task de kill (o Arauto): boss_quest_drops põe o drop na própria quest e nos dependentes."""
    p = jprog(boss_quest_drops={"prologo/chefe": ["x:c"]})
    chapters = [ch([start(), q("chefe", deps=["despertar"], tasks=[{"item": "x:c"}]),
                    q("depois", deps=["chefe"], tasks=[{"item": "x:c"}]), q("fora", deps=["despertar"], tasks=[{"item": "x:c"}])])]
    assert [f.path for f in errors(jrun(chapters, p=p))] == ["prologo/fora"]


def test_iron_vanilla_raw_impossible_in_prologue():
    bad = jrun([ch([start(), q("ferro", deps=["despertar"], tasks=[{"tag": "forge:raw_materials/iron"}])])])
    assert [f.path for f in errors(bad)] == ["prologo/ferro"]
    assert "#forge:raw_materials/iron" in errors(bad)[0].msg
    assert jrun([ch([start(), q("ferro", deps=["despertar"], tasks=[{"tag": "ecos:minerios_de_ferro"}])])]) == []


def test_deep_only_warns_before_act():
    g = jreg(gt_veins=[{"id": "gtceu:diamond_vein", "dims": [OW], "min_y": -60, "max_y": -10, "weight": 1,
                        "materials": ["diamond"]}], pickaxe_tiers={"minecraft:iron_pickaxe": 2})
    g.items.add("minecraft:iron_pickaxe")
    p = jprog({OW: ["minecraft:iron_pickaxe"]})
    task = [{"item": "minecraft:diamond"}]
    f0 = jrun([ch([start(), q("d", deps=["despertar"], tasks=task)])], p=p, g=g)
    assert [(f.path, f.level) for f in f0] == [("prologo/d", "aviso")]
    assert "veio fundo" in f0[0].msg
    f1 = jrun([ch([start()]), ch([q("d", deps=["prologo/despertar"], tasks=task)], slug="ato1", act=1)], p=p, g=g)
    assert f1 == []


def test_gt_recipe_above_act_tier_warns():
    recs = [{"id": "gtceu:macerator/x", "type": "gtceu:macerator", "outputs": ["x:dust"], "inputs": [["x:a"]], "eut": 120}]
    machines = ["gtceu:mv_macerator", "gtceu:lv_steam_turbine"]

    def chapters(act):
        return [ch([start()]), ch([q("m", deps=["prologo/despertar"], rewards=[{"item": i} for i in machines]),
                                   q("p", deps=["m"], tasks=[{"item": "x:dust"}])], slug=f"ato{act}", act=act)]
    f1 = jrun(chapters(1), recs)
    assert [(f.path, f.level) for f in f1] == [("ato1/p", "aviso")]
    assert "mv" in f1[0].msg.lower()
    assert jrun(chapters(2), recs) == []


def test_dimension_task_quest_sees_its_dimension():
    p = jprog({OW: ["x:a"], "minecraft:the_nether": ["x:nether_thing"]})
    chapters = [ch([start(), q("nether", deps=["despertar"],
                               tasks=[{"dimension": "minecraft:the_nether"}, {"item": "x:nether_thing"}]),
                    q("depois", deps=["nether"], tasks=[{"item": "x:nether_thing"}]),
                    q("antes", deps=["despertar"], tasks=[{"item": "x:nether_thing"}])])]
    assert [f.path for f in errors(jrun(chapters, p=p))] == ["prologo/antes"]


def test_dimension_task_before_unlock_is_error():
    p = jprog({OW: ["x:a"]}, dimension_unlocks={"minecraft:the_nether": "prologo/chave"})
    chapters = [ch([start(), q("chave", deps=["despertar"]),
                    q("vai", deps=["despertar"], tasks=[{"dimension": "minecraft:the_nether"}])])]
    errs = errors(jrun(chapters, p=p))
    assert [f.path for f in errs] == ["prologo/vai"] and "prologo/chave" in errs[0].msg


def test_missing_reason_points_to_root():
    """falta: segue o caminho mais curto até o que realmente falta (aqui, a dimensão fechada)."""
    p = jprog({OW: ["x:a"], "minecraft:the_nether": ["x:nether_thing"]})
    recs = [{"id": "x:c", "type": "minecraft:crafting_shaped", "outputs": ["x:c"], "inputs": [["x:a"], ["x:nether_thing"]]}]
    f = errors(jrun([ch([start(), q("c", deps=["despertar"], tasks=[{"item": "x:c"}])])], recs, p=p))
    assert len(f) == 1 and "x:nether_thing" in f[0].msg and "minecraft:the_nether" in f[0].msg


def test_check_with_prog_adds_journey_errors():
    p = jprog()
    chapters = [ch([start(), q("x", deps=["despertar"], tasks=[{"item": "x:c"}])])]
    g = jreg(items=jreg().items | {"minecraft:oak_log"})
    plain = questcheck.check(chapters, g, recipes.Recipes([]), p.naturals, [], {})
    assert not any("impossível" in e for e in plain)
    full = questcheck.check(chapters, g, recipes.Recipes([]), p.naturals, [], {}, prog=p)
    assert any(e.startswith("prologo/x: ") and "impossível" in e for e in full)


def test_report_groups_by_chapter_in_quest_order(tmp_path):
    chapters = [ch([start(), q("b", deps=["despertar"], tasks=[{"item": "x:c"}]), q("a", deps=["b"], tasks=[{"item": "x:b"}])]),
                ch([q("z", deps=["prologo/despertar"], tasks=[{"item": "x:b"}])], slug="ato1", act=1)]
    out = tmp_path / "r.txt"
    questcheck.write_report(chapters, jrun(chapters), out)
    lines = [ln for ln in out.read_text(encoding="utf-8").splitlines() if ln.strip()]
    heads = [i for i, ln in enumerate(lines) if "|" not in ln]
    assert "prologo" in lines[heads[0]] and "ato1" in lines[heads[1]]
    body = [ln for ln in lines if "|" in ln]
    assert body[0].startswith("erro | prologo/b | ") and body[1].startswith("erro | prologo/a | ")
    assert body[2].startswith("erro | ato1/z | ")


def test_real_pack_progress_runs():
    from paths import BUILD
    if not (BUILD / "registry_dump.json").exists():
        pytest.skip("sem dump")
    import time
    t = time.time()
    findings = questcheck.main_progress()
    assert time.time() - t < 120
    assert findings and all(f.level in ("erro", "aviso") for f in findings)


def test_real_progression_quests_exist():
    """dimension_unlocks e boss_quest_drops apontam para quests que existem (renomear a quest quebraria a jornada)."""
    import progression as prog_mod
    paths = {f"{c.slug}/{q['slug']}" for c in questgen.load_sources() for q in c.quests}
    p = prog_mod.load(questcheck.PROGRESSION, questcheck.NATURALS)
    assert set(p.dimension_unlocks.values()) <= paths
    assert set(p.boss_quest_drops) <= paths
    assert set(p.act_tier) == {c.act for c in questgen.load_sources()}
