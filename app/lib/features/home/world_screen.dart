import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../app/strings.dart';
import '../../app/theme.dart';
import '../../app/widgets.dart';
import '../../core/content.dart';
import '../../core/providers.dart';
import '../../core/sounds.dart';

/// A world: its picture and the games that suit the child's age (two for
/// 3～4, three for 4～5), each a big button.
class WorldScreen extends ConsumerStatefulWidget {
  const WorldScreen({super.key, required this.world});

  final World world;

  @override
  ConsumerState<WorldScreen> createState() => _WorldScreenState();
}

class _WorldScreenState extends ConsumerState<WorldScreen> {
  late final Sounds _sounds;

  @override
  void initState() {
    super.initState();
    _sounds = ref.read(soundsProvider);
    _sounds.hold(this, Music.of(widget.world));
    WidgetsBinding.instance.addPostFrameCallback((_) => _say(Strings.worldAsk(widget.world)));
  }

  @override
  void dispose() {
    _sounds.release(this);
    super.dispose();
  }

  void _say(String zh) {
    if (mounted && ref.read(gameProvider).settings.voice) ref.read(voiceProvider).say(zh);
  }

  void _play(Mode m) {
    _say(m.zh);
    context.push('/play/${widget.world.name}/${m.name}');
  }

  @override
  Widget build(BuildContext context) {
    final g = ref.watch(gameProvider);
    final w = widget.world;
    return Scaffold(
      body: Sky(
        top: Color.lerp(worldColor(w), Colors.white, 0.82)!,
        bottom: Felt.cream,
        child: SafeArea(
          child: Column(children: [
            Padding(
              padding: const EdgeInsets.fromLTRB(12, 8, 12, 0),
              child: Row(children: [
                RoundButton(label: Strings.home, icon: Icons.home_rounded, size: 50, onTap: () => context.canPop() ? context.pop() : context.go('/')),
                const SizedBox(width: 10),
                Pill(text: w.zh, color: worldColor(w)),
                const SizedBox(width: 8),
                Stars(count: g.starsOf(w), size: 22),
                const Spacer(),
                const StyleSwitch(size: 50),
              ]),
            ),
            Padding(
              padding: const EdgeInsets.fromLTRB(12, 10, 12, 6),
              child: SpeakBubble(text: Strings.worldAsk(w), onTap: () => _say(Strings.worldAsk(w)), size: 18, color: worldColor(w)),
            ),
            Expanded(
              flex: 5,
              child: Padding(
                padding: const EdgeInsets.all(14),
                child: Center(
                  child: AspectRatio(
                    aspectRatio: 1.5,
                    child: FeltCard(
                      padding: const EdgeInsets.all(8),
                      child: ClipRRect(borderRadius: BorderRadius.circular(16), child: Art(artPath(g.settings.style, w, 'card'), fit: BoxFit.cover)),
                    ),
                  ),
                ),
              ),
            ),
            Expanded(
              flex: 4,
              child: LayoutBuilder(builder: (_, box) {
                const gap = 12.0;
                final modes = g.settings.modes;
                final width = math.min((box.maxWidth - 3 * gap) / 2, 260.0);
                final height = math.min((box.maxHeight - 3 * gap) / 2, width * 0.62);
                return Center(
                  child: Wrap(spacing: gap, runSpacing: gap, alignment: WrapAlignment.center, children: [
                    for (final m in modes) ModeButton(mode: m, width: width, height: height, onTap: () => _play(m)),
                  ]),
                );
              }),
            ),
          ]),
        ),
      ),
    );
  }
}

/// A big button for a game: its colour, a picture of what it is, its name.
class ModeButton extends StatelessWidget {
  const ModeButton({super.key, required this.mode, required this.width, required this.height, required this.onTap});

  final Mode mode;
  final double width;
  final double height;
  final VoidCallback onTap;

  static IconData icon(Mode m) => switch (m) {
        Mode.road => Icons.gesture_rounded,
        Mode.maze => Icons.grid_view_rounded,
        Mode.errand => Icons.vpn_key_rounded,
      };

  @override
  Widget build(BuildContext context) {
    final color = modeColor(mode);
    return Semantics(
      container: true,
      button: true,
      label: mode.zh,
      excludeSemantics: true,
      onTap: onTap,
      child: Pressable(
        onTap: onTap,
        child: Container(
          width: width,
          height: height,
          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
          decoration: BoxDecoration(
            color: color,
            borderRadius: BorderRadius.circular(24),
            border: Border.all(color: Colors.white.withValues(alpha: 0.6), width: 2),
            boxShadow: [BoxShadow(color: Color.lerp(color, Colors.black, 0.25)!, offset: const Offset(0, 5))],
          ),
          child: Center(
            child: Column(mainAxisSize: MainAxisSize.min, children: [
              Icon(icon(mode), color: Colors.white, size: height * 0.38),
              const SizedBox(height: 4),
              FittedBox(child: Text(mode.zh, style: const TextStyle(fontSize: 20, fontWeight: FontWeight.w700, color: Colors.white))),
            ]),
          ),
        ),
      ),
    );
  }
}
