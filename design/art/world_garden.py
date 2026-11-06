"""花園 garden: a little bee goes home to the flower. The template for every other world.

    python3 build.py garden       # writes app/assets/art/<a|b|c>/garden/*.svg and checks them

A world module defines WORLD (a kit.World): the road and ground looks per style, the palettes, and
one function per picture. Each function takes the style and returns pieces in its file's units
(see kit.py). Characters are drawn round (0, 0) at a comfortable size and placed with kit.place().
"""
import math

import numpy as np

import kit
from kit import BTN, E, EYE, F, L, OBJ, R, U, crs, place, sbox, star_shape, tube

# ---------------------------------------------------------------- colours (style a, felt)
YEL, YEL_T = "#FFD54F", "#C9951C"
GOLD, GOLD_T = "#FFC83D", "#FFF6CF"
ORA = "#FFA84C"
CORAL = "#FF8A73"
PINK = "#FF9EC1"
RED = "#F2665C"
LILAC = "#B7A3F0"
SKY = "#8FD3F4"
BLUE = "#7CC6F2"
GRN, DGRN = "#8DCF6E", "#5DAA5A"
LEAF_ST = "#D4F0C2"
BRN, BRN_T = "#9A6B4F", "#D9B08F"
WOOD, WOOD_T = "#E5A869", "#FFE6C2"
COCOA = "#6B4A3B"
CREAM = "#FFF0CF"
WHITE = kit.WHITE
WING, WING_T = "#EAF6FF", "#93C9E8"
DARK, CHEEK = kit.DARK, kit.CHEEK

PIXEL = dict(
    outline="#2B2340",
    palette=["#FFFFFF", "#FFF3CF", "#FFE3A1", "#F0C478", "#FFD23A", "#FF9F1C", "#FF6FA8", "#FFB3C8", "#FF4D5E",
             "#B86BFF", "#D9C2FF", "#8EE3FF", "#4FA8E8", "#7BDB6E", "#3DB55B", "#2A8F47", "#1D6B3A", "#C98A55",
             "#9A5E3A", "#5A3828", "#E8B898"],
    map={WING: "#CDEFFF", CHEEK: "#FF8FA8", YEL: "#FFD23A", GOLD: "#FFC21F", PINK: "#FF8FBF", COCOA: "#5A3828",
         DGRN: "#7BDB6E", GRN: "#B2EC8C", "#A3D982": "#9BE47E", "#7CC261": "#7BDB6E"},
)
JELLY = dict(shadow="#C2407A", map={GRN: "#7FD86A", DGRN: "#4FBF5A", BRN: "#B07850"})

ROAD = {
    "a": dict(fill="#FFF1CC", stitch="#C99A62"),
    "b": dict(fill="#FFE3A1", speck="#F0C478", shade="#EDBA62", light="#FFF3CF", border="#1D6B3A"),
    "c": dict(body="#6FD6F7", rim="#2FA6D8", glow="#E2FAFF", shadow="#C2407A"),
}
FLOWERS_PX = [{"p": "#FF6FA8", "y": "#FFD23A"}, {"p": "#FFFFFF", "y": "#FFD23A"}, {"p": "#D9C2FF", "y": "#FF9F1C"}]
GROUND = {
    "a": dict(base="#A3D982", fibres=("#B6E39B", "#90C870")),
    "b": dict(base="#3DB55B", specks=[("#2A8F47", .07), ("#7BDB6E", .045)],
              stamps=[([".p.", "pyp", ".p."], FLOWERS_PX, 1.6), (["l.l", ".l."], {"l": "#7BDB6E"}, 2.0)]),
    "c": dict(top="#FFE4F0", bottom="#FFD3E6", swirl="#FFF2F8",
              sprinkles=("#FF6FA8", "#7FD8FF", "#FFD43B", "#8CE07A", "#B98BFF", "#FFFFFF"), n=12),
}


