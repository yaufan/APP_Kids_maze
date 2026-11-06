"""Art kit for 迷宮小冒險: ONE geometry, THREE styles.

Every picture (road tiles, grounds, 土豆 the mole, each world's hero, home, family, items, scenery,
stickers and card) is described ONCE as a list of pieces (`Piece`): shapely shapes with plain colours
and a few hints. Three renderers paint the same list, so switching style never moves anything:

    a  羊毛氈布書風  felt quiet book. Each piece is a felt cut-out: a soft shadow under it, an outline
                     pushed about a little (deterministic noise), short hair strokes across the edge
                     (the fuzz), a lighter band on its top-left edge and a darker one on its
                     bottom-right (the puffy look), fibre strokes on the surface and a running stitch
                     (explicit dashes) sewn just inside the edge. Faces are embroidered: satin-stitch
                     eyes with a white glint, thread smiles, felt cheeks; buttons are sewing buttons.
    b  像素小遊戲風  chunky pixels. Everything is rasterised (pixel centres) onto a grid of `px` units
                     (4 on a 100-unit file, so 25 x 25 per tile; 5 on bigger files); colours snap to a
                     small bright palette per world; each object gets a 1-pixel dark outline (and
                     pieces with `po` an inner outline over the parts under them), a light top-left
                     and dark bottom-right pixel bevel; eyes are pixel blocks with a white glint.
    c  果凍糖果風    glossy jelly and gummy candy: radial-gradient bodies with a darker rim, a white
                     crescent highlight on the top-left, glint dots; the road is a see-through jelly
                     tube (layered translucent fills, a light core, a white highlight streak).
                     No blend modes, no filters: only plain fills, strokes and gradients.

THE CONTRACT with the app is docs/art.md (files, viewBoxes, the road tiles). `World.build()` writes
every file of a world; `check_svg()` enforces the flutter_svg rules and `check_world()` the contract.
`python3 build.py fluttercheck` draws every file with the real flutter_svg and compares with Chromium.

flutter_svg limits (hard rules, enforced by check_svg): no <filter>, <mask>, <style>, style=, CSS,
<text>, <image>, <foreignObject>, <pattern>, blend modes; every drawing element carries its own
fill/stroke attribute; under ~70 KB and fewer than 800 <use> per file. This kit writes no <use> and
no clip paths at all: shapes are clipped with shapely before they are written.

------------------------------------------------------------------------------------------------
THE ROAD TILES (docs/art.md): tile_<n>.svg, n = up 1 + right 2 + down 4 + left 8. `tile_geom(n)` is
the one geometry: the road is 62 wide (19..81); an open side is a straight band to the tile edge
(and 30 units beyond it, so every effect is computed as if the neighbour were there, then clipped);
a turn (3, 6, 12, 9) is a quarter ring of constant width round the inner corner (inner radius 19);
T-crossings and the cross round their inner corners with the same radius 19; a dead end (1, 2, 4, 8)
ends in a half circle. Because every effect depends only on that extended shape:
  a: stitches are dashes with HALF a gap at each tile edge, so two tiles make one full gap; the
     outline noise fades to nothing at the tile edges; bands and shadows come from the extended shape;
  b: the pixel grid has its lines on the tile edges (25 x 25), the border and bevel rows run straight
     across; the road's sand is 20..80 and its 1-pixel border 16..20 / 80..84;
  c: rim, body, core and the highlight streak (the part of an inset line that faces the top-left)
     are insets of the extended shape, so they continue straight into the next tile.
`python3 build.py seams <world>` renders the tiles and compares every edge that can meet.

------------------------------------------------------------------------------------------------
HOW TO DESCRIBE A WORLD (copy world_garden.py)

    W = kit.World("garden", "花園",
        road={"a": dict(fill=..., stitch=...),                      # felt path and its stitch
              "b": dict(fill=..., speck=..., shade=..., light=..., border=...),   # pixel road
              "c": dict(body=..., rim=..., glow=..., shadow=...)},  # jelly road
        ground={"a": dict(base=..., fibres=(light, dark)),          # felt cloth
                "b": dict(base=..., specks=[(colour, chance), ...], stamps=[(rows, palette, per_1000px)]),
                "c": dict(top=..., bottom=..., sprinkles=(colours...), n=per_10000_units)},
        pixel=dict(outline=..., palette=[...], map={felt colour: pixel colour}),
        jelly=dict(shadow=..., map={felt colour: jelly colour}),
        bits=fn(style) -> pieces,           # small things sewn/printed on the bg (optional)
        hero=fn, home=fn, family=fn, star=fn, key=fn, gate=fn,      # fn(style) -> pieces
        deco=[6 fns], stickers=[10 fns], card=fn)
    W.build()

Every art function gets the style ("a"/"b"/"c") and returns a list of pieces in its file's units
(hero/home/star/key/gate/deco: 100 x 100; family 400 x 400; sticker 200 x 200, the kit adds the
round sticker; card 300 x 200). Normally ignore the style: the same pieces are drawn three ways.
Use the style only for a colour that must differ (pass cols={"b": ..., "c": ...} on a piece) or for
a whole small part that is only in some styles (only="ac").

Pieces (all coordinates in the file's units; draw a character round (0, 0) and `place()` it):
    F(shape, col, st=None, inset=None, lift=1, shade=True, fuzz=True, po=None, gloss=True, only=None)
        a filled felt piece. shape: a point list or any shapely polygon (use E(), U(), rrect()...).
        st: colour of the running stitch inside its edge (a); inset in screen dp (default 3.4).
        lift 0: sewn flat on the piece under it (stripes, cheeks): no shadow, no pixel outline.
        po: pixel outline over the parts under it (default: on for lifted pieces >= 4 pixels).
    L(points, col, w, dash=None)     an embroidered line (antennae, smiles, claws); w in units
    EYE(cx, cy, r, look=(0, 0))      an eye: satin-stitch / pixel block / gummy eye with glints
    BTN(cx, cy, r, col)              a sewing button
    OBJ(pieces, shadow=1)            one object: its parts are outlined together in b, and it casts a
                                     soft shadow in a and c. Always wrap a character or a thing in it.
    place(pieces, dx, dy, s, rot, flip)   move/scale/rotate/mirror a list of pieces
Colours: give the felt (style a) colour; b snaps it to the world's pixel palette (or `pixel.map`),
c uses `jelly.map` or the colour itself. A piece can override with cols={"b": ..., "c": ...}.

Screen scale: the felt details (stitch width and dashes, fuzz, shadows) and jelly rims are given in
screen dp and divided by K, the dp per unit a file is shown at (KIND below), so they look the same
on every file whatever its viewBox. Pixel size per file kind is KIND[...]["px"].

Determinism: all randomness is seeded from md5 of the file name and the piece's index, never from
Python's hash(), so the same code gives the same bytes on every run.
"""
import colorsys
import hashlib
import math
import pathlib
import random
import re
import xml.etree.ElementTree as ET

import numpy as np
import shapely
from shapely import affinity
from shapely.geometry import LineString, MultiLineString, Point, Polygon
from shapely.geometry import box as sbox
from shapely.geometry.polygon import orient
from shapely.ops import linemerge, substring, unary_union

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ART = ROOT / "app" / "assets" / "art"
STYLES = ("a", "b", "c")

# file kinds: viewBox (w, h), K = screen dp per unit when the app shows it, px = units per pixel (b)
KIND = {
    "tile": dict(w=100, h=100, K=.55, px=4),
    "item": dict(w=100, h=100, K=.55, px=4),     # hero, home, star, key, gate, deco_n
    "bg": dict(w=600, h=800, K=.6, px=5),
    "family": dict(w=400, h=400, K=.8, px=5),
    "sticker": dict(w=200, h=200, K=.5, px=5),
    "card": dict(w=300, h=200, K=.55, px=5),
    "tudou": dict(w=200, h=200, K=.7, px=5),
}
ROAD0, ROAD1 = 19.0, 81.0       # the road band on a tile (docs/art.md)
HALF = (ROAD1 - ROAD0) / 2      # 31
EXT = 30.0                      # how far an open side is extended beyond the tile edge

# common colours (style a)
DARK = "#3B2C29"        # embroidery thread for eyes and smiles
CHEEK = "#FF9DAE"
WHITE = "#FFFDF8"
SHADOW = "#2A1C14"      # felt shadows
WARM = "#2E2018"        # felt shading goes towards this


