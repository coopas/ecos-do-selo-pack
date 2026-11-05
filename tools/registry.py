"""Carrega o dump de registro gerado por kubejs/server_scripts/dev/registry_dump.js."""
import json
from dataclasses import dataclass, field
from pathlib import Path


def _tag(t: str) -> str:
    return t[1:] if t.startswith("#") else t


@dataclass
class Registry:
    items: set[str] = field(default_factory=set)
    fluids: set[str] = field(default_factory=set)
    entities: set[str] = field(default_factory=set)
    item_tags: dict[str, set[str]] = field(default_factory=dict)
    block_tags: dict[str, set[str]] = field(default_factory=dict)
    dimensions: set[str] = field(default_factory=set)
    fluid_tags: dict[str, set[str]] = field(default_factory=dict)
    pickaxe_tiers: dict[str, int] = field(default_factory=dict)  # 0 madeira/ouro, 1 pedra, 2 ferro, 3 diamante, 4 netherite
    block_tiers: dict[str, int] = field(default_factory=dict)  # nível mínimo de picareta (tags needs_*_tool)
    gt_veins: list[dict] = field(default_factory=list)  # {id, dims, min_y, max_y, weight, materials}

    def has_item(self, id_: str) -> bool:
        return id_ in self.items

    def has_tag(self, tag: str) -> bool:
        return _tag(tag) in self.item_tags

    def tag_items(self, tag: str) -> set[str]:
        return self.item_tags.get(_tag(tag), set())

    def has_block_tag(self, tag: str) -> bool:
        return _tag(tag) in self.block_tags

    def block_tag_blocks(self, tag: str) -> set[str]:
        return self.block_tags.get(_tag(tag), set())

    def has_fluid(self, id_: str) -> bool:
        return id_ in self.fluids

    def has_fluid_tag(self, tag: str) -> bool:
        return _tag(tag) in self.fluid_tags

    def fluid_tag_fluids(self, tag: str) -> set[str]:
        return self.fluid_tags.get(_tag(tag), set())

    def has_entity(self, id_: str) -> bool:
        return id_ in self.entities


def load(path: Path | str) -> Registry:
    d = json.loads(Path(path).read_text(encoding="utf-8"))
    return Registry(set(d["items"]), set(d["fluids"]), set(d["entities"]),
                    {k: set(v) for k, v in d["item_tags"].items()},
                    {k: set(v) for k, v in d.get("block_tags", {}).items()},
                    set(d.get("dimensions", [])),
                    {k: set(v) for k, v in d.get("fluid_tags", {}).items()},
                    d.get("pickaxe_tiers", {}), d.get("block_tiers", {}), d.get("gt_veins", []))
