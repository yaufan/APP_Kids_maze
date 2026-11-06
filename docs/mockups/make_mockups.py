"""Design-stage sketches for the maze game 「迷宮小冒險」 (working name, not final).

    python3 make_mockups.py          # writes docs/mockups/*.png (needs Node.js + Playwright, and shapely)
    python3 make_mockups.py 3        # only one page: 0 = style page, 1..7 = a screen, c = contact sheet
    python3 make_mockups.py items    # one sheet of all the felt characters (written to the temp folder)

Every picture is drawn here as SVG by code (no outside pictures, no emoji). render.js turns each page
into a PNG with Playwright's Chromium. shapely (pip install shapely) does the path outlines and the
stitch lines. The font is jf open-huninn from a sibling app's checkout.

    0_畫風選擇.png   the same small garden maze (the bee at the start, a flower at the goal, a wide
                     winding path with one fork and a short dead end, two stars on the path) in three
                     styles: A 羊毛氈布書風, B 像素小遊戲風, C 果凍糖果風
    1_首頁.png       home: the title, 土豆 the mole popping out of his hole, six world cards, 貼紙冊
    2_跟著路走.png   2-3 years: one wide winding path with no forks, a finger drags the bee to the flower house
    3_走迷宮.png     3-5 years: a 5 x 5 sea maze, the fish's bubble trail, 土豆 points the way (hint)
    4_送東西.png     4-5 years: city roads, the bus has the key (task strip: key, gate, home); the gate opens
    5_到家了.png     reward: the bee hugs its family, confetti, a sticker flies into the sticker book
    6_貼紙冊.png     the sticker book: felt stickers and empty slots, one tab per world
    7_家長模式.png   parents' settings: age, play time, hints, sound, read aloud, English, progress
    contact_sheet.png  screens 1-7 in two rows

Style A 「羊毛氈布書風」 (used for screens 1-7) looks like a toddler's felt quiet book. Every felt piece
goes through one SVG filter (felt_f): its edge is pushed about by noise so it comes out fuzzy, its
surface is lit from the top left through a blurred copy of its own shape plus fibre noise (so a piece
looks thick and a little puffy, with a matt woolly texture), and it throws a soft shadow on what is
under it. Most pieces have a running stitch (a dashed thread) sewn just inside their edge; shapely
works out that inset line. Faces are embroidered: satin-stitch eyes with a white glint, backstitch
smiles, felt cheeks. Pages sit on cotton fabric (gingham or dots with a woven texture).
The drawing scale K (screen pixels per drawing unit) is tracked while placing characters so the fuzz,
the shadows and the stitches come out the same size on screen whatever the character's size.
Style B 「像素小遊戲風」: the same maze laid on a grid of big 5 px pixels, path and grass as clean tiles,
pixel sprites, a small bright palette. Style C 「果凍糖果風」: the same maze as a glossy, see-through
jelly tube with highlights on a frosting floor with sprinkles; gummy bee, lollipop flower, candy stars.
"""
import hashlib
import math
import pathlib
import random
import subprocess
import sys
import tempfile

from shapely.geometry import LineString, Polygon
from shapely.geometry import box as sbox
from shapely.ops import unary_union

HERE = pathlib.Path(__file__).resolve().parent
FONT = None
for _c in ("app_kids_falsecharge", "app_kids_brainstorming", "app_kids_paint_for_learning_writing", "app_kids_card_game", "app_kids_cook"):
    _p = HERE.parents[2] / _c / "app" / "assets" / "fonts" / "jf-openhuninn-2.1.ttf"
    if _p.exists():
        FONT = _p
        break
SCRATCH = pathlib.Path("/dev/shm") if pathlib.Path("/dev/shm").is_dir() else pathlib.Path(tempfile.gettempdir())
W, H = 390, 844

# ---------------------------------------------------------------- colours (style A felt)
INK = "#4D3B34"        # words: warm cocoa
SOFT = "#A08F84"
YEL, YEL_T = "#FFD54F", "#C9951C"
ORA = "#FFA84C"
CORAL = "#FF8A73"
PINK, PINK_T = "#FF9EC1", "#D9668F"
RED = "#F2665C"
LILAC = "#B7A3F0"
SKY = "#8FD3F4"
BLUE = "#5BA8E8"
NAVY = "#3E4C82"
MINT = "#8FE0C4"
GRN, GRN_T = "#8DCF6E", "#5E9E45"
DGRN = "#5DAA5A"
BRN = "#9A6B4F"
COCOA = "#6B4A3B"
CREAM = "#FFF0CF"
WHITE = "#FFFDF8"
GREY = "#B9BFCB"
DARK = "#3B2C29"       # embroidery thread for eyes and smiles
CHEEK = "#FF9DAE"


# ---------------------------------------------------------------- defs registry
class Defs:
    def __init__(self):
        self.d = {}

    def add(self, key, svg):
        self.d.setdefault(key, svg)
        return key

    def svg(self):
        return "<defs>" + "".join(self.d.values()) + "</defs>"


D = Defs()


def _h(*parts):
    return hashlib.md5("|".join(map(str, parts)).encode()).hexdigest()[:10]


def _stops(stops):
    return "".join(f'<stop offset="{s[0]}" stop-color="{s[1]}"' + (f' stop-opacity="{s[2]}"' if len(s) > 2 else "") + "/>" for s in stops)


def lg(stops, x1=0, y1=0, x2=0, y2=1, user=False):
    k = "lg" + _h(stops, x1, y1, x2, y2, user)
    u = ' gradientUnits="userSpaceOnUse"' if user else ""
    D.add(k, f'<linearGradient id="{k}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"{u}>{_stops(stops)}</linearGradient>')
    return f"url(#{k})"


def rg(stops, cx=.5, cy=.5, r=.5, user=False, fx=None, fy=None):
    k = "rg" + _h(stops, cx, cy, r, user, fx, fy)
    u = ' gradientUnits="userSpaceOnUse"' if user else ""
    f = (f' fx="{fx}" fy="{fy}"' if fx is not None else "")
    D.add(k, f'<radialGradient id="{k}" cx="{cx}" cy="{cy}" r="{r}"{f}{u}>{_stops(stops)}</radialGradient>')
    return f"url(#{k})"


def clip(d):
    k = "cp" + _h(d)
    D.add(k, f'<clipPath id="{k}"><path d="{d}"/></clipPath>')
    return f"url(#{k})"


def blur(sd):
    k = "bl" + str(sd).replace(".", "_")
    D.add(k, f'<filter id="{k}" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="{sd}"/></filter>')
    return f"url(#{k})"


# ================================================================ GEOMETRY
def ellp(cx, cy, rx, ry=None, n=48, rot=0.0):
    ry = rx if ry is None else ry
    a = math.radians(rot)
    ca, sa = math.cos(a), math.sin(a)
    out = []
    for i in range(n):
        t = 2 * math.pi * i / n
        x, y = rx * math.cos(t), ry * math.sin(t)
        out.append((cx + x * ca - y * sa, cy + x * sa + y * ca))
    return out