# ================================================================ numbers and colours
def n(v):
    """A number, short: one decimal, no trailing .0, no leading 0, no -0."""
    s = f"{v:.1f}"
    if s.endswith(".0"):
        s = s[:-2]
    if s == "-0":
        s = "0"
    if s.startswith("0."):
        s = s[1:]
    elif s.startswith("-0."):
        s = "-" + s[2:]
    return s


def _join(nums):
    """Numbers for path data with the fewest separators (a minus sign separates by itself)."""
    out = ""
    for i, s in enumerate(nums):
        if i and not s.startswith("-"):
            out += " "
        out += s
    return out


def _rgb(h):
    h = h.lstrip("#")
    return [int(h[i:i + 2], 16) for i in (0, 2, 4)]


def _hexrgb(r, g, b):
    return "#%02X%02X%02X" % tuple(max(0, min(255, round(v))) for v in (r, g, b))


def mix(a, b, t):
    """Colour a moved t of the way to colour b."""
    return _hexrgb(*[x + (y - x) * t for x, y in zip(_rgb(a), _rgb(b))])


def lt(c, t):
    return mix(c, "#FFFFFF", t)


def dk(c, t):
    return mix(c, WARM, t)


def tone(c, l=1.0, s=1.0, dh=0.0):
    """Scale lightness and saturation, shift hue."""
    h, L, S = colorsys.rgb_to_hls(*[x / 255 for x in _rgb(c)])
    r, g, b = colorsys.hls_to_rgb((h + dh) % 1, max(0, min(1, L * l)), max(0, min(1, S * s)))
    return _hexrgb(r * 255, g * 255, b * 255)


def _dist2(a, b):
    (r1, g1, b1), (r2, g2, b2) = _rgb(a), _rgb(b)
    rm = (r1 + r2) / 2
    return (2 + rm / 256) * (r1 - r2) ** 2 + 4 * (g1 - g2) ** 2 + (2 + (255 - rm) / 256) * (b1 - b2) ** 2


def nearest(c, palette):
    return min(palette, key=lambda p: _dist2(c, p))


def _op(op, attr="opacity"):
    return f' {attr}="{op:.2f}"'.replace('"0.', '".') if op < .999 else ""


# ================================================================ geometry: point lists
def ellp(cx, cy, rx, ry=None, k=None, rot=0.0):
    """Points of an ellipse (k points; by default about one per 2.5 units of edge)."""
    ry = rx if ry is None else ry
    if k is None:
        k = int(max(24, min(120, math.pi * (rx + ry) / 2.5)))
    a = math.radians(rot)
    ca, sa = math.cos(a), math.sin(a)
    out = []
    for i in range(k):
        t = 2 * math.pi * i / k
        x, y = rx * math.cos(t), ry * math.sin(t)
        out.append((cx + x * ca - y * sa, cy + x * sa + y * ca))
    return out


def crs(ctrl, k=10, closed=True):
    """Catmull-Rom spline through the control points, as a dense point list."""
    m = len(ctrl)
    out = []
    segs = m if closed else m - 1
    for i in range(segs):
        p0 = ctrl[(i - 1) % m] if closed else ctrl[max(i - 1, 0)]
        p1, p2 = ctrl[i], ctrl[(i + 1) % m]
        p3 = ctrl[(i + 2) % m] if closed else ctrl[min(i + 2, m - 1)]
        for j in range(k):
            t = j / k
            t2, t3 = t * t, t * t * t
            out.append(tuple(.5 * (2 * p1[q] + (-p0[q] + p2[q]) * t + (2 * p0[q] - 5 * p1[q] + 4 * p2[q] - p3[q]) * t2
                                   + (-p0[q] + 3 * p1[q] - 3 * p2[q] + p3[q]) * t3) for q in (0, 1)))
    if not closed:
        out.append(tuple(ctrl[-1]))
    return out


def rrect_pts(x, y, w, h, r, k=6):
    r = max(.01, min(r, w / 2, h / 2))
    out = []
    for cx, cy, a0 in ((x + w - r, y + r, -90), (x + w - r, y + h - r, 0), (x + r, y + h - r, 90), (x + r, y + r, 180)):
        for j in range(k + 1):
            a = math.radians(a0 + 90 * j / k)
            out.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return out


def star_pts(R, r, cx=0.0, cy=0.0, k=5, rot=-90.0):
    out = []
    for i in range(2 * k):
        a = math.radians(rot + 180 * i / k)
        rr = R if i % 2 == 0 else r
        out.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return out


def heart_pts(cx, cy, s):
    out = []
    for i in range(60):
        t = 2 * math.pi * i / 60
        x = 16 * math.sin(t) ** 3
        y = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
        out.append((cx + x * s / 16, cy + y * s / 16))
    return out


def tf(pts, dx=0.0, dy=0.0, rot=0.0, s=1.0, sx=None):
    a = math.radians(rot)
    ca, sa = math.cos(a), math.sin(a)
    sx = s if sx is None else sx
    return [(x * sx * ca - y * s * sa + dx, x * sx * sa + y * s * ca + dy) for x, y in pts]


# ================================================================ geometry: shapely shapes
def G(x):
    """Anything shape-like (a point list or a shapely geometry) as a valid shapely geometry."""
    if isinstance(x, (list, tuple)):
        return Polygon(x).buffer(0)
    return x


def E(cx, cy, rx, ry=None, rot=0.0):
    """An ellipse shape."""
    return Polygon(ellp(cx, cy, rx, ry, rot=rot))


def R(x, y, w, h, r=0.0):
    """A rectangle with round corners (r) as a shape."""
    return Polygon(rrect_pts(x, y, w, h, r)) if r > 0 else sbox(x, y, x + w, y + h)


def U(*gs):
    return unary_union([G(g) for g in gs])


def soft(g, r):
    """Round the corners of a shape (convex ones, then concave ones)."""
    return G(g).buffer(-r, join_style="round").buffer(2 * r, join_style="round").buffer(-r, join_style="round")


def tube(pts, w, cap="round"):
    """A stroke of width w along a polyline, as a shape."""
    return LineString(pts).buffer(w / 2, cap_style=cap, join_style="round")


def star_shape(R_, cx=0.0, cy=0.0, rot=-90.0, ratio=.5):
    return soft(Polygon(star_pts(R_, R_ * ratio, cx, cy, 5, rot)), R_ * .12)


def polys(g):
    """The polygons of any geometry (empty and tiny parts dropped)."""
    if g is None or g.is_empty:
        return []
    if g.geom_type == "Polygon":
        return [g] if g.area > .02 else []
    if hasattr(g, "geoms"):
        out = []
        for p in g.geoms:
            out += polys(p)
        return out
    return []


def lines_of(g):
    if g is None or g.is_empty:
        return []
    if g.geom_type == "LineString":
        return [g] if g.length > .05 else []
    if g.geom_type == "LinearRing":
        return [LineString(g.coords)]
    if hasattr(g, "geoms"):
        out = []
        for p in g.geoms:
            out += lines_of(p)
        return out
    return []


def bounds_size(g):
    x0, y0, x1, y1 = g.bounds
    return min(x1 - x0, y1 - y0)


# ================================================================ pieces
class Piece:
    """One part of a picture. kind: fill | line | eye | button | obj | road | ground."""

    def __init__(self, kind, geom, col, w=0.0, r=0.0, st=None, inset=None, lift=1, shade=True, fuzz=True,
                 po=None, gloss=True, only=None, op=1.0, cols=None, data=None, dash=None, look=(0.0, 0.0)):
        self.kind, self.geom, self.col = kind, geom, col
        self.w, self.r, self.st, self.inset, self.lift = w, r, st, inset, lift
        self.shade, self.fuzz, self.po, self.gloss, self.only, self.op = shade, fuzz, po, gloss, only, op
        self.cols, self.data, self.dash, self.look = cols or {}, data, dash, look

    def copy(self, **kw):
        p = Piece.__new__(Piece)
        p.__dict__.update(self.__dict__)
        p.__dict__.update(kw)
        return p


def F(shape, col, **kw):
    """A filled piece (felt cut-out / pixel area / gummy part)."""
    return Piece("fill", G(shape), col, **kw)


def L(pts, col=DARK, w=2.0, **kw):
    """An embroidered line of width w (units), e.g. antennae, smiles, claws."""
    return Piece("line", LineString(pts), col, w=w, **kw)


