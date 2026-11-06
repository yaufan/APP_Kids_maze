"""Writes the game's pictures (kit.py: one geometry, three styles) and checks them.

    python3 build.py tudou                       # 土豆: app/assets/art/<a|b|c>/tudou_<pose>.svg
    python3 build.py garden                      # one world: app/assets/art/<a|b|c>/garden/*.svg
    python3 build.py all                         # 土豆 and every world_<name>.py in this folder
    python3 build.py check                       # only the checks (flutter_svg rules + docs/art.md)
    python3 build.py preview garden OUT.png      # contact sheet in a, b and c: a composed small road
                                                 # (no forks, 4 x 5) and a 6 x 6 maze with forks, key
                                                 # and gate, all 15 tiles, the things, 土豆, the family,
                                                 # the stickers and the card
    python3 build.py seams [garden|all]          # render every tile and compare every pair of edges
                                                 # that can meet (needs Chromium)
    python3 build.py fluttercheck [garden|tudou|all]
                                                 # draw every file with the real flutter_svg (a throw-away
                                                 # Flutter project in /dev/shm, deleted afterwards) and with
                                                 # Chromium, and compare them

A world is a module world_<name>.py with WORLD = kit.World(...). Previews, seams and the comparison
need Node.js with Playwright (Chromium); fluttercheck needs Flutter at /home/user/flutter/bin (or
$FLUTTER) and a pub cache that already has flutter_svg (the sibling apps filled it).
"""
import sys

sys.dont_write_bytecode = True      # no __pycache__ in design/art

import html  # noqa: E402
import importlib  # noqa: E402
import os  # noqa: E402
import pathlib  # noqa: E402
import random  # noqa: E402
import shutil  # noqa: E402
import subprocess  # noqa: E402
import tempfile  # noqa: E402

import kit  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
SCRATCH = pathlib.Path("/dev/shm") if pathlib.Path("/dev/shm").is_dir() else pathlib.Path(tempfile.gettempdir())


def world_names():
    return sorted(p.stem[len("world_"):] for p in HERE.glob("world_*.py"))


def world(name):
    return importlib.import_module(f"world_{name}").WORLD


def build_tudou():
    import tudou
    tudou.build()


def check_all():
    """Re-check every file on disk."""
    n_ = 0
    for st in kit.STYLES:
        for p in sorted((kit.ART / st).rglob("*.svg")):
            kit.check_svg(str(p.relative_to(kit.ROOT)), p.read_text())
            n_ += 1
    kit.check_tudou()
    for w in world_names():
        kit.check_world(w)
    print(f"check: {n_} SVG files are fine (土豆 and {len(world_names())} world(s): {', '.join(world_names())})")


# ================================================================ little mazes for the previews
DIRS = {1: (0, -1), 2: (1, 0), 4: (0, 1), 8: (-1, 0)}
OPP = {1: 4, 4: 1, 2: 8, 8: 2}


def winding_path(cols, rows, seed, min_len):
    """A path with no forks from the bottom-left corner (a self-avoiding random walk)."""
    rnd = random.Random(seed)
    for _ in range(4000):
        path = [(0, rows - 1)]
        seen = set(path)
        while True:
            x, y = path[-1]
            opts = [(x + dx, y + dy) for dx, dy in DIRS.values()
                    if 0 <= x + dx < cols and 0 <= y + dy < rows and (x + dx, y + dy) not in seen]
            # no touching an earlier cell sideways (keeps it a clean single road)
            opts = [c for c in opts if sum((c[0] + dx, c[1] + dy) in seen for dx, dy in DIRS.values()) == 1]
            if not opts:
                break
            c = rnd.choice(opts)
            path.append(c)
            seen.add(c)
        if len(path) >= min_len:
            return path
    raise SystemExit("no winding path found")


def masks_from_edges(cells, edges):
    m = {c: 0 for c in cells}
    for a, b in edges:
        for bit, (dx, dy) in DIRS.items():
            if (a[0] + dx, a[1] + dy) == b:
                m[a] |= bit
                m[b] |= OPP[bit]
    return m


def tree_maze(cols, rows, seed, holes):
    """A maze (a random spanning tree grown Prim-style, so it branches a lot) over the grid minus
    some empty cells for scenery."""
    rnd = random.Random(seed)
    allc = [(x, y) for y in range(rows) for x in range(cols)]
    start, goal = (0, rows - 1), (cols - 1, 0)
    while True:
        empty = set(rnd.sample([c for c in allc if c not in (start, goal)], holes))
        cells = set(c for c in allc if c not in empty)
        seen, edges = {start}, []
        front = [(start, (start[0] + dx, start[1] + dy)) for dx, dy in DIRS.values()]
        while front:
            a, b = front.pop(rnd.randrange(len(front)))
            if b not in cells or b in seen:
                continue
            seen.add(b)
            edges.append((a, b))
            front += [(b, (b[0] + dx, b[1] + dy)) for dx, dy in DIRS.values()]
        if goal in seen:
            empty |= cells - seen
            return sorted(seen), edges, sorted(empty), start, goal