def crs(ctrl, n=10, closed=True):
    """Catmull-Rom spline through the control points, as a dense point list."""
    m = len(ctrl)
    out = []
    segs = m if closed else m - 1
    for i in range(segs):
        p0 = ctrl[(i - 1) % m] if closed else ctrl[max(i - 1, 0)]
        p1, p2 = ctrl[i], ctrl[(i + 1) % m]
        p3 = ctrl[(i + 2) % m] if closed else ctrl[min(i + 2, m - 1)]
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            out.append(tuple(.5 * (2 * p1[j] + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                                   + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in (0, 1)))
    if not closed:
        out.append(tuple(ctrl[-1]))
    return out


def rrect(x, y, w, h, r, n=8):
    r = min(r, w / 2, h / 2)
    out = []
    for cx, cy, a0 in ((x + w - r, y + r, -90), (x + w - r, y + h - r, 0), (x + r, y + h - r, 90), (x + r, y + r, 180)):
        for k in range(n + 1):
            a = math.radians(a0 + 90 * k / n)
            out.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return out


def star_pts(R, r, cx=0.0, cy=0.0, n=5, rot=-90.0):
    out = []
    for i in range(2 * n):
        a = math.radians(rot + 180 * i / n)
        rr_ = R if i % 2 == 0 else r
        out.append((cx + rr_ * math.cos(a), cy + rr_ * math.sin(a)))
    return out


def soft(g, r):
    """Round the corners of a shape (convex ones, then concave ones)."""
    return g.buffer(-r, join_style=1).buffer(2 * r, join_style=1).buffer(-r, join_style=1)


def star_g(R, cx=0.0, cy=0.0, rot=-90.0, ratio=.5):
    return soft(Polygon(star_pts(R, R * ratio, cx, cy, 5, rot)), R * .12)


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


def rline(pts, r, n=10):
    """A polyline through pts with each corner rounded (radius r): dense points."""
    out = [pts[0]]
    for i in range(1, len(pts) - 1):
        (x0, y0), (x1, y1), (x2, y2) = pts[i - 1], pts[i], pts[i + 1]
        l1, l2 = math.hypot(x1 - x0, y1 - y0), math.hypot(x2 - x1, y2 - y1)
        rr_ = min(r, l1 * (.5 if i > 1 else .9), l2 * (.5 if i < len(pts) - 2 else .9))
        ax, ay = x1 - (x1 - x0) / l1 * rr_, y1 - (y1 - y0) / l1 * rr_
        bx, by = x1 + (x2 - x1) / l2 * rr_, y1 + (y2 - y1) / l2 * rr_
        for k in range(n + 1):
            t = k / n
            out.append(((1 - t) ** 2 * ax + 2 * (1 - t) * t * x1 + t * t * bx, (1 - t) ** 2 * ay + 2 * (1 - t) * t * y1 + t * t * by))
    out.append(pts[-1])
    return out


def along(line, t):
    """The point at fraction t of a dense point list, and the direction there (degrees)."""
    ls = LineString(line)
    p = ls.interpolate(t, normalized=True)
    q = ls.interpolate(min(1.0, t + .01), normalized=True)
    p0 = ls.interpolate(max(0.0, t - .01), normalized=True)
    return (p.x, p.y), math.degrees(math.atan2(q.y - p0.y, q.x - p0.x))


def part_line(line, t0, t1, step=2.0):
    ls = LineString(line)
    L = ls.length
    n = max(2, int(L * (t1 - t0) / step))
    return [(ls.interpolate(L * (t0 + (t1 - t0) * i / n)).x, ls.interpolate(L * (t0 + (t1 - t0) * i / n)).y) for i in range(n + 1)]


def G(x):
    """Anything shape-like (a point list or a shapely geometry) as a shapely geometry."""
    if isinstance(x, (list, tuple)):
        return Polygon(x).buffer(0)
    return x


def dpts(pts, closed=True):
    return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + ("Z" if closed else "")


def dgeom(g):
    polys = list(g.geoms) if hasattr(g, "geoms") else [g]
    out = []
    for p in polys:
        if p.is_empty or p.geom_type != "Polygon":
            continue
        for ring in (p.exterior, *p.interiors):
            out.append(dpts(list(ring.coords)[:-1]))
    return "".join(out)


def bounds(g):
    return G(g).bounds


# ================================================================ STYLE A: FELT KIT
K = 1.0   # screen pixels per drawing unit of whatever is being drawn now (place() keeps it right)


def place(x, y, s, fn, *a, rot=0.0, **kw):
    """Draw fn(*a, **kw) moved to (x, y) and scaled by s; K follows so the felt looks the same size."""
    global K
    old = K
    K = old * s
    try:
        inner = fn(*a, **kw)
    finally:
        K = old
    r = f" rotate({rot:.1f})" if rot else ""
    return f'<g transform="translate({x:.1f} {y:.1f}){r} scale({s:.4f})">{inner}</g>'


def felt_f(sh=1, m=.2):
    """The felt filter at the current scale. sh: 0 = no shadow, 1 = sewn on, 2 = lifted (cards), 3 = big page."""
    k = round(K, 3)
    key = "ft" + _h(k, sh, m)
    dy, sd, op = {0: (0, 0, 0), 1: (1.7, 1.3, .42), 2: (3.4, 3.2, .34), 3: (5, 6, .26)}[sh]
    shadow = ""
    merge = '<feMergeNode in="top"/>'
    if sh:
        shadow = (f'<feGaussianBlur in="src" stdDeviation="{sd / k:.3f}" result="sb"/>'
                  f'<feOffset in="sb" dx="{dy * .3 / k:.3f}" dy="{dy / k:.3f}" result="so"/>'
                  f'<feColorMatrix in="so" type="matrix" values="0 0 0 0 0.17  0 0 0 0 0.11  0 0 0 0 0.07  0 0 0 {op} 0" result="sh"/>')
        merge = '<feMergeNode in="sh"/>' + merge
    D.add(key, f'<filter id="{key}" x="{-m}" y="{-m}" width="{1 + 2 * m}" height="{1 + 2.4 * m}" color-interpolation-filters="sRGB">'
               f'<feTurbulence type="fractalNoise" baseFrequency="{.85 * k:.4f}" numOctaves="3" seed="4" result="n"/>'
               f'<feTurbulence type="turbulence" baseFrequency="{1.6 * k:.4f}" numOctaves="2" seed="11" result="fib"/>'
               f'<feDisplacementMap in="SourceGraphic" in2="n" scale="{2.9 / k:.3f}" xChannelSelector="R" yChannelSelector="G" result="src"/>'
               f'<feGaussianBlur in="src" stdDeviation="{2.6 / k:.3f}" result="b"/>'
               f'<feColorMatrix in="fib" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0.55 0 0 0 0" result="na"/>'
               f'<feComposite in="b" in2="na" operator="arithmetic" k2="1" k3="0.34" result="h"/>'
               f'<feDiffuseLighting in="h" surfaceScale="{3.2 / k:.3f}" diffuseConstant="1.1" lighting-color="#ffffff" result="l">'
               f'<feDistantLight azimuth="235" elevation="56"/></feDiffuseLighting>'
               f'<feComposite in="src" in2="l" operator="arithmetic" k1="0.7" k2="0.42" result="lit"/>'
               f'<feColorMatrix in="n" type="matrix" values="1 0 0 0 0  1 0 0 0 0  1 0 0 0 0  0 0 0 0 1" result="ng"/>'
               f'<feComposite in="lit" in2="ng" operator="arithmetic" k1="0.42" k2="0.81" result="mot"/>'
               f'<feComposite in="mot" in2="src" operator="in" result="top"/>'
               f'{shadow}<feMerge>{merge}</feMerge></filter>')
    return f"url(#{key})"


def _margin(g):
    x0, y0, x1, y1 = g.bounds
    s = max(1e-3, min(x1 - x0, y1 - y0) * K)
    need = 9 / s
    for m in (.04, .08, .15, .3, .6, 1.2):
        if need <= m:
            return m
    return 2.0


def stitch(d, col, w=1.7, dash=(5.2, 3.6), op=1.0):
    """A running stitch along the path d (screen sizes divided by K)."""
    k = K
    da = f"{dash[0] / k:.2f} {dash[1] / k:.2f}"
    return (f'<path d="{d}" fill="none" stroke="#2A1C14" stroke-opacity="{.26 * op:.2f}" stroke-width="{(w + .5) / k:.2f}" stroke-dasharray="{da}" '
            f'stroke-linecap="round" stroke-linejoin="round" transform="translate({.35 / k:.2f} {.75 / k:.2f})"/>'
            f'<path d="{d}" fill="none" stroke="{col}" stroke-opacity="{op}" stroke-width="{w / k:.2f}" stroke-dasharray="{da}" '
            f'stroke-linecap="round" stroke-linejoin="round"/>')


def thread(d, col=DARK, w=1.9, dash=None):
    """An embroidered line (solid, or a backstitch when dash is given)."""
    k = K
    da = f' stroke-dasharray="{dash[0] / k:.2f} {dash[1] / k:.2f}"' if dash else ""
    return (f'<path d="{d}" fill="none" stroke="#2A1C14" stroke-opacity=".18" stroke-width="{(w + .6) / k:.2f}" stroke-linecap="round" '
            f'stroke-linejoin="round"{da} transform="translate({.3 / k:.2f} {.6 / k:.2f})"/>'
            f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{w / k:.2f}" stroke-linecap="round" stroke-linejoin="round"{da}/>')


def felt(shape, fill, st=None, inset=None, sh=1, dash=(5.2, 3.6), sw=1.7, extra=""):
    """One felt piece. st: the colour of the running stitch sewn just inside the edge (None = no stitch)."""
    g = G(shape)
    if g.is_empty:
        return ""
    o = f'<path d="{dgeom(g.simplify(.08 / K))}" fill="{fill}" fill-rule="evenodd" filter="{felt_f(sh, _margin(g))}"{extra}/>'
    if st:
        ins = (3.6 if inset is None else inset) / K
        gi = g.buffer(-ins, join_style=1)
        if not gi.is_empty:
            o += stitch(dgeom(gi.simplify(.1 / K)), st, sw, dash)
    return o


def eye(cx, cy, r, glint=True):
    o = f'<ellipse cx="{cx:.2f}" cy="{cy:.2f}" rx="{r * .82:.2f}" ry="{r:.2f}" fill="{DARK}"/>'
    if glint:
        o += f'<circle cx="{cx + r * .26:.2f}" cy="{cy - r * .36:.2f}" r="{r * .34:.2f}" fill="#FFFFFF"/>'
    return o


def happy_eye(cx, cy, r):
    return thread(f"M{cx - r:.2f},{cy + r * .35:.2f} Q{cx:.2f},{cy - r * 1.1:.2f} {cx + r:.2f},{cy + r * .35:.2f}", DARK, 2.2)


def smile(cx, cy, w, open_=False):
    if open_:
        d = f"M{cx - w:.2f},{cy:.2f} Q{cx:.2f},{cy + w * 1.5:.2f} {cx + w:.2f},{cy:.2f}Z"
        return f'<path d="{d}" fill="#B5414F"/>' + thread(d, DARK, 1.5)
    return thread(f"M{cx - w:.2f},{cy:.2f} Q{cx:.2f},{cy + w * .95:.2f} {cx + w:.2f},{cy:.2f}", DARK, 1.8)


def cheeks(cx, cy, dx, r):
    return felt(ellp(cx - dx, cy, r, r * .82), CHEEK, sh=0) + felt(ellp(cx + dx, cy, r, r * .82), CHEEK, sh=0)


def button(cx, cy, r, col, holes=4, thr="#FFFFFF"):
    """A sewing button (plastic, a little glossy), sewn on with a cross of thread."""
    o = (f'<circle cx="{cx:.2f}" cy="{cy + r * .12:.2f}" r="{r:.2f}" fill="#2A1C14" opacity=".22"/>'
         f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" fill="{rg([(0, mixc(col, "#FFFFFF", .35)), (1, col)], .38, .32, .75)}"/>'
         f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r * .72:.2f}" fill="none" stroke="{mixc(col, "#000000", .18)}" stroke-width="{r * .1:.2f}" opacity=".6"/>')
    hs = [(-1, -1), (1, -1), (-1, 1), (1, 1)] if holes == 4 else [(-1, 0), (1, 0)]
    q = r * .26
    pts = [(cx + a * q, cy + b * q) for a, b in hs]
    if holes == 4:
        o += f'<path d="M{pts[0][0]:.2f},{pts[0][1]:.2f} L{pts[3][0]:.2f},{pts[3][1]:.2f} M{pts[1][0]:.2f},{pts[1][1]:.2f} L{pts[2][0]:.2f},{pts[2][1]:.2f}" stroke="{thr}" stroke-width="{r * .16:.2f}" stroke-linecap="round"/>'
    else:
        o += f'<path d="M{pts[0][0]:.2f},{pts[0][1]:.2f} L{pts[1][0]:.2f},{pts[1][1]:.2f}" stroke="{thr}" stroke-width="{r * .16:.2f}" stroke-linecap="round"/>'
    o += "".join(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r * .1:.2f}" fill="{mixc(col, "#000000", .35)}"/>' for x, y in pts)
    o += f'<path d="M{cx - r * .55:.2f},{cy - r * .35:.2f} A{r * .65:.2f},{r * .65:.2f} 0 0 1 {cx - r * .1:.2f},{cy - r * .66:.2f}" stroke="#FFFFFF" stroke-width="{r * .13:.2f}" fill="none" stroke-linecap="round" opacity=".7"/>'
    return o


def _rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def mixc(a, b, t):
    ra, rb = _rgb(a), _rgb(b)
    return "#" + "".join(f"{round(ra[i] + (rb[i] - ra[i]) * t):02X}" for i in range(3))


def knot(cx, cy, r, col=DARK):
    """A French knot / felt ball."""
    return felt(ellp(cx, cy, r), col, sh=1)


# ---------------------------------------------------------------- fabric backgrounds
def linen(x, y, w, h, op=.5, seed=2):
    k = "ln" + _h(x, y, w, h, seed)
    D.add(k, f'<filter id="{k}" filterUnits="userSpaceOnUse" x="{x}" y="{y}" width="{w}" height="{h}">'
             f'<feTurbulence type="fractalNoise" baseFrequency="0.02 0.85" numOctaves="2" seed="{seed}" result="a"/>'
             f'<feTurbulence type="fractalNoise" baseFrequency="0.85 0.02" numOctaves="2" seed="{seed + 3}" result="b"/>'
             f'<feComposite in="a" in2="b" operator="arithmetic" k2="0.5" k3="0.5"/>'
             f'<feColorMatrix type="matrix" values="0 0 0 0 0.25  0 0 0 0 0.2  0 0 0 0 0.16  -3 0 0 0 1.62"/></filter>')
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#000" filter="url(#{k})" opacity="{op}"/>'


def gingham(x, y, w, h, base, col, size=26, op=.38, lop=.26):
    k = "gh" + _h(base, col, size, op)
    s2 = size / 2
    D.add(k, f'<pattern id="{k}" width="{size}" height="{size}" patternUnits="userSpaceOnUse" x="{x}" y="{y}">'
             f'<rect width="{size}" height="{size}" fill="{base}"/><rect width="{s2}" height="{size}" fill="{col}" opacity="{op}"/>'
             f'<rect width="{size}" height="{s2}" fill="{col}" opacity="{op}"/></pattern>')
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#{k})"/>' + linen(x, y, w, h, lop)


def dotcloth(x, y, w, h, base, col, size=30, r=4.2, lop=.26):
    k = "dc" + _h(base, col, size, r)
    D.add(k, f'<pattern id="{k}" width="{size}" height="{size}" patternUnits="userSpaceOnUse" x="{x}" y="{y}">'
             f'<rect width="{size}" height="{size}" fill="{base}"/><circle cx="{size / 4}" cy="{size / 4}" r="{r}" fill="{col}"/>'
             f'<circle cx="{size * .75}" cy="{size * .75}" r="{r}" fill="{col}"/></pattern>')
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#{k})"/>' + linen(x, y, w, h, lop)


# ================================================================ FELT CHARACTERS (drawn round (0, 0), about 100 units tall)
def bee(arms=False, happy=False, bow=None, body=YEL, look=0.0):
    o = []
    for sgn in (-1, 1):
        o.append(thread(f"M{sgn * 7},-24 Q{sgn * 9},-38 {sgn * 15},-43", DARK, 2.3))
    for sgn in (-1, 1):
        o.append(felt(ellp(sgn * 25, -26, 17, 11.5, rot=-sgn * 32), "#EAF6FF", st="#93C9E8", inset=3.2))
    for sgn in (-1, 1):
        o.append(knot(sgn * 15.5, -44, 4.6, COCOA))
    if arms:
        for sgn in (-1, 1):
            o.append(felt(ellp(sgn * 31, 6, 9, 6.5, rot=sgn * 35), body, sh=1))
    bd = Polygon(ellp(0, 0, 32, 29))
    o.append(felt(bd, body, st=YEL_T))
    for y0, y1 in ((10, 17.5), (22.5, 30)):
        o.append(felt(bd.intersection(sbox(-40, y0, 40, y1)), COCOA, sh=0))
    ex = 10.5 + look
    if happy:
        o.append(happy_eye(-ex, -6, 4.6) + happy_eye(ex + look, -6, 4.6))
    else:
        o.append(eye(-ex + look, -6, 4.8) + eye(ex + look, -6, 4.8))
    o.append(cheeks(look, 2, 19, 4.3))
    o.append(smile(look, 0, 4.6, open_=happy))
    if bow:
        o.append(felt(ellp(-8, -27, 8, 5.5, rot=-20), bow, st="#FFFFFF", inset=2.4) + felt(ellp(8, -27, 8, 5.5, rot=20), bow, st="#FFFFFF", inset=2.4)
                 + felt(ellp(0, -27, 3.6), mixc(bow, "#000000", .12), sh=1))
    return "".join(o)


def hole_back(rx=46, ry=13):
    return felt(Polygon(ellp(0, 6, rx + 11, ry + 9)), "#B98A63", st="#E7C9A5", inset=3) + felt(ellp(0, 2, rx, ry), "#4A3127", sh=0)


def hole_front(rx=46, ry=13):
    ring = Polygon(ellp(0, 6, rx + 11, ry + 9)).difference(Polygon(ellp(0, 2, rx, ry))).intersection(sbox(-99, 2, 99, 99))
    return felt(ring, "#B98A63", st="#E7C9A5", inset=3, sh=1)


def mole_body(point=None, hat=True, wave=False, cut=None):
    """土豆 the mole from the waist up. point: angle (degrees) of the pointing arm, or None."""
    o = []
    body = Polygon(crs([(0, -66), (24, -60), (36, -38), (38, -8), (36, 14), (-36, 14), (-38, -8), (-36, -38), (-24, -60)], 8))
    if cut is not None:
        body = body.intersection(cut)
    o.append(felt(body, "#8C6A57", st="#C7A58F"))
    if wave:
        o.append(felt(LineString([(-28, -18), (-46, -36), (-50, -50)]).buffer(8.5, cap_style=1), "#8C6A57", st="#C7A58F", inset=2.6))
        o.append(felt(ellp(-51, -55, 10.5, 9, rot=-15), "#FFB3C3", st="#FFFFFF", inset=2.6))
        for d_ in (-4.5, 0, 4.5):
            o.append(thread(f"M{-51 + d_:.1f},{-62:.1f} l{d_ * .2:.1f},-3.5", "#E07F98", 1.5))
    if point is not None:
        a = math.radians(point)
        sx, sy = (26 if math.cos(a) >= 0 else -26), -14
        hx, hy = sx + 34 * math.cos(a), sy + 34 * math.sin(a)
        o.append(felt(LineString([(sx, sy), (hx, hy)]).buffer(8.5, cap_style=1), "#8C6A57", st="#C7A58F", inset=2.6))
        o.append(felt(ellp(hx, hy, 10, 8, rot=point), "#FFB3C3", st="#FFFFFF", inset=2.6))
        for d_ in (-4, 0, 4):
            px, py = hx + 9 * math.cos(a) - d_ * math.sin(a) * .9, hy + 9 * math.sin(a) + d_ * math.cos(a) * .9
            o.append(thread(f"M{px:.1f},{py:.1f} l{3.5 * math.cos(a):.1f},{3.5 * math.sin(a):.1f}", "#E07F98", 1.5))
    o.append(felt(ellp(0, -22, 21, 15), "#D9B9A0", st="#FFFFFF", inset=3))
    o.append(felt(ellp(0, -29, 10.5, 8.5), "#FF8FAB", st=None))
    o.append('<ellipse cx="-3" cy="-32" rx="3.4" ry="2.2" fill="#FFFFFF" opacity=".8"/>')
    o.append(eye(-13, -39, 3.6) + eye(13, -39, 3.6))
    o.append(cheeks(0, -24, 24, 4.5))
    o.append(thread("M-6,-17 Q-3,-13 0,-17 Q3,-13 6,-17", DARK, 1.7))
    if hat:
        dome = Polygon(ellp(0, -56, 31, 24)).intersection(sbox(-40, -90, 40, -54))
        o.append(felt(dome, "#FFC83D", st="#FFF3C0", inset=3))
        o.append(felt(rrect(-38, -58, 76, 9, 4.5), "#FFB31F", sh=1))
        o.append(felt(ellp(0, -70, 7.5, 6.5), "#FFF6CF", st=None))
        o.append('<circle cx="-2" cy="-72" r="2" fill="#FFFFFF"/>')
    return o


def mole(point=None, hat=True, wave=False, paws=True):
    """土豆 popping out of his hole: the hole is at y = 0."""
    rx, ry = 46, 13
    cut = sbox(-99, -200, 99, 2).union(Polygon(ellp(0, 2, rx, ry)))   # the body goes on down the hole
    o = [hole_back(rx, ry)] + mole_body(point, hat, wave, cut)
    o.append(hole_front(rx, ry))
    if paws:
        for sgn in (-1, 1):
            if point is not None and sgn == (1 if math.cos(math.radians(point)) >= 0 else -1):
                continue
            if wave and sgn == -1:
                continue
            o.append(felt(ellp(sgn * 24, 12, 11, 7.5), "#FFB3C3", st="#FFFFFF", inset=2.5))
            for d_ in (-4.5, 0, 4.5):
                o.append(thread(f"M{sgn * 24 + d_:.1f},{16:.1f} l0,3.5", "#E07F98", 1.5))
    return "".join(o)


def fish(col=CORAL, fin=YEL, face=1, happy=False):
    f = face
    o = []
    tail = Polygon(crs([(-24 * f, 0), (-50 * f, -21), (-44 * f, 0), (-50 * f, 21)], 6))
    o.append(felt(tail, fin, st="#FFFFFF", inset=3))
    o.append(felt(Polygon(crs([(-12 * f, -18), (2 * f, -36), (16 * f, -21)], 6)).union(Polygon(ellp(0, -18, 14, 5))), fin, st="#FFFFFF", inset=2.6))
    bd = Polygon(ellp(0, 0, 35, 26))
    o.append(felt(bd, col, st="#FFE3D8"))
    o.append(felt(bd.intersection(sbox(-14 * f if f > 0 else 6, -40, -6 * f if f > 0 else 14, 40)), WHITE, sh=0))
    o.append(felt(ellp(-2 * f, 10, 9, 5.5, rot=-25 * f), fin, st="#FFFFFF", inset=2.2))
    if happy:
        o.append(happy_eye(15 * f, -6, 5))
    else:
        o.append(eye(15 * f, -6, 5.4))
    o.append(felt(ellp(22 * f, 6, 4.2, 3.4), CHEEK, sh=0))
    o.append(thread(f"M{27 * f},{2} Q{30 * f},{6} {33.5 * f},{2}", DARK, 1.8))
    return "".join(o)


def bus(col="#FF7A59", key=False):
    """The little bus, facing right."""
    f = 1
    o = []
    for wx in (-25, 25):
        o.append(felt(ellp(wx * f, 24, 11.5), "#4A4458", st="#8A8598", inset=2.6))
    bd = Polygon(rrect(-48, -36, 96, 60, 15))
    o.append(felt(bd, col, st="#FFE0D2"))
    o.append(felt(bd.intersection(sbox(-60, 6, 60, 13)), "#FFF4D6", sh=0))
    for wx in (-40, -17):
        o.append(felt(rrect(wx, -26, 19, 17, 5), "#CFEFFF", st="#FFFFFF", inset=2.3))
    o.append(felt(rrect(8, -28, 30, 24, 7), "#CFEFFF", st="#FFFFFF", inset=2.5))
    ex = 23 * f
    o.append(eye(ex - 6, -16, 3.8) + eye(ex + 6, -16, 3.8))
    o.append(thread(f"M{ex - 4},{-9} Q{ex},{-6} {ex + 4},{-9}", DARK, 1.6))
    o.append(felt(ellp(43 * f, 15, 4.2), "#FFE36B", sh=0))
    o.append(felt(rrect(-6, -40, 8, 5, 2), "#FFE36B", sh=1))
    for wx in (-25, 25):
        o.append(button(wx * f, 24, 4.8, "#D9D4E4", thr="#8A8598"))
    if key:
        o.append(place(0, -50, .62, key_piece, rot=-15))
    return "".join(o)


def penguin(scarf=RED, happy=False):
    o = []
    for sgn in (-1, 1):
        o.append(felt(ellp(sgn * 11, 40, 10, 5.5), ORA, sh=1))
    for sgn in (-1, 1):
        o.append(felt(ellp(sgn * 30, 6, 8, 19, rot=sgn * -22), NAVY, st="#8E9BD0", inset=2.6))
    bd = Polygon(crs([(0, -46), (22, -38), (31, -6), (28, 30), (0, 42), (-28, 30), (-31, -6), (-22, -38)], 8))
    o.append(felt(bd, NAVY, st="#8E9BD0"))
    face_ = Polygon(crs([(0, -26), (14, -36), (22, -20), (20, 8), (14, 33), (0, 37), (-14, 33), (-20, 8), (-22, -20), (-14, -36)], 8))
    o.append(felt(face_, WHITE, st="#B9C6E6", inset=3))
    if happy:
        o.append(happy_eye(-9, -19, 4.2) + happy_eye(9, -19, 4.2))
    else:
        o.append(eye(-9, -19, 4.4) + eye(9, -19, 4.4))
    o.append(cheeks(0, -10, 15, 3.8))
    o.append(felt(Polygon([(-6, -13), (6, -13), (0, -5)]).buffer(1.6), ORA, sh=1))
    if scarf:
        hat = bd.intersection(sbox(-40, -60, 40, -33)).buffer(1.2)
        o.append(felt(hat, scarf, st="#FFFFFF", inset=2.4, dash=(3.6, 2.8)))
        o.append(felt(rrect(-21, -38, 42, 8, 4), "#FFFFFF", sh=1))
        o.append(knot(0, -50, 6.5, "#FFFFFF"))
    return "".join(o)


def astronaut(happy=False):
    o = []
    o.append(felt(rrect(-27, -4, 54, 40, 12), "#C9CED8", st="#FFFFFF", inset=3))
    o.append(felt(rrect(-21, -2, 42, 44, 14), WHITE, st="#C2C8D4"))
    o.append(felt(ellp(-27, 14, 8, 13, rot=15), WHITE, st="#C2C8D4", inset=2.5) + felt(ellp(27, 14, 8, 13, rot=-15), WHITE, st="#C2C8D4", inset=2.5))
    o.append(felt(ellp(0, 14, 8), RED, sh=1) + felt(star_g(5, 0, 14), YEL, sh=0))
    o.append(thread("M18,-40 L24,-52", "#9AA2B4", 2.2) + knot(24.5, -53, 4, RED))
    o.append(felt(ellp(0, -22, 30, 28), WHITE, st="#C2C8D4"))
    o.append(felt(ellp(0, -20, 22, 19), "#BFE6FF", st="#FFFFFF", inset=2.6))
    o.append(felt(ellp(0, -18, 15.5, 14.5), "#FFD9C0", sh=1))
    o.append(felt(Polygon(crs([(-15, -22), (-10, -33), (2, -35), (13, -29), (15, -21), (6, -26), (-4, -25)], 5)), "#7A5444", sh=0))
    if happy:
        o.append(happy_eye(-6, -17, 3.4) + happy_eye(6, -17, 3.4))
    else:
        o.append(eye(-6, -17, 3.5) + eye(6, -17, 3.5))
    o.append(cheeks(0, -11, 10, 3))
    o.append(smile(0, -11, 3.2, open_=happy))
    o.append('<path d="M-17,-32 A22,19 0 0 1 -3,-38" stroke="#FFFFFF" stroke-width="3" fill="none" stroke-linecap="round" opacity=".85"/>')
    return "".join(o)


def star_piece(R=20, col=YEL, st="#FFFFFF", rot=-90.0):
    return felt(star_g(R, 0, 0, rot), col, st=st, inset=max(2.6, R * .16), sw=1.5, dash=(3.8, 2.8))


def flower(r=16, petal=PINK, center=YEL, n=6, st="#FFFFFF", rot=0.0):
    pet = unary_union([Polygon(ellp(r * .62 * math.cos(math.radians(rot + 360 * i / n)), r * .62 * math.sin(math.radians(rot + 360 * i / n)),
                                    r * .5, r * .38, rot=rot + 360 * i / n)) for i in range(n)])
    return felt(pet, petal, st=st, inset=max(2.2, r * .1), sw=1.4, dash=(3.4, 2.6)) + button(0, 0, r * .36, center)


def leaf(x, y, L, rot, col=GRN):
    return felt(Polygon(tf(crs([(0, 0), (L * .5, -L * .28), (L, 0), (L * .5, L * .28)], 6), x, y, rot)), col, st="#FFFFFF", inset=2.2, sw=1.3, dash=(3.2, 2.6))


def flower_house(door=True):
    """The bee's home: a big felt flower on a stem, with a little round door in the middle."""
    o = [felt(LineString([(0, 30), (2, 70), (0, 100)]).buffer(6, cap_style=1), DGRN, st="#C7EBB5", inset=2.4)]
    o.append(leaf(2, 66, 34, -30, GRN) + leaf(0, 84, 30, 205, GRN))
    n = 8
    pet = unary_union([Polygon(ellp(34 * math.cos(2 * math.pi * i / n), 34 * math.sin(2 * math.pi * i / n), 21, 15, rot=360 * i / n)) for i in range(n)])
    o.append(felt(pet, PINK, st="#FFFFFF", inset=3.4))
    o.append(felt(ellp(0, 0, 27), YEL, st=YEL_T, inset=3.2))
    if door:
        dg = Polygon(rrect(-9, -10, 18, 24, 9)).intersection(sbox(-20, -20, 20, 14))
        o.append(felt(dg, "#B07850", st="#F3D2AE", inset=2.2, sw=1.3, dash=(3, 2.4)))
        o.append('<circle cx="5" cy="3" r="1.8" fill="#FFE36B"/>')
        o.append(felt(ellp(-15, -12, 4.5), "#CFEFFF", sh=1) + felt(ellp(15, -12, 4.5), "#CFEFFF", sh=1))
    return "".join(o)


def key_piece(col="#FFC83D"):
    bow = Polygon(ellp(-16, 0, 13)).difference(Polygon(ellp(-16, 0, 5)))
    shaft = Polygon(rrect(-6, -4.5, 34, 9, 4))
    teeth = Polygon(rrect(14, 2, 6, 10, 2)).union(Polygon(rrect(22, 2, 6, 8, 2)))
    g = unary_union([bow, shaft, teeth])
    return felt(g, col, st="#FFF6CF", inset=2.4, sw=1.4, dash=(3.4, 2.6))


def heart(s=12, col=PINK):
    return felt(heart_pts(0, 0, s), col, st="#FFFFFF", inset=max(2, s * .17), sw=1.3, dash=(3, 2.4))


def cloud_piece(w=60, col=WHITE):
    g = unary_union([Polygon(ellp(-w * .28, 4, w * .26)), Polygon(ellp(w * .05, -4, w * .32)), Polygon(ellp(w * .33, 5, w * .22)),
                     Polygon(rrect(-w * .5, 0, w, w * .26, w * .13))])
    return felt(g, col, st="#C9DDF0", inset=3)


def tree(col=DGRN, s=1.0):
    o = [felt(rrect(-6, 0, 12, 30, 5), BRN, st="#D9B08F", inset=2.2)]
    crown = unary_union([Polygon(ellp(-14, -6, 18)), Polygon(ellp(12, -8, 19)), Polygon(ellp(0, -24, 21)), Polygon(ellp(0, 2, 16))])
    o.append(felt(crown, col, st="#D4F0C2", inset=3.2))
    for x, y in ((-12, -10), (10, -20), (6, 2)):
        o.append(felt(ellp(x, y, 4), RED, sh=1))
    return "".join(o)


def bush(w=50, col=DGRN):
    g = unary_union([Polygon(ellp(-w * .25, 0, w * .3)), Polygon(ellp(w * .1, -w * .12, w * .32)), Polygon(ellp(w * .32, 2, w * .24))]).intersection(sbox(-w, -w, w, w * .2))
    return felt(g, col, st="#D4F0C2", inset=3)


def grass_tuft(col=DGRN):
    g = unary_union([Polygon([(-8, 0), (-6, -12), (-3, 0)]), Polygon([(-3, 0), (0, -16), (3, 0)]), Polygon([(3, 0), (6, -11), (8, 0)])]).buffer(1.2)
    return felt(g, col, sh=1)


def sticker_book_icon(col=RED):
    o = [felt(rrect(-26, -20, 52, 40, 8), col, st="#FFFFFF", inset=3)]
    o.append(felt(rrect(-19, -13, 17, 13, 3), YEL, sh=1) + felt(rrect(2, -13, 17, 13, 3), SKY, sh=1))
    o.append(felt(rrect(-19, 3, 17, 13, 3), MINT, sh=1) + felt(ellp(10.5, 9.5, 6), PINK, sh=1))
    o.append(felt(star_g(4.5, -10.5, -6.5), WHITE, sh=0))
    return "".join(o)


def seaweed(h=60, col="#4FB98A"):
    pts = [(math.sin(i * .9) * 6, -h * i / 8) for i in range(9)]
    return felt(LineString(pts).buffer(6, cap_style=1), col, st="#CFF3DF", inset=2.2, sw=1.3, dash=(3.2, 2.6))


def bubble_ring(r=6):
    return (f'<circle cx="0" cy="0" r="{r}" fill="#FFFFFF" fill-opacity=".35" stroke="#FFFFFF" stroke-width="{1.6 / K:.2f}"/>'
            f'<path d="M{-r * .55:.1f},{-r * .2:.1f} A{r * .6:.1f},{r * .6:.1f} 0 0 1 {-r * .1:.1f},{-r * .6:.1f}" stroke="#FFFFFF" stroke-width="{1.4 / K:.2f}" fill="none" stroke-linecap="round"/>')


def shell(col="#FFC1A8"):
    g = Polygon(crs([(0, -16), (16, -6), (14, 10), (0, 14), (-14, 10), (-16, -6)], 6))
    o = felt(g, col, st="#FFFFFF", inset=2.6)
    for a in (-50, -25, 0, 25, 50):
        r_ = math.radians(a - 90)
        o += thread(f"M0,12 L{13 * math.cos(r_):.1f},{10 + 22 * math.sin(r_) * .9:.1f}", "#E38E72", 1.3)
    return o


def coral_house():
    """The fish's home: a round pink coral with knobbly branches on top and a round door."""
    o = []
    for x, h, w in ((-22, 34, 7), (-6, 46, 8), (12, 40, 7.5), (26, 28, 6.5)):
        br = LineString([(x * .6, 0), (x, -h * .6), (x + (3 if x < 0 else -3), -h)]).buffer(w, cap_style=1)
        o.append(felt(br, "#FF9DB0", st="#FFFFFF", inset=2.4, sw=1.3, dash=(3, 2.4)))
        o.append(knot(x + (3 if x < 0 else -3), -h - 2, w * .62, "#FFD6DE"))
    dome = Polygon(ellp(0, 14, 40, 32)).intersection(sbox(-50, -40, 50, 34))
    o.append(felt(dome, "#FF7F98", st="#FFFFFF", inset=3.4))
    for k_ in range(3):
        pts = [(-30 + i * 4, -2 + k_ * 10 + 3.5 * math.sin(i * 1.4 + k_)) for i in range(16)]
        o.append(thread(dpts(pts, False), "#FFC2CE", 1.6))
    o.append(felt(Polygon(rrect(-10, 10, 20, 26, 10)).intersection(sbox(-20, 0, 20, 34)), "#A8405A", st="#FFC7D2", inset=2, sw=1.2, dash=(3, 2.4)))
    o.append(felt(ellp(-22, 14, 5), "#CFEFFF", sh=1) + felt(ellp(22, 14, 5), "#CFEFFF", sh=1))
    return "".join(o)


def station(sign=True):
    """The bus's home: a little bus station with a striped roof and a round sign."""
    o = [felt(rrect(-34, -18, 68, 46, 6), "#FFE7B8", st="#D9A86A")]
    roof = Polygon([(-44, -16), (44, -16), (36, -38), (-36, -38)]).buffer(3)
    o.append(felt(roof, "#4CB7A5", st="#FFFFFF", inset=3))
    for i in range(4):
        o.append(felt(roof.intersection(sbox(-46 + i * 23, -60, -34.5 + i * 23, 0)), WHITE, sh=0))
    o.append(felt(Polygon(rrect(-11, 2, 22, 26, 11)).intersection(sbox(-20, 0, 20, 28)), "#8E5B3E", st="#F3D2AE", inset=2))
    o.append(felt(rrect(-30, -6, 13, 11, 3), "#CFEFFF", sh=1) + felt(rrect(17, -6, 13, 11, 3), "#CFEFFF", sh=1))
    if sign:
        o.append(felt(rrect(46, -40, 5, 68, 2.5), GREY, sh=1))
        o.append(felt(ellp(48.5, -46, 13), "#4C8DFF", st="#FFFFFF", inset=2.4))
        o.append(felt(rrect(41, -51, 15, 9, 3), WHITE, sh=0) + felt(ellp(44, -41, 2), WHITE, sh=0) + felt(ellp(53, -41, 2), WHITE, sh=0))
    return "".join(o)


def gate(open_=0.0):
    """A wooden gate across the road; open_ 0 = shut, 1 = swung open."""
    o = [felt(rrect(-34, -30, 8, 46, 3), "#A8714E", st="#E6C3A2", inset=2) , felt(rrect(26, -30, 8, 46, 3), "#A8714E", st="#E6C3A2", inset=2)]
    sx = 1 - .78 * open_
    planks = unary_union([Polygon(rrect(-26, -22, 52, 9, 3)), Polygon(rrect(-26, 0, 52, 9, 3))] +
                         [Polygon(rrect(-24 + i * 13, -26, 9, 38, 3)) for i in range(4)])
    pl = Polygon([(-26 + (x + 26) * sx, y - (x + 26) * .18 * open_) for x, y in planks.exterior.coords])
    o.append(felt(pl, "#E5A869", st="#FFE6C2", inset=2.2, sw=1.3, dash=(3.2, 2.4)))
    if open_ < .5:
        o.append(felt(rrect(-6, -4, 12, 11, 3), "#FFC83D", st="#FFFFFF", inset=1.8, sw=1.1, dash=(2.4, 2)))
    return "".join(o)


def house_piece(col="#FF9C7A", roof="#C9675A"):
    o = [felt(rrect(-24, -10, 48, 36, 5), col, st="#FFFFFF", inset=3)]
    o.append(felt(Polygon([(-32, -8), (0, -36), (32, -8)]).buffer(3), roof, st="#FFFFFF", inset=3))
    o.append(felt(rrect(-6, 6, 12, 20, 5), "#8E5B3E", sh=1) + felt(rrect(-19, 0, 9, 9, 2), "#CFEFFF", sh=1) + felt(rrect(10, 0, 9, 9, 2), "#CFEFFF", sh=1))
    return "".join(o)


def snowman():
    o = [felt(ellp(0, 14, 20), WHITE, st="#BFD2EC"), felt(ellp(0, -14, 14), WHITE, st="#BFD2EC", inset=3)]
    o.append(eye(-5, -16, 2.4) + eye(5, -16, 2.4))
    o.append(felt(Polygon([(-1, -12), (3, -12), (12, -9)]).buffer(1.2), ORA, sh=1))
    o.append(felt(rrect(-15, -4, 30, 6, 3), "#5BA8E8", sh=1))
    o.append(button(0, 12, 3, RED) + button(0, 21, 3, RED))
    return "".join(o)


def rocket():
    o = [felt(Polygon([(-14, 10), (-24, 30), (-12, 26)]).buffer(2), RED, sh=1), felt(Polygon([(14, 10), (24, 30), (12, 26)]).buffer(2), RED, sh=1)]
    bd = Polygon(crs([(0, -42), (14, -20), (15, 16), (0, 26), (-15, 16), (-14, -20)], 8))
    o.append(felt(bd, WHITE, st="#C2C8D4"))
    o.append(felt(bd.intersection(sbox(-20, -60, 20, -24)), RED, sh=0))
    o.append(felt(ellp(0, -4, 8), "#8FD3F4", st="#FFFFFF", inset=2))
    o.append(felt(Polygon([(-7, 24), (7, 24), (0, 40)]).buffer(2.5), ORA, sh=1))
    return "".join(o)


def gem(col="#7CD3F7"):
    g = Polygon([(-10, -4), (-5, -11), (5, -11), (10, -4), (0, 10)]).buffer(1.5)
    return felt(g, col, st="#FFFFFF", inset=2, sw=1.2, dash=(2.6, 2)) + '<path d="M-5,-7 L-2,-9" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round"/>'


def root_piece(L=40):
    return felt(LineString([(0, 0), (L * .3, L * .25), (L * .55, L * .2), (L, L * .45)]).buffer(3.4, cap_style=1), "#C68E63", sh=1)


def snowflake(r=8, col="#FFFFFF"):
    o = ""
    for i in range(3):
        a = math.radians(60 * i)
        o += thread(f"M{-r * math.cos(a):.1f},{-r * math.sin(a):.1f} L{r * math.cos(a):.1f},{r * math.sin(a):.1f}", col, 2.2)
    return o


def planet(col="#FFB86B", ring="#B7A3F0"):
    return (felt(ellp(0, 0, 16), col, st="#FFFFFF", inset=2.6)
            + felt(Polygon(ellp(0, 2, 27, 7, rot=-15)).difference(Polygon(ellp(0, 0, 18, 4.5, rot=-15))).difference(sbox(-30, -30, 30, -2).intersection(Polygon(ellp(0, 0, 16)))), ring, sh=1))


def finger(x, y, rot=-25.0):
    """A see-through grown-up fingertip pressing at (x, y)."""
    g = LineString([(0, 0), (0, 96)]).buffer(24, cap_style=1)
    d = dgeom(g)
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot})">'
            f'<circle cx="0" cy="0" r="34" fill="#FFFFFF" opacity=".35"/>'
            f'<path d="{d}" fill="#FFE1CF" fill-opacity=".62" stroke="#D99D82" stroke-opacity=".55" stroke-width="2"/>'
            f'<path d="M-12,-8 Q0,-17 12,-8 L12,8 Q0,14 -12,8Z" fill="#FFFFFF" fill-opacity=".55"/>'
            f'<path d="M-16,10 Q-18,40 -14,64" stroke="#FFFFFF" stroke-opacity=".55" stroke-width="4" fill="none" stroke-linecap="round"/></g>')



