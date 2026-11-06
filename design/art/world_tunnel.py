"""地底隧道 tunnel: 土豆 the mole walks home through his tunnels to his burrow.

    python3 build.py tunnel       # writes app/assets/art/<a|b|c>/tunnel/*.svg and checks them

Built like world_garden.py (the template). The ground is warm, rich soil with pebbles, roots, tiny
worms and buried gems; the road is a tunnel of lighter packed earth (felt: tan felt with a brown
stitch; pixel: light brown tiles; jelly: honey / caramel jelly on a chocolate-crumb ground with
gummy worms). The hero is 土豆 himself (his shapes come from tudou.py), the home a round burrow
door with a lantern, the family 土豆 hugging his mole family inside their burrow.
"""
import math

from shapely import affinity
from shapely.geometry import Point
from shapely.ops import unary_union

import kit
import tudou
from kit import BTN, E, EYE, F, L, OBJ, R, U, crs, place, sbox, tube
from tudou import BELLY, BELLY_ST, BODY, BODY_ST, PAW

# ---------------------------------------------------------------- colours (style a, felt)
SOIL = "#7E5036"                       # the ground
TAN, TAN_ST = "#F7DDB0", "#B8763E"      # the tunnel (road)
MOUND, MOUND_ST = "#C98B57", "#F6D7B2"  # the earth round the burrow door
DOOR, DOOR_ST = "#EC6A4F", "#FFD5C7"
WOOD, WOOD_ST = "#D99A5E", "#FFE4C2"
WOOD_D = "#9C643E"
PEB, PEB2, PEB3 = "#D9D0C6", "#BFB2A5", "#ECE3D6"
CARROT, CARROT_ST, CARROT_D = "#FF8C2E", "#FFE0BF", "#E0661A"
LEAF, LEAF_ST = "#62C057", "#D6F5C8"
GOLD, GOLD_T = "#FFC83D", "#FFF6CF"
YEL = "#FFD54F"
GLASS = "#FFE680"
FLAME = "#FF9F1C"
IRON = "#E25A48"                        # the lantern's frame (a cheerful red)
WORM, WORM_ST, WORM_D = "#FF9DB5", "#FFE3EA", "#E8738F"
ROOT, ROOT_ST = "#E9A465", "#FFE1BE"
RUBY, SAPH, EMER, AMET, TOPAZ = "#FF5577", "#4FB2F8", "#3FD98A", "#B57BFF", "#FFC23D"
CAP_RED, CAP_TEAL, CAP_YEL = "#F2665C", "#56CFC8", "#FFC94D"
STEM = "#FFF0D6"
PINK, CORAL, RED = "#FF9EC1", "#FF8A73", "#F2665C"
RUG, RUG_ST = "#FF8A73", "#FFE1D8"
CAVE, CAVE_ST = "#F1D3A6", "#FFF6E6"
BEETLE, BEETLE_D = "#4FC3B0", "#2E8F86"
ACORN, ACORN_CAP = "#D98A4E", "#8E5A3A"
POTATO, POTATO_ST = "#E5B776", "#FFF0D2"
STEEL = "#A9C6E3"
CRYSTAL, CRYSTAL_F = "#4FBDF5", "#CDEFFF"     # the star: a blue crystal (it pops on the warm road)
KEYB, KEYB_T = "#4E9BE6", "#DDEEFF"           # the key's shaft
BURST = "#FFF0A6"                              # a lantern's glow
BABY, BABY_ST, BABY_BELLY = "#CF9C88", "#F3D6CA", "#E2B9A6"   # baby moles are pink
WHITE, DARK, CHEEK = kit.WHITE, kit.DARK, kit.CHEEK

PIXEL = dict(
    outline="#2B1D1A",
    palette=["#FFFFFF", "#FFF4D6", "#FFE2B3", "#F0C88E", "#D9A66A", "#C98B57", "#A86B42", "#8E5A3A", "#7A4A2E",
             "#5E3622", "#FFD23A", "#FF9F1C", "#FF7A2E", "#E8483C", "#FF6FA8", "#FFB3C8", "#B86BFF", "#D9C2FF",
             "#8EE3FF", "#4FA8E8", "#7BDB6E", "#3DB55B", "#2A8F47", "#3FCFB8", "#C9C0B6", "#9E9389"],
    map={**tudou.PIXEL["map"],
         TAN: "#F0C88E", MOUND: "#C98B57", DOOR: "#E8483C", WOOD: "#D9A66A", WOOD_D: "#8E5A3A",
         PEB: "#C9C0B6", PEB2: "#9E9389", PEB3: "#FFF4D6", CARROT: "#FF7A2E", CARROT_D: "#E8483C",
         LEAF: "#3DB55B", GOLD: "#FFD23A", YEL: "#FFD23A", GLASS: "#FFF4A0", FLAME: "#FF9F1C", IRON: "#E8483C",
         WORM: "#FFA5BC", WORM_D: "#FF6FA8", ROOT: "#D9A66A", RUBY: "#FF4D6A", SAPH: "#4FA8E8", EMER: "#3DB55B",
         AMET: "#B86BFF", TOPAZ: "#FF9F1C", CAP_RED: "#E8483C", CAP_TEAL: "#3FCFB8", CAP_YEL: "#FFD23A",
         STEM: "#FFF4D6", RUG: "#FF6FA8", CAVE: "#FFE2B3", BEETLE: "#3FCFB8", BEETLE_D: "#2A8F47",
         ACORN: "#D9A66A", ACORN_CAP: "#8E5A3A", POTATO: "#F0C88E", STEEL: "#8EE3FF", CORAL: "#FF6FA8",
         PINK: "#FFB3C8", RED: "#E8483C", CRYSTAL: "#4FA8E8", CRYSTAL_F: "#8EE3FF", KEYB: "#4FA8E8", BURST: "#FFF4A0", BABY: "#D29A86", BABY_BELLY: "#E6BBA6", "#FFFFFF": "#FFFFFF", WHITE: "#FFFFFF"},
)
JELLY = dict(shadow="#5A2E1C", map={**tudou.JELLY["map"], LEAF: "#5ED65A", MOUND: "#D9955A", WOOD: "#E8A35E",
                                     TAN: "#FFD27A"})

