import snbt


def test_snbt_escapes_quotes():
    backslash = "\\"
    src = f'diz "oi" {backslash} fim'
    assert snbt.dumps(src) == f'"diz {backslash}"oi{backslash}" {backslash}{backslash} fim"'


def test_snbt_long_and_double_and_byte():
    assert snbt.dumps(snbt.Long(5)) == "5L"
    assert snbt.dumps(1.5) == "1.5d"
    assert snbt.dumps(snbt.Byte(1)) == "1b"
    assert snbt.dumps(True) == "true"


def test_snbt_dict_sorted_keys_and_lists():
    out = snbt.dumps({"b": 1, "a": ["x", "y"]})
    assert out.index("a:") < out.index("b:")
    assert '"x"' in out and '"y"' in out


def test_snbt_quotes_nonplain_keys():
    assert '"ftbfiltersystem:filter": ' in snbt.dumps({"ftbfiltersystem:filter": "v"})