# ================================================================ PAGE 0: THE SAME GARDEN MAZE IN THREE STYLES
# Tiles (column, row) on an 8 x 6 grid: the bee starts bottom left, the flower is on the right,
# one fork at the top right corner leads to a short dead end.
GARDEN_MAIN = [(0, 5), (3, 5), (3, 3), (1, 3), (1, 1), (5, 1), (5, 4), (7, 4)]
GARDEN_FORK = [(5, 1), (7, 1)]
GARDEN_STARS = [(1, 2), (5, 2.55)]


def gpt(c, T, ox, oy):
    return ox + (c[0] + .5) * T, oy + (c[1] + .5) * T


def frame_clip(x, y, w, h, r):
    return clip(dpts(rrect(x, y, w, h, r)))


# ---------------------------------------------------------------- A: felt
def garden_felt(x, y, w=330, h=240):
    T = 36
    ox, oy = x + (w - 8 * T) / 2, y + (h - 6 * T) / 2
    o = [gingham(x, y, w, h, "#FFFDF6", "#9ED3F0", 22)]
    o.append(felt(rrect(x + 7, y + 6, w - 14, h - 12, 16), "#A3D982", st="#FFFFFF", inset=6, sh=2))
    P = lambda c: gpt(c, T, ox, oy)
    main = rline([P(c) for c in GARDEN_MAIN], 20)
    fork = [P(c) for c in GARDEN_FORK]
    pw = 30
    cor = soft(unary_union([LineString(main).buffer(pw / 2), LineString(fork).buffer(pw / 2)]), 2)
    for c, s in (((0, 1.7), .72), ((0, 3.9), .66), ((6.4, 0.05), .66), ((2.9, 0.1), .6), ((6.6, 5.25), .7), ((4.3, 5.4), .66)):
        px, py = P(c)
        o.append(place(px, py, s, flower, 16, [PINK, "#FFFFFF", LILAC, ORA][int(c[0] * 7 + c[1]) % 4]))
    for c in ((2.1, 2.05), (0.15, 0.4), (4.55, 3.4), (6.0, 2.6), (2.0, 4.3)):
        px, py = P(c)
        o.append(place(px, py + 6, .8, grass_tuft))
    bx, by = P((2.7, 2.0))
    o.append(place(bx, by + 8, .62, bush, 60))
    tx_, ty_ = P((6.55, 2.3))
    o.append(place(tx_, ty_, .55, tree))
    o.append(felt(cor, "#FFF1CC", st="#C99A62", inset=3.6))
    for c in GARDEN_STARS:
        px, py = P(c)
        o.append(place(px, py, .72, star_piece, 20))
    gx, gy = P(GARDEN_MAIN[-1])
    o.append(place(gx + 4, gy - 6, .44, flower_house))
    sx, sy = P(GARDEN_MAIN[0])
    o.append(place(sx + 5, sy - 3, .6, bee))
    return f'<g clip-path="{frame_clip(x, y, w, h, 18)}">{"".join(o)}</g>'


