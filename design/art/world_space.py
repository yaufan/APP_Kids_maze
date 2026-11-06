"""太空 space: a little astronaut floats home to the rocket.

    python3 build.py space        # writes app/assets/art/<a|b|c>/space/*.svg and checks them

Built like world_garden.py (the template). The ground is a friendly night sky (deep blue-purple,
little stars, tiny planets, soft nebula patches); the road is a glowing star path: lavender felt
with a gold stitch and little embroidered sparkles (a), light purple tiles with glitter and yellow
pixel stars (b), glowing lilac jelly with candy sparkles (c).

The sparkles on the road are extra pieces on each tile (SpaceWorld.files): they sit on the road's
centre line, never closer than 10 units to a tile edge, so they cannot break a seam. SpaceWorld.build
also keeps the felt road's hairs clear of the tile edges (see there).
"""
import math

import numpy as np

import kit
from kit import BTN, E, EYE, F, L, OBJ, R, U, crs, place, sbox, star_shape, tube

# ---------------------------------------------------------------- colours (style a, felt)
NIGHT = "#34368A"          # the felt sky
NEB1, NEB2 = "#45449E", "#4E3F98"    # nebula patches (a little lighter than the sky)
SUIT, SUIT_ST = "#F7F5FF", "#A9A1D8"
GLASS, GLASS_ST = "#9ED8FF", "#E6F6FF"
SKIN = "#FFD9C2"
HAIR = "#7A4E3A"
ORA, ORA_T = "#FF9F43", "#FFE0BF"
RED, RED_T = "#FF6B6B", "#FFD1D1"
PINK = "#FF8FC4"
YEL, YEL_T = "#FFD84D", "#FFF6CF"
GOLD, GOLD_T = "#FFC83D", "#FFF3C2"
LILAC, LILAC_T = "#B9A2FF", "#EEE6FF"
PURP = "#8E6BE8"
BLUE, BLUE_T = "#5FB4FF", "#D6ECFF"
TEAL = "#4FD6C4"
GRN, GRN_T, DGRN = "#86DE72", "#DDF7D3", "#5DBB55"
GREY, GREY_T, DGREY = "#C4C8E2", "#EEF0FA", "#8E93BA"
MOON, MOON_T = "#FFE37A", "#FFF8D6"
ROCK, ROCK_T = "#CFC8F2", "#F4F1FF"
SPARK = "#FFE680"
WHITE = kit.WHITE
DARK, CHEEK = kit.DARK, kit.CHEEK

PIXEL = dict(
    outline="#1C1840",
    palette=["#FFFFFF", "#FFF6C8", "#FFE36B", "#FFC21F", "#FF9F1C", "#FF5E5E", "#FF8FBF", "#FFC2DC", "#C9A8FF",
             "#E6DCFF", "#9B6BFF", "#8EE3FF", "#4FA8E8", "#2E6FD0", "#7BDB6E", "#3DB55B", "#4FD6C4", "#D3D6EC",
             "#9196C0", "#5A5F88", "#FFD3B8", "#8A5A40"],
    map={SUIT: "#FFFFFF", GLASS: "#8EE3FF", SKIN: "#FFD3B8", HAIR: "#8A5A40", ORA: "#FF9F1C", YEL: "#FFE36B",
         GOLD: "#FFC21F", MOON: "#FFE36B", LILAC: "#C9A8FF", PURP: "#9B6BFF", GREY: "#D3D6EC", DGREY: "#9196C0",
         ROCK: "#D3D6EC", GRN: "#7BDB6E", DGRN: "#3DB55B", CHEEK: "#FF8FBF", SPARK: "#FFE36B",
         NEB1: "#3A3890", NEB2: "#443489", DARK: "#1C1840", "#B5414F": "#C23A55"},
)
JELLY = dict(shadow="#120C3A", map={SUIT: "#FBF8FF", GLASS: "#7FD0FF", NEB1: "#4A4AB4"})

ROAD = {
    "a": dict(fill="#DCCFFF", stitch="#FFC33A"),
    "b": dict(fill="#C9B6FF", speck="#DED0FF", shade="#A890F0", light="#E9E0FF", border="#FFD23A"),
    "c": dict(body="#C7A4FF", rim="#8A5FE6", glow="#FBF5FF", shadow="#0E0A30"),
}
STARS_PX = [{"y": "#FFE36B", "w": "#FFFFFF"}, {"y": "#FFFFFF", "w": "#FFF6C8"}, {"y": "#8EE3FF", "w": "#FFFFFF"}]
GROUND = {
    "a": dict(base=NIGHT, fibres=("#4447A0", "#2C2E78")),
    "b": dict(base="#2B2A70", specks=[("#34338A", .05), ("#FFFFFF", .004), ("#FFE36B", .003)],
              stamps=[([".y.", "ywy", ".y."], STARS_PX, .9), (["w"], {"w": "#FFFFFF"}, 1.6)]),
    "c": dict(top="#2A2A7E", bottom="#4A2F92", swirl="#4B48B4",
              sprinkles=("#FFE36B", "#FFFFFF", "#FF9ECF", "#8EE3FF"), n=4),
}