# ================================================================ characters and things (round (0, 0))
def bee(look=0.0, happy=False, bow=None, arms=False, sting=False):
    """The bee, about 96 x 80 units round (0, 0). look > 0 turns the face to the right."""
    o = []
    ax = look * .55
    for sgn in (-1, 1):
        o.append(L([(ax + sgn * 7, -24), (ax + sgn * 9.5, -35), (ax + sgn * 15, -41)], COCOA, 2.6))
        o.append(F(E(ax + sgn * 15.5, -43, 4.8), COCOA, lift=.6, fuzz=False))
    for sgn in (-1, 1):
        o.append(F(E(sgn * 24 - look * .6, -25, 17, 11.5, rot=-sgn * 32), WING, st=WING_T, inset=2.8))
    if sting:
        o.append(F(kit.soft(kit.G([(-28, 2), (-43, 9), (-28, 15)]), 1.5), COCOA, lift=.6))
    if arms:
        for sgn in (-1, 1):
            o.append(F(E(sgn * 31, 7, 9, 6.5, rot=sgn * 35), YEL))
    body = E(0, 0, 32, 29)
    o.append(F(body, YEL, st=YEL_T))
    for y0, y1 in ((10, 17.5), (22.5, 30)):
        o.append(F(body.intersection(sbox(-40, y0, 40, y1)), COCOA, lift=0))
    ex = 10.5
    if happy:
        for x in (look - ex, look + ex):
            o.append(L([(x - 5, -4), (x, -9.5), (x + 5, -4)], DARK, 2.5))
    else:
        o.append(EYE(look - ex, -6, 5.2, look=(look * .15, 0)))
        o.append(EYE(look + ex, -6, 5.2, look=(look * .15, 0)))
    for x in (look - 19, look + 19):
        o.append(F(E(x, 2.5, 4.4, 3.6), CHEEK, lift=0))
    if happy:
        o.append(F(kit.G(crs([(look - 6, 0), (look, -.5), (look + 6, 0), (look + 3, 6), (look - 3, 6)], 6)), "#B5414F", lift=0, fuzz=False))
    else:
        o.append(L([(look - 4.6, .5), (look, 4.6), (look + 4.6, .5)], DARK, 2.0))
    if bow:
        o.append(F(E(-8, -27, 8.5, 6, rot=-20), bow, st="#FFFFFF", inset=2.2))
        o.append(F(E(8, -27, 8.5, 6, rot=20), bow, st="#FFFFFF", inset=2.2))
        o.append(F(E(0, -27, 3.8), kit.dk(bow, .15), lift=.5, fuzz=False))
    return o


def flower_head(r=16, petal=PINK, center=YEL, k=6, rot=0.0, st="#FFFFFF"):
    """A small flower: petals and a sewing-button centre (r = petal tip radius / 1.12)."""
    pet = U(*[E(r * .62 * math.cos(math.radians(rot + 360 * i / k)), r * .62 * math.sin(math.radians(rot + 360 * i / k)),
                r * .5, r * .38, rot=rot + 360 * i / k) for i in range(k)])
    return [F(pet, petal, st=st, inset=2.2 if r > 12 else 1.6), BTN(0, 0, r * .36, center)]


def leaf(x, y, ln, rot, col=GRN):
    return F(kit.G(tf_leaf(x, y, ln, rot)), col, st=LEAF_ST, inset=2)


def tf_leaf(x, y, ln, rot):
    return kit.tf(crs([(0, 0), (ln * .5, -ln * .3), (ln, 0), (ln * .5, ln * .3)], 6), x, y, rot)


