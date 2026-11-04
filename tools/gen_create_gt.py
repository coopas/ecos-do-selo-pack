"""Gera pack/kubejs/ecos/create_gt.json: minério do GregTech no Create, ligas na batedeira e redstone do cascalho.

Lê build/registry_dump.json (e build/recipe_dump.json, para não duplicar prensas do Create e para achar as moagens
de compat do Create que pegam o mesmo minério bruto que as nossas: essas vão em "remove")."""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import registry  # noqa: E402
from paths import BUILD, PACK  # noqa: E402

OUT = PACK / "kubejs" / "ecos" / "create_gt.json"

# create:crushing/gravel original (data/create/recipes/crushing/gravel.json do Create 6.0.8).
# O recipe_dump só lista as saídas sem chance (areia), então flint e argila ficam aqui.
GRAVEL_KEEP = [{"item": "minecraft:sand", "count": 1},
               {"item": "minecraft:flint", "chance": 0.1},
               {"item": "minecraft:clay_ball", "chance": 0.05}]
GRAVEL_EXTRA = {"item": "minecraft:redstone", "chance": 0.1}

ALLOYS = {  # nome: (saída, quantidade, [(tag, quantidade)])
    "bronze": ("gtceu:bronze_ingot", 4, [("forge:ingots/copper", 3), ("forge:ingots/tin", 1)]),
    "tin_alloy": ("gtceu:tin_alloy_ingot", 2, [("forge:ingots/iron", 1), ("forge:ingots/tin", 1)]),
    "cupronickel": ("gtceu:cupronickel_ingot", 2, [("forge:ingots/copper", 1), ("forge:ingots/nickel", 1)]),
    "invar": ("gtceu:invar_ingot", 3, [("forge:ingots/iron", 2), ("forge:ingots/nickel", 1)]),
    "red_alloy": ("gtceu:red_alloy_ingot", 1, [("forge:ingots/copper", 1), ("forge:dusts/redstone", 4)]),
}


def _pressed_inputs(reg, recipes) -> set[str]:
    """Itens aceitos por alguma receita create:pressing que não seja nossa (tags expandidas)."""
    out = set()
    for r in recipes or []:
        if r.get("type") == "create:pressing" and not r.get("id", "").startswith("ecos:"):
            for slot in r.get("inputs", []):
                for s in slot:
                    out |= reg.tag_items(s) if s.startswith("#") else {s}
    return out


def _crushing_dupes(recipes, materials) -> set[str]:
    """Receitas create:crushing que não são nossas e pegam #forge:raw_materials/<m> de um material que geramos
    (ex.: create:crushing/raw_tin, compat do Create): duas moagens para o mesmo item no JEI e no moedor."""
    out = set()
    for r in recipes or []:
        if r.get("type") != "create:crushing" or r.get("id", "").startswith("ecos:"):
            continue
        tags = {s[1:] for slot in r.get("inputs", []) for s in slot if s.startswith("#")}
        if any(f"forge:raw_materials/{m}" in tags for m in materials):
            out.add(r["id"])
    return out


def _ingredient(reg, tag: str, item: str) -> dict:
    return {"tag": tag} if reg.has_tag(tag) else {"item": item}


def build(reg, recipes=None, keep_remove=()) -> dict:
    """keep_remove: o "remove" do create_gt.json anterior. Depois de removidas, as receitas somem do recipe_dump;
    sem isso, regenerar com o dump novo devolveria a duplicata. Só fica o que ainda é de um material gerado."""
    crushing, splashing, pressing, mixing = {}, {}, {}, {}
    for raw in sorted(i for i in reg.items if i.startswith("gtceu:raw_")):
        m = raw[len("gtceu:raw_"):]
        crushed, purified = f"gtceu:crushed_{m}_ore", f"gtceu:purified_{m}_ore"
        if not (reg.has_item(crushed) and reg.has_item(purified)):
            continue
        crushing[m] = {"ingredients": [_ingredient(reg, f"forge:raw_materials/{m}", raw)],
                       "results": [{"item": crushed, "count": 1}, {"item": crushed, "chance": 0.3}],
                       "processingTime": 200}
        splashing[m] = {"ingredients": [{"item": crushed}],
                        "results": [{"item": purified, "count": 1}]}
    pressed = _pressed_inputs(reg, recipes)
    for tag in sorted(reg.item_tags):
        mt = re.fullmatch(r"forge:ingots/([a-z0-9_]+)", tag)
        if not mt:
            continue
        m, plate = mt[1], f"gtceu:{mt[1]}_plate"
        if not reg.has_item(plate) or not reg.tag_items(tag):
            continue
        if reg.tag_items(tag) & pressed:
            continue
        pressing[m] = {"ingredients": [{"tag": tag}], "results": [{"item": plate, "count": 1}]}
    for name, (out, n, ins) in ALLOYS.items():
        if not reg.has_item(out) or any(not reg.has_tag(t) for t, _ in ins):
            continue
        mixing[name] = {"ingredients": [{"tag": t} for t, q in ins for _ in range(q)],
                        "results": [{"item": out, "count": n}],
                        "heatRequirement": "heated"}
    gravel = {"ingredients": [{"item": "minecraft:gravel"}],
              "results": GRAVEL_KEEP + [GRAVEL_EXTRA], "processingTime": 250}
    remove = _crushing_dupes(recipes, crushing)
    pre = "create:crushing/raw_"
    remove |= {i for i in keep_remove if i.startswith(pre) and i[len(pre):] in crushing}
    return {"crushing": crushing, "splashing": splashing, "pressing": pressing,
            "mixing": mixing, "gravel": gravel, "remove": sorted(remove)}


def write(reg, out: Path, recipes=None) -> int:
    old = json.loads(out.read_text(encoding="utf-8")).get("remove", []) if out.exists() else []
    d = build(reg, recipes, old)
    out.write_text(json.dumps(d, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return sum(len(d[k]) for k in ("crushing", "splashing", "pressing", "mixing")) + 1


def main() -> int:
    reg = registry.load(BUILD / "registry_dump.json")
    rd = json.loads((BUILD / "recipe_dump.json").read_text(encoding="utf-8"))["recipes"]
    gravel = [r for r in rd if r["id"] == "create:crushing/gravel"]
    # dump feito com o 25_ecos_create_gt.js já ativo: a original foi trocada pela ecos:create_gt/gravel
    if not gravel and any(r["id"] == "ecos:create_gt/gravel" for r in rd):
        gravel = [r for r in rd if r["id"] == "ecos:create_gt/gravel"]
    if not gravel:
        raise SystemExit("create:crushing/gravel ausente do recipe_dump.json")
    for o in gravel[0]["outputs"]:  # o dump só traz as saídas sem chance: devem estar entre as mantidas
        if o not in {k["item"] for k in GRAVEL_KEEP}:
            raise SystemExit(f"saída nova do cascalho no dump: {o}")
    n = write(reg, OUT, rd)
    rm = json.loads(OUT.read_text(encoding="utf-8"))["remove"]
    print(f"{n} receitas -> {OUT}; {len(rm)} moagens do Create removidas: {', '.join(rm)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
