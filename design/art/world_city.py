"""城市 city: a little bus drives home to the bus station.

    python3 build.py city         # writes app/assets/art/<a|b|c>/city/*.svg and checks them

Built like world_garden.py (the template). One addition: the road tiles carry a dashed white centre
line. `CityWorld.files()` adds it to every tile, laid out so it joins across tiles in every style:
  - a straight run through a tile has three dashes at 8-24, 42-58 and 76-92 units from its edge, so
    there is half a gap (8) at every tile edge and nothing is cut by the edge;
  - a turn has two dashes on its quarter circle (radius 50, the middle of the quarter ring), with the
    same half gap at both edges;
  - a dead end has the first two dashes of a straight; a T-crossing runs the line straight through
    and joins the side arm to it in the middle; the cross runs both lines through.
felt: an embroidered white running stitch; pixel: 1-pixel white dashes on the road's middle pixel
column (the road is 15 pixels wide, so the line sits exactly in the middle); jelly: white candy
stripes with a soft shadow (all shadows first, so a stripe never shades its neighbour).
"""
import math

from shapely.geometry import LineString
from shapely.ops import substring

import kit
from kit import BTN, E, EYE, F, L, OBJ, R, U, crs, place, sbox, star_shape, tube

# ---------------------------------------------------------------- colours (style a, felt)
RED, RED_T = "#F2574A", "#FFE0D8"          # the little bus
BLUE, BLUE_T = "#4A8FE7", "#DCEBFF"        # the big bus, the house roof
YEL, YEL_T = "#FFC93C", "#FFF4C8"          # the tiny bus, taxi, garbage truck
GLASS, GLASS_T = "#BDE7FF", "#FFFFFF"
TYRE, TYRE_T = "#3E3B4C", "#8E8C9E"
HUB = "#C9CED9"
TEAL, TEAL_T = "#22B3A2", "#D4F6F0"
LAWN, LAWN2 = "#7DC98A", "#5DB46E"
DGRN, DGRN_T = "#3FA45E", "#CDEFD3"
WOOD, WOOD_T = "#E8964F", "#FFE2C2"
BROWN = "#9A6448"
STEEL, STEEL_T = "#7E869A", "#C9CED9"
DSTEEL = "#4E5468"
PAVE, PAVE_T = "#DCE0EA", "#FFFFFF"
CREAM, CREAM_T = "#FFF1D6", "#E9CFA6"
PINK = "#FF9EC1"
ORA = "#FF9A3C"
LAMP = "#FFE58A"
SOIL = "#A8714F"
WHITE = kit.WHITE
DARK, CHEEK = kit.DARK, kit.CHEEK
CHEEK2 = "#FFB8C6"        # cheeks on a red body (CHEEK would vanish on it)
SIGNAL = {"r": "#FF4D4D", "y": "#FFC21F", "g": "#3DDC84"}

PIXEL = dict(
    outline="#2A2840",
    palette=["#FFFFFF", "#FFF3CF", "#E4E7F0", "#B4BACB", "#8D93A8", "#5A6078", "#FFE066", "#FFC21F", "#FF9A3C",
             "#F2453D", "#FF9EB5", "#8EDCFF", "#4A8FE7", "#2456C8", "#6FDB95", "#3FBF73", "#2E9A5C", "#1F6E45",
             "#22B3A2", "#E8964F", "#9A5E3A", "#5A3828", "#3E3B4C", "#B6F2C4"],
    map={RED: "#F2453D", BLUE: "#4A8FE7", YEL: "#FFC21F", GLASS: "#8EDCFF", TYRE: "#3E3B4C", HUB: "#E4E7F0",
         LAWN: "#6FDB95", DGRN: "#2E9A5C", TEAL: "#22B3A2", PAVE: "#E4E7F0", STEEL: "#8D93A8", DSTEEL: "#5A6078",
         CREAM: "#FFF3CF", CHEEK: "#FF9EB5", CHEEK2: "#FF9EB5", LAMP: "#FFE066", WOOD: "#E8964F", SOIL: "#9A5E3A",
         SIGNAL["r"]: "#F2453D", SIGNAL["y"]: "#FFC21F", SIGNAL["g"]: "#6FDB95", "#4DB860": "#6FDB95",
         "#86D97C": "#B6F2C4", "#3D6FE0": "#2456C8", "#3D7BE0": "#4A8FE7"},
)
JELLY = dict(shadow="#44527A", map={LAWN: "#7FD88E", DGRN: "#43B866", TYRE: "#4A4660", STEEL: "#8A93AC"})

