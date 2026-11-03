import json

import pytest
import yaml

import questgen
import registry
from paths import BUILD, ROOT

TABLES = yaml.safe_load((ROOT / "quests" / "reward_tables.yaml").read_text(encoding="utf-8"))
ORDER = ["comum", "rara", "epica", "lendaria"]
GATES = {"ecos:fragmento_selo_floresta", "ecos:fragmento_selo_profundezas", "ecos:fragmento_selo_ceus",
         "ecos:fragmento_selo_estrelas", "ecos:chave_crepuscular", "ecos:chave_celeste", "ecos:artefato_selo",
         "undergarden:catalyst", "blue_skies:zeal_lighter", "ad_astra:nasa_workbench",
         "projecte:philosophers_stone", "deeperdarker:heart_of_the_deep"}


def chapters():
    return questgen.load_sources()


def shop():
    return next(c for c in chapters() if c.slug == "loja")


def mean_tier(table):
    total = sum(e["weight"] for e in table["entries"])
    return sum(e["weight"] * e["tier"] for e in table["entries"]) / total


def test_four_crates_exist_with_rarity_order():
    assert list(TABLES) == ORDER
    tiers = [mean_tier(TABLES[t]) for t in ORDER]
    assert tiers == sorted(tiers) and len(set(tiers)) == 4


def test_shop_never_sells_gates():
    sold = {r["item"] for q in shop().quests for r in q["rewards"] if "item" in r}
    crate = {e["item"] for t in TABLES.values() for e in t["entries"]}
    for item in sold | crate:
        assert item not in GATES, item
        assert not item.startswith("projecte:"), item


def test_shop_quests_are_repeatable_and_consume_coins():
    for q in shop().quests:
        if q["slug"] == "balcao":
            continue
        assert q.get("repeatable") is True, q["slug"]
        assert q["tasks"] == [{"item": questgen.COIN, "count": q["tasks"][0]["count"], "consume": True}], q["slug"]


def test_no_repeatable_gives_coins():
    for c in chapters():
        for q in c.quests:
            if q.get("repeatable"):
                assert not any("coins" in r for r in q["rewards"]), f"{c.slug}/{q['slug']}"


def test_coin_budget_per_act():
    earned = {a: 0 for a in range(6)}
    for c in chapters():
        if c.slug == "loja":
            continue
        for q in c.quests:
            earned[c.act] += sum(r.get("coins", 0) for r in q["rewards"])
    for q in shop().quests:
        if q["slug"] == "balcao":
            continue
        tier = q["tier"]
        if not any(c.act == tier for c in chapters() if c.slug != "loja"):
            continue  # ato ainda não escrito (Tasks 5–9)
        available = sum(earned[a] for a in range(tier + 1))
        assert available >= q["tasks"][0]["count"], f"{q['slug']}: custa {q['tasks'][0]['count']}, ganho até ato {tier} = {available}"


def test_crate_entries_ids_exist():
    dump = BUILD / "registry_dump.json"
    if not dump.exists():
        pytest.skip("sem dump")
    reg = registry.load(dump)
    for t in TABLES.values():
        for e in t["entries"]:
            assert reg.has_item(e["item"]), e["item"]


def test_diary_book_from_lore():
    book = questgen.diary_book(3)
    assert book["id"] == "minecraft:written_book"
    assert book["tag"]["author"] == "Ilse Varrow"
    assert "Página 3" in book["tag"]["title"]
    assert "Faça uma cama" in "".join(book["tag"]["pages"])


def test_reward_tables_loaded_ingame():
    p = BUILD / "quest_selftest.json"
    if not p.exists():
        pytest.skip("sem selftest")
    d = json.loads(p.read_text(encoding="utf-8"))
    assert set(d["tables"]) == set(ORDER)
    for slug, t in d["tables"].items():
        assert t["rewards"] == len(TABLES[slug]["entries"]) and t["crate"] == slug