# ================================================================ little helpers
def only(pieces, st):
    """The pieces (an OBJ marker included) drawn only in the given styles."""
    return [p.copy(only=st) for p in pieces]


def sparkle(x, y, r, col=SPARK, lift=.4):
    """A four-pointed twinkle."""
    pts = []
    for i in range(8):
        a = math.radians(45 * i - 90)
        rr = r if i % 2 == 0 else r * .3
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
    return [F(kit.soft(kit.G(pts), r * .06), col, lift=lift, fuzz=False, shade=False)]


def happy_eye(x, y, r, w):
    """A smiling closed eye (an arch of thread); in pixels a plain eye, since a pixel arch reads as a frown."""
    return [L([(x - r, y + 2), (x, y - 2.5), (x + r, y + 2)], DARK, w, only="ac"), EYE(x, y, r * .9, only="b")]


def half_plane(cx, cy, rot, upper=True, big=400):
    """The half of the plane above (upper) or below the line through (cx, cy) at angle rot."""
    b = sbox(-big, -big, big, 0) if upper else sbox(-big, 0, big, big)
    return kit.affinity.translate(kit.affinity.rotate(b, rot, origin=(0, 0)), cx, cy)


def ringed_planet(r=26, col="#FF9F7A", band="#FFC2A3", ring=LILAC, ring_st=LILAC_T, rot=-18, st="#FFFFFF"):
    """A planet with stripes and a ring round (0, 0): the ring's back half, the planet, its front half."""
    rx, ry, w = r * 1.75, r * .48, r * .3
    outer = E(0, 0, rx, ry, rot=rot)
    inner = E(0, 0, rx - w, max(1.0, ry - w * .5), rot=rot)
    rg = outer.difference(inner)
    ball = E(0, 0, r)
    o = [F(rg.difference(half_plane(0, 0, rot, upper=False).intersection(ball.buffer(.5))), ring, st=ring_st, inset=1.8)]
    o.append(F(ball, col, st=st, inset=2.6))
    for y0, y1 in ((-r * .55, -r * .3), (r * .15, r * .38)):
        b = kit.affinity.rotate(sbox(-2 * r, y0, 2 * r, y1), rot, origin=(0, 0))
        o.append(F(ball.intersection(b), band, lift=0, fuzz=False))
    front = rg.intersection(half_plane(0, 0, rot, upper=False)).intersection(ball.buffer(.5))
    o.append(F(front, ring, lift=.6))
    return o


def taper(pts, w0, w1):
    """A stroke along pts whose width goes from w0 to w1 (a comet's tail, a flame)."""
    P = np.array(pts, float)
    T = np.gradient(P, axis=0)
    T /= np.linalg.norm(T, axis=1, keepdims=True) + 1e-9
    N = np.stack([-T[:, 1], T[:, 0]], 1)
    hw = np.linspace(w0, w1, len(P))[:, None] / 2
    left, right = P + N * hw, P - N * hw
    poly = kit.G([tuple(p) for p in left] + [tuple(p) for p in right[::-1]])
    return U(poly, E(P[0][0], P[0][1], w0 / 2), E(P[-1][0], P[-1][1], max(.5, w1 / 2)))


# ================================================================ characters and things (round (0, 0))
HANDS = {"down": (28, 38), "out": (41, 22), "up": (40, -6), "hip": (25, 30)}


