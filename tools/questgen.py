"""Gera as quests do FTB Quests (SNBT) a partir de quests/src/*.yaml.

Formatos de campo lidos do jar do FTB Quests 2001 (ver quests/FORMAT.md) e do item-filtro do
FTB Filter System (descoberto em jogo com makeTagFilter: tests/fixtures/tag_filter.json).
"""
import hashlib
import json
import math
import random
import shutil
import sys
import zlib
from dataclasses import dataclass, field
from pathlib import Path

import yaml

import layoutcheck
import snbt
from paths import BUILD, PACK, ROOT

SRC = ROOT / "quests" / "src"
OUT = PACK / "config" / "ftbquests" / "quests"
QUEST_TAGS = PACK / "kubejs" / "ecos" / "quest_tags.json"
KILL_TASKS = PACK / "kubejs" / "ecos" / "kill_tasks.json"
TABLES_SRC = ROOT / "quests" / "reward_tables.yaml"
LORE = ROOT / "docs" / "lore.md"
BOOK_PAGE_CHARS = 230
COIN = "ecos:fragmento_eco"
GROUPS = {"atos": "Atos", "caminhos": "Caminhos", "loja": "Loja", "diario": "Diário"}


class QuestError(ValueError):
    pass


def quest_id(path: str) -> str:
    """16 hex determinísticos; bit mais alto zerado (long positivo no FTB Quests)."""
    n = int(hashlib.sha1(path.encode("utf-8")).hexdigest()[:16], 16) & 0x7FFFFFFFFFFFFFFF
    return f"{n or 1:016X}"


@dataclass
class Chapter:
    slug: str
    title: str
    icon: str
    group: str
    act: int
    quests: list = field(default_factory=list)
    order: int = 0

    @classmethod
    def from_dict(cls, d: dict, order: int = 0) -> "Chapter":
        return cls(d["chapter"], d["title"], d["icon"], d.get("group", "atos"), int(d.get("act", 0)),
                   list(d.get("quests", [])), order)


def load_sources(directory: Path = SRC) -> list[Chapter]:
    files = sorted(directory.glob("*.yaml"))
    return [Chapter.from_dict(yaml.safe_load(f.read_text(encoding="utf-8")), i) for i, f in enumerate(files)]


def icon_value(icon: str) -> dict:
    """Ícone no formato do FTB Quests 2001 (sempre item): imagem .png vira ftbquests:custom_icon com NBT Icon."""
    if icon.endswith(".png"):
        return item_stack("ftbquests:custom_icon", {"Icon": icon})
    return item_stack(icon)


def item_stack(item_id: str, tag: dict | None = None) -> dict:
    stack = {"Count": snbt.Byte(1), "id": item_id}
    if tag:
        stack["tag"] = tag
    return stack


def lore_pages() -> dict[int, str]:
    import re
    parts = re.split(r"^### Página (\d+)[^\n]*\n", LORE.read_text(encoding="utf-8"), flags=re.M)
    pages = {}
    for i in range(1, len(parts), 2):
        body = parts[i + 1].split("\n## ")[0].strip()
        pages[int(parts[i])] = body
    return pages


def diary_book(n: int) -> dict:
    """Página n da lore (docs/lore.md) como livro escrito de Ilse Varrow."""
    text = lore_pages()[n]
    chunks, current = [], ""
    for line in text.splitlines():
        if current and len(current) + len(line) + 1 > BOOK_PAGE_CHARS:
            chunks.append(current)
            current = line
        else:
            current = f"{current}\n{line}" if current else line
    chunks.append(current)
    return item_stack("minecraft:written_book", {
        "title": f"Diário — Página {n}", "author": "Ilse Varrow", "generation": 0,
        "pages": [json.dumps({"text": c}, ensure_ascii=False) for c in chunks]})


def crate_stack(table_slug: str) -> dict:
    return item_stack("ftbquests:lootcrate", {"type": table_slug})


def load_tables(path: Path = TABLES_SRC) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) if path.exists() else {}


def image_line(q: dict) -> list[str]:
    """Arte da quest (Plano 4) como primeira linha da descrição, no formato do FTB Quests."""
    return [f"{{image:{q['image']} width:200 height:112 align:center}}"] if q.get("image") else []