def flower_house(door=True):
    """The bee's home: a big felt flower with a round door; head centre at (0, 0), stem to y = 64."""
    o = [F(tube([(0, 26), (2, 46), (0, 64)], 11), DGRN, st="#C7EBB5", inset=2.2)]
    o += [leaf(2, 44, 30, -32), leaf(-1, 56, 26, 205)]
    k = 8
    pet = U(*[E(34 * math.cos(2 * math.pi * i / k), 34 * math.sin(2 * math.pi * i / k), 21, 15, rot=360 * i / k) for i in range(k)])
    o.append(F(pet, PINK, st="#FFFFFF", inset=3.4))
    o.append(F(E(0, 0, 27), YEL, st=YEL_T, inset=3.2))
    if door:
        dg = R(-9, -10, 18, 24, 9).intersection(sbox(-20, -20, 20, 14))
        o.append(F(dg, "#B07850", st="#F3D2AE", inset=1.6))
        o.append(BTN(4.6, 3, 2.2, GOLD))
        o.append(F(E(-16, -11, 4.6), "#CFEFFF", lift=.6, fuzz=False))
        o.append(F(E(16, -11, 4.6), "#CFEFFF", lift=.6, fuzz=False))
    return o


def heart(s=12, col=PINK):
    return [F(kit.heart_pts(0, 0, s), col, st="#FFFFFF", inset=1.6 if s < 12 else 2.2)]


def sparkle(x, y, r, col="#FFE36B"):
    pts = []
    for i in range(8):
        a = math.radians(45 * i - 90)
        rr = r if i % 2 == 0 else r * .3
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
    return [F(kit.soft(kit.G(pts), r * .06), col, lift=.4, fuzz=False, shade=False)]


def tree():
    o = [F(R(-6, 4, 12, 34, 5), BRN, st=BRN_T, inset=2.2)]
    crown = U(E(-17, -6, 21), E(15, -8, 22), E(0, -26, 24), E(0, 2, 19))
    o.append(F(crown, DGRN, st=LEAF_ST, inset=3.2))
    for x, y in ((-14, -10), (11, -22), (8, 0), (-4, -32)):
        o.append(F(E(x, y, 4.6), RED, lift=.6))
    return o


def bush():
    g = U(E(-20, 0, 21), E(2, -10, 24), E(22, 0, 18)).intersection(sbox(-50, -50, 50, 12))
    o = [F(g, DGRN, st=LEAF_ST, inset=3)]
    for x, y, c in ((-18, -4, WHITE), (6, -16, "#FFE36B"), (20, 2, WHITE)):
        o += place(flower_head(6, c, ORA, 5), x, y)
    return o


def mushroom():
    cap = kit.soft(E(0, 0, 34, 27).intersection(sbox(-40, -40, 40, 6)), 3)
    o = [F(R(-11, 2, 22, 30, 9), CREAM, st="#E7D2B0", inset=2)]
    o.append(F(cap, RED, st="#FFFFFF", inset=3))
    for x, y, r in ((-16, -8, 5), (4, -16, 6), (18, -4, 4.4), (-2, -2, 3.6)):
        o.append(F(E(x, y, r), WHITE, lift=0, fuzz=False))
    return o


def grass(x, y, s=1.0, col=DGRN, only="ac"):
    """A felt grass tuft (not in pixels by default: the pixel ground has its own grass)."""
    g = U(kit.G([(-8, 0), (-6, -12), (-3, 0)]), kit.G([(-3, 0), (0, -16), (3, 0)]), kit.G([(3, 0), (6, -11), (8, 0)])).buffer(1.2)
    return [F(kit.affinity.affine_transform(g, [s, 0, 0, s, x, y]), col, lift=.6, only=only)]


# ================================================================ the files
def hero(st):
    return place(OBJ(bee(look=9, sting=True)), 50, 57, .93)


def home(st):
    return place(OBJ(flower_house()), 50, 47, .8)