# ---------------------------------------------------------------- B: pixels
class Pix:
    """A grid of big square pixels (None = empty)."""

    def __init__(self, w, h):
        self.w, self.h = w, h
        self.g = [[None] * w for _ in range(h)]

    def put(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h and c:
            self.g[y][x] = c

    def get(self, x, y):
        return self.g[y][x] if 0 <= x < self.w and 0 <= y < self.h else None

    def rect(self, x0, y0, x1, y1, c):
        for yy in range(y0, y1):
            for xx in range(x0, x1):
                self.put(xx, yy, c)

    def ell(self, cx, cy, rx, ry, c):
        for yy in range(int(cy - ry) - 1, int(cy + ry) + 2):
            for xx in range(int(cx - rx) - 1, int(cx + rx) + 2):
                if ((xx + .5 - cx) / rx) ** 2 + ((yy + .5 - cy) / ry) ** 2 <= 1.0:
                    self.put(xx, yy, c)

    def rows(self, ox, oy, rows, pal):
        for j, row in enumerate(rows):
            for i, ch in enumerate(row):
                if ch in pal:
                    self.put(ox + i, oy + j, pal[ch])

    def blit(self, o, ox, oy, outline=None):
        if outline:
            for yy in range(-1, o.h + 1):
                for xx in range(-1, o.w + 1):
                    if o.get(xx, yy) is None and any(o.get(xx + a, yy + b) for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                        self.put(ox + xx, oy + yy, outline)
        for yy in range(o.h):
            for xx in range(o.w):
                if o.g[yy][xx]:
                    self.put(ox + xx, oy + yy, o.g[yy][xx])

    def svg(self, x, y, s):
        out = []
        for j, row in enumerate(self.g):
            i = 0
            while i < self.w:
                c = row[i]
                n = 1
                while i + n < self.w and row[i + n] == c:
                    n += 1
                if c:
                    out.append(f'<rect x="{x + i * s:.2f}" y="{y + j * s:.2f}" width="{n * s + .3:.2f}" height="{s + .3:.2f}" fill="{c}"/>')
                i += n
        return f'<g shape-rendering="crispEdges">{"".join(out)}</g>'


PX = {"k": "#2B2340", "y": "#FFD23A", "o": "#FF9F1C", "w": "#FFFFFF", "s": "#8EE3FF", "p": "#FF6FA8", "r": "#FF4D5E",
      "g": "#3DB55B", "G": "#2A8F47", "l": "#7BDB6E", "d": "#1D6B3A", "t": "#FFE3A1", "T": "#F0C478", "u": "#FFF3CF",
      "m": "#B86BFF", "b": "#7A4A2B"}

PX_STAR = ["...y...",
           "..yyy..",
           "yyuyyyy",
           ".yyyyy.",
           "..yyy..",
           ".yy.yy.",
           "yy...yy"]
PX_SMALL = [".p.", "pyp", ".p."]


PX_BEE = ["....k...k....",
          ".kk..k.k..kk.",
          "kwwkkkkkkkwwk",
          "kwskyyyyykswk",
          "kwkykyyykykwk",
          ".kkykyyykykk.",
          "..kpyyyyypk..",
          "..kkkkkkkkk..",
          "..kyyyyyyyk..",
          "...kkkkkkk...",
          "....kkkkk...."]
PX_FLOWER = ["...ppp...",
             "..pwppp..",
             "..ppppp..",
             "pppyyyppp",
             "pwyyoyypp",
             "pppyyyppp",
             "..ppppp..",
             "..ppppp..",
             "...ppp...",
             "....G....",
             ".ll.G.ll.",
             "..llGll..",
             "....G...."]


def sprite(rows):
    s = Pix(max(len(r) for r in rows), len(rows))
    s.rows(0, 0, rows, PX)
    return s


def garden_pixel(x, y, w=330, h=240):
    cs, T = 4, 9
    P = Pix(83, 60)
    ox, oy = 5, 3
    path = set()
    for line in (GARDEN_MAIN, GARDEN_FORK):
        for (a, b), (c, d) in zip(line, line[1:]):
            for t in range(max(abs(c - a), abs(d - b)) + 1):
                path.add((a + (c > a) * t - (c < a) * t, b + (d > b) * t - (d < b) * t))
    rnd = random.Random(5)
    hedge = [["g"] * T for _ in range(T)]
    for _ in range(8):
        hedge[rnd.randrange(0, T - 1)][rnd.randrange(T)] = "G"
    for _ in range(6):
        hedge[rnd.randrange(0, T - 1)][rnd.randrange(T)] = "l"
    sand = [["t"] * T for _ in range(T)]
    for xx, yy in ((2, 3), (6, 6), (4, 7), (7, 2)):
        sand[yy][xx] = "T"
    for yy in range(60):
        for xx in range(83):
            P.put(xx, yy, PX[hedge[(yy - oy) % T][(xx - ox) % T]])
    for ty in range(6):
        for tx_ in range(8):
            X, Y = ox + tx_ * T, oy + ty * T
            if (tx_, ty) in path:
                P.rows(X, Y, ["".join(r) for r in sand], PX)
                if (tx_, ty - 1) not in path:
                    P.rect(X, Y, X + T, Y + 1, PX["T"])
                if (tx_ - 1, ty) not in path:
                    P.rect(X, Y, X + 1, Y + T, PX["T"])
            else:
                P.rows(X, Y, ["".join(r) for r in hedge], PX)
                if (tx_, ty + 1) in path:
                    P.rect(X, Y + T - 1, X + T, Y + T, PX["d"])
    for tx_, ty in ((0, 1), (2, 2), (4, 3), (6, 2), (3, 0), (6, 5), (0, 3), (4, 5), (7, 0), (1, 0)):
        P.rows(ox + tx_ * T + 2 + (tx_ % 2) * 2, oy + ty * T + 2, PX_SMALL, {"p": PX["p"] if (tx_ + ty) % 2 else PX["w"], "y": PX["y"]})
    for c in GARDEN_STARS:
        P.blit(sprite(PX_STAR), ox + int(c[0] * T + T / 2 - 3.5), oy + int(c[1] * T + T / 2 - 3.5), PX["k"])
    P.blit(sprite(PX_FLOWER), ox + 7 * T + 4 - 4, oy + 4 * T + 4 - 7, PX["k"])
    P.blit(sprite(PX_BEE), ox + 0 * T + 4 - 6, oy + 5 * T - 2)
    return f'<g clip-path="{frame_clip(x, y, w, h, 18)}"><rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{PX["g"]}"/>{P.svg(x - 1, y, cs)}</g>'


# ---------------------------------------------------------------- C: jelly and candy
def gloss(cx, cy, rx, ry, rot=-30.0, op=.9):
    return (f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="#FFFFFF" opacity="{op}" transform="rotate({rot} {cx:.1f} {cy:.1f})"/>'
            f'<circle cx="{cx + rx * 1.3:.1f}" cy="{cy + ry * .3:.1f}" r="{max(1.0, ry * .45):.1f}" fill="#FFFFFF" opacity="{op}"/>')


def jfill(d, col, op=.86, rim=None, sh=True, cx=.38, cy=.3):
    rim = rim or mixc(col, "#5A1A3A", .3)
    grad = rg([(0, mixc(col, "#FFFFFF", .6)), (.5, col), (1, mixc(col, "#3A0A2A", .14))], cx, cy, .78)
    o = ""
    if sh:
        o += f'<path d="{d}" fill="{mixc(col, "#7A1A4A", .45)}" opacity=".28" transform="translate(1.5 4)" filter="{blur(2.2)}"/>'
    return o + f'<path d="{d}" fill="{grad}" fill-opacity="{op}" stroke="{rim}" stroke-width="1.4" stroke-opacity=".5"/>'


def j_bee(s=1.0):
    o = []
    for sgn in (-1, 1):
        o.append(f'<path d="M{sgn * 6},-24 Q{sgn * 9},-36 {sgn * 15},-40" stroke="#6B3A2A" stroke-width="2.6" fill="none" stroke-linecap="round"/>')
        o.append(jfill(dpts(ellp(sgn * 15.5, -41, 4.6)), "#FF6FA8", sh=False))
    for sgn in (-1, 1):
        o.append(jfill(dpts(ellp(sgn * 24, -24, 16, 11, rot=-sgn * 32)), "#CFF3FF", op=.7, rim="#7CC8E8"))
        o.append(gloss(sgn * 24 - 5, -28, 5, 2.2, -sgn * 32, .8))
    bd = ellp(0, 0, 31, 28)
    o.append(jfill(dpts(bd), "#FFC93A", op=.92, rim="#D88A12"))
    bp = Polygon(bd)
    for y0, y1 in ((9, 16.5), (21, 28)):
        o.append(f'<path d="{dgeom(bp.intersection(sbox(-40, y0, 40, y1)))}" fill="#8A4A22" opacity=".75"/>')
    for ex in (-10, 10):
        o.append(f'<ellipse cx="{ex}" cy="-5" rx="4.4" ry="5.4" fill="#3A1F2A"/><circle cx="{ex + 1.6}" cy="-7.2" r="1.9" fill="#FFFFFF"/>')
    o.append('<ellipse cx="-18" cy="3" rx="4.6" ry="3.2" fill="#FF6F8E" opacity=".55"/><ellipse cx="18" cy="3" rx="4.6" ry="3.2" fill="#FF6F8E" opacity=".55"/>')
    o.append('<path d="M-4.5,1 Q0,6 4.5,1" stroke="#7A2A2A" stroke-width="2" fill="none" stroke-linecap="round"/>')
    o.append(gloss(-14, -16, 9, 4.2, -35))
    return "".join(o)


def j_star(R=11, col="#FFD43B"):
    d = dgeom(star_g(R))
    return jfill(d, col, op=.95, rim="#E08A00") + gloss(-R * .32, -R * .3, R * .3, R * .13, -30)


def j_flower(r=24):
    o = [f'<rect x="-3" y="{r * .6:.1f}" width="6" height="{r * 1.4:.1f}" rx="3" fill="#FFFFFF"/>']
    for i in range(4):
        o.append(f'<path d="M-3,{r * .8 + i * 8:.1f} l6,-4 l0,3 l-6,4Z" fill="#FF5C8A"/>')
    for i in range(6):
        a = math.radians(60 * i - 90)
        o.append(jfill(dpts(ellp(r * .62 * math.cos(a), r * .62 * math.sin(a), r * .42)), "#FF7DB4", op=.9, rim="#E0457E", sh=i == 0))
    for i in range(6):
        a = math.radians(60 * i - 90)
        o.append(gloss(r * .62 * math.cos(a) - r * .14, r * .62 * math.sin(a) - r * .16, r * .12, r * .06, -30, .85))
    o.append(f'<circle cx="0" cy="0" r="{r * .42:.1f}" fill="#FFFFFF" stroke="#E0457E" stroke-opacity=".5" stroke-width="1.4"/>')
    sp = [(math.cos(t * .35) * t * r * .0085, math.sin(t * .35) * t * r * .0085) for t in range(0, 44)]
    o.append(f'<path d="{dpts(sp, False)}" stroke="#FFB800" stroke-width="{r * .1:.1f}" fill="none" stroke-linecap="round"/>')
    o.append(gloss(-r * .18, -r * .2, r * .12, r * .06))
    return "".join(o)


def gumdrop(col, r=11):
    d = f"M{-r},{r * .55} Q{-r},{-r} 0,{-r} Q{r},{-r} {r},{r * .55} Q0,{r * .8} {-r},{r * .55}Z"
    o = jfill(d, col, op=.92)
    rnd = random.Random(int(r * 10) + len(col))
    for _ in range(6):
        o += f'<circle cx="{rnd.uniform(-r * .6, r * .6):.1f}" cy="{rnd.uniform(-r * .5, r * .4):.1f}" r=".9" fill="#FFFFFF" opacity=".9"/>'
    return o + gloss(-r * .35, -r * .45, r * .25, r * .12)


def lolly(r=10, c1="#FF5C8A", c2="#FFFFFF"):
    o = [f'<rect x="-1.6" y="{r * .7:.1f}" width="3.2" height="{r * 1.6:.1f}" rx="1.6" fill="#FFFFFF" stroke="#E7C9D6" stroke-width=".8"/>']
    o.append(jfill(dpts(ellp(0, 0, r)), c1, op=.95))
    sp = [(math.cos(t * .4) * t * r * .045, math.sin(t * .4) * t * r * .045) for t in range(0, 22)]
    o.append(f'<path d="{dpts(sp, False)}" stroke="{c2}" stroke-width="{r * .2:.1f}" fill="none" stroke-linecap="round" opacity=".95"/>')
    return "".join(o) + gloss(-r * .35, -r * .45, r * .25, r * .11)


def sprinkles(x, y, w, h, n, seed=3, cols=("#FF6FA8", "#7FD8FF", "#FFD43B", "#8CE07A", "#B98BFF", "#FFFFFF")):
    rnd = random.Random(seed)
    o = []
    for _ in range(n):
        cx, cy = rnd.uniform(x, x + w), rnd.uniform(y, y + h)
        o.append(f'<rect x="{cx - 3.5:.1f}" y="{cy - 1.3:.1f}" width="7" height="2.6" rx="1.3" fill="{rnd.choice(cols)}" '
                 f'transform="rotate({rnd.uniform(0, 180):.0f} {cx:.1f} {cy:.1f})"/>')
    return "".join(o)


def jelly_path(lines, pw, col="#6FD6F7", rim="#2FA6D8", glow="#E2FAFF", shadow="#C2407A"):
    o = []
    ds = [dpts(l, False) for l in lines]

    def strokes(wd, c, op, extra=""):
        return "".join(f'<path d="{d}" fill="none" stroke="{c}" stroke-width="{wd:.1f}" stroke-linecap="round" stroke-linejoin="round" '
                       f'stroke-opacity="{op}" {extra}/>' for d in ds)
    o.append(f'<g filter="{blur(3)}" transform="translate(2 6)">{strokes(pw + 2, shadow, .3)}</g>')
    o.append(f'<g opacity=".62">{strokes(pw, rim, 1)}</g>')
    o.append(f'<g opacity=".55">{strokes(pw - 5, col, 1)}</g>')
    cor = unary_union([LineString(l).buffer(pw / 2 - 2.5) for l in lines])
    cp = clip(dgeom(cor))
    o.append(f'<g clip-path="{cp}"><g filter="{blur(2.5)}" transform="translate({pw * .16:.1f} {pw * .2:.1f})" opacity=".45">{strokes(pw * .5, rim, 1)}</g></g>')
    o.append(f'<g filter="{blur(2.2)}" opacity=".75">{strokes(pw * .34, glow, 1)}</g>')
    hl = "".join(f'<path d="{d}" fill="none" stroke="#FFFFFF" stroke-width="{pw * .11:.1f}" stroke-linecap="round" stroke-linejoin="round" '
                 f'stroke-dasharray="150 14 5 14" opacity=".92" transform="translate({-pw * .23:.1f} {-pw * .26:.1f})"/>' for d in ds)
    o.append(f'<g clip-path="{cp}">{hl}</g>')
    for l in lines:
        for t in (.12, .47, .8):
            (px_, py_), _ = along(l, t)
            o.append(f'<circle cx="{px_ - pw * .2:.1f}" cy="{py_ - pw * .22:.1f}" r="{pw * .06:.1f}" fill="#FFFFFF" opacity=".9"/>')
    return "".join(o)


def garden_jelly(x, y, w=330, h=240):
    T = 38
    ox, oy = x + (w - 8 * T) / 2, y + (h - 6 * T) / 2
    o = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{lg([(0, "#FFE1EE"), (1, "#FFD0E4")])}"/>']
    o.append(sprinkles(x, y, w, h, 110))
    P = lambda c: gpt(c, T, ox, oy)
    for c, col in (((0, 1.8), "#8CE07A"), ((2.6, 2.05), "#B98BFF"), ((4.5, 3.6), "#FFD43B"), ((6.5, 2.5), "#7FD8FF"), ((5.3, 5.3), "#FF6FA8"), ((2.3, 4.15), "#FFA94D")):
        px, py = P(c)
        o.append(f'<g transform="translate({px:.1f} {py:.1f})">{gumdrop(col, 10)}</g>')
    for c, c1 in (((0.1, 3.9), "#7FD8FF"), ((6.3, 0.2), "#FF5C8A"), ((2.8, 0.15), "#B98BFF"), ((3.8, 5.25), "#8CE07A")):
        px, py = P(c)
        o.append(f'<g transform="translate({px:.1f} {py - 4:.1f})">{lolly(9, c1)}</g>')
    main = rline([P(c) for c in GARDEN_MAIN], 22)
    fork = [P(c) for c in GARDEN_FORK]
    o.append(jelly_path([main, fork], 29))
    # see-through: the sprinkles under the jelly show faintly
    cp = clip(dgeom(unary_union([LineString(l).buffer(29 / 2 - 3) for l in (main, fork)])))
    o.append(f'<g clip-path="{cp}" opacity=".32">{sprinkles(x, y, w, h, 110)}</g>')
    for c in GARDEN_STARS:
        px, py = P(c)
        o.append(f'<g transform="translate({px:.1f} {py:.1f})">{j_star(12.5)}</g>')
    gx, gy = P(GARDEN_MAIN[-1])
    o.append(f'<g transform="translate({gx + 2:.1f} {gy - 6:.1f})">{j_flower(22)}</g>')
    sx, sy = P(GARDEN_MAIN[0])
    o.append(f'<g transform="translate({sx + 4:.1f} {sy - 3:.1f}) scale(.55)">{j_bee()}</g>')
    return f'<g clip-path="{frame_clip(x, y, w, h, 18)}">{"".join(o)}</g>'


# ---------------------------------------------------------------- the page
def lipbox(x, y, w, h, r, fill="#FFFFFF", lip="#E9DED3", lipd=4, sh=True):
    o = ""
    if sh:
        o += f'<rect x="{x}" y="{y + 4}" width="{w}" height="{h}" rx="{r}" fill="#6B4F3F" opacity=".12" filter="{blur(6)}"/>'
    o += f'<rect x="{x}" y="{y + lipd}" width="{w}" height="{h}" rx="{r}" fill="{lip}"/>'
    return o + f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}"/>'


def style_sheet():
    ph = 1226
    o = [f'<rect width="{W}" height="{ph}" fill="#F7F2EA"/>']
    o.append(tx(195, 58, "選一個畫風", 30, INK))
    o.append(tx(195, 90, "同一個花園小迷宮，三種畫法", 16, SOFT))
    bands = [("A 羊毛氈布書風（建議）", "像小朋友的布書：毛氈縫在布上，有縫線、毛茸茸。", "a"),
             ("B 像素小遊戲風", "大大的方塊像素，像以前的電視遊戲，格子很清楚。", "b"),
             ("C 果凍糖果風", "路像透明的果凍，亮晶晶、彈彈的，很甜很可愛。", "c")]
    y = 116
    for title, desc, st in bands:
        h = 346
        if st == "a":
            o.append(f'<rect x="12" y="{y - 4}" width="366" height="{h + 8}" rx="28" fill="#5DB86A"/>')
            o.append(lipbox(16, y, 358, h, 24, "#FFFFFF", "#E3F4E8", 0, sh=False))
            o.append(f'<rect x="270" y="{y - 14}" width="92" height="30" rx="15" fill="#5DB86A"/>' + tx(316, y + 7, "我建議這個", 14, "#FFFFFF"))
        else:
            o.append(lipbox(16, y, 358, h, 24))
        o.append(tx(34, y + 40, title, 22, INK, "start"))
        o.append(tx(34, y + 68, desc, 14.5, "#6E5C52", "start"))
        px, py = 30, y + 88
        o.append({"a": garden_felt, "b": garden_pixel, "c": garden_jelly}[st](px, py))
        y += h + 22
    return page("".join(o), "#F7F2EA", W, ph), ph


# ================================================================ FELT UI PIECES (screens 1-7)
def wtx(x, y, s, size, dark, anchor="middle", col="#FFFFFF"):
    """White words on felt, with a soft darker copy under them."""
    return tx(x + .6, y + 1.6, s, size, dark, anchor, 'opacity=".5"') + tx(x, y, s, size, col, anchor)


def fbtn(cx, cy, r, col, icon="", st="#FFFFFF", sh=2):
    return felt(ellp(cx, cy, r), col, st=st, inset=max(3.5, r * .15), sh=sh) + icon


def i_home(cx, cy, col=CORAL, s=1.0):
    g = Polygon(tf([(-14, 0), (0, -13), (14, 0), (10, 0), (10, 12), (-10, 12), (-10, 0)], cx, cy, s=s)).buffer(1.8 * s, join_style=1)
    return felt(g, col, sh=1) + felt(rrect(cx - 3.8 * s, cy + 3 * s, 7.6 * s, 9.5 * s, 3 * s), WHITE, sh=0)


def i_magnifier(cx, cy, s=1.0):
    c0 = (cx - 3 * s, cy - 3 * s)
    handle = LineString([(cx + 5 * s, cy + 5 * s), (cx + 15 * s, cy + 15 * s)]).buffer(4.4 * s, cap_style=1)
    ring = Polygon(ellp(c0[0], c0[1], 13 * s)).difference(Polygon(ellp(c0[0], c0[1], 8.6 * s)))
    return (felt(handle, BRN, sh=1) + felt(ellp(c0[0], c0[1], 9.5 * s), "#D6F1FF", sh=0) + felt(ring, ORA, sh=1)
            + f'<path d="M{c0[0] - 5.5 * s:.1f},{c0[1] - 1 * s:.1f} A6,6 0 0 1 {c0[0] - 1 * s:.1f},{c0[1] - 5.5 * s:.1f}" stroke="#FFFFFF" stroke-width="{2.4 * s:.1f}" fill="none" stroke-linecap="round"/>')


def i_speaker(cx, cy, col="#FFFFFF", s=1.0):
    g = Polygon(tf([(-12, -5), (-6, -5), (2, -12), (2, 12), (-6, 5), (-12, 5)], cx - 2 * s, cy, s=s)).buffer(1.4 * s, join_style=1)
    w = (f"M{cx + 4.5 * s:.1f},{cy - 5 * s:.1f} A8,8 0 0 1 {cx + 4.5 * s:.1f},{cy + 5 * s:.1f} "
         f"M{cx + 8.5 * s:.1f},{cy - 10 * s:.1f} A14,14 0 0 1 {cx + 8.5 * s:.1f},{cy + 10 * s:.1f}")
    return felt(g, col, sh=1) + thread(w, col, 2.8 * s)


def i_lock(cx, cy, col="#8A8F9C", s=1.0):
    return (thread(f"M{cx - 5 * s:.1f},{cy - 1 * s:.1f} V{cy - 6 * s:.1f} A5,5 0 0 1 {cx + 5 * s:.1f},{cy - 6 * s:.1f} V{cy - 1 * s:.1f}", col, 2.6 * s)
            + felt(rrect(cx - 8 * s, cy - 2 * s, 16 * s, 13 * s, 3 * s), col, sh=1))


def i_check(cx, cy, s=1.0, col="#FFFFFF"):
    return thread(f"M{cx - 7 * s:.1f},{cy:.1f} L{cx - 2 * s:.1f},{cy + 5.5 * s:.1f} L{cx + 8 * s:.1f},{cy - 6 * s:.1f}", col, 3.6 * s)


def i_arrow(cx, cy, s=1.0, col="#FFFFFF", rot=0.0):
    g = Polygon(tf([(-11, -4), (2, -4), (2, -11), (13, 0), (2, 11), (2, 4), (-11, 4)], cx, cy, rot, s=s)).buffer(1.2 * s, join_style=1)
    return felt(g, col, sh=1)


def i_map(cx, cy, s=1.0):
    pts = [(-14, -10), (-5, -13), (5, -10), (14, -13), (14, 10), (5, 13), (-5, 10), (-14, 13)]
    o = felt(Polygon(tf(pts, cx, cy, s=s)), "#FFF1CC", sh=1)
    o += felt(Polygon(tf([(-5, -13), (5, -10), (5, 13), (-5, 10)], cx, cy, s=s)), "#E8D6A8", sh=0)
    o += thread(f"M{cx - 10 * s:.1f},{cy + 6 * s:.1f} Q{cx - 2 * s:.1f},{cy - 8 * s:.1f} {cx + 9 * s:.1f},{cy - 2 * s:.1f}", RED, 1.8 * s, (3, 2.4))
    return o


def fbubble(x, y, w, h, side=None, at=0.0, fill=WHITE, st="#D9C8BA", r=22, tl=18):
    g = Polygon(rrect(x, y, w, h, r))
    if side == "left":
        g = g.union(Polygon([(x + 4, at - 12), (x - tl, at + 6), (x + 4, at + 12)]))
    elif side == "right":
        g = g.union(Polygon([(x + w - 4, at - 12), (x + w + tl, at + 6), (x + w - 4, at + 12)]))
    elif side == "down":
        g = g.union(Polygon([(at - 12, y + h - 4), (at + 4, y + h + tl), (at + 12, y + h - 4)]))
    return felt(soft(g, 2), fill, st=st, inset=5.5, sh=2)


def fpill(cx, cy, w, h, col, label="", size=20, dark=None, icon="", st="#FFFFFF", tdx=0.0):
    o = felt(rrect(cx - w / 2, cy - h / 2, w, h, h / 2), col, st=st, inset=5, sh=2) + icon
    if label:
        o += wtx(cx + tdx, cy + size * .36, label, size, dark or mixc(col, "#000000", .35))
    return o


def age_chip(cx, cy, label):
    return felt(rrect(cx - 42, cy - 17, 84, 34, 17), "#FFFFFF", st="#E2C9B5", inset=4, sh=1) + tx(cx, cy + 5.5, label, 15.5, INK)


def felt_title(cx, cy, text, cols, r=28, gap=60, size=31):
    n = len(text)
    x0 = cx - (n - 1) * gap / 2
    o = []
    for i, ch in enumerate(text):
        x = x0 + i * gap
        yy = cy + (-3 if i % 2 else 3)
        col = cols[i % len(cols)]
        o.append(felt(ellp(x, yy, r), col, st="#FFFFFF", inset=4, sh=2))
        rot = (-7, 6, -4, 7, -5)[i % 5]
        o.append(f'<g transform="rotate({rot} {x:.1f} {yy:.1f})">{wtx(x, yy + size * .36, ch, size, mixc(col, "#000000", .4))}</g>')
    return "".join(o)


def topbar(right=""):
    return fbtn(42, 50, 25, WHITE, i_home(42, 50, CORAL, 1.0), st="#E2C9B5") + right


def instr(text, size=22, y=84, h=66):
    """The spoken instruction at the top: a speaker button and a few words (read out loud for the child)."""
    o = fbubble(18, y, 354, h, fill=WHITE)
    o += fbtn(56, y + h / 2, 22, "#5DB86A", i_speaker(57, y + h / 2, "#FFFFFF", .95))
    o += tx(212, y + h / 2 + size * .36, text, size, INK)
    return o


def fpage(x, y, w, h, col, st="#FFFFFF", r=26):
    return felt(rrect(x, y, w, h, r), col, st=st, inset=8, sh=3)


def sparkle(cx, cy, r, c=YEL, op=1.0):
    return (f'<path d="M{cx},{cy - r} Q{cx + r * .16},{cy - r * .16} {cx + r},{cy} Q{cx + r * .16},{cy + r * .16} {cx},{cy + r} '
            f'Q{cx - r * .16},{cy + r * .16} {cx - r},{cy} Q{cx - r * .16},{cy - r * .16} {cx},{cy - r}Z" fill="{c}" opacity="{op}"/>')


def dots_row(cx, y, n, k, on=CORAL, r=6, gap=20):
    x0 = cx - (n - 1) * gap / 2
    o = []
    for i in range(n):
        x = x0 + i * gap
        if i < k:
            o.append(felt(ellp(x, y, r), on, sh=1))
        elif i == k:
            o.append(felt(ellp(x, y, r + 2), WHITE, st=on, inset=2.2, sw=1.2, dash=(2.6, 2), sh=1))
        else:
            o.append(felt(ellp(x, y, r), "#FFFFFF", sh=0, extra=' opacity=".85"'))
    return "".join(o)


def maze_corridors(edges, cell, x0, y0, pw, r=10):
    cw, ch = cell
    C = lambda c: (x0 + (c[0] + .5) * cw, y0 + (c[1] + .5) * ch)
    g = unary_union([LineString([C(a), C(b)]).buffer(pw / 2, cap_style=3) for a, b in edges])
    return soft(g, r), C


def trail_pts(cells, C, r=18):
    return rline([C(c) for c in cells], r)


# ================================================================ SCREEN 1: home
WORLDS = [("花園", "garden", "#CDEBB4", 3), ("地底隧道", "tunnel", "#EFD9C4", 2), ("海底", "sea", "#C6E8F7", 1),
          ("城市", "city", "#FFE0C6", 0), ("雪地", "snow", "#E2ECFA", 0), ("太空", "space", "#DDD2F6", 0)]


def mini_garden(x, y, w, h):
    o = [felt(rrect(x - 6, y - 6, w + 12, h + 12, 4), "#A3D982", sh=0)]
    line = crs([(x - 10, y + h - 22), (x + 40, y + h - 26), (x + 70, y + 40), (x + 108, y + 34), (x + w + 10, y + 46)], 8, False)
    o.append(felt(LineString(line).buffer(13), "#FFF1CC", st="#C99A62", inset=2.6, sw=1.3, dash=(3.4, 2.6)))
    o.append(place(x + 20, y + 18, .5, flower, 16, ORA) + place(x + 70, y + h - 14, .5, flower, 16, LILAC))
    o.append(place(x + 74, y + 41, .4, star_piece, 20))
    o.append(place(x + w - 26, y + 26, .26, flower_house))
    o.append(place(x + 30, y + h - 30, .52, bee))
    return "".join(o)


def mini_tunnel(x, y, w, h):
    o = [felt(rrect(x - 6, y - 6, w + 12, h + 12, 4), "#B98A63", sh=0)]
    o.append(felt(rrect(x - 6, y - 6, w + 12, 18, 2), "#8DCF6E", sh=1))
    g = soft(unary_union([LineString([(x - 10, y + h - 24), (x + 60, y + h - 24), (x + 60, y + 34), (x + w + 10, y + 34)]).buffer(13, cap_style=3)]), 8)
    o.append(felt(g, "#6B4A3B", st="#D9B08F", inset=2.6, sw=1.3, dash=(3.4, 2.6)))
    o.append(place(x + 108, y + 66, .8, gem, "#7CD3F7") + place(x + 22, y + 34, .7, gem, "#FF9EC1"))
    o.append(place(x + 120, y + 14, .5, root_piece, 34))
    o.append(place(x + 30, y + h - 14, .4, mole, None, True, False, False))
    return "".join(o)


def mini_sea(x, y, w, h):
    o = [felt(rrect(x - 6, y - 6, w + 12, h + 12, 4), "#4FA9CF", sh=0)]
    line = crs([(x - 10, y + 30), (x + 50, y + 34), (x + 80, y + h - 24), (x + w + 10, y + h - 28)], 8, False)
    o.append(felt(LineString(line).buffer(13), "#A8E6F2", st="#FFFFFF", inset=2.6, sw=1.3, dash=(3.4, 2.6)))
    o.append(place(x + 18, y + h, .55, seaweed, 50) + place(x + w - 18, y + 30, .5, seaweed, 44, "#7FD08A"))
    o.append(place(x + 110, y + 24, .6, coral_house))
    for bx, by, r in ((x + 90, y + 30, 5), (x + 98, y + 18, 3.5), (x + 60, y + 56, 4)):
        o.append(place(bx, by, 1, bubble_ring, r))
    o.append(place(x + 34, y + 32, .5, fish))
    return "".join(o)


def mini_city(x, y, w, h):
    o = [felt(rrect(x - 6, y - 6, w + 12, h + 12, 4), "#A3D982", sh=0)]
    g = soft(LineString([(x - 10, y + h - 26), (x + 96, y + h - 26), (x + 96, y - 10)]).buffer(14, cap_style=3), 8)
    o.append(felt(g, "#9EA4B4", sh=1))
    o.append(stitch(dpts([(x - 10, y + h - 26), (x + 96, y + h - 26), (x + 96, y - 10)], False), "#FFFFFF", 2, (7, 6)))
    o.append(place(x + 26, y + 22, .4, house_piece) + place(x + 132, y + 58, .45, house_piece, "#8FD3F4", "#5B8FD0"))
    o.append(place(x + 60, y + 16, .28, tree) + place(x + 130, y + 14, .3, tree))
    o.append(place(x + 50, y + h - 30, .5, bus))
    return "".join(o)


def mini_snow(x, y, w, h):
    o = [felt(rrect(x - 6, y - 6, w + 12, h + 12, 4), "#F2F7FF", sh=0)]
    line = crs([(x - 10, y + h - 20), (x + 50, y + h - 30), (x + 90, y + 34), (x + w + 10, y + 30)], 8, False)
    o.append(felt(LineString(line).buffer(13), "#BFE3F7", st="#FFFFFF", inset=2.6, sw=1.3, dash=(3.4, 2.6)))
    o.append(place(x + 120, y + h - 30, .7, snowman))
    for sx, sy in ((x + 20, y + 18), (x + 66, y + 14), (x + 140, y + 20)):
        o.append(place(sx, sy, .6, snowflake, 7, "#9CC9EE"))
    o.append(place(x + 36, y + h - 34, .44, penguin))
    return "".join(o)


def mini_space(x, y, w, h):
    o = [felt(rrect(x - 6, y - 6, w + 12, h + 12, 4), "#34407A", sh=0)]
    rnd = random.Random(8)
    for _ in range(14):
        o.append(f'<circle cx="{x + rnd.uniform(4, w - 4):.1f}" cy="{y + rnd.uniform(4, h - 4):.1f}" r="{rnd.uniform(.8, 1.7):.1f}" fill="#FFFFFF" opacity=".85"/>')
    line = crs([(x - 10, y + h - 22), (x + 50, y + h - 30), (x + 90, y + 36), (x + w + 10, y + 30)], 8, False)
    o.append(felt(LineString(line).buffer(13), "#5A65A8", st="#FFE36B", inset=2.6, sw=1.3, dash=(3.4, 2.6)))
    o.append(place(x + 124, y + 64, .62, planet))
    o.append(place(x + 130, y + 20, .4, rocket, rot=30))
    o.append(place(x + 38, y + h - 36, .46, astronaut))
    return "".join(o)


MINI = {"garden": mini_garden, "tunnel": mini_tunnel, "sea": mini_sea, "city": mini_city, "snow": mini_snow, "space": mini_space}


def world_card(x, y, w, h, name, key, col, stars):
    o = [felt(rrect(x, y, w, h, 22), col, st="#FFFFFF", inset=5, sh=2)]
    wx, wy, ww, wh = x + 10, y + 10, w - 20, h - 52
    o.append(f'<g clip-path="{clip(dpts(rrect(wx, wy, ww, wh, 15)))}">{MINI[key](wx, wy, ww, wh)}</g>')
    o.append(tx(x + 15, y + h - 15, name, 17, INK, "start"))
    for i in range(3):
        sx = x + w - 54 + i * 19
        if i < stars:
            o.append(place(sx, y + h - 21, .42, star_piece, 20))
        else:
            o.append(felt(star_g(8.2, sx, y + h - 21), mixc(col, "#FFFFFF", .45), sh=0))
    return "".join(o)


def screen_home():
    o = [gingham(0, 0, W, H, "#FFFBF0", "#FFD49A", 28, .3)]
    o.append(felt(rrect(292, 24, 82, 34, 17), "#E9E4EA", st="#FFFFFF", inset=4, sh=1) + i_lock(314, 41, "#9A98A8", .85) + tx(350, 47, "家長", 14.5, "#7E7A8C"))
    o.append(felt_title(195, 108, "迷宮小冒險", [CORAL, ORA, "#7BC86A", BLUE, LILAC]))
    o.append(place(92, 268, .98, mole, None, True, True))
    o.append(fbubble(170, 168, 204, 84, "left", 214))
    o.append(tx(272, 203, "我挖了好多路，", 17.5, INK) + tx(272, 231, "一起走走看！", 17.5, INK))
    cw, ch = 172, 142
    for i, (name, key, col, stars) in enumerate(WORLDS):
        r_, c_ = divmod(i, 2)
        o.append(world_card(16 + c_ * (cw + 14), 304 + r_ * (ch + 12), cw, ch, name, key, col, stars))
    o.append(fpill(195, 790, 210, 58, RED, "", icon=place(140, 790, .78, sticker_book_icon, YEL)))
    o.append(wtx(214, 798, "貼紙冊", 22, "#9E3B33"))
    return page("".join(o), "#FFFBF0")


# ================================================================ SCREEN 2: follow the path (2-3 years)
def screen_follow():
    o = [gingham(0, 0, W, H, "#FFFDF6", "#9ED3F0", 28)]
    o.append(topbar(age_chip(332, 50, "2～3 歲")))
    o.append(instr("帶小蜜蜂去找花！", 23))
    o.append(fpage(14, 166, 362, 604, "#A3D982"))
    main = rline([(56, 706), (306, 706), (306, 566), (86, 566), (86, 426), (306, 426), (306, 300)], 64)
    pw = 76
    for (fx, fy), s, c in (((40, 200), .9, ORA), ((190, 496), .95, PINK), ((350, 640), .8, "#FFFFFF"), ((186, 640), .8, LILAC), ((190, 356), .85, YEL),
                           ((60, 330), .75, PINK), ((350, 500), .7, ORA)):
        o.append(place(fx, fy, s, flower, 16, c))
    for fx, fy in ((120, 640), (250, 642), (240, 498), (120, 360), (40, 400), (350, 380)):
        o.append(place(fx, fy, 1, grass_tuft))
    o.append(place(140, 250, 1.0, bush, 70) + place(64, 268, .7, tree))
    o.append(felt(LineString(main).buffer(pw / 2), "#FFF1CC", st="#C99A62", inset=5))
    tb = .185
    walked = part_line(main, 0, tb)
    o.append(thread(dpts(walked, False), "#FFB020", 4.2, (10, 8)))
    for t in (.47, .64, .84):
        (sx, sy), _ = along(main, t)
        o.append(place(sx, sy, .95, star_piece, 20))
    gx, gy = main[-1]
    o.append(place(gx, gy - 34, .98, flower_house))
    (bx, by), _ = along(main, tb)
    o.append(place(bx, by - 4, .98, bee))
    o.append(sparkle(bx - 46, by - 34, 7, "#FFFFFF") + sparkle(bx - 64, by - 14, 5, "#FFFFFF"))
    o.append(finger(bx + 16, by + 24, -34))
    o.append(dots_row(195, 806, 5, 1, CORAL))
    o.append(fbtn(340, 804, 27, YEL, i_magnifier(340, 804, .95), st="#FFFFFF"))
    return page("".join(o), "#FFFDF6")


# ================================================================ SCREEN 3: the maze (3-5 years)
SEA_EDGES = [((0, 4), (1, 4)), ((1, 4), (1, 3)), ((1, 3), (0, 3)), ((0, 3), (0, 2)), ((0, 2), (0, 1)), ((0, 1), (0, 0)), ((0, 0), (1, 0)),
             ((1, 0), (2, 0)), ((2, 0), (2, 1)), ((2, 1), (2, 2)), ((2, 2), (3, 2)), ((3, 2), (3, 1)), ((3, 1), (4, 1)), ((4, 1), (4, 0)),
             ((0, 2), (1, 2)), ((1, 0), (1, 1)), ((2, 0), (3, 0)), ((3, 2), (4, 2)), ((4, 2), (4, 3)), ((4, 3), (4, 4)), ((4, 4), (3, 4)),
             ((3, 4), (2, 4)), ((2, 4), (2, 3)), ((2, 3), (3, 3))]


def screen_maze():
    o = [dotcloth(0, 0, W, H, "#EAF7FF", "#BFE6FA", 30, 4.5)]
    o.append(topbar(age_chip(332, 50, "3～5 歲")))
    o.append(instr("帶小魚回珊瑚家！", 23))
    o.append(fpage(14, 166, 362, 604, "#2F8FA6", st="#BDEBF5"))
    x0, y0, cw, ch = 26, 180, 67.6, 85
    cor, C = maze_corridors(SEA_EDGES, (cw, ch), x0, y0, 48, 9)
    # sand at the bottom, seaweed on the walls
    sand = Polygon(crs([(0, 650), (60, 640), (130, 652), (200, 638), (270, 650), (340, 640), (400, 650), (400, 800), (0, 800)], 6)).intersection(Polygon(rrect(14, 166, 362, 604, 26)))
    o.append(felt(sand, "#F2D9A6", st="#FFFFFF", inset=5))
    o.append(felt(cor, "#A8E8F2", st="#FFFFFF", inset=4.5))
    tr = trail_pts([(0, 4), (1, 4), (1, 3), (0, 3), (0, 2)], C, 22)
    L = LineString(tr).length
    n = int(L / 19)
    for i in range(1, n - 1):
        (bx, by), _ = along(tr, i / n)
        r = 3.2 + 2.2 * ((i * 37) % 5) / 4
        o.append(place(bx + ((i * 13) % 7 - 3), by + ((i * 7) % 5 - 2), 1, bubble_ring, r))
    hx, hy = C((0, 2))
    tx_, ty_ = C((0, 1))
    o.append(thread(f"M{hx:.1f},{hy - 30:.1f} L{tx_:.1f},{ty_ + 6:.1f}", "#FFD54F", 3.6, (6, 5)))
    o.append(felt(Polygon([(tx_ - 12, ty_ + 10), (tx_, ty_ - 6), (tx_ + 12, ty_ + 10)]).buffer(2.5, join_style=1), "#FFD54F", st="#FFFFFF", inset=2, sw=1.2, dash=(2.6, 2)))
    o.append(sparkle(tx_ + 18, ty_ - 6, 6, "#FFFFFF") + sparkle(tx_ - 18, ty_ + 18, 4.5, "#FFFFFF"))
    gx, gy = C((4, 0))
    o.append(place(gx, gy - 2, .74, coral_house))
    for sx, sy, s in ((36, 760, .8), (362, 720, .7)):
        o.append(place(sx, sy, s, seaweed, 70, "#4FB98A"))
    o.append(place(70, 690, .85, shell) + place(132, 742, .7, star_piece, 16, ORA, "#FFFFFF", -70))
    o.append(place(hx + 4, hy + 2, .62, fish, rot=-14))
    o.append(place(296, 738, .82, mole, -118, True, False))
    o.append(fbubble(108, 670, 116, 50, "right", 698, fill=WHITE))
    o.append(tx(166, 703, "往上游！", 19, INK))
    o.append(fbtn(340, 806, 27, YEL, i_magnifier(340, 806, .95), st="#FFFFFF"))
    o.append(dots_row(195, 808, 5, 2, "#3FA7C9"))
    return page("".join(o), "#EAF7FF")


# ================================================================ SCREEN 4: deliver (4-5 years)
CITY_EDGES = [((0, 5), (1, 5)), ((1, 5), (2, 5)), ((2, 5), (3, 5)), ((3, 5), (4, 5)), ((3, 5), (3, 4)), ((3, 4), (3, 3)), ((3, 3), (2, 3)),
              ((2, 3), (2, 2)), ((2, 2), (2, 1)), ((2, 1), (2, 0)), ((2, 0), (1, 0)), ((1, 0), (0, 0)),
              ((1, 5), (1, 4)), ((1, 4), (0, 4)), ((0, 4), (0, 3)), ((0, 3), (1, 3)), ((1, 3), (1, 2)), ((1, 2), (0, 2)), ((0, 2), (0, 1)), ((0, 1), (1, 1)),
              ((1, 4), (2, 4)), ((3, 3), (4, 3)), ((4, 3), (4, 4)), ((4, 3), (4, 2)), ((4, 2), (3, 2)), ((3, 2), (3, 1)), ((3, 1), (4, 1)),
              ((4, 1), (4, 0)), ((4, 0), (3, 0))]


def boom(x, y, ang):
    """A barrier arm on a post at (x, y), raised to ang degrees."""
    L = 52
    arm = Polygon(tf(rrect(0, -5, L, 10, 5), x, y, ang))
    o = felt(arm, WHITE, sh=1)
    for i in range(3):
        seg = Polygon(tf(rrect(8 + i * 16, -5, 8, 10, 1), x, y, ang)).intersection(arm)
        o += felt(seg, RED, sh=0)
    o += felt(rrect(x - 7, y - 4, 14, 26, 4), "#9EA4B4", st="#FFFFFF", inset=2, sw=1.1, dash=(2.6, 2)) + felt(ellp(x, y, 7), "#FFC83D", sh=1)
    return o


def task_strip(y=84, h=70):
    o = fbubble(18, y, 354, h, fill=WHITE)
    o += fbtn(54, y + h / 2, 22, "#5DB86A", i_speaker(55, y + h / 2, "#FFFFFF", .95))
    cy = y + h / 2
    xs = (132, 222, 312)
    for a, b in zip(xs, xs[1:]):
        o += thread(f"M{a + 30},{cy} L{b - 30},{cy}", "#D3B9A6", 2.6, (5, 4))
        o += thread(f"M{b - 36},{cy - 6} L{b - 30},{cy} L{b - 36},{cy + 6}", "#D3B9A6", 2.6)
    # 1 key: done
    o += felt(ellp(xs[0], cy, 25), "#FFF3D6", st="#E9C98A", inset=3, sh=1) + place(xs[0] - 3, cy + 1, .66, key_piece, rot=-20)
    o += felt(ellp(xs[0] + 19, cy - 18, 10.5), "#5DB86A", sh=1) + i_check(xs[0] + 19, cy - 18, .72)
    # 2 gate: now
    o += f'<circle cx="{xs[1]}" cy="{cy}" r="31" fill="#FFE36B" opacity=".55" filter="{blur(4)}"/>'
    o += felt(ellp(xs[1], cy, 26), "#FFF8E0", st=ORA, inset=3, sh=1, sw=2)
    o += place(xs[1] - 15, cy + 9, .62, boom, 0, 0, -12)
    # 3 home: next
    o += felt(ellp(xs[2], cy, 25), "#F1F1F4", st="#D0D2DA", inset=3, sh=1) + place(xs[2], cy + 6, .46, station, False)
    return o


def screen_deliver():
    o = [dotcloth(0, 0, W, H, "#FFF6E4", "#FFE0A8", 30, 4.5)]
    o.append(topbar(age_chip(332, 50, "4～5 歲")))
    o.append(task_strip())
    o.append(fpage(14, 166, 362, 604, "#A9DB8A"))
    x0, y0, cw, ch = 26, 178, 67.6, 96.5
    cor, C = maze_corridors(CITY_EDGES, (cw, ch), x0, y0, 42, 8)
    # little houses and trees on the blocks
    for (c, r), kind in ((((0.5, 0.5)), "t"), (((3.5, 0.5)), "h"), (((1.5, 1.5)), "h2"), (((3.5, 1.5)), "t"), (((0.5, 2.5)), "t"),
                         (((2.5, 2.5)), "h"), (((3.5, 3.5)), "t"), (((1.5, 3.5)), "h2"), (((0.5, 4.5)), "h"), (((2.5, 4.5)), "t"), (((3.5, 4.5)), "h2")):
        px, py = x0 + (c + .5) * cw, y0 + (r + .5) * ch
        if kind == "t":
            o.append(place(px, py - 2, .38, tree))
        elif kind == "h":
            o.append(place(px, py + 2, .5, house_piece))
        else:
            o.append(place(px, py + 2, .5, house_piece, "#8FD3F4", "#5B8FD0"))
    o.append(felt(cor, "#A3A9B9", st="#E3E6EE", inset=3.5))
    for a, b in CITY_EDGES:
        (ax, ay), (bx, by) = C(a), C(b)
        o.append(stitch(f"M{ax:.1f},{ay:.1f} L{bx:.1f},{by:.1f}", "#FFFFFF", 2.2, (8, 8), .9))
    # zebra crossing on the bottom road, a traffic light beside it
    zx, zy = (C((1, 5))[0] + C((2, 5))[0]) / 2, C((1, 5))[1]
    for i in range(4):
        o.append(felt(rrect(zx - 14, zy - 17 + i * 9.5, 28, 5.5, 2), WHITE, sh=0))
    o.append(felt(rrect(zx + 22, zy - 64, 14, 34, 5), "#4A4458", sh=1) + felt(rrect(zx + 27, zy - 30, 4, 14, 2), "#8A8598", sh=1))
    o.append(felt(ellp(zx + 29, zy - 57, 4.2), "#FF6B6B", sh=0) + felt(ellp(zx + 29, zy - 47, 4.2), "#FFE36B", sh=0) + felt(ellp(zx + 29, zy - 37, 4.2), "#6BD66F", sh=0))
    # the trail behind the bus
    tr = trail_pts([(0, 5), (1, 5), (2, 5), (3, 5), (4, 5)], C, 20)
    tr2 = trail_pts([(3, 5), (3, 4), (3, 3), (2, 3), (2, 2)], C, 20)
    for line in (tr, part_line(tr2, 0, .9)):
        o.append(thread(dpts(line, False), "#FFB020", 3.8, (2, 9)))
    # the key's spot: picked up
    kx, ky = C((4, 5))
    o.append(f'<g opacity=".55">{stitch(dgeom(Polygon(ellp(kx, ky, 17)).buffer(0)), "#FFFFFF", 2, (4, 3))}</g>')
    o.append(felt(ellp(kx, ky, 11), "#5DB86A", sh=1) + i_check(kx, ky, .72))
    # the gate (between (2, 1) and (2, 0)) is opening
    gx, gy = C((2, 0))
    gy2 = (gy + C((2, 1))[1]) / 2
    o.append(boom(gx - 26, gy2 + 4, -62))
    o.append(sparkle(gx + 18, gy2 - 20, 8, "#FFE36B") + sparkle(gx + 28, gy2 + 4, 5, "#FFFFFF") + sparkle(gx - 6, gy2 - 40, 5, "#FFFFFF"))
    sx, sy = C((0, 0))
    o.append(place(sx + 2, sy + 4, .58, station))
    bx, by = C((2, 2))
    o.append(place(bx, by + 4, .6, bus, "#FF7A59", True))
    o.append(fbtn(340, 806, 27, YEL, i_magnifier(340, 806, .95), st="#FFFFFF"))
    o.append(dots_row(195, 808, 5, 3, ORA))
    return page("".join(o), "#FFF6E4")


# ================================================================ SCREEN 5: home at last
def confetti(n, seed, box):
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    cols = [CORAL, YEL, SKY, "#7BC86A", LILAC, PINK, ORA]
    o = []
    for i in range(n):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        c = rnd.choice(cols)
        k = i % 3
        if k == 0:
            o.append(felt(ellp(x, y, rnd.uniform(4, 6.5)), c, sh=1))
        elif k == 1:
            o.append(felt(Polygon(tf([(-6, 4), (0, -6), (6, 4)], x, y, rnd.uniform(0, 360))).buffer(1), c, sh=1))
        else:
            o.append(felt(Polygon(tf(rrect(-7, -2.5, 14, 5, 2.5), x, y, rnd.uniform(0, 180))), c, sh=1))
    return "".join(o)


def sticker(cx, cy, s, inner, rot=0.0, r=40):
    """A felt sticker: a white felt circle with a stitched edge and a little picture on it."""
    body = felt(ellp(0, 0, r), WHITE, st="#E3CDBE", inset=4.5, sh=2) + inner
    return f'<g transform="translate({cx:.1f} {cy:.1f}) rotate({rot}) scale({s})">{body}</g>'


def screen_home_at_last():
    o = [gingham(0, 0, W, H, "#FFF9F4", "#FFC2D2", 28, .3)]
    o.append(confetti(26, 4, (14, 150, 376, 330)))
    o.append(felt_title(195, 104, "到家了！", [CORAL, ORA, "#7BC86A", BLUE], r=31, gap=68, size=34))
    o.append(f'<ellipse cx="195" cy="560" rx="160" ry="22" fill="#5D3B2A" opacity=".1" filter="{blur(6)}"/>')
    o.append(felt(Polygon(crs([(40, 562), (100, 532), (195, 526), (290, 532), (350, 562), (290, 590), (195, 596), (100, 590)], 6)), "#A3D982", st="#FFFFFF", inset=5))
    o.append(place(195, 300, 1.5, flower_house))
    for hx, hy, s, c in ((150, 386, 11, PINK), (238, 372, 9, CORAL), (196, 352, 13, RED)):
        o.append(place(hx, hy, 1, heart, s, c))
    o.append(place(195, 480, 1.3, bee, True, True, PINK))
    o.append(place(146, 516, .95, bee, True, True, rot=8))
    o.append(place(246, 526, .72, bee, True, True, rot=-10))
    for x, y, r in ((62, 440, 8), (330, 430, 7), (84, 370, 5), (306, 350, 6)):
        o.append(sparkle(x, y, r, "#FFE36B"))
    # the new sticker flies into the sticker book
    o.append(thread("M120,610 Q150,676 222,668", "#E3B6A0", 2.8, (6, 7)))
    o.append(thread("M258,684 Q276,700 288,700", "#E3B6A0", 2.8, (6, 7)))
    o.append(place(318, 704, 1.6, sticker_book_icon))
    o.append(sticker(238, 664, .8, place(0, 4, .62, bee, False, True, PINK), -14))
    o.append(sparkle(272, 630, 8, "#FFE36B") + sparkle(196, 642, 5, "#FFE36B") + sparkle(356, 662, 6, "#FFE36B"))
    o.append(fpill(110, 786, 160, 58, "#FFFFFF", "", icon=i_map(62, 786, 1.05), st="#E2C9B5") + tx(126, 793, "回地圖", 20, INK))
    o.append(fpill(282, 786, 168, 62, "#5DB86A", "", icon=i_arrow(324, 786, 1.1)) + wtx(258, 794, "下一關", 22, "#2F7A3E"))
    return page("".join(o), "#FFF9F4")


# ================================================================ SCREEN 6: the sticker book
def honey_pot():
    o = felt(Polygon(crs([(-18, -8), (18, -8), (22, 10), (14, 24), (-14, 24), (-22, 10)], 6)), "#FFB84C", st="#FFFFFF", inset=3)
    o += felt(rrect(-20, -16, 40, 10, 5), "#C9822E", sh=1)
    o += felt(Polygon(crs([(-16, -8), (16, -8), (12, 4), (4, 0), (-4, 6), (-12, 0)], 5)), "#FFE36B", sh=0)
    return o


def ladybug():
    o = felt(ellp(0, -14, 9), DARK, sh=1)
    o += felt(ellp(0, 2, 18, 16), RED, st="#FFFFFF", inset=2.6)
    o += thread("M0,-12 L0,17", DARK, 2)
    for x, y in ((-8, -2), (8, -2), (-9, 9), (9, 9)):
        o += felt(ellp(x, y, 3.2), DARK, sh=0)
    return o + eye(-3.5, -15, 1.8) + eye(3.5, -15, 1.8)


def butterfly():
    o = ""
    for sgn in (-1, 1):
        o += felt(ellp(sgn * 13, -8, 13, 11, rot=sgn * 20), LILAC, st="#FFFFFF", inset=2.6)
        o += felt(ellp(sgn * 11, 12, 9, 8, rot=-sgn * 20), PINK, st="#FFFFFF", inset=2.4)
    o += felt(rrect(-4, -16, 8, 34, 4), COCOA, sh=1)
    o += thread("M-2,-15 Q-6,-24 -10,-26 M2,-15 Q6,-24 10,-26", DARK, 1.6)
    return o


def screen_book():
    o = [dotcloth(0, 0, W, H, "#FFF4EA", "#FFD3BF", 30, 4.5)]
    o.append(topbar())
    o.append(fpill(195, 50, 176, 50, RED, "", icon=place(146, 50, .62, sticker_book_icon, YEL)))
    o.append(wtx(212, 58, "貼紙冊", 21, "#9E3B33"))
    # the book: a red felt cover with a cream page sewn on it; one tab per world sticks out on the right
    tabs = [("garden", "#CDEBB4"), ("tunnel", "#EFD9C4"), ("sea", "#C6E8F7"), ("city", "#FFE0C6"), ("snow", "#E2ECFA"), ("space", "#DDD2F6")]
    icons = [place(0, 0, .44, bee), place(0, 10, .3, mole, None, True, False, False), place(0, 0, .42, fish), place(0, 0, .38, bus),
             place(0, 0, .42, penguin), place(0, 2, .42, astronaut)]
    for i, (k, col) in enumerate(tabs):
        ty = 124 + i * 100
        x1 = 386 if i == 0 else 377
        o.append(felt(rrect(280, ty, x1 - 280, 84, 18), col, st="#FFFFFF", inset=4, sh=1))
        o.append(f'<g transform="translate({352 if i == 0 else 347} {ty + 42})">{icons[i]}</g>')
    o.append(felt(rrect(14, 100, 304, 676, 26), "#E8665A", st="#FFD5CC", inset=7, sh=3))
    o.append(felt(rrect(30, 116, 272, 644, 18), "#FFF6E6", st="#E8CDB8", inset=6, sh=1))
    o.append(f'<g transform="translate(166 160)">{place(0, 0, .52, bee)}</g>')
    stickers = [place(0, 4, .7, bee), place(0, 2, .58, bee, True, True, PINK), place(0, 4, .34, flower_house), place(0, 0, 1.05, ladybug),
                place(0, 0, 1.05, butterfly), place(0, 2, 1.05, honey_pot)]
    for i in range(10):
        r_, c_ = divmod(i, 2)
        sx, sy = (104 if c_ == 0 else 228) + (5 if r_ % 2 else -5), 252 + r_ * 104
        if i < len(stickers):
            o.append(sticker(sx, sy, 1, stickers[i], (-6, 5, -3, 7, -5, 4)[i], r=45))
        else:
            o.append(f'<circle cx="{sx}" cy="{sy}" r="45" fill="#F3E3D2" opacity=".75"/>' + stitch(dpts(ellp(sx, sy, 43)), "#D8BDA8", 2, (5, 4)))
            o.append(f'<g opacity=".22">{felt(star_g(17, sx, sy), "#B89A86", sh=0)}</g>')
    o.append(fbtn(64, 806, 26, "#FFFFFF", i_arrow(64, 806, .9, "#E8665A", 180), st="#E2C9B5"))
    o.append(dots_row(166, 806, 3, 0, "#E8665A"))
    o.append(fbtn(268, 806, 26, "#FFFFFF", i_arrow(268, 806, .9, "#E8665A"), st="#E2C9B5"))
    return page("".join(o), "#FFF4EA")


# ================================================================ SCREEN 7: parents
P_BG, P_TXT, P_SUB, P_ACC = "#F6F2EC", "#3D3A40", "#8A8590", "#3FA58E"


def section(y, h, title=None):
    o = f'<rect x="16" y="{y}" width="358" height="{h}" rx="16" fill="#FFFFFF" stroke="#ECE6DE" stroke-width="1.2"/>'
    if title:
        o += tx(30, y + 26, title, 14, P_SUB, "start")
    return o


def segmented(y, labels, sel, x=30, w=330, h=36):
    n = len(labels)
    sw = w / n
    o = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="#EFECE7"/>'
    for i, lb in enumerate(labels):
        if i == sel:
            o += f'<rect x="{x + i * sw + 3:.1f}" y="{y + 3}" width="{sw - 6:.1f}" height="{h - 6}" rx="8" fill="{P_ACC}"/>'
        o += tx(x + i * sw + sw / 2, y + h / 2 + 5.5, lb, 15, "#FFFFFF" if i == sel else P_TXT)
    return o


def toggle(x, y, on):
    c = P_ACC if on else "#D7D3CD"
    kx = x + 30 if on else x + 12
    return f'<rect x="{x}" y="{y}" width="46" height="26" rx="13" fill="{c}"/><circle cx="{kx}" cy="{y + 13}" r="10" fill="#FFFFFF"/>'


def screen_parents():
    o = [f'<rect width="{W}" height="{H}" fill="{P_BG}"/>']
    o.append(tx(195, 50, "家長模式", 20, P_TXT))
    o.append('<circle cx="350" cy="44" r="18" fill="#E7E2DB"/>' + '<path d="M343,37 L357,51 M357,37 L343,51" stroke="#5C5864" stroke-width="2.4" stroke-linecap="round"/>')
    o.append(section(74, 100, "年齡"))
    o.append(segmented(110, ("2～3 歲", "3～4 歲", "4～5 歲"), 1))
    o.append(tx(30, 164, "年紀越大，路越長、岔路越多。", 12.5, P_SUB, "start"))
    o.append(section(184, 92, "每次玩多久"))
    for i, m in enumerate((5, 10, 15, 20, 30)):
        x = 30 + i * 67
        sel = m == 15
        o.append(f'<rect x="{x}" y="{220}" width="61" height="36" rx="18" fill="{P_ACC if sel else "#FFFFFF"}" stroke="{P_ACC if sel else "#DCD6CE"}" stroke-width="1.5"/>')
        o.append(tx(x + 30.5, 243, f"{m} 分鐘", 14, "#FFFFFF" if sel else P_TXT))
    o.append(section(286, 100, "提示"))
    o.append(segmented(322, ("多", "少"), 0))
    o.append(tx(30, 376, "卡住的時候，土豆會從地洞探出頭指路。", 12.5, P_SUB, "start"))
    o.append(section(396, 150))
    o.append(tx(30, 428, "聲音", 16, P_TXT, "start"))
    o.append(f'<rect x="96" y="420" width="210" height="6" rx="3" fill="#E6E2DC"/><rect x="96" y="420" width="140" height="6" rx="3" fill="{P_ACC}"/>'
             f'<circle cx="236" cy="423" r="10" fill="#FFFFFF" stroke="{P_ACC}" stroke-width="2"/>')
    o.append(f'<g transform="translate(336 423) scale(.7)"><path d="M-14,-5 L-8,-5 L0,-12 L0,12 L-8,5 L-14,5Z" fill="{P_SUB}"/>'
             f'<path d="M5,-6 A9,9 0 0 1 5,6 M9,-11 A15,15 0 0 1 9,11" stroke="{P_SUB}" stroke-width="2.8" fill="none" stroke-linecap="round"/></g>')
    o.append('<path d="M30,446 L360,446" stroke="#F0ECE6" stroke-width="1.2"/>')
    o.append(tx(30, 470, "念出來", 16, P_TXT, "start") + tx(30, 488, "用國語念出要做什麼、往哪裡走", 12.5, P_SUB, "start"))
    o.append(toggle(314, 460, True))
    o.append('<path d="M30,499 L360,499" stroke="#F0ECE6" stroke-width="1.2"/>')
    o.append(tx(30, 520, "英文", 16, P_TXT, "start") + tx(30, 537, "說完國語，再說一次英文", 12.5, P_SUB, "start"))
    o.append(toggle(314, 508, False))
    o.append(section(556, 214, "進度"))
    o.append(tx(360, 582, "已經走完 10 關", 13, P_SUB, "end"))
    rows = [("花園", 6, "#7FC86A"), ("地底隧道", 3, "#B98A63"), ("海底", 1, "#4FB0DA"), ("城市", 0, "#FF8F6B"), ("雪地", 0, "#8FB4E8"), ("太空", 0, "#8A78D8")]
    for i, (n, k, c) in enumerate(rows):
        y = 606 + i * 28
        o.append(f'<rect x="30" y="{y - 11}" width="16" height="16" rx="5" fill="{c}"/>')
        o.append(tx(54, y + 2, n, 14, P_TXT, "start"))
        for j in range(10):
            o.append(f'<circle cx="{142 + j * 17}" cy="{y - 3}" r="6" fill="{c if j < k else "#EFEBE5"}"/>')
        o.append(tx(360, y + 2, f"{k}/10", 13, P_SUB, "end"))
    o.append('<rect x="16" y="780" width="358" height="50" rx="16" fill="#FFF6E2" stroke="#F1DDB0" stroke-width="1.2"/>')
    o.append('<g transform="translate(40 805)"><rect x="-11" y="-7" width="22" height="17" rx="3" fill="#F2B544"/><rect x="-13" y="-12" width="26" height="7" rx="2" fill="#E89A2C"/>'
             '<rect x="-2" y="-12" width="4" height="22" fill="#FFFFFF" opacity=".8"/></g>')
    o.append(tx(60, 801, "完整版（以後）：六個世界、全部玩法，一次買斷", 12.5, "#8A6A2A", "start"))
    o.append(tx(60, 818, "現在免費：花園、海底", 12.5, "#A88A50", "start"))
    return page("".join(o), P_BG)


SCREENS = {"1_首頁": screen_home, "2_跟著路走": screen_follow, "3_走迷宮": screen_maze, "4_送東西": screen_deliver,
           "5_到家了": screen_home_at_last, "6_貼紙冊": screen_book, "7_家長模式": screen_parents}


def contact_sheet(names):
    cw_, ch_, gap, m = 232, 502, 24, 30
    per = 4
    w = per * cw_ + (per - 1) * gap + 2 * m
    rowh = ch_ + 64
    h = 2 * rowh + 40
    items = []
    for i, n in enumerate(names):
        r, c = divmod(i, per)
        x = m + c * (cw_ + gap) + (0 if r == 0 else (cw_ + gap) / 2)
        y = 28 + r * rowh
        items.append(f'<div style="position:absolute;left:{x}px;top:{y}px;width:{cw_}px;text-align:center">'
                     f'<img src="file://{HERE / (n + ".png")}" style="width:{cw_}px;height:{ch_}px;border-radius:18px;box-shadow:0 6px 16px rgba(90,60,40,.2)">'
                     f'<div style="font:19px Huninn, sans-serif;color:{INK};margin-top:10px">{n.replace("_", " ")}</div></div>')
    css = f"@font-face {{ font-family: Huninn; src: url('file://{FONT}'); }} * {{ margin:0; padding:0 }} body {{ width:{w}px; height:{h}px; background:#F7F1E8; position:relative }}"
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head><body>{"".join(items)}</body></html>', w, h


# ================================================================ PAGE MACHINERY
def tx(x, y, s, size=16, color=INK, anchor="middle", extra="", weight=""):
    w = f' font-weight="{weight}"' if weight else ""
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" text-anchor="{anchor}"{w} '
            f'font-family="Huninn, sans-serif" {extra}>{s}</text>')