ROAD = {
    "a": dict(fill="#8C93A8", stitch="#C3C8D6"),
    "b": dict(fill="#8D93A8", speck="#7E8499", shade="#6E748A", light="#A9AFC2", border="#2A2840"),
    "c": dict(body="#8FA2C8", rim="#566A99", glow="#EEF3FF", shadow="#44527A"),
}
GROUND = {
    "a": dict(base="#86CF8E", fibres=("#9ADAA0", "#74BF7E")),
    "b": dict(base="#3FBF73", specks=[("#34AD66", .07), ("#6FDB95", .04)],
              stamps=[([".r.y.r.", "sssssss"], [{"r": "#F2453D", "y": "#FFE066", "s": "#9A5E3A"},
                                                 {"r": "#FF9EB5", "y": "#FFFFFF", "s": "#9A5E3A"}], .6),
                      ([".h.", "hhh"], {"h": "#2E9A5C"}, .8)]),
    "c": dict(top="#E3F8E8", bottom="#C8EED3", swirl="#F5FDF7",
              sprinkles=("#FF6B6B", "#FFD43B", "#4DABF7", "#FFFFFF", "#FF9EC1", "#3DDC84"), n=10),
}
STICKER = dict(fill=WHITE, stitch="#C9CFE0", fill_b="#FFFFFF", fill_c="#F4F8FF")


# ================================================================ the centre line on the road tiles
STRAIGHT = ((8.0, 24.0), (42.0, 58.0), (76.0, 92.0))     # dashes along a straight run, from a tile edge
MID = {1: (50.0, 0.0), 2: (100.0, 50.0), 4: (50.0, 100.0), 8: (0.0, 50.0)}   # the middle of each edge
CL_W = {"a": 5.0, "b": 4.0, "c": 6.5}     # line width per style (b: one pixel)


def _arm(side, a, b):
    """The road's middle line from a to b units in from the edge on `side`."""
    return {1: [(50, a), (50, b)], 4: [(50, 100 - a), (50, 100 - b)],
            8: [(a, 50), (b, 50)], 2: [(100 - a, 50), (100 - b, 50)]}[side]


def centre_dashes(m):
    """The dashes of tile m's centre line (point lists), side arms first, then the lines straight
    through (so in felt a thread that crosses lies on top)."""
    sides = [s for s in (1, 2, 4, 8) if m & s]
    if len(sides) == 2 and m not in (5, 10):          # a turn: the quarter circle of radius 50
        cx = 100.0 if m & 2 else 0.0
        cy = 100.0 if m & 4 else 0.0
        (x0, y0), (x1, y1) = MID[sides[0]], MID[sides[1]]
        a0, a1 = math.atan2(y0 - cy, x0 - cx), math.atan2(y1 - cy, x1 - cx)
        while a1 - a0 > math.pi:
            a1 -= 2 * math.pi
        while a0 - a1 > math.pi:
            a1 += 2 * math.pi
        arc = LineString([(cx + 50 * math.cos(a0 + (a1 - a0) * t / 48), cy + 50 * math.sin(a0 + (a1 - a0) * t / 48))
                          for t in range(49)])
        g = 18.0
        d = (arc.length - 16 - g) / 2
        return [list(substring(arc, a, a + d).coords) for a in (8.0, 8.0 + d + g)]
    out = []
    through = []
    if m & 5 == 5:
        through += [_arm(1, a, b) for a, b in STRAIGHT]
    if m & 10 == 10:
        through += [_arm(8, a, b) for a, b in STRAIGHT]
    for s in sides:
        if (s in (1, 4) and m & 5 == 5) or (s in (2, 8) and m & 10 == 10):
            continue
        if len(sides) == 1:          # a dead end: the line runs into the round end
            out += [_arm(s, 8, 24), _arm(s, 42, 58)]
        else:                        # the side arm of a T: it joins the line going through
            out += [_arm(s, 8, 24), _arm(s, 42, 50)]
    return out + through


def _pull(pts, k):
    """A dash shortened by k at both ends (pixels: its ends stay inside whole pixels)."""
    ln = LineString(pts)
    return list(substring(ln, k, ln.length - k).coords)


def centre_line(dash_list, st, w=None):
    """The centre line pieces for a list of dashes in one style."""
    w = w or CL_W[st]
    if st == "a":
        return [L(d, WHITE, w) for d in dash_list]
    if st == "b":
        return OBJ([L(_pull(d, .5), "#FFFFFF", w) for d in dash_list], shadow=-1)
    caps = [LineString(d).buffer(w / 2, cap_style="round") for d in dash_list]
    shc = JELLY["shadow"]
    return ([F(kit.affinity.translate(g, .5, 1.6), shc, lift=0, op=.32, gloss=False) for g in caps]
            + [F(g, "#FFFFFF", lift=0, gloss=False) for g in caps])


class CityWorld(kit.World):
    """kit.World with the centre line added to every road tile."""

    def files(self, style):
        out = super().files(style)
        for m in range(1, 16):
            kind, pieces = out[f"tile_{m}"]
            out[f"tile_{m}"] = (kind, pieces + centre_line(centre_dashes(m), style))
        return out


