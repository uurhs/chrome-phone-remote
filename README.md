# Chrome Phone Remote · 0.4.1 beta

**ゲーム中のPCブラウザをスマホで操作。Control your PC browser from your phone while gaming.**

Chrome上のYouTube音量を調整するための、家庭内LAN向けリモコンです。PC側のChrome拡張機能とPythonサーバー、スマホのブラウザで動作します。

A local-network remote for Chrome, focused on YouTube volume while gaming. Uses a Chrome extension, a Python server on your PC, and your phone's browser.

## はじめに / Start here

- **[日本語の詳しい説明書](docs/USER_GUIDE_JA.md)**
- **[Detailed English user guide](docs/USER_GUIDE_EN.md)**
- [Security and privacy / セキュリティ](SECURITY.md)
- [Release checklist / 公開前チェック](docs/RELEASE_CHECKLIST.md)

## Features / 機能

- Existing Chrome tabs; no separate Chrome profile / 普段のChromeタブに接続
- Video volume slider, mute, ±5%, play/pause, ±10 seconds
- Page preview, click, scroll, typing, navigation, tab selection
- 1–4× pinch zoom and pan / ピンチ拡大・画面移動
- Low / balanced / high quality; audio-controls-only mode
- One-time six-digit pairing, automatic reconnection, PC-side registration reset
- Quiet startup and isolated Python environment

## Requirements / 動作要件

Windows 10/11, Chrome 116 or newer (current stable recommended), Python 3.10+, phone browser, trusted home LAN. PC Ethernet + phone Wi-Fi also works when the router allows communication. Initial installation requires internet access.

This is a **beta source distribution**, not a signed Windows installer. First-time setup requires manually loading the unpacked extension. Detailed steps are in the guides. macOS/Linux support is not claimed.

## Limits / 制限

Page image only; no audio streaming, desktop capture, or Chrome toolbar capture. Background/minimized tabs, protected video, and live streams may have limitations. No fixed frame rate is promised. Game/anti-cheat compatibility is not certified. No bypass or game injection is used.

## Development

```sh
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
node --check static/remote.js
node --check extension/worker.js
python build_release.py
```

## License and affiliation

Project code: [MIT](LICENSE). Dependencies retain their own licenses; see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). This project is not affiliated with Google, YouTube, or any game publisher. Names identify compatible products; no third-party logos or media are bundled.
