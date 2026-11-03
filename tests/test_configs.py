import re
import tomllib

from paths import PACK


def index_entry(path):
    idx = tomllib.loads((PACK / "index.toml").read_text())
    return next((f for f in idx["files"] if f["file"] == path), None)


def test_shaders_off():
    text = (PACK / "config" / "oculus.properties").read_text()
    assert "enableShaders=false" in text
    assert "shaderPack=ComplementaryReimagined" in text


def test_oculus_config_preserved_on_update():
    entry = index_entry("config/oculus.properties")
    assert entry is not None and entry.get("preserve") is True


def test_no_options_txt_overwriting_player_settings():
    # options.txt no pack sobrescreveria as configs dos jogadores a cada update
    assert not (PACK / "options.txt").exists()


def test_chunk_limits():
    text = (PACK / "defaultconfigs" / "ftbchunks" / "ftbchunks-world.snbt").read_text()
    assert re.search(r"max_force_loaded_chunks: 25\b", text)
    assert re.search(r"max_claimed_chunks: 500\b", text)


def test_ultimine_limit():
    text = (PACK / "defaultconfigs" / "ftbultimine" / "ftbultimine-server.snbt").read_text()
    assert re.search(r"max_blocks: 64\b", text)


def test_improved_mobs_scaling_is_gentle():
    cfg = tomllib.loads((PACK / "config" / "improvedmobs" / "common.toml").read_text())
    general = next(v for v in cfg.values() if isinstance(v, dict) and "Difficulty Delay" in v)
    assert general["Difficulty Delay"] == 72000
    assert general["Difficulty Increase"] == ["0.0-0.03", "250.0-0.0"]
    assert general["Ignore Players"] is False
