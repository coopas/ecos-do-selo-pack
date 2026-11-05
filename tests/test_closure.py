"""Motor de fecho (tools/closure.py): o que o jogador consegue produzir a partir do que tem e das dimensões abertas.

Fixtures pequenos em Python; os testes do fim (dados reais) só rodam com os dumps em build/.
"""
import time

import pytest

import closure
import progression
import recipes
import registry
from paths import BUILD, ROOT


def reg(**kw) -> registry.Registry:
    base = dict(items={"minecraft:iron_pickaxe", "minecraft:diamond_pickaxe", "minecraft:obsidian"},
                pickaxe_tiers={"minecraft:iron_pickaxe": 2, "minecraft:diamond_pickaxe": 3})
    base.update(kw)
    return registry.Registry(**base)


def prog(naturals=None, **kw) -> progression.Progression:
    base = dict(naturals=naturals or {}, manual_types=["minecraft:crafting_shaped"],
                machines={"minecraft:smelting": ["minecraft:furnace"]},
                steam_max_eut={"lp": 8, "hp": 32}, eu_sources=["gtceu:lv_steam_turbine"],
                coils={"gtceu:cupronickel_coil_block": 1800, "fake:weak_coil": 1500})
    base.update(kw)
    return progression.Progression(**base)


def rcp(id_, type_, outputs, inputs, **kw) -> dict:
    return {"id": id_, "type": type_, "outputs": outputs, "inputs": inputs, **kw}


def run(seed, recs, p=None, g=None, dims=("minecraft:overworld",)):
    return closure.reach(set(seed), set(dims), p or prog(), recipes.Recipes(recs), g or reg())


def test_cycle_is_not_a_source():
    recs = [rcp("x:a2b", "minecraft:crafting_shaped", ["x:b"], [["x:a"]]),
            rcp("x:b2a", "minecraft:crafting_shaped", ["x:a"], [["x:b"]])]
    r = run(set(), recs)
    assert "x:a" not in r.items and "x:b" not in r.items
    r = run({"x:a"}, recs)  # com uma fonte, o ciclo inteiro entra
    assert {"x:a", "x:b"} <= r.items


def test_natural_needs_pickaxe_tier():
    p = prog({"minecraft:overworld": [{"id": "minecraft:obsidian", "tier": 3}]})
    assert "minecraft:obsidian" not in run({"minecraft:iron_pickaxe"}, [], p).items
    r = run({"minecraft:diamond_pickaxe"}, [], p)
    assert "minecraft:obsidian" in r.items
    assert "minecraft:overworld" in r.why("minecraft:obsidian")


def test_natural_unlocked_by_crafted_pickaxe():
    """Liberar uma picareta no meio do fecho reavalia as fontes naturais."""
    p = prog({"minecraft:overworld": ["x:gem", {"id": "minecraft:obsidian", "tier": 3}]})
    recs = [rcp("x:pick", "minecraft:crafting_shaped", ["minecraft:diamond_pickaxe"], [["x:gem"]])]
    assert "minecraft:obsidian" in run(set(), recs, p).items


def test_natural_needs_item():
    p = prog({"minecraft:overworld": [{"id": "x:milk", "needs": ["x:bucket", "x:other"]}]})
    assert "x:milk" not in run(set(), [], p).items
    assert "x:milk" in run({"x:other"}, [], p).items


GT = [rcp("gtceu:macerator/x", "gtceu:macerator", ["x:dust"], [["x:ore"]], eut=30)]


def test_gt_recipe_needs_machine_tier():
    assert "x:dust" not in run({"x:ore", "gtceu:lp_steam_macerator"}, GT).items  # steam lp = 8 < 30
    assert "x:dust" in run({"x:ore", "gtceu:lv_macerator", "gtceu:lv_steam_turbine"}, GT).items
    assert "x:dust" not in run({"x:ore", "gtceu:lv_macerator"}, GT).items  # elétrica sem fonte de EU
    assert "x:dust" in run({"x:ore", "gtceu:hp_steam_macerator"}, GT).items  # hp = 32 ≥ 30


def test_machine_must_be_reached():
    recs = [rcp("x:smelt", "minecraft:smelting", ["x:ingot"], [["x:raw"]])]
    assert "x:ingot" not in run({"x:raw"}, recs).items
    # a fornalha só chega depois (raw -> cobble -> furnace): a receita fica bloqueada e é reavaliada
    later = [rcp("x:cobble", "minecraft:crafting_shaped", ["x:cobble"], [["x:raw"]]),
             rcp("x:furnace", "minecraft:crafting_shaped", ["minecraft:furnace"], [["x:cobble"]])]
    r = run({"x:raw"}, recs + later)
    assert "x:ingot" in r.items
    assert "x:smelt" in r.why("x:ingot")


def test_unknown_type_is_not_available():
    recs = [rcp("x:magic", "weird:altar", ["x:out"], [["x:in"]])]
    assert "x:out" not in run({"x:in"}, recs).items


