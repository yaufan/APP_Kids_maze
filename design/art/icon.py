"""迷宮小冒險's app icon, in the game's default look (style a, 羊毛氈布書風: felt cut-outs with soft
shadows, fuzz and running stitches), drawn with kit.py, tudou.py and the garden's bee and flower like
the rest of the art. Three candidates:

    peek   土豆 peeks out of his hole at the end of a short winding felt path (the game's cream road
           with its brown stitch) that comes in from the bottom edge, a star on the way. Warm coral
           felt.
    maze   A little square felt maze board (3 x 3 cells, wide cream corridors, thin green walls, one
           wrong turn and one dead end) on lilac felt: the bee waits at the start, bottom left; the
           flower is the goal, top right.
    map    土豆's face and hard hat close up; he holds a little felt map with a dotted path from a
           green dot to a red heart. Mint felt.

    python3 icon.py preview OUT.png              # the three side by side: big, as the phone cuts them
                                                 # (round, rounded square) at 96 and 48 px, and at 48 px
                                                 # on a light and a dark home screen next to the sibling
                                                 # apps' icons (when their repos are on this machine)
    python3 icon.py export [peek|maze|map]       # writes the Android and iOS icons into app/ (default peek)

export writes
- Android, full square art: app/android/app/src/main/res/mipmap-{mdpi..xxxhdpi}/ic_launcher.png
  (48..192 px, opaque).
- Android adaptive icon (API 26+): mipmap-anydpi-v26/ic_launcher.xml, with
  drawable-{mdpi..xxxhdpi}/ic_launcher_foreground.png and ic_launcher_background.png (108 dp canvas;
  the whole subject stays inside the central 66 dp circle, the part every launcher mask shows).
- iOS: every PNG listed in app/ios/Runner/Assets.xcassets/AppIcon.appiconset/Contents.json, at its
  size, opaque (no alpha).

Everything is drawn in 200 x 200 units (the size of 土豆's own files), rendered at 1024 px by Chromium
(Node.js with Playwright; one browser for all the pictures) and scaled down with Pillow. The felt
details (stitches, fuzz, shadows) are sized for an icon seen at about 100 dp (KIND "icon" below), so the
stitches still show as a dotted line at 48 px. No randomness beyond kit's md5 seeds: the same script
gives the same bytes. Scratch files go to /dev/shm and are deleted.
"""
import sys

sys.dont_write_bytecode = True      # no __pycache__ in design/art

import json  # noqa: E402
import math  # noqa: E402
import pathlib  # noqa: E402
import subprocess  # noqa: E402
import tempfile  # noqa: E402

import shapely  # noqa: E402
from PIL import Image, ImageDraw, ImageFont  # noqa: E402
from shapely.ops import unary_union  # noqa: E402

import kit  # noqa: E402
import tudou as TD  # noqa: E402
import world_garden as GD  # noqa: E402
from kit import E, F, OBJ, R, crs, place  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
APP = ROOT / "app"
RES = APP / "android" / "app" / "src" / "main" / "res"
IOS = APP / "ios" / "Runner" / "Assets.xcassets" / "AppIcon.appiconset"
FONT = APP / "assets" / "fonts" / "jf-openhuninn-2.1.ttf"

U = 200                              # drawing units across the icon
C = 1024                             # rendered size, scaled down from here
DENSITIES = {"mdpi": 1, "hdpi": 1.5, "xhdpi": 2, "xxhdpi": 3, "xxxhdpi": 4}
VIEW = 72 / 108                      # how much of the adaptive canvas a launcher shows
FULL_R = .44 * U                     # full square art (legacy Android, iOS): the subject's radius; in the
                                     # adaptive foreground that is FULL_R * VIEW = 58.7 of 200 units, inside
                                     # the central 66 dp circle of 108 dp (61.1 units)

# file kinds for kit.render: K (dp per unit) as if the 200-unit icon were seen at 120 dp, so a stitch
# (1.6 dp) is 1/75 of the icon: still a dotted line at 96 px, not coarse at 192 or 1024 px;
# q = 4: path data on a quarter-unit grid (1.3 px at 1024 px).
K_ICON = .6
kit.KIND["icon"] = dict(w=U, h=U, K=K_ICON, px=5, q=4)
kit.KIND["icon_a"] = dict(w=U, h=U, K=K_ICON / VIEW, px=5, q=4)    # the adaptive layers (seen 1/VIEW bigger)