def build_table(slug: str, t: dict) -> dict:
    return {
        "id": quest_id(f"table:{slug}"), "title": t["title"], "filename": slug, "icon": icon_value(f"ecos:textures/gui/crates/{slug}.png"),
        "loot_size": int(t.get("loot_size", 1)), "empty_weight": snbt.Float(0.0), "use_title": True,
        "rewards": [{"id": quest_id(f"table:{slug}#e{i}"), "type": "item", "item": item_stack(e["item"]),
                     "count": int(e.get("count", 1)), "weight": snbt.Float(float(e["weight"]))}
                    for i, e in enumerate(t["entries"])],
        "loot_crate": {"string_id": slug, "item_name": t["title"], "color": int(t["color"]), "glow": slug != "comum",
                       "drops": {"passive": 0, "monster": 0, "boss": 0}},
    }


def tag_filter_stack(tag: str) -> dict:
    return {"Count": snbt.Byte(1), "id": "ftbfiltersystem:smart_filter",
            "tag": {"ftbfiltersystem:filter": f"ftbfiltersystem:item_tag({tag})"}}


def _task(t: dict, tid: str) -> dict:
    if "item" in t:
        task = {"id": tid, "type": "item", "item": item_stack(t["item"]), "count": snbt.Long(t.get("count", 1))}
        if t.get("consume"):
            task["consume_items"] = True
        return task
    if "tag" in t:
        return {"id": tid, "type": "item", "item": tag_filter_stack(t["tag"]), "count": snbt.Long(t.get("count", 1))}
    if "kill" in t:
        return {"id": tid, "type": "kill", "entity": t["kill"], "value": snbt.Long(t.get("count", 1))}
    if "dimension" in t:
        return {"id": tid, "type": "dimension", "dimension": t["dimension"]}
    if t.get("checkmark"):
        return {"id": tid, "type": "checkmark"}
    raise QuestError(f"task desconhecida: {t}")


def table_long(table_slug: str) -> snbt.Long:
    return snbt.Long(int(quest_id(f"table:{table_slug}"), 16))


def _reward(r: dict, rid: str, tables: dict) -> dict:
    if "coins" in r:
        return {"id": rid, "type": "item", "item": item_stack(COIN), "count": int(r["coins"])}
    if "item" in r:
        return {"id": rid, "type": "item", "item": item_stack(r["item"]), "count": int(r.get("count", 1))}
    if "xp_levels" in r:
        return {"id": rid, "type": "xp_levels", "xp_levels": int(r["xp_levels"])}
    if "crate" in r:
        if r["crate"] not in tables:
            raise QuestError(f"caixa desconhecida: {r['crate']}")
        return {"id": rid, "type": "item", "item": crate_stack(r["crate"]), "count": int(r.get("count", 1))}
    if "page" in r:
        return {"id": rid, "type": "item", "item": diary_book(int(r["page"])), "count": 1}
    if "loot" in r:
        if r["loot"] not in tables:
            raise QuestError(f"reward table desconhecida: {r['loot']}")
        return {"id": rid, "type": "loot", "table_id": table_long(r["loot"])}
    raise QuestError(f"recompensa desconhecida: {r}")


GRID = 1.5            # distância entre colunas (unidades do FTB Quests; o ícone tem ~1)
_GAP_NODE = 1.5       # folga vertical mínima quest-quest na mesma coluna
_GAP_LINE = 1.25      # quest - linha que atravessa a coluna
_GAP_LINES = 0.5      # linha - linha
_GAP_STEEP = 2.0      # teto da folga extra pedida por linha íngreme
_CLEAR = 0.7          # linha a menos disso do centro de uma quest conta como "por cima" (layoutcheck mede 0.6)
_MIN_DIST = 1.4       # duas quests nunca ficam mais perto que isso
_STEP = 0.25          # y final em múltiplos de 0.25
_LAYOUT_CACHE: dict = {}
LAYOUT_CACHE_DIR = BUILD / "layout_cache"
RELAYER_MAX = 2


