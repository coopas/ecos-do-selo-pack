"""Valida o pack packwiz contra tools/mods.csv."""
import csv
import sys
import tomllib
from pathlib import Path

from paths import PACK, ROOT

META_FOLDERS = ("mods", "resourcepacks", "shaderpacks")
MANIFEST = ROOT / "tools" / "mods.csv"


def load_manifest(path: Path = MANIFEST) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        return [dict(r) for r in csv.DictReader(f) if r["id"] and not r["id"].startswith("#")]


def load_pack_mods(pack_dir: Path = PACK) -> dict[str, dict]:
    mods = {}
    for folder in META_FOLDERS:
        for p in (pack_dir / folder).glob("*.pw.toml"):
            mods[p.name.removesuffix(".pw.toml")] = tomllib.loads(p.read_text(encoding="utf-8"))
    return mods


def check(manifest: list[dict], pack_mods: dict[str, dict]) -> list[str]:
    problems = []
    for row in manifest:
        if row["source"] == "manual":
            continue
        meta = pack_mods.get(row["slug"])
        if meta is None:
            problems.append(f"faltando: {row['id']} ({row['slug']})")
            continue
        if meta.get("side", "both") != row["side"]:
            problems.append(f"side errado: {row['id']} pack={meta.get('side')} manifesto={row['side']}")
    for slug, meta in pack_mods.items():
        dl = meta.get("download", {})
        if not dl.get("url") and "curseforge" not in meta.get("update", {}):
            problems.append(f"download manual (sem url nem metadados cf): {slug}")
    return problems


def main() -> int:
    problems = check(load_manifest(), load_pack_mods())
    for p in problems:
        print(p)
    print("OK" if not problems else f"{len(problems)} problemas")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
