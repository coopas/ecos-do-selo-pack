import add_mods


def test_set_side_rewrites_existing(tmp_path):
    p = tmp_path / "x.pw.toml"
    p.write_text('name = "X"\nfilename = "x.jar"\nside = "both"\n\n[download]\nurl = "u"\n')
    add_mods.set_side(p, "client")
    text = p.read_text()
    assert 'side = "client"' in text and 'side = "both"' not in text


def test_set_side_inserts_when_absent(tmp_path):
    p = tmp_path / "x.pw.toml"
    p.write_text('name = "X"\nfilename = "x.jar"\n\n[download]\nurl = "u"\n')
    add_mods.set_side(p, "client")
    lines = p.read_text().splitlines()
    assert lines.index('side = "client"') < lines.index("[download]")