def test_recipe_without_inputs_never_fires():
    """Receita sem entradas no dump (ex.: smithing que o dump não lê) não é fonte grátis."""
    recs = [rcp("x:free", "minecraft:crafting_shaped", ["x:out"], [])]
    assert "x:out" not in run(set(), recs).items


def test_dimension_gates_naturals():
    p = prog({"minecraft:the_nether": ["x:netherite_scrap"], "qualquer": ["x:everywhere"]})
    r = run(set(), [], p)
    assert "x:netherite_scrap" not in r.items and "x:everywhere" in r.items
    assert "x:netherite_scrap" in run(set(), [], p, dims={"minecraft:overworld", "minecraft:the_nether"}).items


def test_tag_alternative_slot():
    g = reg(item_tags={"forge:ingots/iron": {"minecraft:iron_ingot", "gtceu:wrought_iron_ingot"}})
    recs = [rcp("x:bucket", "minecraft:crafting_shaped", ["minecraft:bucket"], [["#forge:ingots/iron"], ["x:stick"]])]
    assert "minecraft:bucket" in run({"gtceu:wrought_iron_ingot", "x:stick"}, recs, g=g).items
    assert "minecraft:bucket" not in run({"gtceu:wrought_iron_ingot"}, recs, g=g).items  # todo slot precisa


def test_natural_tag_expands():
    g = reg(item_tags={"minecraft:oak_logs": {"minecraft:oak_log", "minecraft:oak_wood"}})
    p = prog({"minecraft:overworld": ["#minecraft:oak_logs"]})
    assert {"minecraft:oak_log", "minecraft:oak_wood"} <= run(set(), [], p, g).items


def test_fluid_slots_and_buckets():
    g = reg(fluids={"minecraft:water", "gtceu:oil"}, fluid_tags={"forge:oil": {"gtceu:oil"}},
            items={"gtceu:oil_bucket", "minecraft:bucket", "minecraft:water_bucket"})
    recs = [rcp("x:wash", "minecraft:crafting_shaped", ["x:clean"], [["x:dirty"]], fluid_inputs=[["#forge:oil"]])]
    assert "x:clean" not in run({"x:dirty"}, recs, g=g).items
    r = run({"x:dirty", "gtceu:oil_bucket"}, recs, g=g)  # fluido vem do balde cheio
    assert "x:clean" in r.items and "gtceu:oil" in r.fluids
    p = prog({"qualquer": ["fluid:minecraft:water"]})
    r = run({"minecraft:bucket"}, [], p, g)  # e o balde vazio enche com o fluido alcançado
    assert "minecraft:water" in r.fluids and "minecraft:water_bucket" in r.items


def test_ebf_needs_coil():
    recs = [rcp("gtceu:electric_blast_furnace/x", "gtceu:electric_blast_furnace", ["x:hot"], [["x:dust"]],
                eut=120, ebf_temp=1800)]
    base = {"x:dust", "gtceu:electric_blast_furnace", "gtceu:lv_energy_input_hatch", "gtceu:lv_steam_turbine"}
    assert "x:hot" not in run(base, recs).items
    assert "x:hot" not in run(base | {"fake:weak_coil"}, recs).items
    assert "x:hot" in run(base | {"gtceu:cupronickel_coil_block"}, recs).items  # 2 hatches LV = MV (128 ≥ 120)
    no_hatch = base - {"gtceu:lv_energy_input_hatch"} | {"gtceu:cupronickel_coil_block"}
    assert "x:hot" not in run(no_hatch, recs).items


def test_gt_veins_give_raw_ore_and_deep_only():
    g = reg(items={"gtceu:raw_diamond", "gtceu:raw_coal", "minecraft:wooden_pickaxe", "minecraft:iron_pickaxe"},
            item_tags={"forge:raw_materials/diamond": {"gtceu:raw_diamond"}, "forge:raw_materials/coal": {"gtceu:raw_coal"}},
            block_tags={"forge:ores/diamond": {"gtceu:diamond_ore"}, "forge:ores/coal": {"gtceu:coal_ore"}},
            block_tiers={"gtceu:diamond_ore": 2},
            pickaxe_tiers={"minecraft:wooden_pickaxe": 0, "minecraft:iron_pickaxe": 2},
            gt_veins=[{"id": "gtceu:diamond_vein", "dims": ["minecraft:overworld"], "min_y": -55, "max_y": -30,
                       "weight": 1, "materials": ["diamond", "coal"]},
                      {"id": "gtceu:coal_vein", "dims": ["minecraft:overworld"], "min_y": 10, "max_y": 140,
                       "weight": 1, "materials": ["coal"]}])
    r = run({"minecraft:wooden_pickaxe"}, [], g=g)
    assert "gtceu:raw_coal" in r.items and "gtceu:raw_diamond" not in r.items  # diamante pede ferro
    r = run({"minecraft:iron_pickaxe"}, [], g=g)
    assert "gtceu:raw_diamond" in r.items and "gtceu:diamond_vein" in r.why("gtceu:raw_diamond")
    ow = {"minecraft:overworld"}
    assert closure.deep_only("gtceu:raw_diamond", ow, prog(), g)
    assert not closure.deep_only("gtceu:raw_coal", ow, prog(), g)  # também vem do veio raso
    assert not closure.deep_only("gtceu:raw_diamond", {"minecraft:the_nether"}, prog(), g)
    assert "gtceu:raw_diamond" not in closure.reach({"minecraft:iron_pickaxe"}, ow, prog(), recipes.Recipes([]), g,
                                                     exclude_deep=True).items


