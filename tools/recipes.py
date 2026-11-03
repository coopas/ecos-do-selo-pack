"""Carrega o dump de receitas gerado por kubejs/server_scripts/dev/registry_dump.js."""
import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Recipes:
    all: list[dict] = field(default_factory=list)

    def __post_init__(self):
        self._by_out: dict[str, list[dict]] = {}
        self._by_id: dict[str, dict] = {}
        for r in self.all:
            self._by_id[r["id"]] = r
            for o in r["outputs"]:
                self._by_out.setdefault(o, []).append(r)

    def for_output(self, item_id: str) -> list[dict]:
        return self._by_out.get(item_id, [])

    def by_id(self, recipe_id: str) -> dict | None:
        return self._by_id.get(recipe_id)


def input_ids(recipe: dict) -> set[str]:
    return {alt for slot in recipe["inputs"] for alt in slot}


def load(path: Path | str) -> Recipes:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return Recipes(data["recipes"] if isinstance(data, dict) else data)
