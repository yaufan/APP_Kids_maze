import '../core/content.dart';

/// Everything the app says, in Traditional Chinese (Taiwan).
abstract final class Strings {
  static const appName = '迷宮小冒險';

  // Home.
  static const welcome = '我是土豆！我挖了好多路，一起走走看！';
  static const hello = ['我是小鼴鼠土豆！', '今天要去哪裡玩？', '我最會挖地道了！', '嘿咻嘿咻，挖好了！'];
  static const parent = '家長';
  static const stickers = '貼紙冊';
  static const home = '回家';
  static const back = '回去';
  static String worldAsk(World w) => '我們在${w.zh}！要玩哪一個？';
  static const locked = '完整版才有喔，請爸爸媽媽看看。';
  static const switchStyle = '換畫風';
  static String styleNow(Style s) => '換成${s.zh}的樣子！';

  // Playing.
  static String ask(World w) => switch (w) {
        World.garden => '帶小蜜蜂去找花！',
        World.tunnel => '帶土豆回地洞的家！',
        World.sea => '帶小魚回珊瑚家！',
        World.city => '帶小公車回總站！',
        World.snow => '帶小企鵝去找媽媽！',
        World.space => '帶太空人回火箭！',
      };
  static String errandAsk(World w) => '先拿鑰匙，打開門，再${ask(w)}';
  static const fork = '要走哪一邊呢？';
  static const deadEnd = '這裡過不去，回頭看看！';
  static const followRoad = '沿著路走喔！';
  static const gotKey = '拿到鑰匙了！門打開了！';
  static const gateShut = '門關著，先去拿鑰匙！';
  static const hint = '土豆來幫忙！往這邊走！';
  static const hintButton = '提示';
  static const right = ['好棒！', '你好會找路！', '真厲害！', '太棒了！'];
  static const arrived = '到家了！';
  static const gotSticker = '得到一張貼紙！';
  static const next = '下一關';
  static const toMap = '回地圖';

  // The sticker book.
  static String stickerCount(int have) => '$have／${World.levels}';

  // Resting.
  static const restTitle = '土豆要睡覺了';
  static const restLine = '眼睛也休息一下。\n我們去窗戶邊，\n看看遠遠的地方吧！';

  // Parent gate (as in the sibling apps).
  static const callParent = '請爸爸媽媽來幫忙喔！';
  static const parentGateTitle = '家長確認';
  static String gateQuestion(String a, String b) => '$a 加 $b 等於多少？';
  static const gateRules = '答錯三次要等一分鐘。';
  static const wrongAnswer = '不對喔，換一題。';
  static String gateWait(int s) => '請等 $s 秒再試';
  static const backspace = '刪掉';
  static const cancel = '取消';

  // Parent mode.
  static const parentTitle = '家長模式';
  static const age = '年齡（難度）';
  static String levelLine(Level l) => l.ages;
  static const ageNote = '年紀越大，路越長、岔路越多。2～3 歲只有一條沒有岔路的路；3～4 歲有幾個很短的岔路；4～5 歲是小迷宮，還要先拿鑰匙再回家。';
  static const playTime = '每次可以玩多久';
  static String minutes(int m) => '$m 分鐘';
  static const playTimeNote = '時間到了，土豆會鑽回地洞睡覺，請小朋友讓眼睛休息、看看遠方。要家長解開，或等一個小時，才能再玩。';
  static const playOn = '讓小朋友再玩一次（重新計時）';
  static const resting = '現在是休息時間。';
  static const style = '一開始的畫風';
  static const styleNote = '三種畫風的迷宮一模一樣，小朋友玩的時候也可以點右上角換。';
  static const hints = '提示';
  static const hintsMany = '多';
  static const hintsFew = '少';
  static const hintsNote = '多：20 秒沒走到新的地方，土豆會探出頭、把該走的路點亮；少：要點放大鏡才有提示。';
  static const sound = '聲音';
  static const music = '背景音樂';
  static const effects = '音效';
  static const voice = '念出要做什麼、往哪裡走';
  static const english = '說完國語，再說一次英文（bee, flower）';
  static const progress = '進度';
  static String progressLine(int walked, int stickers) => walked == 0 ? '還沒玩過' : '走完 $walked 關，貼紙 $stickers／${World.levels}';
  static const progressNote = '每走完一關得一張貼紙，每個世界 10 張。';
  static const together = '生活中一起玩';
  static const tips = [
    '散步時讓小朋友帶路：「從這裡到溜滑梯，要怎麼走？」',
    '用紙膠帶在地上貼一條彎彎的路，讓小朋友沿著走。',
    '畫一張簡單的家裡地圖，一起玩找寶藏。',
    '走迷宮時一起說出方向：「往上」「轉彎」「左邊」。',
    '紙上的迷宮先用手指走一次，再用筆畫。',
  ];
  static const fullVersion = '完整版';
  static const fullNote = '免費版有花園和海底；完整版有全部六個世界。（測試版先全部打開。）';
  static const fullSwitch = '打開完整版（測試用）';
  static const about = '關於';
  static const privacy = '不連網、不定位、沒有廣告、沒有帳號；玩的紀錄不會傳給任何人，只存在這支手機（和家長自己帳號的手機備份）裡。';
  static String version(String v) => '版本 $v';
}