def test_progression_load_reads_naturals(tmp_path):
    (tmp_path / "naturals.yaml").write_text("minecraft:overworld:\n  - x:a\n", encoding="utf-8")
    (tmp_path / "progression.yaml").write_text("manual_types: [minecraft:crafting_shaped]\n"
                                               "steam_max_eut: {lp: 32, hp: 32}\n", encoding="utf-8")
    p = progression.load(tmp_path / "progression.yaml")
    assert p.naturals == {"minecraft:overworld": ["x:a"]} and p.steam_max_eut == {"lp": 32, "hp": 32}


SEQ = rcp("create:sequenced_assembly/pm", "create:sequenced_assembly", ["x:mechanism"],
          [["x:sheet"], ["x:incomplete", "x:cog", "x:big_cog"], ["x:incomplete"]])


def test_sequenced_assembly_transitional_item_is_not_an_input():
    """O item de transição (x:incomplete) nasce dentro da própria montagem; cada passo exige o seu item."""
    p = prog(machines={"create:sequenced_assembly": ["create:deployer"]})
    assert "x:mechanism" in run({"x:sheet", "x:cog", "x:big_cog", "create:deployer"}, [SEQ], p).items
    assert "x:mechanism" not in run({"x:sheet", "x:cog", "create:deployer"}, [SEQ], p).items  # falta um passo


def test_max_eut_cuts_high_tier_recipes():
    seed = {"x:ore", "gtceu:lv_macerator", "gtceu:lv_steam_turbine"}
    assert "x:dust" in run(seed, GT).items
    r = closure.reach(seed, {"minecraft:overworld"}, prog(), recipes.Recipes(GT), reg(), max_eut=8)
    assert "x:dust" not in r.items
    assert closure.max_eut_for("none") == 0 and closure.max_eut_for("mv") == 128


def test_explain_follows_single_missing_input():
    p = prog({"minecraft:the_nether": ["x:far"]})
    recs = [rcp("x:mid", "minecraft:crafting_shaped", ["x:mid"], [["x:far"]]),
            rcp("x:top", "minecraft:crafting_shaped", ["x:top"], [["x:mid"], ["x:mid"]])]
    r = run(set(), recs, p)
    why = closure.explain("x:top", r, {"minecraft:overworld"}, p, recipes.Recipes(recs), reg())
    assert why == "x:mid → x:far → dimensão minecraft:the_nether fechada"


# ---------- dados reais (pulam sem os dumps) ----------

def _real():
    if not (BUILD / "registry_dump.json").exists() or not (BUILD / "recipe_dump.json").exists():
        pytest.skip("sem dump em build/")
    return (progression.load(ROOT / "quests" / "progression.yaml"),
            recipes.load(BUILD / "recipe_dump.json"), registry.load(BUILD / "registry_dump.json"))


def test_real_ids_exist():
    p, _, g = _real()
    missing = [i for i in progression.referenced_items(p) if i not in g.items]
    assert missing == []
    assert [d for d in p.dimension_unlocks if d not in g.dimensions] == []
    assert [d for d in p.naturals if d != "qualquer" and d not in g.dimensions] == []


def test_real_every_recipe_type_classified():
    p, rec, g = _real()
    types = {r["type"] for r in rec.all}
    assert sorted(t for t in types if not closure.type_known(t, p, g)) == []


def test_real_reach_is_fast_and_sane():
    p, rec, g = _real()
    closure.reach(set(), {"minecraft:overworld"}, p, rec, g)  # monta o índice
    t = time.perf_counter()
    r = closure.reach(set(), {"minecraft:overworld"}, p, rec, g)
    assert time.perf_counter() - t < 2.0
    assert {"minecraft:crafting_table", "minecraft:furnace", "minecraft:iron_ingot"} <= r.items
    assert "minecraft:obsidian" not in r.items or "minecraft:diamond_pickaxe" in r.items


def test_real_oil_sprout_is_raw_oil():
    """O broto de petróleo do GT (raw_oil_sprout) põe gtceu:oil_medium; gtceu:oil só sai da sonda (não modelada)."""
    p, _, g = _real()
    srcs = [s for s in closure.build_sources(p, g) if s.dim in ("minecraft:overworld", closure.ANY)]
    natural_fluids = {f for s in srcs for f in s.fluids}
    assert "gtceu:oil_medium" in natural_fluids and "gtceu:oil" not in natural_fluids


def test_real_final_boss_drop_not_natural():
    p, rec, g = _real()
    r = closure.reach(set(), set(g.dimensions), p, rec, g)
    assert not {"ecos:eco_do_arauto", "ecos:selo_restaurado", "ecos:poder_absorvido"} & r.items
