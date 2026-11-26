import 'dart:async';
import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../app/strings.dart';
import '../../app/theme.dart';
import '../../app/widgets.dart';
import '../../core/content.dart';
import '../../core/maze.dart';
import '../../core/providers.dart';
import '../../core/sounds.dart';
import 'board.dart';

/// One level in a world: bring the hero home through a maze made for the
/// child's age (docs/design.md). The finger drags the hero along the road,
/// or taps ahead and the hero walks there by itself (stopping at forks; a
/// finger still down there then drags it on); walls only go "boing". Only
/// the first finger counts. No clock, no score. 土豆 shows the way when
/// asked, or (with many hints) once after a while without getting anywhere
/// new; never while the app is in the background.
class PlayScreen extends ConsumerStatefulWidget {
  const PlayScreen({super.key, required this.world, required this.mode});

  final World world;
  final Mode mode;

  /// How long the hero takes for one cell.
  static const step = Duration(milliseconds: 170);

  /// With many hints, 土豆 shows the way after this long without a new cell
  /// (once: the next one comes after the next new cell).
  static const autoHint = Duration(seconds: 20);

  /// The longest the first line of a level is waited for before 土豆 talks
  /// about forks and dead ends.
  static const introAtMost = Duration(seconds: 12);

  @override
  ConsumerState<PlayScreen> createState() => PlayScreenState();
}

class PlayScreenState extends ConsumerState<PlayScreen> with HushOnLeave {
  late final Sounds _sounds;
  AppLifecycleListener? _life;

  /// The finger that moves the hero (only the first one down counts), and
  /// the cell under it.
  int? _finger;
  Cell? _fingerAt;

  /// 「先拿鑰匙」 was said for this touch (once, however the finger moves).
  var _shutSaid = false;

  /// The level's first line (what to do) has been said: until then 土豆
  /// says nothing about forks and dead ends, so it is not cut off.
  var _introDone = true;

  /// 土豆's own hint is still to come (it waits while the app is in the
  /// background).
  var _autoHintDue = false;
  late final math.Random _random;
  late Maze _maze;
  late Walk _walk;
  final _queue = <Cell>[];
  Timer? _stepTimer, _hintTimer, _hintClear;
  (Cell, bool)? _pending;
  var _dragging = false;
  Cell? _lastBump;
  var _bumps = 0;
  var _facingLeft = false;
  var _done = false;
  var _sticker = 1;
  var _round = 0;
  List<Cell> _hint = const [];
  final _saidForks = <Cell>{}, _saidDeadEnds = <Cell>{};
  String _line = '';

  World get _world => widget.world;
  Mode get _mode => widget.mode;

  /// The maze on the screen and the walk through it (tests play them).
  @visibleForTesting
  Maze get debugMaze => _maze;
  @visibleForTesting
  Walk get debugWalk => _walk;
  @visibleForTesting
  bool get debugDone => _done;

  @override
  void initState() {
    super.initState();
    _sounds = ref.read(soundsProvider);
    _random = ref.read(randomProvider);
    _sounds.hold(this, Music.of(_world));
    _life = AppLifecycleListener(
      onHide: () => _hintTimer?.cancel(),
      onShow: () {
        if (_autoHintDue) _startHintTimer();
      },
    );
    _deal();
    WidgetsBinding.instance.addPostFrameCallback((_) => _ask());
  }

  @override
  void dispose() {
    for (final t in [_stepTimer, _hintTimer, _hintClear]) {
      t?.cancel();
    }
    _life?.dispose();
    _sounds.release(this);
    super.dispose();
  }

  void _deal() {
    final g = ref.read(gameProvider);
    _maze = Maze.make(_mode, g.settings.level.index < _mode.from.index ? _mode.from : g.settings.level, g.walkedWith(_world, _mode), _random);
    _walk = Walk(_maze);
    _queue.clear();
    _stepTimer?.cancel();
    _pending = null;
    _dragging = false;
    _finger = null;
    _fingerAt = null;
    _lastBump = null;
    _bumps = 0;
    _facingLeft = false;
    _done = false;
    _hint = const [];
    _saidForks.clear();
    _saidDeadEnds.clear();
    _round++;
    _restartHintTimer();
  }

  String get _prompt => _mode == Mode.errand ? Strings.errandAsk(_world) : Strings.ask(_world);

  /// Says [zh] (and [en] if the parent turned English on); completes when
  /// it has been said.
  Future<void> _say(String zh, {String? en}) async {
    if (mounted) await speak(ref, zh, en: en);
  }

  Future<void> _setLine(String text, {String? en}) {
    if (!mounted) return Future.value();
    setState(() => _line = text);
    return _say(text, en: en);
  }