def astronaut(look=0.0, happy=False, accent=ORA, panel=BLUE, arms=("down", "down"), hair=None, bow=None,
              antenna=True, suit=SUIT, lite=False):
    """The little astronaut, about 80 x 108 units round (0, 0): a big round helmet with the face in a
    glass visor, a small round suit, gloves and boots in the accent colour. look > 0 turns right.
    lite: no backpack and the arms cut in one piece with the suit (for the big family picture, which
    must stay under the size limit)."""
    o = []
    vx = look * .45
    if antenna:
        o.append(L([(look * .25, -38), (look * .25 + 2, -48)], DGREY, 2.6))
        o.append(F(E(look * .25 + 2, -50, 4.6), accent, lift=.6, fuzz=False))
    if not lite:    # the backpack (behind, on the side away from the face)
        o.append(F(R(-30 - look * .7, 2, 60, 36, 11), GREY, st=GREY_T, inset=2.2))
    for sgn in (-1, 1):
        o.append(F(R(sgn * 10 - 8, 42, 16, 12, 5.5), accent, st=None))
    hands = []
    for sgn, a in zip((-1, 1), arms):
        hx, hy = HANDS[a]
        hands.append((sgn * hx, hy))
    sleeves = [tube([(sgn * 17, 22), (hx, hy)], 12) for (hx, hy), sgn in zip(hands, (-1, 1))]
    if lite:
        o.append(F(U(E(0, 30, 22, 19), *sleeves), suit, st=SUIT_ST, inset=2.6))
    else:
        for sl in sleeves:
            o.append(F(sl, suit, st=SUIT_ST, inset=1.8))
        o.append(F(E(0, 30, 22, 19), suit, st=SUIT_ST, inset=2.6))
    o.append(F(R(-9 + look * .25, 22, 18, 13, 3.5), panel, lift=.6))
    o.append(F(E(-3.5 + look * .25, 28.5, 2.4), RED, lift=0, fuzz=False))
    o.append(F(E(3.5 + look * .25, 28.5, 2.4), YEL, lift=0, fuzz=False))
    for hx, hy in hands:
        o.append(F(E(hx, hy, 6.8), accent, lift=.7))
    # the helmet
    o.append(F(E(0, -8, 34, 31), suit, st=SUIT_ST, inset=3.2))
    for sgn in (-1, 1):
        o.append(F(R(sgn * 33 - 4.5, -17, 9, 17, 4.5), accent, lift=.6))
    o.append(F(E(vx, -7, 26, 22), GLASS, st=GLASS_ST, inset=1.8))
    fx = vx + look * .12
    o.append(F(E(fx, -5, 21.5, 17.5), SKIN, lift=0, fuzz=False, po=False))
    if hair:
        fr = E(fx, -5, 21.5, 17.5).intersection(U(E(fx - 7, -21, 12, 7.5), E(fx + 7, -21.5, 12, 7)))
        o.append(F(fr, hair, lift=0, fuzz=False, po=False))
    ex = 8.5
    if happy:
        for x in (fx - ex, fx + ex):
            o += happy_eye(x, -8, 4.4, 2.3)
    else:
        o.append(EYE(fx - ex, -8, 4.3, look=(look * .12, 0)))
        o.append(EYE(fx + ex, -8, 4.3, look=(look * .12, 0)))
    for x in (fx - 15, fx + 15):
        o.append(F(E(x, 1, 3.8, 2.9), CHEEK, lift=0, fuzz=False))
    if happy:
        o.append(F(kit.G(crs([(fx - 5.5, 1), (fx, .5), (fx + 5.5, 1), (fx + 2.8, 6.5), (fx - 2.8, 6.5)], 6)), "#B5414F", lift=0, fuzz=False))
    else:
        o.append(L([(fx - 4.4, 2), (fx, 5.6), (fx + 4.4, 2)], DARK, 1.9, only="ac"))
        o.append(L([(fx - 2.6, 5.2), (fx + 2.6, 5.2)], DARK, 1.0, only="b"))    # a flat pixel smile
    # a glint on the glass (not in pixels: it would hide an eye)
    o.append(F(E(vx - 15, -18, 5.2, 2.6, rot=-40), "#FFFFFF", lift=0, fuzz=False, op=.8, only="ac"))
    if bow:
        for sgn in (-1, 1):
            o.append(F(E(sgn * 8 + 14, -37, 8, 5.6, rot=sgn * 20), bow, st="#FFFFFF", inset=1.8))
        o.append(F(E(14, -37, 3.6), kit.dk(bow, .15), lift=.5, fuzz=False))
    return o


