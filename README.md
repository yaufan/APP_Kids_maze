# 迷宮小冒險

給 2～5 歲小朋友的迷宮遊戲：跟著小鼴鼠「土豆」，把小蜜蜂、小魚、小公車這些朋友帶回家。從一條彎彎的路開始，慢慢才有岔路和小迷宮；路很寬、撞牆不會怎樣、不會拖也能用點的。

- 設計：[docs/design.md](docs/design.md)，草圖在 `docs/mockups/`，圖和程式的約定在 [docs/art.md](docs/art.md)。
- 和「[畫畫小鎮](https://github.com/yaufan/APP_Kids_Paint)」「[字母寵物](https://github.com/yaufan/APP_Kids_Paint_for_learning_writing)」「[動物小餐廳](https://github.com/yaufan/APP_Kids_Cook)」「[小卡認天下](https://github.com/yaufan/APP_Kids_Card_Game)」「[想一想樂園](https://github.com/yaufan/APP_Kids_Brainstorming)」「[眼尖尖大挑戰](https://github.com/yaufan/APP_Kids_FalseCharge)」是兄弟 APP：同一個作者、同一套技術、不同畫風。
- 不連網、不定位、沒有廣告、沒有帳號。

## 下載（Android）
- 最新版：[Releases](https://github.com/yaufan/APP_Kids_maze/releases/latest)，一般手機下載 `maze-adventure-版本-arm64.apk`。
- 用手機掃描 [docs/download-qr.png](docs/download-qr.png)。

## 目前進度
- 0.1.0（測試版）：三種玩法（跟著路走、走迷宮、送東西）、三個難度、6 個世界、三種畫風隨時換（羊毛氈布書、像素、果凍糖果）、貼紙冊、休息時間、家長模式、音樂和音效、APP 圖示。版本紀錄在 [CHANGELOG.md](CHANGELOG.md)。

## 程式和素材在哪裡
- `app/`：Flutter 程式。`lib/core/` 是世界和玩法（`content.dart`）、迷宮產生和走路規則（`maze.dart`）、存檔、聲音、語音；`lib/features/` 是首頁和世界頁（`home/`）、玩迷宮（`play/`）、貼紙冊、休息、家長模式。
- 圖和程式的約定：[docs/art.md](docs/art.md)（迷宮由一格一格的路塊拼起來）。
- `design/art/`：用 Python 畫的圖。`kit.py` 把同一份描述畫成三種畫風，`world_<世界>.py` 是六個世界，`tudou.py` 是土豆，`icon.py` 是 APP 圖示；`python3 build.py all` 全部重畫，`seams` 檢查路塊接得起來，`fluttercheck` 用真的 flutter_svg 比對。
- `design/sounds/make_sounds.py`：合成全部的音樂和聲音。
- 測試：在 `app/` 裡 `flutter test`；完整流程 `flutter test test/flow_test.dart`，截圖在 `app/build/screenshots/`。

## 授權
- 非商業使用授權：自己、家人使用，或學校、非營利團體的教學，都可以免費使用、修改、分享，要註明出處。
- 商業用途（販賣、收費、廣告、上架）要先取得作者書面同意。也不可以拿來訓練 AI。
- 細節見 [LICENSE](LICENSE)；別人做的部分（字型）見 [NOTICE.md](NOTICE.md)。
