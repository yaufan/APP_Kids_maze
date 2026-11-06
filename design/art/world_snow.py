"""雪地 snow: a little penguin waddles home to its mum's igloo.

    python3 build.py snow        # writes app/assets/art/<a|b|c>/snow/*.svg and checks them

Built like world_garden.py (the template). The ground is a soft, slightly grey-lavender snow with
drifts and pale-blue shadows; the road is clearly bluer ice (felt: icy-blue felt with white
stitches; pixels: light-blue ice with a white shine row and a dark-blue border; jelly: clear
ice-blue jelly), so the road never reads white-on-white.
"""
import math

import kit
from kit import BTN, E, EYE, F, L, OBJ, R, U, crs, place, sbox, soft, star_shape, tube

# ---------------------------------------------------------------- colours (style a, felt)
NAVY, NAVY_T = "#3E4C78", "#A3B3DA"        # penguin body and its stitch
FOOT = "#FF9E3D"
BEAK = "#FFB03B"
RED, RED_T = "#F2665C", "#FFE3DE"
PINK = "#FF9EC1"
BLUE, BLUE_T = "#5BA8E8", "#DDF0FF"
GRN, GRN_T = "#3FA66A", "#C6EBD2"           # pine green (bluer than the garden's)
TEAL = "#3FBFA8"
YEL, YEL_T = "#FFD23F", "#FFFFFF"
GOLD, GOLD_T = "#FFC83D", "#FFF6CF"
BRN, BRN_T = "#9A6B4F", "#D9B08F"
WOOD, WOOD_T = "#E5A869", "#FFE6C2"
SNOW, SNOW_ST = "#FBFDFF", "#A9C6E6"        # snow pieces (snowman, caps, drifts) and their stitch
ICE, ICE_T, ICE_L, ICE_D = "#A6DCF7", "#FFFFFF", "#D8F2FF", "#7FC2EC"
IGLOO, IGLOO2, BLOCK = "#F3F9FF", "#E2EFFB", "#9DC2E6"
DOOR = "#3D5A92"
ROCK, ROCK_T = "#9AA6BC", "#D5DCE8"
SEAL, SEAL_T, SEAL_D = "#A7B6CC", "#E6EDF6", "#8796B0"
WATER = "#7CC6F2"
CREAM, CREAM_T = "#FFF6E8", "#D8C4A6"
COAL = "#4A4F63"
HAT = "#414A6B"
WHITE = kit.WHITE
DARK, CHEEK = kit.DARK, kit.CHEEK

PIXEL = dict(
    outline="#1E2742",
    palette=["#FFFFFF", "#EAF4FF", "#C8E6FA", "#9AD8F8", "#5DB4EE", "#3B7FD0", "#2C4F8C", "#34416A",
             "#FFA53A", "#FFD23A", "#FF5A5F", "#FF8FBF", "#FFC2D6", "#3DB55B", "#2A8F47", "#1D6B3A",
             "#C98A55", "#9A5E3A", "#5A3828", "#B4C0D2", "#7E8BA3", "#FFF1D6", "#3FCFB0"],
    map={NAVY: "#34416A", NAVY_T: "#9AB0E0", SNOW: "#FFFFFF", WHITE: "#FFFFFF", IGLOO: "#FFFFFF", IGLOO2: "#EAF4FF",
         BLOCK: "#9AD8F8", ICE: "#9AD8F8", ICE_L: "#D8F4FF", ICE_D: "#5DB4EE", FOOT: "#FF9F1C", BEAK: "#FFB52E",
         CHEEK: "#FF8FA8", PINK: "#FF8FBF", RED: "#FF5A5F", GRN: "#2FA35A", ROCK: "#9AA8C0", SEAL: "#B4C0D2",
         SEAL_D: "#7E8BA3", CREAM: "#FFF6E6", HAT: "#34416A", COAL: "#34416A", DOOR: "#2C4F8C", WATER: "#5DB4EE",
         GOLD: "#FFC21F", YEL: "#FFD23A"},
)
JELLY = dict(shadow="#4F5FA8", map={NAVY: "#4A5C96", SNOW: "#F4F9FF", WHITE: "#F7FBFF", IGLOO: "#F2F8FF",
                                    GRN: "#3FBF78", ROCK: "#A3AFC6", SEAL: "#AEBDD4", DOOR: "#4467A8"})

