"""Gera kubejs/assets/ecos/lang/{pt_br,en_us}.json a partir de kubejs/ecos/items.json."""
import json

import ecosdata
from paths import PACK

LANG_DIR = PACK / "kubejs" / "assets" / "ecos" / "lang"


def lang_key(item: dict) -> str:
    kind = "block" if item["kind"] == "block" else "item"
    return f'{kind}.ecos.{item["id"].split(":", 1)[1]}'


def build(items: list[dict], field: str) -> dict[str, str]:
    return {lang_key(i): i[field] for i in items}


def main() -> None:
    items = ecosdata.load().items
    LANG_DIR.mkdir(parents=True, exist_ok=True)
    for name, field in (("pt_br", "pt"), ("en_us", "en")):
        (LANG_DIR / f"{name}.json").write_text(
            json.dumps(build(items, field), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"lang gerado para {len(items)} itens")


if __name__ == "__main__":
    main()