  /// What to do in this level (forks and dead ends wait until it has been
  /// said, at most [PlayScreen.introAtMost]).
  void _ask() {
    final round = _round;
    _introDone = false;
    void done() {
      if (mounted && round == _round) _introDone = true;
    }

    _setLine(_prompt, en: '${_world.heroEn}, ${_world.homeEn}').timeout(PlayScreen.introAtMost).then((_) => done(), onError: (_) => done());
  }

  // ---- the finger

  void _down(Cell c, int pointer) {
    if (_done || _finger != null) return;
    _finger = pointer;
    _fingerAt = c;
    _shutSaid = false;
    _dragging = c == _walk.at || c.distance(_walk.at) == 1;
    _target(c, tap: !_dragging);
  }

  void _move(Cell c, int pointer) {
    if (_done || pointer != _finger) return;
    _fingerAt = c;
    if (!_dragging) {
      // Tapped ahead of the hero and still down: once the hero is there
      // (or next to the finger), it follows the finger.
      if (_queue.isNotEmpty || (c != _walk.at && c.distance(_walk.at) > 1)) return;
      _dragging = true;
    }
    _target(c, tap: false);
  }

  void _up(int pointer, {bool cancel = false}) {
    if (pointer != _finger) return;
    _finger = null;
    _fingerAt = null;
    _dragging = false;
    _lastBump = null;
    if (cancel) {
      // Not a touch after all (the phone took it back): the hero stops.
      _pending = null;
      _queue.clear();
    }
  }

  void _target(Cell c, {required bool tap}) {
    if (_queue.isNotEmpty) {
      _pending = (c, tap);
      return;
    }
    final steps = _walk.plan(c, tap: tap);
    if (steps.isEmpty) {
      if (_walk.shutOut(c)) {
        // Home, the gate or beyond it, before the key: say so, and the key
        // lights up.
        if (!_shutSaid) {
          _shutSaid = true;
          _sounds.play('bump');
          _setLine(Strings.gateShut);
          _showKey();
        }
        return;
      }
      if (_walk.bumps(c) && c != _lastBump) {
        _lastBump = c;
        _sounds.play('bump');
        if (c == _maze.gate && !_walk.hasKey) {
          _setLine(Strings.gateShut);
        } else if (++_bumps % 4 == 3) {
          _setLine(Strings.followRoad);
        }
      }
      return;
    }
    _lastBump = null;
    _queue.addAll(steps);
    _advance();
  }

  void _advance() {
    _stepTimer?.cancel();
    if (!mounted || _done) return;
    if (_queue.isEmpty) {
      final p = _pending;
      _pending = null;
      if (p != null && (p.$2 || _dragging)) {
        _target(p.$1, tap: p.$2);
      } else if (_finger != null && !_dragging) {
        // There, and the finger is still down: it drags the hero on.
        _dragging = true;
        final at = _fingerAt;
        if (at != null && at != _walk.at) _target(at, tap: false);
      }
      return;
    }
    final c = _queue.removeAt(0);
    if (c.c != _walk.at.c) _facingLeft = c.c < _walk.at.c;
    final events = _walk.step(c);
    _sounds.play('step_${_world.name}');
    setState(() => _hint = const []);
    _restartHintTimer();
    if (events.contains(Event.star)) _sounds.play('star');
    if (events.contains(Event.key)) {
      _sounds.play('key');
      _sounds.play('gate');
      _setLine(Strings.gotKey);
    }
    if (events.contains(Event.home)) {
      _arrive();
      return;
    }
    // Not over the first line of the level (it would be cut off).
    if (events.contains(Event.fork) && _mode != Mode.road && _queue.isEmpty && _introDone && _saidForks.add(c)) {
      _sounds.play('fork');
      _setLine(Strings.fork);
    }
    if (events.contains(Event.deadEnd) && _introDone && _saidDeadEnds.add(c)) _setLine(Strings.deadEnd);
    _stepTimer = Timer(PlayScreen.step, _advance);
  }

  void _arrive() {
    _queue.clear();
    _autoHintDue = false;
    _hintTimer?.cancel();
    final notifier = ref.read(gameProvider.notifier);
    notifier.change((g) => g.home(_world, _mode));
    final walked = ref.read(gameProvider).walkedIn(_world);
    _sounds.play('arrive');
    _sounds.play('cheer');
    final praise = Strings.right[_random.nextInt(Strings.right.length)];
    setState(() {
      _done = true;
      _sticker = (walked - 1) % World.levels + 1;
      _line = Strings.arrived;
    });
    Future<void>.delayed(const Duration(milliseconds: 900), () {
      if (mounted && _done) _sounds.play('sticker');
    });
    _say('$praise${Strings.arrived}${Strings.gotSticker}');
  }

