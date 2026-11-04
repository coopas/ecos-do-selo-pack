"""Gera as texturas 16x16 do ecosmaquinas (arte original, procedural; nada copiado de outros mods).

Uso: python tools/ecosmaquinas/gen_textures.py  -> escreve em res/assets/ecosmaquinas/textures/block/.
"""
from pathlib import Path

from PIL import Image

OUT = Path(__file__).resolve().parent / "res" / "assets" / "ecosmaquinas" / "textures" / "block"

# Cor base de cada máquina: bronze (vapor), ferro forjado (ULV), aço cinza-azulado (LV), cobre (saída).
BASE = {
    "motor_vapor": (176, 120, 58),
    "dinamo_cinetico_ulv": (110, 104, 100),
    "dinamo_cinetico_lv": (128, 136, 150),
    "saida_vapor": (196, 110, 70),
}
EIXO = (150, 140, 120)
FURO = (40, 34, 30)
BOBINA = (214, 128, 64)
VAPOR = (226, 230, 236)


def tom(c, f):
    return tuple(max(0, min(255, int(v * f))) for v in c)


def placa(base):
    """Placa metálica: borda escura, chanfro claro em cima/esquerda, rebites nos cantos, leve ruído determinístico."""
    img = Image.new("RGBA", (16, 16))
    px = img.load()
    for y in range(16):
        for x in range(16):
            ruido = 1.0 + (((x * 7 + y * 13) % 5) - 2) * 0.02
            px[x, y] = tom(base, ruido) + (255,)
    for i in range(16):
        for p in ((i, 0), (0, i)):
            px[p] = tom(base, 1.25) + (255,)
        for p in ((i, 15), (15, i)):
            px[p] = tom(base, 0.55) + (255,)
    for x, y in ((2, 2), (13, 2), (2, 13), (13, 13)):
        px[x, y] = tom(base, 1.4) + (255,)
        px[x + 1, y + 1] = tom(base, 0.6) + (255,)
    return img


def circulo(img, cor, r_ext, r_int=None, cor_int=None):
    px = img.load()
    for y in range(16):
        for x in range(16):
            d = ((x - 7.5) ** 2 + (y - 7.5) ** 2) ** 0.5
            if r_int is not None and d <= r_int:
                px[x, y] = cor_int + (255,)
            elif d <= r_ext:
                px[x, y] = cor + (255,)


def frente(nome):
    img = placa(BASE[nome])
    circulo(img, tom(BASE[nome], 0.45), 5.0, 3.0, FURO)
    px = img.load()
    for y in range(6, 10):  # ponta do eixo
        for x in range(6, 10):
            px[x, y] = EIXO + (255,)
    return img


def lado(nome):
    img = placa(BASE[nome])
    px = img.load()
    if nome == "motor_vapor":  # grade de ventilação
        for y in (5, 8, 11):
            for x in range(4, 12):
                px[x, y] = FURO + (255,)
    else:  # bobina de cobre
        for y in range(4, 12):
            for x in range(4, 12):
                px[x, y] = (tom(BOBINA, 1.15) if y % 2 == 0 else tom(BOBINA, 0.75)) + (255,)
    return img


def topo(nome):
    img = placa(BASE[nome])
    px = img.load()
    for i in range(4, 12):
        px[i, 7] = tom(BASE[nome], 0.6) + (255,)
        px[7, i] = tom(BASE[nome], 0.6) + (255,)
    return img


def saida_topo():
    img = placa(BASE["saida_vapor"])
    circulo(img, tom(BASE["saida_vapor"], 0.5), 5.0, 3.0, VAPOR)
    return img


def saida_lado():
    img = placa(BASE["saida_vapor"])
    px = img.load()
    for x in range(1, 15):  # cano atravessando
        for y in range(6, 10):
            px[x, y] = (tom(BASE["saida_vapor"], 0.75) if y in (6, 9) else tom(BASE["saida_vapor"], 1.1)) + (255,)
    return img


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for nome in ("motor_vapor", "dinamo_cinetico_ulv", "dinamo_cinetico_lv"):
        frente(nome).save(OUT / f"{nome}_frente.png")
        lado(nome).save(OUT / f"{nome}_lado.png")
        topo(nome).save(OUT / f"{nome}_topo.png")
    saida_topo().save(OUT / "saida_vapor_topo.png")
    saida_lado().save(OUT / "saida_vapor_lado.png")
    print("texturas em", OUT)


if __name__ == "__main__":
    main()