def rocket(door=True, flame=False, body=SUIT, nose=RED, fin=RED, ring=GOLD, puffs=False, stripe=None):
    """A rocket standing up round (0, 0): nose at y = -50, fins down to y = 40; a round window and a door."""
    o = []
    if flame:
        o.append(F(taper([(0, 36), (0, 48), (0, 62)], 22, 4), ORA, lift=.4, fuzz=False))
        o.append(F(taper([(0, 36), (0, 46), (0, 54)], 12, 3), YEL, lift=0, fuzz=False))
    for sgn in (-1, 1):
        fg = kit.soft(kit.G([(sgn * 14, -2), (sgn * 34, 20), (sgn * 35, 41), (sgn * 18, 30), (sgn * 12, 26)]), 4)
        o.append(F(fg, fin, st=kit.lt(fin, .7), inset=2))
    o.append(F(R(-12, 26, 24, 12, 4), DGREY, st=None))
    hull = kit.G(crs([(0, -52), (15, -36), (21, -8), (21, 18), (17, 33), (-17, 33), (-21, 18), (-21, -8), (-15, -36)], 8))
    o.append(F(hull, body, st=SUIT_ST, inset=2.6))
    o.append(F(hull.intersection(sbox(-30, -60, 30, -30)), nose, lift=0))
    if stripe:
        o.append(F(hull.intersection(sbox(-30, 22, 30, 29)), stripe, lift=0, fuzz=False))
    o.append(F(E(0, -14, 12.5), ring, st=kit.lt(ring, .7), inset=1.6))
    o.append(F(E(0, -14, 8.6), GLASS, lift=.4))
    o.append(F(E(-3, -17, 3, 1.8, rot=-40), "#FFFFFF", lift=0, fuzz=False, op=.85))
    if door:
        o.append(F(R(-8.5, 4, 17, 22, 8).intersection(sbox(-20, -20, 20, 26)), "#7D8BE8", st="#D8DEFF", inset=1.5))
        o.append(BTN(4.4, 15, 2.2, GOLD))
    if puffs:
        o.append(F(U(E(-22, 41, 10, 8), E(-6, 44, 12, 9), E(10, 44, 11, 8.5), E(24, 41, 9, 7.5)), "#EEEAFF", st="#C9C2EC", inset=1.6))
    return o


def moon_face(col=MOON, st=MOON_T):
    """A crescent moon with a happy sleepy face (open side to the right)."""
    cres = E(0, 0, 34).difference(E(17, -9, 29))
    o = [F(cres, col, st=st, inset=2.6)]
    for x, y, r in ((-24, 14, 3.2), (-6, 26, 2.4)):
        o.append(F(E(x, y, r), kit.dk(col, .1), lift=0, fuzz=False))
    o.append(L([(-27, -6), (-23, -9.5), (-19, -6.5)], DARK, 2.2))
    o.append(F(E(-21, 2, 3.8, 2.8), CHEEK, lift=0, fuzz=False))
    o.append(L([(-17, 6), (-13, 9.5), (-9, 9)], DARK, 2.0))
    return o


def alien(look=0.0, wave=True):
    """A friendly green alien: a round body, two big eyes, two antennae, little arms and feet."""
    o = []
    for sgn in (-1, 1):
        o.append(L([(sgn * 9, -18), (sgn * 13, -31), (sgn * 19, -36)], DGRN, 2.6))
        o.append(F(E(sgn * 19.5, -37.5, 4.6), PINK, lift=.6, fuzz=False))
    for sgn in (-1, 1):
        o.append(F(E(sgn * 11, 29, 8.5, 5.5), DGRN, lift=.6))
    o.append(F(tube([(-20, 8), (-30, 18)], 8), GRN, st=None))
    o.append(F(tube([(20, 6), (30, -6)] if wave else [(20, 8), (30, 18)], 8), GRN, st=None))
    o.append(F(E(0, 4, 25, 24), GRN, st=GRN_T, inset=2.6))
    for x, y, r in ((-14, 16, 3.2), (13, 19, 2.6), (-4, 22, 2.2)):
        o.append(F(E(x, y, r), DGRN, lift=0, fuzz=False))
    for sgn in (-1, 1):
        o.append(F(E(look + sgn * 9, -4, 8, 9), WHITE, lift=.4, fuzz=False, po=False))
        o.append(EYE(look + sgn * 9 + look * .1, -3, 4.6, look=(look * .1, 0)))
    for x in (look - 19, look + 19):
        o.append(F(E(x, 6, 3.6, 2.6), CHEEK, lift=0, fuzz=False))
    o.append(F(kit.G(crs([(look - 7, 8), (look, 7.5), (look + 7, 8), (look + 3.5, 14), (look - 3.5, 14)], 6)), "#B5414F", lift=0, fuzz=False))
    return o


def satellite():
    """A satellite: a gold box, two blue solar panels on struts and a dish."""
    o = []
    for sgn in (-1, 1):
        o.append(L([(sgn * 10, 0), (sgn * 18, 0)], DGREY, 3.0))
        px0 = 18 if sgn > 0 else -46
        o.append(F(R(px0, -10, 28, 20, 2.5), "#4F86E8", st="#BFD8FF", inset=1.4))
        for k in (1, 2):
            gx = px0 + 28 * k / 3
            o.append(L([(gx, -8), (gx, 8)], "#9CC2FF", 1.3, only="ac"))
        o.append(L([(px0 + 2, 0), (px0 + 26, 0)], "#9CC2FF", 1.3, only="ac"))
    o.append(L([(0, -14), (0, -24)], DGREY, 2.4))
    dish = E(0, -27, 13, 7).intersection(sbox(-20, -40, 20, -26))
    o.append(F(dish, GREY, st=GREY_T, inset=1.4))
    o.append(F(E(0, -34, 2.8), RED, lift=.5, fuzz=False))
    o.append(F(R(-11, -14, 22, 28, 4), GOLD, st=GOLD_T, inset=2))
    o.append(F(E(0, 0, 5.5), GLASS, lift=.4, fuzz=False))
    return o