ROAD = {
    "a": dict(fill=TAN, stitch=TAN_ST),
    "b": dict(fill="#F0C88E", speck="#D9A66A", shade="#D9A066", light="#FFE2B3", border="#3E2418"),
    "c": dict(body="#FFC24D", rim="#E08A1E", glow="#FFF5CC", shadow="#3A1E12"),
}
GEMS_PX = [{"l": "#FFFFFF", "g": "#FF4D6A", "d": "#B8283E"}, {"l": "#FFFFFF", "g": "#4FA8E8", "d": "#2B6CB0"},
           {"l": "#FFFFFF", "g": "#3DB55B", "d": "#1D6B3A"}, {"l": "#FFFFFF", "g": "#B86BFF", "d": "#7A3FC0"},
           {"l": "#FFFFFF", "g": "#FFD23A", "d": "#C98A20"}]
GROUND = {
    "a": dict(base=SOIL, fibres=("#946348", "#6E442D")),
    "b": dict(base="#7A4A2E", specks=[("#6A3E26", .08), ("#8E5A3A", .05)],
              stamps=[([".l.", "lgd", ".d."], GEMS_PX, .9),                                   # buried gems
                      ([".ab.", "abbb", ".bb."], {"a": "#E6DED4", "b": "#B5A99C"}, 1.3),     # pebbles
                      (["p..pp", ".pp.."], {"p": "#FFA5BC"}, .8),                             # tiny worms
                      (["r...", ".r..", ".rr.", "...r"], {"r": "#C98B57"}, 1.0)]),            # roots
    "c": dict(top="#9C6449", bottom="#7C4834", swirl="#B27E61",
              sprinkles=("#FF6FA8", "#FFD43B", "#7FD8FF", "#8CE07A", "#FFFFFF", "#FFA04A"), n=6),
}


# ================================================================ small helpers
def taper(pts, w0, w1, k=10):
    """A stroke along a polyline whose width goes from w0 to w1 (a root, a tail)."""
    m = len(pts)
    parts = []
    for i in range(m - 1):
        r0 = (w0 + (w1 - w0) * i / (m - 1)) / 2
        r1 = (w0 + (w1 - w0) * (i + 1) / (m - 1)) / 2
        parts.append(unary_union([Point(pts[i]).buffer(r0, k), Point(pts[i + 1]).buffer(r1, k)]).convex_hull)
    return unary_union(parts)


def curve(ctrl, k=8):
    return crs(ctrl, k, closed=False)


def sparkle(x, y, r, col="#FFF3A6"):
    pts = []
    for i in range(8):
        a = math.radians(45 * i - 90)
        rr = r if i % 2 == 0 else r * .3
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
    return [F(kit.soft(kit.G(pts), r * .06), col, lift=.4, fuzz=False, shade=False)]


def heart(s=12, col=PINK):
    return [F(kit.heart_pts(0, 0, s), col, st="#FFFFFF", inset=1.6 if s < 12 else 2.2)]


def grass(x, y, s=1.0, col=LEAF, only="ac"):
    g = U(kit.G([(-8, 0), (-6, -12), (-3, 0)]), kit.G([(-3, 0), (0, -16), (3, 0)]), kit.G([(3, 0), (6, -11), (8, 0)])).buffer(1.2)
    return [F(affinity.affine_transform(g, [s, 0, 0, s, x, y]), col, lift=.6, only=only)]


def leaf(x, y, ln, rot, col=LEAF, st=LEAF_ST):
    return F(kit.G(kit.tf(crs([(0, 0), (ln * .5, -ln * .32), (ln, 0), (ln * .5, ln * .32)], 6), x, y, rot)), col, st=st, inset=1.8)


