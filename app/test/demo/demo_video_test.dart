// Records a demo video of 迷宮小冒險 being played: a scripted child (a
// white dot where the finger is) with a caption under the phone screen; the
// music and sounds the app asked for are written down and mixed in
// afterwards by tools/demo_audio.py.
//
//   flutter test test/demo/demo_video_test.dart --dart-define=DEMO=true
//   python3 ../tools/demo_audio.py
//
// Needs ffmpeg; writes build/demo/demo.mp4, chapters.txt and sounds.txt.
// Skipped in normal test runs.
import 'dart:io';
import 'dart:math' as math;
import 'dart:ui' as ui;

import 'package:flutter/material.dart';
import 'package:flutter/rendering.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:maze_adventure/app/app.dart';
import 'package:maze_adventure/app/strings.dart';
import 'package:maze_adventure/core/content.dart';
import 'package:maze_adventure/core/providers.dart';
import 'package:maze_adventure/core/maze.dart';
import 'package:maze_adventure/core/sounds.dart';
import 'package:maze_adventure/core/store.dart';
import 'package:maze_adventure/core/voice.dart';
import 'package:maze_adventure/core/game.dart';
import 'package:maze_adventure/features/play/board.dart';
import 'package:maze_adventure/features/play/play_screen.dart';

import '../helpers.dart' show loadFonts;

const _phone = Size(390, 844);
const _captionHeight = 84.0;
const _fps = 10;
const _demo = bool.fromEnvironment('DEMO');

/// The music and the sounds asked for, with the frame they were asked at.
class _Recording implements Sounds {
  _Recording(this.frame);

  final int Function() frame;
  final lines = <String>[];
  final _holders = MusicHolders();
  Music? _playing;

  @override
  set music(bool on) {}

  @override
  set effects(bool on) {}

  @override
  void play(String sfx) => lines.add('${frame()} sfx $sfx');

  @override
  void hold(Object owner, Music? music) {
    _holders.hold(owner, music);
    _changed();
  }

  @override
  void release(Object owner) {
    _holders.release(owner);
    _changed();
  }

  void _changed() {
    final now = _holders.current;
    if (now == _playing) return;
    _playing = now;
    lines.add('${frame()} music ${now?.file ?? '-'}');
  }
}

