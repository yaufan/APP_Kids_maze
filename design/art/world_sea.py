"""海底 sea: a little fish swims home to its pink coral house (one of the two free worlds).

    python3 build.py sea          # writes app/assets/art/<a|b|c>/sea/*.svg and checks them

Built like world_garden.py (the template): the road and ground looks per style, the palettes and
one function per picture; every function takes the style and returns pieces in its file's units.
The ground is the deep blue sea (sand patches, bubbles, seaweed and shells sewn on it); the road is
a channel of light clear water (felt: light aqua felt with teal stitches; pixel: light cyan tiles;
jelly: clear turquoise jelly).
"""
import math

import numpy as np
from shapely.geometry import Point, Polygon
from shapely.ops import unary_union

import kit
from kit import BTN, E, EYE, F, L, OBJ, R, U, crs, place, sbox, tube

# ---------------------------------------------------------------- colours (style a, felt)
ORA, ORA_T = "#FF8C42", "#FFE0C2"       # the little fish
FIN = "#F2604B"
PINK, PINK_T = "#FF9EC1", "#FFFFFF"     # mum
PFIN = "#F2709E"
YEL, YEL_T = "#FFD54F", "#FFF4C2"       # the baby
YFIN = "#FFAE3D"
CORAL, CORAL_T = "#FF6F9C", "#FFE0EC"   # coral branches
HOUSE, HOUSE_T = "#FFB3CC", "#FFFFFF"   # the coral house
DOOR, DOOR_T = "#B9467F", "#FFD3E6"
STARC = "#FFC23D"
GOLD, GOLD_T = "#FFC83D", "#FFF6CF"
SAND, SAND_T, SAND_D = "#F7E0A6", "#FFF6DC", "#E9C987"
GRN, DGRN, LGRN = "#55C98A", "#2FA06E", "#9BE3A8"
LEAF_ST = "#D2F5DE"
ROCK, ROCK_T, ROCK_D = "#93A6C4", "#DCE4F0", "#7C8FAE"
CRAB, CRAB_T = "#F45B4F", "#FFD9D2"
TURT, TURT_T, TURT_P, SKIN = "#3FA66B", "#C8EFCF", "#79CC8C", "#A9E29B"
LILAC = "#C3A2F6"
JPINK = "#FFB0D8"
BUB = "#D9F6FF"
PEARL = "#FBF8FF"
SHELL, SHELL_IN, SHELL_RIB = "#FFB8CF", "#FFE4EE", "#F0779F"
WHALE, WHALE_B = "#6AA6F2", "#D7ECFF"
OCTO = "#B48AF0"
PUFF, PUFF_D = "#FFD54A", "#F2A93B"
SEAH = "#FFB04A"
TEAL = "#3FC7C0"
WHITE = kit.WHITE
DARK, CHEEK = kit.DARK, kit.CHEEK

PIXEL = dict(
    outline="#1B2447",
    palette=["#FFFFFF", "#DDFBFF", "#A8F0FF", "#5FD8F0", "#2FB8D8", "#3A8EE0", "#2A74C4", "#1F5AA0",
             "#FFF3CF", "#FFE3A1", "#E8C070", "#C98A55", "#9A5E3A",
             "#FFD23A", "#FF9F1C", "#FF6A3D", "#E8433E", "#FF5C93", "#FFB3C8", "#B03A78",
             "#3DCB7B", "#1E9E5E", "#8CEB9A", "#B86BFF", "#D9C2FF", "#8A9BB0", "#5A6A86", "#C9D3E2"],
    map={ORA: "#FF9F1C", FIN: "#FF6A3D", PINK: "#FF8FBF", PFIN: "#FF5C93", YEL: "#FFD23A", YFIN: "#FF9F1C",
         CORAL: "#FF5C93", HOUSE: "#FFB3C8", DOOR: "#B03A78", STARC: "#FFC21F", GOLD: "#FFC21F",
         SAND: "#FFE3A1", SAND_D: "#E8C070", GRN: "#3DCB7B", DGRN: "#1E9E5E", LGRN: "#8CEB9A",
         ROCK: "#8A9BB0", ROCK_D: "#5A6A86", CRAB: "#E8433E", TURT: "#1E9E5E", TURT_P: "#3DCB7B", SKIN: "#8CEB9A",
         LILAC: "#D9C2FF", JPINK: "#FFB3C8", BUB: "#DDFBFF", PEARL: "#FFFFFF", SHELL: "#FFB3C8",
         SHELL_IN: "#FFF3CF", SHELL_RIB: "#FF5C93", WHALE: "#3A8EE0", WHALE_B: "#DDFBFF", OCTO: "#B86BFF",
         PUFF: "#FFD23A", PUFF_D: "#FF9F1C", SEAH: "#FF9F1C", TEAL: "#2FB8D8", CHEEK: "#FF8FA8",
         "#9FE6F5": "#A8F0FF", "#FFE3EE": "#FFFFFF", DARK: "#1B2447", "#B5414F": "#B03A78", "#FFA62B": "#FF9F1C"},
)
JELLY = dict(shadow="#1C2E78", map={GRN: "#5ED88A", DGRN: "#2FB872", ROCK: "#9BB0D6", SAND: "#FFE7A8",
                                    TURT: "#3DBE72", HOUSE: "#FFA9C8", CORAL: "#FF5E95"})

