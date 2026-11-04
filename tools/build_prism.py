"""Monta a instância do Prism (pasta + zip importável)."""
import argparse
import json
import shutil
import tomllib
import zipfile
from pathlib import Path

from paths import BUILD, CACHE, PACK, ROOT

INSTANCE_NAME = "Ecos do Selo"
ICON = ROOT / "tools" / "prism" / "ecos_do_selo.png"


def instance_cfg(pack_url: str, name: str = INSTANCE_NAME) -> str:
    return "\n".join([
        "[General]",
        "ConfigVersion=1.3",
        "InstanceType=OneSix",
        f"name={name}",
        "iconKey=ecos_do_selo",
        "AutomaticJava=true",
        "OverrideMemory=true",
        "MinMemAlloc=2048",
        "MaxMemAlloc=6144",
        "OverrideCommands=true",
        # Qt INI: valor inteiro entre aspas e aspas internas escapadas; senão o Prism lê "$INST_JAVA-jar"
        f'PreLaunchCommand="\\"$INST_JAVA\\" -jar packwiz-installer-bootstrap.jar {pack_url}"',
        "",
    ])


def mmc_pack(forge_version: str) -> dict:
    return {"formatVersion": 1, "components": [
        {"uid": "net.minecraft", "version": "1.20.1", "important": True},
        {"uid": "net.minecraftforge", "version": forge_version},
    ]}


def build(pack_url: str, out: Path = BUILD / "prism", forge_version: str | None = None,
          pack_version: str | None = None, bootstrap_jar: Path | None = None,
          name: str = INSTANCE_NAME) -> Path:
    if forge_version is None or pack_version is None:
        meta = tomllib.loads((PACK / "pack.toml").read_text(encoding="utf-8"))
        forge_version = forge_version or meta["versions"]["forge"]
        pack_version = pack_version or meta["version"]
    if bootstrap_jar is None:
        from build_server import BOOTSTRAP_URL, download
        bootstrap_jar = download(BOOTSTRAP_URL, CACHE / "packwiz-installer-bootstrap.jar")
    if out.exists():
        shutil.rmtree(out)
    (out / "minecraft").mkdir(parents=True)
    (out / "instance.cfg").write_text(instance_cfg(pack_url, name), encoding="utf-8")
    (out / "mmc-pack.json").write_text(json.dumps(mmc_pack(forge_version), indent=2), encoding="utf-8")
    shutil.copy2(bootstrap_jar, out / "minecraft" / "packwiz-installer-bootstrap.jar")
    icon = ICON if ICON.exists() else None
    if icon:  # gerado por tools/integrate_images.py
        shutil.copy2(icon, out / "ecos_do_selo.png")
    zpath = out.parent / f"EcosDoSelo-{pack_version}.zip"
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(out.rglob("*")):
            if f.is_file():
                z.write(f, f.relative_to(out).as_posix())
    return zpath


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True)
    print(build(ap.parse_args().url))