ROAD = {
    "a": dict(fill="#8CCBF3", stitch="#FFFFFF"),
    "b": dict(fill="#9AD8F8", speck="#C8EEFF", shade="#6CBBEB", light="#F0FAFF", border="#2F65B0"),
    "c": dict(body="#A4D8FF", rim="#4F95E0", glow="#F4FBFF", shadow="#4F5FA8"),
}
FLAKES_PX = [{"s": "#B9CEEC", "w": "#FFFFFF"}, {"s": "#C9D5F2", "w": "#FFFFFF"}]
GROUND = {
    "a": dict(base="#E4E8F1", fibres=("#F3F5FA", "#D2D9E6")),
    "b": dict(base="#E6ECF5", specks=[("#FFFFFF", .05), ("#D3DDEC", .05)],
              stamps=[(["s.s", ".w.", "s.s"], FLAKES_PX, 1.0), ([".s.", "sws", ".s."], FLAKES_PX, 1.0),
                      (["...www...", ".wwwwwww.", "wwwwwwwww", "bbbbbbbbb"], {"w": "#FFFFFF", "b": "#C3D2EA"}, .45)]),
    "c": dict(top="#F1F3FF", bottom="#DCE3F8", swirl="#FFFFFF",
              sprinkles=("#FFFFFF", "#8FD0FF", "#B9A8FF", "#FF9EC8", "#7FE0E8"), n=10),
}
STICKER = dict(fill="#DDEFFF", stitch="#FFFFFF", fill_b="#D8F4FF", fill_c="#E3F2FF")


# ================================================================ characters and things (round (0, 0))
def penguin(look=0.0, happy=False, scarf=RED, bow=None, hat=None, flap=False):
    """The round penguin, about 76 x 76 units round (0, 4) (head top y = -34, feet to y = 42).
    look > 0 turns the face to the right (9 = the hero's three-quarter view)."""
    o = []
    ax = look
    t = max(0.0, min(1.0, look / 9))
    for x in (-12, 12):
        o.append(F(E(x + look * .35, 37, 10, 5.2), FOOT, lift=.6))
    body = E(0, 2, 31, 36)
    o.append(F(body, NAVY, st=NAVY_T))
    # the white face (two round patches meeting under a little peak) and the belly
    face = U(E(ax - 8, -10, 12, 11.5), E(ax + 8, -10, 12, 11.5), E(ax * .45, 19, 20, 17)).intersection(body.buffer(-3.2))
    o.append(F(face, WHITE, lift=0))
    for sgn in (-1, 1):
        if flap:
            g = E(sgn * 32, -4, 6.5, 15, rot=sgn * 42)
        else:
            g = E(sgn * 29.5, 12, 6.5, 15, rot=-sgn * 18)
        o.append(F(g, NAVY, lift=.6))
    if scarf:
        tail = kit.G(kit.tf(kit.rrect_pts(-4, 0, 8.5, 19, 3.6), -17 - look * .35, 9, 14))
        o.append(F(tail, kit.dk(scarf, .08), lift=.5))
        band = soft(body.buffer(1.8).intersection(sbox(-45, 7, 45, 13.8)), 1.4)
        o.append(F(band, scarf, st="#FFFFFF", inset=1.6, lift=.6))
    if happy:
        for x in (ax - 8, ax + 8):
            o.append(L([(x - 4.6, -8), (x, -13), (x + 4.6, -8)], DARK, 2.4))
    else:
        o.append(EYE(ax - 8, -10, 4.4, look=(look * .12, 0)))
        o.append(EYE(ax + 8, -10, 4.4, look=(look * .12, 0)))
    for x in (ax - 15, ax + 15):
        ck = E(x, -1, 4, 3).intersection(body.buffer(-2))
        if not ck.is_empty:
            o.append(F(ck, CHEEK, lift=0, fuzz=False))
    beak = [(ax - 6.5 + 1.5 * t, -4 - t), (ax + 6.5 + 7 * t, -4 + 3.5 * t), (ax - 5 * t, 5.5 - .5 * t)]
    o.append(F(soft(kit.G(beak), 1.3), BEAK, lift=.5, only="ac"))
    # pixels: a chunkier beak (a thin triangle rasterises to a "+")
    beak_b = [(ax - 7 + 2 * t, -5), (ax + 7 + 6 * t, -5 + 2 * t), (ax + 3.5 + 6 * t, 4), (ax - 3.5 + t, 4.5)]
    o.append(F(kit.G(beak_b), BEAK, lift=.5, only="b"))
    if bow:
        bx = ax * .4
        o.append(F(E(bx - 8, -33, 8.5, 6, rot=-20), bow, st="#FFFFFF", inset=2.2))
        o.append(F(E(bx + 8, -33, 8.5, 6, rot=20), bow, st="#FFFFFF", inset=2.2))
        o.append(F(E(bx, -33, 3.8), kit.dk(bow, .15), lift=.5, fuzz=False))
    if hat:
        cap = body.buffer(2.2).intersection(sbox(-40, -50, 40, -23))
        o.append(F(cap, hat, st="#FFFFFF", inset=2))
        brim = soft(body.buffer(3.2).intersection(sbox(-40, -27, 40, -20.5)), 1.4)
        o.append(F(brim, kit.lt(hat, .55), lift=.5))
        o.append(F(E(ax * .2, -38.5, 6.5), "#FFFFFF", lift=.6))
    return o


