import 'dart:async';

import 'package:audioplayers/audioplayers.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:maze_adventure/app/strings.dart';
import 'package:maze_adventure/core/content.dart';
import 'package:maze_adventure/core/game.dart';
import 'package:maze_adventure/core/providers.dart';
import 'package:maze_adventure/core/sounds.dart';
import 'package:maze_adventure/core/voice.dart';
import 'package:maze_adventure/features/parent/parent_gate.dart';
import 'package:maze_adventure/core/maze.dart';
import 'package:maze_adventure/features/play/board.dart';
import 'package:maze_adventure/features/play/play_screen.dart';

import 'helpers.dart';

/// A voice that takes as long as the test says (a slow phone voice).
class SlowVoice extends RecordingVoice {
  final pending = <Completer<void>>[];

  @override
  Future<void> say(String zh, {String? en}) {
    super.say(zh, en: en);
    final c = Completer<void>();
    pending.add(c);
    return c.future;
  }

  void finish() {
    for (final c in pending) {
      if (!c.isCompleted) c.complete();
    }
  }
}

/// The lessons from the sibling apps' reviews, on the screens: the play
/// time, the phone's back key, the parent pages, the child's palette
/// button, 土豆's hints and voice, and the fingers on the maze.
void main() {
  group('the play time', () {
    testWidgets('time at the parent gate and in parent mode is not the child\'s', (tester) async {
      final app = await TestApp.start(tester);
      await app.pass(const Duration(minutes: 10));
      await app.tapLabel(Strings.parent, ms: 800);
      expect(find.byType(ParentGatePage), findsOneWidget);
      await app.pass(const Duration(minutes: 8));
      await app.answerGate();
      expect(app.location, '/parent');
      await app.pass(const Duration(minutes: 20));
      expect(app.location, '/parent');
      await tester.tap(find.byTooltip(Strings.back));
      await app.settle(2600);
      expect(app.location, '/', reason: 'the child has played 10 of the 15 minutes');
      await app.pass(const Duration(minutes: 4));
      expect(app.location, '/');
      await app.pass(const Duration(minutes: 2));
      expect(app.location, '/rest');
      await app.end();
    });

    testWidgets('the background is not play time, and no rest starts there; ten minutes away is a new sitting', (tester) async {
      final app = await TestApp.start(tester);
      await app.pass(const Duration(minutes: 12));
      await app.hide();
      await app.pass(const Duration(minutes: 5));
      expect(app.game.restSince, isNull, reason: 'no rest begins in the background');
      await app.show();
      await app.pass(const Duration(minutes: 2));
      expect(app.location, '/', reason: '14 minutes played: the phone call did not count');
      await app.pass(const Duration(minutes: 2));
      expect(app.location, '/rest');
      await app.tapLabel(Strings.parent, ms: 800);
      await app.answerGate();
      expect(app.location, '/', reason: 'a parent let play go on');
      await app.pass(const Duration(minutes: 12));
      await app.hide();
      await app.pass(const Duration(minutes: 10));
      await app.show();
      await app.pass(const Duration(minutes: 14));
      expect(app.location, '/', reason: 'ten minutes away: a new sitting');
      await app.end();
    });

    testWidgets('closed and opened again within ten minutes, the sitting goes on', (tester) async {
      var app = await TestApp.start(tester);
      await app.pass(const Duration(minutes: 12));
      await app.hide();
      final saved = app.saved, then = app.now;
      await app.show();
      await app.end();

      app = await TestApp.start(tester, game: saved, now: then.add(const Duration(minutes: 5)));
      await app.pass(const Duration(minutes: 2));
      expect(app.location, '/');
      await app.pass(const Duration(minutes: 2));
      expect(app.location, '/rest', reason: '12 + 4 minutes');
      await app.end();

      app = await TestApp.start(tester, game: saved, now: then.add(const Duration(minutes: 10)));
      await app.pass(const Duration(minutes: 14));
      expect(app.location, '/', reason: 'closed ten minutes: a new sitting');
      await app.end();
    });

    testWidgets('a clock moved back gives no extra time and does not end the rest early; the rest outlasts a restart', (tester) async {
      var app = await TestApp.start(tester);
      await app.pass(const Duration(minutes: 10));
      app.now = app.now.subtract(const Duration(days: 1));
      await app.settle(2600);
      await app.pass(const Duration(minutes: 4));
      expect(app.location, '/');
      await app.pass(const Duration(minutes: 2));
      expect(app.location, '/rest');
      app.now = app.now.subtract(const Duration(hours: 2));
      await app.settle(2600);
      await app.pass(const Duration(minutes: 30));
      expect(app.location, '/rest');
      final saved = app.saved, then = app.now;
      await app.end();

      app = await TestApp.start(tester, game: saved, now: then.add(const Duration(minutes: 5)));
      expect(app.location, '/rest', reason: 'closing the app does not end the rest');
      await app.pass(const Duration(minutes: 24));
      expect(app.location, '/rest');
      await app.pass(const Duration(minutes: 2));
      expect(app.location, '/', reason: 'the hour is up');
      await app.end();
    });
  });

  group('the phone\'s back key', () {
    testWidgets('never closes the app; elsewhere it goes where the screen\'s own button goes', (tester) async {
      final closed = <String>[];
      tester.binding.defaultBinaryMessenger.setMockMethodCallHandler(SystemChannels.platform, (call) async {
        if (call.method == 'SystemNavigator.pop') closed.add('closed');
        return null;
      });
      addTearDown(() => tester.binding.defaultBinaryMessenger.setMockMethodCallHandler(SystemChannels.platform, null));
      Future<void> back(TestApp app) async {
        await tester.binding.handlePopRoute();
        await app.settle(600);
      }

      final app = await TestApp.start(tester);
      await back(app);
      expect(app.location, '/');
      await app.tapLabel(World.garden.zh, ms: 1200);
      await app.tapLabel(Mode.maze.zh, ms: 1500);
      expect(app.location, '/play/garden/maze');
      await back(app);
      expect(app.location, '/world/garden');
      await back(app);
      expect(app.location, '/');
      await app.tapLabel(Strings.stickers, ms: 800);
      await back(app);
      expect(app.location, '/');
      ParentPass.grant();
      app.go('/parent');
      await app.settle();
      await back(app);
      expect(app.location, '/');
      app.change((g) => g.rest(app.now));
      await app.settle(2600);
      expect(app.location, '/rest');
      await back(app);
      expect(app.location, '/rest');
      expect(closed, isEmpty);
      await app.end();
    });
  });

  group('parent pages', () {
    testWidgets('they close when the app goes to the background, and after five minutes without a touch', (tester) async {
      final app = await TestApp.start(tester);
      await app.tapLabel(Strings.parent, ms: 800);
      expect(find.byType(ParentGatePage), findsOneWidget);
      await app.hide();
      await app.show();
      await app.settle(1200);
      expect(find.byType(ParentGatePage), findsNothing, reason: 'the gate closed');
      expect(app.location, '/');

      await app.tapLabel(Strings.parent, ms: 800);
      await app.answerGate();
      expect(app.location, '/parent');
      await app.hide();
      await app.show();
      expect(app.location, '/', reason: 'a child picking the phone up again finds the home page');
      app.go('/parent');
      await app.settle();
      expect(app.location, '/', reason: 'the pass is used up: the gate again');

      ParentPass.grant();
      app.go('/parent');
      await app.settle();
      await tester.pump(const Duration(minutes: 4));
      await tester.tap(find.byKey(const ValueKey('level-big')));
      await tester.pump(const Duration(minutes: 4));
      expect(app.location, '/parent', reason: 'a touch keeps it open');
      await tester.pump(const Duration(minutes: 1, seconds: 5));
      await app.settle();
      expect(app.location, '/');

      await app.tapLabel(Strings.parent, ms: 800);
      await tester.pump(const Duration(minutes: 5, seconds: 5));
      await app.settle(1200);
      expect(find.byType(ParentGatePage), findsNothing);
      await app.end();
    });

    testWidgets('wrong answers make the gate wait 1, then 5 minutes, even after the app is closed', (tester) async {
      var app = await TestApp.start(tester);
      await app.tapLabel(Strings.parent, ms: 800);
      for (var i = 0; i < 3; i++) {
        await app.wrongGate();
      }
      expect(find.text(Strings.gateWait(const Duration(minutes: 1))), findsOneWidget);
      final saved = app.saved, then = app.now;
      await app.end();

      app = await TestApp.start(tester, game: saved, now: then.add(const Duration(seconds: 30)));
      await app.tapLabel(Strings.parent, ms: 800);
      expect(find.textContaining('請等'), findsOneWidget, reason: 'closing the app does not end the wait');
      app.now = app.now.add(const Duration(seconds: 31));
      await app.settle(1200);
      for (var i = 0; i < 3; i++) {
        await app.wrongGate();
      }
      expect(find.text(Strings.gateWait(const Duration(minutes: 5))), findsOneWidget, reason: 'longer the second time');
      app.now = app.now.subtract(const Duration(days: 1));
      await app.settle(1200);
      app.now = app.now.add(const Duration(minutes: 5));
      await app.settle(1200);
      expect(find.textContaining('請等'), findsNothing, reason: 'a clock moved back does not make it wait for ever');
      await app.answerGate();
      expect(app.location, '/parent');
      expect(app.game.gate.locks, 0, reason: 'a right answer starts again from one minute');
      await app.end();
    });
  });

  testWidgets('the child\'s palette button is for this time only: the parent\'s style stays', (tester) async {
    const parents = Game(settings: Settings(style: Style.b));
    var app = await TestApp.start(tester, game: parents);
    await app.tapLabel(World.garden.zh, ms: 1200);
    await app.tapLabel(Strings.switchStyle);
    expect(app.container.read(styleProvider), Style.c);
    expect(app.game.settings.style, Style.b);
    // Nothing saved at all is the parent's style too.
    final saved = app.store.saved == null ? parents : app.saved;
    await app.end();
    app = await TestApp.start(tester, game: saved);
    expect(app.container.read(styleProvider), Style.b, reason: 'opened again: the parent\'s style');
    await app.tapLabel(World.garden.zh, ms: 1200);
    await app.tapLabel(Strings.switchStyle);
    expect(app.container.read(styleProvider), Style.c);
    ParentPass.grant();
    app.go('/parent');
    await app.settle();
    await tester.tap(find.byKey(const ValueKey('style-a')));
    await app.settle();
    expect(app.container.read(styleProvider), Style.a, reason: 'the parent\'s pick shows straight away');
    await app.end();
  });

  testWidgets('土豆\'s own hint comes once, and never while the app is in the background', (tester) async {
    final app = await TestApp.start(tester, game: const Game(settings: Settings(level: Level.big)));
    int hints() => app.sounds.played.where((s) => s == 'hint').length;
    app.go('/play/garden/maze');
    await app.settle(1500);
    await app.hide();
    await app.wait(45);
    expect(hints(), 0);
    expect(app.voice.said, isNot(contains(Strings.hint)));
    await app.show();
    await app.wait(21);
    expect(hints(), 1);
    await app.wait(60);
    expect(hints(), 1, reason: 'not again and again');
    await app.end();
  });

  group('the voice', () {
    testWidgets('nothing is said in the background, and it stops there', (tester) async {
      final app = await TestApp.start(tester);
      app.go('/play/garden/maze');
      await app.settle(1500);
      final stops = app.voice.stops, said = app.voice.said.length;
      await app.hide();
      expect(app.voice.stops, greaterThan(stops));
      await app.wait(25);
      expect(app.voice.said, hasLength(said), reason: 'nothing is said out of sight');
      await app.show();
      await app.end();
    });

    testWidgets('leaving a screen stops its own line, never the next screen\'s', (tester) async {
      final app = await TestApp.start(tester);
      await app.tapLabel(World.garden.zh, ms: 1200);
      expect(app.voice.said.last, Strings.worldAsk(World.garden));
      expect(app.voice.stops, 0, reason: 'the world\'s first line is not cut off');
      await app.tapLabel(Mode.maze.zh, ms: 1500);
      expect(app.voice.said.last, Strings.ask(World.garden));
      await app.tapLabel(Strings.home, ms: 800);
      expect(app.location, '/world/garden');
      expect(app.voice.stops, 1, reason: 'the game\'s line does not go on');
      ParentPass.grant();
      app.go('/parent');
      await app.settle();
      expect(app.voice.stops, greaterThan(1), reason: 'nothing goes on over parent mode');
      await app.end();
    });

    test('only the newest line is said, and nothing after stop()', () async {
      TestWidgetsFlutterBinding.ensureInitialized();
      final spoken = <String>[];
      final setUp = Completer<void>();
      final messenger = TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger;
      messenger.setMockMethodCallHandler(const MethodChannel('flutter_tts'), (call) async {
        if (call.method == 'awaitSpeakCompletion') await setUp.future;
        if (call.method == 'speak') spoken.add('${call.arguments}');
        return 1;
      });
      addTearDown(() => messenger.setMockMethodCallHandler(const MethodChannel('flutter_tts'), null));
      final voice = SystemVoice();
      final first = voice.say(Strings.welcome);
      final second = voice.say(Strings.worldAsk(World.garden));
      setUp.complete();
      await Future.wait([first, second]);
      expect(spoken, [Strings.worldAsk(World.garden)], reason: 'the welcome, still setting up, does not cut in');
      final third = voice.say(Strings.fork);
      await voice.stop();
      await third;
      expect(spoken, hasLength(1));
    });
  });

  test('the sounds play on the media volume, not the ringer, and do not stop each other', () {
    for (final c in [SystemSounds.effectsContext, SystemSounds.musicContext]) {
      expect(c.android.usageType, isIn([AndroidUsageType.media, AndroidUsageType.game]));
      expect(c.android.audioFocus, AndroidAudioFocus.none);
      expect(c.iOS.category, AVAudioSessionCategory.ambient);
    }
    expect(SystemSounds.musicContext.android.contentType, AndroidContentType.music);
  });

  testWidgets('a hint asked for still works when 土豆\'s own hint is off', (tester) async {
    final app = await TestApp.start(tester, game: const Game(settings: Settings(hints: false)));
    app.go('/play/garden/maze');
    await app.settle(1500);
    await app.wait(25);
    expect(app.sounds.played, isNot(contains('hint')));
    await app.tapLabel(Strings.hintButton);
    expect(app.sounds.played.last, 'hint');
    await app.end();
  });

  group('fingers on the maze', () {
    PlayScreenState state(WidgetTester tester) => tester.state<PlayScreenState>(find.byType(PlayScreen));
    Offset centre(WidgetTester tester, Cell c) {
      final maze = state(tester).debugMaze;
      final rect = tester.getRect(find.byType(Board));
      final s = Board.cellIn(maze, rect.size);
      final topLeft = rect.center - Offset(maze.cols * s / 2, maze.rows * s / 2);
      return topLeft + Offset((c.c + 0.5) * s, (c.r + 0.5) * s);
    }

    testWidgets('only the first finger moves the hero; a second one changes nothing', (tester) async {
      final app = await TestApp.start(tester);
      app.go('/play/garden/maze');
      await app.settle(1500);
      final maze = state(tester).debugMaze, way = maze.solution;
      final first = await tester.startGesture(centre(tester, way[0]));
      await app.settle(100);
      // A thumb lands further along the road, then wiggles next to the hero.
      final thumb = await tester.startGesture(centre(tester, way[3]), pointer: 9);
      await app.settle(800);
      expect(state(tester).debugWalk.at, way[0], reason: 'the thumb does not pull the hero');
      for (final c in way.skip(1).take(2)) {
        await first.moveTo(centre(tester, c));
        await app.settle(300);
      }
      expect(state(tester).debugWalk.at, way[2]);
      await thumb.moveTo(centre(tester, way[1]));
      await app.settle(600);
      expect(state(tester).debugWalk.at, way[2], reason: 'the thumb does not pull it back');
      await thumb.up();
      await app.settle(100);
      await first.moveTo(centre(tester, way[3]));
      await app.settle(600);
      expect(state(tester).debugWalk.at, way[3], reason: 'the first finger still drags after the thumb lets go');
      await first.up();
      await app.end();
    });

    testWidgets('a finger the phone takes back is a cancel: the hero stops', (tester) async {
      final app = await TestApp.start(tester, game: const Game(settings: Settings(level: Level.small)));
      app.go('/play/garden/road');
      await app.settle(1500);
      final way = state(tester).debugMaze.solution;
      final g = await tester.startGesture(centre(tester, way[3]));
      await tester.pump(const Duration(milliseconds: 50));
      await g.cancel();
      await app.settle(1500);
      expect(way.indexOf(state(tester).debugWalk.at), lessThanOrEqualTo(1), reason: 'not on to where the finger was');
      await app.end();
    });

    testWidgets('a finger pressed a little ahead of the hero, then moved, drags it along', (tester) async {
      final app = await TestApp.start(tester, game: const Game(settings: Settings(level: Level.small)));
      app.go('/play/garden/road');
      await app.settle(1500);
      final way = state(tester).debugMaze.solution;
      final g = await tester.startGesture(centre(tester, way[2]));
      await app.settle(800);
      expect(state(tester).debugWalk.at, way[2], reason: 'the hero walks to the finger');
      for (final c in way.skip(3).take(3)) {
        await g.moveTo(centre(tester, c));
        await app.settle(400);
      }
      expect(state(tester).debugWalk.at, way[5], reason: 'and then follows it');
      await g.up();
      await app.end();
    });

    testWidgets('before the key, home and the gate say 「先拿鑰匙」 and the key lights up', (tester) async {
      final app = await TestApp.start(tester, game: const Game(settings: Settings(level: Level.big)));
      app.go('/play/garden/errand');
      await app.settle(1500);
      final maze = state(tester).debugMaze;
      for (final c in [maze.goal, maze.gate!]) {
        app.voice.said.clear();
        await tester.tapAt(centre(tester, c));
        await app.settle(400);
        expect(app.voice.said, [Strings.gateShut]);
        expect(find.byKey(ValueKey('hint-${maze.key}')), findsOneWidget);
        expect(state(tester).debugWalk.at, maze.start);
      }
      await app.end();
    });

    testWidgets('the long first line of an errand is not cut off by 「要走哪一邊呢？」', (tester) async {
      final voice = SlowVoice();
      final app = await TestApp.start(tester, game: const Game(settings: Settings(level: Level.big)), voice: voice);
      app.go('/play/garden/errand');
      await app.settle(1500);
      final maze = state(tester).debugMaze;
      expect(voice.said.last, Strings.errandAsk(World.garden));
      // Drag the hero a cell at a time to the first fork on the way to the
      // key, while the line is still being said.
      final way = maze.path(maze.start, maze.key!, blocked: {maze.gate!})!;
      final fork = way.indexWhere(maze.fork, 1);
      expect(fork, isPositive, reason: 'the way to the key passes a fork');
      final g = await tester.startGesture(centre(tester, way[0]));
      await app.settle(100);
      Future<void> stepTo(Cell c) async {
        await g.moveTo(centre(tester, c));
        await app.settle(400);
      }

      for (final c in way.sublist(1, fork + 1)) {
        await stepTo(c);
      }
      expect(state(tester).debugWalk.at, way[fork]);
      expect(voice.said, isNot(contains(Strings.fork)), reason: 'still saying what to do');
      voice.finish();
      await app.settle(200);
      await stepTo(way[fork - 1]);
      await stepTo(way[fork]);
      expect(voice.said, contains(Strings.fork), reason: 'once it has been said, forks are talked about again');
      await g.up();
      voice.finish();
      await app.settle(200);
      await app.end();
    });

    testWidgets('走迷宮\'s side roads come from 走迷宮 only, not from the other games', (tester) async {
      var g = const Game();
      for (var i = 0; i < 7; i++) {
        g = g.home(World.garden, Mode.road);
      }
      final app = await TestApp.start(tester, game: g);
      app.go('/play/garden/maze');
      await app.settle(1500);
      expect(state(tester).debugMaze.forks, 1, reason: 'the first 走迷宮 in the garden');
      await app.end();
    });
  });
}