def EYE(cx, cy, r, **kw):
    """An eye: a dark oval (r tall) with a white glint."""
    return Piece("eye", Point(cx, cy), DARK, r=r, **kw)


def BTN(cx, cy, r, col, **kw):
    """A sewing button."""
    return Piece("button", Point(cx, cy), col, r=r, **kw)


def OBJ(pieces, shadow=1):
    """One object: a marker (its silhouette) followed by its pieces."""
    sil = unary_union([p.geom.buffer(p.w / 2) if p.kind == "line" else
                       (p.geom.buffer(p.r) if p.kind in ("eye", "button") else p.geom)
                       for p in pieces if p.kind in ("fill", "line", "eye", "button")])
    return [Piece("obj", sil, "#000000", lift=shadow)] + list(pieces)


def place(pieces, dx=0.0, dy=0.0, s=1.0, rot=0.0, flip=False):
    """Move a list of pieces: mirror (about x = 0), scale, rotate (degrees), then move."""
    a = math.radians(rot)
    fx = -1.0 if flip else 1.0
    m = [s * math.cos(a) * fx, -s * math.sin(a), s * math.sin(a) * fx, s * math.cos(a), dx, dy]
    out = []
    for p in pieces:
        if p.kind in ("road", "ground"):
            out.append(p)
            continue
        q = p.copy(geom=affinity.affine_transform(p.geom, m), w=p.w * s, r=p.r * s)
        if p.kind == "eye":
            q.look = (p.look[0] * fx, p.look[1])
        out.append(q)
    return out


def recolor(pieces, cmap):
    return [p.copy(col=cmap.get(p.col, p.col), st=cmap.get(p.st, p.st)) for p in pieces]


# ================================================================ path data
def pd(pts, closed=True):
    """Compact path data: an absolute move, then relative lines in tenths of a unit."""
    q = []
    for x, y in pts:
        t = (round(x * 10), round(y * 10))
        if not q or t != q[-1]:
            q.append(t)
    if closed and len(q) > 1 and q[-1] == q[0]:
        q.pop()
    if not q:
        return ""
    s = "M" + _join([n(q[0][0] / 10), n(q[0][1] / 10)])
    if len(q) > 1:
        nums = []
        for (x0, y0), (x1, y1) in zip(q, q[1:]):
            nums += [n((x1 - x0) / 10), n((y1 - y0) / 10)]
        s += "l" + _join(nums)
    return s + ("z" if closed else "")


def gd(g, tol=0.0):
    """Path data of a (multi)polygon, holes included (draw with fill-rule evenodd)."""
    out = []
    for p in polys(g):
        if tol:
            p = p.simplify(tol)
            if p.is_empty:
                continue
        out.append(pd(list(p.exterior.coords)[:-1]))
        for r in p.interiors:
            out.append(pd(list(r.coords)[:-1]))
    return "".join(out)


def has_holes(g):
    return any(len(p.interiors) for p in polys(g))


# ================================================================ one SVG being written
class Ctx:
    """One file being drawn: its box, its screen scale, the world's palettes, defs and body."""

    def __init__(self, name, style, kind, world=None):
        k = KIND[kind]
        self.name, self.style, self.kind, self.world = name, style, kind, world
        self.W, self.H, self.K, self.px = k["w"], k["h"], k["K"], k["px"]
        self.u = 1.0 / self.K              # units per screen dp
        self.box = sbox(0, 0, self.W, self.H)
        shapely.prepare(self.box)
        self.defs, self.body, self.grads = [], [], {}

    def rnd(self, *key):
        h = hashlib.md5("|".join(map(str, (self.name, self.style) + key)).encode()).hexdigest()
        return random.Random(int(h[:12], 16))

    def clip(self, g):
        if g.is_empty:
            return g
        if self.box.contains(g):
            return g
        return g.intersection(self.box)

    def edge_dist(self, x, y):
        """Distance to the nearest edge of the file (negative outside)."""
        return np.minimum(np.minimum(x, self.W - x), np.minimum(y, self.H - y))

    def taper(self, P, d):
        return np.clip(self.edge_dist(P[:, 0], P[:, 1]) / d, 0.0, 1.0)

    def fill(self, g, col, op=1.0, tol=0.0, clip=True):
        g = self.clip(g) if clip else g
        d = gd(g, tol)
        if not d:
            return
        rule = ' fill-rule="evenodd"' if has_holes(g) else ""
        self.body.append(f'<path d="{d}" fill="{col}"{rule}{_op(op)}/>')

    def stroke(self, d, col, w, op=1.0, extra="", cap="round"):
        if not d:
            return
        ws = n(w) if w >= .95 else f"{max(w, .2):.2f}".lstrip("0")
        self.body.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{ws}" stroke-linecap="{cap}" '
                         f'stroke-linejoin="round"{_op(op)}{extra}/>')

    def radial(self, stops, cx=.38, cy=.32, r=.75):
        """A radial gradient over each shape's own box (objectBoundingBox); returns fill=url(...)."""
        key = (tuple(stops), cx, cy, r)
        if key not in self.grads:
            gid = f"g{len(self.grads) + 1}"
            self.grads[key] = gid
            st = "".join(f'<stop offset="{o:g}" stop-color="{c}"/>' for o, c in stops)
            self.defs.append(f'<radialGradient id="{gid}" cx="{cx:g}" cy="{cy:g}" r="{r:g}">{st}</radialGradient>')
        return f"url(#{self.grads[key]})"

    def linear(self, stops, x1=0, y1=0, x2=0, y2=1):
        key = (tuple(stops), x1, y1, x2, y2, "lin")
        if key not in self.grads:
            gid = f"g{len(self.grads) + 1}"
            self.grads[key] = gid
            st = "".join(f'<stop offset="{o:g}" stop-color="{c}"/>' for o, c in stops)
            self.defs.append(f'<linearGradient id="{gid}" x1="{x1:g}" y1="{y1:g}" x2="{x2:g}" y2="{y2:g}">{st}</linearGradient>')
        return f"url(#{self.grads[key]})"

    def svg(self):
        defs = f"<defs>{''.join(self.defs)}</defs>" if self.defs else ""
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {n(self.W)} {n(self.H)}" '
                f'width="{n(self.W)}" height="{n(self.H)}">{defs}{"".join(self.body)}</svg>\n')

    # colours of a piece in this style
    def colour(self, p, c=None):
        c = p.col if c is None else c
        if self.style in p.cols and c == p.col:
            return p.cols[self.style]
        w = self.world
        if self.style == "b":
            pal = (w.pixel if w else {}) or {}
            if c in pal.get("map", {}):
                return pal["map"][c]
            if pal.get("palette"):
                return nearest(c, pal["palette"])
            return tone(c, s=1.15)
        if self.style == "c":
            pal = (w.jelly if w else {}) or {}
            return pal.get("map", {}).get(c, c)
        return c


# ================================================================ helpers on rings
def _ring_pts(ring, step):
    """A closed ring resampled every ~step units: (points array, length)."""
    Lr = ring.length
    k = max(8, int(round(Lr / step)))
    d = np.arange(k) * (Lr / k)
    P = shapely.get_coordinates(shapely.line_interpolate_point(LineString(ring.coords), d))
    return P, Lr


def _normals(P):
    """Outward normals of a counter-clockwise ring (exterior) / inward-facing hole (both outward from the material)."""
    t = np.roll(P, -1, 0) - np.roll(P, 1, 0)
    t = t / (np.linalg.norm(t, axis=1, keepdims=True) + 1e-9)
    return np.stack([t[:, 1], -t[:, 0]], 1)


def _oriented_rings(poly):
    poly = orient(poly, 1.0)
    return [poly.exterior] + list(poly.interiors)