def txo(x, y, s, size, color, ol="#FFFFFF", ow=6, anchor="middle"):
    """Words with a soft outline around them."""
    return tx(x, y, s, size, color, anchor, f'stroke="{ol}" stroke-width="{ow}" stroke-linejoin="round" paint-order="stroke"')


def page(body, bg, w=W, h=H):
    css = (f"@font-face {{ font-family: Huninn; src: url('file://{FONT}'); }}"
           f"* {{ margin: 0; padding: 0; }} body {{ width: {w}px; height: {h}px; overflow: hidden; background: {bg}; }}")
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">{D.svg()}{body}</svg>'
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head><body>{svg}</body></html>'


def render(html, out, w, h, scale):
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        p = pathlib.Path(tmp) / "page.html"
        p.write_text(html)
        subprocess.run(["node", str(HERE / "render.js"), str(p), str(out), str(w), str(h), str(scale)], check=True)
    if pathlib.Path(out).stat().st_size > 450_000:
        # felt texture makes big PNGs: keep them small with a 256-colour palette (the texture hides the dithering)
        from PIL import Image
        im = Image.open(out).convert("RGB")
        im.quantize(colors=256, method=Image.Quantize.MEDIANCUT, kmeans=2, dither=Image.Dither.FLOYDSTEINBERG).save(out, optimize=True)