ROAD = {
    "a": dict(fill="#C5F2F4", stitch="#4CB2C8"),
    "b": dict(fill="#A8F0FF", speck="#7FE0F5", shade="#6CCDE8", light="#DDFBFF", border="#183C78"),
    "c": dict(body="#5FE6D5", rim="#12A49A", glow="#E8FFFB", shadow="#18307A"),
}
GROUND = {
    "a": dict(base="#3A93C6", fibres=("#52A8D6", "#3283B6")),
    "b": dict(base="#2A74C4", specks=[("#2363AE", .07), ("#3A8EE0", .045)],
              stamps=[([".oo.", "o..o", "o..o", ".oo."], {"o": "#A8F0FF"}, .7),
                      ([".o.", "o.o", ".o."], {"o": "#DDFBFF"}, 1.0),
                      (["g.", ".g", "g.", ".g", "g."], [{"g": "#3DCB7B"}, {"g": "#1E9E5E"}], 1.3),
                      ([".sss.", "sssss", ".sss."], {"s": "#E8C070"}, .5),
                      (["ppp", ".p."], [{"p": "#FFB3C8"}, {"p": "#FFF3CF"}], .7)]),
    "c": dict(top="#4C8BEF", bottom="#3360CC", swirl="#6FA7FF",
              sprinkles=("#FF8FC8", "#FFE35A", "#FFFFFF", "#7FF0D0", "#FFA37A", "#D2B6FF"), n=10),
}
STICKER = dict(fill="#F3FBFF", stitch="#9CD5E6", fill_b="#FFFFFF", fill_c="#F2FBFF")


# ================================================================ small shape helpers
def taper(pts, w0, w1=None):
    """A stroke along pts whose width goes from w0 to w1 (seaweed fronds, tentacles, tails)."""
    w1 = w0 if w1 is None else w1
    k = len(pts)
    disks = [Point(x, y).buffer(max(.4, (w0 + (w1 - w0) * i / max(1, k - 1)) / 2), quad_segs=8) for i, (x, y) in enumerate(pts)]
    return unary_union([unary_union([a, b]).convex_hull for a, b in zip(disks, disks[1:])])


def wave(x0, y0, h, amp=4.0, ph=0.0, k=9, turns=1.3):
    """Points of a wavy line going up from (x0, y0) for h units."""
    return [(x0 + amp * math.sin(ph + turns * 2 * math.pi * t), y0 - h * t) for t in np.linspace(0, 1, k)]


def smile(x, y, w, h, col=DARK, lw=2.0):
    """A thread smile: a soft curve from (x - w/2, y) dipping h at the middle."""
    return L([(x + w / 2 * u, y + h * (1 - u * u)) for u in np.linspace(-1, 1, 7)], col, lw)


def bubble(x, y, r, ring_col=WHITE, faint=True):
    """A bubble: a ring with a glint (felt), a pale pixel disc (b), a see-through gummy ball (c).
    faint: a see-through fill inside the felt ring (left out on the big ground, to keep it small)."""
    ring = E(x, y, r).difference(E(x, y, r - max(1.3, r * .24)))
    return [F(E(x, y, r), BUB, lift=0, fuzz=False, shade=False, op=.28, only="a" if faint else "-"),
            F(ring, ring_col, lift=.3, fuzz=False, shade=False, only="a"),
            F(E(x, y, r), BUB, lift=.3, fuzz=False, only="b"),
            F(E(x, y, r), "#E2F8FF" if ring_col == WHITE else "#CBEFFF", lift=0, op=.62 if ring_col == WHITE else .85, only="c"),
            F(E(x - r * .36, y - r * .36, r * .24, r * .17, rot=-40), WHITE, lift=0, fuzz=False, only="a")]


def bubbles(pts, ring_col=WHITE, faint=True):
    o = []
    for x, y, r in pts:
        o += OBJ(bubble(x, y, r, ring_col, faint), shadow=0)
    return o


def scallop(r, col=SHELL, rib=SHELL_RIB, k=7, inner=None, ribs=True):
    """A scallop shell: hinge at (0, 0), the scalloped edge up (radius r)."""
    pts = [(0, -r * .08)]
    m = 70
    for i in range(m + 1):
        t = i / m
        a = math.radians(202 + 136 * t)
        rr = r * (.9 + .1 * abs(math.sin(math.pi * k * t)))
        pts.append((rr * math.cos(a), rr * math.sin(a)))
    fan = kit.soft(kit.G(pts), r * .05)
    ears = R(-r * .3, -r * .16, r * .6, r * .2, r * .06)
    o = [F(U(fan, ears), col, st=WHITE if r > 14 else None, inset=2.2 if r > 25 else 1.6)]
    if inner:
        o.append(F(kit.soft(kit.G(pts).buffer(-r * .2), r * .05), inner, lift=0, fuzz=False))
    if ribs:
        for j in range(1, k):
            a = math.radians(202 + 136 * j / k)
            o.append(L([(r * .16 * math.cos(a), r * .16 * math.sin(a) - r * .05),
                        (r * .8 * math.cos(a), r * .8 * math.sin(a))], rib, max(1.0, r * .055)))
    return o