def comet():
    """A comet flying up to the right: a round glowing head and a three-coloured tail."""
    o = []
    path = [(18, -16), (2, -2), (-14, 12), (-32, 26)]
    for off, col, w in ((-7, PINK, 9), (7, BLUE, 9), (0, YEL, 13)):
        pts = crs([(x + off * .7, y + off * .7) for x, y in path], 6, closed=False)
        o.append(F(taper(pts, w, 2.5), col, lift=.4, fuzz=False))
    o.append(F(E(20, -18, 14), "#FFF3B0", st="#FFFFFF", inset=2.2))
    o.append(F(E(16, -22, 4, 2.4, rot=-40), "#FFFFFF", lift=0, fuzz=False, op=.9))
    return o


def sun_face():
    o = []
    k = 10
    rays = U(*[kit.soft(kit.G(kit.tf([(-6, -30), (0, -46), (6, -30)], 0, 0, 360 * i / k)), 1.8) for i in range(k)])
    o.append(F(rays, ORA, st=None))
    o.append(F(E(0, 0, 31), YEL, st=YEL_T, inset=2.6))
    for sgn in (-1, 1):
        o += happy_eye(sgn * 11, -7, 5, 2.4)
        o.append(F(E(sgn * 18, 5, 4.4, 3.2), CHEEK, lift=0, fuzz=False))
    o.append(F(kit.G(crs([(-8, 5), (0, 4.5), (8, 5), (4, 12), (-4, 12)], 6)), "#B5414F", lift=0, fuzz=False))
    return o


def ufo():
    o = []
    o.append(F(E(0, 11, 24, 7), "#7A5BD8", st=None))
    dome = E(0, -6, 22, 22).intersection(sbox(-30, -40, 30, -2))
    o.append(F(dome, GLASS, st=GLASS_ST, inset=1.8))
    o += place(alien(wave=False)[8:], 0, -10, .42)     # the alien (no feet, arms or antennae) peeks out of the dome
    o.append(F(E(-9, -18, 4.4, 2.4, rot=-40), "#FFFFFF", lift=0, fuzz=False, op=.8, only="ac"))
    o.append(F(E(0, 2, 47, 12.5), "#B58CFF", st="#EADFFF", inset=2.2))
    for x in (-32, -16, 0, 16, 32):
        o.append(F(E(x, 3, 3.8), YEL, lift=.4, fuzz=False))
    return o


def star_face(r=34, happy=True):
    o = [F(star_shape(r, 0, 2, ratio=.55), YEL, st="#FFFFFF", inset=2.6)]
    o.append(EYE(-7, -1, 3.4))
    o.append(EYE(7, -1, 3.4))
    for sgn in (-1, 1):
        o.append(F(E(sgn * 12, 6, 3.2, 2.4), CHEEK, lift=0, fuzz=False))
    o.append(L([(-4, 6), (0, 9.5), (4, 6)], DARK, 1.9))
    return o


# ================================================================ the files
def hero(st):
    return place(OBJ(astronaut(look=8, arms=("down", "out"))), 51, 49, .79)


def home(st):
    return place(OBJ(rocket(puffs=True)), 50, 48, .9)


def family(st):
    """Home at last: the little astronaut with mum and dad, waving in front of their rocket."""
    o = []
    o += OBJ(place(ringed_planet(19, "#7FD8C8", "#B8F0E6", PINK, "#FFE0EF"), 62, 70), shadow=.6)
    for x, y, r, c in ((338, 52, 11, GOLD), (304, 128, 7, LILAC), (34, 176, 8, BLUE), (370, 200, 9, PINK),
                       (130, 30, 7, LILAC), (150, 118, 6, GOLD), (262, 22, 6, BLUE)):
        o += OBJ(sparkle(x, y, r, c), shadow=0)
    o += OBJ(place(rocket(), 200, 150, 2.15))
    mound = kit.G(crs([(18, 344), (80, 310), (200, 302), (320, 310), (382, 344), (320, 372), (200, 380), (80, 372)], 6))
    o += OBJ([F(mound, ROCK, st="#FFFFFF", inset=4)] +
             [F(E(x, y, rx, ry), "#B7AEE6", lift=0, fuzz=False) for x, y, rx, ry in ((60, 344, 12, 4.6), (340, 342, 11, 4.4), (150, 366, 9, 3.6))])
    o += OBJ(place(astronaut(look=4, happy=True, accent=BLUE, panel=GOLD, arms=("down", "up"), hair=HAIR, lite=True), 82, 258, 1.3))
    o += OBJ(place(astronaut(look=-4, happy=True, accent=PINK, panel=LILAC, arms=("up", "down"), bow=PINK, hair="#5A3A2E", lite=True), 318, 264, 1.2))
    o += OBJ(place(astronaut(happy=True, accent=ORA, arms=("up", "up"), lite=True), 200, 290, 1.1))
    return o


