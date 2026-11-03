"""Aplica tools/mods.csv ao pack via packwiz e força o side de cada mod."""
import re
import subprocess
import sys
from pathlib import Path

from check_manifest import META_FOLDERS, load_manifest
from paths import PACK, PACKWIZ


def set_side(path: Path, side: str) -> None:
    text = path.read_text(encoding="utf-8")
    line = f'side = "{side}"'
    if re.search(r'^side = ".*"$', text, flags=re.M):
        text = re.sub(r'^side = ".*"$', line, text, flags=re.M)
    else:
        lines = text.splitlines()
        first_table = next((i for i, l in enumerate(lines) if l.startswith("[")), len(lines))
        lines.insert(first_table, line)
        text = "\n".join(lines) + "\n"
    path.write_text(text, encoding="utf-8")


def find_meta(slug: str) -> Path | None:
    for folder in META_FOLDERS:
        p = PACK / folder / f"{slug}.pw.toml"
        if p.exists():
            return p
    return None


def main() -> int:
    failed = []
    for row in load_manifest():
        if row["source"] == "manual":
            print(f"manual: {row['id']}")
            continue
        if find_meta(row["slug"]) is None:
            cmd = [PACKWIZ, "modrinth" if row["source"] == "mr" else "curseforge", "add", row["slug"], "-y"]
            r = subprocess.run(cmd, cwd=PACK, capture_output=True, text=True, encoding="utf-8", errors="replace")
            if r.returncode != 0 or find_meta(row["slug"]) is None:
                failed.append(row["id"])
                print(f"FALHOU {row['id']}: {(r.stdout + r.stderr).strip()[-400:]}")
                continue
            print(f"adicionado {row['id']}")
        set_side(find_meta(row["slug"]), row["side"])
    subprocess.run([PACKWIZ, "refresh"], cwd=PACK, check=True, capture_output=True)
    print("falhas:", failed or "nenhuma")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