void main() {
  testWidgets('demo video', skip: !_demo, (tester) async {
    await tester.runAsync(loadFonts);
    tester.view.physicalSize = Size(_phone.width * 3, (_phone.height + _captionHeight) * 3);
    tester.view.devicePixelRatio = 3;
    addTearDown(tester.view.reset);

    var frameCount = 0;
    var now = DateTime(2026, 11, 6, 10);
    final track = _Recording(() => frameCount);
    final finger = ValueNotifier<Offset?>(null);
    final caption = ValueNotifier<String>('');
    final key = GlobalKey();
    final store = MemoryStore();
    await tester.pumpWidget(RepaintBoundary(
      key: key,
      child: Directionality(
        textDirection: TextDirection.ltr,
        child: Column(children: [
          SizedBox.fromSize(
            size: _phone,
            child: MediaQuery(
              data: const MediaQueryData(size: _phone, devicePixelRatio: 3, padding: EdgeInsets.only(top: 24)),
              child: Stack(children: [
                ProviderScope(
                  overrides: [
                    storeProvider.overrideWithValue(store),
                    savedGameProvider.overrideWithValue(const Game(settings: Settings(level: Level.small))),
                    soundsProvider.overrideWithValue(track),
                    voiceProvider.overrideWithValue(const SilentVoice()),
                    randomProvider.overrideWithValue(math.Random(8)),
                    clockProvider.overrideWithValue(() => now),
                  ],
                  child: const MazeApp(),
                ),
                IgnorePointer(child: ValueListenableBuilder(valueListenable: finger, builder: (_, at, _) => _Finger(at))),
              ]),
            ),
          ),
          SizedBox(
            width: _phone.width,
            height: _captionHeight,
            child: ColoredBox(
              color: const Color(0xFF5DB85A),
              child: Center(
                child: ValueListenableBuilder(
                  valueListenable: caption,
                  builder: (_, text, _) => Text(text,
                      textAlign: TextAlign.center, style: const TextStyle(fontFamily: 'Huninn', color: Colors.white, fontSize: 17, height: 1.35)),
                ),
              ),
            ),
          ),
        ]),
      ),
    ));

    final rec = (await tester.runAsync(() => _Recorder.start(key)))!;
    final marks = <String>[];
    void mark(String name) => marks.add('$name $frameCount');
    Future<void> frames(int n) async {
      for (var i = 0; i < n; i++) {
        frameCount++;
        await tester.runAsync(() async {
          await rec.capture();
          await Future<void>.delayed(const Duration(milliseconds: 15));
        });
        await tester.pump(const Duration(milliseconds: 1000 ~/ _fps));
      }
    }

    Future<void> seconds(double s) => frames((s * _fps).round());
    Future<void> touch(Offset at) async {
      finger.value = at;
      await frames(2);
      await tester.tapAt(at);
      await frames(2);
      finger.value = null;
    }

    Offset at(String l) => tester.getCenter(find.bySemanticsLabel(l).last);
    Future<void> label(String l) => touch(at(l));
    PlayScreenState play() => tester.state<PlayScreenState>(find.byType(PlayScreen));
    Offset centre(Cell c) {
      final maze = play().debugMaze;
      final rect = tester.getRect(find.byType(Board));
      final s = Board.cellIn(maze, rect.size);
      final topLeft = rect.center - Offset(maze.cols * s / 2, maze.rows * s / 2);
      return topLeft + Offset((c.c + 0.5) * s, (c.r + 0.5) * s);
    }

    Future<void> drag(List<Cell> cells) async {
      finger.value = centre(cells.first);
      final g = await tester.startGesture(centre(cells.first));
      await frames(2);
      for (final c in cells.skip(1)) {
        final from = finger.value!, to = centre(c);
        for (var i = 1; i <= 3; i++) {
          final p = Offset.lerp(from, to, i / 3)!;
          await g.moveTo(p);
          finger.value = p;
          await frames(1);
        }
      }
      await g.up();
      finger.value = null;
      await frames(2);
    }

    Future<void> walkHome() async {
      for (var i = 0; i < 60 && !play().debugDone; i++) {
        final ahead = play().debugWalk.hint(3);
        if (ahead.isEmpty) break;
        await touch(centre(ahead.last));
        await seconds(0.9);
      }
    }

    void level(Level l) {
      final c = ProviderScope.containerOf(tester.element(find.byType(MazeApp)));
      c.read(gameProvider.notifier).settings((s) => s.copyWith(level: l));
    }

    // Home.
    mark('home');
    caption.value = '迷宮小冒險：跟著小鼴鼠土豆\n把小蜜蜂、小魚、小公車帶回家！';
    await seconds(3.5);
    caption.value = '六個世界：花園、地底隧道、海底\n城市、雪地、太空';
    await seconds(2.5);

    // 2～3: the road.
    mark('road');
    caption.value = '2～3 歲：一條彎彎的寬路，沒有岔路\n手指拖著小蜜蜂走';
    await label(World.garden.zh);
    await seconds(2);
    final road = play().debugMaze.solution;
    await drag(road.take(5).toList());
    await seconds(0.8);
    caption.value = '不會拖也沒關係：點路上的地方\n小蜜蜂自己走過去';
    await touch(centre(road.last));
    await seconds(road.length * 0.2 + 1);
    mark('home_at_last');
    caption.value = '到家了！每走完一關得一張貼紙';
    await seconds(4);
    await label(Strings.toMap);
    await seconds(1.2);

    // 3～4: a maze with forks.
    mark('maze');
    level(Level.mid);
    caption.value = '3～4 歲：有幾個很短的岔路\n死路一眼就看得到';
    await label(World.sea.zh);
    await seconds(1.5);
    await label(Mode.maze.zh);
    await seconds(2);
    final maze = play().debugMaze;
    final wall = [for (final d in Dir.values) if (maze.inside(maze.start.go(d)) && !maze.joins(maze.start, d)) maze.start.go(d)];
    if (wall.isNotEmpty) {
      caption.value = '撞到牆只會輕輕「咚」一聲\n沒有失敗、不用重來';
      await touch(centre(wall.first));
      await seconds(2);
    }
    caption.value = '卡住了？點放大鏡，土豆把路點亮';
    await label(Strings.hintButton);
    await seconds(2.5);
    caption.value = '走到岔路口會停下來，讓小朋友自己選';
    await walkHome();
    await seconds(3);
    await label(Strings.toMap);
    await seconds(1);

    // Three styles.
    mark('style');
    await label(Mode.maze.zh);
    await seconds(1.5);
    caption.value = '三種畫風隨時換，迷宮完全一樣\n像素小遊戲風';
    await label(Strings.switchStyle);
    await seconds(2.4);
    caption.value = '果凍糖果風';
    await label(Strings.switchStyle);
    await seconds(2.4);
    caption.value = '羊毛氈布書風（預設）';
    await label(Strings.switchStyle);
    await seconds(1.6);
    await label(Strings.home);
    await seconds(1);
    await label(Strings.home);
    await seconds(1);

    // 4～5: an errand.
    mark('errand');
    level(Level.big);
    caption.value = '4～5 歲：小迷宮，先拿鑰匙\n打開門，再帶小公車回總站';
    await label(World.city.zh);
    await seconds(1.5);
    await label(Mode.errand.zh);
    await seconds(2);
    await walkHome();
    await seconds(3);
    await label(Strings.toMap);
    await seconds(1);
    await label(Strings.home);
    await seconds(1);

    // The sticker book.
    mark('stickers');
    caption.value = '貼紙冊：每個世界 10 張貼紙';
    await label(Strings.stickers);
    await seconds(3);
    await label(Strings.home);
    await seconds(1);

    // Time for a rest.
    mark('rest');
    now = now.add(const Duration(minutes: 15, seconds: 1));
    caption.value = '家長設定的時間到了（預設 15 分鐘）\n土豆睡覺，眼睛也休息一下';
    await seconds(5.5);

    // Parent mode.
    mark('parent');
    caption.value = '家長答對題目，才能再玩或進家長模式';
    const digits = {'零': 0, '一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9};
    Future<void> gate() async {
      final parts = (find.textContaining('加').evaluate().first.widget as Text).data!.split(' ');
      for (final d in '${digits[parts[0]]! + digits[parts[2]]!}'.split('')) {
        await touch(tester.getCenter(find.byKey(ValueKey('gate-key-$d'))));
        await frames(3);
      }
    }

    await label(Strings.parent);
    await seconds(1.2);
    await gate();
    await seconds(1.5);
    await label(Strings.parent);
    await seconds(1);
    await gate();
    await seconds(1);
    caption.value = '家長模式：年齡（三個難度）、每次玩多久\n一開始的畫風、提示多或少、聲音、英文';
    await seconds(3);
    await tester.drag(find.byType(ListView), const Offset(0, -900));
    await seconds(3);
    caption.value = '';
    mark('end');
    await seconds(0.5);

    await tester.runAsync(() async {
      await rec.finish();
      File('build/demo/chapters.txt').writeAsStringSync('${marks.join('\n')}\n');
      File('build/demo/sounds.txt').writeAsStringSync('fps $_fps\nframes $frameCount\n${track.lines.join('\n')}\n');
    });
    await tester.pumpWidget(const SizedBox());
    await tester.pump(const Duration(milliseconds: 100));
  }, timeout: const Timeout(Duration(minutes: 40)));
}

class _Finger extends StatelessWidget {
  const _Finger(this.at);

  final Offset? at;

  @override
  Widget build(BuildContext context) {
    final p = at;
    if (p == null) return const SizedBox.expand();
    return Stack(children: [
      Positioned(
        left: p.dx - 22,
        top: p.dy - 22,
        child: Container(
          width: 44,
          height: 44,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            color: Colors.white.withValues(alpha: 0.55),
            border: Border.all(color: const Color(0xFF4A3B32).withValues(alpha: 0.5), width: 3),
          ),
        ),
      ),
    ]);
  }
}

