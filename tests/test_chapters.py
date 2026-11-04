"""Capítulos das Tasks 5–9: existência, tamanho, validação e páginas de diário por ato."""
import pytest

import questcheck
import questgen
from paths import BUILD

SIZES = {
    "prologo": (25, 35), "ato1": (40, 55), "side_create": (30, 40), "side_gt_steam_lv": (35, 45),
    "ato2": (40, 50), "side_ars": (25, 35), "side_irons": (20, 30), "side_occultism": (25, 35),
    "ato3": (40, 50), "side_gt_mv_ev": (35, 45), "side_ae2": (15, 25),
    "ato4": (35, 45), "side_space": (20, 30),
    "ato5": (30, 40), "side_projecte": (15, 25),
}
PAGES_BY_ACT = {0: range(1, 5), 1: range(5, 11), 2: range(11, 17), 3: range(17, 22), 4: range(22, 27), 5: range(27, 31)}
# capítulos já escritos (cresce a cada task): os testes só cobrem o que existe + o próximo bloco declarado
WRITTEN = {c.slug for c in questgen.load_sources()}
TARGET = [s for s in SIZES if s in WRITTEN] or ["prologo"]


def by_slug():
    return {c.slug: c for c in questgen.load_sources()}


@pytest.mark.parametrize("slug", list(SIZES))
def test_chapter_size(slug):
    if slug not in WRITTEN:
        pytest.skip("capítulo de task futura")
    lo, hi = SIZES[slug]
    n = len(by_slug()[slug].quests)
    assert lo <= n <= hi, f"{slug}: {n} quests (esperado {lo}–{hi})"


@pytest.mark.parametrize("slug", list(SIZES))
def test_chapter_valid(slug):
    if slug not in WRITTEN:
        pytest.skip("capítulo de task futura")
    if not (BUILD / "registry_dump.json").exists():
        pytest.skip("sem dump")
    errs = [e for e in questcheck.main_check() if e.startswith(f"{slug}/")]
    assert errs == []


@pytest.mark.parametrize("act", list(PAGES_BY_ACT))
def test_act_delivers_its_lore_pages(act):
    chapters = [c for c in questgen.load_sources() if c.act == act and c.slug != "loja"]
    main = {0: "prologo", 1: "ato1", 2: "ato2", 3: "ato3", 4: "ato4", 5: "ato5"}[act]
    if main not in WRITTEN:
        pytest.skip("ato de task futura")
    pages = sorted(r["page"] for c in chapters for q in c.quests for r in q["rewards"] if "page" in r)
    assert pages == list(PAGES_BY_ACT[act])


def test_task5_chapters_exist():
    assert {"prologo", "ato1", "side_create", "side_gt_steam_lv"} <= WRITTEN
