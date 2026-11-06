"""土豆 the mole (our guide): app/assets/art/<a|b|c>/tudou_<pose>.svg, 200 x 200.

A round brown mole with a pink nose, little pink paws and a yellow hard hat with a lamp.
    wave   standing, waving with one paw
    point  standing, pointing right with a paw (the app mirrors it to point left), eyes looking right
    cheer  both paws up, happy eyes, open mouth
    sleep  curled up on a little pillow, eyes closed (no letters)
    peek   only his head and paws out of a round hole in the ground (the hint)

`mole_pieces(pose)` gives the pieces drawn round (0, 0) (body about 120 units tall) so a world
(the tunnel world, where he is the hero) can place him at any size.
"""
import math

import kit
from kit import BTN, E, EYE, F, L, OBJ, R, U, crs, place, sbox

BODY, BODY_ST = "#8C6A57", "#C7A58F"
BELLY, BELLY_ST = "#A8836E", "#CDAE98"
MUZ = "#D9B9A0"
NOSE = "#FF8FAB"
PAW, CLAW = "#FFB3C3", "#E07F98"
HAT, HAT_ST, BRIM, LAMP = "#FFC83D", "#FFF3C0", "#FFB31F", "#FFF6CF"
DIRT, DIRT_ST, HOLE = "#B98A63", "#E7C9A5", "#4A3127"
PILLOW = "#BFE3F5"

PIXEL = dict(outline="#2B2340", map={BODY: "#8E5E44", BELLY: "#B07A5A", MUZ: "#E8B898", NOSE: "#FF6F9C", PAW: "#FFA5BC",
                                     HAT: "#FFCC2E", BRIM: "#FF9F1C", LAMP: "#FFF6C8", DIRT: "#B87A4A", HOLE: "#3A2420",
                                     PILLOW: "#8EE3FF", kit.CHEEK: "#FF8FA8", CLAW: "#E0607F"})
JELLY = dict(shadow="#7A4A3A", map={BODY: "#A0705A", BELLY: "#C08C70", NOSE: "#FF7AA6", HAT: "#FFC93A", PAW: "#FFA9C2"})


class _Look:
    """A stand-in world for drawing 土豆 alone (his own pixel palette and jelly colours)."""
    pixel, jelly = PIXEL, JELLY


def hat(rot=0.0):
    """The hard hat, its brim centre at (0, 0)."""
    dome = E(0, 3, 34, 27).intersection(sbox(-40, -40, 40, 0))
    o = [F(dome, HAT, st=HAT_ST, inset=3)]
    o.append(F(R(-43, -4, 86, 10, 5), BRIM))
    o.append(F(E(0, -15, 8.5, 7.5), LAMP, st=None))
    o.append(F(E(-2.2, -17.2, 2.4, 2), "#FFFFFF", lift=0, fuzz=False))
    return place(o, rot=rot)


def paw(x, y, rot=0.0, s=1.0):
    """A pink paw (an oval) with three claw threads at its tip, pointing at angle rot (degrees)."""
    a = math.radians(rot)
    o = [F(E(x, y, 11 * s, 8.5 * s, rot=rot), PAW, st="#FFFFFF", inset=2.4)]
    for d in (-4, 0, 4):
        px = x + 8 * s * math.cos(a) - d * s * math.sin(a)
        py = y + 8 * s * math.sin(a) + d * s * math.cos(a)
        o.append(L([(px, py), (px + 3.6 * s * math.cos(a), py + 3.6 * s * math.sin(a))], CLAW, 1.7 * s))
    return o


def arm(x0, y0, x1, y1, rot):
    return [F(kit.tube([(x0, y0), (x1, y1)], 17), BODY, st=BODY_ST, inset=2.4)] + paw(x1, y1, rot)


def face(look=0.0, mood="smile"):
    """Muzzle, nose, eyes, cheeks, mouth (the head is at the top of the body)."""
    o = [F(E(look * .5, -14, 24, 17), MUZ, st="#FFFFFF", inset=3, po=False)]
    o.append(F(E(look * .7, -24, 11.5, 9), NOSE, st=None, po=False))
    o.append(F(E(look * .7 - 3.5, -27, 3.6, 2.3), "#FFFFFF", lift=0, fuzz=False))
    if mood == "happy":
        for ex in (-15, 15):
            o.append(L([(ex - 5.5, -35), (ex, -40.5), (ex + 5.5, -35)], kit.DARK, 2.6))
    elif mood == "sleep":
        for ex in (-15, 15):
            o.append(L([(ex - 5.5, -38), (ex, -34), (ex + 5.5, -38)], kit.DARK, 2.4))
    else:
        o.append(EYE(-15 + look, -38, 5.6, look=(look * .25, 0)))
        o.append(EYE(15 + look, -38, 5.6, look=(look * .25, 0)))
    for ex in (-28, 28):
        o.append(F(E(ex + look * .4, -13, 5.8, 4.6), kit.CHEEK, lift=0))
    if mood == "happy":
        o.append(F(kit.G(crs([(-8, -5), (0, -5.5), (8, -5), (4, 3), (0, 4.5), (-4, 3)], 6)), "#B5414F", lift=0, fuzz=False))
    else:
        o.append(L([(-6 + look * .5, -4), (-3 + look * .5, -.5), (0 + look * .5, -4), (3 + look * .5, -.5), (6 + look * .5, -4)], kit.DARK, 1.9))
    return o


