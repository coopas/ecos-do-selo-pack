import subprocess


def test_paths_java17_exists():
    from paths import JAVA17
    assert JAVA17.exists()
    out = subprocess.run([str(JAVA17), "-version"], capture_output=True, text=True)
    assert '"17.' in out.stderr


def test_pack_dir_has_pack_toml():
    from paths import PACK
    assert (PACK / "pack.toml").exists()


def test_packwiz_resolves():
    from paths import PACKWIZ
    out = subprocess.run([PACKWIZ, "--help"], capture_output=True, text=True)
    assert out.returncode == 0