def dashed(line, d, g):
    """Dashes (point lists) along a polyline: half a gap at each end, gaps of g, dashes about d."""
    ln = LineString(line)
    k = max(1, round((ln.length) / (d + g)))
    p = ln.length / k
    dl = p - g
    return [list(substring(ln, i * p + g / 2, i * p + g / 2 + dl).coords) for i in range(k)]


# ================================================================ characters and things (round (0, 0))
def wheel(x, y, r):
    return [F(E(x, y, r), TYRE, st=TYRE_T, inset=1.6 if r < 12 else 2.2), BTN(x, y, r * .42, HUB)]


def eyes(xs, y, r, happy=False, look=0.0):
    o = []
    for x in xs:
        if happy:
            o.append(L([(x - r * .95, y + r * .35), (x, y - r * .55), (x + r * .95, y + r * .35)], DARK, max(1.8, r * .46)))
        else:
            o.append(EYE(x, y, r, look=(look, 0)))
    return o


def mouth(x, y, w, happy=False):
    if happy:
        return [F(kit.G(crs([(x - w, y - .5), (x, y - 1), (x + w, y - .5), (x + w * .5, y + w * .9), (x - w * .5, y + w * .9)], 6)),
                  "#B5414F", lift=0, fuzz=False)]
    return [L([(x - w, y), (x, y + w * .75), (x + w, y)], DARK, max(1.6, w * .4))]


def bus(col=RED, st=RED_T, happy=False, look=1.5, cheek=CHEEK2, stripe=WHITE, roof="#E4E7F0"):
    """The little round bus, about 92 x 76 units round (0, 0), facing right (the face is on the
    front window)."""
    o = [F(R(-27, -39, 36, 10, 5), roof, lift=.6, fuzz=False)]          # the roof unit
    body = R(-46, -33, 92, 56, 17)
    o.append(F(body, col, st=st, inset=3.2))
    o.append(F(body.intersection(sbox(-60, 9, 60, 15)), stripe, lift=0, fuzz=False))
    for x in (-39, -20):
        o.append(F(R(x, -25, 16, 17, 5), GLASS, lift=.5))
    front = kit.soft(body.buffer(-6).intersection(sbox(1, -27, 60, -3)), 4)
    o.append(F(front, GLASS, lift=.5))
    o += eyes((14 + look, 29 + look), -14.5, 5.4, happy, look * .3)
    o += mouth(22 + look, 2, 4.4, happy)
    o += [F(E(8, 2.5, 4.2, 3.2), cheek, lift=0), F(E(36.5, 2.5, 3.6, 3), cheek, lift=0)]
    o.append(F(E(42.5, 13, 2.6, 4), LAMP, lift=.4, fuzz=False))
    o += wheel(-26, 23, 11) + wheel(26, 23, 11)
    return o


def car(col, st, kind="taxi", look=1.0):
    """A small car facing right: taxi (a blank sign on the roof) or police (a white cabin on a blue
    body, a red and blue light bar)."""
    o = []
    if kind == "taxi":
        o.append(F(R(-11, -38, 22, 9, 4), CREAM, st=None, lift=.6))
    else:
        o.append(F(R(-14, -37, 14, 8, 3.5), "#FF4D5E", lift=.6))
        o.append(F(R(0, -37, 14, 8, 3.5), "#3D7BFF", lift=.6))
    lower = R(-46, -8, 92, 28, 12)
    cabin = kit.soft(kit.G([(-30, -6), (-22, -30), (18, -30), (32, -6)]), 6)
    if kind == "police":
        o.append(F(cabin.buffer(1), WHITE, st="#C9CFE0", inset=2.2))
        o.append(F(lower, col, st=st, inset=2.8))
        o.append(F(lower.intersection(sbox(-60, 5, 60, 10)), WHITE, lift=0, fuzz=False))
    else:
        o.append(F(U(lower, cabin), col, st=st, inset=2.8))
    o.append(F(kit.soft(kit.G([(-24, -9), (-18, -25), (-3, -25), (-3, -9)]), 3), GLASS, lift=.5))
    o.append(F(kit.soft(kit.G([(1, -9), (1, -25), (16, -25), (27, -9)]), 3), GLASS, lift=.5))
    o += eyes((8 + look, 17 + look), -16, 3.8, look=look * .3)
    o += mouth(28, 1, 3.6)
    o.append(F(E(38, 1, 3.4, 2.6), CHEEK, lift=0))
    o.append(F(E(43, 4, 2.4, 3.4), LAMP, lift=.4, fuzz=False))
    o += wheel(-26, 20, 10) + wheel(26, 20, 10)
    return o