# ================================================================ characters and things (round (0, 0))
def fish(body=ORA, body_st=ORA_T, fin=FIN, stripe=WHITE, happy=False, bow=None, stripes=True, fin_st="#FFD9CF"):
    """The little fish, facing right, about 84 x 66 units round (0, 0) (the body centre is (4, 0))."""
    o = []
    tail = kit.G(crs([(-20, -4), (-37, -21), (-47, -18), (-40, 0), (-47, 18), (-37, 21), (-20, 4)], 6))
    o.append(F(tail, fin, st=fin_st, inset=2.4))
    dors = kit.G(crs([(-17, -15), (-10, -31), (4, -36), (15, -27), (12, -15)], 6))
    o.append(F(dors, fin, st=fin_st, inset=2.2))
    bel = kit.G(crs([(-10, 17), (-5, 30), (6, 30), (9, 18)], 6))
    o.append(F(bel, fin, lift=.6))
    b = E(4, 0, 31, 27)
    o.append(F(b, body, st=body_st))
    if stripes:
        band = E(-40, 0, 50, 50).difference(E(-40, 0, 43, 43)).intersection(b)
        o.append(F(band, stripe, lift=0))
        band2 = E(-70, 0, 46, 46).difference(E(-70, 0, 41, 41)).intersection(b)
        o.append(F(band2, stripe, lift=0))
    o.append(F(E(-1, 9, 9.5, 5.5, rot=28), fin, st=fin_st, inset=1.6, lift=.6))
    if happy:
        o.append(L([(12.5, -5), (17.5, -10.5), (22.5, -5)], DARK, 2.6))
    else:
        o.append(EYE(18, -6, 5.6, look=(.8, 0)))
    o.append(F(E(14, 8, 4.2, 3.2), CHEEK, lift=0))
    if happy:
        o.append(F(kit.G(crs([(23, 5), (27.5, 5), (32, 5), (30, 10), (25, 10)], 6)), "#B5414F", lift=0, fuzz=False))
    else:
        o.append(smile(27.6, 6.2, 8, 3.6))
    if bow:
        o.append(F(E(-2, -27, 8, 5.6, rot=-25), bow, st="#FFFFFF", inset=2.0))
        o.append(F(E(13, -27, 8, 5.6, rot=25), bow, st="#FFFFFF", inset=2.0))
        o.append(F(E(5.5, -27, 3.6), kit.dk(bow, .15), lift=.5, fuzz=False))
    return o


def coral_branches(col=CORAL, st=CORAL_T):
    """Three coral fingers with side branches, their feet near y = -6 (behind the house)."""
    lines = [([(-22, -6), (-26, -32), (-21, -50)], 11), ([(-25, -28), (-36, -38), (-39, -49)], 8.5),
             ([(0, -10), (1, -42), (-1, -62)], 12), ([(1, -38), (12, -48), (14, -57)], 8.5),
             ([(22, -6), (26, -33), (23, -50)], 11), ([(25, -27), (36, -36), (39, -47)], 8.5)]
    g = U(*[tube(crs(p, 6, closed=False), w) for p, w in lines])
    o = [F(g, col, st=st, inset=2.0)]
    for x, y in ((-21, -50), (-39, -49), (-1, -62), (14, -57), (23, -50), (39, -47)):
        o.append(F(E(x, y + 1.5, 2.6), "#FFE3EE", lift=0, fuzz=False))
    return o


def coral_house(door=True):
    """The fish's home: a pink coral house with coral fingers on top and a round door; the
    house body is centred at (0, 0) (about 90 x 106 units with the coral)."""
    o = coral_branches()
    body = kit.soft(U(E(0, 0, 38, 30), R(-38, 0, 76, 33, 12)), 3)
    o.append(F(body, HOUSE, st=HOUSE_T, inset=3.2))
    zz = [(-31 + 6.2 * i, -13 if i % 2 else -7) for i in range(11)]
    o.append(L(zz, "#FF7FA6", 2.2))
    for x, y in ((-26, -20), (-9, -24), (9, -24), (26, -20), (-31, 25), (31, 25), (-17, -1), (17, -1)):
        o.append(F(E(x, y, 2.4), "#FFE3EE", lift=0, fuzz=False))
    if door:
        o.append(F(R(-12, 3, 24, 30, 12), DOOR, st=DOOR_T, inset=1.8))
        o.append(F(E(-4.5, 10, 3.4, 2.4, rot=-35), "#D978A6", lift=0, fuzz=False, only="ac"))
        o.append(BTN(6, 20, 2.4, GOLD))
        for sgn in (-1, 1):
            o.append(F(E(sgn * 25, 9, 6.6), WHITE, lift=.6, fuzz=False))
            o.append(F(E(sgn * 25, 9, 4.4), "#9FE6F5", lift=0, fuzz=False))
    o.append(F(kit.soft(U(E(0, 34, 46, 7.5)), 2).difference(body), SAND, lift=.5))
    return o


def seaweed(x0, y0, h, col=GRN, amp=4.5, ph=0.0, w=9.0, st=LEAF_ST):
    """One seaweed frond rising from (x0, y0), h tall, getting thinner at the top."""
    g = taper(wave(x0, y0, h, amp, ph), w, w * .45)
    return [F(g, col, st=st if w > 7 else None, inset=1.8)]


def sand_mound(x, y, rx, ry=7.0):
    return [F(E(x, y, rx, ry), SAND, st=SAND_T, inset=1.8, lift=.5)]


