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


def test_ftb_chunks_minimap_off():
    """O mapa do pack é o Xaero's; o FTB Chunks fica só para claim e chunk loading (senão aparecem dois minimapas)."""
    text = (PACK / "defaultconfigs" / "ftbchunks" / "ftbchunks-world.snbt").read_text()
    assert re.search(r"force_disable_minimap: true\b", text)


def test_ultimine_limit():
    text = (PACK / "defaultconfigs" / "ftbultimine" / "ftbultimine-server.snbt").read_text()
    assert re.search(r"max_blocks: 64\b", text)


def test_improved_mobs_scaling_is_gentle():
    cfg = tomllib.loads((PACK / "config" / "improvedmobs" / "common.toml").read_text())
    general = next(v for v in cfg.values() if isinstance(v, dict) and "Difficulty Delay" in v)
    assert general["Difficulty Delay"] == 72000
    assert general["Difficulty Increase"] == ["0.0-0.03", "250.0-0.0"]
    assert general["Ignore Players"] is False


def test_improved_mobs_difficulty_hud_hidden():
    # o HUD "Difficulty 0.0" no canto da tela fica escondido; sem preserve para corrigir instalações antigas
    cfg = tomllib.loads((PACK / "config" / "improvedmobs" / "client.toml").read_text())
    assert cfg["gui"]["Show Difficulty"] is False
    entry = index_entry("config/improvedmobs/client.toml")
    assert entry is not None and not entry.get("preserve")


def test_pack_toml_hash_bate_com_index():
    # packwiz guarda no pack.toml o sha256 do index.toml; hash velho = erro de hash para os jogadores
    import hashlib
    pack = tomllib.loads((PACK / "pack.toml").read_text())
    assert pack["index"]["hash-format"] == "sha256"
    esperado = hashlib.sha256((PACK / "index.toml").read_bytes()).hexdigest()
    assert pack["index"]["hash"] == esperado, "rode packwiz refresh e commite pack.toml junto com index.toml"