def fire_engine():
    o = []
    for x in range(-40, 14, 9):
        o.append(L([(x, -31), (x, -21)], "#E4E7F0", 2.4))
    o.append(F(R(-46, -33, 60, 4.4, 2.2), "#E4E7F0", lift=.6, fuzz=False))
    o.append(F(R(-46, -22.5, 60, 4.4, 2.2), "#E4E7F0", lift=.6, fuzz=False))
    o.append(F(E(30, -35, 6, 4.5), "#FFC21F", lift=.6))
    back = R(-48, -18, 68, 38, 7)
    cab = kit.soft(kit.G([(14, -31), (34, -31), (48, -8), (48, 20), (14, 20)]), 6)
    o.append(F(back, RED, st=RED_T, inset=2.8))
    o.append(F(cab, RED, st=RED_T, inset=2.8))
    o.append(F(U(back, cab).intersection(sbox(-60, 6, 60, 11)), WHITE, lift=0))
    o.append(F(kit.soft(kit.G([(19, -26), (32, -26), (42, -8), (19, -8)]), 3), GLASS, lift=.5))
    o += eyes((25, 34), -16, 3.6, look=.6)
    o += mouth(31, 0, 3.4)
    o.append(F(E(42, 0, 3, 2.4), CHEEK2, lift=0))
    hose = E(-22, -4, 9)
    o.append(F(hose, "#FFC21F", st="#FFF4C8", inset=1.5, lift=.6))
    o.append(F(E(-22, -4, 3.4), "#E09A10", lift=0, fuzz=False))
    o.append(F(R(-6, -12, 18, 14, 3), "#FFB3A8", lift=.5))
    o += wheel(-30, 21, 10) + wheel(28, 21, 10)
    return o


def note(x, y, s, col):
    """A music note (the garbage truck plays a tune)."""
    g = U(E(x, y, 4.6 * s, 3.6 * s, rot=-25), R(x + 3 * s, y - 17 * s, 2.6 * s, 17 * s, 1.2 * s),
          kit.G([(x + 3 * s, y - 17 * s), (x + 11 * s, y - 12 * s), (x + 11 * s, y - 8 * s), (x + 3 * s, y - 12 * s)]))
    return [F(g, col, lift=.6, fuzz=False)]


def garbage_truck():
    o = []
    box = kit.soft(kit.G([(-48, -20), (12, -30), (14, -30), (14, 14), (-48, 14)]), 7)
    o.append(F(R(-52, -4, 10, 18, 3), DSTEEL, lift=.6))
    o.append(F(box, YEL, st=YEL_T, inset=2.8))
    for y in (-8, 2):
        o.append(L([(-40, y), (6, y - 5)], "#E8A912", 2.2))
    cab = kit.soft(kit.G([(16, -24), (32, -24), (48, -6), (48, 16), (16, 16)]), 6)
    o.append(F(cab, WHITE, st="#D8DCE6", inset=2.6))
    o.append(F(cab.intersection(sbox(0, 6, 60, 11)), "#3FBF73", lift=0))
    o.append(F(kit.soft(kit.G([(20, -19), (31, -19), (42, -6), (20, -6)]), 3), GLASS, lift=.5))
    o += eyes((25, 34), -12.5, 3.4, look=.5)
    o += mouth(32, 1, 3.2)
    o += wheel(-28, 16, 10) + wheel(30, 16, 10)
    return o


def bicycle():
    o = []
    for x in (-28, 28):
        o.append(F(E(x, 12, 18).difference(E(x, 12, 13.5)), TYRE, lift=.6))
        for a in (0, 60, 120):
            ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
            o.append(L([(x - 13 * ca, 12 - 13 * sa), (x + 13 * ca, 12 + 13 * sa)], "#B4BACB", 1.4))
        o.append(BTN(x, 12, 3.2, HUB))
    fr = ORA
    for a, b in (((-28, 12), (-10, -14)), ((-28, 12), (-2, 14)), ((-2, 14), (-10, -14)), ((-10, -14), (17, -14)),
                 ((-2, 14), (17, -14)), ((17, -14), (28, 12))):
        o.append(L([a, b], fr, 4.4))
    o.append(L([(-10, -14), (-12, -20)], DSTEEL, 3))
    o.append(F(kit.soft(kit.G([(-22, -24), (-6, -23), (-6, -19), (-20, -18)]), 2), "#5A4A55", lift=.6))
    o.append(L([(17, -14), (16, -24), (10, -28)], DSTEEL, 3.2))
    o.append(F(kit.soft(kit.G([(20, -26), (40, -26), (37, -12), (22, -12)]), 2.4), "#D9A25F", st="#FFE6C2", inset=1.3))
    for x, c in ((25, PINK), (33, "#FFE066")):
        o.append(F(E(x, -28, 3.6), c, lift=.5, fuzz=False))
    o.append(BTN(-2, 14, 3, DSTEEL))
    return o