def snowflake_shape(r, w):
    """A six-armed snowflake as one shape (arms with a little V on each)."""
    parts = [E(0, 0, w * .9)]
    for i in range(6):
        a = math.radians(-90 + 60 * i)
        ca, sa = math.cos(a), math.sin(a)
        parts.append(tube([(0, 0), (r * ca, r * sa)], w))
        mx, my = r * .55 * ca, r * .55 * sa
        for s in (-1, 1):
            b = a + s * math.radians(48)
            parts.append(tube([(mx, my), (mx + .34 * r * math.cos(b), my + .34 * r * math.sin(b))], w * .8))
    return U(*parts)


def flake_lines(x, y, r, col, w, only=None):
    """An embroidered snowflake: three crossing lines and a V near each end."""
    o = []
    for i in range(3):
        a = math.radians(90 + 60 * i)
        o.append(L([(x - r * math.cos(a), y - r * math.sin(a)), (x + r * math.cos(a), y + r * math.sin(a))], col, w, only=only))
    for i in range(6):
        a = math.radians(90 + 60 * i)
        mx, my = x + .6 * r * math.cos(a), y + .6 * r * math.sin(a)
        pts = []
        for s in (-1, 1):
            b = a + s * math.radians(50)
            pts.append((mx + .32 * r * math.cos(b), my + .32 * r * math.sin(b)))
        o.append(L([pts[0], (mx, my), pts[1]], col, w * .85, only=only))
    return o


def flake(r=10, col=BLUE, st="#FFFFFF"):
    return [F(snowflake_shape(r, max(2.2, r * .2)), col, st=st if r > 14 else None, inset=1.4, lift=.5)]


FLAKE_PX = ["...x...", ".x.x.x.", "..xxx..", "xxxoxxx", "..xxx..", ".x.x.x.", "...x..."]


HEART_PX = [".xx.xx.", "xoxxxxx", "xxxxxxx", ".xxxxx.", "..xxx..", "...x..."]


