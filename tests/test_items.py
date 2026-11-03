import json

import pytest

import ecosdata
import registry
from paths import BUILD, PACK

LANG = PACK / "kubejs" / "assets" / "ecos" / "lang"
EXPECTED = {
    "ecos:fragmento_eco", "ecos:fragmento_selo_floresta", "ecos:fragmento_selo_profundezas",
    "ecos:fragmento_selo_ceus", "ecos:fragmento_selo_estrelas", "ecos:chave_crepuscular",
    "ecos:artefato_selo", "ecos:pedra_celeste",
}


def items():
    return ecosdata.load().items


def test_expected_items_declared():
    assert ecosdata.load().item_ids() == EXPECTED


def test_no_duplicate_ids():
    ids = [i["id"] for i in items()]
    assert len(ids) == len(set(ids))


def test_placeholder_textures_are_vanilla():
    for i in items():
        assert i["texture"].startswith("minecraft:"), i["id"]


def lang_key(item):
    return f'{"block" if item["kind"] == "block" else "item"}.ecos.{item["id"].split(":")[1]}'


def test_lang_complete():
    pt = json.loads((LANG / "pt_br.json").read_text(encoding="utf-8"))
    en = json.loads((LANG / "en_us.json").read_text(encoding="utf-8"))
    for i in items():
        assert pt[lang_key(i)] == i["pt"]
        assert en[lang_key(i)] == i["en"]
    assert any(pt[lang_key(i)] != en[lang_key(i)] for i in items())


def test_artefato_is_unique_and_glows():
    a = next(i for i in items() if i["id"] == "ecos:artefato_selo")
    assert a["max_stack"] == 1 and a["glow"] is True and a["rarity"] == "epic"


def test_items_registered_ingame():
    dump = BUILD / "registry_dump.json"
    if not dump.exists():
        pytest.skip("sem dump")
    reg = registry.load(dump)
    assert [i for i in EXPECTED if not reg.has_item(i)] == []


def test_items_json_root_is_object():
    # JsonIO.read do KubeJS devolve null para array na raiz (bug real: startup quebrou e o servidor travou)
    raw = json.loads((PACK / "kubejs" / "ecos" / "items.json").read_text(encoding="utf-8"))
    assert isinstance(raw, dict) and isinstance(raw["items"], list)
