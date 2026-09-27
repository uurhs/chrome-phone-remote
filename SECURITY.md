# Security and privacy / セキュリティとプライバシー

## Supported use

Trusted home LAN only. This beta is not an internet-facing remote desktop. HTTP/WebSocket traffic is not encrypted. Do not expose port 8765 with port forwarding or use untrusted/public Wi-Fi. Pairing is not a substitute for TLS or a trusted network.

## Access model

- Phone pairing uses a fresh six-digit code per server start and an HttpOnly, SameSite=Strict persistent device cookie. Five failed pairing attempts per IP within a minute trigger a temporary block.
- The extension connects through loopback (127.0.0.1). A long random device token is stored in Chrome extension storage until Forget device or revocation. Only SHA-256 token hashes and device types are saved in the PC's `.state/registrations.json`. The phone and extension receive different credentials. The running server keeps frames and commands in memory.
- The selected tab is controlled through Chrome's debugger permission. This is a powerful permission: review the source and only load files you trust.
- No remote shell, arbitrary Python command endpoint, external analytics, or recording-to-disk is implemented. Media controls execute fixed scripts in the selected tab.
- Tab titles/URLs and frames are visible to paired phones. Users sharing the same code share one selected tab. Pair only your own devices.
- Stop the server when finished; registrations persist across restarts. Type R then Enter in the PC console to revoke all devices and invalidate existing connections. Preserve `.state` for personal updates but exclude it from all distributions.

## Reporting

Do not post a working exploit, code, cookie or private tab content in a public issue. Contact the repository maintainer privately. Before public release, the maintainer should enable GitHub private vulnerability reporting. No reporting address has been invented for this source package.

## 日本語要約

家庭内の信頼できるLAN専用です。通信内容は暗号化されません。接続済みスマホからは選択タブの内容を見て操作できます。終了後はPC側を停止してください。登録は保持されます。PC画面でR→Enterを押すと全登録を解除できます。`.state` フォルダを配布物へ含めないでください。脆弱性を見つけた場合は公開Issueへ詳細を書かず、配布リポジトリの管理者へ非公開で連絡してください。
