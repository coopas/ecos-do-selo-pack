"""Motor de fecho da progressão: dado o que o jogador tem (seed) e as dimensões abertas, tudo o que ele produz.

Regra: entram as fontes naturais das dimensões (naturals.yaml + veios do GregTech) cujo `needs`/`tier` já é
satisfeito, mais a seed; depois ponto fixo por fila (índice entrada -> receitas). Uma receita entra quando todo slot
de item e de fluido tem uma alternativa alcançada e a máquina está disponível:
- tipo manual: sempre; tipo ignorado ou desconhecido: nunca;
- outros: algum item da máquina alcançado (progression.machines; tipos gtceu:<x> sem entrada lá resolvem por nome:
  gtceu:<tier>_<x>, gtceu:lp_steam_<x>/hp_steam_<x> ou o controlador gtceu:<x>);
- máquina do GregTech precisa aguentar o `eut`: elétrica de tier T -> V[T] (e uma fonte de EU alcançada); vapor ->
  steam_max_eut; controlador de multibloco -> V[tier do hatch de energia + 1] (dois hatches sobem um tier, como no
  GTCEu) com fonte de EU; `ebf_temp` <= maior bobina alcançada.
Montagem em sequência do Create: o item de transição não é entrada (ver _item_slots).
Receita sem nenhuma entrada no dump (o dump não lê smithing, glifos do Ars…) nunca dispara: não é fonte grátis.
Liberar uma picareta (ou um item de `needs`) reavalia as fontes naturais. Fluido vem de fonte natural, de receita ou
do balde cheio alcançado; balde vazio + fluido alcançado dá o balde cheio.

Veio do GregTech: o minério dá o item `rawOre` do material (como o loot do GTCEu: raw, senão gema, senão pó); o nível
de picareta é o MAIOR `block_tiers` entre os blocos `gtceu:` de `forge:ores/<material>` (sem tag = 0); o veio é
"fundo" quando `max_y < 0`.
"""
import re
from collections import deque
from dataclasses import dataclass, field
from fnmatch import fnmatchcase

import progression as progression_mod

TIERS = ["ulv", "lv", "mv", "hv", "ev", "iv", "luv", "zpm", "uv", "uhv"]
V = [8 * 4 ** i for i in range(len(TIERS))]  # GTValues.V
_TIER_RE = re.compile(rf"^gtceu:({'|'.join(TIERS)})_(.+)$")
_STEAM_RE = re.compile(r"^gtceu:(lp|hp)_steam_(.+)$")
_HATCH_RE = re.compile(rf"^gtceu:({'|'.join(TIERS)})_energy_input_hatch(?:_\d+a)?$")
_BUCKET_PREFIXES = ("skyroot_", "ventium_")  # baldes de madeira do Aether e de ventium do Blue Skies
INF = float("inf")
ANY = "qualquer"


@dataclass
class Source:
    dim: str
    label: str
    items: set[str]
    fluids: set[str]
    needs: frozenset[str] | None = None
    tier: int | None = None  # nível mínimo de picareta (0..4)
    deep: bool = False


@dataclass
class Reach:
    items: set[str] = field(default_factory=set)
    fluids: set[str] = field(default_factory=set)
    _why: dict[str, str] = field(default_factory=dict)

    def why(self, item: str) -> str:
        """Receita ou fonte que trouxe o item (fluido: "fluid:<id>"); "" se não foi alcançado."""
        return self._why.get(item, "")


# ---------- fontes naturais ----------

def _vein_products(material: str, reg) -> set[str]:
    for prefix in ("raw_materials", "gems", "dusts"):
        items = reg.tag_items(f"forge:{prefix}/{material}")
        if items:
            return set(items)
    return set()


def _vein_tier(material: str, reg) -> int:
    blocks = [b for b in reg.block_tag_blocks(f"forge:ores/{material}") if b.startswith("gtceu:")]
    return max((reg.block_tiers.get(b, 0) or 0 for b in blocks), default=0)


