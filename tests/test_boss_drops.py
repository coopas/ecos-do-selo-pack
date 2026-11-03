import pytest

import ecosdata

FRAGMENTS = {"ecos:fragmento_selo_floresta", "ecos:fragmento_selo_profundezas",
             "ecos:fragmento_selo_ceus", "ecos:fragmento_selo_estrelas"}


def drops():
    return ecosdata.load().boss_drops


def test_boss_drop_ids_valid():
    d = drops()
    assert d, "boss_drops.json vazio"
    assert set(d.values()) <= FRAGMENTS


def test_every_fragment_has_a_source():
    assert set(drops().values()) == FRAGMENTS


def test_expected_bosses():
    assert drops() == {
        "twilightforest:lich": "ecos:fragmento_selo_floresta",
        "minecraft:warden": "ecos:fragmento_selo_profundezas",
        "aether:sun_spirit": "ecos:fragmento_selo_ceus",
        "cataclysm:ignis": "ecos:fragmento_selo_estrelas",
    }


@pytest.mark.ingame
def test_lich_drop_ingame():
    import boot_test
    problems = boot_test.server(console=[
        "forceload add 0 0",
        "summon twilightforest:lich 0 100 0 {NoAI:1b}",
        "kill @e[type=twilightforest:lich]",
        'execute if entity @e[type=item,nbt={Item:{id:"ecos:fragmento_selo_floresta"}}] run say ECOS_DROP_OK',
    ])
    assert problems == []
    assert any("ECOS_DROP_OK" in line for line in boot_test.LAST_CONSOLE), boot_test.LAST_CONSOLE[-20:]
