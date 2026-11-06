/// The fixed things the game is made of: the six worlds, the three games,
/// the three ages and the three drawing styles (docs/design.md).
library;

/// A world: who walks home there, and where home is. Its pictures are in
/// `assets/art/<style>/<name>/` (docs/art.md).
enum World {
  garden('花園', '小蜜蜂', '花', 'bee', 'flower'),
  tunnel('地底隧道', '土豆', '地洞的家', 'mole', 'burrow'),
  sea('海底', '小魚', '珊瑚家', 'fish', 'coral'),
  city('城市', '小公車', '公車總站', 'bus', 'bus station'),
  snow('雪地', '小企鵝', '企鵝媽媽', 'penguin', 'igloo'),
  space('太空', '太空人', '火箭', 'astronaut', 'rocket');

  const World(this.zh, this.hero, this.home, this.heroEn, this.homeEn);

  final String zh;

  /// Who walks home.
  final String hero;

  /// Where home is.
  final String home;
  final String heroEn;
  final String homeEn;

  /// Free to play before the full version is bought (docs/design.md).
  bool get free => this == garden || this == sea;

  /// Levels (and stickers) in a world.
  static const levels = 10;
}

/// How old the child is, which sets how hard the mazes are.
enum Level {
  small('小小', '2～3 歲'),
  mid('中', '3～4 歲'),
  big('大', '4～5 歲');

  const Level(this.zh, this.ages);

  final String zh;
  final String ages;

  T pick<T>(T small, T mid, T big) => switch (this) {
        Level.small => small,
        Level.mid => mid,
        Level.big => big,
      };
}

/// The three games (docs/design.md 「三種玩法」) and the age each starts at.
enum Mode {
  road('跟著路走', Level.small),
  maze('走迷宮', Level.mid),
  errand('送東西', Level.big);

  const Mode(this.zh, this.from);

  final String zh;
  final Level from;
}

/// The three drawing styles; all draw the same maze, so switching never
/// changes the way home.
enum Style {
  /// 羊毛氈布書風 (the default).
  a('布書'),

  /// 像素小遊戲風.
  b('像素'),

  /// 果凍糖果風.
  c('果凍');

  const Style(this.zh);

  final String zh;

  Style get next => Style.values[(index + 1) % Style.values.length];
}