def tree_path(edges, a, b):
    nb = {}
    for p, q in edges:
        nb.setdefault(p, []).append(q)
        nb.setdefault(q, []).append(p)
    prev, todo = {a: None}, [a]
    while todo:
        c = todo.pop()
        for d in nb.get(c, []):
            if d not in prev:
                prev[d] = c
                todo.append(d)
    out, c = [], b
    while c is not None:
        out.append(c)
        c = prev[c]
    return out[::-1], nb


def _img(src, x, y, w, h, extra=""):
    return (f'<img src="file://{src}" style="position:absolute;left:{x:.1f}px;top:{y:.1f}px;width:{w:.1f}px;'
            f'height:{h:.1f}px;{extra}">')


def board(wid, st, cols, rows, S, masks, empty, start, goal, stars=(), key=None, gate=None):
    d = kit.ART / st / wid
    W, H = cols * S, rows * S
    o = [_img(d / "bg.svg", 0, 0, W, H, "object-fit:cover")]
    for (x, y), m in masks.items():
        o.append(_img(d / f"tile_{m}.svg", x * S, y * S, S, S))
    for i, (x, y) in enumerate(empty):
        o.append(_img(d / f"deco_{i % 6 + 1}.svg", x * S, y * S, S, S))
    o.append(_img(d / "home.svg", goal[0] * S, goal[1] * S, S, S))
    for x, y in stars:
        o.append(_img(d / "star.svg", (x + .25) * S, (y + .25) * S, S / 2, S / 2))
    if key:
        o.append(_img(d / "key.svg", (key[0] + .25) * S, (key[1] + .25) * S, S / 2, S / 2))
    if gate:
        rot = "transform:rotate(90deg);" if masks[gate] in (5,) else ""
        o.append(_img(d / "gate.svg", gate[0] * S, gate[1] * S, S, S, rot))
    o.append(_img(d / "hero.svg", start[0] * S, start[1] * S, S, S))
    return f'<div style="position:relative;width:{W}px;height:{H}px;overflow:hidden;border-radius:10px">{"".join(o)}</div>'


def small_road(wid, st, S, seed=3):
    cols, rows = 4, 5
    path = winding_path(cols, rows, seed, 13)
    masks = masks_from_edges(path, list(zip(path, path[1:])))
    empty = [(x, y) for y in range(rows) for x in range(cols) if (x, y) not in masks]
    stars = [path[i] for i in (3, 7, 10) if i < len(path) - 1]
    return board(wid, st, cols, rows, S, masks, empty, path[0], path[-1], stars)