def build_sources(prog, reg) -> list[Source]:
    out: list[Source] = []
    for dim, entries in (prog.naturals or {}).items():
        for e in entries or []:
            id_, needs, tier = progression_mod.entry_parts(e)
            items, fluids = set(), set()
            if id_.startswith("fluid:"):
                f = id_[len("fluid:"):]
                fluids = set(reg.fluid_tag_fluids(f)) if f.startswith("#") else {f}
            elif id_.startswith("#"):
                items = set(reg.tag_items(id_))
            else:
                items = {id_}
            label = f"fonte natural em {dim}" + (f" (com {' ou '.join(needs)})" if needs else "")
            out.append(Source(dim, label, items, fluids, frozenset(needs) if needs else None, tier))
    for v in reg.gt_veins:
        deep = v["max_y"] < 0
        for dim in v["dims"]:
            for m in v["materials"]:
                items = _vein_products(m, reg)
                if items:
                    out.append(Source(dim, f"veio {v['id']} em {dim} (y {v['min_y']}..{v['max_y']})", items, set(),
                                      None, _vein_tier(m, reg), deep))
    return out


# ---------- máquinas ----------

def _manual(t: str, prog) -> bool:
    return any(fnmatchcase(t, pat) for pat in prog.manual_types)


def _ignored(t: str, prog) -> bool:
    return any(fnmatchcase(t, pat) for pat in prog.ignored_types)


def machine_candidates(t: str, prog) -> list[str]:
    if t in prog.machines:
        return list(prog.machines[t] or [])
    ns, _, x = t.partition(":")
    if ns != "gtceu":
        return []
    return [f"gtceu:{p}_{x}" for p in TIERS] + [f"gtceu:lp_steam_{x}", f"gtceu:hp_steam_{x}", f"gtceu:{x}"]


def type_known(t: str, prog, reg) -> bool:
    """Tipo classificado: manual, ignorado, mapeado em machines ou resolvido por nome no registro."""
    if _manual(t, prog) or _ignored(t, prog) or t in prog.machines:
        return True
    return any(m in reg.items for m in machine_candidates(t, prog))


def _machine_kind(m: str):
    if mt := _STEAM_RE.match(m):
        return ("steam", mt.group(1))
    if mt := _TIER_RE.match(m):
        return ("tier", TIERS.index(mt.group(1)))
    if m.startswith("gtceu:"):
        return ("ctrl", None)
    return ("plain", None)


SEQUENCED = "create:sequenced_assembly"


def _item_slots(r: dict) -> list[list[str]]:
    """Slots de item da receita. Montagem em sequência do Create: o dump traz o item de transição (o slot final, sozinho)
    misturado aos passos; ele nasce dentro da montagem, então sai, e cada item que sobra num passo vira slot próprio."""
    slots = r["inputs"]
    if r["type"] != SEQUENCED or len(slots) < 2 or len(slots[-1]) != 1:
        return slots
    trans = slots[-1][0]
    out = [slots[0]]
    for slot in slots[1:]:
        if trans in slot:
            out += [[a] for a in slot if a != trans]
        else:
            out.append(slot)
    return out


# ---------- índice (montado uma vez por prog/rec/reg) ----------