def layout(c: "Chapter") -> dict[str, tuple[float, float]]:
    """Posição de cada quest. `x`/`y` explícitos vencem; o resto é automático (FTB liga cada dependência local por um
    segmento reto entre centros, então o alvo é nenhuma linha cruzando outra nem passando por cima de quest):
    1. coluna = profundidade de dependência local (quest sem dependência local na coluna 0), com folga usada para
       encurtar linhas que vão dar em quest de muitos pais, abrir uma coluna depois de fonte com leque grande e,
       se ainda houver cruzamento, empurrar quest para a direita;
    2. ordem na coluna por mediana dos vizinhos, passadas ida e volta + troca de vizinhos, com pontos virtuais nas
       arestas que pulam colunas (não viram quest);
    3. y contínuo: cada coluna mantém a ordem com folga entre quests e as linhas longas que a atravessam (reta,
       y interpolado), puxando cada quest para a média dos vizinhos;
    4. reparo na geometria real (segmentos retos) para o que sobrou, depois aproxima cada quest dos vizinhos sem
       criar problema. Determinístico (semente = slug do capítulo); resultado guardado por conteúdo."""
    slugs = [q["slug"] for q in c.quests]
    present = set(slugs)
    local = {q["slug"]: [d for d in q.get("deps", []) if "/" not in d and d in present] for q in c.quests}
    fixed = {q["slug"]: (float(q["x"]), float(q["y"])) for q in c.quests if "x" in q and "y" in q}
    key = (c.slug, tuple((s, tuple(local[s]), fixed.get(s)) for s in slugs))
    if key not in _LAYOUT_CACHE:
        _LAYOUT_CACHE[key] = _disk_cached(key, lambda: _auto_layout(zlib.crc32(c.slug.encode("utf-8")), slugs, local,
                                                                    fixed))
    return dict(_LAYOUT_CACHE[key])


def _disk_cached(key, compute):
    """Cache em build/layout_cache/: chave = capítulo + código do layout (questgen.py e layoutcheck.py), então mudar
    o algoritmo ou o capítulo recalcula. Só economiza tempo; o resultado é o mesmo sem ele."""
    code = b"".join(Path(m.__file__).read_bytes() for m in (sys.modules[__name__], layoutcheck))
    h = hashlib.sha1(code + repr(key).encode("utf-8")).hexdigest()
    path = LAYOUT_CACHE_DIR / f"{h}.json"
    try:
        return {s: tuple(p) for s, p in json.loads(path.read_text(encoding="utf-8")).items()}
    except (OSError, ValueError):
        pass
    pos = compute()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(pos), encoding="utf-8")
    except OSError:
        pass
    return pos


def _auto_layout(seed: int, slugs: list[str], local: dict, fixed: dict) -> dict[str, tuple[float, float]]:
    if len(fixed) == len(slugs):
        return dict(fixed)
    children = {s: [] for s in slugs}
    for s in slugs:
        for p in local[s]:
            children[p].append(s)
    col = _columns(slugs, local, children)
    col, (layered, layers, up, down) = _relayer(slugs, local, children, col, seed)
    y = _assign_y(layers, up, down, col)
    pos = {s: fixed.get(s, (col[s] * GRID, round(y[s] / _STEP) * _STEP)) for s in slugs}
    best = None
    for k in range(6 if layered <= 1 else 1):  # várias sementes só quando o capítulo tem chance de zerar
        cand, bad = _repair(seed + k, slugs, local, children, pos, fixed)
        if best is None or bad < best[1]:
            best = (cand, bad)
        if bad == 0:
            break
    return best[0]


