import 'dart:collection';
import 'dart:math' as math;

import 'content.dart';

/// A side of a cell. The bits match the road tiles: `tile_<sum>.svg`
/// (docs/art.md: up 1, right 2, down 4, left 8).
enum Dir {
  up(1, 0, -1),
  right(2, 1, 0),
  down(4, 0, 1),
  left(8, -1, 0);

  const Dir(this.bit, this.dc, this.dr);

  final int bit;
  final int dc;
  final int dr;

  Dir get back => switch (this) {
        Dir.up => Dir.down,
        Dir.right => Dir.left,
        Dir.down => Dir.up,
        Dir.left => Dir.right,
      };
}

/// A square of the maze's grid: column and row, from the top left.
class Cell {
  const Cell(this.c, this.r);

  final int c;
  final int r;

  Cell go(Dir d) => Cell(c + d.dc, r + d.dr);

  /// The side [o] is on, if it is next to this one.
  Dir? toward(Cell o) {
    for (final d in Dir.values) {
      if (go(d) == o) return d;
    }
    return null;
  }

  int distance(Cell o) => (c - o.c).abs() + (r - o.r).abs();

  @override
  bool operator ==(Object other) => other is Cell && other.c == c && other.r == r;

  @override
  int get hashCode => Object.hash(c, r);

  @override
  String toString() => '($c,$r)';
}

/// A maze: the road cells and which of their sides are open, where the
/// hero starts and where home is, the stars on the way and (in an errand)
/// the key and the gate it opens. Cells that are not road get scenery.
class Maze {
  Maze({
    required this.cols,
    required this.rows,
    required Map<Cell, int> open,
    required this.start,
    required this.goal,
    this.stars = const [],
    this.key,
    this.gate,
    this.deco = const {},
  }) : open = Map.unmodifiable(open);

  final int cols;
  final int rows;

  /// Road cells and their open sides (a sum of [Dir.bit]s, 1–15).
  final Map<Cell, int> open;
  final Cell start;
  final Cell goal;
  final List<Cell> stars;

  /// The key to fetch before the gate opens (errands only).
  final Cell? key;

  /// The cell the gate stands in: it cannot be walked into without the key.
  final Cell? gate;

  /// Scenery in cells that are not road: `deco_<n>.svg`, n 1–6.
  final Map<Cell, int> deco;

  bool inside(Cell x) => x.c >= 0 && x.r >= 0 && x.c < cols && x.r < rows;

  bool road(Cell x) => open.containsKey(x);

  bool joins(Cell a, Dir d) => (open[a] ?? 0) & d.bit != 0;

  /// The road cells one step from [a].
  List<Cell> next(Cell a) => [for (final d in Dir.values) if (joins(a, d)) a.go(d)];

  /// Where the road splits: a choice to make.
  bool fork(Cell a) => next(a).length >= 3;

  /// A road that ends and is not somewhere to go.
  bool deadEnd(Cell a) => road(a) && next(a).length == 1 && a != start && a != goal && a != key;

  int get forks => open.keys.where(fork).length;

  /// The shortest way from [from] to [to] along the road, both ends
  /// included; null if there is none. [blocked] cells cannot be entered.
  List<Cell>? path(Cell from, Cell to, {Set<Cell> blocked = const {}}) {
    if (!road(from) || !road(to)) return null;
    final came = <Cell, Cell>{from: from};
    final queue = Queue<Cell>()..add(from);
    while (queue.isNotEmpty) {
      final here = queue.removeFirst();
      if (here == to) {
        final way = [to];
        while (way.last != from) {
          way.add(came[way.last]!);
        }
        return way.reversed.toList();
      }
      for (final n in next(here)) {
        if (came.containsKey(n) || blocked.contains(n)) continue;
        came[n] = here;
        queue.add(n);
      }
    }
    return null;
  }

