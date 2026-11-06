import 'dart:math' as math;

import 'package:flutter_test/flutter_test.dart';
import 'package:maze_adventure/core/content.dart';
import 'package:maze_adventure/core/game.dart';
import 'package:maze_adventure/core/maze.dart';

/// Every road cell's open sides lead to a road cell that opens back.
void expectWellFormed(Maze m) {
  for (final MapEntry(key: c, value: bits) in m.open.entries) {
    expect(bits, inInclusiveRange(1, 15), reason: '$c');
    expect(m.inside(c), isTrue, reason: '$c');
    for (final d in Dir.values) {
      if (bits & d.bit == 0) continue;
      final n = c.go(d);
      expect(m.road(n), isTrue, reason: '$c opens $d onto nothing');
      expect(m.joins(n, d.back), isTrue, reason: '$c→$n is one-way');
    }
  }
  expect(m.road(m.start) && m.road(m.goal), isTrue);
  expect(m.path(m.start, m.goal), isNotNull, reason: 'home can be reached');
  for (final s in m.stars) {
    expect(m.road(s), isTrue);
    expect(s, isNot(m.start));
    expect(s, isNot(m.goal));
  }
  for (final d in m.deco.keys) {
    expect(m.road(d), isFalse);
  }
}

void main() {
  test('2～3: one winding road, no forks, never a dead end, home far from the start', () {
    for (var seed = 0; seed < 300; seed++) {
      for (final n in [0, 6]) {
        final m = Maze.make(Mode.road, Level.small, n, math.Random(seed));
        expectWellFormed(m);
        expect(m.forks, 0, reason: 'seed $seed');
        expect(m.open.keys.where((c) => m.next(c).length == 1).toSet(), {m.start, m.goal}, reason: 'only the two ends');
        final way = m.path(m.start, m.goal)!;
        expect(way.length, m.open.length, reason: 'the whole road is the way');
        expect(way.length, inInclusiveRange(n == 0 ? 7 : 9, n == 0 ? 10 : 12));
        expect(m.goal.distance(m.start), greaterThanOrEqualTo((m.cols + m.rows) ~/ 2));
        expect(m.stars, isNotEmpty);
        expect(m.key, isNull);
      }
    }
  });

  test('3～4: one to three short side roads that end where you can see them', () {
    for (var seed = 0; seed < 300; seed++) {
      for (final (n, forks) in [(0, 1), (4, 2), (8, 3)]) {
        final m = Maze.make(Mode.maze, Level.mid, n, math.Random(seed));
        expectWellFormed(m);
        expect(m.forks, forks, reason: 'seed $seed level $n');
        final way = m.path(m.start, m.goal)!.toSet();
        for (final c in m.open.keys.where((c) => !way.contains(c))) {
          // Every side-road cell is at most two steps from the way home.
          final back = m.path(c, m.start)!;
          expect(back.takeWhile((x) => !way.contains(x)).length, lessThanOrEqualTo(2), reason: 'seed $seed: $c');
        }
      }
    }
  });

  test('4～5: a grid maze, every cell reachable, one way between any two', () {
    for (var seed = 0; seed < 100; seed++) {
      final m = Maze.make(Mode.maze, Level.big, 6, math.Random(seed));
      expectWellFormed(m);
      expect(m.open.length, m.cols * m.rows);
      // A tree: one fewer joins than cells.
      final joins = m.open.values.fold<int>(0, (a, b) => a + [for (final d in Dir.values) if (b & d.bit != 0) d].length) ~/ 2;
      expect(joins, m.open.length - 1);
      expect(m.start, Cell(0, m.rows - 1));
      expect(m.goal, Cell(m.cols - 1, 0));
    }
  });

  test('an errand: the key is off the way home, the gate stands before home and only the key opens it', () {
    for (var seed = 0; seed < 100; seed++) {
      final m = Maze.make(Mode.errand, Level.big, seed % 10, math.Random(seed));
      expectWellFormed(m);
      final gate = m.gate!, key = m.key!;
      expect(m.path(m.start, key, blocked: {gate}), isNotNull, reason: 'the key is reachable before the gate opens');
      expect(m.path(m.start, m.goal, blocked: {gate}), isNull, reason: 'home is behind the gate');
      expect(m.path(m.start, m.goal)!.contains(key), isFalse, reason: 'the key is down a side road');
      expect(m.next(m.goal), contains(gate));
      final sol = m.solution;
      expect(sol.first, m.start);
      expect(sol.last, m.goal);
      expect(sol, contains(key));
    }
  });

  test('a finger: dragging goes a few cells along the road, never through a wall; a far tap stops at a fork', () {
    final m = Maze.make(Mode.maze, Level.mid, 4, math.Random(7));
    final walk = Walk(m);
    final way = m.path(m.start, m.goal)!;
    // Dragging one cell ahead.
    expect(walk.plan(way[1], tap: false), [way[1]]);
    // Dragging too far ahead does nothing (a finger cannot jump).
    expect(walk.plan(way[6], tap: false), isEmpty);
    // A tap far away walks to the first fork on the way, or all the way.
    final tapped = walk.plan(m.goal, tap: true);
    expect(tapped, isNotEmpty);
    final forkAt = way.skip(1).where(m.fork).firstOrNull;
    expect(tapped.last, forkAt ?? m.goal);
    // Not on the road: nothing.
    final off = [for (var r = 0; r < m.rows; r++) for (var c = 0; c < m.cols; c++) Cell(c, r)].firstWhere((c) => !m.road(c));
    expect(walk.plan(off, tap: true), isEmpty);
    // A wall next to the hero is a bump.
    final wall = [for (final d in Dir.values) if (m.inside(m.start.go(d)) && !m.joins(m.start, d)) m.start.go(d)];
    for (final w in wall) {
      expect(walk.bumps(w), isTrue);
    }
    expect(walk.bumps(way[1]), isFalse);
  });

  test('walking home: stars, the key opening the gate, forks and dead ends are noticed', () {
    final m = Maze.make(Mode.errand, Level.big, 0, math.Random(3));
    final walk = Walk(m);
    expect(walk.plan(m.gate!, tap: true).contains(m.gate), isFalse, reason: 'the gate is shut');
    final events = <Event>{};
    for (final c in m.solution.skip(1)) {
      events.addAll(walk.step(c));
    }
    expect(walk.home, isTrue);
    expect(walk.hasKey, isTrue);
    expect(events, containsAll([Event.key, Event.gate, Event.home]));
    expect(walk.trail.first, m.start);
    expect(walk.trail.last, m.goal);

    final road = Maze.make(Mode.road, Level.small, 0, math.Random(5));
    final w2 = Walk(road);
    final picked = <Event>[];
    for (final c in road.solution.skip(1)) {
      picked.addAll(w2.step(c));
    }
    expect(picked.where((e) => e == Event.star).length, road.stars.length);
    expect(picked, isNot(contains(Event.fork)));
    expect(picked, isNot(contains(Event.deadEnd)));
  });

  test('a hint points along the way to go (to the key first)', () {
    final m = Maze.make(Mode.errand, Level.big, 0, math.Random(11));
    final walk = Walk(m);
    final hint = walk.hint();
    expect(hint, hasLength(3));
    expect(hint, orderedEquals(m.path(m.start, m.key!, blocked: {m.gate!})!.skip(1).take(3)));
  });

  test('each age gets its games: 2～3 only the road; 3～4 also mazes; 4～5 also errands', () {
    expect(const Settings(level: Level.small).modes, [Mode.road]);
    expect(const Settings(level: Level.mid).modes, [Mode.road, Mode.maze]);
    expect(const Settings(level: Level.big).modes, Mode.values);
    expect(const Settings(full: false).opens(World.city), isFalse);
    expect(const Settings(full: false).opens(World.sea), isTrue);
    expect(Style.c.next, Style.a);
  });

  test('progress and settings are kept, and a damaged save does not break the game', () {
    var g = const Game(settings: Settings(level: Level.big, minutes: 20, style: Style.c, hints: false, english: true));
    for (var i = 0; i < 12; i++) {
      g = g.home(World.sea);
    }
    g = g.home(World.city).rest(DateTime(2026, 11, 6, 10));
    final back = Game.fromJson(g.toJson());
    expect(back.walkedIn(World.sea), 12);
    expect(back.stickers(World.sea), 10);
    expect(back.starsOf(World.sea), 3);
    expect(back.starsOf(World.city), 1);
    expect(back.starsOf(World.garden), 0);
    expect(back.settings.level, Level.big);
    expect(back.settings.style, Style.c);
    expect(back.settings.hints, isFalse);
    expect(back.resting(DateTime(2026, 11, 6, 10, 30)), isTrue);
    expect(back.resting(DateTime(2026, 11, 6, 11, 1)), isFalse);

    final broken = Game.fromJson({
      'walked': {'sea': -1, 'city': 'x', 'snow': 4},
      'restSince': 3,
      'settings': {'level': 'giant', 'minutes': 8, 'style': 'q', 'voice': 'no'},
    });
    expect(broken.walked, {World.snow: 4});
    expect(broken.restSince, isNull);
    expect(broken.settings.level, Level.mid);
    expect(broken.settings.minutes, 15);
    expect(broken.settings.style, Style.a);
    expect(broken.settings.voice, isTrue);
  });
}
