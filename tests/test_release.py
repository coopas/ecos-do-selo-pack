"""Pacotes de lançamento: zip do servidor limpo e zip da instância do Prism apontando para a URL pública."""
import zipfile

import release

URL = "https://raw.githubusercontent.com/coopas/ecos-do-selo-pack/main/pack/pack.toml"


def _fake_server(d):
    for rel, text in {"start.bat": "x", "eula.txt": "eula=true\n", "pack-url.txt": "old\n", "mods/a.jar": "j",
                      "world/level.dat": "w", "logs/latest.log": "l", "crash-reports/c.txt": "c",
                      "kubejs/config/dev.json": "{}", "kubejs/exported/registry_dump.json": "{}",
                      "kubejs/server_scripts/x.js": "s", "usercache.json": "[]", "ops.json": "[]"}.items():
        p = d / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)


def test_server_zip_is_clean(tmp_path):
    src = tmp_path / "server"
    _fake_server(src)
    z = release.zip_server(src, tmp_path / "out.zip", URL)
    names = set(zipfile.ZipFile(z).namelist())
    assert {"start.bat", "mods/a.jar", "kubejs/server_scripts/x.js", "pack-url.txt", "eula.txt"} <= names
    for bad in ("world/level.dat", "logs/latest.log", "crash-reports/c.txt", "kubejs/config/dev.json",
                "kubejs/exported/registry_dump.json", "usercache.json", "ops.json"):
        assert bad not in names, bad
    zf = zipfile.ZipFile(z)
    assert zf.read("eula.txt").decode() == "eula=false\n"
    assert zf.read("pack-url.txt").decode().strip() == URL