def crab(col=CRAB, happy=False):
    """A red crab, front view, round (0, 0): body 48 x 34, claws up."""
    o = []
    dk = kit.dk(col, .18)
    for sgn in (-1, 1):
        for i in range(3):
            o.append(L([(sgn * 16, 5 + i * 5), (sgn * 27, 7 + i * 6), (sgn * 31, 15 + i * 5)], dk, 3.2))
        o.append(L([(sgn * 15, -4), (sgn * 24, -14)], col, 4.4))
        claw = E(0, 0, 10, 9).difference(kit.G([(0, 1), (13, -9), (13, 3)]))
        o += place([F(claw, col, st="#FFFFFF", inset=1.4)], sgn * 28, -21, rot=-62 if sgn > 0 else -118)
        o.append(L([(sgn * 7, -13), (sgn * 9, -23)], col, 3.0))
        o.append(F(E(sgn * 9.5, -26, 5.2), WHITE, lift=.5, fuzz=False))
        if happy:
            o.append(L([(sgn * 9.5 - 3, -25), (sgn * 9.5, -28.5), (sgn * 9.5 + 3, -25)], DARK, 1.8))
        else:
            o.append(EYE(sgn * 9.5 + .6, -25.6, 3.0))
    o.append(F(E(0, 0, 24, 17), col, st=CRAB_T, inset=2.4))
    for sgn in (-1, 1):
        o.append(F(E(sgn * 13, 3, 3.6, 2.8), CHEEK, lift=0))
    o.append(smile(0, 2.4, 9.5, 3.6))
    return o


def turtle():
    """A small sea turtle swimming right, round (0, 0), about 84 x 50."""
    o = [F(E(-24, 10, 11, 5, rot=-30), SKIN, lift=.6),
         F(kit.G(crs([(-30, 2), (-38, 4), (-32, 7)], 4)), SKIN, lift=.5, fuzz=False),
         F(E(10, 13, 16, 6.2, rot=30), SKIN, st="#FFFFFF", inset=1.4)]
    o.append(F(E(31, -4, 12, 10.5), SKIN, st="#FFFFFF", inset=1.8))
    shell = kit.soft(E(-2, 2, 29, 22).intersection(sbox(-40, -30, 40, 7)), 2.5)
    o.append(F(shell, TURT, st=TURT_T, inset=2.4))
    o.append(F(R(-29, 4, 55, 6, 3), kit.dk(TURT, .15), lift=.5))
    for x, y, rx, ry in ((-2, -9, 8.5, 6.5), (-17, -2, 6.5, 5.5), (13, -2, 6.5, 5.5)):
        o.append(F(E(x, y, rx, ry), TURT_P, lift=0, fuzz=False))
    o.append(F(E(-4, 18, 9, 4, rot=-25), SKIN, lift=.6))
    o.append(EYE(34, -7, 3.4))
    o.append(F(E(31, 0, 2.8, 2.1), CHEEK, lift=0, fuzz=False))
    o.append(smile(38, 1.2, 6.4, 2.4, lw=1.6))
    return o


def jellyfish(col=LILAC, tent=JPINK, happy=False):
    """A jellyfish, round (0, 0): a dome 48 wide and wavy tentacles below."""
    o = []
    for i, x in enumerate((-14, -5, 5, 14)):
        o.append(F(taper(wave(x, 32, 26, 3.2, i * 1.3 + 3.1, 9, 1.0)[::-1], 2.6, 4.6), tent, lift=.5))
    dome = E(0, 2, 24, 22).intersection(sbox(-30, -30, 30, 4))
    frill = U(*[E(x, 4, 4.4, 3.8) for x in (-18, -9, 0, 9, 18)])
    o.append(F(U(dome, frill), col, st="#FFFFFF", inset=2.2))
    o.append(F(E(-8, -11, 4.6, 3, rot=-30), "#EADDFF", lift=0, fuzz=False))
    if happy:
        for x in (-7, 7):
            o.append(L([(x - 3.4, -4), (x, -7.6), (x + 3.4, -4)], DARK, 2.0))
    else:
        o.append(EYE(-7, -5, 3.4))
        o.append(EYE(7, -5, 3.4))
    for x in (-13, 13):
        o.append(F(E(x, 0, 3, 2.2), CHEEK, lift=0, fuzz=False))
    o.append(smile(0, .2, 6.6, 2.6, lw=1.6))
    return o


def octopus():
    """A purple octopus, round (0, 0) (head 56 wide, curly arms below)."""
    o = []
    arms = [(-22, -1, 1), (-13, 1, 1), (-4, 2, 1), (4, 2, -1), (13, 1, -1), (22, -1, -1)]
    for i, (x, y, s) in enumerate(arms):
        out = -1 if x < 0 else 1
        pts = [(x, y + 10), (x + out * 6, y + 22), (x + out * 3, y + 34), (x + out * 9, y + 40), (x + out * 14, y + 35)]
        o.append(F(taper(crs(pts, 5, closed=False), 10, 4.5), OCTO, lift=.6))
        o.append(F(E(x + out * 5.5, y + 25, 1.8), "#E6D6FF", lift=0, fuzz=False))
    o.append(F(kit.soft(U(E(0, -12, 30, 28), R(-26, -6, 52, 20, 9)), 3), OCTO, st="#FFFFFF", inset=2.6))
    o.append(F(E(-12, -26, 7, 4.4, rot=-30), "#D9C6FF", lift=0, fuzz=False))
    o.append(EYE(-10, -4, 4.4))
    o.append(EYE(10, -4, 4.4))
    for x in (-17, 17):
        o.append(F(E(x, 5, 3.8, 2.8), CHEEK, lift=0))
    o.append(smile(0, 4.4, 10, 3.8))
    return o