def big_maze(wid, st, S, seed=11):
    """A 6 x 6 maze with forks; the gate on a straight cell of the way home, the key in the farthest
    dead end that branches off before the gate (tries seeds until both fit)."""
    cols = rows = 6
    for sd in range(seed, seed + 200):
        cells, edges, empty, start, goal = tree_maze(cols, rows, sd, 5)
        masks = masks_from_edges(cells, edges)
        path, nb = tree_path(edges, start, goal)
        onpath = {c: i for i, c in enumerate(path)}
        gate = key = None
        for gi in range(len(path) - 2, 2, -1):
            if masks[path[gi]] in (5, 10):
                gate = path[gi]
                break
        if not gate:
            continue
        best = None
        for c in cells:
            if masks[c] in (1, 2, 4, 8) and c not in (start, goal):
                p, _ = tree_path(edges, start, c)
                attach = max(onpath.get(q, -1) for q in p)
                if attach < onpath[gate] and (best is None or len(p) > best[0]):
                    best = (len(p), c)
        if best and best[0] >= 4:
            key = best[1]
            break
    stars = [path[i] for i in (2, len(path) // 2) if path[i] not in (gate, key)]
    return board(wid, st, cols, rows, S, masks, empty, start, goal, stars, key, gate)


def _cell(inner, label, bg="#FFFFFF"):
    return f'<div class="cell" style="background:{bg}">{inner}<div class="lb">{html.escape(label)}</div></div>'


def _page(rows, width):
    css = ("body{margin:0;background:#E9E4DA;font:15px sans-serif;color:#433}"
           ".row{display:flex;flex-wrap:wrap;gap:8px;padding:6px 14px;align-items:flex-start}"
           ".cell{border-radius:10px;padding:5px}.lb{text-align:center;padding-top:2px;font-size:13px}"
           "h2{margin:12px 14px 0;font-size:18px}")
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head><body style="width:{width}px">{"".join(rows)}</body></html>'


def shoot(page_html, out, width):
    """HTML -> PNG with Playwright (full page)."""
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        hp = pathlib.Path(tmp) / "page.html"
        hp.write_text(page_html)
        js = pathlib.Path(tmp) / "shot.js"
        js.write_text("""const { chromium } = require('playwright');
(async () => { const [inp, out, w] = process.argv.slice(2);
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: +w, height: 800 }, deviceScaleFactor: 1 });
  await p.goto('file://' + inp); await p.waitForTimeout(500); await p.screenshot({ path: out, fullPage: true }); await b.close(); })();""")
        pathlib.Path(out).parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["node", str(js), str(hp), str(out), str(width)], check=True, cwd=tmp)


def preview(wid, out):
    W = world(wid)
    rows = []
    ground = {st: W.ground[st]["base"] if st != "c" else W.ground[st]["top"] for st in kit.STYLES}
    for st in kit.STYLES:
        rows.append(f"<h2>{html.escape(W.zh)} {wid} — {st}: 小小 road (4 x 5) and a 6 x 6 maze with key and gate</h2>")
        rows.append('<div class="row">' + _cell(small_road(wid, st, 104), "small road") + _cell(big_maze(wid, st, 104), "maze")
                    + _cell(f'<img src="file://{kit.ART / st / wid / "card.svg"}" width="450" height="300">', "card") + "</div>")
    for st in kit.STYLES:
        d = kit.ART / st / wid
        tiles = "".join(_cell(f'<img src="file://{d / f"tile_{m}.svg"}" width="104" height="104" style="display:block">', f"tile_{m}", ground[st])
                        for m in range(1, 16))
        rows.append(f"<h2>{st}: tiles 1-15</h2><div class='row'>{tiles}</div>")
    for st in kit.STYLES:
        d = kit.ART / st / wid
        things = ["hero", "home", "star", "key", "gate"] + [f"deco_{i}" for i in range(1, 7)]
        cells = "".join(_cell(f'<img src="file://{d / f"{t}.svg"}" width="120" height="120" style="display:block">', t, ground[st]) for t in things)
        rows.append(f"<h2>{st}: things</h2><div class='row'>{cells}</div>")
    for st in kit.STYLES:
        cells = "".join(_cell(f'<img src="file://{kit.ART / st / f"tudou_{p}.svg"}" width="180" height="180" style="display:block">', f"土豆 {p}", "#F6EFE3")
                        for p in kit.TUDOU_POSES)
        cells += _cell(f'<img src="file://{kit.ART / st / wid / "family.svg"}" width="300" height="300" style="display:block">', "family", "#FBE3EA")
        rows.append(f"<h2>{st}: 土豆 and the family</h2><div class='row'>{cells}</div>")
    for st in kit.STYLES:
        d = kit.ART / st / wid
        cells = "".join(_cell(f'<img src="file://{d / f"sticker_{i:02d}.svg"}" width="150" height="150" style="display:block">', f"{i:02d}", "#F6EFE3")
                        for i in range(1, 11))
        rows.append(f"<h2>{st}: stickers</h2><div class='row'>{cells}</div>")
    shoot(_page(rows, 1900), out, 1900)
    print(out)


# ================================================================ tile seams
SEAM_JS = r"""
const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const [list, out, px] = process.argv.slice(2);
  const files = fs.readFileSync(list, 'utf8').split('\n').filter(l => l.trim());
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: files.length * +px, height: +px }, deviceScaleFactor: 1 });
  const imgs = files.map((f, i) => `<img src="file://${f}" style="position:absolute;left:${i * px}px;top:0;width:${px}px;height:${px}px">`).join('');
  fs.writeFileSync(list + '.html', `<html><body style="margin:0;background:#808080">${imgs}</body></html>`);
  await p.goto('file://' + list + '.html');   // a file page, so the file:// images load
  await p.waitForTimeout(500);
  await p.screenshot({ path: out });
  await b.close();
})();
"""


def seams(wid, px=200):
    """Every tile edge that can meet another: the last pixel column (row) of one tile against the
    first of the other. Reports the worst mismatch per style."""
    import numpy as np
    from PIL import Image
    worst_all = 0.0
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        tmp = pathlib.Path(tmp)
        (tmp / "seam.js").write_text(SEAM_JS)
        for st in kit.STYLES:
            files = [kit.ART / st / wid / f"tile_{m}.svg" for m in range(1, 16)]
            (tmp / "list.txt").write_text("\n".join(map(str, files)))
            subprocess.run(["node", str(tmp / "seam.js"), str(tmp / "list.txt"), str(tmp / f"{st}.png"), str(px)], check=True, cwd=tmp)
            A = np.asarray(Image.open(tmp / f"{st}.png").convert("RGB")).astype(float)
            T = {m: A[:, (m - 1) * px:m * px] for m in range(1, 16)}
            for m, t in T.items():      # the road must be there (not just the grey page)
                if (np.abs(t - 128).max(axis=2) > 30).mean() < .25:
                    raise SystemExit(f"seams: tile_{m} ({st}) did not render")
            worst = (0.0, None)
            for a in range(1, 16):
                for b in range(1, 16):
                    for bit, opp, ea, eb in ((2, 8, lambda t: t[:, -1], lambda t: t[:, 0]), (4, 1, lambda t: t[-1, :], lambda t: t[0, :])):
                        if a & bit and b & opp:
                            D = np.abs(ea(T[a]) - eb(T[b])).max(axis=1)
                            # a seam is bad where many neighbouring pixels differ a lot (single pixels are fuzz)
                            bad = np.convolve((D > 70).astype(float), np.ones(5) / 5, mode="same").max()
                            score = max(bad, D.mean() / 255)
                            if score > worst[0]:
                                worst = (score, (a, b, "right/left" if bit == 2 else "bottom/top"))
            print(f"seams {wid} {st}: worst {worst[0]:.2f} at tiles {worst[1]}")
            worst_all = max(worst_all, worst[0])
    if worst_all > .6:
        raise SystemExit("some tile edges do not meet")
    print("seams: every pair of tiles that can meet joins up")


# ================================================================ flutter_svg against Chromium
DART_TEST = r"""
import 'dart:io';
import 'dart:ui' as ui;

import 'package:flutter/widgets.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('render svgs', (tester) async {
    final lines = File('list.txt').readAsLinesSync().where((l) => l.trim().isNotEmpty);
    final failed = <String>[];
    for (final line in lines) {
      final p = line.split('|');
      final w = int.parse(p[2]), h = int.parse(p[3]);
      await tester.runAsync(() async {
        try {
          final info = await vg.loadPicture(SvgStringLoader(File(p[0]).readAsStringSync()), null);
          final rec = ui.PictureRecorder();
          final c = Canvas(rec);
          c.scale(w / info.size.width, h / info.size.height);
          c.drawPicture(info.picture);
          final img = await rec.endRecording().toImage(w, h);
          final bytes = await img.toByteData(format: ui.ImageByteFormat.png);
          File(p[1]).writeAsBytesSync(bytes!.buffer.asUint8List());
          info.picture.dispose();
        } catch (e) {
          failed.add('${p[0]}: $e');
        }
      });
    }
    File('failed.txt').writeAsStringSync(failed.join('\n'));
  });
}
"""

CHROME_JS = r"""
const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const lines = fs.readFileSync(process.argv[2], 'utf8').split('\n').filter(l => l.trim());
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 400, height: 400 }, deviceScaleFactor: 1 });
  for (const line of lines) {
    const [inp, out, w, h] = line.split('|');
    const svg = fs.readFileSync(inp);
    await page.setViewportSize({ width: +w, height: +h });
    await page.setContent(`<html><body style="margin:0;background:transparent"><img style="display:block;width:${w}px;height:${h}px" src="data:image/svg+xml;base64,${svg.toString('base64')}"></body></html>`);
    await page.waitForFunction(() => document.images[0].complete);
    await page.screenshot({ path: out, omitBackground: true });
  }
  await browser.close();
})();
"""


def fluttercheck(which="all", keep=False, px=260):
    """Draw every SVG with flutter_svg (the app's renderer) and with Chromium; report the files whose
    pictures differ. A throw-away Flutter project in /dev/shm is made for it and deleted after."""
    import numpy as np
    from PIL import Image
    files = []
    for st in kit.STYLES:
        if which in ("all", "tudou"):
            files += sorted((kit.ART / st).glob("tudou_*.svg"))
        for wid in (world_names() if which == "all" else [which]):
            if (kit.ART / st / wid).is_dir():
                files += sorted((kit.ART / st / wid).glob("*.svg"))
    if not files:
        raise SystemExit(f"nothing to check for {which!r}")
    flutter = pathlib.Path(os.environ.get("FLUTTER", "/home/user/flutter/bin")) / "flutter"
    work = pathlib.Path(tempfile.mkdtemp(prefix="svgcheck_", dir=SCRATCH))
    try:
        (work / "lib").mkdir()
        (work / "test").mkdir()
        (work / "out").mkdir()
        (work / "pubspec.yaml").write_text("name: svgcheck\npublish_to: 'none'\nversion: 0.0.1\nenvironment:\n  sdk: ^3.13.7\n"
                                           "dependencies:\n  flutter:\n    sdk: flutter\n  flutter_svg: ^2.3.0\n"
                                           "dev_dependencies:\n  flutter_test:\n    sdk: flutter\n")
        (work / "lib" / "main.dart").write_text("void main() {}\n")
        (work / "test" / "render_test.dart").write_text(DART_TEST)
        (work / "shot.js").write_text(CHROME_JS)
        fl, cr = [], []
        for i, f in enumerate(files):
            vb = [float(v) for v in kit.ET.parse(f).getroot().get("viewBox").split()]
            s = px / max(vb[2], vb[3])
            w, h = max(8, round(vb[2] * s)), max(8, round(vb[3] * s))
            fl.append(f"{f}|{work / 'out' / f'{i}_f.png'}|{w}|{h}")
            cr.append(f"{f}|{work / 'out' / f'{i}_c.png'}|{w}|{h}")
        (work / "list.txt").write_text("\n".join(fl))
        (work / "crlist.txt").write_text("\n".join(cr))
        subprocess.run([str(flutter), "pub", "get", "--offline"], cwd=work, check=True, capture_output=True)
        r = subprocess.run([str(flutter), "test", "test/render_test.dart"], cwd=work, capture_output=True, text=True)
        if r.returncode:
            print(r.stdout[-3000:], r.stderr[-3000:])
            raise SystemExit("flutter test failed")
        failed = (work / "failed.txt").read_text().strip()
        if failed:
            print("flutter_svg could not draw:\n" + failed)
        subprocess.run(["node", str(work / "shot.js"), str(work / "crlist.txt")], cwd=work, check=True)
        rows = []
        for i, f in enumerate(files):
            a = work / "out" / f"{i}_f.png"
            b = work / "out" / f"{i}_c.png"
            if not a.exists():
                rows.append((1.0, 1.0, f))
                continue
            A = np.asarray(Image.open(a).convert("RGBA")).astype(float)
            B = np.asarray(Image.open(b).convert("RGBA")).astype(float)

            def flat(X):   # over white
                al = X[..., 3:4] / 255
                return X[..., :3] * al + 255 * (1 - al)
            D = np.abs(flat(A) - flat(B)).max(axis=2)
            # differences in single pixels are anti-aliasing; count pixels whose neighbourhood all differ
            big = D > 60
            core = big[1:-1, 1:-1] & big[:-2, 1:-1] & big[2:, 1:-1] & big[1:-1, :-2] & big[1:-1, 2:]
            rows.append((core.mean(), D.mean() / 255, f))
        rows.sort(key=lambda r: (-r[0], -r[1]))
        bad = [r for r in rows if r[0] > .004]
        print(f"fluttercheck: {len(files)} files; worst:")
        for frac, mean, f in rows[:8]:
            print(f"  {frac * 100:6.2f}% solid differences, mean {mean * 100:.2f}%  {f.relative_to(kit.ROOT)}")
        if keep:
            print("kept", work)
        if bad or failed:
            raise SystemExit(f"{len(bad)} files draw differently in flutter_svg (more than 0.4% of the picture)")
        print("fluttercheck: flutter_svg draws every file like Chromium")
    finally:
        if not keep:
            shutil.rmtree(work, ignore_errors=True)


def main(argv):
    if not argv:
        print(__doc__)
        return
    cmd = argv[0]
    if cmd == "tudou":
        build_tudou()
    elif cmd == "all":
        build_tudou()
        for w in world_names():
            world(w).build()
        check_all()
    elif cmd == "check":
        check_all()
    elif cmd == "preview":
        preview(argv[1], argv[2])
    elif cmd == "seams":
        for w in (world_names() if len(argv) < 2 or argv[1] == "all" else [argv[1]]):
            seams(w)
    elif cmd == "fluttercheck":
        fluttercheck(argv[1] if len(argv) > 1 else "all", keep="--keep" in argv)
    elif cmd in world_names():
        world(cmd).build()
    else:
        raise SystemExit(f"unknown: {cmd} (worlds: {', '.join(world_names())})")


if __name__ == "__main__":
    main(sys.argv[1:])