def items_sheet():
    cells = [("bee", place(0, 0, 1.3, bee)), ("bee happy arms", place(0, 0, 1.3, bee, arms=True, happy=True, bow=PINK)),
             ("mole", place(0, 20, 1.1, mole)), ("mole point", place(0, 20, 1.1, mole, point=-20)),
             ("fish", place(0, 0, 1.3, fish)), ("bus", place(0, 0, 1.2, bus, key=True)),
             ("penguin", place(0, 0, 1.25, penguin)), ("astronaut", place(0, 6, 1.25, astronaut)),
             ("flower house", place(0, -30, 1.0, flower_house)), ("coral", place(0, 0, 1.2, coral_house)),
             ("station", place(-6, 6, 1.2, station)), ("gate", place(0, 0, 1.4, gate, .9)),
             ("star key heart", place(-40, -20, 1.0, star_piece) + place(20, -20, 1.0, key_piece) + place(-20, 40, 1.0, heart, 16) + place(30, 40, .8, flower)),
             ("tree bush", place(-25, 0, .9, tree) + place(35, 40, .8, bush) + place(-40, 50, 1, grass_tuft)),
             ("misc", place(-40, -30, 1, snowman) + place(30, -20, .9, rocket) + place(-30, 40, 1, gem) + place(30, 50, 1, shell)),
             ("misc2", place(-30, -30, 1, planet) + place(30, -30, 1, seaweed, 50) + place(-30, 40, 1.2, sticker_book_icon) + place(40, 40, 2, bubble_ring)),
             ]
    cw, ch, per = 220, 230, 4
    o = [gingham(0, 0, 16 + per * (cw + 16), 16 + 4 * (ch + 16), "#FFFDF6", "#A9D8F2")]
    for i, (name, svg) in enumerate(cells):
        r_, c_ = divmod(i, per)
        x, y = 16 + c_ * (cw + 16), 16 + r_ * (ch + 16)
        o.append(f'<rect x="{x}" y="{y}" width="{cw}" height="{ch}" rx="18" fill="#BFE3A8" opacity=".55"/>')
        o.append(f'<g transform="translate({x + cw / 2} {y + ch / 2 - 6})">{svg}</g>')
        o.append(tx(x + cw / 2, y + ch - 10, name, 14, INK))
    w, h = 16 + per * (cw + 16), 16 + 4 * (ch + 16)
    return page("".join(o), "#FFFDF6", w, h), w, h


def main(only=None):
    global D
    if only in (None, "0"):
        D = Defs()
        html, ph = style_sheet()
        render(html, HERE / "0_畫風選擇.png", W, ph, 2)
        print("0_畫風選擇")
    for name, make in SCREENS.items():
        if only not in (None, name.split("_")[0]):
            continue
        D = Defs()
        render(make(), HERE / f"{name}.png", W, H, 2)
        print(name)
    if only in (None, "c"):
        html, w, h = contact_sheet(list(SCREENS))
        render(html, HERE / "contact_sheet.png", w, h, 1.25)
        print("contact_sheet")
    if only and only.startswith("items"):
        D = Defs()
        html, w, h = items_sheet()
        out = SCRATCH / "maze_items.png"
        render(html, out, w, h, 1.5)
        print(out)
        return


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