/// Streams frames of [key]'s boundary into ffmpeg.
class _Recorder {
  _Recorder(this._key, this._ffmpeg);

  final GlobalKey _key;
  final Process _ffmpeg;

  static Future<_Recorder> start(GlobalKey key) async {
    Directory('build/demo').createSync(recursive: true);
    final size = Size(_phone.width * 2, (_phone.height + _captionHeight) * 2);
    final ffmpeg = await Process.start('ffmpeg', [
      '-y', '-loglevel', 'error',
      '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', '${size.width.toInt()}x${size.height.toInt()}', '-r', '$_fps', '-i', '-',
      '-vf', 'fps=30', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '24', '-movflags', '+faststart', 'build/demo/demo_silent.mp4',
    ]);
    ffmpeg.stderr.listen(stderr.add);
    return _Recorder(key, ffmpeg);
  }

  Future<void> capture() async {
    final boundary = _key.currentContext!.findRenderObject()! as RenderRepaintBoundary;
    final image = await boundary.toImage(pixelRatio: 2);
    final bytes = await image.toByteData(format: ui.ImageByteFormat.rawRgba);
    image.dispose();
    _ffmpeg.stdin.add(bytes!.buffer.asUint8List());
    await _ffmpeg.stdin.flush();
  }

  Future<void> finish() async {
    await _ffmpeg.stdin.flush();
    await _ffmpeg.stdin.close();
    final code = await _ffmpeg.exitCode;
    if (code != 0) throw StateError('ffmpeg failed ($code)');
  }
}
