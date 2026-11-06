import 'package:flutter/material.dart';

import '../core/content.dart';

/// The app's colours (docs/mockups/): warm cream cloth, brown words.
abstract final class Felt {
  static const ink = Color(0xFF4A3B32);
  static const inkSoft = Color(0xFF9A8A7C);
  static const cream = Color(0xFFFFF6E9);
  static const cloth = Color(0xFFFBEBD5);
  static const green = Color(0xFF5DB85A);
  static const coral = Color(0xFFEF6B5B);
  static const orange = Color(0xFFF59A3C);
  static const blue = Color(0xFF4C9BE8);
  static const purple = Color(0xFF9A7BE0);
  static const gold = Color(0xFFFFC53D);
  static const glow = Color(0xFFFFE45C);
  static const card = Colors.white;
  static const edge = Color(0xFFE6D6BF);
  static const parentBg = Color(0xFFF5F2EE);
}

/// Each world's colour (its card, its pill, the trail of footprints).
Color worldColor(World w) => switch (w) {
      World.garden => const Color(0xFF5DB85A),
      World.tunnel => const Color(0xFFB07A4F),
      World.sea => const Color(0xFF3DA9E0),
      World.city => const Color(0xFFF2A33B),
      World.snow => const Color(0xFF79B8E3),
      World.space => const Color(0xFF6F5BD6),
    };

/// Each game's colour.
Color modeColor(Mode m) => switch (m) {
      Mode.road => Felt.green,
      Mode.maze => Felt.blue,
      Mode.errand => Felt.orange,
    };

abstract final class FeltTheme {
  /// jf open 粉圓 (OFL): a rounded typeface made in Taiwan.
  static const font = 'Huninn';

  static ThemeData light() {
    final base = ThemeData(
      colorScheme: ColorScheme.fromSeed(seedColor: Felt.green, surface: Felt.cream),
      scaffoldBackgroundColor: Felt.cream,
      fontFamily: font,
      materialTapTargetSize: MaterialTapTargetSize.padded,
    );
    return base.copyWith(textTheme: base.textTheme.apply(bodyColor: Felt.ink, displayColor: Felt.ink, fontFamily: font));
  }
}