class ClosureIndex:
    def __init__(self, prog, rec, reg):
        self.prog, self.reg = prog, reg
        self.sources = build_sources(prog, reg)
        self.pickaxe = dict(reg.pickaxe_tiers)
        self.needs_items = {n for s in self.sources if s.needs for n in s.needs}
        self.coils = dict(prog.coils)
        self.eu_sources = set(prog.eu_sources)

        self.r_id, self.r_type, self.r_out, self.r_fout, self.r_eut, self.r_ebf = [], [], [], [], [], []
        self.r_nslots: list[int] = []
        self.slot_recipe: list[int] = []
        self.item_slots: dict[str, list[int]] = {}
        self.fluid_slots: dict[str, list[int]] = {}
        self.type_mode: dict[str, object] = {}  # "manual" | "none" | [(item, kind)]
        self.machine_types: dict[str, set[str]] = {}
        self.electric_types: set[str] = set()
        for r in rec.all:
            if not r["inputs"] and not r.get("fluid_inputs"):
                continue  # entradas desconhecidas: nunca dispara
            t = r["type"]
            if t not in self.type_mode:
                self._classify(t)
            if self.type_mode[t] == "none":
                continue
            ri = len(self.r_id)
            self.r_id.append(r["id"]); self.r_type.append(t)
            self.r_out.append(r["outputs"]); self.r_fout.append(r.get("fluid_outputs") or [])
            self.r_eut.append(r.get("eut") or 0); self.r_ebf.append(r.get("ebf_temp") or 0)
            n = 0
            for slot in _item_slots(r):
                alts = set()
                for a in slot:
                    alts |= set(reg.tag_items(a)) if a.startswith("#") else {a}
                self._add_slot(ri, alts, self.item_slots)
                n += 1
            for slot in r.get("fluid_inputs") or []:
                alts = set()
                for a in slot:
                    alts |= set(reg.fluid_tag_fluids(a)) if a.startswith("#") else {a}
                self._add_slot(ri, alts, self.fluid_slots)
                n += 1
            self.r_nslots.append(n)

        self.bucket_fluid: dict[str, str] = {}
        for i in reg.items:
            if not i.endswith("_bucket"):
                continue
            ns, _, name = i.partition(":")
            name = name[: -len("_bucket")]
            cands = [f"{ns}:{name}"]
            for p in _BUCKET_PREFIXES:
                if name.startswith(p):
                    cands.append(f"minecraft:{name[len(p):]}")
            for f in cands:
                if f in reg.fluids:
                    self.bucket_fluid[i] = f
                    break
        self.fluid_bucket: dict[str, str] = {}
        for i, f in sorted(self.bucket_fluid.items()):
            if i.startswith("minecraft:") or f not in self.fluid_bucket:
                self.fluid_bucket[f] = i
            if i == f"{f}_bucket":
                self.fluid_bucket[f] = i

    def _add_slot(self, ri: int, alts: set[str], index: dict[str, list[int]]):
        gs = len(self.slot_recipe)
        self.slot_recipe.append(ri)
        for a in alts:
            index.setdefault(a, []).append(gs)

    def _classify(self, t: str):
        prog = self.prog
        if _manual(t, prog):
            self.type_mode[t] = "manual"
            return
        cands = [] if _ignored(t, prog) else machine_candidates(t, prog)
        if not cands:
            self.type_mode[t] = "none"
            return
        mode = [(m, _machine_kind(m)) for m in cands]
        self.type_mode[t] = mode
        for m, kind in mode:
            self.machine_types.setdefault(m, set()).add(t)
            if kind[0] in ("tier", "ctrl"):
                self.electric_types.add(t)


_CACHE: list[tuple] = []


def index_for(prog, rec, reg) -> ClosureIndex:
    """Índice memorizado pela identidade de (prog, rec, reg): não mude os objetos depois de usar."""
    for p, r, g, idx in _CACHE:
        if p is prog and r is rec and g is reg:
            return idx
    idx = ClosureIndex(prog, rec, reg)
    _CACHE.append((prog, rec, reg, idx))
    del _CACHE[:-4]
    return idx


# ---------- fecho ----------

def max_eut_for(tier: str | None) -> float:
    """Teto de EU/t de um tier ("none" = nenhuma receita do GregTech que gaste EU; None = sem teto)."""
    if tier is None:
        return INF
    return 0 if tier == "none" else V[TIERS.index(tier)]