# colours (felt)
PATH, PATH_ST = GD.ROAD["a"]["fill"], GD.ROAD["a"]["stitch"]       # the garden road
YEL, PINK, RED, GRN = GD.YEL, GD.PINK, GD.RED, GD.GRN
WHITE = kit.WHITE
CORAL = "#F7826B"
LILAC = "#B6A2EE"
MINT = "#8FD8B4"
BOARD, BOARD_ST = "#9ED47C", "#FFFFFF"
PAPER, PAPER_ST, PAPER_FOLD = "#FFF4DA", "#D7B88E", "#F3E3C0"


# ================================================================ the three subjects (their own units)
def path_star(x, y, r):
    return OBJ([F(kit.star_shape(r, x, y), YEL, st="#FFFFFF", inset=1.8),
                F(E(x - r * .22, y - r * .3, r * .14, r * .09, rot=-35), "#FFFFFF", lift=0, fuzz=False, op=.85)])


def mole_peek():
    """土豆 peeking out of his hole: tudou.peek_pieces with a narrower mound, so he can be bigger."""
    mound, hole = E(0, 14, 70, 27), E(0, 9, 57, 15.5)
    o = [F(mound, TD.DIRT, st=TD.DIRT_ST, inset=3.4)]
    o.append(F(hole, TD.HOLE, lift=0, shade=False))
    head = TD.body_shape().intersection(kit.sbox(-99, -200, 99, 9).union(hole))
    o.append(F(head, TD.BODY, st=TD.BODY_ST))
    o += TD.face(0, "smile")
    o += place(TD.hat(), 0, -55)
    ring = mound.difference(hole).intersection(kit.sbox(-99, 9, 99, 99))
    o.append(F(ring, TD.DIRT, st=TD.DIRT_ST, inset=3.4))
    o += TD.paw(-32, 20, -100) + TD.paw(32, 20, -80)
    for x, y in ((-50, 30), (44, 33), (58, 20)):
        o.append(F(E(x, y, 3.6, 2.8), "#8A6040", lift=0, fuzz=False))       # crumbs of soil
    return OBJ(o)


# the peek icon is laid out in the icon's own 200 units: 土豆 (x, y, scale) and the path, which comes in
# from beyond the bottom edge (it is in the background layer, so it runs off under every mask; a path
# with both ends in the picture looked like a letter, S or J)
PEEK_AT = (116, 82, .84)
PEEK_PATH = [(150, 340), (90, 205), (40, 170), (42, 132), (74, 110), (108, 96)]     # ends deep under the mound
PEEK_STAR = (44, 158, 13)


def peek():
    """土豆 peeking out of his hole (the path and its star are in bg_peek)."""
    return place(mole_peek(), *PEEK_AT)


MAZE = {(0, 0): 6, (1, 0): 8, (2, 0): 4,          # cells: their open sides (up 1, right 2, down 4, left 8)
        (0, 1): 5, (1, 1): 6, (2, 1): 13,
        (0, 2): 3, (1, 2): 9, (2, 2): 1}


def corridors(cells, T, wall, r):
    """Wide corridors (the cell less `wall` on each side, joined to the open neighbours), corners
    rounded by r. With the game's road width (kit.tile_geom, 62 of 100) a 3 x 3 maze looked like a
    letter; wide corridors and thin walls look like a maze."""
    gs = []
    for (i, j), m in cells.items():
        x0, y0, w = i * T + wall, j * T + wall, T - 2 * wall
        gs.append(kit.sbox(x0, y0, x0 + w, y0 + w))
        if m & 2:
            gs.append(kit.sbox(x0 + w / 2, y0, x0 + T + w / 2, y0 + w))
        if m & 4:
            gs.append(kit.sbox(x0, y0 + w / 2, x0 + w, y0 + T + w / 2))
    return kit.soft(unary_union(gs), r)