def starfish(col="#FF8A65", dot="#FFD0BE", face=True):
    g = kit.soft(kit.G(kit.star_pts(44, 21, 0, 2, 5, -90)), 6)
    o = [F(g, col, st="#FFFFFF", inset=2.6)]
    for i in range(5):
        a = math.radians(-90 + 72 * i)
        for rr, r0 in ((24, 2.4), (33, 1.8)):
            o.append(F(E(rr * math.cos(a), 2 + rr * math.sin(a), r0), dot, lift=0, fuzz=False))
    if face:
        o.append(EYE(-6, -1, 3.4))
        o.append(EYE(6, -1, 3.4))
        o.append(F(E(-11, 6, 2.8, 2.1), CHEEK, lift=0, fuzz=False))
        o.append(F(E(11, 6, 2.8, 2.1), CHEEK, lift=0, fuzz=False))
        o.append(smile(0, 5.6, 7, 2.8, lw=1.6))
    return o


def seahorse():
    """A seahorse facing right, round (0, 0), about 56 x 96: a crowned head with a long snout,
    a round belly and a curled tail."""
    spine = crs([(-1, -30), (-5, -17), (-2, -2), (5, 11), (4, 23), (-4, 31), (-14, 29), (-17, 20), (-11, 15)], 8, closed=False)
    knots = [(0, 15), (.12, 13), (.36, 25), (.55, 19), (.78, 9), (1, 5.5)]
    k = len(spine)
    ws = [float(np.interp(i / (k - 1), [a for a, _ in knots], [b for _, b in knots])) for i in range(k)]
    disks = [Point(x, y).buffer(w / 2, quad_segs=8) for (x, y), w in zip(spine, ws)]
    body = unary_union([unary_union([a, b]).convex_hull for a, b in zip(disks, disks[1:])])
    fin = kit.G(crs([(-9, -14), (-22, -12), (-25, -2), (-20, 6), (-8, 2)], 5))
    o = [F(fin, "#FFD27A", st="#FFFFFF", inset=1.6, lift=.6)]
    for x, y in ((-7, -48), (-1, -50.5), (5, -48)):
        o.append(F(E(x, y, 3.2), "#FF8F3A", lift=.4, fuzz=False))
    head = U(E(1, -38, 13, 11.5), tube([(6, -37), (24, -33)], 9.5))
    o.append(F(U(body, head), SEAH, st="#FFFFFF", inset=2.2))
    for y in (-6, 1, 8, 15, 22):
        o.append(L([(2 + (y - 8) * .05, y - 1), (11 - abs(y - 8) * .22, y + 1)], "#FFE0A0", 2.0))
    o.append(EYE(4, -40, 4.0))
    o.append(F(E(1, -31, 3.2, 2.4), CHEEK, lift=0, fuzz=False))
    o.append(smile(14, -32.2, 5, 1.8, lw=1.5))
    return o


def whale():
    """A friendly blue whale facing right with a water spout, round (0, 0), about 120 x 90."""
    o = []
    for pts in (((14, -30), (10, -42), (2, -48)), ((16, -30), (17, -46), (22, -52)), ((18, -30), (26, -42), (34, -44))):
        o.append(L(list(pts), "#8EDCF7", 3.4))
    for x, y in ((0, -50), (24, -55), (36, -45)):
        o.append(F(kit.G(kit.tf([(0, -3.6), (2.6, 1), (0, 3.4), (-2.6, 1)], x, y)), "#8EDCF7", lift=0, fuzz=False))
    tail = kit.G(crs([(-38, 6), (-52, -6), (-62, -14), (-56, -2), (-62, 10), (-48, 6), (-36, 14)], 6))
    o.append(F(tail, WHALE, st="#FFFFFF", inset=2.0))
    body = kit.soft(U(E(4, 4, 42, 30), E(-26, 8, 18, 12)), 4)
    o.append(F(body, WHALE, st="#FFFFFF", inset=2.6))
    o.append(F(body.intersection(E(8, 30, 40, 16)), WHALE_B, lift=0))
    for x in (0, 9, 18):
        o.append(L([(x, 18), (x + 1, 26)], "#A8CDF0", 1.6))
    o.append(F(E(-6, 14, 9, 5, rot=30), "#5592E0", lift=.6))
    o.append(EYE(26, -2, 4.4))
    o.append(F(E(24, 8, 4, 3), CHEEK, lift=0))
    o.append(L([(31, 8.5), (34, 11.4), (37.5, 12), (41, 9.4)], DARK, 2.0))
    return o


def puffer():
    """A round yellow pufferfish facing right with soft spikes, round (0, 0)."""
    sp = []
    for i in range(14):
        a = math.radians(360 * i / 14 + 8)
        x, y = 30 * math.cos(a), 30 * math.sin(a)
        sp.append(kit.G([(x - 4.5 * math.sin(a), y + 4.5 * math.cos(a)), (x + 4.5 * math.sin(a), y - 4.5 * math.cos(a)),
                         (37.5 * math.cos(a), 37.5 * math.sin(a))]).buffer(1.2))
    o = [F(kit.G(crs([(-28, -2), (-42, -12), (-44, 12), (-28, 4)], 5)), PUFF_D, lift=.6)]
    o.append(F(U(*sp), PUFF_D, lift=.6))
    body = E(0, 0, 32)
    o.append(F(body, PUFF, st="#FFFFFF", inset=2.6))
    o.append(F(body.intersection(E(0, 26, 30, 18)), "#FFF1B5", lift=0))
    for x, y in ((-14, -14), (-4, -22), (-18, 2), (6, -16)):
        o.append(F(E(x, y, 2.2), PUFF_D, lift=0, fuzz=False))
    o.append(F(E(-6, 8, 8, 5, rot=25), PUFF_D, lift=.6))
    o.append(EYE(12, -6, 5))
    o.append(F(E(8, 7, 4, 3), CHEEK, lift=0))
    o.append(F(E(22, 6, 3.8, 4.2), "#B5414F", lift=0, fuzz=False))
    return o