def family(st):
    """Home at last: the bee hugs its family (mum with a bow, a baby) in front of the flower house."""
    o = OBJ(place(flower_house(), 200, 124, 1.9))
    for x, y, s, c in ((52, 196, 17, PINK), (350, 186, 14, RED), (330, 72, 11, CORAL), (70, 84, 10, PINK)):
        o += OBJ(place(heart(s, c), x, y))
    mound = kit.G(crs([(26, 340), (88, 306), (200, 298), (312, 306), (374, 340), (312, 366), (200, 374), (88, 366)], 6))
    o += OBJ([F(mound, "#A3D982", st="#FFFFFF", inset=4)])
    o += OBJ(place(bee(happy=True, arms=True, bow=PINK), 200, 262, 1.62))
    o += OBJ(place(bee(happy=True, arms=True), 106, 300, 1.26, rot=8))
    o += OBJ(place(bee(happy=True, arms=True), 298, 312, .98, rot=-10))
    for x, y, r in ((40, 270, 11), (364, 268, 10), (130, 34, 8), (284, 28, 9)):
        o += OBJ(sparkle(x, y, r), shadow=0)
    return o


def star(st):
    return OBJ([F(star_shape(40, 50, 53), YEL, st="#FFFFFF", inset=3.6),
                F(E(37, 38, 4.2, 2.6, rot=-35), "#FFFFFF", lift=0, fuzz=False, op=.85)])


def key(st):
    bow = E(-18, 0, 16).difference(E(-18, 0, 6.5))
    g = U(bow, R(-4, -5, 40, 10, 4), R(18, 3, 7, 11, 2.5), R(28, 3, 7, 8, 2.5))
    return place(OBJ([F(g, GOLD, st=GOLD_T, inset=2.4)]), 52, 52, 1.12, rot=-30)


def gate(st):
    """A little garden gate standing across a left-right road, with a padlock."""
    o = []
    for x in (27, 73):
        o.append(F(R(x - 6, 12, 12, 82, 4), "#A8714E", st="#E6C3A2", inset=2))
        o.append(F(E(x, 10, 8), "#C98B57", lift=.6))
    for y in (30, 72):
        o.append(F(R(31, y, 38, 8, 3), "#B97F4E", lift=.6))
    for x in (37.5, 50, 62.5):
        pk = kit.soft(kit.G([(x - 5, 88), (x - 5, 22), (x, 15), (x + 5, 22), (x + 5, 88)]), 1.2)
        o.append(F(pk, WOOD, st=WOOD_T, inset=1.6))
    o.append(F(tube(crs([(42, 52), (42, 43), (50, 37), (58, 43), (58, 52)], 6, closed=False), 4.6), "#B8BCC8", lift=.6))
    o.append(F(R(38, 48, 24, 20, 5.5), GOLD, st=GOLD_T, inset=1.8))
    o.append(F(U(E(50, 55.5, 3), R(48.7, 55.5, 2.6, 7, 1)), DARK, lift=0, fuzz=False, only="ac"))
    o.append(L([(50, 54), (50, 62)], DARK, 2.0, only="b"))
    return OBJ(o)


def deco_tree(st):
    return place(OBJ(grass(-20, 38, .8)) + OBJ(grass(22, 38, .7)) + OBJ(tree()), 50, 54, 1.0)


def deco_bush(st):
    return place(OBJ(bush()), 50, 60, 1.05)


def deco_flowers(st):
    o = []
    for x, h, c, r in ((-22, 30, PINK, 13), (2, 44, LILAC, 15), (25, 26, ORA, 12)):
        o.append(L([(x, 32), (x + 1, 32 - h * .5), (x, 32 - h)], DGRN, 3.6))
        o.append(leaf(x, 32 - h * .35, 14, -35 if x < 10 else 215))
    for x, h, c, r in ((-22, 30, PINK, 13), (2, 44, LILAC, 15), (25, 26, ORA, 12)):
        o += place(flower_head(r, c, YEL), x, 32 - h)
    return place(OBJ(grass(-30, 34, .7)) + OBJ(grass(34, 34, .6)) + OBJ(o), 50, 56, 1.05)


def deco_mushroom(st):
    return place(OBJ(grass(-22, 32, .7)) + OBJ(grass(20, 32, .6)) + OBJ(mushroom()), 50, 56, 1.05)