def scooter():
    o = []
    o += wheel(-26, 18, 11) + wheel(28, 18, 11)
    o.append(F(tube(crs([(16, 12), (20, 2), (30, -1), (40, 6)], 6, closed=False), 5), "#3DBFA8", lift=.6))
    body = U(kit.soft(kit.G([(-40, 8), (-38, -8), (-26, -17), (-2, -17), (4, -4), (6, 8)]), 6),
             R(-8, 2, 30, 9, 4), kit.soft(kit.G([(14, 10), (19, -24), (27, -32), (35, -26), (33, 10)]), 4))
    o.append(F(body, "#5ED3BE", st="#E0FBF5", inset=2.4))
    o.append(F(kit.soft(R(-36, -26, 34, 10, 5), 1), "#5A4A55", lift=.6))
    o.append(L([(27, -31), (31, -40)], DSTEEL, 3.2))
    o.append(L([(31, -40), (24, -42)], DSTEEL, 3.4))
    o.append(L([(30, -40), (35, -48)], DSTEEL, 1.8))
    o.append(F(E(36, -50, 4.4, 3), GLASS, lift=.5, fuzz=False))
    o.append(F(E(33, -18, 3.4, 4.6), LAMP, lift=.4, fuzz=False))
    o.append(F(E(-39, -5, 2.4, 3.4), "#FF4D5E", lift=.4, fuzz=False))
    helmet = E(-18, -27, 11, 10).intersection(sbox(-40, -40, 0, -27))
    o.append(F(helmet, "#FFC21F", st="#FFF4C8", inset=1.6, lift=.6))
    o.append(F(R(-30, -30, 24, 4, 2), "#E8A912", lift=0, fuzz=False))
    return o


def traffic_light(sq=False):
    """A traffic light about 34 x 102 units, round (0, 0): a box of three big lamps on a short pole.
    sq: pixel lamps as squares that land on whole pixels (only right for deco_3's placement)."""
    o = [F(R(-3.5, 14, 7, 24, 3), STEEL, lift=.6), F(R(-13, 36, 26, 8, 4), DSTEEL, lift=.6)]
    o.append(F(R(-17, -57, 34, 72, 11), DSTEEL, st=STEEL_T, inset=2.2))
    for y, k in ((-20 / .46, "r"), (-10 / .46, "y"), (0, "g")):
        o.append(F(E(0, y, 8.6), SIGNAL[k], lift=.5, only="ac" if sq else None))
        o.append(F(E(-2.8, y - 3, 2.4, 1.6, rot=-30), "#FFFFFF", lift=0, fuzz=False, op=.8, only="ac"))
        if sq:
            hx, hy = 6 / .92, 7.2 / .92      # 3 x 3 pixels (over 3.5 pixels tall, so not drawn as a dot)
            o.append(F(R(-hx, y - hy, 2 * hx, 2 * hy), SIGNAL[k], lift=.5, only="b"))
    return o


def house(roof=BLUE, roof_st=BLUE_T, door="#F2574A"):
    o = [F(R(14, -36, 10, 18, 2.5), "#C8664C", lift=.6)]
    o.append(F(R(-30, -8, 60, 44, 4), CREAM, st=CREAM_T, inset=2.4))
    o.append(F(kit.soft(kit.G([(-39, -4), (0, -40), (39, -4)]), 4), roof, st=roof_st, inset=2.6))
    o.append(F(E(0, -16, 5.4), LAMP, lift=.5))
    o.append(F(R(-8, 10, 16, 26, 7).intersection(sbox(-10, 0, 10, 36)), door, lift=.5))
    o.append(BTN(4, 24, 1.8, "#FFC21F"))
    for x in (-25, 12):
        o.append(F(R(x, 2, 13, 13, 3), GLASS, lift=.5))
        o.append(F(E(x + 4.4, 5.8, 2.4, 1.6, rot=-30), "#FFFFFF", lift=0, fuzz=False, op=.85))
    return o


def shop():
    """A little fruit shop: a striped awning, a window with fruit, a door; an apple on the sign."""
    o = [F(R(-34, -20, 68, 56, 4), "#FFD8E2", lift=1)]
    o.append(F(R(-30, -38, 60, 14, 5), TEAL, st=TEAL_T, inset=1.8))
    o.append(F(E(0, -30, 4.6, 4.2), "#F2453D", lift=.4, fuzz=False))
    o.append(F(E(2.4, -35.5, 2.4, 1.3, rot=-30), "#3FBF73", lift=0, fuzz=False))
    aw = U(R(-40, -24, 80, 13, 2), *[E(-35 + 10 * i, -11, 5) for i in range(8)])
    o.append(F(aw, WHITE, st=None, lift=.8, fuzz=False))
    for i in range(8):
        if i % 2 == 0:
            o.append(F(aw.intersection(sbox(-40 + 10 * i, -40, -30 + 10 * i, 0)), ORA, lift=0, fuzz=False))
    o.append(F(R(-28, 0, 32, 22, 3), GLASS, lift=.5))
    o.append(F(R(-27, 15, 30, 7, 2), WOOD, lift=.4))
    for i, (x, y) in enumerate(((-22, 12), (-15, 12), (-8, 12), (-1, 12), (-18, 6), (-11, 6), (-4, 6))):
        o.append(F(E(x, y, 3.2), ("#F2453D", "#FF9A3C", "#FFE066")[i % 3], lift=.4, fuzz=False))
    o.append(F(R(10, 0, 18, 36, 3), "#4A8FE7", lift=.5))
    o.append(F(R(13, 4, 12, 12, 2), GLASS, lift=0, fuzz=False))
    o.append(BTN(23, 20, 1.6, "#FFC21F"))
    return o


