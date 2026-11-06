import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../app/strings.dart';
import '../../app/theme.dart';
import '../../app/widgets.dart';
import '../../core/content.dart';
import '../../core/providers.dart';
import '../../core/sounds.dart';
import '../parent/parent_gate.dart';

/// The home page: 土豆 says hello from his hole, the six worlds as felt
/// cards with their stars, the sticker book, and (small, at the top) the way
/// into parent mode.
class HomeScreen extends ConsumerStatefulWidget {
  const HomeScreen({super.key});

  @override
  ConsumerState<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends ConsumerState<HomeScreen> {
  late final Sounds _sounds;
  var _hello = 0;
  var _wiggle = 0;

  @override
  void initState() {
    super.initState();
    _sounds = ref.read(soundsProvider);
    _sounds.hold(this, Music.home);
    if (ref.read(onceProvider).add('welcome')) WidgetsBinding.instance.addPostFrameCallback((_) => _say(Strings.welcome));
  }

  @override
  void dispose() {
    _sounds.release(this);
    super.dispose();
  }

  void _say(String zh, {String? en}) {
    final s = ref.read(gameProvider).settings;
    if (mounted && s.voice) ref.read(voiceProvider).say(zh, en: s.english ? en : null);
  }

  void _tudou() {
    _sounds.play('giggle');
    setState(() {
      _wiggle++;
      _hello = (_hello + 1) % Strings.hello.length;
    });
    _say(Strings.hello[_hello]);
  }

  void _open(World w) {
    final s = ref.read(gameProvider).settings;
    if (!s.opens(w)) {
      _say(Strings.locked);
      return;
    }
    _say(w.zh, en: w.homeEn);
    // 2～3 year olds have one game: straight into it.
    final modes = s.modes;
    context.push(modes.length == 1 ? '/play/${w.name}/${modes.single.name}' : '/world/${w.name}');
  }

  Future<void> _parent() async {
    if (await showParentGate(context) && mounted) await context.push('/parent');
  }

  @override
  Widget build(BuildContext context) {
    final style = ref.watch(gameProvider.select((g) => g.settings.style));
    return Scaffold(
      body: Sky(
        top: Felt.cloth,
        bottom: Felt.cream,
        child: SafeArea(
          child: LayoutBuilder(builder: (context, box) {
            final wide = box.maxWidth > 600;
            final pad = box.maxWidth > 860 ? (box.maxWidth - 860) / 2 + 16 : 16.0;
            return Column(children: [
              Expanded(
                child: ListView(padding: EdgeInsets.fromLTRB(pad, 8, pad, 12), children: [
                  Row(children: [
                    const Spacer(),
                    Semantics(
                      container: true,
                      button: true,
                      label: Strings.parent,
                      excludeSemantics: true,
                      onTap: _parent,
                      child: GestureDetector(
                        behavior: HitTestBehavior.opaque,
                        onTap: _parent,
                        child: Container(
                          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                          decoration: BoxDecoration(color: Colors.white.withValues(alpha: 0.7), borderRadius: BorderRadius.circular(18)),
                          child: const Row(mainAxisSize: MainAxisSize.min, children: [
                            Icon(Icons.lock_outline_rounded, color: Felt.inkSoft, size: 18),
                            SizedBox(width: 4),
                            Text(Strings.parent, style: TextStyle(fontSize: 15, color: Felt.inkSoft)),
                          ]),
                        ),
                      ),
                    ),
                  ]),
                  const SizedBox(height: 4),
                  const Center(child: FeltTitle(Strings.appName)),
                  const SizedBox(height: 10),
                  Row(children: [
                    Semantics(
                      container: true,
                      button: true,
                      label: '土豆',
                      excludeSemantics: true,
                      onTap: _tudou,
                      child: GestureDetector(
                        behavior: HitTestBehavior.opaque,
                        onTap: _tudou,
                        child: Wiggle(trigger: _wiggle, child: SizedBox.square(dimension: 118, child: Bob(child: Tudou(pose: 'wave', style: style)))),
                      ),
                    ),
                    const SizedBox(width: 6),
                    Expanded(child: SpeakBubble(text: _hello == 0 ? Strings.welcome : Strings.hello[_hello], onTap: () => _say(_hello == 0 ? Strings.welcome : Strings.hello[_hello]), size: 18)),
                  ]),
                  const SizedBox(height: 14),
                  GridView.count(
                    crossAxisCount: wide ? 3 : 2,
                    shrinkWrap: true,
                    physics: const NeverScrollableScrollPhysics(),
                    mainAxisSpacing: 14,
                    crossAxisSpacing: 14,
                    childAspectRatio: 1.08,
                    children: [for (final w in World.values) WorldCard(world: w, onTap: () => _open(w))],
                  ),
                ]),
              ),
              Padding(
                padding: const EdgeInsets.fromLTRB(16, 6, 16, 14),
                child: WideButton(label: Strings.stickers, icon: Icons.auto_stories_rounded, color: Felt.coral, onTap: () => context.push('/stickers')),
              ),
            ]);
          }),
        ),
      ),
    );
  }
}

/// A world: its picture, its name and stars (a lock while it is not open).
class WorldCard extends ConsumerWidget {
  const WorldCard({super.key, required this.world, required this.onTap});