# ================================================================ things (drawn round (0, 0))
def small_arm(x0, y0, x1, y1, rot, col=BODY, st=BODY_ST):
    """tudou.arm without the claw threads (for the baby: fewer bytes, too small to see them)."""
    return [F(tube([(x0, y0), (x1, y1)], 17), col, st=st, inset=2.4),
            F(E(x1, y1, 11, 8.5, rot=rot), PAW, st="#FFFFFF", inset=2.4)]


def mole(mood="happy", look=0.0, arms=None, hat=False, bow=None, glasses=False, feet=(-1, 1), baby=False):
    """A mole of 土豆's family built from tudou.py's shapes (body about 106 x 120 round (0, 0)).
    arms: None, "up" (both raised), "hug" (both reaching out sideways). feet: the sides (-1, 1) that get a foot."""
    o = []
    col, st, belly = (BABY, BABY_ST, BABY_BELLY) if baby else (BODY, BODY_ST, BELLY)
    if arms == "up":
        o += small_arm(-38, -10, -62, -48, -70, col, st) + small_arm(38, -10, 62, -48, -110, col, st)
    for sgn in feet:
        o.append(F(E(sgn * 22, 55, 15, 9), PAW, st="#FFFFFF", inset=2.4))
    o.append(F(tudou.body_shape(), col, st=st))
    o.append(F(E(0, 24, 30, 26), belly, st=BELLY_ST, inset=3, lift=0))
    o += tudou.face(look, mood)
    if glasses:
        for ex in (-15, 15):
            o.append(L(kit.ellp(ex + look, -38, 10, 9, k=28) + [kit.ellp(ex + look, -38, 10, 9, k=28)[0]], "#5A3A8C", 2.2, only="ac"))
        o.append(L([(-5 + look, -39), (5 + look, -39)], "#5A3A8C", 2.2, only="ac"))
    if hat:
        o += place(tudou.hat(), 0, -55)
    if bow:
        o.append(F(E(-12, -60, 13, 9, rot=-24), bow, st="#FFFFFF", inset=2.2))
        o.append(F(E(12, -60, 13, 9, rot=24), bow, st="#FFFFFF", inset=2.2))
        o.append(F(E(0, -60, 5.5), kit.dk(bow, .15), lift=.5, fuzz=False))
    if arms == "hug":
        o += tudou.arm(38, 2, 70, -2, -10) + tudou.arm(-38, 2, -70, -2, 190)
    return o


def mole_walk():
    """土豆 walking to the right: leaning forward a little, front paw swinging, eyes to the right."""
    o = tudou.arm(-34, 0, -52, 20, 125)                  # the far arm swings back (behind him)
    o.append(F(E(-24, 55, 15, 9, rot=-10), PAW, st="#FFFFFF", inset=2.4))     # back foot
    o.append(F(E(28, 56, 16, 9, rot=4), PAW, st="#FFFFFF", inset=2.4))        # front foot
    up = [F(tudou.body_shape(), BODY, st=BODY_ST), F(E(0, 24, 30, 26), BELLY, st=BELLY_ST, inset=3, lift=0)]
    up += tudou.face(8, "smile")
    up += place(tudou.hat(), 2, -55)
    o += place(up, rot=6)
    o += tudou.arm(36, 4, 58, 24, 35)                    # the near arm swings forward
    return o


def lantern(glow=True):
    """A little lantern; its glass is centred at (0, 0), about 30 x 50."""
    o = []
    if glow:
        o.append(F(kit.soft(kit.G(kit.star_pts(31, 23, 0, -3, 12)), 2.2), BURST, lift=0, shade=False))
    o.append(F(tube(crs([(-8, -21), (-8, -31), (0, -36), (8, -31), (8, -21)], 6, closed=False), 3.4), IRON, lift=.6, fuzz=False))
    o.append(F(R(-11, -18, 22, 30, 6), GLASS, st="#FFFFFF", inset=1.8))
    o.append(F(kit.G(crs([(0, -9), (4, 0), (2.6, 5), (0, 6), (-2.6, 5), (-4, 0)], 5)), FLAME, lift=0, fuzz=False, shade=False))
    o.append(F(R(-14, -24, 28, 8, 4), IRON, lift=.8))
    o.append(F(R(-14, 10, 28, 8, 4), IRON, lift=.8))
    return o


def carrot(s=1.0):
    """A carrot pointing down, top at y = -24; leaves above it."""
    o = []
    for x, ln, rot in ((-4, 26, -112), (0, 30, -90), (4, 26, -68)):
        o.append(leaf(x, -22, ln, rot))
    body = kit.G(crs([(-15, -21), (0, -26), (15, -21), (11, 6), (4, 34), (0, 40), (-4, 34), (-11, 6)], 6))
    o.append(F(body, CARROT, st=CARROT_ST, inset=2.4))
    for y, x0, x1 in ((-10, -13, -5), (2, 6, 12), (14, -9, -3), (24, 2, 6)):
        o.append(L([(x0, y), (x1, y + 1)], CARROT_D, 1.8))
    return place(o, s=s)


