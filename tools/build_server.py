"""Monta o pacote de servidor portátil em build/server."""
import contextlib
import shutil
import subprocess
import sys
import time
import tomllib
import urllib.request
from pathlib import Path

from paths import BUILD, CACHE, JAVA17, PACK, PACKWIZ, ROOT

TEMPLATE = ROOT / "tools" / "server_template"
BOOTSTRAP_URL = "https://github.com/packwiz/packwiz-installer-bootstrap/releases/latest/download/packwiz-installer-bootstrap.jar"
FORGE_URL = "https://maven.minecraftforge.net/net/minecraftforge/forge/1.20.1-{v}/forge-1.20.1-{v}-installer.jar"
SERVE_PORT = 8089
KEEP_IF_EXISTS = {"server.properties", "eula.txt", "user_jvm_args.txt"}
UA = {"User-Agent": "ecos-do-selo-modpack-builder"}


def forge_version(pack_dir: Path = PACK) -> str:
    return tomllib.loads((pack_dir / "pack.toml").read_text(encoding="utf-8"))["versions"]["forge"]


def copy_template(out: Path, forge_version: str) -> None:
    out.mkdir(parents=True, exist_ok=True)
    for src in TEMPLATE.iterdir():
        dest = out / src.name
        if src.name in KEEP_IF_EXISTS and dest.exists():
            continue
        text = src.read_text(encoding="utf-8").replace("FORGEVER", forge_version)
        dest.write_text(text, encoding="utf-8", newline="\r\n" if src.suffix == ".bat" else "\n")


@contextlib.contextmanager
def eula_accepted(server_dir: Path):
    """Aceita a EULA só durante o teste local e restaura o arquivo original depois."""
    eula = server_dir / "eula.txt"
    original = eula.read_text() if eula.exists() else None
    eula.write_text("eula=true\n")
    try:
        yield
    finally:
        if original is None:
            eula.unlink(missing_ok=True)
        else:
            eula.write_text(original)


def prune_client_mods(out: Path, pack_dir: Path = PACK) -> list[str]:
    removed = []
    for meta in (pack_dir / "mods").glob("*.pw.toml"):
        data = tomllib.loads(meta.read_text(encoding="utf-8"))
        if data.get("side") == "client":
            jar = out / "mods" / data["filename"]
            if jar.exists():
                jar.unlink()
                removed.append(data["filename"])
    return sorted(removed)


def download(url: str, dest: Path) -> Path:
    if not dest.exists():
        dest.parent.mkdir(parents=True, exist_ok=True)
        tmp = dest.with_suffix(".part")
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r, open(tmp, "wb") as f:
            shutil.copyfileobj(r, f)
        tmp.replace(dest)
    return dest


@contextlib.contextmanager
def serve_pack(port: int = SERVE_PORT):
    proc = subprocess.Popen([PACKWIZ, "serve", "-p", str(port)], cwd=PACK,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    url = f"http://localhost:{port}/pack.toml"
    try:
        for _ in range(60):
            try:
                urllib.request.urlopen(url, timeout=2)
                break
            except OSError:
                time.sleep(0.5)
        else:
            raise RuntimeError("packwiz serve não respondeu")
        yield url
    finally:
        proc.terminate()
        proc.wait(timeout=10)


def install_mods(out: Path, pack_url: str) -> None:
    jar = download(BOOTSTRAP_URL, CACHE / "packwiz-installer-bootstrap.jar")
    shutil.copy2(jar, out / "packwiz-installer-bootstrap.jar")
    subprocess.run([str(JAVA17), "-jar", "packwiz-installer-bootstrap.jar", "-g", "-s", "server", pack_url],
                   cwd=out, check=True)


def install_forge(out: Path, version: str) -> None:
    if (out / "libraries" / "net" / "minecraftforge" / "forge" / f"1.20.1-{version}").exists():
        return
    jar = download(FORGE_URL.format(v=version), CACHE / f"forge-{version}-installer.jar")
    subprocess.run([str(JAVA17), "-jar", str(jar), "--installServer"], cwd=out, check=True,
                   stdout=subprocess.DEVNULL)
    for junk in ("run.bat", "run.sh"):
        (out / junk).unlink(missing_ok=True)


def build(out: Path = BUILD / "server", pack_url: str | None = None) -> Path:
    version = forge_version()
    out.mkdir(parents=True, exist_ok=True)
    install_forge(out, version)
    if pack_url:
        install_mods(out, pack_url)
    else:
        with serve_pack() as url:
            install_mods(out, url)
    removed = prune_client_mods(out)
    if removed:
        print("removidos (client-only):", removed)
    copy_template(out, version)
    if pack_url:
        (out / "pack-url.txt").write_text(pack_url + "\n")
    print(f"servidor pronto em {out}")
    return out


if __name__ == "__main__":
    build(pack_url=sys.argv[1] if len(sys.argv) > 1 else None)