def city_tree():
    o = [F(R(-5, 4, 10, 30, 4), BROWN, st="#E0B79C", inset=1.8)]
    o.append(F(E(0, -14, 30, 27), "#4DB860", st="#D6F3D0", inset=3))
    for x, y, r in ((-12, -24, 6), (10, -6, 5), (-6, -2, 4), (14, -26, 4.4)):
        o.append(F(E(x, y, r, r * .8), "#86D97C", lift=0, fuzz=False))
    o.append(F(R(-15, 28, 30, 11, 5), PAVE, st=None, lift=.6))
    return o


def bench_lamp():
    o = [F(R(-39, 40, 18, 7, 3.5), DGRN, lift=.6), F(R(-33, -34, 6, 78, 3), DGRN, st=None, lift=.6)]
    o.append(F(R(-43, -49, 24, 6, 3), DGRN, lift=.6))
    o.append(F(kit.soft(kit.G([(-41, -43), (-23, -43), (-26, -28), (-38, -28)]), 1.6), LAMP, lift=.6))
    o.append(BTN(-31, -52, 2.4, DGRN))
    for x in (-12, 30):
        o.append(F(R(x, 14, 5, 22, 2), DSTEEL, lift=.6))
    for y in (-6, 3):
        o.append(F(R(-18, y, 58, 7, 3.5), WOOD, lift=.8))
    o.append(F(R(-21, 14, 64, 8, 4), WOOD, st=WOOD_T, inset=1.4))
    return o


def mailboxes():
    """Taiwan's pair of post boxes, green and red: a domed cap, one leg, a slot under the cap with a
    letter going in."""
    o = []
    for x0, col, st, rot in ((-31, "#2FA65A", "#CDEFD3", 12), (3, "#E8483F", "#FFE0D8", -12)):
        o.append(F(R(x0 + 4, 32, 20, 6, 3), DSTEEL, lift=.6))
        o.append(F(R(x0 + 9, 20, 10, 16, 2), DSTEEL, lift=.6))
        o.append(F(R(x0 + 2, -14, 24, 38, 4), col, st=st, inset=2))
        cap = U(R(x0 - 1, -21, 30, 9, 3), E(x0 + 14, -21, 15, 9).intersection(sbox(-60, -40, 60, -20)))
        o.append(F(cap, kit.dk(col, .18), lift=.6))
        o.append(F(R(x0 + 6, -7, 16, 3.6, 1.8), "#2B2734", lift=0, fuzz=False))
        env = kit.tf([(-7, -9), (7, -9), (7, 1), (-7, 1)], x0 + 14, -5.5, rot=rot)
        o.append(F(kit.G(env), WHITE, lift=.5, fuzz=False, only="ac"))
        o.append(L(kit.tf([(-5.6, -7.6), (0, -3.6), (5.6, -7.6)], x0 + 14, -5.5, rot=rot), col, 1.3, only="ac"))
        o.append(F(R(x0 + 8, -16, 12, 10), WHITE, lift=.5, fuzz=False, only="b"))
    return o


def station(sign=True):
    """The bus station round (0, 0): a teal roof on two posts, a glass back, a bench, a platform and
    a round blue sign with a white bus on top (about 100 x 100 units)."""
    o = [F(R(-46, 30, 92, 12, 6), PAVE, lift=1)]
    o.append(F(R(-34, -12, 68, 40, 4), GLASS, lift=.6))
    for x in (-42, 35):
        o.append(F(R(x, -16, 7, 48, 3), STEEL, lift=.6))
    for x in (-23, 17):
        o.append(F(R(x, 16, 5, 14, 2), DSTEEL, lift=.5))
    o.append(F(R(-27, 1, 54, 7, 3.5), WOOD, lift=.6))
    o.append(F(R(-29, 11, 58, 8, 4), WOOD, st=WOOD_T, inset=1.4, lift=.6))
    scal = U(R(-48, -18, 96, 6, 2), *[E(-42 + 12 * i, -12, 6) for i in range(8)])
    o.append(F(scal, WHITE, st=None, lift=.6, fuzz=False))
    top = crs([(-50, -16), (-46, -27), (-26, -35), (0, -38), (26, -35), (46, -27), (50, -16)], 8, closed=False)
    o.append(F(kit.G(top + [(50, -15), (-50, -15)]), TEAL, st=TEAL_T, inset=2.6))
    if sign:
        o.append(F(R(-2, -46, 4, 10, 1.5), STEEL, lift=.5, fuzz=False))
        o.append(F(E(0, -50, 11), "#3D7BE0", st="#FFFFFF", inset=1.6))
        o.append(F(R(-6.5, -55, 13, 8.5, 2.6), WHITE, lift=0, fuzz=False))
        o.append(F(R(-4.6, -53.4, 9.2, 3, 1), "#3D7BE0", lift=0, fuzz=False))
        for x in (-3.5, 3.5):
            o.append(F(E(x, -45.5, 1.8), WHITE, lift=0, fuzz=False))
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