def deco_pond(st):
    o = [F(E(0, 0, 42, 27), BLUE, st="#FFFFFF", inset=3)]
    for pts in (((-26, 2), (-18, -1), (-10, 2)), ((8, 10), (16, 7), (24, 10)), ((10, -12), (18, -15), (26, -12))):
        o.append(L(list(pts), "#E8F7FF", 1.8))
    pad = E(-10, 4, 15, 10).difference(kit.G([(-10, 4), (8, -2), (8, 10)]))
    o.append(F(pad, GRN, st=LEAF_ST, inset=1.8))
    o += place(flower_head(7, PINK, YEL, 5), -14, 2)
    o.append(L([(30, 2), (31, -22), (33, -40)], DGRN, 2.6))
    o.append(F(R(28.5, -46, 8, 16, 4), BRN, lift=.6))
    return place(OBJ(o), 50, 60, 1.0)


def deco_fence(st):
    o = []
    for y in (-8, 12):
        o.append(F(R(-42, y, 84, 8, 3), "#F3E6D3", st=None, lift=.6))
    for x in (-30, -10, 10, 30):
        pk = kit.soft(kit.G([(x - 7, 30), (x - 7, -20), (x, -29), (x + 7, -20), (x + 7, 30)]), 2)
        o.append(F(pk, WHITE, st="#D8C9B5", inset=2))
    o += place(flower_head(7, RED, YEL, 5), -20, 26) + place(flower_head(6, "#FFE36B", ORA, 5), 22, 28)
    return place(OBJ(grass(-38, 32, .7)) + OBJ(grass(36, 32, .6)) + OBJ(o), 50, 56, 1.0)


# ---------------------------------------------------------------- stickers (200 x 200, the kit adds the round sticker)
def s_bee(st):
    return place(OBJ(bee()), 100, 112, 1.5)


def s_flower(st):
    o = [F(tube([(0, 20), (2, 48), (0, 72)], 9), DGRN, st="#C7EBB5", inset=2), leaf(2, 50, 26, -35), leaf(0, 62, 22, 210)]
    o += flower_head(36, PINK, YEL, 6)
    return place(OBJ(o), 100, 76, 1.3)


def s_ladybug(st):
    o = [F(E(0, -15, 10), DARK, lift=.6)]
    for sgn in (-1, 1):
        for y in (-4, 6, 15):
            o.append(L([(sgn * 14, y), (sgn * 24, y + 3)], DARK, 2.2))
    o.append(F(E(0, 3, 19, 17), RED, st="#FFFFFF", inset=2.4))
    o.append(L([(0, -12), (0, 19)], DARK, 2.2))
    for x, y, r in ((-9, -3, 3.4), (9, -3, 3.4), (-10, 10, 3), (10, 10, 3)):
        o.append(F(E(x, y, r), DARK, lift=0, fuzz=False))
    o.append(EYE(-4, -16, 2.2))
    o.append(EYE(4, -16, 2.2))
    return place(OBJ(o), 100, 104, 2.6)


def s_butterfly(st):
    o = []
    for sgn in (-1, 1):
        o.append(F(E(sgn * 14, -9, 14, 12, rot=sgn * 20), LILAC, st="#FFFFFF", inset=2.4))
        o.append(F(E(sgn * 11, 12, 9.5, 8.5, rot=-sgn * 20), PINK, st="#FFFFFF", inset=2.2))
        o.append(F(E(sgn * 15, -10, 4, 3.2), "#FFFFFF", lift=0, fuzz=False))
    o.append(F(R(-4, -16, 8, 34, 4), COCOA, lift=.6))
    o.append(L([(-2, -15), (-6, -24), (-10, -27)], DARK, 1.8))
    o.append(L([(2, -15), (6, -24), (10, -27)], DARK, 1.8))
    return place(OBJ(o), 100, 100, 2.6)