def maze():
    """A 3 x 3 felt maze board: cream corridors with the game's road stitch, thin green walls; the bee
    at the start (bottom left), the flower is the goal (top right); one wrong turn, one dead end."""
    T, m = 100, 12
    o = OBJ([F(R(-m, -m, 3 * T + 2 * m, 3 * T + 2 * m, 70), BOARD, st=BOARD_ST, inset=4.2)])
    o.append(kit.Piece("road", corridors(MAZE, T, 16, 10), "#000000", data=dict(fill=PATH, stitch=PATH_ST)))
    o += OBJ(place(GD.flower_head(42, PINK, YEL), 2.5 * T, .5 * T, rot=8))
    o += OBJ(place(GD.bee(look=9), .5 * T, 2.5 * T + 4, .9))
    return o


def mole_front():
    """土豆 standing, face to the front, no arms (his paws hold whatever is in front of him)."""
    o = []
    for sx in (-22, 22):
        o.append(F(E(sx, 55, 15, 9), TD.PAW, st="#FFFFFF", inset=2.4))
    o.append(F(TD.body_shape(), TD.BODY, st=TD.BODY_ST))
    o += TD.face(0, "smile")
    o += place(TD.hat(), 0, -55)
    return OBJ(o)


def little_map():
    """A felt map (its middle at 0, 0), folded in three, with a dotted path from a dot to a heart."""
    w, h = 112, 64
    o = [F(R(-w / 2, -h / 2, w, h, 7), PAPER, st=PAPER_ST, inset=2.6)]
    o.append(F(R(-w / 6, -h / 2 + 1.5, w / 3, h - 3, 1), PAPER_FOLD, lift=0, fuzz=False))
    o.append(F(E(-38, 15, 6.4), GRN, st="#FFFFFF", inset=1.4, lift=.5))
    pts = crs([(-38, 15), (-20, 14), (-16, -2), (4, -12), (14, 4), (28, -6)], 14, closed=False)
    ln = shapely.LineString(pts)
    k = 9
    for i in range(1, k):
        p = ln.interpolate(ln.length * i / k)
        o.append(F(E(p.x, p.y, 3.1), RED, lift=0, fuzz=False, shade=False))
    o += place([F(kit.heart_pts(0, 0, 11), RED, st="#FFFFFF", inset=1.4)], 31, -9)
    return o


def map_():
    """土豆 holding his little map in front of his tummy."""
    o = mole_front()
    o += OBJ(place(little_map(), 0, 32, rot=-5))
    o += OBJ(TD.paw(-56, 34, -62) + TD.paw(56, 28, -118))
    return o


# ================================================================ backgrounds (full 200 x 200, opaque)
def ground(base):
    return kit.Piece("ground", kit.sbox(0, 0, 1, 1), "#000000",
                     data=dict(base=base, fibres=(kit.lt(base, .2), kit.dk(base, .09)), per=9.5))


def deco(view, items):
    """French knots (little felt dots) and tiny felt stars, placed from the middle so the adaptive
    layer (of which a launcher shows only the middle `view`) keeps them in sight."""
    o = []
    for kind, dx, dy, r, col in items:
        x, y, rr = U / 2 + dx * view, U / 2 + dy * view, r * view
        if kind == "star":
            o += OBJ([F(kit.star_shape(rr, x, y), col, lift=.5, fuzz=False)])
        else:
            o += OBJ([F(E(x, y, rr), col, lift=.5, fuzz=False)])
    return o


def from_middle(view, x, y):
    return U / 2 + (x - U / 2) * view, U / 2 + (y - U / 2) * view


def bg_peek(view):
    """Coral felt, and the felt path from beyond the corner to 土豆's hole, a star on the way."""
    line = [from_middle(view, x, y) for x, y in crs(PEEK_PATH, 16, closed=False)]
    o = [ground(CORAL), kit.Piece("road", kit.tube(line, 36 * view), "#000000", data=dict(fill=PATH, stitch=PATH_ST))]
    x, y, r = PEEK_STAR
    o += path_star(*from_middle(view, x, y), r * view)
    return o + deco(view, [
        ("dot", 74, 66, 3.4, "#FFE0D6"), ("dot", 86, 52, 2.6, "#FFD27A"), ("star", -74, -70, 7, "#FFD27A"),
        ("dot", -86, -50, 2.6, "#FFE0D6"), ("dot", 40, 84, 2.6, "#FFE0D6")])