def wobble(c, g, amp, step, key):
    """The shape with its outline pushed about by smooth deterministic noise (amp units). The noise
    fades out near the file's edges, so a shape cut by the edge (a road) meets its neighbour."""
    out = []
    for pi, poly in enumerate(polys(g)):
        rings = []
        for ri, ring in enumerate(_oriented_rings(poly)):
            P, Lr = _ring_pts(ring, step)
            Nn = _normals(P)
            k = len(P)
            rnd = c.rnd(key, pi, ri, "wob")
            s = np.arange(k) / k
            f1 = max(1, round(Lr / (step * 9)))
            f2 = max(2, round(Lr / (step * 3.5)))
            noise = (.6 * np.sin(2 * np.pi * f1 * s + rnd.uniform(0, 6.3))
                     + .35 * np.sin(2 * np.pi * f2 * s + rnd.uniform(0, 6.3))
                     + np.array([rnd.uniform(-.4, .4) for _ in range(k)]))
            P2 = P + Nn * (amp * noise * c.taper(P, 3 * c.u))[:, None]
            rings.append(P2)
        q = Polygon(rings[0], rings[1:]).buffer(0)
        out.append(q if not q.is_empty else poly)
    return unary_union(out) if out else g


def dashes(line, period, dash_frac, closed=False):
    """Explicit dashes along a line: a whole number of periods; an open line starts and ends with
    half a gap (so a line cut by a tile edge meets the next tile's line with one full gap)."""
    Lr = line.length
    if Lr < period * .5:
        return []
    k = max(1, int(round(Lr / period)))
    p = Lr / k
    dl = p * dash_frac
    gap = p - dl
    out = []
    for i in range(k):
        a = i * p + gap / 2
        seg = substring(line, a, a + dl)
        if seg.length > .05:
            out.append(list(seg.coords))
    return out


def _lines_d(lines, closed=False):
    return "".join(pd(l, closed) for l in lines if len(l) > 1)