  /// The way home (by way of the key in an errand).
  List<Cell> get solution {
    final k = key;
    if (k == null) return path(start, goal)!;
    return [...path(start, k, blocked: {?gate})!, ...path(k, goal)!.skip(1)];
  }

  /// A maze for [mode] at [level]; [n] is how many levels of this world
  /// the child has done, which makes it a little bigger as they go.
  factory Maze.make(Mode mode, Level level, int n, math.Random r) {
    final later = n >= 5;
    return switch ((mode, level)) {
      (Mode.road, Level.small) => Maze.road(4, 5, r, len: later ? (9, 12) : (7, 10)),
      (Mode.road, Level.mid) => Maze.road(4, 6, r, len: (10, 14)),
      (Mode.road, Level.big) => Maze.road(5, 6, r, len: (12, 16)),
      (Mode.maze, Level.small || Level.mid) => Maze.forks(4, 6, r, len: (9, 12), forks: n < 3 ? 1 : (n < 7 ? 2 : 3)),
      (Mode.maze, Level.big) => Maze.grid(later ? 6 : 5, later ? 7 : 6, r),
      (Mode.errand, _) => Maze.errand(later ? 6 : 5, later ? 7 : 6, r),
    };
  }

  /// One winding road and nothing else (for 2～3: no choices to make);
  /// [len] is how many cells long it may be.
  factory Maze.road(int cols, int rows, math.Random r, {required (int, int) len}) {
    final start = Cell(0, rows - 1);
    final way = _winding(cols, rows, start, len, r);
    final open = <Cell, int>{};
    for (var i = 1; i < way.length; i++) {
      _join(open, way[i - 1], way[i]);
    }
    return Maze(
      cols: cols,
      rows: rows,
      open: open,
      start: start,
      goal: way.last,
      stars: {for (final f in [0.3, 0.55, 0.8]) way[math.min(way.length - 2, math.max(1, (way.length * f).round()))]}.toList(),
      deco: _scenery(cols, rows, open, r),
    );
  }

  /// A road with [forks] short side roads (one or two cells) that end
  /// where you can see them (for 3～4).
  factory Maze.forks(int cols, int rows, math.Random r, {required (int, int) len, required int forks}) {
    for (var attempt = 0; attempt < 200; attempt++) {
      final start = Cell(0, rows - 1);
      final way = _winding(cols, rows, start, len, r);
      final open = <Cell, int>{};
      for (var i = 1; i < way.length; i++) {
        _join(open, way[i - 1], way[i]);
      }
      var made = 0;
      final spots = [for (var i = 2; i < way.length - 2; i++) way[i]]..shuffle(r);
      for (final at in spots) {
        if (made == forks) break;
        if (open[at] == null || _bits(open[at]!) != 2) continue;
        final room = [for (final d in Dir.values) if (_free(cols, rows, open, at.go(d))) at.go(d)]..shuffle(r);
        if (room.isEmpty) continue;
        _join(open, at, room.first);
        var tip = room.first;
        if (r.nextBool()) {
          final more = [for (final d in Dir.values) if (_free(cols, rows, open, tip.go(d))) tip.go(d)]..shuffle(r);
          if (more.isNotEmpty) {
            _join(open, tip, more.first);
            tip = more.first;
          }
        }
        made++;
      }
      if (made < forks) continue;
      return Maze(
        cols: cols,
        rows: rows,
        open: open,
        start: start,
        goal: way.last,
        stars: [way[way.length ~/ 3], way[way.length * 2 ~/ 3]],
        deco: _scenery(cols, rows, open, r),
      );
    }
    throw StateError('no maze with $forks forks in $cols×$rows');
  }

