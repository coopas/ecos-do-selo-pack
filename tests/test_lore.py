import re

from paths import ROOT

LORE = ROOT / "docs" / "lore.md"
SECTIONS = ["## Premissa", "## Linha do tempo", "## A Entidade", "## Os Fragmentos do Selo", "## O Narrador",
            "## Os Atos", "## Páginas do Diário", "## O Final", "## Glossário"]


def text():
    return LORE.read_text(encoding="utf-8")


def pages():
    parts = re.split(r"^### Página (\d+)", text(), flags=re.M)
    return [(int(parts[i]), parts[i + 1]) for i in range(1, len(parts), 2)]


def test_lore_has_required_sections():
    t = text()
    for s in SECTIONS:
        assert s in t, s


def test_page_count_and_numbering():
    ps = pages()
    assert 25 <= len(ps) <= 35
    assert [n for n, _ in ps] == list(range(1, len(ps) + 1))


def test_pages_are_short():
    for n, body in pages():
        lines = [l for l in body.split("## ")[0].splitlines()[1:] if l.strip()]
        assert len(lines) <= 12, f"página {n} com {len(lines)} linhas"


def test_every_page_has_act():
    for n, body in pages():
        assert re.search(r"\((Ato [IV]+|Prólogo)\)", body.splitlines()[0]), f"página {n} sem ato no título"


def test_glossary_not_empty():
    gloss = text().split("## Glossário", 1)[1]
    assert len([l for l in gloss.splitlines() if l.startswith("- **")]) >= 10
