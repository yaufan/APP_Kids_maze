import 'dart:math' as math;

import 'package:flutter/material.dart';

import '../../app/theme.dart';
import '../../app/widgets.dart';
import '../../core/content.dart';
import '../../core/maze.dart';

/// The maze, drawn from its pieces (docs/art.md): the ground, scenery in
/// the empty cells, a road tile in each road cell, the trail of footprints,
/// stars, the key and gate, home, and the hero. A finger on it reports the
/// cell under it.
class Board extends StatelessWidget {
  const Board({
    super.key,
    required this.maze,
    required this.walk,
    required this.world,
    required this.style,
    this.hint = const [],
    this.facingLeft = false,
    this.onDown,
    this.onMove,
    this.onUp,
    this.step = const Duration(milliseconds: 170),
  });

  final Maze maze;
  final Walk walk;
  final World world;
  final Style style;

  /// Cells to light up (a hint).
  final List<Cell> hint;
  final bool facingLeft;
  final void Function(Cell c)? onDown;
  final void Function(Cell c)? onMove;
  final VoidCallback? onUp;

  /// How long the hero takes for one cell.
  final Duration step;

  /// The size of a cell in a [box].
  static double cellIn(Maze m, Size box) => math.min(box.width / m.cols, box.height / m.rows);

  @override
  Widget build(BuildContext context) => LayoutBuilder(builder: (_, box) {
        final s = cellIn(maze, box.biggest);
        final w = s * maze.cols, h = s * maze.rows;
        Rect rect(Cell c, [double scale = 1]) {
          final size = s * scale;
          return Rect.fromLTWH(c.c * s + (s - size) / 2, c.r * s + (s - size) / 2, size, size);
        }

        Widget at(Cell c, Widget child, {double scale = 1, Key? key}) => Positioned.fromRect(key: key, rect: rect(c, scale), child: child);
        Cell? cellAt(Offset p) {
          final c = Cell((p.dx / s).floor(), (p.dy / s).floor());
          return maze.inside(c) ? c : null;
        }

        final gate = maze.gate;
        final gateOpen = walk.hasKey;
        // The gate stands across the road from it to home.
        final gateUpright = gate != null && (gate.toward(maze.goal) == Dir.left || gate.toward(maze.goal) == Dir.right);
        final board = SizedBox(
          width: w,
          height: h,
          child: Stack(clipBehavior: Clip.none, children: [
            Positioned.fill(
              child: ClipRRect(borderRadius: BorderRadius.circular(s * 0.25), child: Art(artPath(style, world, 'bg'), fit: BoxFit.cover)),
            ),
            for (final MapEntry(key: c, value: n) in maze.deco.entries) at(c, Art(artPath(style, world, 'deco_$n'), fit: BoxFit.contain), scale: 0.9),
            for (final MapEntry(key: c, value: bits) in maze.open.entries) at(c, Art(artPath(style, world, 'tile_$bits'), fit: BoxFit.fill)),
            Positioned.fill(child: IgnorePointer(child: CustomPaint(painter: _Trail(walk.trail, s, worldColor(world))))),
            for (final c in hint) at(c, const _Glow(), scale: 0.9, key: ValueKey('hint-$c')),
            for (final c in maze.stars)
              if (!walk.stars.contains(c)) at(c, Bob(phase: (c.c + c.r) * 0.17, amount: s * 0.04, child: Art(artPath(style, world, 'star'))), scale: 0.5, key: ValueKey('star-$c')),
            if (maze.key != null && !walk.hasKey) at(maze.key!, Bob(amount: s * 0.05, child: Art(artPath(style, world, 'key'))), scale: 0.6, key: const ValueKey('key')),
            if (gate != null && !gateOpen) at(gate, gateUpright ? Art(artPath(style, world, 'gate')) : RotatedBox(quarterTurns: 1, child: Art(artPath(style, world, 'gate'))), key: const ValueKey('gate')),
            at(maze.goal, Art(artPath(style, world, 'home')), scale: 1.15, key: const ValueKey('home')),
            AnimatedPositioned(
              key: const ValueKey('hero'),
              duration: step,
              curve: Curves.linear,
              left: walk.at.c * s + s * 0.08,
              top: walk.at.r * s + s * 0.04,
              width: s * 0.84,
              height: s * 0.84,
              child: IgnorePointer(
                child: Bob(
                  amount: s * 0.03,
                  child: Transform.flip(flipX: facingLeft, child: Art(artPath(style, world, 'hero'))),
                ),
              ),
            ),
          ]),
        );
        return Center(
          child: Listener(
            behavior: HitTestBehavior.opaque,
            onPointerDown: (e) {
              final c = cellAt(e.localPosition);
              if (c != null) onDown?.call(c);
            },
            onPointerMove: (e) {
              final c = cellAt(e.localPosition);
              if (c != null) onMove?.call(c);
            },
            onPointerUp: (_) => onUp?.call(),
            onPointerCancel: (_) => onUp?.call(),
            child: board,
          ),
        );
      });
}

/// Footprints where the hero has walked.
class _Trail extends CustomPainter {
  _Trail(this.trail, this.s, this.color) : count = trail.length;

  final List<Cell> trail;
  final double s;
  final Color color;
  final int count;

  @override
  void paint(Canvas canvas, Size size) {
    final dot = Paint()..color = Colors.white.withValues(alpha: 0.85);
    final ring = Paint()
      ..color = color.withValues(alpha: 0.7)
      ..style = PaintingStyle.stroke
      ..strokeWidth = s * 0.025;
    Offset mid(Cell c) => Offset((c.c + 0.5) * s, (c.r + 0.5) * s);
    for (var i = 1; i < trail.length; i++) {
      final a = mid(trail[i - 1]), b = mid(trail[i]);
      for (final t in [0.0, 0.5]) {
        final p = Offset.lerp(a, b, t)!;
        canvas.drawCircle(p, s * 0.06, dot);
        canvas.drawCircle(p, s * 0.06, ring);
      }
    }
  }

  @override
  bool shouldRepaint(_Trail old) => old.count != count || old.s != s || old.color != color;
}

/// A soft yellow glow that pulses: 土豆's hint.
class _Glow extends StatefulWidget {
  const _Glow();

  @override
  State<_Glow> createState() => _GlowState();
}

class _GlowState extends State<_Glow> with SingleTickerProviderStateMixin {
  late final _c = AnimationController(vsync: this, duration: const Duration(milliseconds: 800))..repeat(reverse: true);

  @override
  void dispose() {
    _c.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => IgnorePointer(
        child: AnimatedBuilder(
          animation: _c,
          builder: (_, _) => DecoratedBox(
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              gradient: RadialGradient(colors: [
                Felt.glow.withValues(alpha: 0.75),
                Felt.glow.withValues(alpha: 0.35 + 0.25 * _c.value),
                Felt.glow.withValues(alpha: 0),
              ], stops: const [0.2, 0.6, 1]),
            ),
          ),
        ),
      );
}