def star(st):
    return OBJ([F(star_shape(41, 50, 53, ratio=.54), YEL, st="#FFFFFF", inset=3.6),
                F(E(37, 38, 4.2, 2.6, rot=-35), "#FFFFFF", lift=0, fuzz=False, op=.85)])


def key(st):
    """A key whose bow is a little planet with a ring."""
    shaft = U(R(-6, -5, 42, 10, 4), R(20, 3, 7, 11, 2.5), R(30, 3, 7, 8, 2.5))
    o = [F(shaft, GOLD, st=GOLD_T, inset=2.2)]
    o += place(ringed_planet(13, PURP, LILAC, GOLD, GOLD_T, rot=-25, st=LILAC_T), -18, 0)
    return place(OBJ(o), 52, 52, 1.12, rot=-30)


def gate(st):
    """An air-lock gate across a left-right road: two posts with lights, a force field and a padlock."""
    o = []
    for x in (21, 79):
        o.append(F(R(x - 7, 12, 14, 82, 5), GREY, st=GREY_T, inset=2))
        o.append(F(E(x, 11, 7.5), RED if x < 50 else YEL, lift=.6))
    for y in (24, 38, 74, 86):
        pts = [(28 + t, y + 2.6 * math.sin(t / 44 * 2 * math.pi * 1.5)) for t in np.linspace(0, 44, 23)]
        o.append(F(tube(pts, 6.5), "#7FE8FF", lift=.4, fuzz=False, only="ac"))
        o.append(F(R(28, y - 3.5, 44, 7), "#7FE8FF", lift=.4, only="b"))
    o.append(F(tube(crs([(42, 54), (42, 45), (50, 39), (58, 45), (58, 54)], 6, closed=False), 4.6), "#B8BCC8", lift=.6))
    o.append(F(R(37, 50, 26, 21, 6), GOLD, st=GOLD_T, inset=1.8))
    o.append(F(U(E(50, 58, 3), R(48.7, 58, 2.6, 7, 1)), DARK, lift=0, fuzz=False, only="ac"))
    o.append(L([(50, 56.5), (50, 64.5)], DARK, 2.0, only="b"))
    return OBJ(o)


def deco_planet(st):
    o = OBJ(ringed_planet(24))
    o += OBJ(place(sparkle(0, 0, 6), 34, -30))
    return place(o, 50, 52, 1.0)


def deco_moon(st):
    return place(OBJ(moon_face()) + OBJ(sparkle(30, -24, 7)) + OBJ(sparkle(26, 22, 5)), 50, 50, 1.12)


def deco_alien(st):
    return place(OBJ(alien(look=2)), 50, 54, 1.05)


def deco_satellite(st):
    return place(OBJ(satellite()), 50, 54, 1.0, rot=-18)


def deco_comet(st):
    return place(OBJ(comet()) + OBJ(sparkle(-26, -24, 5)), 50, 50, 1.15)


def deco_ship(st):
    return place(OBJ(rocket(door=False, flame=True, body=BLUE, nose=YEL, fin=YEL, ring=WHITE)), 50, 46, .72, rot=35)


# ---------------------------------------------------------------- stickers (200 x 200, the kit adds the round sticker)
def twinkles(pts=((44, 58, 7), (158, 50, 6), (152, 150, 7), (50, 146, 5))):
    o = []
    for x, y, r in pts:
        o += OBJ(sparkle(x, y, r, lift=0), shadow=0)
    return o


def s_astronaut(st):
    return twinkles() + place(OBJ(astronaut(happy=True, arms=("down", "up"))), 100, 106, 1.22)


def s_rocket(st):
    return twinkles() + place(OBJ(rocket(flame=True, stripe=BLUE)), 100, 92, 1.28)


def s_planet(st):
    return twinkles() + place(OBJ(ringed_planet(34, "#7FD8C8", "#B8F0E6", PINK, "#FFE0EF", rot=-20)), 100, 100, 1.2)


def s_moon(st):
    return twinkles(((150, 60, 8), (154, 140, 6), (48, 150, 5))) + place(OBJ(moon_face()), 96, 100, 1.9)


def s_sun(st):
    return place(OBJ(sun_face()), 100, 100, 1.6)