def coral_tree(col=CORAL, st=CORAL_T):
    """A branching coral, its foot at (0, 0), about 56 wide and 62 tall."""
    lines = [([(0, 0), (-2, -26), (-12, -42), (-14, -56)], 9), ([(-2, -24), (8, -38), (10, -54)], 8),
             ([(-1, -12), (-16, -22), (-24, -36)], 7.5), ([(0, -10), (16, -18), (24, -30)], 7.5),
             ([(9, -36), (18, -42), (22, -50)], 6)]
    g = U(*[tube(crs(p, 6, closed=False), w) for p, w in lines])
    o = [F(g, col, st=st, inset=1.8)]
    for x, y in ((-14, -56), (10, -54), (-24, -36), (24, -30), (22, -50)):
        o.append(F(E(x, y + 1.2, 2.2), "#FFE3EE", lift=0, fuzz=False))
    return o


def fan_coral(col="#FFB347"):
    pts = [(0, 0)] + [(26 * math.cos(math.radians(a)), -4 + 26 * math.sin(math.radians(a))) for a in np.linspace(205, 335, 14)]
    o = [F(kit.soft(kit.G(pts), 3), col, st="#FFF1D6", inset=1.8)]
    for a in np.linspace(222, 318, 5):
        o.append(L([(0, -2), (20 * math.cos(math.radians(a)), -4 + 20 * math.sin(math.radians(a)))], kit.dk(col, .2), 1.6))
    return o


def heart(s=12, col=PINK):
    return [F(kit.heart_pts(0, 0, s), col, st="#FFFFFF", inset=1.6 if s < 12 else 2.2)]


# ================================================================ the files
def hero(st):
    return place(OBJ(fish()), 54, 51, 1.04)


def home(st):
    return place(OBJ(coral_house()), 50, 56, .8)


def hug_fin(fin, fin_st):
    """The little fish's front fin stretched out to hug (drawn over the one it hugs)."""
    return [F(E(37, 16, 15, 6, rot=-14), fin, st=fin_st, inset=1.4, lift=.8)]


def family(st):
    """Home at last: the little fish hugs mum (pink, with a bow) in front of the coral house; the
    baby swims up to them."""
    mound = kit.G(crs([(24, 340), (80, 306), (200, 298), (320, 306), (376, 340), (320, 370), (200, 380), (80, 370)], 6))
    o = OBJ([F(mound, SAND, st="#FFFFFF", inset=4)])
    o += OBJ(place(coral_house(), 200, 134, 2.0))
    o += OBJ(place(seaweed(0, 0, 84, GRN, 5, 0, 13) + seaweed(16, 4, 60, DGRN, 4, 2, 11), 34, 338))
    o += OBJ(place(seaweed(0, 0, 74, DGRN, 5, 1, 12) + seaweed(-16, 4, 52, GRN, 4, 3, 10), 366, 338))
    mum = dict(dx=262, dy=288, s=1.8, flip=True)
    kid = dict(dx=140, dy=300, s=1.62, rot=-5)
    o += OBJ(place(fish(PINK, PINK_T, PFIN, happy=True, bow="#FFD23A", fin_st="#FFE0EC"), **mum))
    o += OBJ(place(fish(happy=True), **kid))
    o += OBJ(place(hug_fin(FIN, "#FFD9CF"), **kid), shadow=.5)
    o += OBJ(place(fish(YEL, YEL_T, YFIN, happy=True, stripes=False, fin_st="#FFF0C8"), 338, 196, .78, rot=-8, flip=True))
    for x, y, s_, c in ((200, 232, 14, "#FF6F9C"), (66, 214, 10, PINK)):
        o += OBJ(place(heart(s_, c), x, y))
    o += bubbles([(46, 60, 12), (72, 100, 7.5), (354, 62, 10), (330, 104, 6.5)], "#8FD3EE")
    return o


def star(st):
    g = kit.soft(kit.G(kit.star_pts(42, 22, 50, 53, 5, -90)), 4.5)
    o = [F(g, STARC, st="#FFFFFF", inset=3.4)]
    for i in range(5):
        a = math.radians(-90 + 72 * i)
        o.append(F(E(50 + 25 * math.cos(a), 53 + 25 * math.sin(a), 2.6), "#FFA62B", lift=0, fuzz=False, only="ac"))
    o.append(F(E(50, 53, 3.2), "#FFA62B", lift=0, fuzz=False, only="ac"))
    o.append(F(E(38, 39, 4.2, 2.6, rot=-35), "#FFFFFF", lift=0, fuzz=False, op=.85))
    return OBJ(o)


def key(st):
    """A golden key whose handle is a pink scallop shell."""
    shaft = U(R(-4, -5.5, 46, 11, 4.5), R(25, 2, 8, 13, 3), R(35.5, 2, 8, 10, 3))
    o = [F(shaft, GOLD, st=GOLD_T, inset=2.0)]
    o += place(scallop(23, "#FF8DB4", "#FFFFFF", k=6), -2, 0, rot=-90)
    o.append(BTN(-1, 0, 4, GOLD))
    return place(OBJ(o), 50, 54, 1.16, rot=-30)