def reach(seed: set[str], dims: set[str], prog, rec, reg, *, exclude_deep: bool = False,
          max_eut: float = INF, index: ClosureIndex | None = None) -> Reach:
    """Tudo o que se produz a partir da seed (itens; "fluid:<id>" para fluido) com as dimensões abertas.

    exclude_deep=True ignora veios com max_y < 0 (para saber se um item depende só de veio fundo);
    max_eut corta receitas com eut acima dele (para saber se um item depende de tier alto)."""
    idx = index or index_for(prog, rec, reg)
    out = Reach()
    items, fluids, why = out.items, out.fluids, out._why
    queue: deque = deque()

    def add_item(i: str, reason: str):
        if i not in items:
            items.add(i)
            why[i] = reason
            queue.append((0, i))

    def add_fluid(f: str, reason: str):
        if f not in fluids:
            fluids.add(f)
            why["fluid:" + f] = reason
            queue.append((1, f))

    for s in seed:
        if s.startswith("fluid:"):
            add_fluid(s[len("fluid:"):], "semente")
        else:
            add_item(s, "semente")

    pending = [s for s in idx.sources if (s.dim == ANY or s.dim in dims) and not (exclude_deep and s.deep)]
    state = {"pick": -1, "eu": False, "hatch": -1, "coil": 0}

    def check_sources():
        nonlocal pending
        keep = []
        for s in pending:
            if (s.tier is None or state["pick"] >= s.tier) and (s.needs is None or not s.needs.isdisjoint(items)):
                for i in s.items:
                    add_item(i, s.label)
                for f in s.fluids:
                    add_fluid(f, s.label)
            else:
                keep.append(s)
        pending = keep

    def cap(m: str, kind) -> float:
        k, arg = kind
        if k == "plain":
            return INF
        if k == "steam":
            return idx.prog.steam_max_eut.get(arg, 0)
        if not state["eu"]:
            return 0
        if k == "tier":
            return V[arg]
        return V[min(state["hatch"] + 1, len(V) - 1)] if state["hatch"] >= 0 else 0

    def available(ri: int) -> bool:
        mode = idx.type_mode[idx.r_type[ri]]
        if mode == "manual":
            return True
        ebf = idx.r_ebf[ri]
        if ebf and state["coil"] < ebf:
            return False
        eut = idx.r_eut[ri]
        if eut > max_eut:
            return False
        return any(m in items and eut <= cap(m, kind) for m, kind in mode)

    blocked: dict[str, list[int]] = {}

    def fire(ri: int):
        reason = f"receita {idx.r_id[ri]} ({idx.r_type[ri]})"
        for o in idx.r_out[ri]:
            add_item(o, reason)
        for f in idx.r_fout[ri]:
            add_fluid(f, reason)

    def try_fire(ri: int):
        if available(ri):
            fire(ri)
        else:
            blocked.setdefault(idx.r_type[ri], []).append(ri)

    def recheck(types):
        for t in types:
            waiting = blocked.get(t)
            if not waiting:
                continue
            still = []
            for ri in waiting:
                if available(ri):
                    fire(ri)
                else:
                    still.append(ri)
            blocked[t] = still

    remaining = list(idx.r_nslots)
    sat = bytearray(len(idx.slot_recipe))

    def satisfy(slots):
        for gs in slots:
            if not sat[gs]:
                sat[gs] = 1
                ri = idx.slot_recipe[gs]
                remaining[ri] -= 1
                if remaining[ri] == 0:
                    try_fire(ri)

    check_sources()
    while queue:
        kind, x = queue.popleft()
        if kind == 1:
            if "minecraft:bucket" in items and x in idx.fluid_bucket:
                add_item(idx.fluid_bucket[x], f"balde cheio com {x}")
            satisfy(idx.fluid_slots.get(x, ()))
            continue
        tier = idx.pickaxe.get(x)
        if (tier is not None and tier > state["pick"]) or x in idx.needs_items:
            state["pick"] = max(state["pick"], tier if tier is not None else -1)
            check_sources()
        if x in idx.bucket_fluid:
            add_fluid(idx.bucket_fluid[x], f"balde {x}")
        if x == "minecraft:bucket":
            for f in list(fluids):
                if f in idx.fluid_bucket:
                    add_item(idx.fluid_bucket[f], f"balde cheio com {f}")
        satisfy(idx.item_slots.get(x, ()))
        grid = False
        if x in idx.eu_sources and not state["eu"]:
            state["eu"] = grid = True
        if x.startswith("gtceu:") and (mh := _HATCH_RE.match(x)) and TIERS.index(mh.group(1)) > state["hatch"]:
            state["hatch"] = TIERS.index(mh.group(1))
            grid = True
        if idx.coils.get(x, 0) > state["coil"]:
            state["coil"] = idx.coils[x]
            grid = True
        if grid:
            recheck(idx.electric_types | set(blocked))
        elif x in idx.machine_types:
            recheck(idx.machine_types[x])
    return out