def pix_sprite(rows, cx, cy, px, cols, outline=None):
    """Pixel art laid exactly on a file's pixel grid (b only; px = KIND[...]["px"]), centred near
    (cx, cy): rows of characters, cols {char: colour}; `outline`: a colour round it. No bevel."""
    if outline:
        w0 = max(len(r) for r in rows)
        g = [["."] * (w0 + 2)] + [["."] + list(r.ljust(w0, ".")) + ["."] for r in rows] + [["."] * (w0 + 2)]
        for j in range(len(g)):
            for i in range(len(g[0])):
                if g[j][i] == "." and any(0 <= j + dj < len(g) and 0 <= i + di < len(g[0]) and g[j + dj][i + di] not in ".k"
                                          for dj, di in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                    g[j][i] = "k"
        rows = ["".join(r) for r in g]
        cols = dict(cols, k=outline)
    h, w = len(rows), max(len(r) for r in rows)
    i0, j0 = round(cx / px - w / 2), round(cy / px - h / 2)
    o = []
    for ch, col in cols.items():
        boxes = [sbox((i0 + i) * px + .2, (j0 + j) * px + .2, (i0 + i + 1) * px - .2, (j0 + j + 1) * px - .2)
                 for j, row in enumerate(rows) for i, c in enumerate(row) if c == ch]
        if boxes:
            o.append(F(U(*boxes), col, lift=0, po=False, shade=False, fuzz=False, only="b"))
    obj = OBJ(o, shadow=-1)        # lift < 0: no pixel outline round it
    return [obj[0].copy(only="b")] + obj[1:]


def twinkle(x, y, r, px, col="#8FCBF2"):
    """A floating snowflake in a file's final units: a felt / jelly flake (a, c) or a pixel flake (b)."""
    o = OBJ(place(flake(r, col), x, y), shadow=0)
    o = [q.copy(only="ac") for q in o]
    return o + pix_sprite(FLAKE_PX, x, y, px, {"x": col, "o": "#FFFFFF"})


def heart_at(x, y, s, col, px):
    """A heart in a file's final units: felt / jelly (a, c) or a pixel heart with an outline (b)."""
    o = [q.copy(only="ac") for q in OBJ(place(heart(s, col), x, y))]
    return o + pix_sprite(HEART_PX, x, y, px, {"x": PIXEL["map"].get(col, col), "o": "#FFFFFF"}, PIXEL["outline"])


def igloo(base=True, flag=True):
    """The igloo: a dome (92 wide, top y = -32, ground y = 10) of ice blocks with a round-arched door
    in a little entrance tunnel (base y = 16); a red pennant on top; a snow mound under it."""
    o = []
    if base:
        o.append(F(E(0, 15, 54, 9), SNOW, st=SNOW_ST, inset=2.2, cols={"b": "#C8E6FA"}))
    if flag:
        o.append(L([(17, -24), (20, -55)], BRN, 2.8))
        o.append(F(soft(kit.G([(19.4, -55), (42, -47), (20.6, -38.5)]), 1.4), RED, lift=.5))
    dome = soft(E(0, 10, 46, 42).intersection(sbox(-50, -40, 50, 10)), 2)
    o.append(F(dome, IGLOO, st="#FFFFFF", inset=3))
    inner = dome.buffer(-2.6)
    rows = (-19, -5)
    for y0 in rows:
        ln = kit.LineString([(x, y0 + 3.5 * (1 - (x / 46) ** 2)) for x in range(-48, 49, 4)]).intersection(inner)
        for part in kit.lines_of(ln):
            o.append(L(list(part.coords), BLOCK, 1.8))
    joints = ((-32, -19, (-12, 14)), (-19, -5, (-28, 0, 27)), (-5, 10, (-36, 34)))
    for ya, yb, xs in joints:
        for x in xs:
            ya2 = ya + 3.5 * (1 - (x / 46) ** 2)
            yb2 = yb + 3.5 * (1 - (x / 46) ** 2) if yb < 10 else yb
            seg = kit.LineString([(x, ya2 + 1), (x, yb2 - 1)]).intersection(inner)
            for part in kit.lines_of(seg):
                if part.length > 3:
                    o.append(L(list(part.coords), BLOCK, 1.8))
    tunnel = soft(E(0, 16, 21, 27).intersection(sbox(-30, -20, 30, 16)), 1.5)
    o.append(F(tunnel, IGLOO2, st=SNOW_ST, inset=2.2))
    door = E(0, 16, 12, 17).intersection(sbox(-20, -10, 20, 16))
    o.append(F(door, DOOR, lift=0, fuzz=False))
    o.append(F(E(-4.5, 4, 3, 4.2).intersection(door), kit.lt(DOOR, .25), lift=0, fuzz=False, only="ac"))
    return o


def heart(s=12, col=PINK):
    return [F(kit.heart_pts(0, 0, s), col, st="#FFFFFF", inset=1.6 if s < 12 else 2.2)]


def snowman(scarf=TEAL):
    """A two-ball snowman with a top hat, coal buttons, a carrot nose; about 76 x 90 round (0, -5)."""
    o = []
    for sgn in (-1, 1):
        o.append(L([(sgn * 14, 4), (sgn * 30, -6), (sgn * 37, -15)], BRN, 2.8))
        o.append(L([(sgn * 30, -6), (sgn * 38, -5)], BRN, 2.2))
    bottom = E(0, 18, 25, 21)
    head = E(0, -16, 17, 16)
    o.append(F(bottom, SNOW, st=SNOW_ST, inset=2.8))
    o.append(F(head, SNOW, st=SNOW_ST, inset=2.4))
    if scarf:
        o.append(F(kit.G(kit.tf(kit.rrect_pts(-4, 0, 8, 17, 3.4), 11, 1, -12)), kit.dk(scarf, .1), lift=.5))
        band = soft(U(head, bottom).buffer(1.6).intersection(sbox(-30, -3.5, 30, 4)), 1.3)
        o.append(F(band, scarf, st="#FFFFFF", inset=1.4, lift=.6))
    for y in (13, 24):
        o.append(BTN(0, y, 2.8, COAL))
    o.append(EYE(-6, -20, 2.7))
    o.append(EYE(6, -20, 2.7))
    o.append(F(E(-11, -12, 3.2, 2.4), CHEEK, lift=0, fuzz=False))
    o.append(F(E(11, -12, 3.2, 2.4), CHEEK, lift=0, fuzz=False))
    o.append(F(soft(kit.G([(-1.5, -16.8), (16.5, -12.5), (-1.5, -8.6)]), .9), "#FF8A3D", lift=.5))
    o.append(L([(-6, -7.5), (0, -5), (6, -7.5)], DARK, 1.8))
    o.append(F(R(-15, -34, 30, 5, 2.4), HAT, lift=.6))
    o.append(F(R(-10, -52, 20, 20, 3), HAT, lift=.6))
    o.append(F(R(-10, -38.5, 20, 4.5, 1), RED, lift=0))
    return o


def pine(snow=True):
    """A pine tree with snow on each tier: about 72 x 84 round (0, -4)."""
    o = [F(R(-6, 22, 12, 16, 3), BRN, st=BRN_T, inset=1.8)]
    tiers = ((-14, 28, 36), (-30, 8, 29), (-46, -12, 21))
    for ay, by, hw in tiers:
        tri = soft(kit.G([(0, ay), (hw, by), (hw * .5, by + 3), (0, by + 1), (-hw * .5, by + 3), (-hw, by)]), 3)
        o.append(F(tri, GRN, st=GRN_T, inset=2.4))
        if snow:
            yc = ay + (by - ay) * .4
            cap = U(sbox(-50, ay - 4, 50, yc), *[E(x, yc, 4.2) for x in range(-48, 49, 8)]).intersection(tri.buffer(.6))
            o.append(F(soft(cap, .8), SNOW, lift=.4, st=None))
    return o


def ice_block(w=46, h=36, d=12, shine=True):
    """An ice cube in a little 3/4 view: front face (w x h) round (0, 0), the top and right faces."""
    x0, y0 = -w / 2 - d / 2, -h / 2 + d / 2
    o = []
    top = kit.G([(x0, y0), (x0 + d, y0 - d), (x0 + w + d, y0 - d), (x0 + w, y0)])
    side = kit.G([(x0 + w, y0), (x0 + w + d, y0 - d), (x0 + w + d, y0 + h - d), (x0 + w, y0 + h)])
    o.append(F(soft(top.buffer(.8), 1.5), ICE_L, lift=0))
    o.append(F(soft(side.buffer(.8), 1.5), ICE_D, lift=0))
    front = R(x0, y0, w, h, 4)
    o.append(F(front, ICE, st=ICE_T, inset=2.2, lift=.6))
    if shine:
        o.append(L([(x0 + .15 * w, y0 + .44 * h), (x0 + .35 * w, y0 + .19 * h)], "#FFFFFF", w * .056))
        o.append(L([(x0 + .17 * w, y0 + .69 * h), (x0 + .52 * w, y0 + .25 * h)], "#FFFFFF", w * .044))
    return o


def sled():
    """A red sled from the side, its runner curling up at the front (right); about 86 x 36."""
    o = []
    run = crs([(-40, 15), (-20, 17), (10, 17), (30, 16), (39, 9), (38, 0), (33, -1)], 6, closed=False)
    o.append(F(tube(run, 4.6), "#6E7FA6", lift=.6))
    for x in (-26, -6, 14):
        o.append(F(R(x - 2.2, 2, 4.4, 14, 1.5), "#B5413A", lift=.4))
    o.append(F(R(-36, -6, 64, 11, 4.5), RED, st=RED_T, inset=1.8))
    o.append(F(R(-36, -1.5, 64, 3, 1.2), YEL, lift=0, fuzz=False))
    o.append(L(crs([(27, -2), (36, -8), (44, -6), (48, -12)], 5, closed=False), "#C98A55", 2.0))
    return o


def seal():
    """A grey seal lying on its tummy, head up on the right; about 82 x 48 round (0, 0)."""
    o = []
    for rot, y in ((-28, 4), (28, 13)):
        o.append(F(E(-36, y, 9.5, 4.5, rot=rot), SEAL_D, lift=.5))
    body = soft(U(E(-8, 8, 28, 12.5), E(12, 0, 15, 14), E(19, -10, 14, 13)), 3)
    o.append(F(body, SEAL, st=SEAL_T, inset=2))
    o.append(F(E(2, 16, 9, 4.2, rot=22), SEAL_D, lift=.5))
    o.append(EYE(14, -14, 2.8))
    o.append(EYE(25, -14, 2.8))
    for x in (16, 23):
        o.append(F(E(x, -6, 4.2, 3.4), "#DCE4EF", lift=0, fuzz=False))
    o.append(F(E(19.5, -8.6, 2.6, 2), DARK, lift=0, fuzz=False))
    for sgn, x in ((-1, 13), (1, 26)):
        for dy in (-1.5, 1.5):
            o.append(L([(x, -6 + dy * .6), (x + sgn * 7, -6 + dy * 1.8)], "#6B7894", 1.0, only="ac"))
    o.append(F(E(9.5, -9, 2.8, 2.1), CHEEK, lift=0, fuzz=False))
    o.append(F(E(29.5, -9, 2.4, 2), CHEEK, lift=0, fuzz=False))
    return o


def floe():
    """A little hole of water with a flat ice floe in it; about 92 x 26 round (0, 0)."""
    water = E(0, 0, 46, 13)
    ice = kit.G(crs([(-36, -4), (-14, -9), (14, -9), (34, -5), (38, 3), (20, 8), (-12, 8), (-34, 5)], 6))
    return [F(water, WATER, st="#FFFFFF", inset=2), F(ice, SNOW, st=SNOW_ST, inset=2)]


def rock():
    big = soft(kit.G([(-34, 26), (-30, 2), (-16, -16), (4, -22), (24, -12), (32, 8), (30, 26)]), 6)
    small = soft(kit.G([(16, 30), (22, 14), (34, 10), (44, 18), (44, 30)]), 4)
    o = [F(big, ROCK, st=ROCK_T, inset=2.6)]
    cap = U(sbox(-50, -30, 50, -6), *[E(x, -6, 5, 4.4) for x in range(-48, 49, 9)]).intersection(big.buffer(.6))
    o.append(F(soft(cap, .8), SNOW, lift=.4))
    o.append(F(small, kit.dk(ROCK, .08), st=ROCK_T, inset=1.8))
    cap2 = U(sbox(10, 0, 50, 15.5), *[E(x, 15.5, 3, 2.6) for x in range(16, 48, 5)]).intersection(small.buffer(.5))
    o.append(F(soft(cap2, .6), SNOW, lift=.3))
    for x, y in ((-14, 8), (2, 14), (-20, 18)):
        o.append(F(E(x, y, 2.4, 1.8), kit.dk(ROCK, .15), lift=0, fuzz=False))
    return o


def drift(w=40, h=12, only=None):
    """A soft snow drift (a mound) whose bottom is at y = 0, with a pale-blue shadow under it."""
    g = U(E(-w * .25, 0, w * .45, h), E(w * .2, 0, w * .38, h * .78)).intersection(sbox(-w, -h * 2, w, 0))
    sh = U(E(-w * .1, .5, w * .58, h * .32))
    return [F(sh, "#C9D6EA", lift=0, fuzz=False, only=only), F(soft(g, 1.2), SNOW, lift=.4, only=only)]


# ================================================================ the files
def hero(st):
    return place(OBJ(penguin(look=9)), 50, 46, 1.1)


def home(st):
    return place(OBJ(igloo()), 50, 61, .9)


def family(st):
    """Home at last: the little penguin hugs mum (pink bow) and dad (bobble hat) at the igloo."""
    o = OBJ(place(igloo(base=False), 200, 134, 2.3))
    for x, y, r in ((46, 70, 14), (354, 62, 12), (40, 206, 11), (362, 196, 11)):
        o += twinkle(x, y, r, 5)
    for x, y, s, c in ((58, 140, 14, PINK), (344, 132, 12, RED)):
        o += heart_at(x, y, s, c, 5)
    mound = kit.G(crs([(26, 344), (88, 312), (200, 304), (312, 312), (374, 344), (312, 370), (200, 378), (88, 370)], 6))
    o += OBJ([F(mound, SNOW, st=SNOW_ST, inset=4)])
    o += OBJ(place(penguin(happy=True, flap=True, scarf=PINK, bow=PINK), 124, 262, 1.5, rot=8))
    o += OBJ(place(penguin(happy=True, flap=True, scarf=BLUE, hat=BLUE), 280, 256, 1.58, rot=-8))
    o += OBJ(place(penguin(happy=True, flap=True, scarf=RED), 202, 302, 1.1))
    for x, y, s in ((202, 210, 9), (150, 178, 7), (252, 176, 7.5)):
        o += [q.copy(only="ac") for q in OBJ(place(heart(s, PINK if s < 8 else RED), x, y))]
    o += pix_sprite(HEART_PX, 202, 206, 5, {"x": PIXEL["map"][RED], "o": "#FFFFFF"}, PIXEL["outline"])
    return o


def star(st):
    o = [F(star_shape(40, 50, 53), YEL, st=YEL_T, inset=3.6)]
    o += flake_lines(50, 55, 9, "#FFFFFF", 2.0, only="ac")
    o.append(F(E(37, 38, 4.2, 2.6, rot=-35), "#FFFFFF", lift=0, fuzz=False, op=.85))
    return OBJ(o)


def key(st):
    bow = E(-18, 0, 16).difference(E(-18, 0, 6.5))
    g = U(bow, R(-4, -5, 40, 10, 4), R(18, 3, 7, 11, 2.5), R(28, 3, 7, 8, 2.5))
    o = [F(g, GOLD, st=GOLD_T, inset=2.4)]
    gem = kit.G([(-18, -11.8), (-14.2, -8.6), (-18, -5.4), (-21.8, -8.6)])
    o.append(F(gem, "#7CC8F2", lift=.4, fuzz=False))
    return place(OBJ(o), 52, 52, 1.12, rot=-30)


def gate(st):
    """A wooden gate with snow on top and little icicles, standing across a left-right road."""
    o = []
    for x in (27, 73):
        o.append(F(R(x - 6, 12, 12, 82, 4), "#A8714E", st="#E6C3A2", inset=2))
    for y in (30, 72):
        o.append(F(R(31, y, 38, 8, 3), "#B97F4E", lift=.6))
    for x in (37.5, 50, 62.5):
        pk = soft(kit.G([(x - 5, 88), (x - 5, 22), (x, 15), (x + 5, 22), (x + 5, 88)]), 1.2)
        o.append(F(pk, WOOD, st=WOOD_T, inset=1.6))
        o.append(F(soft(U(E(x, 18.5, 6, 4), E(x - 3, 20.5, 3.4, 2.6)), .5), SNOW, lift=.4, fuzz=False))
    for x in (27, 73):
        o.append(F(soft(U(E(x, 10.5, 9.5, 5.5), E(x + 4, 13, 4, 3)), .6), SNOW, lift=.5))
    for x in (34, 44, 56, 66):
        o.append(F(soft(kit.G([(x - 2.6, 79.5), (x + 2.6, 79.5), (x, 88)]), .4), "#BFE6FA", lift=.3, fuzz=False))
    o.append(F(tube(crs([(42, 52), (42, 43), (50, 37), (58, 43), (58, 52)], 6, closed=False), 4.6), "#B8BCC8", lift=.6))
    o.append(F(R(38, 48, 24, 20, 5.5), GOLD, st=GOLD_T, inset=1.8))
    o.append(F(U(E(50, 55.5, 3), R(48.7, 55.5, 2.6, 7, 1)), DARK, lift=0, fuzz=False, only="ac"))
    o.append(L([(50, 54), (50, 62)], DARK, 2.0, only="b"))
    return OBJ(o)


def deco_snowman(st):
    return place(OBJ(drift(46, 7)) + OBJ(snowman()), 50, 52, .95)


def deco_pine(st):
    return place(OBJ(pine()), 50, 52, 1.0)


def deco_ice(st):
    return OBJ(place(ice_block(), 54, 46, 1.05)) + OBJ(place(ice_block(22, 18, 7), 26, 72, 1.0))


def deco_sled(st):
    return place(OBJ(drift(70, 6)) + OBJ(sled()), 50, 54, 1.05)


def deco_seal(st):
    return OBJ(place(floe(), 50, 73, .96)) + OBJ(place(seal(), 56, 50, 1.1))


def deco_rock(st):
    return place(OBJ(rock()), 46, 50, 1.05)


# ---------------------------------------------------------------- stickers (200 x 200, the kit adds the round sticker)
def s_penguin(st):
    return place(OBJ(penguin()), 100, 98, 1.55)


def s_snowman(st):
    return place(OBJ(snowman()), 100, 108, 1.4)


def s_bear(st):
    o = []
    for sgn in (-1, 1):
        o.append(F(E(sgn * 24, -24, 11), CREAM, st=CREAM_T, inset=2))
        o.append(F(E(sgn * 24, -23, 5.5), "#FFC9D6", lift=0, fuzz=False))
    o.append(F(E(0, 0, 35, 30), CREAM, st=CREAM_T, inset=2.6))
    o.append(F(E(0, 12, 15, 11), "#FFFFFF", lift=.4))
    o.append(F(E(0, 6.5, 6, 4.4), DARK, lift=0, fuzz=False))
    o.append(L([(0, 10), (0, 14), (-5, 17.5)], DARK, 1.8))
    o.append(L([(0, 14), (5, 17.5)], DARK, 1.8))
    o.append(EYE(-12, -5, 3.6))
    o.append(EYE(12, -5, 3.6))
    o.append(F(E(-21, 7, 5, 3.6), CHEEK, lift=0, fuzz=False))
    o.append(F(E(21, 7, 5, 3.6), CHEEK, lift=0, fuzz=False))
    return place(OBJ(o), 100, 108, 2.0)


def s_seal(st):
    return OBJ(place(floe(), 100, 136, 1.6)) + OBJ(place(seal(), 108, 100, 1.68))


def s_snowflake(st):
    return place(OBJ(flake(42, BLUE, "#FFFFFF")), 100, 100, 1.65)


def s_mitten(st):
    def mitten(col):
        palm = soft(U(R(-19, -26, 38, 50, 18), E(-20, -2, 7.5, 13, rot=-28)), 2)
        return [F(palm, col, st="#FFFFFF", inset=2.2), F(R(-22, 18, 44, 14, 6.5), "#FFFFFF", st=SNOW_ST, inset=1.8)]
    o = place(mitten(BLUE), 22, -6, 1.0, rot=16, flip=True)
    o = OBJ(o) + OBJ(mitten(RED) + flake_lines(1, -4, 9, "#FFFFFF", 2.0, only="ac"))
    return place(o, 88, 104, 1.85) + pix_sprite(FLAKE_PX, 90, 97, 5, {"x": "#FFFFFF", "o": "#FFC2D6"})


def s_sled(st):
    return place(OBJ(sled()), 98, 116, 1.75) + twinkle(62, 60, 15, 5) + twinkle(126, 48, 12, 5)


def s_igloo(st):
    return place(OBJ(igloo()), 100, 116, 1.55)


def s_fish(st):
    o = [F(soft(kit.G([(-22, 0), (-44, -18), (-40, 0), (-44, 18)]), 2.5), "#FF8A3D", lift=.6)]
    o.append(F(soft(kit.G([(-6, -16), (6, -27), (14, -15)]), 2), "#FF8A3D", lift=.6))
    body = E(0, 0, 30, 19)
    o.append(F(body, "#FFA552", st="#FFFFFF", inset=2.2))
    for x in (-12, -2):
        o.append(F(E(x, 0, 3.4, 17).intersection(body.buffer(-1)), "#FFD27A", lift=0))
    o.append(EYE(15, -4, 3.6))
    o.append(F(E(10, 6, 3.4, 2.4), CHEEK, lift=0, fuzz=False))
    o.append(L([(22, 6), (25, 8.5), (28, 6)], DARK, 1.6))
    for x, y, r in ((40, -16, 5), (46, -30, 3.6), (36, -36, 2.8)):
        o.append(F(E(x, y, r).difference(E(x, y, r * .55)), "#7CC6F2", lift=0, fuzz=False))
    return place(OBJ(o), 96, 102, 1.85)


def s_fox(st):
    """The arctic fox: a white fox face with a pointed chin, big ears and a fluffy tail."""
    o = []
    tail = kit.G(crs([(8, 36), (34, 32), (50, 12), (48, -16), (36, -30), (32, -12), (27, 10), (8, 24)], 8))
    o.append(F(tail, SNOW, st=SNOW_ST, inset=2.2))
    o.append(F(E(0, 34, 19, 15).intersection(sbox(-30, 10, 30, 46)), SNOW, st=SNOW_ST, inset=2))
    for sgn in (-1, 1):
        ear = soft(kit.G([(sgn * 7, -13), (sgn * 27, -46), (sgn * 31, -6)]), 2.6)
        o.append(F(ear, SNOW, st=SNOW_ST, inset=1.8))
        o.append(F(soft(kit.G([(sgn * 14, -14), (sgn * 25.5, -36), (sgn * 27, -11)]), 1.5), "#FFC9D6", lift=0, fuzz=False))
    head = kit.G(crs([(-35, 6), (-25, -13), (0, -18), (25, -13), (35, 6), (19, 11), (6, 25), (0, 28), (-6, 25), (-19, 11)], 8))
    o.append(F(head, SNOW, st=SNOW_ST, inset=2.2))
    o.append(EYE(-11, -3, 3.5))
    o.append(EYE(11, -3, 3.5))
    o.append(F(E(0, 21, 4.4, 3.2), DARK, lift=0, fuzz=False))
    o.append(F(E(-19, 6, 4, 3), CHEEK, lift=0, fuzz=False))
    o.append(F(E(19, 6, 4, 3), CHEEK, lift=0, fuzz=False))
    return place(OBJ(o), 94, 104, 1.68)


# ---------------------------------------------------------------- the home-page card (300 x 200)
def card(st):
    line = crs([(-40, 172), (40, 162), (110, 132), (170, 100), (230, 92), (340, 96)], 10, closed=False)
    road = tube(line, 48, cap="flat")
    o = [kit.ground_piece(WORLD, st)]
    for x, y, w in ((22, 112, 46), (196, 168, 60), (286, 150, 40), (86, 30, 40)):
        o += OBJ(place(drift(w, w * .24, only="ac"), x, y), shadow=0)
    o += OBJ(place(pine(), 136, 52, .52))
    o += OBJ(place(pine(), 176, 40, .4))
    o += OBJ(place(snowman(), 38, 62, .6))
    for x, y, r in ((96, 84, 7), (214, 16, 6), (282, 184, 6.5), (128, 176, 6)):
        o += twinkle(x, y, r, 4, "#9CC9EE")
    o.append(kit.road_piece(WORLD, st, road, width=48))
    o += OBJ(place([F(star_shape(17, 0, 0), YEL, st="#FFFFFF", inset=1.8)], 150, 113))
    o += OBJ(place(igloo(), 250, 72, .7))
    o += OBJ(place(penguin(look=9), 60, 147, .6))
    return o


def bits(st):
    """Drifts and snowflakes on the snow (a: felt drifts and embroidered flakes; c: marshmallow
    drifts and sugar flakes; b has its own pixel stamps)."""
    if st == "b":
        return []
    rnd = kit.random.Random(11)
    o = []
    spots = []
    for i in range(34):
        for _ in range(30):
            x, y = rnd.uniform(24, 576), rnd.uniform(24, 776)
            if all((x - a) ** 2 + (y - b) ** 2 > 66 ** 2 for a, b in spots):
                break
        spots.append((x, y))
        if i % 3 == 0:
            o += OBJ(place(drift(rnd.uniform(36, 56), rnd.uniform(9, 13)), x, y), shadow=0)
        elif st == "a":     # an embroidered flake: one thin shape (thread), sewn flat
            r = rnd.uniform(6.5, 9.5)
            o.append(F(kit.affinity.translate(snowflake_shape(r, 1.7), x, y), ("#FFFFFF", "#A9C4E4")[i % 2],
                       lift=0, fuzz=False, shade=False))
        elif i % 3 == 1:
            o += OBJ(place(flake(rnd.uniform(6, 8), ("#FFFFFF", "#B7D9F7")[i % 2], None), x, y), shadow=0)
    return o


WORLD = kit.World(
    "snow", "雪地",
    road=ROAD, ground=GROUND, pixel=PIXEL, jelly=JELLY, bits=bits, sticker=STICKER,
    hero=hero, home=home, family=family, star=star, key=key, gate=gate,
    deco=[deco_snowman, deco_pine, deco_ice, deco_sled, deco_seal, deco_rock],
    stickers=[s_penguin, s_snowman, s_bear, s_seal, s_snowflake, s_mitten, s_sled, s_igloo, s_fish, s_fox],
    card=card,
)
