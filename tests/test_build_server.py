from pathlib import Path

import build_server

CLIENT_META = 'name = "Emb"\nfilename = "embeddium-1.jar"\nside = "client"\n[download]\nurl = "u"\n'
BOTH_META = 'name = "Create"\nfilename = "create-6.jar"\nside = "both"\n[download]\nurl = "u"\n'


def test_template_props(tmp_path):
    build_server.copy_template(tmp_path, forge_version="47.4.28")
    props = (tmp_path / "server.properties").read_text()
    assert "max-players=15" in props
    assert "allow-flight=true" in props


def test_start_bat_requires_java17(tmp_path):
    build_server.copy_template(tmp_path, forge_version="47.4.28")
    bat = (tmp_path / "start.bat").read_text()
    assert 'findstr /r /c:"version .17[^0-9]"' in bat
    assert "1.20.1-47.4.28" in bat
    assert "FORGEVER" not in bat


def test_start_sh_requires_java17(tmp_path):
    build_server.copy_template(tmp_path, forge_version="47.4.28")
    sh = (tmp_path / "start.sh").read_text()
    assert 'version "17' in sh and "1.20.1-47.4.28" in sh


def test_template_keeps_existing_world_props(tmp_path):
    (tmp_path / "server.properties").write_text("motd=meu\n")
    build_server.copy_template(tmp_path, forge_version="47.4.28")
    assert (tmp_path / "server.properties").read_text() == "motd=meu\n"


def test_no_client_mods_in_server(tmp_path):
    pack = tmp_path / "pack"
    (pack / "mods").mkdir(parents=True)
    (pack / "mods" / "embeddium.pw.toml").write_text(CLIENT_META)
    (pack / "mods" / "create.pw.toml").write_text(BOTH_META)
    out = tmp_path / "server"
    (out / "mods").mkdir(parents=True)
    (out / "mods" / "embeddium-1.jar").write_bytes(b"x")
    (out / "mods" / "create-6.jar").write_bytes(b"x")
    removed = build_server.prune_client_mods(out, pack)
    assert removed == ["embeddium-1.jar"]
    assert not (out / "mods" / "embeddium-1.jar").exists()
    assert (out / "mods" / "create-6.jar").exists()


def test_forge_version_read_from_pack(tmp_path):
    (tmp_path / "pack.toml").write_text('[versions]\nforge = "47.4.28"\nminecraft = "1.20.1"\n')
    assert build_server.forge_version(tmp_path) == "47.4.28"


def test_start_bat_quotes_balanced_on_every_line(tmp_path):
    # aspas ímpares fazem o cmd engolir o ">nul" e o findstr falha sempre (bug real)
    build_server.copy_template(tmp_path, forge_version="47.4.28")
    for line in (tmp_path / "start.bat").read_text().splitlines():
        assert line.count('"') % 2 == 0, line


def test_start_scripts_self_update_server_mods(tmp_path):
    build_server.copy_template(tmp_path, forge_version="47.4.28")
    bat = (tmp_path / "start.bat").read_text()
    sh = (tmp_path / "start.sh").read_text()
    for s in (bat, sh):
        assert "pack-url.txt" in s
        assert "packwiz-installer-bootstrap.jar -g -s server" in s


def test_accept_eula_temporarily_restores(tmp_path):
    (tmp_path / "eula.txt").write_text("eula=false\n")
    with build_server.eula_accepted(tmp_path):
        assert (tmp_path / "eula.txt").read_text() == "eula=true\n"
    assert (tmp_path / "eula.txt").read_text() == "eula=false\n"
