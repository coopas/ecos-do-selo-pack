"""Mede o layout do livro de quests (o FTB Quests liga cada dependência local por um segmento reto entre centros).

crossings: pares de segmentos que se cruzam (não conta par que divide uma ponta).
lines_over_quests: segmento que passa a menos de `radius` do centro de uma quest que não é ponta dele.

CLI: python tools/layoutcheck.py [--png build/layout/] imprime por capítulo e sai 1 se algum passar
do limite (zero, salvo LIMITES);
--png desenha um PNG por capítulo (linhas e círculos, Pillow) para olhar sem abrir o jogo.
"""
import argparse
import sys
from pathlib import Path


# Capítulo -> (cruzamentos, linhas sobre quest) tolerados, com o motivo. Linha sobre quest: zero em todos.
# Os quatro abaixo têm grafo de dependências NÃO planar (nenhum desenho, com qualquer posição, zera os cruzamentos;
# é preciso tirar 1-2 arestas para ficar planar) e o livro ainda exige ler da esquerda para a direita (pai antes do
# filho), o que custa mais alguns. Valor = o que questgen.layout atingiu; baixar se o layout melhorar.
LIMITES: dict[str, tuple[int, int]] = {
    "side_gt_steam_lv": (7, 0),  # não planar (planar sem caldeira->extrator_vapor)
    "ato2": (2, 0),              # não planar (planar sem inicio->alto_forno_eletrico)
    "side_gt_mv_ev": (6, 0),     # não planar (planar sem inicio->pirolise e emissor_hv->campo_hv)
    "ato4": (3, 0),              # não planar (planar sem inicio->montadora_ev e casco_iv->motor_iv)
}


def edges(c) -> list[tuple[str, str]]:
    """Dependências locais (sem `/`) cujas duas pontas estão no capítulo: (pai, filho)."""
    slugs = {q["slug"] for q in c.quests}
    return [(d, q["slug"]) for q in c.quests for d in q.get("deps", []) if "/" not in d and d in slugs]


def _orient(a, b, c) -> float:
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def _on_segment(a, b, p) -> bool:
    return min(a[0], b[0]) - 1e-9 <= p[0] <= max(a[0], b[0]) + 1e-9 and \
        min(a[1], b[1]) - 1e-9 <= p[1] <= max(a[1], b[1]) + 1e-9


def segments_cross(p1, p2, p3, p4) -> bool:
    """Os segmentos p1-p2 e p3-p4 se cruzam (ou se sobrepõem colineares)."""
    eps = 1e-9
    if max(p1[0], p2[0]) < min(p3[0], p4[0]) - eps or max(p3[0], p4[0]) < min(p1[0], p2[0]) - eps or \
            max(p1[1], p2[1]) < min(p3[1], p4[1]) - eps or max(p3[1], p4[1]) < min(p1[1], p2[1]) - eps:
        return False  # caixas separadas
    d1, d2 = _orient(p3, p4, p1), _orient(p3, p4, p2)
    d3, d4 = _orient(p1, p2, p3), _orient(p1, p2, p4)
    if ((d1 > eps and d2 < -eps) or (d1 < -eps and d2 > eps)) and \
            ((d3 > eps and d4 < -eps) or (d3 < -eps and d4 > eps)):
        return True
    # colineares sobrepostos também contam (as linhas se confundem)
    return any(abs(d) <= eps and _on_segment(s, e, p)
               for d, s, e, p in ((d1, p3, p4, p1), (d2, p3, p4, p2), (d3, p1, p2, p3), (d4, p1, p2, p4)))


def crossings(c, pos) -> int:
    es = edges(c)
    n = 0
    for i, (a, b) in enumerate(es):
        for e, f in es[i + 1:]:
            if {a, b} & {e, f}:
                continue
            if segments_cross(pos[a], pos[b], pos[e], pos[f]):
                n += 1
    return n


def point_segment_distance(p, a, b) -> float:
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = dx * dx + dy * dy
    t = 0.0 if L == 0 else max(0.0, min(1.0, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / L))
    x, y = a[0] + t * dx - p[0], a[1] + t * dy - p[1]
    return (x * x + y * y) ** 0.5


def lines_over_quests(c, pos, radius: float = 0.6) -> int:
    n = 0
    for a, b in edges(c):
        for q in c.quests:
            s = q["slug"]
            if s not in (a, b) and point_segment_distance(pos[s], pos[a], pos[b]) < radius:
                n += 1
    return n


def draw(c, pos, path: Path, scale: int = 40) -> None:
    from PIL import Image, ImageDraw
    xs = [p[0] for p in pos.values()] or [0]
    ys = [p[1] for p in pos.values()] or [0]
    x0, y0 = min(xs) - 1.5, min(ys) - 1.5
    w, h = int((max(xs) - x0 + 1.5) * scale), int((max(ys) - y0 + 1.5) * scale)
    img = Image.new("RGB", (max(w, 100), max(h, 100) + 20), (30, 30, 36))
    g = ImageDraw.Draw(img)
    pt = lambda p: ((p[0] - x0) * scale, (p[1] - y0) * scale + 20)
    for a, b in edges(c):
        g.line([pt(pos[a]), pt(pos[b])], fill=(150, 150, 170), width=2)
    r = 0.5 * scale
    for q in c.quests:
        x, y = pt(pos[q["slug"]])
        g.ellipse([x - r, y - r, x + r, y + r], fill=(70, 110, 160), outline=(220, 220, 230))
        g.text((x - r, y + r), q["slug"][:14], fill=(230, 230, 200))
    g.text((4, 4), f"{c.slug}: {crossings(c, pos)} cruzamentos, {lines_over_quests(c, pos)} linhas sobre quest",
           fill=(255, 255, 255))
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--png", type=Path, help="pasta para um PNG por capítulo")
    a = ap.parse_args(argv)
    import questgen  # aqui: questgen.layout usa este módulo
    bad = 0
    for c in questgen.load_sources():
        pos = questgen.layout(c)
        x, o = crossings(c, pos), lines_over_quests(c, pos)
        xs = [p[0] for p in pos.values()]
        ys = [p[1] for p in pos.values()]
        print(f"{c.slug:20} quests={len(c.quests):3} arestas={len(edges(c)):3} cruzamentos={x:3} "
              f"linhas_sobre_quest={o:3} tamanho={max(xs) - min(xs):.1f}x{max(ys) - min(ys):.1f}")
        lim = LIMITES.get(c.slug, (0, 0))
        bad += x > lim[0] or o > lim[1]
        if a.png:
            draw(c, pos, a.png / f"{c.slug}.png")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
