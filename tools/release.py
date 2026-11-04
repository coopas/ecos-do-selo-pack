"""Gera os pacotes de lançamento apontando para a URL pública do pack.

Uso: python tools/release.py [--url URL]
Saída em build/release/:
  EcosDoSelo-<versão>.zip           instância do Prism (importar no Prism; atualiza sozinha ao abrir)
  EcosDoSelo-Servidor-<versão>.zip  pacote do servidor (sem mundo, logs ou arquivos de teste; eula=false)
"""
import argparse
import shutil
import tomllib
import zipfile
from pathlib import Path

import build_prism
import build_server
from paths import BUILD, PACK

PUBLIC_URL = "https://raw.githubusercontent.com/coopas/ecos-do-selo-pack/main/pack/pack.toml"
OUT = BUILD / "release"
# Nunca vão no pacote: mundo e estado do servidor de teste, logs e artefatos de desenvolvimento.
EXCLUDE_DIRS = {"world", "logs", "crash-reports", "debug", "kubejs/exported", "kubejs/config"}
EXCLUDE_FILES = {"usercache.json", "ops.json", "banned-ips.json", "banned-players.json", "whitelist.json"}


def _excluded(rel: str) -> bool:
    return rel in EXCLUDE_FILES or any(rel == d or rel.startswith(d + "/") for d in EXCLUDE_DIRS)


def zip_server(src: Path, dest: Path, pack_url: str) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(src.rglob("*")):
            rel = f.relative_to(src).as_posix()
            if not f.is_file() or _excluded(rel) or rel in ("eula.txt", "pack-url.txt"):
                continue
            z.write(f, rel)
        z.writestr("eula.txt", "eula=false\n")  # cada dono de servidor aceita a EULA por conta própria
        z.writestr("pack-url.txt", pack_url + "\n")
    return dest


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default=PUBLIC_URL)
    url = ap.parse_args().url
    version = tomllib.loads((PACK / "pack.toml").read_text(encoding="utf-8"))["version"]
    if OUT.exists():
        shutil.rmtree(OUT)
    server = build_server.build(pack_url=url)
    print(zip_server(server, OUT / f"EcosDoSelo-Servidor-{version}.zip", url))
    prism_zip = build_prism.build(url, out=BUILD / "prism-release")
    final = OUT / prism_zip.name
    shutil.move(str(prism_zip), final)
    print(final)


if __name__ == "__main__":
    main()
