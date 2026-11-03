"""Gera pack/config/ProjectE/custom_emc.json: EMC 0 (removido) para todo item do GregTech.

Formato descoberto com `projecte removeemc` no servidor: {"entries": [{"item": "<id>", "emc": 0}]}.
"""
import json
from collections.abc import Iterable

import registry
from paths import BUILD, PACK

OUT = PACK / "config" / "ProjectE" / "custom_emc.json"


def build_entries(item_ids: Iterable[str]) -> list[dict]:
    return [{"item": i, "emc": 0} for i in item_ids if i.startswith("gtceu:")]


def main() -> None:
    items = sorted(registry.load(BUILD / "registry_dump.json").items)
    entries = build_entries(items)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"entries": entries}, indent=1) + "\n", encoding="utf-8")
    print(f"{len(entries)} itens do GregTech com EMC removido -> {OUT}")


if __name__ == "__main__":
    main()