  /// A small grid maze where every cell is road and there is exactly one
  /// way between any two (for 4～5), from the bottom left to the top right.
  factory Maze.grid(int cols, int rows, math.Random r) {
    final open = _carve(cols, rows, r);
    final start = Cell(0, rows - 1), goal = Cell(cols - 1, 0);
    final way = Maze(cols: cols, rows: rows, open: open, start: start, goal: goal).path(start, goal)!;
    return Maze(cols: cols, rows: rows, open: open, start: start, goal: goal, stars: [way[way.length ~/ 3], way[way.length * 2 ~/ 3]]);
  }

  /// A grid maze with a gate in front of home and its key down a side road
  /// (for 4～5): fetch the key, then go home.
  factory Maze.errand(int cols, int rows, math.Random r) {
    for (var attempt = 0; attempt < 200; attempt++) {
      final open = _carve(cols, rows, r);
      final start = Cell(0, rows - 1), goal = Cell(cols - 1, 0);
      final plain = Maze(cols: cols, rows: rows, open: open, start: start, goal: goal);
      final way = plain.path(start, goal)!;
      if (way.length < 6) continue;
      final gate = way[way.length - 2];
      final onWay = way.toSet();
      // The key: at the end of a side road, two to six steps off the way
      // home, reachable without passing the gate.
      final keys = <Cell>[];
      for (final c in open.keys) {
        if (onWay.contains(c) || plain.next(c).length != 1) continue;
        final to = plain.path(start, c, blocked: {gate});
        if (to == null) continue;
        final off = to.where((x) => !onWay.contains(x)).length;
        if (off >= 2 && off <= 6) keys.add(c);
      }
      if (keys.isEmpty) continue;
      keys.sort((a, b) => a.distance(start).compareTo(b.distance(start)));
      final key = keys[r.nextInt(keys.length)];
      return Maze(cols: cols, rows: rows, open: open, start: start, goal: goal, key: key, gate: gate);
    }
    throw StateError('no errand in $cols×$rows');
  }
}

int _bits(int v) => [for (final d in Dir.values) if (v & d.bit != 0) d].length;

bool _inGrid(int cols, int rows, Cell x) => x.c >= 0 && x.r >= 0 && x.c < cols && x.r < rows;

bool _free(int cols, int rows, Map<Cell, int> open, Cell x) => _inGrid(cols, rows, x) && !open.containsKey(x);

void _join(Map<Cell, int> open, Cell a, Cell b) {
  final d = a.toward(b)!;
  open[a] = (open[a] ?? 0) | d.bit;
  open[b] = (open[b] ?? 0) | d.back.bit;
}

/// A road that winds from [start] without crossing itself, [len] cells long
/// (between the two numbers), ending well away from the start.
List<Cell> _winding(int cols, int rows, Cell start, (int, int) len, math.Random r) {
  final (shortest, longest) = len;
  final far = (cols + rows) ~/ 2;
  for (var attempt = 0; attempt < 500; attempt++) {
    final way = [start];
    final used = {start};
    Dir? last;
    while (way.length < longest) {
      final here = way.last;
      final options = [
        for (final d in Dir.values)
          if (_inGrid(cols, rows, here.go(d)) && !used.contains(here.go(d))) d,
      ]..shuffle(r);
      if (options.isEmpty) break;
      // Rather keep going the same way for a while (nicer curves), and
      // rather not hug the road already made.
      int crowd(Dir d) => [for (final e in Dir.values) here.go(d).go(e)].where(used.contains).length;
      options.sort((a, b) {
        final score = crowd(a).compareTo(crowd(b));
        if (score != 0) return score;
        return (a == last ? 0 : 1).compareTo(b == last ? 0 : 1);
      });
      final pick = r.nextDouble() < 0.75 ? options.first : options[r.nextInt(options.length)];
      last = pick;
      final step = here.go(pick);
      way.add(step);
      used.add(step);
    }
    for (var end = way.length - 1; end >= shortest - 1; end--) {
      if (way[end].distance(start) >= far) return way.sublist(0, end + 1);
    }
  }
  throw StateError('no road of $len in $cols×$rows');
}

