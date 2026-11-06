import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:maze_adventure/app/strings.dart';
import 'package:maze_adventure/core/content.dart';
import 'package:maze_adventure/core/game.dart';
import 'package:maze_adventure/core/maze.dart';
import 'package:maze_adventure/features/play/board.dart';
import 'package:maze_adventure/features/play/play_screen.dart';

import 'helpers.dart';

/// The whole app played through, on a phone and a tablet, with screenshots
/// in build/screenshots/ (CLAUDE.md 「完整流程和截圖」).
void main() {
  setUpAll(loadFonts);

  for (final (device, size, ratio) in [('phone', const Size(1080, 2340), 2.75), ('tablet', const Size(1620, 2160), 2.0)]) {
    testWidgets('the road, a maze, the sticker book, rest and parent mode ($device)', (tester) async {
      final app = await TestApp.start(tester, size: size, ratio: ratio);
      final play = Play(app);
      await play.shot(device, '01_home');

      await app.tapLabel(World.garden.zh, ms: 1000);
      expect(app.location, '/world/garden');
      await play.shot(device, '02_world');

      // 跟著路走: drag the bee a few cells, then tap home far away.
      await app.tapLabel(Mode.road.zh, ms: 1200);
      expect(app.location, '/play/garden/road');
      await play.shot(device, '03_road');
      final road = play.maze;
      expect(road.forks, 0);
      await play.drag(road.solution.take(4).toList());
      expect(play.walk.at, road.solution[3]);
      expect(app.sounds.played, contains('step_garden'));
      await play.shot(device, '04_road_drag');
      await play.tapCell(road.goal);
      await play.wait(road.solution.length * 0.2 + 1);
      expect(play.done, isTrue);
      expect(app.sounds.played, containsAll(['arrive', 'cheer']));
      expect(app.game.walkedIn(World.garden), 1);
      await play.wait(1.5);
      await play.shot(device, '05_home_at_last');
      await app.tapLabel(Strings.next, ms: 800);
      expect(play.done, isFalse);
      await app.tapLabel(Strings.home, ms: 800);
      expect(app.location, '/world/garden');

      // 走迷宮: a wall bumps, a hint lights the way, taps find the way home.
      await app.tapLabel(Mode.maze.zh, ms: 1200);
      final maze = play.maze;
      expect(maze.forks, greaterThanOrEqualTo(1));
      await play.shot(device, '06_maze');
      final wall = [for (final d in Dir.values) if (maze.inside(maze.start.go(d)) && !maze.joins(maze.start, d)) maze.start.go(d)];
      if (wall.isNotEmpty) {
        await play.tapCell(wall.first);
        expect(app.sounds.played.last, 'bump');
        expect(play.walk.at, maze.start, reason: 'walls stop the hero');
      }
      await app.tapLabel(Strings.hintButton, ms: 600);
      expect(app.sounds.played.last, 'hint');
      await play.shot(device, '07_maze_hint');
      await play.walkHome();
      expect(play.done, isTrue);
      await app.tapLabel(Strings.toMap, ms: 800);

      // Another style, the same maze.
      await app.tapLabel(Mode.maze.zh, ms: 1200);
      final same = play.maze;
      await app.tapLabel(Strings.switchStyle, ms: 1000);
      expect(app.game.settings.style, Style.b);
      expect(play.maze, same, reason: 'switching style keeps the maze');
      await play.shot(device, '08_style_b');
      await app.tapLabel(Strings.switchStyle, ms: 1000);
      expect(app.game.settings.style, Style.c);
      await play.shot(device, '09_style_c');
      await app.tapLabel(Strings.switchStyle, ms: 600);
      await app.tapLabel(Strings.home, ms: 800);
      await app.tapLabel(Strings.home, ms: 800);
      expect(app.location, '/');
      await play.shot(device, '10_home_stars');

      // The sticker book.
      await app.tapLabel(Strings.stickers, ms: 1000);
      await play.shot(device, '11_stickers');
      await app.tapLabel(Strings.home, ms: 800);

      // Parent mode, through the gate.
      await app.tapLabel(Strings.parent, ms: 800);
      await play.answerGate();
      expect(app.location, '/parent');
      await play.shot(device, '12_parent');
      await tester.tap(find.byKey(const ValueKey('level-big')));
      await app.settle();
      expect(app.game.settings.level, Level.big);
      await tester.tap(find.byTooltip(Strings.back));
      await app.settle();

      // The play time runs out: 土豆 sleeps.
      app.now = app.now.add(const Duration(minutes: 15, seconds: 5));
      await app.settle(2500);
      expect(app.location, '/rest');
      await play.shot(device, '13_rest');
      await app.end();
    });
  }

  testWidgets('4～5: fetch the key, the gate opens, then home', (tester) async {
    final app = await TestApp.start(tester, game: const Game(settings: Settings(level: Level.big)));
    final play = Play(app);
    await app.tapLabel(World.city.zh, ms: 1000);
    expect(find.bySemanticsLabel(Mode.errand.zh), findsOneWidget);
    await app.tapLabel(Mode.errand.zh, ms: 1200);
    final m = play.maze;
    expect(m.key, isNotNull);
    await play.shot('errand', '01_errand');
    // Straight for the gate: it is shut.
    final toGate = m.path(m.start, m.gate!)!;
    await play.drag(toGate.sublist(0, toGate.length - 1).take(4).toList());
    await play.walkHome();
    expect(play.walk.hasKey, isTrue);
    expect(app.sounds.played, containsAll(['key', 'gate', 'arrive']));
    expect(play.done, isTrue);
    await play.wait(1.5);
    await play.shot('errand', '02_home');
    await app.end();
  });

  testWidgets('the youngest: a world goes straight to the road; tapping home walks all the way', (tester) async {
    final app = await TestApp.start(tester, game: const Game(settings: Settings(level: Level.small)));
    final play = Play(app);
    await app.tapLabel(World.sea.zh, ms: 1200);
    expect(app.location, '/play/sea/road');
    await play.shot('littlest', '01_road');
    final m = play.maze;
    expect(m.forks, 0);
    await play.tapCell(m.goal);
    await play.wait(m.solution.length * 0.2 + 1);
    expect(play.done, isTrue);
    await play.shot('littlest', '02_home');
    await app.end();
  });

  testWidgets('every world and style draws; 20 seconds without a new cell brings a hint', (tester) async {
    final app = await TestApp.start(tester, game: const Game(settings: Settings(level: Level.big)));
    final play = Play(app);
    for (final w in World.values) {
      app.go('/play/${w.name}/maze');
      await app.settle(1200);
      if (w == World.garden) {
        await play.wait(21);
        expect(app.sounds.played.last, 'hint');
        expect(play.state.debugWalk.hint(), isNotEmpty);
      }
      await play.shot('worlds', w.name);
    }
    for (final s in [Style.b, Style.c]) {
      app.change((g) => g.copyWith(settings: g.settings.copyWith(style: s)));
      for (final w in World.values) {
        app.go('/play/${w.name}/errand');
        await app.settle(1200);
        await play.shot('worlds', '${w.name}_${s.name}');
      }
    }
    await app.end();
  });
}