  // ---- hints

  /// A new cell or a new level: 土豆's own hint comes [PlayScreen.autoHint]
  /// later if the hero gets nowhere new (with many hints).
  void _restartHintTimer() {
    _autoHintDue = !_done && ref.read(gameProvider).settings.hints;
    _startHintTimer();
  }

  void _startHintTimer() {
    _hintTimer?.cancel();
    if (!_autoHintDue) return;
    final st = WidgetsBinding.instance.lifecycleState;
    // In the background it waits until the app is back.
    if (st == AppLifecycleState.hidden || st == AppLifecycleState.paused || st == AppLifecycleState.detached) return;
    _hintTimer = Timer(PlayScreen.autoHint, _giveHint);
  }

  void _giveHint() {
    if (!mounted || _done) return;
    // Once: 土豆 does not say it again and again (the next one by himself
    // comes after the next new cell).
    _autoHintDue = false;
    _hintTimer?.cancel();
    _sounds.play('hint');
    _glow(_walk.hint());
    _setLine(Strings.hint);
  }

  /// Lights up [cells] for a few seconds.
  void _glow(List<Cell> cells) {
    setState(() => _hint = cells);
    _hintClear?.cancel();
    _hintClear = Timer(const Duration(seconds: 5), () {
      if (mounted) setState(() => _hint = const []);
    });
  }

  void _showKey() {
    final key = _maze.key;
    if (key != null) _glow([key]);
  }

  void _next() {
    _sounds.play('next');
    setState(_deal);
    _ask();
  }

  void _toMap() => context.canPop() ? context.pop() : context.go('/');

  @override
  Widget build(BuildContext context) {
    final style = ref.watch(styleProvider);
    final color = worldColor(_world);
    return BackKey(
      onBack: _toMap,
      child: Scaffold(
      body: Sky(
        top: Color.lerp(color, Colors.white, 0.82)!,
        bottom: Felt.cream,
        child: Stack(children: [
          SafeArea(
            child: Column(children: [
              Padding(
                padding: const EdgeInsets.fromLTRB(12, 8, 12, 0),
                child: Row(children: [
                  RoundButton(label: Strings.home, icon: Icons.home_rounded, onTap: _toMap, size: 50),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Align(
                      alignment: Alignment.centerLeft,
                      child: _mode == Mode.errand ? _Errand(world: _world, style: style, hasKey: _walk.hasKey) : Pill(text: _world.zh, color: color),
                    ),
                  ),
                  const SizedBox(width: 8),
                  StyleSwitch(size: 50, onSwitched: (s) => _say(Strings.styleNow(s))),
                ]),
              ),
              Padding(
                padding: const EdgeInsets.fromLTRB(12, 10, 12, 4),
                child: SpeakBubble(text: _line.isEmpty ? _prompt : _line, onTap: () => _say(_line.isEmpty ? _prompt : _line), color: color),
              ),
              Expanded(
                child: Padding(
                  padding: const EdgeInsets.fromLTRB(10, 6, 10, 0),
                  child: Board(
                    key: ValueKey('board-$_round'),
                    maze: _maze,
                    walk: _walk,
                    world: _world,
                    style: style,
                    hint: _hint,
                    facingLeft: _facingLeft,
                    step: PlayScreen.step,
                    onDown: _down,
                    onMove: _move,
                    onUp: _up,
                  ),
                ),
              ),
              SizedBox(
                height: 92,
                child: Row(crossAxisAlignment: CrossAxisAlignment.end, children: [
                  const SizedBox(width: 8),
                  Semantics(
                    container: true,
                    button: true,
                    label: '土豆',
                    excludeSemantics: true,
                    onTap: _ask,
                    child: GestureDetector(
                      behavior: HitTestBehavior.opaque,
                      onTap: () {
                        _sounds.play('giggle');
                        _ask();
                      },
                      child: SizedBox.square(dimension: 88, child: Tudou(pose: _hint.isNotEmpty ? 'point' : (_done ? 'cheer' : 'peek'), style: style)),
                    ),
                  ),
                  const Spacer(),
                  Padding(
                    padding: const EdgeInsets.fromLTRB(8, 0, 14, 12),
                    child: RoundButton(label: Strings.hintButton, icon: Icons.search_rounded, size: 58, sound: null, onTap: _done ? null : _giveHint),
                  ),
                ]),
              ),
            ]),
          ),
          if (_done) Arrived(world: _world, style: style, sticker: _sticker, onNext: _next, onMap: _toMap),
        ]),
      ),
      ),
    );
  }
}