def s_alien(st):
    return twinkles() + place(OBJ(alien()), 100, 104, 1.7)


def s_comet(st):
    return twinkles(((150, 140, 7), (50, 60, 6))) + place(OBJ(comet()), 102, 102, 1.75)


def s_ufo(st):
    return twinkles(((46, 60, 6), (156, 56, 7), (100, 160, 6))) + place(OBJ(ufo()), 100, 104, 1.5)


def s_satellite(st):
    return twinkles(((50, 50, 6), (152, 152, 7))) + place(OBJ(satellite()), 100, 104, 1.55, rot=-18)


def s_star(st):
    return twinkles(((44, 56, 6), (158, 150, 6), (154, 50, 5))) + place(OBJ(star_face()), 100, 102, 1.85)


# ---------------------------------------------------------------- the home-page card (300 x 200)
def card(st):
    line = crs([(-40, 176), (40, 164), (110, 136), (170, 108), (230, 98), (340, 100)], 10, closed=False)
    road = tube(line, 48, cap="flat")
    o = [kit.ground_piece(WORLD, st)]
    o += OBJ(place(ringed_planet(15), 46, 50))
    o += OBJ(place(moon_face(), 150, 46, .5))
    for x, y, r in ((100, 24, 6), (206, 30, 5), (292, 150, 6), (230, 172, 7), (16, 118, 5), (110, 92, 4)):
        o += OBJ(sparkle(x, y, r), shadow=0)
    o.append(kit.road_piece(WORLD, st, road, width=48))
    o += OBJ(place([F(star_shape(18, 0, 0, ratio=.54), YEL),
                    F(E(-4, -5, 2.6, 1.6, rot=-35), "#FFFFFF", lift=0, fuzz=False, op=.85)], 150, 118))
    o += OBJ(place(rocket(puffs=True), 254, 64, .78))
    o += OBJ(place(astronaut(look=8, arms=("down", "out")), 62, 146, .5))
    return o


# ---------------------------------------------------------------- the night sky's bits
def bits(st):
    """Things on the sky: nebula patches, little planets and twinkles (style a); b and c get a few too."""
    rnd = kit.random.Random(11)
    o = []
    nebulae = [(120, 190, 95, 55, 20, NEB1), (470, 420, 90, 60, -25, NEB2), (170, 640, 100, 50, 10, NEB2), (500, 720, 70, 40, 0, NEB1)]
    for x, y, rx, ry, rot, col in nebulae:
        g = kit.soft(U(E(x, y, rx, ry, rot=rot), E(x + rx * .45, y - ry * .35, rx * .55, ry * .7, rot=rot),
                       E(x - rx * .5, y + ry * .3, rx * .5, ry * .65, rot=rot)), 6)
        neb = OBJ([F(g, col, lift=0, shade=False, po=False)], shadow=-1)
        if st == "b":
            o += only(neb, "b")
        elif st == "a":
            o += [F(g, col, lift=0, shade=False)]
    planets = [(90, 410, 12, "#FF9F7A", "#FFC2A3", LILAC), (520, 120, 10, "#7FD8C8", "#B8F0E6", PINK),
               (330, 300, 8, PINK, "#FFC2DC", GOLD), (420, 610, 11, LILAC, "#E0D4FF", GOLD), (60, 760, 9, "#7FD8C8", "#B8F0E6", YEL)]
    for x, y, r, c1, c2, rc in planets:
        o += OBJ(place(ringed_planet(r, c1, c2, rc, kit.lt(rc, .6), rot=rnd.uniform(-30, 10)), x, y), shadow=.5)
    for x, y, r, c in ((250, 470, 13, "#FFE6A8"), (560, 560, 9, "#E6E0FF")):
        o += OBJ([F(E(x, y, r), c, st=None)] + [F(E(x + dx * r, y + dy * r, r * rr), kit.dk(c, .12), lift=0, fuzz=False)
                                                 for dx, dy, rr in ((-.3, -.2, .28), (.35, .3, .2))], shadow=.5)
    if st == "b":
        return o            # the pixel sky has its own star stamps
    for i in range(34 if st == "a" else 22):
        x, y = rnd.uniform(16, 584), rnd.uniform(16, 784)
        if i % 3 == 2 and st == "a":
            o.append(F(E(x, y, 2.6), (WHITE, SPARK, "#FFC2DC")[i % 3], lift=.4, fuzz=False))
        else:
            o += OBJ(sparkle(x, y, rnd.uniform(5, 10), (SPARK, WHITE, "#BFEFFF")[i % 3]), shadow=0)
    return o