  final World world;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final g = ref.watch(gameProvider);
    final open = g.settings.opens(world);
    return Semantics(
      container: true,
      button: true,
      label: world.zh,
      excludeSemantics: true,
      onTap: onTap,
      child: Pressable(
        onTap: onTap,
        child: FeltCard(
          padding: const EdgeInsets.all(8),
          child: Column(children: [
            Expanded(
              child: Stack(children: [
                Positioned.fill(child: ClipRRect(borderRadius: BorderRadius.circular(14), child: Art(artPath(g.settings.style, world, 'card'), fit: BoxFit.cover))),
                if (!open)
                  Positioned.fill(
                    child: Container(
                      decoration: BoxDecoration(color: Colors.white.withValues(alpha: 0.55), borderRadius: BorderRadius.circular(14)),
                      child: const Icon(Icons.lock_rounded, size: 40, color: Felt.inkSoft),
                    ),
                  ),
              ]),
            ),
            const SizedBox(height: 6),
            Row(children: [
              Container(width: 10, height: 10, decoration: BoxDecoration(color: worldColor(world), shape: BoxShape.circle)),
              const SizedBox(width: 6),
              Expanded(child: Text(world.zh, maxLines: 1, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w700))),
              Stars(count: g.starsOf(world), size: 17),
            ]),
          ]),
        ),
      ),
    );
  }
}

/// The title as felt circles, one per character, each its own colour.
class FeltTitle extends StatelessWidget {
  const FeltTitle(this.text, {super.key, this.size = 46});

  final String text;
  final double size;

  static const _colors = [Felt.coral, Felt.orange, Felt.green, Felt.blue, Felt.purple];

  @override
  Widget build(BuildContext context) {
    final chars = text.characters.toList();
    return Semantics(
      label: text,
      excludeSemantics: true,
      child: Row(mainAxisSize: MainAxisSize.min, children: [
        for (var i = 0; i < chars.length; i++)
          Container(
            width: size,
            height: size,
            margin: const EdgeInsets.symmetric(horizontal: 2),
            alignment: Alignment.center,
            decoration: BoxDecoration(
              color: _colors[i % _colors.length],
              shape: BoxShape.circle,
              border: Border.all(color: Colors.white.withValues(alpha: 0.7), width: 2),
              boxShadow: const [BoxShadow(color: Color(0x336B4F33), offset: Offset(0, 3), blurRadius: 4)],
            ),
            child: Text(chars[i], style: TextStyle(fontSize: size * 0.5, fontWeight: FontWeight.w700, color: Colors.white)),
          ),
      ]),
    );
  }
}