def gem(w, col, facet=True):
    """A cut gem (a brilliant seen from the side), about w wide, centred at (0, 0)."""
    h = w * .82
    pts = [(-w * .3, -h * .45), (w * .3, -h * .45), (w * .5, -h * .12), (0, h * .55), (-w * .5, -h * .12)]
    o = [F(pts, col, st="#FFFFFF" if w > 20 else None, inset=1.6)]
    if facet:
        o.append(F([(-w * .3, -h * .45), (w * .3, -h * .45), (w * .17, -h * .12), (-w * .17, -h * .12)], kit.lt(col, .45),
                   lift=0, fuzz=False, shade=False))
        o.append(F([(-w * .5, -h * .12), (-w * .17, -h * .12), (0, h * .55)], kit.lt(col, .22), lift=0, fuzz=False, shade=False))
        o.append(F([(w * .5, -h * .12), (w * .17, -h * .12), (0, h * .55)], kit.dk(col, .12), lift=0, fuzz=False, shade=False))
    return o


def mushroom(r, cap, dots=WHITE, stem_h=None, face=False):
    """A mushroom: cap radius r, the cap's bottom at y = 0, the stem going down."""
    sh = stem_h if stem_h is not None else r * .9
    o = [F(R(-r * .36, -r * .1, r * .72, sh + r * .1, r * .3), STEM, st="#E7D2B0" if r > 12 else None, inset=1.8)]
    capg = kit.soft(E(0, 0, r, r * .8).intersection(sbox(-r - 5, -r - 5, r + 5, r * .16)), r * .1)
    o.append(F(capg, cap, st="#FFFFFF" if r > 10 else None, inset=2.2 if r > 18 else 1.7))
    if dots:
        for x, y, rr in ((-.5, -.3, .17), (.15, -.55, .19), (.55, -.2, .14)):
            o.append(F(E(x * r, y * r, rr * r), dots, lift=0, fuzz=False))
    if face:
        o.append(EYE(-r * .24, sh * .42, r * .1))
        o.append(EYE(r * .24, sh * .42, r * .1))
        o.append(L([(-r * .1, sh * .6), (0, sh * .68), (r * .1, sh * .6)], DARK, max(1.4, r * .05)))
        for x in (-.36, .36):
            o.append(F(E(x * r * .9, sh * .56, r * .07, r * .05), CHEEK, lift=0, fuzz=False))
    return o


def worm_body(pts, w=11):
    return tube(curve(pts), w)


def worm(sleep=True, cap=None):
    """A curled worm resting (head on the right)."""
    path = [(-30, 8), (-20, -2), (-8, 8), (4, 0), (16, -6)]
    o = [F(worm_body(path, 12), WORM, st=WORM_ST, inset=1.8)]
    for x, y in ((-24, 3), (-14, 3), (-3, 4), (8, -2)):
        o.append(L([(x - 1.5, y - 4), (x + 1.5, y + 4)], WORM_D, 1.6))
    o.append(F(E(22, -9, 12, 11), WORM, st=WORM_ST, inset=2))
    if sleep:
        for ex in (18, 27):
            o.append(L([(ex - 3, -10), (ex, -7.5), (ex + 3, -10)], DARK, 1.7))
    else:
        o.append(EYE(18, -11, 2.4))
        o.append(EYE(27, -11, 2.4))
        o.append(L([(19, -4), (22.5, -1.6), (26, -4)], DARK, 1.6))
    o.append(F(E(31, -5, 2.6, 2), CHEEK, lift=0, fuzz=False))
    o.append(F(E(14, -5, 2.6, 2), CHEEK, lift=0, fuzz=False))
    if cap:
        o.append(F(kit.soft(kit.G([(12, -16), (32, -16), (40, -34)]), 1.5), cap, st="#FFFFFF", inset=1.4))
        o.append(F(E(40, -34, 3.6), WHITE, lift=.5, fuzz=False))
    return o


def burrow_home(lamp=True):
    """The burrow: a round red door in a mound of earth, a ring of stones, a lantern on a post.
    Centred round (0, 0), about 100 x 90."""
    o = []
    if lamp:
        o.append(F(R(35, -30, 5.5, 64, 2.5), WOOD_D, lift=.6))
        o.append(F(R(26, -32, 16, 5, 2.5), WOOD_D, lift=.6))
    mound = kit.G(crs([(-48, 36), (-47, 6), (-36, -22), (-14, -36), (14, -36), (36, -22), (47, 6), (48, 36)], 7)).intersection(sbox(-60, -60, 60, 36))
    o.append(F(mound, MOUND, st=MOUND_ST, inset=3.2))
    o += grass(-22, -32, .8) + grass(14, -35, .9) + grass(34, -22, .7)
    o.append(F(E(-30, -27, 3.2), "#FFE36B", lift=.5, fuzz=False, only="ac"))
    o.append(F(E(25, -32, 3), "#FFFFFF", lift=.5, fuzz=False, only="ac"))
    # a ring of stones round the door
    for i in range(9):
        a = math.radians(180 + 180 * i / 8)
        x, y = 30 * math.cos(a), 12 + 30 * math.sin(a)
        o.append(F(E(x, y, 6.6, 5.6, rot=math.degrees(a)), (PEB, PEB3)[i % 2], lift=.5))
    door = E(0, 12, 22).intersection(sbox(-30, -20, 30, 34))
    o.append(F(door, DOOR, st=DOOR_ST, inset=2.2))
    for x in (-8, 8):
        o.append(L([(x, 3), (x, 32)], kit.dk(DOOR, .2), 1.6))
    o.append(F(E(0, 0, 6.4), GLASS, st=None, lift=.5))
    o.append(L([(0, -6), (0, 6)], kit.dk(DOOR, .25), 1.5, only="ac"))
    o.append(L([(-6, 0), (6, 0)], kit.dk(DOOR, .25), 1.5, only="ac"))
    o.append(BTN(12, 18, 2.8, GOLD))
    o.append(F(R(-17, 31, 34, 7, 3.5), "#7FC8F0", lift=.5, only="ac"))
    if lamp:
        o += place(lantern(glow=False), 30, -16, .42)
    return o