/// An errand's three steps: the key, the gate, home (each ticked when done).
class _Errand extends StatelessWidget {
  const _Errand({required this.world, required this.style, required this.hasKey});

  final World world;
  final Style style;
  final bool hasKey;

  @override
  Widget build(BuildContext context) {
    Widget part(String art, {required bool done, required bool now}) => Container(
          width: 44,
          height: 44,
          padding: const EdgeInsets.all(5),
          decoration: BoxDecoration(
            color: Colors.white,
            shape: BoxShape.circle,
            border: Border.all(color: now ? Felt.glow : Colors.transparent, width: 3),
          ),
          child: Stack(clipBehavior: Clip.none, children: [
            Positioned.fill(child: Art(artPath(style, world, art))),
            if (done) const Positioned(right: -8, top: -8, child: Icon(Icons.check_circle_rounded, color: Felt.green, size: 20)),
          ]),
        );
    const arrow = Padding(padding: EdgeInsets.symmetric(horizontal: 3), child: Icon(Icons.arrow_forward_rounded, size: 18, color: Felt.inkSoft));
    return Semantics(
      label: hasKey ? '拿到鑰匙了，回家' : '先拿鑰匙',
      child: Row(mainAxisSize: MainAxisSize.min, children: [
        part('key', done: hasKey, now: !hasKey),
        arrow,
        part('gate', done: hasKey, now: false),
        arrow,
        part('home', done: false, now: hasKey),
      ]),
    );
  }
}

/// Home at last: the hero with its family, a sticker flying into the book,
/// next level or back to the map.
class Arrived extends StatefulWidget {
  const Arrived({super.key, required this.world, required this.style, required this.sticker, required this.onNext, required this.onMap});

  final World world;
  final Style style;

  /// The sticker earned, 1–10.
  final int sticker;
  final VoidCallback onNext;
  final VoidCallback onMap;

  @override
  State<Arrived> createState() => _ArrivedState();
}

class _ArrivedState extends State<Arrived> with SingleTickerProviderStateMixin {
  late final _c = AnimationController(vsync: this, duration: const Duration(milliseconds: 1800))..forward();

  @override
  void dispose() {
    _c.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => Positioned.fill(
        child: Container(
          decoration: const BoxDecoration(gradient: LinearGradient(begin: Alignment.topCenter, end: Alignment.bottomCenter, colors: [Color(0xFFFFF4E0), Color(0xFFFFE8EC)])),
          child: SafeArea(
            child: LayoutBuilder(builder: (context, box) {
              final pic = math.min(box.maxWidth * 0.78, box.maxHeight * 0.42);
              final sticker = math.min(120.0, box.maxWidth * 0.3);
              return Center(
                child: SingleChildScrollView(
                  child: Column(mainAxisSize: MainAxisSize.min, children: [
                    ScaleTransition(
                      scale: CurvedAnimation(parent: _c, curve: const Interval(0, 0.4, curve: Curves.elasticOut)),
                      child: const Text(Strings.arrived, style: TextStyle(fontSize: 40, fontWeight: FontWeight.w700, color: Felt.coral)),
                    ),
                    const SizedBox(height: 8),
                    SizedBox.square(dimension: pic, child: Art(artPath(widget.style, widget.world, 'family'))),
                    const SizedBox(height: 4),
                    AnimatedBuilder(
                      animation: _c,
                      builder: (_, child) {
                        final t = Curves.easeOutBack.transform(((_c.value - 0.35) / 0.65).clamp(0.0, 1.0));
                        return Opacity(opacity: t.clamp(0.0, 1.0), child: Transform.scale(scale: 0.4 + 0.6 * t, child: child));
                      },
                      child: Row(mainAxisSize: MainAxisSize.min, children: [
                        SizedBox.square(dimension: sticker, child: Art(artPath(widget.style, widget.world, 'sticker_${widget.sticker.toString().padLeft(2, '0')}'))),
                        const SizedBox(width: 10),
                        const Text(Strings.gotSticker, style: TextStyle(fontSize: 20, fontWeight: FontWeight.w700)),
                      ]),
                    ),
                    const SizedBox(height: 18),
                    WideButton(label: Strings.next, icon: Icons.arrow_forward_rounded, onTap: widget.onNext),
                    const SizedBox(height: 12),
                    WideButton(label: Strings.toMap, icon: Icons.map_rounded, color: Colors.white, onTap: widget.onMap),
                  ]),
                ),
              );
            }),
          ),
        ),
      );
}