/// Plays a maze the way a child would, using the maze on screen.
class Play {
  Play(this.app);

  final TestApp app;

  WidgetTester get tester => app.tester;

  PlayScreenState get state => tester.state<PlayScreenState>(find.byType(PlayScreen));
  Maze get maze => state.debugMaze;
  Walk get walk => state.debugWalk;
  bool get done => state.debugDone;

  Future<void> shot(String device, String name) async {
    await app.settle(300);
    await shoot(tester, device, name);
  }

  Future<void> wait(double seconds) async {
    for (var i = 0; i < (seconds * 4).ceil(); i++) {
      await app.settle(250);
    }
  }

  /// The middle of [c] on the screen.
  Offset centre(Cell c) {
    final rect = tester.getRect(find.byType(Board));
    final s = Board.cellIn(maze, rect.size);
    final topLeft = rect.center - Offset(maze.cols * s / 2, maze.rows * s / 2);
    return topLeft + Offset((c.c + 0.5) * s, (c.r + 0.5) * s);
  }

  Future<void> tapCell(Cell c) async {
    await tester.tapAt(centre(c));
    await app.settle(300);
  }

  /// A finger pressing the hero and moving along [cells] (the first is
  /// where the hero is).
  Future<void> drag(List<Cell> cells) async {
    final g = await tester.startGesture(centre(cells.first));
    await app.settle(100);
    for (final c in cells.skip(1)) {
      await g.moveTo(centre(c));
      await app.settle(300);
    }
    await g.up();
    await app.settle(300);
  }

  /// Taps a few cells ahead on the way home until the hero is there.
  Future<void> walkHome() async {
    for (var i = 0; i < 80 && !done; i++) {
      final ahead = walk.hint(3);
      if (ahead.isEmpty) break;
      await tapCell(ahead.last);
      await wait(0.8);
    }
  }

  Future<void> answerGate() async {
    const digits = {'零': 0, '一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9};
    final parts = (find.textContaining('加').evaluate().first.widget as Text).data!.split(' ');
    for (final d in '${digits[parts[0]]! + digits[parts[2]]!}'.split('')) {
      await tester.tap(find.byKey(ValueKey('gate-key-$d')));
      await app.settle(200);
    }
    await app.settle(800);
  }
}