def bits(st):
    """Small things on the soil: pebbles, roots, tiny worms, buried gems (a felt; c candy)."""
    if st == "b":
        return []
    rnd = kit.random.Random(5)
    o = []
    if st == "a":
        for i in range(32):
            x, y = rnd.uniform(24, 576), rnd.uniform(24, 776)
            k = i % 4
            if k == 0:       # two pebbles
                o.append(F(E(x, y, 9, 6.5, rot=rnd.uniform(-30, 30)), (PEB, PEB2, PEB3)[i % 3], lift=.6))
                o.append(F(E(x + 13, y + 6, 5.5, 4.4), (PEB3, PEB, PEB2)[i % 3], lift=.5))
            elif k == 1:     # a little root
                a = rnd.uniform(0, 6.3)
                pts = [(x + math.cos(a) * t * 10 + math.sin(t * 1.6) * 3, y + math.sin(a) * t * 10 + math.cos(t * 1.6) * 3) for t in range(4)]
                o.append(L(curve(pts, 5), "#C99062", 3.2))
                o.append(L([pts[1], (pts[1][0] + 7, pts[1][1] + 6)], "#C99062", 2.2))
            elif k == 2:     # a tiny worm
                s = 1 if i % 8 == 2 else -1
                pts = [(x - 13 * s, y + 3), (x - 6 * s, y - 3), (x + 1 * s, y + 3), (x + 8 * s, y - 1)]
                o.append(F(tube(curve(pts, 5), 6.5), WORM, lift=.5, fuzz=False))
                o.append(F(E(x + 8.5 * s, y - 2, 1.3), DARK, lift=0, fuzz=False, shade=False))
            else:            # a buried gem
                o += place(gem(16, (RUBY, SAPH, EMER, AMET, TOPAZ)[i // 4 % 5], facet=False), x, y, rot=rnd.uniform(-20, 20))
    else:
        for i in range(14):
            x, y = rnd.uniform(30, 570), rnd.uniform(30, 770)
            if i % 2 == 0:   # a gummy worm
                s = 1 if i % 4 == 0 else -1
                pts = [(x - 14 * s, y + 3), (x - 6 * s, y - 3), (x + 2 * s, y + 3), (x + 10 * s, y - 2)]
                o.append(F(tube(curve(pts, 5), 7), ("#FF8FB8", "#FFB04A", "#8CE07A")[i // 2 % 3], lift=.6))
            else:            # a candy gem
                o += place(gem(13, (RUBY, SAPH, EMER, AMET)[i // 2 % 4], facet=False), x, y, rot=rnd.uniform(-20, 20))
    return o


# ================================================================ the files
def hero(st):
    return place(OBJ(mole_walk()), 50, 55, .58)


def home(st):
    return place(OBJ(burrow_home()), 50, 52, .9)


def family(st):
    """Home at last: 土豆 hugs his family (dad with glasses, mum with a bow, the baby) in their burrow."""
    cave = kit.G(crs([(24, 372), (18, 230), (56, 112), (140, 56), (260, 56), (344, 112), (382, 230), (376, 372)], 8))
    o = OBJ([F(cave, CAVE, st=CAVE_ST, inset=4, fuzz=False, gloss=False)])
    for x, y0, y1 in ((76, 120, 138), (324, 120, 138)):
        o += OBJ([L([(x, y0), (x, y1)], WOOD_D, 2.2)] + place(lantern(), x, y1 + 32, .78))
    o += OBJ([F(E(200, 352, 172, 34), RUG, st=RUG_ST, inset=4, fuzz=False)])
    o += OBJ(place(heart(16, CORAL), 200, 96))
    o += OBJ(place(mole("happy", glasses=True, feet=(-1,)), 98, 262, 1.2))      # the feet behind 土豆 are left out
    o += OBJ(place(mole("happy", bow=PINK, feet=(1,)), 304, 268, 1.12))
    o += OBJ(place(mole("happy", arms="hug", hat=True), 200, 282, 1.04))
    o += OBJ(place(mole("happy", arms="up", baby=True), 150, 346, .56))
    for x, y, r in ((40, 300, 10), (362, 306, 9), (152, 108, 9), (250, 104, 8)):
        o += OBJ(sparkle(x, y, r), shadow=0)
    return o


def star(st):
    g = kit.star_shape(40, 50, 53)
    pts = kit.star_pts(40, 20, 50, 53)
    o = [F(g, CRYSTAL, st="#FFFFFF", inset=3.6)]
    for i in range(0, 10, 2):         # a lighter facet on one side of each point
        o.append(F(kit.G([(50, 53), pts[i], pts[(i + 1) % 10]]).intersection(g.buffer(-3)), CRYSTAL_F, lift=0, fuzz=False, shade=False))
    o.append(F(E(38, 38, 4.2, 2.6, rot=-35), "#FFFFFF", lift=0, fuzz=False, op=.85))
    return OBJ(o) + OBJ(sparkle(84, 18, 8, "#FFFFFF"), shadow=0)


def key(st):
    """A key with a blue shaft whose bow is a carrot ring with a leafy top."""
    o = [leaf(-31, 0, 15, 150), leaf(-32, 0, 17, 180), leaf(-31, 0, 15, 210)]
    o.append(F(U(R(-6, -5, 42, 10, 4), R(20, 3, 7, 11, 2.5), R(30, 3, 7, 8, 2.5)), KEYB, st=KEYB_T, inset=2.2))
    o.append(F(E(-16, 0, 16).difference(E(-16, 0, 6.5)), CARROT, st=CARROT_ST, inset=2.2))
    for a in (60, 150, 240, 320):
        x, y = -16 + 11.3 * math.cos(math.radians(a)), 11.3 * math.sin(math.radians(a))
        o.append(L([(x - 1.6 * math.sin(math.radians(a)), y + 1.6 * math.cos(math.radians(a))),
                    (x + 1.6 * math.sin(math.radians(a)), y - 1.6 * math.cos(math.radians(a)))], CARROT_D, 1.4, only="ac"))
    return place(OBJ(o), 52, 53, 1.18, rot=-30)


def gate(st):
    """A round-topped wooden burrow door standing across a left-right tunnel, with a padlock."""
    o = []
    for x in (24, 76):
        o.append(F(R(x - 6, 10, 12, 84, 5), WOOD_D, st="#E9C29E", inset=1.8))
    door = U(E(50, 34, 21, 22).intersection(sbox(20, 0, 80, 40)), R(29, 34, 42, 58, 3))
    o.append(F(door, WOOD, st=WOOD_ST, inset=2))
    for x in (39.5, 50, 60.5):
        o.append(L([(x, 18 if x == 50 else 22), (x, 88)], kit.dk(WOOD, .25), 1.6))
    for y in (40, 78):
        o.append(F(R(27, y, 46, 7, 3), WOOD_D, lift=.6))
    for x, y in ((30.5, 43.5), (69.5, 43.5), (30.5, 81.5), (69.5, 81.5)):
        o.append(F(E(x, y, 1.8), "#E8DCCF", lift=0, fuzz=False, shade=False, only="ac"))
    o.append(F(tube(crs([(43, 58), (43, 50), (50, 44), (57, 50), (57, 58)], 6, closed=False), 4.4), "#B8BCC8", lift=.6))
    o.append(F(R(39, 55, 22, 19, 5.5), GOLD, st=GOLD_T, inset=1.8))
    o.append(F(U(E(50, 62, 2.8), R(48.8, 62, 2.4, 6.5, 1)), DARK, lift=0, fuzz=False, only="ac"))
    o.append(L([(50, 61), (50, 68)], DARK, 2.0, only="b"))
    return OBJ(o)


def deco_roots(st):
    """A little plant: three leaves up top and its fan of curly roots spreading out underneath."""
    o = []
    tips = []
    for k, (ang, ln) in enumerate(((22, 40), (52, 50), (90, 54), (128, 50), (158, 40))):
        a = math.radians(ang)
        dx, dy = math.cos(a), math.sin(a)
        pts = [(dx * t + -dy * math.sin(t / 8 + k) * 3.5, -16 + dy * t * .85 + dx * math.sin(t / 8 + k) * 3.5)
               for t in (0, ln * .35, ln * .7, ln)]
        tips.append(pts[-1])
        o.append(F(taper(curve(pts, 4), 9 if ang == 90 else 7, 2.6), ROOT, lift=.6))
        mid = pts[2]
        side = 1 if ang < 90 else -1
        o.append(L([mid, (mid[0] + side * 3 + dx * 6, mid[1] + 6)], ROOT, 2.0))
    o.append(F(E(0, -14, 15, 8), ROOT, st=ROOT_ST, inset=1.8))
    o += [leaf(0, -20, 22, -150), leaf(0, -20, 22, -30), leaf(0, -20, 25, -90)]
    return place(OBJ(o), 50, 50, 1.1)


def deco_carrot(st):
    return place(OBJ(carrot()), 50, 56, 1.1, rot=18)


def deco_mushrooms(st):
    o = place(mushroom(15, CAP_TEAL, WHITE, 18), 26, 2) + place(mushroom(10, CAP_YEL, WHITE, 12), -28, 14)
    o += place(mushroom(22, CAP_RED, WHITE, 24), -6, -6)
    o += [F(E(x, 30, r, r * .55), "#7FCF6A", lift=.4, fuzz=False, only="ac") for x, r in ((-22, 7), (10, 6), (30, 5))]
    return place(OBJ(o), 50, 52, 1.05)


def deco_gems(st):
    o = place(gem(26, SAPH), -18, 12, rot=-12) + place(gem(24, EMER), 20, 14, rot=14)
    o += place(gem(30, RUBY), 0, -6) + place(gem(18, AMET), -30, 26, rot=-25) + place(gem(17, TOPAZ), 32, 28, rot=20)
    o += sparkle(-22, -16, 7, "#FFFFFF") + sparkle(26, -14, 6, "#FFF3A6")
    return place(OBJ(o), 50, 52, 1.0)


def deco_worm(st):
    o = [F(E(4, 14, 44, 13), "#7FCF6A", st="#D6F5C8", inset=2)]         # a leaf bed
    o.append(L([(-34, 14), (40, 14)], "#4FA84A", 1.8))
    o += place(worm(sleep=True, cap="#7CB8F2"), -2, 4, 1.0)
    for x, y, s in ((24, -30, 4.5), (33, -40, 6)):                      # little z z (stitched)
        o.append(L([(x - s, y - s), (x + s, y - s), (x - s, y + s), (x + s, y + s)], WHITE, 1.8))
    return place(OBJ(o), 50, 56, 1.0)


def deco_lantern(st):
    o = [F(kit.soft(E(0, 30, 22, 9), 2), PEB2, st=None)]
    o += place(lantern(), 0, 0, 1.3)
    return place(OBJ(o), 50, 52, 1.0)


# ---------------------------------------------------------------- stickers (200 x 200, the kit adds the round sticker)
def s_mole(st):
    return place(tudou.mole_pieces("wave"), 97, 110, .86)


def s_carrot(st):
    return place(OBJ(carrot()), 100, 104, 1.9, rot=28)


def s_gem(st):
    o = OBJ(gem(108, RUBY))
    o += OBJ(sparkle(48, -38, 11, "#FFFFFF"), shadow=0) + OBJ(sparkle(-48, 30, 9, "#FFE36B"), shadow=0)
    return place(o, 100, 104, 1.0)


def s_worm(st):
    o = [F(E(0, 26, 36, 10), "#9C6449", lift=.5)]                        # a hole in the soil
    o.append(F(E(0, 24, 24, 5.5), "#4A3127", lift=0, shade=False))
    o.append(F(tube(curve([(-4, 24), (-8, 6), (2, -12), (14, -22)], 6), 15), WORM, st=WORM_ST, inset=2))
    for x, y in ((-6, 14), (-5, 2), (2, -8)):
        o.append(L([(x - 5, y), (x + 5, y + 1)], WORM_D, 1.6))
    o.append(F(E(18, -28, 14, 13), WORM, st=WORM_ST, inset=2))
    o.append(EYE(13, -31, 2.8))
    o.append(EYE(24, -31, 2.8))
    o.append(L([(14, -22), (18.5, -19), (23, -22)], DARK, 1.7))
    o.append(F(E(9, -24, 2.8, 2.1), CHEEK, lift=0, fuzz=False))
    o.append(F(E(28, -24, 2.8, 2.1), CHEEK, lift=0, fuzz=False))
    return place(OBJ(o), 96, 108, 1.78)


def s_mushroom(st):
    return place(OBJ(mushroom(40, CAP_RED, WHITE, 34, face=True)), 100, 98, 1.45)


def s_lantern(st):
    return place(OBJ(lantern()), 100, 106, 2.25)


def s_shovel(st):
    o = [F(R(-5, -48, 10, 66, 4), WOOD, st=WOOD_ST, inset=1.8)]
    o.append(F(kit.G(crs([(-14, -58), (0, -62), (14, -58), (14, -48), (-14, -48)], 4)).buffer(0), WOOD_D, lift=.6))
    o.append(F(tube([(-10, -60), (10, -60)], 5), WOOD_D, lift=.6))
    blade = kit.G(crs([(-20, 14), (20, 14), (21, 36), (10, 54), (0, 60), (-10, 54), (-21, 36)], 6))
    o.append(F(blade, STEEL, st="#FFFFFF", inset=2.2))
    o.append(F(R(-8, 10, 16, 12, 4), "#7C8BA0", lift=.6))
    o.append(F(E(-9, 34, 3.4, 9, rot=-8), "#FFFFFF", lift=0, fuzz=False, op=.7))
    return place(OBJ(o), 100, 98, 1.5, rot=28)


def s_acorn(st):
    o = [F(R(-3, -40, 6, 12, 3), ACORN_CAP, lift=.6)]
    o.append(F(kit.G(crs([(-28, 0), (-22, 22), (0, 40), (22, 22), (28, 0)], 6)), ACORN, st="#FFE0C2", inset=2.4))
    capg = kit.soft(E(0, -6, 32, 22).intersection(sbox(-40, -40, 40, 2)), 3)
    o.append(F(capg, ACORN_CAP, st="#D8B08C", inset=2.2))
    for x in (-18, -6, 6, 18):
        o.append(L([(x - 3, -18), (x + 3, -10), (x - 3, -3)], kit.lt(ACORN_CAP, .25), 1.6, only="ac"))
    o.append(F(E(-12, 14, 4, 8, rot=20), "#FFFFFF", lift=0, fuzz=False, op=.45))
    return place(OBJ(o), 100, 106, 1.8)


def s_beetle(st):
    o = []
    for sgn in (-1, 1):
        for y in (-2, 10, 22):
            o.append(L([(sgn * 18, y), (sgn * 30, y + 4)], DARK, 2.4))
    o.append(F(E(0, -24, 14, 11), BEETLE_D, lift=.6))
    o.append(F(taper(curve([(0, -32), (2, -40), (7, -45)], 4), 6, 2.6), BEETLE_D, lift=.6))
    o.append(L([(-6, -32), (-12, -42), (-18, -44)], DARK, 1.8))
    o.append(L([(6, -32), (13, -38), (19, -38)], DARK, 1.8))
    o.append(F(E(0, 10, 23, 26), BEETLE, st="#FFFFFF", inset=2.4))
    o.append(L([(0, -14), (0, 34)], BEETLE_D, 2.2))
    for x, y, r in ((-10, 2, 3.4), (10, 8, 3), (-9, 20, 2.6), (11, 22, 3.2)):
        o.append(F(E(x, y, r), "#FFE36B", lift=0, fuzz=False))
    o.append(EYE(-6, -25, 3.2))
    o.append(EYE(6, -25, 3.2))
    o.append(F(E(-10, -2, 4, 9, rot=20), "#FFFFFF", lift=0, fuzz=False, op=.45))
    return place(OBJ(o), 100, 110, 2.15)


def s_potato(st):
    body = kit.G(crs([(-40, -8), (-30, -28), (-4, -34), (24, -30), (40, -12), (42, 12), (28, 30), (0, 34), (-28, 30), (-42, 14)], 7))
    o = [leaf(6, -32, 18, -70), leaf(4, -32, 14, -130)]
    o.append(F(body, POTATO, st=POTATO_ST, inset=2.6))
    for x, y, r in ((-28, -12, 2.6), (26, -18, 2.2), (30, 14, 2.4), (-22, 20, 2.0)):
        o.append(F(E(x, y, r, r * .8), "#B9874E", lift=0, fuzz=False))
    o.append(EYE(-10, -4, 4))
    o.append(EYE(12, -4, 4))
    o.append(F(E(-18, 8, 4.4, 3.2), CHEEK, lift=0, fuzz=False))
    o.append(F(E(20, 8, 4.4, 3.2), CHEEK, lift=0, fuzz=False))
    o.append(L([(-5, 8), (1, 13), (7, 8)], DARK, 2.0))
    return place(OBJ(o), 100, 108, 1.62)


# ---------------------------------------------------------------- the home-page card (300 x 200)
def card(st):
    line = crs([(-40, 168), (40, 160), (110, 136), (170, 104), (230, 94), (340, 98)], 10, closed=False)
    road = tube(line, 48, cap="flat")
    o = [kit.ground_piece(WORLD, st)]
    o += OBJ(place(mushroom(14, CAP_RED, WHITE, 14), 120, 62) + place(mushroom(9, CAP_TEAL, WHITE, 9), 140, 70))
    o += OBJ(place(gem(20, SAPH), 36, 52, rot=-10) + place(gem(16, RUBY), 54, 62, rot=12))
    o += OBJ(place(carrot(), 210, 168, .6, rot=-70))
    o += OBJ(place(worm(sleep=True), 186, 46, .55))
    o += OBJ(place(lantern(), 280, 172, .75))
    o.append(kit.road_piece(WORLD, st, road, width=48))
    o += OBJ(place([F(kit.star_shape(17, 0, 0), CRYSTAL, st="#FFFFFF", inset=1.8)], 150, 116))
    o += OBJ(place(burrow_home(), 254, 64, .78))
    o += OBJ(place(mole_walk(), 62, 140, .4))
    return o


WORLD = kit.World(
    "tunnel", "地底隧道",
    road=ROAD, ground=GROUND, pixel=PIXEL, jelly=JELLY, bits=bits,
    sticker=dict(fill="#FFF6E8", stitch="#D9B590", fill_b="#FFF4D6", fill_c="#FFF4E4"),
    hero=hero, home=home, family=family, star=star, key=key, gate=gate,
    deco=[deco_roots, deco_carrot, deco_mushrooms, deco_gems, deco_worm, deco_lantern],
    stickers=[s_mole, s_carrot, s_gem, s_worm, s_mushroom, s_lantern, s_shovel, s_acorn, s_beetle, s_potato],
    card=card,
)
