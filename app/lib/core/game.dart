import 'dart:math' as math;

import 'content.dart';

/// What a parent set (parent mode).
class Settings {
  const Settings({
    this.level = Level.mid,
    this.minutes = 15,
    this.style = Style.a,
    this.hints = true,
    this.english = false,
    this.music = true,
    this.sounds = true,
    this.voice = true,
    this.full = true,
  });

  /// The child's age, which sets how hard the mazes are.
  final Level level;

  /// How long one sitting may be before a rest.
  final int minutes;

  /// The drawing style (the child can switch it while playing too).
  final Style style;

  /// Many hints: 土豆 shows the way after 20 seconds without moving on.
  final bool hints;
  final bool english;
  final bool music;
  final bool sounds;
  final bool voice;

  /// The full version (all worlds); on while testing.
  final bool full;

  static const minuteChoices = [5, 10, 15, 20, 30];

  /// The games that suit the age (2～3 only follow the road).
  List<Mode> get modes => [for (final m in Mode.values) if (m.from.index <= level.index) m];

  bool opens(World w) => full || w.free;

  Settings copyWith({Level? level, int? minutes, Style? style, bool? hints, bool? english, bool? music, bool? sounds, bool? voice, bool? full}) => Settings(
        level: level ?? this.level,
        minutes: minutes ?? this.minutes,
        style: style ?? this.style,
        hints: hints ?? this.hints,
        english: english ?? this.english,
        music: music ?? this.music,
        sounds: sounds ?? this.sounds,
        voice: voice ?? this.voice,
        full: full ?? this.full,
      );

  Map<String, dynamic> toJson() => {
        'level': level.name,
        'minutes': minutes,
        'style': style.name,
        'hints': hints,
        'english': english,
        'music': music,
        'sounds': sounds,
        'voice': voice,
        'full': full,
      };

  factory Settings.fromJson(Map<String, dynamic> j) {
    final m = j['minutes'];
    bool flag(String k, bool d) => j[k] is bool ? j[k] as bool : d;
    return Settings(
      level: Level.values.asNameMap()[j['level']] ?? Level.mid,
      minutes: m is int && minuteChoices.contains(m) ? m : 15,
      style: Style.values.asNameMap()[j['style']] ?? Style.a,
      hints: flag('hints', true),
      english: flag('english', false),
      music: flag('music', true),
      sounds: flag('sounds', true),
      voice: flag('voice', true),
      full: flag('full', true),
    );
  }
}

/// Everything kept: the levels walked in each world, the rest and the
/// settings. One small file (store.dart).
class Game {
  const Game({this.walked = const {}, this.restSince, this.settings = const Settings()});

  /// Levels walked home in each world (each gives the next sticker).
  final Map<World, int> walked;

  /// When the play time ran out (null: playing).
  final DateTime? restSince;
  final Settings settings;

  /// A rest lasts until a parent lets play go on, or an hour has passed.
  static const restLength = Duration(hours: 1);

  bool resting(DateTime now) => restSince != null && now.difference(restSince!) < restLength;

  int walkedIn(World w) => walked[w] ?? 0;

  /// Stickers collected in [w] (one a level, ten at most).
  int stickers(World w) => math.min(World.levels, walkedIn(w));

  /// Stars on a world's card: one for the first level home, two at five,
  /// three when all ten stickers are in.
  int starsOf(World w) {
    final n = walkedIn(w);
    return n >= World.levels ? 3 : (n >= 5 ? 2 : (n >= 1 ? 1 : 0));
  }

  Game copyWith({Map<World, int>? walked, DateTime? restSince, bool clearRest = false, Settings? settings}) => Game(
        walked: walked ?? this.walked,
        restSince: clearRest ? null : (restSince ?? this.restSince),
        settings: settings ?? this.settings,
      );

  /// A level of [w] walked home.
  Game home(World w) => copyWith(walked: {...walked, w: walkedIn(w) + 1});

  Game rest(DateTime now) => copyWith(restSince: now);

  Game playOn() => copyWith(clearRest: true);

  Map<String, dynamic> toJson() => {
        'version': 1,
        'walked': {for (final e in walked.entries) e.key.name: e.value},
        if (restSince != null) 'restSince': restSince!.toIso8601String(),
        'settings': settings.toJson(),
      };

  factory Game.fromJson(Map<String, dynamic>? j) {
    if (j == null) return const Game();
    final walked = j['walked'], rest = j['restSince'];
    return Game(
      walked: {
        if (walked is Map)
          for (final w in World.values)
            if (walked[w.name] is int && (walked[w.name] as int) >= 0) w: walked[w.name] as int,
      },
      restSince: rest is String ? DateTime.tryParse(rest) : null,
      settings: Settings.fromJson(j['settings'] is Map ? (j['settings'] as Map).cast<String, dynamic>() : const {}),
    );
  }
}