/// Every cell joined, one way between any two (a randomised depth-first
/// carve).
Map<Cell, int> _carve(int cols, int rows, math.Random r) {
  final open = <Cell, int>{};
  final start = Cell(0, rows - 1);
  final seen = {start};
  final stack = [start];
  while (stack.isNotEmpty) {
    final here = stack.last;
    final options = [
      for (final d in Dir.values)
        if (_inGrid(cols, rows, here.go(d)) && !seen.contains(here.go(d))) here.go(d),
    ];
    if (options.isEmpty) {
      stack.removeLast();
      continue;
    }
    final n = options[r.nextInt(options.length)];
    _join(open, here, n);
    seen.add(n);
    stack.add(n);
  }
  return open;
}

/// Scenery for most cells that are not road.
Map<Cell, int> _scenery(int cols, int rows, Map<Cell, int> open, math.Random r) => {
      for (var row = 0; row < rows; row++)
        for (var col = 0; col < cols; col++)
          if (!open.containsKey(Cell(col, row)) && r.nextDouble() < 0.75) Cell(col, row): 1 + r.nextInt(6),
    };

/// What happened on a step (for sounds and words).
enum Event { star, key, gate, fork, deadEnd, home }

/// The hero on the way home: where they are, where they have been, what
/// they picked up. The rules for a finger (docs/design.md): dragging moves
/// the hero along the road a few cells at a time and never through a wall;
/// a tap further away walks there by itself but stops at a fork, so the
/// child still chooses the way.
class Walk {
  Walk(this.maze)
      : at = maze.start,
        trail = [maze.start];

  final Maze maze;
  Cell at;

  /// Where the hero has been, in order (drawn as a dotted trail).
  final List<Cell> trail;
  final Set<Cell> stars = {};
  var hasKey = false;

  /// A finger this many cells away along the road is "dragging".
  static const near = 3;

  bool get home => at == maze.goal;

  Set<Cell> get blocked => {if (maze.gate != null && !hasKey) maze.gate!};

  /// The cells to walk to go toward the finger at [target]: the way there
  /// if it is near; for a [tap] further away, the way up to the first fork.
  /// Empty if it is not on the road, or only through a wall.
  List<Cell> plan(Cell target, {required bool tap}) {
    if (!maze.road(target) || target == at) return const [];
    final way = maze.path(at, target, blocked: blocked);
    if (way == null) return const [];
    final steps = way.sublist(1);
    if (steps.length <= near) return steps;
    if (!tap) return const [];
    for (var i = 0; i < steps.length; i++) {
      if (maze.fork(steps[i])) return steps.sublist(0, i + 1);
    }
    return steps;
  }

  /// Whether a finger at [target] presses against a wall (or the closed
  /// gate) right next to the hero.
  bool bumps(Cell target) {
    final d = at.toward(target);
    if (d == null || !maze.inside(target)) return false;
    return !maze.joins(at, d) || blocked.contains(target);
  }

  /// One step to the neighbour [c]; what happened there.
  Set<Event> step(Cell c) {
    assert(maze.next(at).contains(c) && !blocked.contains(c), 'a step to $c from $at');
    at = c;
    trail.add(c);
    final events = <Event>{};
    if (maze.stars.contains(c) && stars.add(c)) events.add(Event.star);
    if (c == maze.key && !hasKey) {
      hasKey = true;
      events
        ..add(Event.key)
        ..add(Event.gate);
    }
    if (c == maze.goal) events.add(Event.home);
    if (maze.fork(c)) events.add(Event.fork);
    if (maze.deadEnd(c)) events.add(Event.deadEnd);
    return events;
  }

  /// The next few cells toward where to go now (the key first), for a hint.
  List<Cell> hint([int count = 3]) {
    final to = !hasKey && maze.key != null ? maze.key! : maze.goal;
    final way = maze.path(at, to, blocked: blocked) ?? const [];
    return way.skip(1).take(count).toList();
  }
}
