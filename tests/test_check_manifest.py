from pathlib import Path

import check_manifest as cm

MR_TOML = '''name = "{name}"
filename = "{name}.jar"
side = "{side}"

[download]
url = "https://cdn.modrinth.com/x/{name}.jar"
hash-format = "sha1"
hash = "abc"

[update]
[update.modrinth]
mod-id = "x"
version = "y"
'''

CF_TOML = '''name = "{name}"
filename = "{name}.jar"
side = "{side}"

[download]
hash-format = "sha1"
hash = "abc"
mode = "metadata:curseforge"

[update]
[update.curseforge]
file-id = 1
project-id = 2
'''

BROKEN_TOML = '''name = "{name}"
filename = "{name}.jar"
side = "{side}"

[download]
hash-format = "sha1"
hash = "abc"
'''


def write(pack: Path, folder: str, slug: str, template: str, side="both"):
    d = pack / folder
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{slug}.pw.toml").write_text(template.format(name=slug, side=side))


def manifest(*rows):
    return [dict(id=r[0], source=r[1], slug=r[2], side=r[3], category=r[4]) for r in rows]


def test_missing_mod_reported(tmp_path):
    m = manifest(("create", "mr", "create", "both", "core"))
    problems = cm.check(m, cm.load_pack_mods(tmp_path))
    assert any("faltando: create" in p for p in problems)


def test_wrong_side_reported(tmp_path):
    write(tmp_path, "mods", "embeddium", MR_TOML, side="both")
    m = manifest(("embeddium", "mr", "embeddium", "client", "perf"))
    problems = cm.check(m, cm.load_pack_mods(tmp_path))
    assert any("side" in p for p in problems)


def test_no_download_source_reported(tmp_path):
    write(tmp_path, "mods", "weird", BROKEN_TOML)
    m = manifest(("weird", "cf", "weird", "both", "core"))
    problems = cm.check(m, cm.load_pack_mods(tmp_path))
    assert any("download manual" in p for p in problems)


def test_clean_pack_ok(tmp_path):
    write(tmp_path, "mods", "create", MR_TOML)
    write(tmp_path, "mods", "ftb-quests-forge", CF_TOML)
    write(tmp_path, "shaderpacks", "bsl-shaders", MR_TOML, side="client")
    m = manifest(
        ("create", "mr", "create", "both", "core"),
        ("ftbquests", "cf", "ftb-quests-forge", "both", "core"),
        ("bsl", "mr", "bsl-shaders", "client", "visual"),
    )
    assert cm.check(m, cm.load_pack_mods(tmp_path)) == []


def test_load_manifest_reads_csv(tmp_path):
    p = tmp_path / "mods.csv"
    p.write_text("id,source,slug,side,category\ncreate,mr,create,both,core\n")
    assert cm.load_manifest(p) == manifest(("create", "mr", "create", "both", "core"))