def bg_maze(view):
    return [ground(LILAC)] + deco(view, [
        ("dot", -84, -86, 3, "#F1EAFF"), ("dot", 86, 86, 3, "#F1EAFF"), ("star", 88, -88, 6, "#FFE36B"),
        ("star", -88, 88, 5, "#FFFFFF")])


def bg_map(view):
    return [ground(MINT)] + deco(view, [
        ("dot", -80, -76, 3, "#EAFFF4"), ("dot", 84, 80, 3, "#EAFFF4"), ("star", 80, -78, 7, "#FFE36B"),
        ("dot", -84, 72, 2.6, "#FFFFFF")])


CANDIDATES = {                          # subject, background, label, subject already placed?
    "peek": (peek, bg_peek, "1 地洞和小路", True),
    "maze": (maze, bg_maze, "2 小迷宮", False),
    "map": (map_, bg_map, "3 土豆看地圖", False),
}
DEFAULT = "peek"


# ================================================================ placing and drawing
def silhouette(pieces):
    gs = []
    for p in pieces:
        if p.kind in ("fill", "road"):
            gs.append(p.geom)
        elif p.kind == "line":
            gs.append(p.geom.buffer(p.w / 2))
        elif p.kind in ("eye", "button"):
            gs.append(p.geom.buffer(p.r))
    return unary_union(gs)


def placed(name):
    """The candidate's subject in the full square art: moved and scaled so it sits in the middle and
    its smallest enclosing circle has radius FULL_R (unless the candidate places it itself). Checks it
    stays inside that circle, so the adaptive foreground (the same, VIEW times smaller) stays inside
    the central 66 dp circle that every launcher mask shows."""
    pieces = CANDIDATES[name][0]()
    if not CANDIDATES[name][3]:
        sil = silhouette(pieces)
        r = shapely.minimum_bounding_radius(sil)
        c = shapely.minimum_bounding_circle(sil).centroid
        s = FULL_R / r
        pieces = place(pieces, U / 2 - c.x * s, U / 2 - c.y * s, s)
    hull = silhouette(pieces).convex_hull
    far = max(math.hypot(x - U / 2, y - U / 2) for x, y in hull.exterior.coords)
    if far > FULL_R * 1.02:
        sys.exit(f"{name}: the subject reaches {far:.1f} units from the middle (keep within {FULL_R * 1.02:.1f})")
    return pieces


def inner(svg):
    """The inside of the <svg> element kit.render wrote."""
    return svg[svg.index(">") + 1:svg.rindex("</svg>")]