def _columns(slugs, local, children) -> dict[str, int]:
    depth: dict[str, int] = {}

    def d(s: str, seen=()) -> int:
        if s in depth:
            return depth[s]
        if s in seen:
            return 0
        depth[s] = 0 if not local[s] else 1 + max(d(p, seen + (s,)) for p in local[s])
        return depth[s]

    for s in slugs:
        d(s)
    base = dict(depth)
    # quest com folga anda para a direita quando as linhas dos filhos pesam mais (filho de muitos pais = leque)
    for _ in range(len(slugs)):
        changed = False
        for s in sorted(slugs, key=lambda s: -depth[s]):
            if not local[s] or not children[s]:
                continue
            hi = min(min(depth[c] for c in children[s]) - 1, base[s] + 2)  # até 2 colunas: fica perto do pai
            if hi > depth[s] and sum(len(local[c]) for c in children[s]) > len(local[s]):
                depth[s] = hi
                changed = True
        if not changed:
            break
    # fonte com leque grande: coluna vazia depois dela, as linhas do leque ficam menos íngremes
    if any(not local[s] and len(children[s]) >= 6 for s in slugs):
        for s in slugs:
            if local[s]:
                depth[s] += 1
    # fonte cujo filho mais próximo está a 3+ colunas (ex.: zinco do latão): fica logo antes dele, não na coluna 0
    for s in slugs:
        if not local[s] and children[s] and min(depth[c] for c in children[s]) >= 3:
            depth[s] = min(depth[c] for c in children[s]) - 1
    return depth


def _layered_graph(slugs, local, col):
    """Camadas com pontos virtuais ("~", pai, filho, coluna) nas arestas que pulam colunas."""
    layers: dict[int, list] = {}
    up: dict = {}
    down: dict = {}

    def add(n, k):
        layers.setdefault(k, []).append(n)
        up[n], down[n] = [], []

    for s in slugs:
        add(s, col[s])
    for s in slugs:
        for p in local[s]:
            prev = p
            for k in range(col[p] + 1, col[s]):
                v = ("~", p, s, k)
                add(v, k)
                down[prev].append(v)
                up[v].append(prev)
                prev = v
            down[prev].append(s)
            up[s].append(prev)
    return layers, up, down


def _layered_crossings(layers, down) -> int:
    t = 0
    for k in sorted(layers):
        if k + 1 not in layers:
            continue
        ix = {n: i for i, n in enumerate(layers[k + 1])}
        es = [(i, ix[b]) for i, a in enumerate(layers[k]) for b in down[a]]
        t += sum(1 for i, (a0, b0) in enumerate(es) for a1, b1 in es[i + 1:] if (a0 - a1) * (b0 - b1) < 0)
    return t


