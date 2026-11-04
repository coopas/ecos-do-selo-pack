"""Plano 4: imagens do GPT Image 2 integradas (texturas de item, ícones de capítulo, artes de quest, caixas, logo)."""
import json

from PIL import Image

import questgen
from paths import PACK

ASSETS = PACK / "kubejs" / "assets"


def _png(rl: str):
    """'ecos:textures/x.png' -> caminho no resource pack do KubeJS."""
    ns, path = rl.split(":", 1)
    return ASSETS / ns / path


def test_every_item_has_its_own_texture():
    items = json.loads((PACK / "kubejs/ecos/items.json").read_text(encoding="utf-8"))["items"]
    for it in items:
        name = it["id"].split(":")[1]
        assert it["texture"] == f"ecos:item/{name}", it["id"]
        im = Image.open(ASSETS / "ecos/textures/item" / f"{name}.png")
        assert im.size == (32, 32) and im.mode == "RGBA", (name, im.size, im.mode)
        alpha = im.getchannel("A").getextrema()
        assert alpha[0] == 0 and alpha[1] == 255, f"{name}: fundo não transparente"


def test_every_chapter_icon_is_an_existing_image():
    for c in questgen.load_sources():
        assert c.icon == f"ecos:textures/gui/chapters/{c.slug}.png", c.slug
        assert Image.open(_png(c.icon)).size == (64, 64), c.slug


def test_quest_images_exist_and_are_wide():
    with_image = [(c.slug, q) for c in questgen.load_sources() for q in c.quests if q.get("image")]
    assert len(with_image) == 12, [f"{s}/{q['slug']}" for s, q in with_image]
    for slug, q in with_image:
        im = Image.open(_png(q["image"]))
        assert im.size == (512, 288), (slug, q["slug"], im.size)


def test_quest_image_goes_first_in_description():
    q = next(q for c in questgen.load_sources() if c.slug == "ato1" for q in c.quests if q["slug"] == "morvane")
    built = questgen.build(questgen.load_sources(), questgen.load_tables())
    text = built["chapters/ato1.snbt"]
    assert "{image:ecos:textures/gui/quests/morvane.png width:200 height:112 align:center}" in text
    assert q["image"] == "ecos:textures/gui/quests/morvane.png"


def test_reward_table_icons_are_crate_images():
    built = questgen.build(questgen.load_sources(), questgen.load_tables())
    for rarity in ("comum", "rara", "epica", "lendaria"):
        assert f'Icon: "ecos:textures/gui/crates/{rarity}.png"' in built[f"reward_tables/{rarity}.snbt"]
        assert Image.open(ASSETS / "ecos/textures/gui/crates" / f"{rarity}.png").size == (64, 64)


def test_title_logo_replaces_minecraft_logo():
    im = Image.open(ASSETS / "minecraft/textures/gui/title/minecraft.png")
    assert im.size == (1024, 256) and im.mode == "RGBA"
    edition = Image.open(ASSETS / "minecraft/textures/gui/title/edition.png")
    assert edition.getchannel("A").getextrema() == (0, 0), "o 'Java Edition' some atrás do logo"


def test_image_icons_use_ftbquests_custom_icon():
    """O FTB Quests só aceita item como ícone: imagem vai como ftbquests:custom_icon com NBT Icon (senão aparece '?')."""
    built = questgen.build(questgen.load_sources(), questgen.load_tables())
    ch = built["chapters/ato1.snbt"]
    assert 'id: "ftbquests:custom_icon"' in ch
    assert 'Icon: "ecos:textures/gui/chapters/ato1.png"' in ch
    assert 'icon: "ecos:textures/' not in ch
    assert 'Icon: "ecos:textures/gui/crates/comum.png"' in built["reward_tables/comum.snbt"]


def test_fancymenu_overlay_hidden_for_players():
    opts = (PACK / "config/fancymenu/options.txt").read_text(encoding="utf-8")
    assert "B:show_customization_overlay = 'false';" in opts