def gate(st):
    """A little gate of seaweed bars between two coral posts, with a padlock, across a left-right road."""
    o = []
    for y in (29, 69):
        o.append(F(R(24, y, 52, 8, 4), "#FF9DBD", lift=.6))
    for i, x in enumerate((36, 50, 64)):
        g = taper(wave(x, 91, 74, 2.0, 0.0, 13, 1.5), 8.5, 7)
        o.append(F(g, (GRN, DGRN, GRN)[i], st=LEAF_ST, inset=1.5))
    for x in (22, 78):
        o.append(F(R(x - 6, 17, 12, 77, 6), CORAL, st=CORAL_T, inset=1.8))
        o.append(F(E(x, 13, 8.5), CORAL, lift=.6))
        o.append(F(E(x - 2.6, 10.4, 2.8, 1.9, rot=-30), "#FFE3EE", lift=0, fuzz=False))
        for y in (40, 60, 80):
            o.append(F(E(x, y, 1.9), "#FFE3EE", lift=0, fuzz=False, only="ac"))
    o.append(F(tube(crs([(42, 52), (42, 43), (50, 37), (58, 43), (58, 52)], 6, closed=False), 4.6), "#B8BCC8", lift=.6))
    o.append(F(R(38, 48, 24, 20, 5.5), GOLD, st=GOLD_T, inset=1.8))
    o.append(F(U(E(50, 55.5, 3), R(48.7, 55.5, 2.6, 7, 1)), DARK, lift=0, fuzz=False, only="ac"))
    o.append(L([(50, 54), (50, 62)], DARK, 2.0, only="b"))
    return OBJ(o)


def deco_seaweed(st):
    o = sand_mound(0, 34, 34, 7)
    o += seaweed(-16, 34, 62, DGRN, 4.5, 0, 10)
    o += seaweed(14, 34, 50, GRN, 4, 2.2, 10)
    o += seaweed(0, 36, 74, LGRN, 5, 1, 11)
    return place(OBJ(o) + bubbles([(30, -24, 5), (36, -38, 3.6)]), 50, 54, 1.0)


def deco_clam(st):
    o = sand_mound(0, 22, 40, 8)
    o += place(scallop(32, SHELL, SHELL_RIB, k=7, inner=SHELL_IN, ribs=False), 0, 14)
    o.append(F(E(0, -2, 10.5), PEARL, st=None, lift=1))
    o.append(F(E(-3.5, -5.5, 3.2, 2.4, rot=-30), WHITE, lift=0, fuzz=False, cols={"b": "#DDFBFF"}))
    bowl = kit.soft(E(0, 10, 33, 15).intersection(sbox(-40, 9, 40, 40)), 2)
    o.append(F(bowl, SHELL, st="#FFFFFF", inset=2))
    for x in (-18, -6, 6, 18):
        o.append(L([(x, 12), (x * .55, 22)], SHELL_RIB, 1.6))
    return place(OBJ(o) + bubbles([(28, -24, 4.4), (34, -36, 3)]), 50, 58, 1.0)


def deco_crab(st):
    rock = kit.soft(U(E(-8, 14, 33, 20), E(16, 18, 24, 15)).intersection(sbox(-50, -20, 50, 30)), 3)
    o = [F(rock, ROCK, st=ROCK_T, inset=2.4)]
    for x, y, r in ((-24, 18, 3.6), (22, 22, 3), (4, 24, 2.4)):
        o.append(F(E(x, y, r), ROCK_D, lift=0, fuzz=False))
    o += place(crab(), 2, -6, .66)
    return place(OBJ(o), 50, 54, 1.0)


def deco_coral(st):
    o = sand_mound(0, 34, 38, 7)
    o += place(fan_coral("#FFB347"), 18, 34, .9)
    o += place(coral_tree("#FF6F7F", "#FFE0E4"), -8, 35, 1.0)
    o += place(coral_tree(LILAC, "#F1E8FF"), 24, 36, .52)
    return place(OBJ(o), 50, 56, .98)


def deco_turtle(st):
    return place(OBJ(turtle()) + bubbles([(-40, -20, 4.4), (-46, -32, 3)]), 52, 54, .98)


def deco_jelly(st):
    return place(OBJ(jellyfish()) + bubbles([(30, -22, 6), (36, 2, 4), (-30, -16, 4.4), (-28, 14, 3)]), 50, 44, 1.0)


# ---------------------------------------------------------------- stickers (200 x 200, the kit adds the round sticker)
def s_fish(st):
    return place(OBJ(fish()) + bubbles([(34, -26, 5.5), (25, -38, 3.6)]), 104, 104, 1.6)


def s_octopus(st):
    return place(OBJ(octopus()), 100, 98, 1.85)


def s_crab(st):
    return place(OBJ(crab()), 100, 108, 2.0)


def s_starfish(st):
    return place(OBJ(starfish()), 100, 100, 1.72)


def s_seahorse(st):
    return place(OBJ(seahorse()) + bubbles([(32, -14, 4.6), (38, -26, 3.2)]), 100, 115, 1.5)


def s_shell(st):
    o = place(scallop(52, SHELL, SHELL_RIB, k=8, inner=SHELL_IN), 0, 26)
    o.append(F(E(0, 4, 11), PEARL, lift=1))
    o.append(F(E(-3.6, .5, 3.4, 2.4, rot=-30), WHITE, lift=0, fuzz=False, cols={"b": "#DDFBFF"}))
    return place(OBJ(o), 100, 112, 1.3)


def s_whale(st):
    return place(OBJ(whale()), 104, 112, 1.22)


