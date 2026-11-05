"""Dados de progressão do jogador (quests/progression.yaml + quests/naturals.yaml) para o motor de fecho.

progression.yaml: dimension_unlocks, manual_types, ignored_types, machines, steam_max_eut, eu_sources, coils,
deep_ok_from_act. naturals.yaml: fontes do mundo por dimensão (formato no comentário do topo do arquivo).
"""
from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class Progression:
    naturals: dict = field(default_factory=dict)  # dimensão | "qualquer" -> [entrada]
    dimension_unlocks: dict = field(default_factory=dict)  # dimensão -> "capitulo/slug" da quest que libera
    manual_types: list = field(default_factory=list)  # tipos sempre disponíveis (aceita curinga fnmatch)
    ignored_types: list = field(default_factory=list)  # tipos que não produzem nada (bans, munição…)
    machines: dict = field(default_factory=dict)  # tipo -> [itens da máquina, um basta]
    steam_max_eut: dict = field(default_factory=lambda: {"lp": 32, "hp": 32})
    eu_sources: list = field(default_factory=list)  # máquina elétrica só conta com uma destas no fecho
    coils: dict = field(default_factory=dict)  # item da bobina -> temperatura
    deep_ok_from_act: int = 1
    act_tier: dict = field(default_factory=dict)  # ato -> tier do GregTech esperado ("none", "lv", "mv"...)
    boss_quest_drops: dict = field(default_factory=dict)  # "capitulo/slug" -> itens do chefe sem task de kill


def load(path: Path | str, naturals: Path | str | None = None) -> Progression:
    """Lê progression.yaml; naturals.yaml vem do mesmo diretório se não for dado."""
    path = Path(path)
    d = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    nat_path = Path(naturals) if naturals else path.with_name("naturals.yaml")
    nat = yaml.safe_load(nat_path.read_text(encoding="utf-8")) if nat_path.exists() else {}
    fields = set(Progression.__dataclass_fields__) - {"naturals"}
    unknown = set(d) - fields
    if unknown:
        raise ValueError(f"{path}: chaves desconhecidas {sorted(unknown)}")
    return Progression(naturals=nat or {}, **d)


def entry_parts(entry) -> tuple[str, list[str] | None, int | None]:
    """Entrada de naturals -> (id, needs, tier). id pode ser item, "#tag" ou "fluid:<id>"."""
    if isinstance(entry, dict):
        return entry["id"], entry.get("needs"), entry.get("tier")
    return entry, None, None


def referenced_items(p: Progression) -> set[str]:
    """Itens (não tags nem fluidos) citados nos dados, para conferir contra o registro."""
    out: set[str] = set()
    for entries in p.naturals.values():
        for e in entries or []:
            id_, needs, _ = entry_parts(e)
            if not id_.startswith(("#", "fluid:")):
                out.add(id_)
            out |= set(needs or [])
    for ms in p.machines.values():
        out |= set(ms)
    out |= set(p.eu_sources) | set(p.coils)
    for items in p.boss_quest_drops.values():
        out |= set(items)
    return out