def s_honey(st):
    pot = kit.G(crs([(-20, -8), (20, -8), (25, 10), (16, 27), (-16, 27), (-25, 10)], 6))
    o = [F(pot, "#FFB84C", st="#FFFFFF", inset=2.6)]
    o.append(F(kit.G(crs([(-17, -8), (17, -8), (13, 4), (5, 0), (-3, 7), (-12, 1)], 5)), "#FFE36B", lift=0))
    o.append(F(R(-22, -17, 44, 11, 5), "#C9822E", lift=.8))
    o.append(F(R(-9, 7, 18, 11, 3), CREAM, st=None, lift=0))
    o += place(heart(5, RED), 0, 12.5)
    return place(OBJ(o), 100, 104, 2.4)


def s_snail(st):
    o = [F(kit.G(crs([(-34, 18), (-10, 14), (18, 12), (32, 4), (40, -10), (46, -8), (44, 10), (30, 22), (-30, 24)], 6)), "#C9E58C", st="#FFFFFF", inset=2)]
    for sgn, x in ((-1, 36), (1, 43)):
        o.append(L([(x, -6), (x + sgn * 2 + 2, -20)], "#9BBF5E", 2.4))
        o.append(F(E(x + sgn * 2 + 2, -21, 2.8), DARK, lift=0, fuzz=False))
    o.append(F(E(-6, -4, 26), ORA, st="#FFFFFF", inset=2.6))
    sp = [(-6 + math.cos(t * .5) * t * .9, -4 + math.sin(t * .5) * t * .9) for t in np.linspace(1, 22, 36)]
    o.append(L(sp, "#C9822E", 2.6))
    o.append(F(E(34, 8, 2.6), CHEEK, lift=0, fuzz=False))
    return place(OBJ(o), 104, 104, 1.8)


def s_sunflower(st):
    o = [F(tube([(0, 18), (0, 64)], 8), DGRN, st="#C7EBB5", inset=2), leaf(0, 44, 24, -30), leaf(0, 54, 20, 210)]
    k = 12
    pet = U(*[E(22 * math.cos(2 * math.pi * i / k), 22 * math.sin(2 * math.pi * i / k), 11, 6, rot=360 * i / k) for i in range(k)])
    o.append(F(pet, "#FFCF33", st="#FFFFFF", inset=1.8))
    o.append(F(E(0, 0, 15), "#8A5A3A", st="#C9946A", inset=2))
    for x, y in ((-6, -5), (5, -6), (-7, 5), (6, 5), (0, 0), (0, -9), (0, 9)):
        o.append(F(E(x, y, 1.6), "#5E3A26", lift=0, fuzz=False))
    return place(OBJ(o), 100, 76, 1.52)


def s_can(st):
    o = [F(tube(crs([(-16, -4), (-30, -10), (-30, 10), (-18, 14)], 6, closed=False), 6), "#4FA8E8", lift=.8)]
    o.append(F(kit.G([(16, 2), (40, -18), (44, -14), (22, 12)]), "#5BA8E8", st=None, lift=.8))
    o.append(F(E(44, -18, 6, 3.6, rot=-40), "#5BA8E8", lift=.6))
    o.append(F(R(-20, -10, 40, 34, 8), SKY, st="#FFFFFF", inset=2.4))
    o.append(F(R(-14, -16, 28, 8, 4), "#5BA8E8", lift=.6))
    o += place(flower_head(7, PINK, YEL, 5), 0, 8)
    for x, y in ((50, -6), (55, 2), (47, 6)):
        o.append(F(kit.G(kit.tf([(0, -4), (2.6, 1), (0, 3.4), (-2.6, 1)], x, y)), "#8EE3FF", lift=0, fuzz=False))
    return place(OBJ(o), 90, 106, 1.72)


