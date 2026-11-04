"""Integra as imagens do GPT Image 2 no pack (Plano 4).

Uso: python tools/integrate_images.py <pasta com as imagens>
Lê os nomes definidos em docs/prompts-imagens.md e grava no resource pack do KubeJS:
  item-<id>.png   -> kubejs/assets/ecos/textures/item/<id>.png          (32x32, pixel art, alfa binário)
  cap-<slug>.png  -> kubejs/assets/ecos/textures/gui/chapters/<slug>.png (64x64)
  caixa-<r>.png   -> kubejs/assets/ecos/textures/gui/crates/<r>.png      (64x64)
  quest-<x>.png   -> kubejs/assets/ecos/textures/gui/quests/<x>.png      (512x288)
  ilse.png        -> kubejs/assets/ecos/textures/gui/quests/ilse.png     (512x288, retrato centralizado)
  logo.png        -> kubejs/assets/minecraft/textures/gui/title/minecraft.png (1024x256) + edition.png vazio
  icone-pack.png  -> tools/prism/ecos_do_selo.png (256x256, ícone da instância do Prism)
"""
import sys
from pathlib import Path

from PIL import Image

from paths import PACK, ROOT

ASSETS = PACK / "kubejs" / "assets"
CRATES = ("comum", "rara", "epica", "lendaria")


def crop_to_content(im: Image.Image) -> Image.Image:
    """Recorta a área com alfa e devolve um quadrado centralizado (sem distorcer)."""
    im = im.convert("RGBA")
    box = im.getchannel("A").point(lambda a: 255 if a > 16 else 0).getbbox() or (0, 0, *im.size)
    im = im.crop(box)
    side = max(im.size)
    sq = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    sq.paste(im, ((side - im.width) // 2, (side - im.height) // 2))
    return sq


def pixel_icon(im: Image.Image, size: int = 32, colors: int = 48) -> Image.Image:
    """Ícone estilo Minecraft: reduz, limita a paleta e deixa o alfa só 0/255."""
    small = crop_to_content(im).resize((size, size), Image.LANCZOS)
    alpha = small.getchannel("A").point(lambda a: 255 if a >= 110 else 0)
    rgb = small.convert("RGB").quantize(colors=colors, method=Image.Quantize.MEDIANCUT).convert("RGB")
    out = rgb.convert("RGBA")
    out.putalpha(alpha)
    return out


def emblem(im: Image.Image, size: int = 64) -> Image.Image:
    return crop_to_content(im).resize((size, size), Image.LANCZOS)


def wide(im: Image.Image, w: int = 512, h: int = 288) -> Image.Image:
    """Recorta para 16:9 pelo centro e reduz."""
    im = im.convert("RGB")
    target = w / h
    if im.width / im.height > target:
        nw = int(im.height * target)
        im = im.crop(((im.width - nw) // 2, 0, (im.width - nw) // 2 + nw, im.height))
    else:
        nh = int(im.width / target)
        im = im.crop((0, (im.height - nh) // 2, im.width, (im.height - nh) // 2 + nh))
    return im.resize((w, h), Image.LANCZOS)


def portrait_card(im: Image.Image, w: int = 512, h: int = 288) -> Image.Image:
    """Retrato quadrado centralizado num cartão 16:9 escuro."""
    card = Image.new("RGB", (w, h), (10, 15, 20))
    face = im.convert("RGB").resize((h, h), Image.LANCZOS)
    card.paste(face, ((w - h) // 2, 0))
    return card


def title_logo(im: Image.Image) -> Image.Image:
    """O 1.20 desenha minecraft.png como 256x44 de uma textura 256x64; em HD: 1024x256 com o logo nos 176 px de cima."""
    logo = crop_to_content_keep_ratio(im)
    canvas = Image.new("RGBA", (1024, 256), (0, 0, 0, 0))
    scale = min(1024 / logo.width, 176 / logo.height)
    logo = logo.resize((int(logo.width * scale), int(logo.height * scale)), Image.LANCZOS)
    canvas.paste(logo, ((1024 - logo.width) // 2, (176 - logo.height) // 2), logo)
    return canvas


def crop_to_content_keep_ratio(im: Image.Image) -> Image.Image:
    im = im.convert("RGBA")
    box = im.getchannel("A").point(lambda a: 255 if a > 16 else 0).getbbox() or (0, 0, *im.size)
    return im.crop(box)


def save(im: Image.Image, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    im.save(dest, optimize=True)


def integrate(src: Path) -> list[str]:
    done = []
    for f in sorted(src.glob("*.png")):
        name = f.stem
        im = Image.open(f)
        if name.startswith("item-"):
            save(pixel_icon(im), ASSETS / "ecos/textures/item" / f"{name[5:]}.png")
        elif name.startswith("cap-"):
            save(emblem(im), ASSETS / "ecos/textures/gui/chapters" / f"{name[4:]}.png")
        elif name.startswith("caixa-") and name[6:] in CRATES:
            save(emblem(im), ASSETS / "ecos/textures/gui/crates" / f"{name[6:]}.png")
        elif name.startswith("quest-"):
            save(wide(im), ASSETS / "ecos/textures/gui/quests" / f"{name[6:]}.png")
        elif name == "ilse":
            save(portrait_card(im), ASSETS / "ecos/textures/gui/quests/ilse.png")
        elif name == "logo":
            save(title_logo(im), ASSETS / "minecraft/textures/gui/title/minecraft.png")
            save(Image.new("RGBA", (128, 16), (0, 0, 0, 0)), ASSETS / "minecraft/textures/gui/title/edition.png")
        elif name == "icone-pack":
            save(im.convert("RGBA").resize((256, 256), Image.LANCZOS), ROOT / "tools" / "prism" / "ecos_do_selo.png")
        else:
            continue  # menu/carregamento/banner: usados fora do resource pack
        done.append(name)
    return done


if __name__ == "__main__":
    names = integrate(Path(sys.argv[1]))
    print(f"{len(names)} imagens integradas")
