import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../app/strings.dart';
import '../../app/theme.dart';
import '../../app/widgets.dart';
import '../../core/content.dart';
import '../../core/providers.dart';

/// The sticker book: a felt page for each world with ten places, filled
/// one by one as the child walks the levels home.
class StickerScreen extends ConsumerStatefulWidget {
  const StickerScreen({super.key});

  @override
  ConsumerState<StickerScreen> createState() => _StickerScreenState();
}

class _StickerScreenState extends ConsumerState<StickerScreen> {
  var _world = World.garden;

  void _turn(World w) {
    ref.read(soundsProvider).play('page');
    setState(() => _world = w);
  }

  @override
  Widget build(BuildContext context) {
    final g = ref.watch(gameProvider);
    final style = g.settings.style;
    final have = g.stickers(_world);
    return Scaffold(
      body: Sky(
        top: const Color(0xFFFFEDE6),
        bottom: Felt.cream,
        child: SafeArea(
          child: Column(children: [
            Padding(
              padding: const EdgeInsets.fromLTRB(12, 8, 12, 0),
              child: Row(children: [
                RoundButton(label: Strings.home, icon: Icons.home_rounded, size: 50, onTap: () => context.canPop() ? context.pop() : context.go('/')),
                const SizedBox(width: 10),
                const Pill(text: Strings.stickers, color: Felt.coral),
                const Spacer(),
                Text(Strings.stickerCount(have), style: const TextStyle(fontSize: 18, color: Felt.inkSoft, fontWeight: FontWeight.w700)),
              ]),
            ),
            SizedBox(
              height: 64,
              child: ListView(scrollDirection: Axis.horizontal, padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8), children: [
                for (final w in World.values)
                  Padding(
                    padding: const EdgeInsets.only(right: 8),
                    child: Semantics(
                      container: true,
                      button: true,
                      selected: w == _world,
                      label: w.zh,
                      excludeSemantics: true,
                      onTap: () => _turn(w),
                      child: Pressable(
                        onTap: () => _turn(w),
                        sound: null,
                        child: AnimatedContainer(
                          duration: const Duration(milliseconds: 200),
                          padding: const EdgeInsets.symmetric(horizontal: 14),
                          alignment: Alignment.center,
                          decoration: BoxDecoration(
                            color: w == _world ? worldColor(w) : Colors.white,
                            borderRadius: BorderRadius.circular(20),
                            border: Border.all(color: worldColor(w), width: 2),
                          ),
                          child: Text(w.zh, style: TextStyle(fontSize: 17, fontWeight: FontWeight.w700, color: w == _world ? Colors.white : Felt.ink)),
                        ),
                      ),
                    ),
                  ),
              ]),
            ),
            Expanded(
              child: Padding(
                padding: const EdgeInsets.fromLTRB(16, 4, 16, 16),
                child: Container(
                  decoration: BoxDecoration(
                    color: worldColor(_world),
                    borderRadius: BorderRadius.circular(28),
                    boxShadow: const [BoxShadow(color: Color(0x336B4F33), offset: Offset(0, 6), blurRadius: 12)],
                  ),
                  padding: const EdgeInsets.all(10),
                  child: Container(
                    decoration: BoxDecoration(
                      color: const Color(0xFFFFFBF3),
                      borderRadius: BorderRadius.circular(22),
                      border: Border.all(color: Colors.white, width: 3),
                    ),
                    child: LayoutBuilder(builder: (_, box) {
                      const cols = 2, rows = 5;
                      final cell = math.min((box.maxWidth - 24) / cols, (box.maxHeight - 24) / rows);
                      return Center(
                        child: Wrap(children: [
                          for (var i = 1; i <= World.levels; i++)
                            SizedBox.square(
                              dimension: cell,
                              child: Padding(
                                padding: EdgeInsets.all(cell * 0.08),
                                child: i <= have
                                    ? Semantics(label: '貼紙 $i', child: Art(artPath(style, _world, 'sticker_${i.toString().padLeft(2, '0')}')))
                                    : Container(
                                        decoration: BoxDecoration(shape: BoxShape.circle, color: const Color(0xFFF3E8D8), border: Border.all(color: Felt.edge, width: 2)),
                                        child: Icon(Icons.star_rounded, size: cell * 0.3, color: Colors.white),
                                      ),
                              ),
                            ),
                        ]),
                      );
                    }),
                  ),
                ),
              ),
            ),
          ]),
        ),
      ),
    );
  }
}