def deep_only(item: str, dims: set[str], prog, reg) -> bool:
    """O item só vem, direto do mundo nessas dimensões, de veio fundo (max_y < 0)? Receitas não contam."""
    srcs = [s for s in build_sources(prog, reg) if (s.dim == ANY or s.dim in dims) and item in s.items]
    return bool(srcs) and all(s.deep for s in srcs)


# ---------- diagnóstico: o que falta para um item fora do fecho ----------

def _missing_options(target: str, r: Reach, dims: set[str], idx: ClosureIndex, rec, reg,
                     max_eut: float = INF) -> list[tuple[int, list]]:
    """Cada jeito de obter o alvo (item, "#tag" ou "fluid:<id>") -> (custo, o que falta nele), com o que falta em
    [("alvo", x) | ("motivo", texto)]. Receita de tipo sem máquina no modelo custa mais que qualquer outra."""
    if target.startswith("#"):
        return [opt for m in sorted(reg.tag_items(target)) for opt in _missing_options(m, r, dims, idx, rec, reg, max_eut)]
    fluid = target.startswith("fluid:")
    x = target[len("fluid:"):] if fluid else target
    if fluid and x.startswith("#"):
        return [opt for f in sorted(reg.fluid_tag_fluids(x))
                for opt in _missing_options("fluid:" + f, r, dims, idx, rec, reg, max_eut)]
    opts: list[tuple[int, list]] = []
    pick = max((idx.pickaxe[i] for i in r.items if i in idx.pickaxe), default=-1)
    for s in idx.sources:
        if x not in (s.fluids if fluid else s.items):
            continue
        miss = []
        if s.dim != ANY and s.dim not in dims:
            miss.append(("motivo", f"dimensão {s.dim} fechada"))
        if s.tier is not None and pick < s.tier:
            miss.append(("motivo", f"picareta nível {s.tier} ({s.label})"))
        if s.needs and s.needs.isdisjoint(r.items):
            miss.append(("alvo", sorted(s.needs)[0]) if len(s.needs) == 1 else ("motivo", " ou ".join(sorted(s.needs))))
        opts.append((len(miss), miss))
    eu = not idx.eu_sources.isdisjoint(r.items)
    hatch = max((TIERS.index(m.group(1)) for i in r.items if i.startswith("gtceu:") and (m := _HATCH_RE.match(i))),
                default=-1)
    coil = max((t for i, t in idx.coils.items() if i in r.items), default=0)
    for raw in (rec.fluid_producers(x) if fluid else rec.for_output(x)):
        if not raw["inputs"] and not raw.get("fluid_inputs"):
            continue
        t = raw["type"]
        if t not in idx.type_mode:
            idx._classify(t)
        mode = idx.type_mode[t]
        if mode == "none":
            opts.append((99, [("motivo", f"receita {raw['id']}: tipo {t} sem máquina no modelo")]))
            continue
        miss = []
        for slot in _item_slots(raw):
            alts = set()
            for a in slot:
                alts |= set(reg.tag_items(a)) if a.startswith("#") else {a}
            if alts.isdisjoint(r.items):
                miss.append(("alvo", slot[0]))
        for slot in raw.get("fluid_inputs") or []:
            alts = set()
            for a in slot:
                alts |= set(reg.fluid_tag_fluids(a)) if a.startswith("#") else {a}
            if alts.isdisjoint(r.fluids):
                miss.append(("alvo", "fluid:" + slot[0]))
        eut = raw.get("eut") or 0
        if eut > max_eut:
            need = next((TIERS[i] for i, v in enumerate(V) if v >= eut), "uhv")
            miss.append(("motivo", f"receita {raw['id']} de {eut} EU/t ({need})"))
        elif mode != "manual":
            have = [(m, k) for m, k in mode if m in r.items]
            if not have:
                names = [m for m, _ in mode if m in reg.items] or [m for m, _ in mode]
                miss.append(("motivo", f"máquina {names[0]} ({t})"))
            else:
                def cap(k):
                    if k[0] == "plain":
                        return INF
                    if k[0] == "steam":
                        return idx.prog.steam_max_eut.get(k[1], 0)
                    if not eu:
                        return 0
                    return V[k[1]] if k[0] == "tier" else (V[min(hatch + 1, len(V) - 1)] if hatch >= 0 else 0)
                if not any(eut <= cap(k) for _, k in have):
                    need = next((TIERS[i] for i, v in enumerate(V) if v >= eut), "uhv")
                    miss.append(("motivo", f"máquina {t} que aguente {eut} EU/t ({need})"
                                 + ("" if eu else " e uma fonte de EU")))
            if (raw.get("ebf_temp") or 0) > coil:
                miss.append(("motivo", f"bobina de {raw['ebf_temp']} K"))
        opts.append((len(miss), miss))
    return opts