def doc(px, body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {U} {U}" width="{px}" height="{px}">{body}</svg>'


def subject_svg(name, adaptive):
    pieces = placed(name)
    if adaptive:          # the adaptive foreground: the same subject, VIEW times smaller round the middle
        pieces = place(pieces, U / 2 * (1 - VIEW), U / 2 * (1 - VIEW), VIEW)
    return doc(C, inner(kit.render(pieces, "a", "icon_a" if adaptive else "icon", f"icon/{name}")))


def background_svg(name, adaptive):
    pieces = CANDIDATES[name][1](VIEW if adaptive else 1.0)
    return doc(C, inner(kit.render(pieces, "a", "icon_a" if adaptive else "icon", f"icon/{name}/bg")))


RENDER_JS = """
const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const jobs = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
  const browser = await chromium.launch();
  for (const [inp, out, px] of jobs) {
    for (let tries = 1; ; tries++) {          // a screenshot now and then fails while the machine is busy
      const page = await browser.newPage({ viewport: { width: px, height: px }, deviceScaleFactor: 1 });
      try {
        await page.goto('file://' + inp);
        await page.screenshot({ path: out, omitBackground: true });
        break;
      } catch (e) {
        if (tries >= 3) throw e;
      } finally {
        await page.close();
      }
    }
  }
  await browser.close();
})();
"""


def render_all(svgs):
    """{key: svg text} -> {key: RGBA image}, all drawn by one Chromium."""
    shm = "/dev/shm" if pathlib.Path("/dev/shm").is_dir() else None
    with tempfile.TemporaryDirectory(dir=shm, prefix="maze_icon_") as tmp:
        tmp = pathlib.Path(tmp)
        jobs = []
        for i, (key, text) in enumerate(svgs.items()):
            src, out = tmp / f"{i}.svg", tmp / f"{i}.png"
            src.write_text(text)
            jobs.append([str(src), str(out), C])
        (tmp / "jobs.json").write_text(json.dumps(jobs))
        (tmp / "r.js").write_text(RENDER_JS)
        subprocess.run(["node", str(tmp / "r.js"), str(tmp / "jobs.json")], check=True)
        return {key: Image.open(tmp / f"{i}.png").convert("RGBA").copy() for i, key in enumerate(svgs)}


def art(names):
    """{name: (full square art RGB, adaptive background RGB, adaptive foreground RGBA)}."""
    svgs = {}
    for nm in names:
        svgs[(nm, "bg")] = background_svg(nm, False)
        svgs[(nm, "fg")] = subject_svg(nm, False)
        svgs[(nm, "abg")] = background_svg(nm, True)
        svgs[(nm, "afg")] = subject_svg(nm, True)
    im = render_all(svgs)
    out = {}
    for nm in names:
        full = Image.alpha_composite(im[(nm, "bg")], im[(nm, "fg")]).convert("RGB")
        out[nm] = (full, im[(nm, "abg")].convert("RGB"), im[(nm, "afg")])
    return out


def launcher_view(bg, fg):
    """The adaptive icon as a launcher shows it: both layers, the middle 72 dp of 108."""
    whole = Image.alpha_composite(bg.convert("RGBA"), fg).convert("RGB")
    k = C * 18 / 108
    return whole.crop((round(k), round(k), round(C - k), round(C - k)))


def resized(img, px):
    return img.resize((px, px), Image.LANCZOS)


def mask(kind, px):
    s = px * 4
    m = Image.new("L", (s, s), 0)
    dr = ImageDraw.Draw(m)
    if kind == "round":
        dr.ellipse((0, 0, s - 1, s - 1), fill=255)
    elif kind == "squircle":
        pts = []
        for i in range(720):
            t = 2 * math.pi * i / 720
            c, si = math.cos(t), math.sin(t)
            pts.append((s / 2 + s / 2 * math.copysign(abs(c) ** (2 / 5), c), s / 2 + s / 2 * math.copysign(abs(si) ** (2 / 5), si)))
        dr.polygon(pts, fill=255)
    else:                                       # iOS-like rounded square
        dr.rounded_rectangle((0, 0, s - 1, s - 1), radius=s * .225, fill=255)
    return m.resize((px, px), Image.LANCZOS)


# ================================================================ preview
SIBLINGS = (("畫畫小鎮", "APP_Kids_Paint"), ("字母寵物", "app_kids_paint_for_learning_writing"), ("動物小餐廳", "app_kids_cook"),
            ("小卡認天下", "app_kids_card_game"), ("想一想樂園", "app_kids_brainstorming"), ("眼尖尖", "app_kids_falsecharge"))


def font(size):
    try:
        return ImageFont.truetype(str(FONT), size)
    except OSError:
        return ImageFont.load_default()


def siblings():
    out = []
    for zh, repo in SIBLINGS:
        p = ROOT.parent / repo / "app" / "android" / "app" / "src" / "main" / "res" / "mipmap-xxxhdpi" / "ic_launcher.png"
        if p.is_file():
            out.append((zh, Image.open(p).convert("RGB")))
    return out


def home_screen(icons, dark, W):
    """A strip of a phone's home screen: icons (label, image) at 48 px, round, with their names."""
    H = 104
    top, bottom = ("#3A3550", "#1E1B2B") if dark else ("#F6EFE6", "#E3EEF8")
    strip = Image.new("RGB", (W, H))
    dr = ImageDraw.Draw(strip)
    for y in range(H):
        dr.line([(0, y), (W, y)], fill=kit.mix(top, bottom, y / (H - 1)))
    step = W / len(icons)
    f = font(13)
    for i, (label, im) in enumerate(icons):
        x = round(step * i + step / 2 - 24)
        strip.paste(resized(im, 48), (x, 18), mask("round", 48))
        tw = dr.textlength(label, font=f)
        dr.text((x + 24 - tw / 2, 74), label, font=f, fill="#FFFFFF" if dark else "#3B3550")
    return strip


def preview(out):
    names = list(CANDIDATES)
    arts = art(names)
    views = {nm: launcher_view(arts[nm][1], arts[nm][2]) for nm in names}
    col, pad, big = 420, 24, 320
    W = pad * 2 + col * len(names)
    H = 24 + big + 60 + 120 + 24 + 104 * 2 + 24
    sheet = Image.new("RGB", (W, H), "#FFFFFF")
    dr = ImageDraw.Draw(sheet)
    f = font(30)
    for i, nm in enumerate(names):
        x0 = pad + col * i
        v, full = views[nm], arts[nm][0]
        sheet.paste(resized(v, big), (x0 + (col - big) // 2, 24), mask("squircle", big))
        label = CANDIDATES[nm][2] + ("（建議）" if nm == DEFAULT else "")
        tw = dr.textlength(label, font=f)
        dr.text((x0 + col / 2 - tw / 2, 24 + big + 12), label, font=f, fill="#3B3550")
        y = 24 + big + 64
        x = x0 + 44
        for kind, im, s in (("round", v, 96), ("square", full, 96), ("round", v, 48), ("square", full, 48)):
            sheet.paste(resized(im, s), (x, y + 96 - s), mask(kind, s))
            x += s + 26
    y = 24 + big + 60 + 120 + 24
    icons = siblings() + [(CANDIDATES[nm][2][2:], views[nm]) for nm in names]
    sheet.paste(home_screen(icons, False, W - 2 * pad), (pad, y))
    sheet.paste(home_screen(icons, True, W - 2 * pad), (pad, y + 104))
    sheet.save(out)
    print(out)


# ================================================================ export
ADAPTIVE_XML = """<?xml version="1.0" encoding="utf-8"?>
<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
    <background android:drawable="@drawable/ic_launcher_background"/>
    <foreground android:drawable="@drawable/ic_launcher_foreground"/>
</adaptive-icon>
"""


def export(name):
    full, bg, fg = art([name])[name]
    written = []
    for d, k in DENSITIES.items():
        mip = RES / f"mipmap-{d}"
        mip.mkdir(parents=True, exist_ok=True)
        resized(full, round(48 * k)).save(mip / "ic_launcher.png")
        dr = RES / f"drawable-{d}"
        dr.mkdir(parents=True, exist_ok=True)
        resized(fg, round(108 * k)).save(dr / "ic_launcher_foreground.png")
        resized(bg, round(108 * k)).save(dr / "ic_launcher_background.png")
        written += [mip / "ic_launcher.png", dr / "ic_launcher_foreground.png", dr / "ic_launcher_background.png"]
    anydpi = RES / "mipmap-anydpi-v26"
    anydpi.mkdir(parents=True, exist_ok=True)
    (anydpi / "ic_launcher.xml").write_text(ADAPTIVE_XML)
    written.append(anydpi / "ic_launcher.xml")
    contents = json.loads((IOS / "Contents.json").read_text())
    sizes = {}
    for image in contents["images"]:
        if image.get("filename"):
            px = round(float(image["size"].split("x")[0]) * float(image["scale"].rstrip("x")))
            if sizes.setdefault(image["filename"], px) != px:
                sys.exit(f"{image['filename']} is listed at two sizes in Contents.json")
    for fname, px in sizes.items():
        resized(full, px).convert("RGB").save(IOS / fname)
        written.append(IOS / fname)
    manifest = (APP / "android" / "app" / "src" / "main" / "AndroidManifest.xml").read_text()
    if 'android:icon="@mipmap/ic_launcher"' not in manifest:
        print("note: AndroidManifest.xml's android:icon is not @mipmap/ic_launcher")
    for p in written:
        print(p.relative_to(ROOT))


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "export":
        nm = sys.argv[2] if len(sys.argv) >= 3 else DEFAULT
        if nm not in CANDIDATES:
            sys.exit(f"unknown icon {nm!r}: one of {', '.join(CANDIDATES)}")
        export(nm)
    elif len(sys.argv) >= 3 and sys.argv[1] == "preview":
        preview(sys.argv[2])
    else:
        print(__doc__)