def s_caterpillar(st):
    o = []
    for i, (x, y) in enumerate(((-36, 8), (-22, 2), (-8, 6), (6, 2))):
        o.append(F(E(x, y, 11), GRN if i % 2 else "#A6DB7E", st="#FFFFFF", inset=1.8))
        o.append(F(E(x - 3, y + 11, 2.6, 2), DGRN, lift=0, fuzz=False))
    o.append(L([(22, -10), (20, -20), (16, -26)], DARK, 1.8))
    o.append(L([(28, -9), (30, -20), (34, -25)], DARK, 1.8))
    o.append(F(E(25, -1, 14), "#B9E68C", st="#FFFFFF", inset=2))
    o.append(EYE(21, -3, 2.6))
    o.append(EYE(30, -3, 2.6))
    o.append(F(E(17, 4, 2.6, 2), CHEEK, lift=0, fuzz=False))
    o.append(L([(23, 4), (26, 7), (29, 4)], DARK, 1.5))
    return place(OBJ(o), 104, 104, 1.8)


def s_hive(st):
    o = []
    for i, (w, y) in enumerate(((22, 18), (30, 8), (34, -3), (30, -14), (20, -24))):
        o.append(F(R(-w, y - 6, 2 * w, 13, 6.5), "#F5C25A" if i % 2 else "#FFD573", st="#FFF1C2", inset=1.6))
    o.append(F(R(-6, 12, 12, 13, 6).intersection(sbox(-10, 0, 10, 24)), COCOA, lift=0, shade=False))
    o += place(bee(), 28, -26, .34)
    return place(OBJ(o), 96, 108, 2.1)


# ---------------------------------------------------------------- the home-page card (300 x 200)
def card(st):
    line = crs([(-40, 172), (40, 162), (110, 132), (170, 100), (230, 92), (340, 96)], 10, closed=False)
    road = tube(line, 48, cap="flat")
    o = [kit.ground_piece(WORLD, st)]
    o += OBJ(place(tree(), 128, 50, .55))
    o += OBJ(place(flower_head(14, ORA, YEL), 34, 46))
    o += OBJ(place(flower_head(12, LILAC, YEL), 200, 166))
    o += OBJ(place(flower_head(10, WHITE, YEL), 280, 176))
    o += OBJ(grass(84, 104, .9)) + OBJ(grass(268, 140, .8))
    o.append(kit.road_piece(WORLD, st, road, width=48))
    o += OBJ(place([F(star_shape(17, 0, 0), YEL, st="#FFFFFF", inset=1.8)], 150, 113))
    o += OBJ(place(flower_house(), 252, 64, .62))
    o += OBJ(place(bee(look=9, sting=True), 60, 148, .62))
    return o


def bits(st):
    """Small embroidered things on the felt ground (a only; b and c have their own texture)."""
    if st != "a":
        return []
    rnd = kit.random.Random(7)
    o = []
    for i in range(30):
        x, y = rnd.uniform(20, 580), rnd.uniform(20, 780)
        if i % 3 == 0:
            o += place(grass(0, 0, 1.0, "#7CC261"), x, y)
        elif i % 3 == 1:     # two French knots
            o.append(F(E(x, y, 3.2), (WHITE, "#FFE36B", "#FFC2D6")[i % 2], lift=.5, fuzz=False))
            o.append(F(E(x + 7, y + 4, 2.6), (WHITE, "#FFE36B", "#FFC2D6")[i % 2 + 1], lift=.5, fuzz=False))
        else:
            o += place(flower_head(6, ("#FFFFFF", "#FFD6E5", "#E6DCFF")[i % 3], "#FFE36B", 5), x, y)
    return o


WORLD = kit.World(
    "garden", "花園",
    road=ROAD, ground=GROUND, pixel=PIXEL, jelly=JELLY, bits=bits,
    hero=hero, home=home, family=family, star=star, key=key, gate=gate,
    deco=[deco_tree, deco_bush, deco_flowers, deco_mushroom, deco_pond, deco_fence],
    stickers=[s_bee, s_flower, s_ladybug, s_butterfly, s_honey, s_snail, s_sunflower, s_can, s_caterpillar, s_hive],
    card=card,
)