# ---------------------------------------------------------------- sparkles sewn on the road tiles
def road_spots(m):
    """Points on the road's centre line 25 units in from every open side (on a turn: a quarter and
    three quarters round the bend). Never near a tile edge, so the tiles still join."""
    sides = {1: (50, 0), 2: (100, 50), 4: (50, 100), 8: (0, 50)}
    inward = {1: (0, 1), 2: (-1, 0), 4: (0, -1), 8: (1, 0)}
    opn = [b for b in (1, 2, 4, 8) if m & b]
    if len(opn) == 2 and not (m in (5, 10)):
        cx = 100.0 if m & 2 else 0.0
        cy = 100.0 if m & 4 else 0.0
        (x1, y1), (x2, y2) = sides[opn[0]], sides[opn[1]]
        a1, a2 = math.atan2(y1 - cy, x1 - cx), math.atan2(y2 - cy, x2 - cx)
        if a2 - a1 > math.pi:
            a2 -= 2 * math.pi
        if a1 - a2 > math.pi:
            a1 -= 2 * math.pi
        return [(cx + 50 * math.cos(a1 + (a2 - a1) * t), cy + 50 * math.sin(a1 + (a2 - a1) * t)) for t in (.25, .75)]
    out = []
    for b in opn:
        (x, y), (dx, dy) = sides[b], inward[b]
        out.append((x + dx * 25, y + dy * 25))
    return out


def road_bits(m, st):
    o = []
    for i, (x, y) in enumerate(road_spots(m)):
        if st == "a":     # an embroidered twinkle: a long cross and a short diagonal one
            r = 5.2
            o.append(L([(x, y - r), (x, y + r)], "#FFC33A", 1.9))
            o.append(L([(x - r, y), (x + r, y)], "#FFC33A", 1.9))
            q = r * .45
            o.append(L([(x - q, y - q), (x + q, y + q)], "#FFE58A", 1.3))
            o.append(L([(x - q, y + q), (x + q, y - q)], "#FFE58A", 1.3))
        elif st == "c":
            o += sparkle(x, y, 4.6, "#FFF6B8", lift=0)
        else:             # a yellow pixel star (a plus), each its own object so none gets an outline
            o += OBJ(sparkle(x, y, 6, "#FFE36B", lift=0), shadow=0)
    return o


class _Inset:
    """Stands in for a kit.Ctx whose file is d units smaller on every side (see SpaceWorld.build)."""
    stroke = kit.Ctx.stroke

    def __init__(self, c, d):
        self.c, self.u, self.kind = c, c.u, c.kind
        self.W, self.H = c.W - 2 * d, c.H - 2 * d
        self.body = []

    def rnd(self, *key):
        return self.c.rnd(*key)


class SpaceWorld(kit.World):
    """kit.World with little sparkles on every road tile, and felt road hairs that keep clear of the
    tile edges.

    Why the hairs: kit._hairs only drops hair points that are less than 0.4 units (virtual grid) from
    the file's edge, so on a road tile a hair can still reach the tile edge, where the next tile has
    none (`build.py seams` caught one on this world's light road). While this world is built,
    _hairs on a tile is run on a file shrunk by d units on every side (and moved back), so no hair
    point lies within d + 0.4 of an edge. Everything else, the wobble included, is the kit's."""

    def files(self, style):
        out = super().files(style)
        for m in range(1, 16):
            kind, pieces = out[f"tile_{m}"]
            out[f"tile_{m}"] = (kind, pieces + road_bits(m, style))
        return out

    def build(self, *args, **kw):
        orig = kit._hairs

        def hairs(c, g, col, key, k=1.0):
            if c.kind != "tile":
                return orig(c, g, col, key, k)
            d = math.ceil(1.1 * c.u)            # about 1 dp: hairs are 0.5 dp wide and slant
            sub = _Inset(c, d)
            orig(sub, kit.affinity.translate(g, -d, -d), col, key, k)
            if sub.body:
                c.body.append(f'<g transform="translate({d} {d})">{"".join(sub.body)}</g>')

        kit._hairs = hairs
        try:
            return super().build(*args, **kw)
        finally:
            kit._hairs = orig


WORLD = SpaceWorld(
    "space", "太空",
    road=ROAD, ground=GROUND, pixel=PIXEL, jelly=JELLY, bits=bits,
    sticker=dict(fill="#3E3C96", stitch="#FFE07A", fill_b="#2E2A70", fill_c="#4A3FA6"),
    hero=hero, home=home, family=family, star=star, key=key, gate=gate,
    deco=[deco_planet, deco_moon, deco_alien, deco_satellite, deco_comet, deco_ship],
    stickers=[s_astronaut, s_rocket, s_planet, s_moon, s_sun, s_alien, s_comet, s_ufo, s_satellite, s_star],
    card=card,
)