def grass(x, y, s=1.0, col=DGRN, only="ac"):
    g = U(kit.G([(-8, 0), (-6, -12), (-3, 0)]), kit.G([(-3, 0), (0, -16), (3, 0)]), kit.G([(3, 0), (6, -11), (8, 0)])).buffer(1.2)
    return [F(kit.affinity.affine_transform(g, [s, 0, 0, s, x, y]), col, lift=.6, only=only)]


# ================================================================ the files
def hero(st):
    return place(OBJ(bus()), 50, 55, .96)


def home(st):
    return place(OBJ(station()), 50, 57, .88)


def family(st):
    """Home at last: the little bus cuddles up to its family (a big blue bus, a tiny yellow bus) at
    the station."""
    o = OBJ(place(station(), 200, 136, 2.0))
    for x, y, s, c in ((52, 126, 14, PINK), (350, 118, 13, "#FF6B6B"), (344, 46, 10, "#FFB3C8"), (56, 46, 9, PINK)):
        o += OBJ(place(heart(s, c), x, y))
    mound = kit.G(crs([(14, 336), (90, 306), (200, 300), (310, 306), (386, 336), (310, 366), (200, 374), (90, 366)], 6))
    o += OBJ([F(mound, LAWN, st="#FFFFFF", inset=4)])
    o += OBJ(place(bus(BLUE, BLUE_T, happy=True, stripe=YEL), 110, 282, 1.66))
    o += OBJ(place(bus(happy=True), 258, 300, 1.22, flip=True))
    o += OBJ(place(bus(YEL, YEL_T, happy=True, cheek=CHEEK, stripe=TEAL), 348, 322, .82, flip=True))
    for x, y, r in ((26, 230, 10), (376, 226, 10), (128, 28, 8), (276, 26, 8)):
        o += OBJ(sparkle(x, y, r), shadow=0)
    return o


def star(st):
    return OBJ([F(star_shape(40, 50, 53), "#FFD23F", st="#FFFFFF", inset=3.6),
                F(E(37, 38, 4.2, 2.6, rot=-35), "#FFFFFF", lift=0, fuzz=False, op=.85)])


def key(st):
    bow = U(E(-18, 0, 16)).difference(E(-18, 0, 6.5))
    g = U(bow, R(-4, -5, 40, 10, 4), R(16, 3, 7, 12, 2.5), R(27, 3, 7, 9, 2.5))
    return place(OBJ([F(g, "#FFC83D", st="#FFF6CF", inset=2.4), F(E(-18, -12.5, 4.4, 2.4), "#FF6B6B", lift=0, fuzz=False)]),
                 52, 52, 1.12, rot=-30)


def gate(st):
    """A red-and-white barrier arm standing across a left-right road: its post box below the road
    (with the pivot), the arm resting on a little post above it, a padlock in the middle."""
    o = [F(R(40, 0, 20, 10, 4), STEEL, lift=.6)]
    arm = R(40, 4, 20, 86, 10)
    o.append(F(arm, WHITE, st=None))
    for k in range(-1, 6):
        y0 = 4 + 18 * k
        band = kit.G([(30, y0 + 12), (70, y0 + 2), (70, y0 + 11), (30, y0 + 21)])
        o.append(F(arm.intersection(band), "#F2453D", lift=0, fuzz=False))
    o.append(F(E(50, 11, 4.4), "#FF4D4D", lift=.5, fuzz=False))
    o.append(F(R(30, 78, 40, 20, 7), YEL, st=YEL_T, inset=2))
    o.append(BTN(50, 86, 5, STEEL))
    o.append(F(tube(crs([(43, 52), (43, 42), (50, 36), (57, 42), (57, 52)], 6, closed=False), 4.4), "#B8BCC8", lift=.6))
    o.append(F(R(38, 47, 24, 20, 5.5), "#FFC83D", st="#FFF6CF", inset=1.8))
    o.append(F(U(E(50, 54.5, 3), R(48.7, 54.5, 2.6, 7, 1)), DARK, lift=0, fuzz=False, only="ac"))
    o.append(L([(50, 53), (50, 61)], DARK, 2.0, only="b"))
    return OBJ(o)


def deco_house(st):
    return place(OBJ(grass(-30, 36, .6)) + OBJ(house()), 50, 56, 1.0)


def deco_tree(st):
    return place(OBJ(city_tree()), 50, 52, 1.05)