def s_jellyfish(st):
    return place(OBJ(jellyfish()) + bubbles([(30, -22, 5), (-32, -4, 4)]), 100, 92, 1.9)


def s_turtle(st):
    return place(OBJ(turtle()), 98, 102, 1.66)


def s_puffer(st):
    return place(OBJ(puffer()), 102, 100, 1.6)


# ---------------------------------------------------------------- the home-page card (300 x 200)
def card(st):
    line = crs([(-40, 168), (40, 160), (110, 132), (170, 108), (230, 102), (340, 104)], 10, closed=False)
    road = tube(line, 48, cap="flat")
    o = [kit.ground_piece(WORLD, st)]
    o += OBJ(place(seaweed(0, 0, 50, DGRN, 4, 0, 9) + seaweed(12, 2, 38, GRN, 3.5, 2, 8), 20, 108))
    o += OBJ(place(coral_tree("#FF6F7F", "#FFE0E4"), 128, 76, .62))
    o += OBJ(place(jellyfish(), 40, 44, .62))
    o += OBJ(place(scallop(14, SHELL, SHELL_RIB, k=6), 196, 186))
    o += OBJ(place(seaweed(0, 0, 40, GRN, 4, 1, 8), 286, 194))
    o += bubbles([(84, 30, 6), (96, 50, 4), (176, 40, 5), (16, 140, 4)])
    o.append(kit.road_piece(WORLD, st, road, width=48))
    o += OBJ(place([F(kit.soft(kit.G(kit.star_pts(17, 9, 0, 0, 5, -90)), 2), STARC, st="#FFFFFF", inset=1.8)], 152, 118))
    o += OBJ(place(coral_house(), 252, 74, .6))
    o += OBJ(place(fish(), 64, 150, .64))
    o += bubbles([(98, 136, 4.6), (108, 124, 3)])
    return o


def bits(st):
    """Things sewn on the felt sea floor (a), a few see-through bubbles on the candy sea (c)."""
    rnd = kit.random.Random(23)
    o = []
    if st == "c":
        for i in range(14):
            x, y, r = rnd.uniform(20, 580), rnd.uniform(20, 780), rnd.uniform(4, 8)
            o += OBJ(bubble(x, y, r), shadow=0)
        return o
    if st != "a":
        return []
    for i in range(7):     # sand patches, sewn on
        x, y = rnd.uniform(30, 570), rnd.uniform(30, 770)
        g = kit.G(crs([(x + math.cos(t) * rnd.uniform(28, 38) * 1.3, y + math.sin(t) * rnd.uniform(15, 22))
                       for t in np.linspace(0, 2 * math.pi, 8, endpoint=False)], 5))
        o.append(F(g, "#EAD49C", st="#FFF3D2", inset=2.6, lift=.4, shade=False, fuzz=False))
    for i in range(30):
        x, y = rnd.uniform(20, 580), rnd.uniform(20, 780)
        kind = i % 4
        if kind == 0:     # a seaweed tuft
            o += OBJ(seaweed(x - 5, y, 24, "#2F9D78", 2.4, i, 5.5) + seaweed(x + 4, y, 17, "#4DBB8E", 2.2, i + 2, 5), shadow=.5)
        elif kind == 1:   # bubbles
            o += bubbles([(x, y, 5.4), (x + 7, y - 12, 3.6), (x + 2, y - 21, 2.6)][:2 + (i // 4) % 2], faint=False)
        elif kind == 2:   # a little shell
            o += OBJ(place(scallop(9, ("#FFD0DE", "#FFF0D6", "#E8DDFF")[i % 3], "#E59AB3", k=5), x, y, rot=rnd.uniform(-30, 30)), shadow=.5)
        else:             # French knots (pebbles)
            o.append(F(E(x, y, 3.2), ("#BFE6F5", "#FFE9B8")[i % 2], lift=.5, fuzz=False))
            o.append(F(E(x + 7, y + 3, 2.6), ("#FFE9B8", "#BFE6F5")[i % 2], lift=.5, fuzz=False))
    return o


class _SeaWorld(kit.World):
    """kit.World with one local workaround. The felt road's edge hairs (kit._hairs) are random per
    tile and, unlike the outline wobble, do not fade out at the tile's edge, so where the road's
    side meets the tile edge two neighbouring tiles can differ by a few hairs. With this world's
    file names the default random keys gave tiles 11 | 10 a seam score of 0.8 (`build.py seams`
    allows 0.6). The felt tiles therefore get FELT_TILE_KEY empty, invisible markers in front of
    the road, which only moves the road's random key (0.4 at worst, like every other pair)."""
    FELT_TILE_KEY = 3

    def files(self, style):
        out = super().files(style)
        if style == "a":
            for m in range(1, 16):
                kind, pieces = out[f"tile_{m}"]
                pad = [kit.Piece("obj", Polygon(), "#000000", lift=0) for _ in range(self.FELT_TILE_KEY)]
                out[f"tile_{m}"] = (kind, pad + pieces)
        return out


WORLD = _SeaWorld(
    "sea", "海底",
    road=ROAD, ground=GROUND, pixel=PIXEL, jelly=JELLY, bits=bits, sticker=STICKER,
    hero=hero, home=home, family=family, star=star, key=key, gate=gate,
    deco=[deco_seaweed, deco_clam, deco_crab, deco_coral, deco_turtle, deco_jelly],
    stickers=[s_fish, s_octopus, s_crab, s_starfish, s_seahorse, s_shell, s_whale, s_jellyfish, s_turtle, s_puffer],
    card=card,
)
