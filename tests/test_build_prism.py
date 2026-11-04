import json
import zipfile

import build_prism

URL = "https://example.com/pack/pack.toml"


def built(tmp_path):
    return build_prism.build(URL, out=tmp_path / "prism", forge_version="47.4.28", pack_version="0.1.0",
                             bootstrap_jar=_fake_jar(tmp_path))


def _fake_jar(tmp_path):
    p = tmp_path / "bootstrap.jar"
    p.write_bytes(b"jar")
    return p


def cfg(tmp_path):
    return (tmp_path / "prism" / "instance.cfg").read_text()


def test_instance_cfg_memory(tmp_path):
    built(tmp_path)
    c = cfg(tmp_path)
    assert "MaxMemAlloc=6144" in c and "OverrideMemory=true" in c


def test_prelaunch_has_url(tmp_path):
    built(tmp_path)
    c = cfg(tmp_path)
    assert "OverrideCommands=true" in c
    # formato INI do Qt: valor inteiro entre aspas, aspas internas escapadas
    assert f'PreLaunchCommand="\\"$INST_JAVA\\" -jar packwiz-installer-bootstrap.jar {URL}"' in c


def test_mmc_pack_versions(tmp_path):
    built(tmp_path)
    comps = json.loads((tmp_path / "prism" / "mmc-pack.json").read_text())["components"]
    versions = {c["uid"]: c["version"] for c in comps}
    assert versions["net.minecraft"] == "1.20.1"
    assert versions["net.minecraftforge"] == "47.4.28"
    assert comps[0]["uid"] == "org.lwjgl3" and versions["org.lwjgl3"] == "3.3.1"


def test_zip_contains_bootstrap(tmp_path):
    z = built(tmp_path)
    assert z.name == "EcosDoSelo-0.1.0.zip"
    names = zipfile.ZipFile(z).namelist()
    assert "instance.cfg" in names
    assert "mmc-pack.json" in names
    assert "minecraft/packwiz-installer-bootstrap.jar" in names


def test_instance_uses_pack_icon(tmp_path):
    """O Prism importa <iconKey>.png da raiz do zip como ícone da instância."""
    z = built(tmp_path)
    assert "iconKey=ecos_do_selo" in cfg(tmp_path)
    assert "ecos_do_selo.png" in zipfile.ZipFile(z).namelist()