def deco_light(st):
    return place(OBJ(traffic_light(sq=True)), 50, 54, .92)


def deco_shop(st):
    return place(OBJ(shop()), 50, 53, 1.0)


def deco_bench(st):
    return place(OBJ(bench_lamp()), 52, 51, .92)


def deco_mail(st):
    return place(OBJ(grass(-36, 34, .6)) + OBJ(mailboxes()), 52, 54, 1.08)


# ---------------------------------------------------------------- stickers (200 x 200, the kit adds the round sticker)
def s_bus(st):
    return place(OBJ(bus()), 100, 104, 1.5)


def s_light(st):
    return place(OBJ(traffic_light()), 100, 106, 1.62)


def s_taxi(st):
    return place(OBJ(car(YEL, YEL_T, "taxi")), 100, 106, 1.5)


def s_fire(st):
    return place(OBJ(fire_engine()), 100, 104, 1.45)


def s_police(st):
    return place(OBJ(car("#3D6FE0", "#DCE6FF", "police")), 100, 106, 1.5)


def s_bike(st):
    return place(OBJ(bicycle()), 100, 106, 1.6)


def s_scooter(st):
    return place(OBJ(scooter()), 100, 108, 1.5)


def s_house(st):
    return place(OBJ(house()), 100, 104, 1.65)


def s_tree(st):
    return place(OBJ(city_tree()), 100, 102, 1.6)


def s_garbage(st):
    o = OBJ(garbage_truck())
    o += OBJ(note(-28, -36, 1.0, "#FF6FA8")) + OBJ(note(-6, -44, .85, "#4A8FE7")) + OBJ(note(20, -40, .75, "#22B3A2"))
    return place(o, 102, 118, 1.42)


# ---------------------------------------------------------------- the home-page card (300 x 200)
def card(st):
    line = crs([(-40, 168), (40, 160), (110, 132), (170, 102), (230, 94), (340, 98)], 10, closed=False)
    road = tube(line, 48, cap="flat")
    o = [kit.ground_piece(WORLD, st)]
    o += OBJ(place(city_tree(), 128, 48, .5))
    o += OBJ(place(house(), 40, 52, .62))
    o += OBJ(place(traffic_light(), 202, 160, .54))
    o += OBJ(place(shop(), 268, 166, .5))
    o += OBJ(grass(86, 104, .9)) + OBJ(grass(150, 186, .8))
    o.append(kit.road_piece(WORLD, st, road, width=48))
    ln = LineString(line).intersection(sbox(-2, -2, 302, 202))
    o += centre_line(dashed(list(ln.coords), 13, 14), st, {"a": 4.0, "b": 4.0, "c": 5.0}[st])
    o += OBJ(place([F(star_shape(15, 0, 0), "#FFD23F", st="#FFFFFF", inset=1.8)], 152, 112))
    o += OBJ(place(station(), 254, 58, .58))
    o += OBJ(place(bus(), 66, 140, .66))
    return o


def bits(st):
    """Small things sewn on the felt lawn (a only; b and c have their own texture): little flower
    beds, stepping stones, round shrubs and grass."""
    if st != "a":
        return []
    rnd = kit.random.Random(23)
    o = []
    for i in range(26):
        x, y = rnd.uniform(24, 576), rnd.uniform(24, 776)
        t = i % 4
        if t == 0:
            bed = [F(R(-18, -7, 36, 14, 5), "#E9E8E1", lift=.6, fuzz=False), F(R(-14.5, -3.5, 29, 7, 3), SOIL, lift=0)]
            for k, dx in enumerate((-9, 0, 9)):
                bed.append(F(E(dx, -3, 3.4), ("#FF6B6B", "#FFE066", "#FFFFFF", "#FF9EC1")[(i + k) % 4], lift=.5, fuzz=False))
            o += place(bed, x, y, rot=rnd.uniform(-10, 10))
        elif t == 1:
            for k, (dx, dy) in enumerate(((-14, 2), (0, -2), (14, 2))):
                o.append(F(R(x + dx - 5, y + dy - 4.5, 10, 9, 3), "#E9E8E1", lift=.5, fuzz=False))
        elif t == 2:
            o.append(F(E(x, y, 10, 8), LAWN2, st="#CDEFD3", inset=1.8, lift=.6))
        else:
            o += place(grass(0, 0, 1.0, "#68B874"), x, y)
    return o


WORLD = CityWorld(
    "city", "城市",
    road=ROAD, ground=GROUND, pixel=PIXEL, jelly=JELLY, bits=bits, sticker=STICKER,
    hero=hero, home=home, family=family, star=star, key=key, gate=gate,
    deco=[deco_house, deco_tree, deco_light, deco_shop, deco_bench, deco_mail],
    stickers=[s_bus, s_light, s_taxi, s_fire, s_police, s_bike, s_scooter, s_house, s_tree, s_garbage],
    card=card,
)
