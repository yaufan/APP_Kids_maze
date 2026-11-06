import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:maze_adventure/app/widgets.dart';
import 'package:maze_adventure/core/content.dart';

/// Every picture the app asks for is there, in every style (docs/art.md).
void main() {
  void exists(String path) => expect(File(path).existsSync(), isTrue, reason: path);

  test('土豆 in every pose and style', () {
    for (final s in Style.values) {
      for (final pose in ['wave', 'point', 'cheer', 'sleep', 'peek']) {
        exists(tudouPath(s, pose));
      }
    }
  });

  for (final w in World.values) {
    test('${w.name}: the ground, all fifteen road tiles and every picture, in every style', () {
      for (final s in Style.values) {
        for (final name in [
          'bg', 'hero', 'home', 'family', 'star', 'key', 'gate', 'card',
          for (var n = 1; n <= 15; n++) 'tile_$n',
          for (var n = 1; n <= 6; n++) 'deco_$n',
          for (var n = 1; n <= World.levels; n++) 'sticker_${n.toString().padLeft(2, '0')}',
        ]) {
          exists(artPath(s, w, name));
        }
      }
    });
  }

  test('every sound the app plays is there', () {
    for (final name in [
      'tap', 'bump', 'star', 'fork', 'key', 'gate', 'arrive', 'cheer', 'sticker', 'hint', 'giggle', 'next', 'switch_style', 'rest', 'page',
      for (final w in World.values) 'step_${w.name}',
      for (final w in World.values) 'music_${w.name}',
      'music_home', 'music_rest',
    ]) {
      exists('assets/sounds/$name.wav');
    }
  });
}