def _order(slugs, local, col, seed, restarts=20):
    """(cruzamentos, camadas ordenadas, up, down): mediana + troca de vizinhos, recomeços embaralhados."""
    layers, up, down = _layered_graph(slugs, local, col)
    rnd = random.Random(seed)
    ks = sorted(layers)

    def sweep(L):
        best = (_layered_crossings(L, down), {k: list(v) for k, v in L.items()})
        for it in range(12):
            if best[0] == 0:
                break
            ix = {n: i for k in ks for i, n in enumerate(L[k])}
            seq, nb = (ks[1:], up) if it % 2 == 0 else (ks[-2::-1], down)
            for k in seq:
                def key(n):
                    ps = sorted(ix[p] for p in nb[n])
                    if not ps:
                        return ix[n]
                    m = len(ps)
                    return ps[m // 2] if m % 2 else (ps[m // 2 - 1] + ps[m // 2]) / 2
                L[k].sort(key=key)
                for i, n in enumerate(L[k]):
                    ix[n] = i
            changed = True
            while changed:
                changed = False
                for k in ks:
                    row = L[k]
                    for i in range(len(row) - 1):
                        u, v = row[i], row[i + 1]
                        before = sum(ix[a] > ix[b] for nb2 in (up, down) for a in nb2[u] for b in nb2[v])
                        after = sum(ix[b] > ix[a] for nb2 in (up, down) for a in nb2[u] for b in nb2[v])
                        if after < before:
                            row[i], row[i + 1] = v, u
                            ix[u], ix[v] = i + 1, i
                            changed = True
            t = _layered_crossings(L, down)
            if t < best[0]:
                best = (t, {k: list(v) for k, v in L.items()})
        return best

    best = sweep({k: list(v) for k, v in layers.items()})
    for _ in range(restarts):
        if best[0] == 0:
            break
        L = {k: list(v) for k, v in layers.items()}
        for row in L.values():
            rnd.shuffle(row)
        r = sweep(L)
        if r[0] < best[0]:
            best = r
    return best[0], best[1], up, down


def _relayer(slugs, local, children, col, seed):
    """Se a ordem ainda cruza, empurra quest para a direita dentro da folga quando isso tira cruzamento."""
    best = _order(slugs, local, col, seed)
    last = max(col.values(), default=0)
    start = dict(col)
    improved = True
    while improved and best[0] > 0:
        improved = False
        for s in slugs:
            if not local[s]:
                continue
            hi = min((col[c] - 1 for c in children[s]), default=last + 1)
            for x in range(col[s] + 1, min(hi, start[s] + RELAYER_MAX) + 1):  # poucas colunas: linha curta
                c2 = dict(col)
                c2[s] = x
                r = _order(slugs, local, c2, seed, restarts=6)
                if r[0] < best[0]:
                    col, best, improved = c2, r, True
                    break
            if best[0] == 0:
                break
    return col, best


def _assign_y(layers, up, down, col) -> dict[str, float]:
    """y contínuo mantendo a ordem de cada coluna com folgas. Item da coluna é quest ou ponto virtual (y = reta entre
    as pontas). Relaxação: puxa cada quest para a média dos vizinhos e projeta as folgas (empurra o par violado)."""
    real = [n for ns in layers.values() for n in ns if not isinstance(n, tuple)]
    y = {}
    for ns in layers.values():
        for i, n in enumerate(ns):
            if not isinstance(n, tuple):
                y[n] = (i - (len(ns) - 1) / 2) * _GAP_NODE
    ends: dict = {n: [] for n in real}   # quest -> [(outra ponta, colunas de distância)]
    for n in real:
        for m in down[n]:
            span = 1
            while isinstance(m, tuple):
                m = down[m][0]
                span += 1
            ends[n].append((m, span))
            ends[m].append((n, span))

    def at(n):
        if not isinstance(n, tuple):
            return y[n], ((n, 1.0),)
        _, a, b, k = n
        t = (k - col[a]) / (col[b] - col[a])
        return (1 - t) * y[a] + t * y[b], ((a, 1 - t), (b, t))

    def steep(n, sign):
        """Folga para a linha de n que desce (sign=+1) ou sobe (-1) passar a _CLEAR da vizinha da coluna."""
        if isinstance(n, tuple):
            _, a, b, _k = n
            s = (y[b] - y[a]) / ((col[b] - col[a]) * GRID)
            return _CLEAR * (1 + s * s) ** 0.5
        g = 0.0
        for m, span in ends[n]:
            dy = (y[m] - y[n]) * sign
            if dy > 0:
                s = dy / (span * GRID)
                g = max(g, _CLEAR * (1 + s * s) ** 0.5)
        return g

    def gap(u, v):
        tu, tv = isinstance(u, tuple), isinstance(v, tuple)
        if tu and tv:
            return _GAP_LINES
        base = _GAP_NODE if not tu and not tv else _GAP_LINE
        return max(base, min(_GAP_STEEP, max(steep(u, +1), steep(v, -1))))

    def project(rounds):
        for _ in range(rounds):
            worst = 0.0
            for k in sorted(layers):
                ns = layers[k]
                for i in range(len(ns) - 1):
                    u, v = ns[i], ns[i + 1]
                    yu, wu = at(u)
                    yv, wv = at(v)
                    viol = gap(u, v) - (yv - yu)
                    if viol <= 1e-6:
                        continue
                    worst = max(worst, viol)
                    lam = viol / (sum(w * w for _, w in wu) + sum(w * w for _, w in wv))
                    for m, w in wu:
                        y[m] -= lam * w
                    for m, w in wv:
                        y[m] += lam * w
            if worst < 1e-4:
                return

    for _ in range(80):
        for n in real:
            if ends[n]:
                y[n] = 0.5 * y[n] + 0.5 * sum(y[m] for m, _ in ends[n]) / len(ends[n])
        project(20)
    project(3000)
    return y


def _repair(seed, slugs, local, children, pos, fixed, iters=6000, patience=4000):
    """Busca local na geometria real: move quest (y; coluna dentro da folga) ou desloca o bloco acima/abaixo dela
    para abrir espaço; custo = cruzamentos + linhas a menos de _CLEAR de quest (+ pouco por afastar do início).
    Depois, polimento: aproxima cada quest da média dos vizinhos sem piorar. Devolve (posições, problemas)."""
    rnd = random.Random(seed)
    P = dict(pos)
    orig = dict(pos)
    edges = [(p, s) for s in slugs for p in local[s]]
    inc: dict = {s: [] for s in slugs}
    for i, (p, s) in enumerate(edges):
        inc[p].append(i)
        inc[s].append(i)
    movable = [s for s in slugs if s not in fixed]

    def boxes():
        out = []
        for a, b in edges:
            (ax, ay), (bx, by) = P[a], P[b]
            out.append((min(ax, bx), max(ax, bx), min(ay, by), max(ay, by)))
        return out

    def crosses(i, j, box):
        (a, b), (e, f) = edges[i], edges[j]
        if a == e or a == f or b == e or b == f:
            return False
        p, q = box[i], box[j]
        if p[1] < q[0] or q[1] < p[0] or p[3] < q[2] or q[3] < p[2]:
            return False
        return layoutcheck.segments_cross(P[a], P[b], P[e], P[f])

    def near(s, i, box):
        a, b = edges[i]
        if s == a or s == b:
            return False
        (x, y), (x0, x1, y0, y1) = P[s], box[i]
        if x < x0 - _CLEAR or x > x1 + _CLEAR or y < y0 - _CLEAR or y > y1 + _CLEAR:
            return False
        return layoutcheck.point_segment_distance(P[s], P[a], P[b]) < _CLEAR

    def problems():
        box = boxes()
        out = []
        for i, (a, b) in enumerate(edges):
            out += [(a, b) + edges[j] for j in range(i + 1, len(edges)) if crosses(i, j, box)]
            out += [(a, b, s) for s in slugs if near(s, i, box)]
            if layoutcheck.edge_length(P[a], P[b]) > layoutcheck.MAX_EDGE:
                out.append((a, b))
        return out

    def local_bad(v):
        box = boxes()
        mine = inc[v]
        n = 0
        for i in mine:
            n += sum(1 for j in range(len(edges)) if crosses(i, j, box))
            n += sum(1 for s in slugs if near(s, i, box))
            n += layoutcheck.edge_length(P[edges[i][0]], P[edges[i][1]]) > layoutcheck.MAX_EDGE
        return n + sum(1 for j in range(len(edges)) if j not in mine and near(v, j, box))

    def excess(v):
        """Quanto as linhas de v passam do comprimento máximo: guia o reparo de linha longa passo a passo."""
        return 0.2 * sum(max(0.0, layoutcheck.edge_length(P[edges[i][0]], P[edges[i][1]]) - layoutcheck.MAX_EDGE)
                         for i in inc[v])

    def free(v, p):
        return all((P[u][0] - p[0]) ** 2 + (P[u][1] - p[1]) ** 2 >= _MIN_DIST ** 2 for u in slugs if u != v)

    cur = len(problems())
    best = (cur, dict(P))
    last_gain = 0
    hot = movable
    for it in range(iters):
        if cur == 0 or not movable or it - last_gain > patience:
            break
        if it % 25 == 0:
            hot = [s for t in problems() for s in t if s not in fixed] or movable
        v = rnd.choice(hot) if rnd.random() < 0.8 else rnd.choice(movable)
        if rnd.random() < 0.1:  # abre espaço: desloca tudo acima (ou abaixo) de v
            side = rnd.choice((-1, 1))
            dy = rnd.choice((0.5, 1.0, 1.5)) * side
            yv = P[v][1]
            group = [u for u in movable if (P[u][1] - yv) * side > 0 or (u == v and rnd.random() < 0.5)]
            saved = {u: P[u] for u in group}
            for u in group:
                P[u] = (P[u][0], P[u][1] + dy)
            if any((P[a][0] - P[b][0]) ** 2 + (P[a][1] - P[b][1]) ** 2 < _MIN_DIST ** 2
                   for a in group for b in slugs if b not in saved):
                P.update(saved)
                continue
            new = len(problems())
            if new < cur or (new == cur and rnd.random() < 0.2):
                cur = new
                if cur < best[0]:
                    best, last_gain = (cur, dict(P)), it
            else:
                P.update(saved)
            continue
        old = P[v]
        nx, ny = old
        if rnd.random() < 0.25 and local[v]:
            lo = max(P[p][0] for p in local[v]) + GRID
            hi = min((P[c][0] for c in children[v]), default=old[0] + 2 * GRID) - GRID
            opts = [x for x in (old[0] - GRID, old[0] + GRID) if lo - 1e-9 <= x <= hi + 1e-9]
            if opts:
                nx = rnd.choice(opts)
        if nx == old[0] or rnd.random() < 0.5:
            ny = old[1] + rnd.choice((0.25, 0.5, 0.75, 1, 1.5, 2, 3)) * rnd.choice((-1, 1))
        if not free(v, (nx, ny)):
            continue
        b0 = local_bad(v)
        s0 = 0.03 * ((old[0] - orig[v][0]) ** 2 + (old[1] - orig[v][1]) ** 2) + excess(v)
        P[v] = (nx, ny)
        b1 = local_bad(v)
        s1 = 0.03 * ((nx - orig[v][0]) ** 2 + (ny - orig[v][1]) ** 2) + excess(v)
        d = (b1 - b0) + (s1 - s0)
        temp = max(0.3 * (1 - it / iters), 1e-3)
        if d <= 0 or rnd.random() < math.exp(-d / temp):
            cur += b1 - b0
            if cur < best[0]:
                best, last_gain = (cur, dict(P)), it
        else:
            P[v] = old
    cur, P = best[0], dict(best[1])

    def pull(v):
        t = 0.0
        for i in inc[v]:
            a, b = edges[i]
            o = P[b] if a == v else P[a]
            t += (o[1] - P[v][1]) ** 2 / max(abs(o[0] - P[v][0]) / GRID, 1)
        return t

    for _ in range(30):  # polimento
        moved = False
        for v in movable:
            if not inc[v]:
                continue
            old = P[v]
            b0 = local_bad(v)
            if local[v] and (old[0] > orig[v][0] or not children[v]) and old[0] - GRID > max(P[p][0] for p in local[v]):
                # empurrada para a direita (pelo reparo, ou folha): volta uma coluna, y entre o atual e o do pai, se nada piora
                py = sum(P[p][1] for p in local[v]) / len(local[v])
                back = False
                for k in range(9):
                    cand = (old[0] - GRID, round((old[1] + (py - old[1]) * k / 8) / _STEP) * _STEP)
                    if not free(v, cand):
                        continue
                    P[v] = cand
                    b1 = local_bad(v)
                    if b1 <= b0:
                        cur += b1 - b0
                        back = True
                        break
                    P[v] = old
                if back:
                    moved = True
                    continue
            s0 = pull(v)
            want =sum(P[edges[i][1] if edges[i][0] == v else edges[i][0]][1] for i in inc[v]) / len(inc[v])
            step = max(-1.5, min(1.5, want - old[1]))
            for st in (step, step / 2, _STEP if step > 0 else -_STEP):
                ny = round((old[1] + st) / _STEP) * _STEP
                if ny == old[1] or not free(v, (old[0], ny)):
                    continue
                P[v] = (old[0], ny)
                b1 = local_bad(v)
                if b1 <= b0 and pull(v) < s0 - 1e-6:
                    cur += b1 - b0
                    moved = True
                    break
                P[v] = old
        if not moved:
            break
    return P, cur


def resolve_dep(dep: str, chapter: str, known: set[str]) -> str:
    path = dep if "/" in dep else f"{chapter}/{dep}"
    if path not in known:
        raise QuestError(f"dependência inexistente: {dep} (em {chapter})")
    return path


def id_base(chapter_slug: str, quest: dict) -> str:
    """Base dos IDs da quest (e de `#t<i>`/`#r<i>`): `legacy_id` se houver, senão `capitulo/slug`.
    Único ponto que decide isso: quem mover/renomear uma quest mantém o progresso dos jogadores."""
    return quest.get("legacy_id") or f"{chapter_slug}/{quest['slug']}"


def all_paths(chapters: list[Chapter]) -> set[str]:
    return {f"{c.slug}/{q['slug']}" for c in chapters for q in c.quests}


def used_tags(chapters: list[Chapter]) -> set[str]:
    return {t["tag"] for c in chapters for q in c.quests for t in q.get("tasks", []) if "tag" in t}


def kill_tasks(chapters: list[Chapter]) -> dict[str, list[str]]:
    """Entidade → ids (hex) das tasks de kill. O script 35_ecos_kill_share.js credita todo jogador perto do chefe."""
    out: dict[str, list[str]] = {}
    for c in chapters:
        for q in c.quests:
            for i, t in enumerate(q.get("tasks", [])):
                if "kill" in t:
                    out.setdefault(t["kill"], []).append(quest_id(f"{id_base(c.slug, q)}#t{i}"))
    return out


def build(chapters: list[Chapter], tables: dict) -> dict[str, str]:
    known = all_paths(chapters)
    bases = {f"{c.slug}/{q['slug']}": id_base(c.slug, q) for c in chapters for q in c.quests}
    files: dict[str, str] = {}
    groups = sorted({c.group for c in chapters})
    files["chapter_groups.snbt"] = snbt.dumps({"chapter_groups": [
        {"id": quest_id(f"group:{g}"), "title": GROUPS.get(g, g)} for g in groups]}) + "\n"
    files["data.snbt"] = snbt.dumps({
        "version": 13, "title": "Ecos do Selo", "icon": icon_value("ecos:artefato_selo"),
        "default_reward_team": False, "default_consume_items": False, "default_quest_shape": "circle",
        "progression_mode": "linear", "show_lock_icons": True, "drop_loot_crates": False,
    }) + "\n"
    for slug, t in tables.items():
        files[f"reward_tables/{slug}.snbt"] = snbt.dumps(build_table(slug, t)) + "\n"
    for c in chapters:
        quests = []
        pos = layout(c)
        for q in c.quests:
            path = id_base(c.slug, q)
            quest = {
                "id": quest_id(path), "title": q["title"], "description": image_line(q) + list(q.get("desc", [])),
                "x": pos[q["slug"]][0], "y": pos[q["slug"]][1],
                "dependencies": [quest_id(bases[resolve_dep(d, c.slug, known)]) for d in q.get("deps", [])],
                "tasks": [_task(t, quest_id(f"{path}#t{i}")) for i, t in enumerate(q.get("tasks", []))],
                "rewards": [_reward(r, quest_id(f"{path}#r{i}"), tables) for i, r in enumerate(q.get("rewards", []))],
            }
            if q.get("shape"):
                quest["shape"] = q["shape"]
            if q.get("icon"):
                quest["icon"] = icon_value(q["icon"])
            if q.get("repeatable"):
                quest["can_repeat"] = True
            quests.append(quest)
        files[f"chapters/{c.slug}.snbt"] = snbt.dumps({
            "id": quest_id(f"chapter:{c.slug}"), "group": quest_id(f"group:{c.group}"), "order_index": c.order,
            "filename": c.slug, "title": c.title, "icon": icon_value(c.icon), "default_quest_shape": "",
            "default_hide_dependency_lines": False, "quests": quests, "quest_links": [], "images": [],
        }) + "\n"
    return files


def write(out: Path = OUT, chapters: list[Chapter] | None = None, tables: dict | None = None) -> int:
    chapters = load_sources() if chapters is None else chapters
    files = build(chapters, load_tables() if tables is None else tables)
    if out.exists():
        shutil.rmtree(out)
    for rel, text in files.items():
        p = out / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    QUEST_TAGS.write_text(json.dumps({"tags": sorted(used_tags(chapters))}, indent=1) + "\n", encoding="utf-8")
    KILL_TASKS.write_text(json.dumps({"kills": kill_tasks(chapters)}, indent=1) + "\n", encoding="utf-8")
    return sum(len(c.quests) for c in chapters)


if __name__ == "__main__":
    n = write()
    print(f"{n} quests geradas em {OUT}")