def _seg_d(segs, sort=False):
    """Many short straight strokes as one path: M x y l dx dy m dx dy l dx dy ... (each move is
    relative to the end of the stroke before, in tenths of a unit, so nothing drifts)."""
    if sort:   # rows of 12 units, then left to right: short moves
        segs = sorted(segs, key=lambda s: (int(s[0][1] // 12), s[0][0] if int(s[0][1] // 12) % 2 == 0 else -s[0][0]))
    out = []
    cur = None
    for (x0, y0), (x1, y1) in segs:
        a = (round(x0 * 10), round(y0 * 10))
        b = (round(x1 * 10), round(y1 * 10))
        if a == b:
            continue
        if cur is None:
            out.append("M" + _join([n(a[0] / 10), n(a[1] / 10)]))
        else:
            out.append("m" + _join([n((a[0] - cur[0]) / 10), n((a[1] - cur[1]) / 10)]))
        out.append("l" + _join([n((b[0] - a[0]) / 10), n((b[1] - a[1]) / 10)]))
        cur = b
    return "".join(out)


# ================================================================ STYLE A: felt
def _felt_shadow(c, g, dx, dy, spread, op):
    sh = affinity.translate(g, dx, dy)
    if spread and bounds_size(g) > 14 * c.u:
        c.fill(sh.buffer(spread), SHADOW, op * .45, tol=.5 * c.u)
    c.fill(sh, SHADOW, op, tol=.45 * c.u)


def _fibres(c, g, col, key, per, length=(1.0, 2.1), cols=None):
    """Short fibre strokes on a felt surface: one per (per dp)^2."""
    u = c.u
    inner = g.buffer(-.8 * u)
    if inner.is_empty:
        return
    shapely.prepare(inner)
    x0, y0, x1, y1 = inner.bounds
    x0, y0, x1, y1 = max(x0, 0), max(y0, 0), min(x1, c.W), min(y1, c.H)
    area = c.clip(inner).area
    cnt = int(area / (per * u) ** 2)
    if cnt < 2:
        return
    rnd = c.rnd(key, "fib")
    cols = cols or (lt(col, .22), dk(col, .09))
    segs = {cc: [] for cc in cols}
    tries = 0
    while sum(len(v) for v in segs.values()) < cnt and tries < cnt * 4:
        tries += 1
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        a = rnd.uniform(0, math.pi)
        ln = rnd.uniform(*length) * u
        ex, ey = x + math.cos(a) * ln, y + math.sin(a) * ln
        if not (shapely.contains_xy(inner, x, y) and 0 < ex < c.W and 0 < ey < c.H and 0 < x < c.W and 0 < y < c.H):
            continue
        segs[cols[rnd.random() < .45 and len(cols) > 1 and 1 or 0]].append(((x, y), (ex, ey)))
    for cc, s in segs.items():
        if s:
            c.stroke(_seg_d(s, sort=True), cc, .42 * u)


def _hairs(c, g, col, key):
    """The fuzz: short strokes across the edge, mostly outwards."""
    u = c.u
    rnd = c.rnd(key, "hair")
    cols = (col, lt(col, .2))
    segs = {cc: [] for cc in cols}
    for pi, poly in enumerate(polys(g)):
        for ring in _oriented_rings(poly):
            P, _ = _ring_pts(ring, 2.2 * u)
            Nn = _normals(P)
            for (x, y), (nx, ny) in zip(P, Nn):
                a = rnd.uniform(-.95, .95)
                ln = rnd.uniform(.9, 2.0) * u
                dx = nx * math.cos(a) - ny * math.sin(a)
                dy = nx * math.sin(a) + ny * math.cos(a)
                sx, sy = x - nx * .45 * u, y - ny * .45 * u
                ex, ey = sx + dx * ln, sy + dy * ln
                if min(sx, ex) <= .3 or min(sy, ey) <= .3 or max(sx, ex) >= c.W - .3 or max(sy, ey) >= c.H - .3:
                    continue
                r = rnd.random()
                segs[cols[0 if r < .62 else 1]].append(((sx, sy), (ex, ey)))
    for cc, s in segs.items():
        if s:
            c.stroke(_seg_d(s), cc, .5 * u)


def _stitch(c, g, col, inset_dp, key, w_dp=1.6, dash=(4.8, 3.4)):
    """A running stitch inside the edge of g (explicit dashes, a shadow under the thread)."""
    u = c.u
    ins = g.buffer(-inset_dp * u, join_style="round").simplify(.15 * u)
    if ins.is_empty:
        return
    period = (dash[0] + dash[1]) * u
    frac = dash[0] / (dash[0] + dash[1])
    segs = []
    for poly in polys(ins):
        for ring in _oriented_rings(poly):
            ln = LineString(ring.coords)
            if c.box.contains(ln):
                segs += dashes(ln, period, frac, closed=True)
            else:
                cut = ln.intersection(c.box)
                parts = lines_of(cut)
                if len(parts) > 1:
                    parts = lines_of(linemerge(parts))
                for part in parts:
                    segs += dashes(part, period, frac)
    if not segs:
        return
    segs = [list(LineString(s).simplify(.12 * u).coords) for s in segs]
    d = _lines_d(segs)
    if w_dp > 1.4:
        sd = _lines_d([[(x + .3 * u, y + .65 * u) for x, y in s] for s in segs])
        c.stroke(sd, SHADOW, (w_dp + .45) * u, .24)
    c.stroke(d, col, w_dp * u)


def felt_piece(c, p, key, road=False):
    u = c.u
    g = p.geom
    if g.is_empty:
        return
    col = c.colour(p)
    size = bounds_size(g)
    if p.lift and not road:
        _felt_shadow(c, g, .35 * u * p.lift, 1.0 * u * p.lift, .55 * u, .17)
    fuzzy = p.fuzz and size > 4 * u
    wob = wobble(c, g, .42 * u, 2.0 * u, key) if fuzzy else g
    c.fill(wob, col, p.op)
    if p.shade and size > 6 * u:
        d1 = min(1.5 * u, size * .1)
        if size > 30 * u:
            c.fill(wob.difference(affinity.translate(wob, -2.6 * u, -2.6 * u)), dk(col, .07), tol=.35 * u)
        c.fill(wob.difference(affinity.translate(wob, -d1, -d1)), dk(col, .08), tol=.35 * u)
        c.fill(wob.difference(affinity.translate(wob, d1 * .7, d1 * .7)), lt(col, .3), tol=.35 * u)
    if size > 12 * u:
        _fibres(c, wob, col, key, 7.5)
    if fuzzy and size > 12 * u and (p.lift or road):
        _hairs(c, wob, col, key)
    if p.st:
        ins = p.inset if p.inset is not None else 3.4
        sw = 1.6 if size > 14 * u else 1.25
        dash = (4.8, 3.4) if size > 14 * u else (3.4, 2.6)
        _stitch(c, g, c.colour(p, p.st), ins, key, sw, dash)


def felt_line(c, p, key):
    u = c.u
    col = c.colour(p)
    pts = list(p.geom.coords)
    if p.dash:
        segs = dashes(p.geom, (p.dash[0] + p.dash[1]) * u, p.dash[0] / (p.dash[0] + p.dash[1]))
    else:
        segs = [pts]
    d = _lines_d(segs)
    sd = _lines_d([[(x + .3 * u, y + .6 * u) for x, y in s] for s in segs])
    c.stroke(sd, SHADOW, p.w + .5 * u, .18)
    c.stroke(d, col, p.w)


def felt_eye(c, p):
    x, y = p.geom.x, p.geom.y
    r = p.r
    lx, ly = p.look
    c.body.append(f'<ellipse cx="{n(x + lx)}" cy="{n(y + ly)}" rx="{n(r * .82)}" ry="{n(r)}" fill="{DARK}"/>')
    c.body.append(f'<circle cx="{n(x + lx + r * .26)}" cy="{n(y + ly - r * .36)}" r="{n(max(.5, r * .34))}" fill="#FFFFFF"/>')


def felt_button(c, p):
    x, y, r = p.geom.x, p.geom.y, p.r
    col = c.colour(p)
    c.body.append(f'<circle cx="{n(x)}" cy="{n(y + r * .14)}" r="{n(r)}" fill="{SHADOW}" opacity=".22"/>')
    c.body.append(f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(r)}" fill="{c.radial([(0, lt(col, .38)), (1, col)], .38, .32, .75)}"/>')
    c.body.append(f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(r * .72)}" fill="none" stroke="{dk(col, .2)}" stroke-width="{n(max(.3, r * .1))}" opacity=".6"/>')
    q = r * .26
    hs = [(x - q, y - q), (x + q, y - q), (x - q, y + q), (x + q, y + q)]
    c.stroke(pd([hs[0], hs[3]], False) + pd([hs[1], hs[2]], False), "#FFFFFF", max(.3, r * .16))
    for hx, hy in hs:
        c.body.append(f'<circle cx="{n(hx)}" cy="{n(hy)}" r="{n(max(.3, r * .1))}" fill="{dk(col, .35)}"/>')


def felt_ground(c, p):
    d = p.data
    base = d["base"]
    c.body.append(f'<path d="M0 0h{n(c.W)}v{n(c.H)}h-{n(c.W)}z" fill="{base}"/>')
    rnd = c.rnd("mottle")
    for i in range(int(c.W * c.H / 9000)):
        x, y = rnd.uniform(0, c.W), rnd.uniform(0, c.H)
        rx, ry = rnd.uniform(20, 46), rnd.uniform(14, 34)
        blob = wobble(c, E(x, y, rx, ry, rot=rnd.uniform(0, 180)), 3, 6, ("mot", i))
        c.fill(blob, lt(base, .07) if i % 2 else dk(base, .045), tol=.6)
    cols = d.get("fibres") or (lt(base, .2), dk(base, .09))
    _fibres(c, c.box.buffer(10), base, "ground", d.get("per", 8.5), (1.2, 2.6), cols)


def felt_road(c, p, key):
    d = p.data
    q = p.copy(col=d["fill"], st=d["stitch"], inset=d.get("inset", 3.4), lift=1)
    u = c.u
    _felt_shadow(c, p.geom, .4 * u, 1.3 * u, .7 * u, .2)
    felt_piece(c, q, key, road=True)


def felt_obj(c, p):
    if p.lift and not p.geom.is_empty:
        u = c.u
        _felt_shadow(c, p.geom, .5 * u * p.lift, 1.9 * u * p.lift, 1.1 * u, .13)


def render_a(c, pieces):
    for i, p in enumerate(pieces):
        if p.kind == "ground":
            felt_ground(c, p)
        elif p.kind == "road":
            felt_road(c, p, i)
        elif p.kind == "obj":
            felt_obj(c, p)
        elif p.kind == "fill":
            felt_piece(c, p, i)
        elif p.kind == "line":
            felt_line(c, p, i)
        elif p.kind == "eye":
            felt_eye(c, p)
        elif p.kind == "button":
            felt_button(c, p)


# ================================================================ STYLE B: pixels
def _shift(m, dy, dx):
    """m moved by (dx, dy) pixels; what moves in from outside is False."""
    out = np.zeros_like(m)
    H, W = m.shape
    ys = slice(max(0, dy), H + min(0, dy))
    yd = slice(max(0, -dy), H + min(0, -dy))
    xs = slice(max(0, dx), W + min(0, dx))
    xd = slice(max(0, -dx), W + min(0, -dx))
    out[ys, xs] = m[yd, xd]
    return out


def _dilate4(m):
    return m | _shift(m, 1, 0) | _shift(m, -1, 0) | _shift(m, 0, 1) | _shift(m, 0, -1)


class PixGrid:
    """The pixel grid of one file: pixel (i, j) covers units [i*px, (i+1)*px) with a margin of M
    pixels all round (so edge effects see what lies beyond the file)."""
    M = 2

    def __init__(self, c):
        self.c = c
        px = c.px
        self.w, self.h = int(round(c.W / px)), int(round(c.H / px))
        M = self.M
        gx = (np.arange(-M, self.w + M) + .5) * px
        gy = (np.arange(-M, self.h + M) + .5) * px
        self.X, self.Y = np.meshgrid(gx, gy)
        self.canvas = np.full(self.X.shape, "", dtype=object)

    def inside(self, g):
        if g.is_empty:
            return np.zeros(self.X.shape, bool)
        return shapely.contains_xy(g, self.X, self.Y)

    def cell(self, x, y):
        px = self.c.px
        return int(math.floor(y / px)) + self.M, int(math.floor(x / px)) + self.M

    def raster_fill(self, g):
        m = self.inside(g)
        if not m.any() and g.area > (self.c.px ** 2) * .12:
            pt = g.representative_point()
            j, i = self.cell(pt.x, pt.y)
            if 0 <= j < m.shape[0] and 0 <= i < m.shape[1]:
                m[j, i] = True
        return m

    def raster_line(self, line, w):
        px = self.c.px
        if w >= 1.25 * px:
            return self.raster_fill(line.buffer(w / 2, cap_style="round"))
        m = np.zeros(self.X.shape, bool)
        k = max(2, int(line.length / (px / 4)))
        for t in np.linspace(0, line.length, k):
            pt = line.interpolate(t)
            j, i = self.cell(pt.x, pt.y)
            if 0 <= j < m.shape[0] and 0 <= i < m.shape[1]:
                m[j, i] = True
        return m


def _pix_eye(grid, p):
    px = grid.c.px
    x, y = p.geom.x + p.look[0], p.geom.y + p.look[1]
    w = max(1, int(round(1.6 * p.r / px)))
    h = max(2 if 2 * p.r / px > 1.1 else 1, int(round(2.1 * p.r / px)))
    j, i = grid.cell(x - w * px / 2 + px / 2, y - h * px / 2 + px / 2)
    dark = np.zeros(grid.X.shape, bool)
    glint = np.zeros(grid.X.shape, bool)
    dark[j:j + h, i:i + w] = True
    if w >= 2 and h >= 2:
        glint[j, i + w - 1] = True
    return dark & ~glint, glint


def pixel_ground(grid, p):
    c = grid.c
    d = p.data
    cv = grid.canvas
    cv[:, :] = d["base"]
    H, W = cv.shape
    rnd = c.rnd("pg")
    for j in range(H):
        for i in range(W):
            r = rnd.random()
            acc = 0.0
            for col, chance in d.get("specks", ()):
                acc += chance
                if r < acc:
                    cv[j, i] = col
                    break
    for rows, pal, per in d.get("stamps", ()):
        sh, sw = len(rows), max(len(r) for r in rows)
        cnt = int(grid.w * grid.h * per / 1000)
        for k in range(cnt):
            ox = grid.M + rnd.randrange(1, max(2, grid.w - sw - 1))
            oy = grid.M + rnd.randrange(1, max(2, grid.h - sh - 1))
            pal2 = pal[k % len(pal)] if isinstance(pal, list) else pal
            for jj, row in enumerate(rows):
                for ii, ch in enumerate(row):
                    if ch in pal2:
                        cv[oy + jj, ox + ii] = pal2[ch]


def pixel_road(grid, p):
    d = p.data
    m = grid.inside(p.geom)
    cv = grid.canvas
    up, dn = _shift(m, 1, 0), _shift(m, -1, 0)
    lf, rt = _shift(m, 0, 1), _shift(m, 0, -1)
    border = _dilate4(m) & ~m
    cv[border] = d["border"]
    cv[m] = d["fill"]
    # sand specks: a fixed pattern on the pixel grid (the same on every tile)
    H, W = m.shape
    jj, ii = np.mgrid[0:H, 0:W]
    pat = ((ii * 7 + jj * 13) % 23 == 0) | ((ii * 11 + jj * 5) % 29 == 3)
    cv[m & pat] = d["speck"]
    light = m & (~dn | ~rt)
    shade = m & (~up | ~lf)
    cv[light] = d["light"]
    cv[shade] = d["shade"]


def pixel_object(grid, pieces, outline=True):
    c = grid.c
    OL = (c.world.pixel or {}).get("outline", "#2B2340") if c.world else "#2B2340"
    shape = grid.X.shape
    tc = np.full(shape, "", dtype=object)
    tid = np.full(shape, -1, int)
    own = {}
    for i, p in enumerate(pieces):
        col = c.colour(p)
        if p.kind == "eye":
            dark, glint = _pix_eye(grid, p)
            tc[dark] = OL
            tc[glint] = "#FFFFFF"
            tid[dark | glint] = i
            continue
        if p.kind == "line":
            m = grid.raster_line(p.geom, p.w)
        elif p.kind == "button":
            m = grid.raster_fill(p.geom.buffer(p.r))
        else:
            m = grid.raster_fill(p.geom)
        if not m.any():
            continue
        po = p.po
        if po is None:
            ys, xs = np.nonzero(m)
            po = p.kind == "fill" and p.lift > 0 and (np.ptp(ys) >= 3 and np.ptp(xs) >= 3)
        if po:
            ring = _dilate4(m) & ~m & (tid >= 0)
            tc[ring] = OL
            tid[ring] = -2 - i
        tc[m] = col
        tid[m] = i
        own[i] = m
        if p.kind == "button":
            j, ii = grid.cell(p.geom.x, p.geom.y)
            tc[j, ii] = dk(col, .35)
    # bevel: light top-left, dark bottom-right on each big lifted piece's own outline
    for i, m in own.items():
        p = pieces[i]
        if p.kind != "fill" or not p.shade or not p.lift:
            continue
        ys, xs = np.nonzero(m)
        if np.ptp(ys) < 4 or np.ptp(xs) < 4:
            continue
        mine = tid == i
        col = c.colour(p)
        lt_ = m & (~_shift(m, 1, 0) | ~_shift(m, 0, 1))
        dk_ = m & (~_shift(m, -1, 0) | ~_shift(m, 0, -1))
        tc[mine & lt_ & ~dk_] = mix(col, "#FFFFFF", .4)
        tc[mine & dk_ & ~lt_] = mix(col, OL, .28)
    body = tid != -1
    if outline:
        ring = _dilate4(body) & ~body
        grid.canvas[ring] = OL
    grid.canvas[body] = tc[body]


def _objects(pieces):
    """Split a piece list into objects: each obj marker, road or ground starts a new one."""
    groups, cur = [], None
    for p in pieces:
        if p.kind in ("road", "ground"):
            groups.append((p, []))
            cur = None
        elif p.kind == "obj":
            cur = (p, [])
            groups.append(cur)
        else:
            if cur is None:
                cur = (None, [])
                groups.append(cur)
            cur[1].append(p)
    return groups


def _rects(mask):
    """Greedy rectangles covering a boolean mask: [(x, y, w, h)]."""
    m = mask.copy()
    H, W = m.shape
    out = []
    for y in range(H):
        x = 0
        row = m[y]
        while x < W:
            if not row[x]:
                x += 1
                continue
            w = 1
            while x + w < W and row[x + w]:
                w += 1
            h = 1
            while y + h < H and m[y + h, x:x + w].all():
                h += 1
            m[y:y + h, x:x + w] = False
            out.append((x, y, w, h))
            x += w
    return out


def pixel_write(c, grid):
    M = grid.M
    cv = grid.canvas[M:M + grid.h, M:M + grid.w]
    filled = cv != ""
    if not filled.any():
        return
    cols, counts = np.unique(cv[filled].astype(str), return_counts=True)
    order = [cc for _, cc in sorted(zip(-counts, cols))]
    parts = []
    under = order[0]
    # underlay: everything that is drawn, in the most common colour (hides hairline seams between pixels)
    parts.append((under, _rects(filled)))
    for cc in order[1:]:
        parts.append((cc, _rects(cv == cc)))
    out = []
    for cc, rects in parts:
        d = "".join(f"M{x} {y}h{w}v{h}h-{w}z" for x, y, w, h in rects)
        out.append(f'<path d="{d}" fill="{cc}"/>')
    c.body.append(f'<g transform="scale({c.px:g})">{"".join(out)}</g>')


def render_b(c, pieces):
    grid = PixGrid(c)
    for head, ps in _objects(pieces):
        if head is not None and head.kind == "ground":
            pixel_ground(grid, head)
        elif head is not None and head.kind == "road":
            pixel_road(grid, head)
        else:
            ps = [p for p in ps if p.kind in ("fill", "line", "eye", "button")]
            if ps:
                pixel_object(grid, ps, outline=head is None or head.lift >= 0)
    pixel_write(c, grid)


# ================================================================ STYLE C: jelly and candy
def _jelly_shadow(c, g, dx, dy, op):
    shc = (c.world.jelly or {}).get("shadow", "#B04A7A") if c.world else "#B04A7A"
    sh = affinity.translate(g, dx, dy)
    c.fill(sh.buffer(1.1 * c.u), shc, op * .5, tol=.3 * c.u)
    c.fill(sh, shc, op * .7, tol=.3 * c.u)


def _gloss(c, g, size, op=.78):
    """A white crescent on the top-left inside of g, and a glint dot."""
    u = c.u
    inner = g.buffer(-max(.9 * u, size * .07))
    if inner.is_empty:
        return
    h = max(1.1 * u, min(size * .14, 6 * u))
    band = inner.difference(affinity.translate(inner, h, h))
    band = band.buffer(-h * .22).buffer(h * .22)
    # keep only the upper-left part of the band (the light comes from there)
    x0, y0, x1, y1 = g.bounds
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    keep = Polygon([(cx - 3 * size, cy + .25 * size), (cx + .25 * size, cy - 3 * size), (cx - 3 * size, cy - 3 * size)])
    band = band.intersection(keep)
    if not band.is_empty and band.area > .5 * u * u:
        c.fill(band, "#FFFFFF", op, tol=.15 * u)
    gx, gy = x0 + (x1 - x0) * .7, y0 + (y1 - y0) * .26
    if shapely.contains_xy(inner, gx, gy) and size > 7 * u:
        c.body.append(f'<circle cx="{n(gx)}" cy="{n(gy)}" r="{n(max(.6 * u, size * .045))}" fill="#FFFFFF"{_op(op)}/>')


def jelly_piece(c, p):
    g = p.geom
    if g.is_empty:
        return
    u = c.u
    col = c.colour(p)
    size = bounds_size(g)
    if p.lift and size > 3 * u:
        _jelly_shadow(c, g, .25 * u, .8 * u, .16)
    rim = dk(col, .2)
    if size > 5 * u:
        c.fill(g, rim, p.op, tol=.1 * u)
        body = g.buffer(-.75 * u)
        c.fill(body, c.radial([(0, lt(col, .5)), (.55, col), (1, dk(col, .1))]), p.op, tol=.1 * u)
        if p.gloss and size > 7 * u:
            _gloss(c, g, size)
        elif p.gloss:
            c.body.append(f'<circle cx="{n(g.centroid.x - size * .2)}" cy="{n(g.centroid.y - size * .2)}" r="{n(size * .14)}" fill="#FFFFFF" opacity=".75"/>')
    else:
        c.fill(g, col, p.op)


def jelly_line(c, p):
    col = c.colour(p)
    c.stroke(pd(list(p.geom.coords), False), col, p.w)


def jelly_eye(c, p):
    x, y = p.geom.x + p.look[0], p.geom.y + p.look[1]
    r = p.r
    c.body.append(f'<ellipse cx="{n(x)}" cy="{n(y)}" rx="{n(r * .86)}" ry="{n(r * 1.05)}" fill="#3A1F2A"/>')
    c.body.append(f'<circle cx="{n(x + r * .3)}" cy="{n(y - r * .4)}" r="{n(max(.5, r * .4))}" fill="#FFFFFF"/>')
    c.body.append(f'<circle cx="{n(x - r * .32)}" cy="{n(y + r * .42)}" r="{n(max(.3, r * .17))}" fill="#FFFFFF"/>')


def jelly_button(c, p):
    jelly_piece(c, p.copy(kind="fill", geom=p.geom.buffer(p.r), lift=0))


def jelly_ground(c, p):
    d = p.data
    fill = c.linear([(0, d["top"]), (1, d["bottom"])])
    c.body.append(f'<path d="M0 0h{n(c.W)}v{n(c.H)}h-{n(c.W)}z" fill="{fill}"/>')
    rnd = c.rnd("cg")
    # soft frosting swirls
    sw = d.get("swirl", lt(d["top"], .45))
    for i in range(int(c.W * c.H / 26000)):
        x, y = rnd.uniform(-20, c.W + 20), rnd.uniform(-20, c.H + 20)
        r = rnd.uniform(18, 40)
        a0 = rnd.uniform(0, 6.3)
        pts = [(x + math.cos(a0 + t) * r * (1 - t / 9), y + math.sin(a0 + t) * r * .55 * (1 - t / 9)) for t in np.linspace(0, 3.6, 16)]
        c.stroke(pd(pts, False), sw, 5 * c.u, .55)
    cols = d["sprinkles"]
    segs = {cc: [] for cc in cols}
    cnt = int(c.W * c.H * d.get("n", 14) / 10000)
    for k in range(cnt):
        x, y = rnd.uniform(3, c.W - 3), rnd.uniform(3, c.H - 3)
        a = rnd.uniform(0, math.pi)
        ln = 2.4 * c.u
        segs[cols[k % len(cols)]].append(((x - math.cos(a) * ln, y - math.sin(a) * ln), (x + math.cos(a) * ln, y + math.sin(a) * ln)))
    for cc, s in segs.items():
        c.stroke(_seg_d(s), cc, 2.2 * c.u)


def jelly_road(c, p, key):
    d = p.data
    u = c.u
    g = p.geom
    wid = 2 * HALF if c.kind == "tile" else d.get("width", 2 * HALF)
    sh = affinity.translate(g, 1.2 * u, 3.4 * u).difference(g)
    c.fill(affinity.translate(g, 1.4 * u, 4.2 * u).buffer(1.4 * u).difference(g), d["shadow"], .1, tol=.2)
    c.fill(sh, d["shadow"], .2, tol=.2)
    c.fill(g, d["rim"], .82, tol=.15)
    body = g.buffer(-.09 * wid)
    c.fill(body, d["body"], .8, tol=.15)
    # darker refraction along the lower-right inside edge
    c.fill(body.difference(affinity.translate(body, -.07 * wid, -.07 * wid)), d["rim"], .32, tol=.15)
    c.fill(g.buffer(-.3 * wid), d["glow"], .35, tol=.15)
    c.fill(g.buffer(-.38 * wid), d["glow"], .45, tol=.15)
    # the highlight streak: the part of an inset line that faces the top-left
    hl = g.buffer(-.22 * wid)
    segs = []
    for poly in polys(hl):
        for ring in _oriented_rings(poly):
            P, _ = _ring_pts(ring, .8)
            Nn = _normals(P)
            face = (Nn[:, 0] * -.7071 + Nn[:, 1] * -.7071) > .3
            inbox = (P[:, 0] > -.01) & (P[:, 0] < c.W + .01) & (P[:, 1] > -.01) & (P[:, 1] < c.H + .01)
            ok = face & inbox
            k = len(P)
            # walk the ring from a point that is not kept, collect runs
            start = int(np.argmin(ok)) if not ok.all() else 0
            run = []
            for t in range(k + 1):
                i = (start + t) % k
                if ok[i] and t < k:
                    run.append(tuple(P[i]))
                else:
                    if len(run) > 2:
                        segs.append(run)
                    run = []
    lines = []
    for s in segs:
        ln = LineString(s).intersection(c.box)
        lines += [list(l.coords) for l in lines_of(ln)]
    if lines:
        c.stroke(_lines_d(lines), "#FFFFFF", .085 * wid, .9)
        # little glints along the streak (at fixed distances, away from the file's edges)
        dots = []
        for l in lines:
            ls = LineString(l)
            t = 22.0
            while t < ls.length - 8:
                pt = ls.interpolate(t)
                if 8 < pt.x < c.W - 8 and 8 < pt.y < c.H - 8:
                    dots.append(pt)
                t += 47.0
        for pt in dots:
            c.body.append(f'<circle cx="{n(pt.x + .05 * wid)}" cy="{n(pt.y + .09 * wid)}" r="{n(.035 * wid)}" fill="#FFFFFF" opacity=".9"/>')


def jelly_obj(c, p):
    if p.lift and not p.geom.is_empty:
        _jelly_shadow(c, p.geom, .5 * c.u * p.lift, 2.2 * c.u * p.lift, .2)


def render_c(c, pieces):
    for i, p in enumerate(pieces):
        if p.kind == "ground":
            jelly_ground(c, p)
        elif p.kind == "road":
            jelly_road(c, p, i)
        elif p.kind == "obj":
            jelly_obj(c, p)
        elif p.kind == "fill":
            jelly_piece(c, p)
        elif p.kind == "line":
            jelly_line(c, p)
        elif p.kind == "eye":
            jelly_eye(c, p)
        elif p.kind == "button":
            jelly_button(c, p)


# ================================================================ render one file
def render(pieces, style, kind, name, world=None):
    c = Ctx(name, style, kind, world)
    pieces = [p for p in pieces if p.only is None or style in p.only]
    {"a": render_a, "b": render_b, "c": render_c}[style](c, pieces)
    return c.svg()


# ================================================================ the road tiles
def tile_geom(mask, ext=EXT):
    """The road of tile n (bitmask up 1, right 2, down 4, left 8), with its open sides extended
    `ext` units beyond the tile (see the module doc)."""
    a, b = ROAD0, ROAD1
    up, rt, dn, lf = bool(mask & 1), bool(mask & 2), bool(mask & 4), bool(mask & 8)
    arms = []
    if up:
        arms.append(sbox(a, -ext, b, 50))
    if rt:
        arms.append(sbox(50, a, 100 + ext, b))
    if dn:
        arms.append(sbox(a, 50, b, 100 + ext))
    if lf:
        arms.append(sbox(-ext, a, 50, b))
    k = up + rt + dn + lf
    if k == 1:
        return unary_union(arms + [Point(50, 50).buffer(HALF, quad_segs=24)])
    if k == 2 and not ((up and dn) or (lf and rt)):
        cx = 100.0 if rt else 0.0
        cy = 100.0 if dn else 0.0
        # a quarter ring of constant width round the inner corner (cx, cy)
        ring = Point(cx, cy).buffer(b, quad_segs=32).difference(Point(cx, cy).buffer(a, quad_segs=24))
        tile = sbox(0, 0, 100, 100)
        ext_arms = [g.difference(tile) for g in arms]
        return unary_union([ring.intersection(tile)] + ext_arms).buffer(0)
    g = unary_union(arms + [sbox(a, a, b, b)])
    r = a   # inner corners: radius 19 (round the corner of the tile)
    return g.buffer(r, join_style="round", quad_segs=16).buffer(-r, join_style="round", quad_segs=16)


def road_piece(world, style, geom):
    return Piece("road", geom, "#000000", data=world.road[style])


def ground_piece(world, style):
    return Piece("ground", sbox(0, 0, 1, 1), "#000000", data=world.ground[style])


def sticker_disc(world, style):
    """The round sticker every sticker picture is laid on (200 x 200)."""
    sd = world.sticker or {}
    return OBJ([F(E(100, 100, 92), sd.get("fill", WHITE), st=sd.get("stitch", "#E3CDBE"), inset=4.2,
                  cols={"b": sd.get("fill_b", "#FFFFFF"), "c": sd.get("fill_c", "#FFF6FA")})], shadow=1)


# ================================================================ a world
ROLES = ("hero", "home", "family", "star", "key", "gate", "card")


class World:
    """All the art of one world in three styles (see the module doc for the fields)."""

    def __init__(self, wid, zh, road, ground, hero, home, family, star, key, gate, deco, stickers, card,
                 pixel=None, jelly=None, bits=None, sticker=None):
        assert len(deco) == 6, "a world has deco_1..deco_6"
        assert len(stickers) == 10, "a world has sticker_01..sticker_10"
        for st in STYLES:
            assert st in road and st in ground, f"road and ground need styles a, b, c ({st} missing)"
        need = {"a": {"fill", "stitch"}, "b": {"fill", "speck", "shade", "light", "border"},
                "c": {"body", "rim", "glow", "shadow"}}
        for st, keys in need.items():
            miss = keys - set(road[st])
            assert not miss, f"road[{st!r}] needs {sorted(miss)}"
        self.wid, self.zh = wid, zh
        self.road, self.ground, self.pixel, self.jelly, self.bits, self.sticker = road, ground, pixel, jelly, bits, sticker
        self.fns = dict(hero=hero, home=home, family=family, star=star, key=key, gate=gate, card=card)
        self.deco, self.stickers = deco, stickers

    def files(self, style):
        """{file name: (kind, pieces)} for one style."""
        out = {}
        bg = [ground_piece(self, style)] + (self.bits(style) if self.bits else [])
        out["bg"] = ("bg", bg)
        for m in range(1, 16):
            out[f"tile_{m}"] = ("tile", [road_piece(self, style, tile_geom(m))])
        for role in ("hero", "home", "star", "key", "gate"):
            out[role] = ("item", self.fns[role](style))
        out["family"] = ("family", self.fns["family"](style))
        for i, fn in enumerate(self.deco, 1):
            out[f"deco_{i}"] = ("item", fn(style))
        for i, fn in enumerate(self.stickers, 1):
            out[f"sticker_{i:02d}"] = ("sticker", sticker_disc(self, style) + fn(style))
        out["card"] = ("card", self.fns["card"](style))
        return out

    def build(self, styles=STYLES, verbose=True):
        sizes = {}
        for st in styles:
            for name, (kind, pieces) in self.files(st).items():
                text = render(pieces, st, kind, f"{self.wid}/{name}", self)
                path = ART / st / self.wid / f"{name}.svg"
                sizes[(st, name)] = write_svg(path, text, KIND[kind])
        check_world(self.wid)
        if verbose:
            for st in styles:
                ks = {nm: kb for (s, nm), kb in sizes.items() if s == st}
                big = sorted(ks.items(), key=lambda t: -t[1])[:4]
                tiles = [kb for nm, kb in ks.items() if nm.startswith("tile_")]
                print(f"{self.wid} {st}: {len(ks)} files, {sum(ks.values()):.0f} KB; tiles up to {max(tiles):.1f} KB; "
                      f"biggest " + ", ".join(f"{nm} {kb:.0f}" for nm, kb in big))
        return sizes


# ================================================================ checks (flutter_svg rules + docs/art.md)
FORBIDDEN = ("<filter", "<mask", "<style", "style=", "class=", "<text", "<image", "<foreignObject", "<pattern",
             "mix-blend-mode", "mask=", "filter=", "vector-effect", "<symbol", "<marker", "@import")
_TOK = re.compile(r"[MmLlHhVvCcSsQqTtAaZz]|[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?")
_NARGS = {"M": 2, "L": 2, "H": 1, "V": 1, "C": 6, "S": 4, "Q": 4, "T": 2, "A": 7, "Z": 0}
DRAWN = {"path", "ellipse", "circle", "rect", "polygon", "polyline", "line", "use"}
MAX_KB = 70
MAX_USE = 800


def check_path(d):
    """Raise ValueError unless d is path data flutter_svg reads (it drops the WHOLE picture over one
    bad path, where Chromium only skips that path)."""
    toks = _TOK.findall(d)
    if not toks or toks[0] not in "Mm":
        raise ValueError(f"path does not start with M: {d[:40]!r}")
    if len("".join(toks)) != len(re.sub(r"[\s,]", "", d)):
        raise ValueError(f"stray characters in path: {d[:60]!r}")
    i = 0
    while i < len(toks):
        cmd = toks[i]
        if not cmd.isalpha():
            raise ValueError(f"numbers without a command: {d[:60]!r}")
        i += 1
        k = _NARGS[cmd.upper()]
        j = i
        while j < len(toks) and not toks[j].isalpha():
            j += 1
        cnt = j - i
        if (k == 0 and cnt) or (k and (cnt == 0 or cnt % k)):
            raise ValueError(f"command {cmd} has {cnt} numbers: {d[:60]!r}")
        i = j


def check_svg(name, text, size=None):
    """flutter_svg rules: forbidden features, explicit paint on every drawn element, size, <use>
    count, parseable XML and path data, the viewBox (0 0 w h). Returns KB; SystemExit on a problem."""
    bad = [f for f in FORBIDDEN if f in text]
    if bad:
        raise SystemExit(f"{name}: uses {bad} (flutter_svg cannot draw these)")
    if text.count("<use") >= MAX_USE:
        raise SystemExit(f"{name}: {text.count('<use')} <use> (keep under {MAX_USE})")
    kb = len(text.encode()) / 1024
    if kb > MAX_KB:
        raise SystemExit(f"{name}: {kb:.0f} KB (keep under {MAX_KB} KB)")
    if not text.rstrip().endswith("</svg>"):
        raise SystemExit(f"{name}: cut short")
    root = ET.fromstring(text)
    ns = "{http://www.w3.org/2000/svg}"
    vb = [float(v) for v in root.get("viewBox").split()]
    if vb[0] or vb[1]:
        raise SystemExit(f"{name}: viewBox must start at 0 0")
    if size and (abs(vb[2] - size["w"]) > .01 or abs(vb[3] - size["h"]) > .01):
        raise SystemExit(f"{name}: viewBox {vb[2]:g} x {vb[3]:g}, docs/art.md says {size['w']} x {size['h']}")
    defs = root.find(f"{ns}defs")
    in_defs = set()
    if defs is not None:
        for el in defs.iter():
            in_defs.add(id(el))
    for el in root.iter():
        tag = el.tag.replace(ns, "")
        d = el.get("d")
        if d is not None:
            try:
                check_path(d)
            except ValueError as e:
                raise SystemExit(f"{name}: {e}")
        if tag in DRAWN and id(el) not in in_defs and el.get("fill") is None and el.get("stroke") is None:
            raise SystemExit(f"{name}: a <{tag}> without fill/stroke")
        for a in ("fill", "stroke"):
            v = el.get(a)
            if v and v.startswith("url(#") and root.find(f".//*[@id='{v[5:-1]}']") is None:
                raise SystemExit(f"{name}: {a} points to a missing {v}")
    return kb


def write_svg(path, text, size=None):
    path = pathlib.Path(path)
    kb = check_svg(str(path.relative_to(ROOT)) if ROOT in path.parents else str(path), text, size)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return kb


TUDOU_POSES = ("wave", "point", "cheer", "sleep", "peek")


def world_files():
    """docs/art.md: every file of a world, with its kind."""
    out = {"bg": "bg", "hero": "item", "home": "item", "family": "family", "star": "item", "key": "item",
           "gate": "item", "card": "card"}
    for m in range(1, 16):
        out[f"tile_{m}"] = "tile"
    for i in range(1, 7):
        out[f"deco_{i}"] = "item"
    for i in range(1, 11):
        out[f"sticker_{i:02d}"] = "sticker"
    return out


def check_world(wid):
    """Every file of docs/art.md exists in a, b and c with the right viewBox and passes check_svg."""
    for st in STYLES:
        for name, kind in world_files().items():
            p = ART / st / wid / f"{name}.svg"
            if not p.exists():
                raise SystemExit(f"missing {p.relative_to(ROOT)}")
            check_svg(str(p.relative_to(ROOT)), p.read_text(), KIND[kind])
        extra = {p.stem for p in (ART / st / wid).glob("*.svg")} - set(world_files())
        if extra:
            raise SystemExit(f"{st}/{wid}: files docs/art.md does not know: {sorted(extra)}")


def check_tudou():
    for st in STYLES:
        for pose in TUDOU_POSES:
            p = ART / st / f"tudou_{pose}.svg"
            if not p.exists():
                raise SystemExit(f"missing {p.relative_to(ROOT)}")
            check_svg(str(p.relative_to(ROOT)), p.read_text(), KIND["tudou"])