def explain(target: str, r: Reach, dims: set[str], prog, rec, reg, *, index: ClosureIndex | None = None,
            max_eut: float = INF, depth: int = 10, budget: int = 400) -> str:
    """O que faltou no caminho mais curto até o alvo fora do fecho: "a → b → motivos".

    Busca em largura: um jeito de obter o item em que falta UMA coisa desce para ela; um jeito em que faltam várias
    (ou só motivos: máquina, dimensão, picareta) encerra o caminho. Vence o caminho mais curto e, nele, o jeito com
    menos faltas distintas. Jeitos que voltam a um item da cadeia (bloco <-> lingote, desmontar a própria peça) não
    contam. `budget` limita os nós visitados."""
    idx = index or index_for(prog, rec, reg)

    def items_of(x: str) -> set[str]:
        if x.startswith("fluid:#"):
            return {"fluid:" + f for f in reg.fluid_tag_fluids(x[len("fluid:"):])}
        return set(reg.tag_items(x)) if x.startswith("#") else {x}

    level = [(target, [], items_of(target) | {target})]
    loop_reason = None
    for _ in range(depth + 1):
        found, nxt = [], []
        for cur, chain, seen in level:
            budget -= 1
            if budget < 0:
                break
            opts = _missing_options(cur, r, dims, idx, rec, reg, max_eut)
            if not opts:
                found.append((1, chain, "nenhuma receita nem fonte natural"))
                continue
            for cost, miss in opts:
                miss = list(dict.fromkeys(miss))  # 9 slots da mesma tag contam uma vez
                if any(k == "alvo" and (v in seen or not items_of(v).isdisjoint(seen)) for k, v in miss):
                    loop_reason = loop_reason or ", ".join(v for _, v in miss)
                    continue
                if len(miss) == 1 and miss[0][0] == "alvo":
                    v = miss[0][1]
                    nxt.append((v, chain + [v], seen | items_of(v) | {v}))
                else:
                    found.append((cost if cost >= 99 else len(miss), chain, ", ".join(v for _, v in miss) or "?"))
        if found:
            _, chain, reason = min(found, key=lambda f: f[0])
            return " → ".join(chain + [reason])
        if not nxt or budget < 0:
            break
        seen_nodes = set()
        level = [n for n in nxt if not (n[0] in seen_nodes or seen_nodes.add(n[0]))]
    return f"só por ciclo ({loop_reason})" if loop_reason else "caminho longo demais para explicar"