BODY_PTS = [(0, -62), (30, -57), (48, -33), (53, 0), (48, 31), (30, 51), (0, 57), (-30, 51), (-48, 31), (-53, 0), (-48, -33), (-30, -57)]


def body_shape():
    return kit.G(crs(BODY_PTS, 8))


def mole_pieces(pose):
    """土豆 in one pose, drawn round (0, 0); about 150 x 150 units with the hat and paws."""
    o = []
    look = 2.5 if pose == "point" else 0.0
    mood = {"cheer": "happy", "sleep": "sleep"}.get(pose, "smile")
    if pose == "sleep":
        return sleep_pieces()
    if pose == "peek":
        return peek_pieces()
    # arms behind the body for the raised ones
    if pose == "wave":
        o += arm(-38, -10, -64, -46, -70)
    if pose == "cheer":
        o += arm(-38, -10, -62, -50, -70) + arm(38, -10, 62, -50, -110)
    for sx in (-22, 22):
        o.append(F(E(sx, 55, 15, 9), PAW, st="#FFFFFF", inset=2.4))
    body = body_shape()
    o.append(F(body, BODY, st=BODY_ST))
    o.append(F(E(0, 24, 30, 26), BELLY, st=BELLY_ST, inset=3, lift=0))
    o += face(look, mood)
    o += place(hat(), 0, -55)
    if pose == "wave":
        o += arm(40, 0, 52, 22, 70)
    if pose == "point":
        o += arm(-40, 0, -52, 22, 110)
        o += arm(40, -8, 76, -12, -6)
    return OBJ(o)


def sleep_pieces():
    """Lying on his tummy on a little pillow, curled round, face to the front, eyes shut."""
    o = [F(R(-70, 30, 140, 28, 14), PILLOW, st="#FFFFFF", inset=3)]
    o.append(F(E(-62, 18, 9, 7, rot=-30), BODY, st=None))          # little tail
    body = kit.G(crs([(-62, 30), (-64, 2), (-48, -22), (-16, -36), (22, -38), (50, -22), (62, 4), (58, 32), (22, 42), (-30, 42)], 8))
    o.append(F(body, BODY, st=BODY_ST))
    o.append(F(E(-34, 40, 15, 8), PAW, st="#FFFFFF", inset=2.2))   # a foot
    o += place(face(0, "sleep"), 24, 25, s=.84)
    o += paw(8, 38, 150, .9) + paw(42, 40, 30, .9)
    o += place(hat(), 16, -30, s=.9, rot=-16)
    return OBJ(o)


def peek_pieces():
    o = [F(E(0, 14, 82, 30), DIRT, st=DIRT_ST, inset=3.4)]
    o.append(F(E(0, 9, 62, 17), HOLE, lift=0, shade=False))
    # the head: the top of the body, cut where it goes down the hole
    cut = sbox(-99, -200, 99, 9).union(E(0, 9, 62, 17))
    head = body_shape().intersection(cut)
    o.append(F(head, BODY, st=BODY_ST))
    o += face(0, "smile")
    o += place(hat(), 0, -55)
    ring = E(0, 14, 82, 30).difference(E(0, 9, 62, 17)).intersection(sbox(-99, 9, 99, 99))
    o.append(F(ring, DIRT, st=DIRT_ST, inset=3.4))
    o += paw(-34, 20, -100) + paw(34, 20, -80)
    for x, y in ((-60, 30), (52, 34), (66, 18)):
        o.append(F(E(x, y, 4, 3), "#8A6040", lift=0, fuzz=False))       # crumbs of soil
    return OBJ(o)


# where each pose sits in its 200 x 200 file (centre and scale)
POSE_AT = {"wave": (108, 116, 1.0), "point": (88, 112, 1.0), "cheer": (100, 120, .98),
           "sleep": (100, 116, 1.12), "peek": (100, 122, 1.04)}


def pose_file(pose):
    x, y, s = POSE_AT[pose]
    return place(mole_pieces(pose), x, y, s)


def build(styles=kit.STYLES):
    for st in styles:
        for pose in kit.TUDOU_POSES:
            text = kit.render(pose_file(pose), st, "tudou", f"tudou_{pose}", _Look)
            kit.write_svg(kit.ART / st / f"tudou_{pose}.svg", text, kit.KIND["tudou"])
    kit.check_tudou()
    print("tudou: " + ", ".join(f"{st} {sum((kit.ART / st / f'tudou_{p}.svg').stat().st_size for p in kit.TUDOU_POSES) / 1024:.0f} KB"
                                for st in styles))
