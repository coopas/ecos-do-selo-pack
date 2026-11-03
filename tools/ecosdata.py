"""Dados do pack (pack/kubejs/ecos/*.json): fonte única para KubeJS e testes."""
import json
from dataclasses import dataclass
from pathlib import Path

from paths import PACK

ECOS_DIR = PACK / "kubejs" / "ecos"


def _read(path: Path, default):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


@dataclass
class EcosData:
    items: list
    recipes: dict
    tags: dict
    boss_drops: dict

    def item_ids(self) -> set[str]:
        return {i["id"] for i in self.items}

    def all_recipes(self) -> list[dict]:
        return [r for section in self.recipes.values() for r in section]

    def referenced_ids(self) -> dict[str, set[str]]:
        refs = {"item": set(), "item_tag": set(), "block_tag": set(), "entity": set()}

        def ref(value: str):
            if value.startswith("#"):
                refs["item_tag"].add(value[1:])
            else:
                refs["item"].add(value)

        for r in self.all_recipes():
            refs["item"].add(r["output"])
            for v in r["key"].values():
                ref(v)
        for kind, target in (("item", "item_tag"), ("block", "block_tag")):
            for tag, op in self.tags.get(kind, {}).items():
                refs[target].add(tag)
                for v in op.get("set", []) + op.get("add", []):
                    ref(v)
        for entity, item in self.boss_drops.items():
            refs["entity"].add(entity)
            refs["item"].add(item)
        return refs


def load(directory: Path = ECOS_DIR) -> EcosData:
    return EcosData(_read(directory / "items.json", []),
                    _read(directory / "recipes.json", {"gates": [], "cross": [], "late": []}),
                    _read(directory / "tags.json", {}),
                    _read(directory / "boss_drops.json", {}))
