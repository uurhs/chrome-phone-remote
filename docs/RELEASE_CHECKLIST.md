# GitHub公開前チェック / Release checklist

This package is prepared for a public **beta source release**. It has not been uploaded to GitHub. The existing user has confirmed the earlier core functionality; new changes need Windows/phone confirmation below.

## Repository preparation

- [ ] Create the intended repository and review its visibility.
- [ ] Review MIT LICENSE and contributor attribution; add maintainer identity/contact if desired.
- [ ] Enable private vulnerability reporting and decide how to handle support issues.
- [ ] Commit only the source tree. Never copy `.venv`, `chrome-profile`, cookies, tokens or logs.
- [ ] Run automated checks and resolve failures.
- [ ] Run `python build_release.py`; use the generated allowlisted source ZIP.
- [ ] Describe the release as beta; state Python and manual extension setup requirements.
- [ ] Do not advertise a signed executable, Web Store approval, security audit, fixed FPS or anti-cheat certification.

## Manual device checks before promoting out of beta

- [ ] Clean Windows 10/11 account: Python setup, first launch, firewall prompt, repeat launch.
- [ ] Android Chrome and iPhone Safari: pairing, reconnect, landscape, zoom/pan, scroll and typing.
- [ ] Existing YouTube tab: volume/mute, ±5%, play/pause and ±10 seconds.
- [ ] Quality changes and audio-only mode; re-enable preview.
- [ ] PC server restart/automatic reconnect and R/Enter registration reset, closed selected tab, Wi-Fi interruption, extension reload/disconnect.
- [ ] Game foreground: no Windows cursor/focus change during remote input; measure actual responsiveness.
- [ ] Update from prior ZIP and uninstall instructions.

## Verification scope for this handoff

Automated server/request checks, JavaScript parsing and local WebSocket relay can run in the development environment. They do not substitute for the Windows/phone/game matrix. Record actual device results in the release notes rather than marking untested items complete.

## 日本語補足

README・説明書・ライセンス・CI・ZIP作成スクリプトを同梱しています。公開そのものは未実施です。まずベータ版として配布し、上の実機チェックを実施した機種だけ動作確認済みとしてください。実行ファイル化する場合は、依存ライセンス同梱、コード署名、配布物の検査を別途行う必要があります。
