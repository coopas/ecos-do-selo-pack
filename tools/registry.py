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

    def has_entity(self, id_: str) -> bool:
        return id_ in self.entities


def load(path: Path | str) -> Registry:
    d = json.loads(Path(path).read_text(encoding="utf-8"))
    return Registry(set(d["items"]), set(d["fluids"]), set(d["entities"]),
                    {k: set(v) for k, v in d["item_tags"].items()},
                    {k: set(v) for k, v in d.get("block_tags", {}).items()})
