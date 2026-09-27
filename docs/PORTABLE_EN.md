# Windows edition without installing Python

Use `chrome-phone-remote-windows-beta.zip` on 64-bit Windows 10/11. Python and pip are bundled; they do not need to be installed separately. You still need Chrome, a phone, and a trusted home LAN. This is an unsigned beta, not an installer.

## First setup

1. Download the Windows ZIP, right-click it, and choose **Extract All**. Do not run it from inside the ZIP.
2. Place the extracted `ChromePhoneRemote` folder somewhere writable, such as Documents. Avoid Program Files. Keep the folder in place because Chrome loads the extension from it.
3. Double-click `ChromePhoneRemote.exe`. Keep its console window open; it displays a six-digit pairing code and phone URL.
4. If Windows Firewall asks, allow only your trusted **private** network, not public networks.
5. In PC Chrome, open `chrome://extensions`, enable Developer mode, choose **Load unpacked**, and select the extracted `ChromePhoneRemote/extension` folder.
6. Open the extension and enter the six-digit code shown on the PC. Open the YouTube tab you want to control.
7. Connect the phone to the same home LAN. Type the PC's URL into the phone browser's **address bar**, then enter the code on the phone once.

On later days, launch the EXE and open the same URL on the phone. Registered devices reconnect automatically. See [the full guide](USER_GUIDE_EN.md) for the controls.

## Update, stop, remove

- Press `Q` then Enter in the PC console to stop. Press `R` then Enter to revoke all registered devices.
- Stop the server before replacing files with the next ZIP **in the same folder**. Keep `.state` to preserve paired devices. Reload the extension at `chrome://extensions`.
- To uninstall, stop the server, remove the Chrome extension, then delete the extracted folder.
- Do not move the EXE alone: its neighboring `_internal` folder is required.

## Troubleshooting

- Windows may warn about this unsigned beta. **Do not run it if you cannot verify its source and ZIP contents.** Do not blindly bypass security warnings.
- Managed PCs may block unsigned applications. Administrator privileges are not needed.
- If the phone cannot connect, check the home LAN, the URL shown on the PC and private-network firewall permission. Never use port forwarding or public Wi-Fi; HTTP/WebSocket traffic is unencrypted.
- If port 8765 is in use, stop the already-running copy.

The source edition's `start.bat` still needs Python. Use `ChromePhoneRemote.exe` from the Windows ZIP instead.
