# First-time user guide (English)

Chrome Phone Remote 0.4.1 beta

**Want to skip installing Python?** Use the [Windows portable guide](PORTABLE_EN.md). The steps below are for the source ZIP.

## 1. What does this do?

Control a YouTube video in your PC's Chrome from your phone while a game stays in front. Your phone only needs a browser. Setup happens on your PC.

The volume slider changes the video in the selected tab. Audio continues playing on the PC. It does not change the game's, Discord's, or Windows master volume.

## 2. What you need

- A Windows 10 or 11 PC
- Google Chrome (current stable recommended; minimum 116)
- Python 3.10 or newer
- A smartphone with a browser
- A trusted home network connecting both devices

Ethernet on the PC and Wi-Fi on the phone can work through the same router. Guest Wi-Fi may block communication between devices. Internet access is needed to install dependencies initially.

This is beta **source software**, not a signed Windows installer or a Chrome Web Store extension.

## 3. Extract the download

1. Download the ZIP from the distribution page.
2. Right-click it and choose **Extract All**.
3. Choose a permanent folder, for example `Documents/ChromePhoneRemote`.
4. Open the extracted `chrome_phone_remote` folder.
5. Confirm you can see `start.bat`, `app.py`, and the `extension` folder.

Do not run the tool from inside the ZIP. Once you load the extension, do not move or delete its folder: Chrome reads its files from that location.

## 4. Install Python once

Skip this if Python 3.10 or newer is already installed.

1. Download Python for Windows from [python.org](https://www.python.org/downloads/).
2. If the installer offers **Add Python to PATH**, select it.
3. Complete installation and close any old command windows.

You do not need to run this tool as an administrator.

## 5. Start the PC server

1. Double-click `start.bat`.
2. On the first run, wait while it prepares an isolated `.venv` environment and installs components.
3. A console window displays a six-digit code and a phone URL such as `http://192.168...:8765/`.
4. Leave this window open.

If Windows Firewall prompts you, allow communication on your trusted **Private network**. Do not disable the firewall entirely.

## 6. Add the Chrome extension once

1. Type `chrome://extensions` into Chrome's address bar and press Enter.
2. Enable **Developer mode** in the upper right.
3. Click **Load unpacked**.
4. Select the **`extension` subfolder** in the extracted download, not the ZIP or parent folder.
5. Confirm **Chrome Phone Remote Bridge** appears.
6. Click Chrome's puzzle-piece icon to open it. Pinning it makes later access easier.

Permissions: `debugger` sends commands to the selected page, `tabs` reads tab names and URLs for the picker, `storage` remembers its registration, and `alarms` wakes it for automatic reconnection. Review these permissions before loading the extension.

## 7. Connect the phone

1. Open the YouTube video or other page you want to control on the PC.
2. Open the extension popup, enter the code displayed by the PC server, and click **Connect**.
3. Chrome may display a debugging notification. This is expected for this connection method.
4. Connect your phone to the same trusted home network.
5. Enter the displayed phone URL into your phone browser's **address bar**, rather than searching for it.
6. Enter the same six-digit code on the phone.
7. Select a tab. The page preview and video volume controls should become available.

Enter the code only for first-time registration. Registered phones and extensions reconnect after a PC server restart without re-entering it. A changed code is only needed to register another device. Repeated wrong pairing codes are temporarily blocked for one minute.

## 8. Controls

| Control | How to use it |
|---|---|
| Volume bar | Drag left/right; use ±5% for fine changes |
| Speaker | Mute/unmute; raising the volume also unmutes |
| ▶ / Ⅱ | Play/pause |
| −10s / +10s | Seek; live streams may restrict seeking |
| Top tab list | Select a PC tab and make it active in its Chrome window, without focusing that window |
| Page preview | Tap to click |
| Scroll mode (`操作: スクロール`) | Swipe vertically to scroll the web page |
| Zoom | Pinch or use +/−, up to 400% |
| Pan mode (`操作: 画面移動`) | Drag the enlarged preview around |
| Percentage button | Reset to 100% |
| Text entry (`入力`) | First tap a field in the preview, then type in the phone text box and press the Input button |
| Reconnect | Reattach the selected tab; select it again if needed |

Some inherited navigation labels remain Japanese: `戻る` = Back, `進む` = Forward, `更新` = Reload, `新規タブ` = New tab, `移動` = Go, `タブ更新` = Refresh tabs, `接続` = Connect. This guide covers the full setup and usage in English.

## 9. Recommended for volume-only gaming use

Select your YouTube tab, then choose **Audio controls only** in the quality selector. This stops preview capture while retaining volume, mute, and playback controls. Choose **Balanced** to restore the preview.

Use **Low** when bandwidth or rendering is limited. **High** uses larger images and more resources. Chrome can reduce rendering for background or minimized tabs regardless of the selected quality; no fixed frame rate is promised.

## 10. Stop and restart

To stop: type `Q` then Enter in the PC console, or press `Ctrl+C`. Registrations are preserved.

Next time: run `start.bat` and open the same URL in the same phone browser. The extension reconnects automatically. If Chrome suspended it, allow about one minute; to reconnect immediately, open the popup and press Connect with an empty code field.

To forget all devices, type `R` then Enter in the PC console. Existing phone and extension credentials and connections are invalidated. Register again using the new code. To forget only the extension, use its **Forget device** button.

Registrations are stored in `.state/registrations.json` in the extracted folder. Preserve this folder during updates; never publish it. Clearing phone cookies, private browsing, a changed PC IP, or long inactivity (cookie lifetime is normally one year) may require pairing again.

## 11. Update or uninstall

Upgrading from 0.3.x requires pairing the phone and extension once more. After that, registrations persist.

Before updating, stop the PC server. Extract the new ZIP and replace the old files in the same folder. Open `chrome://extensions` and click the extension's reload arrow. Start the server again and reload the phone page.

If you extract to a different location, remove the old extension and load the new `extension` folder.

To uninstall: disconnect, stop the server, remove the extension from Chrome, and delete the extracted folder. The tool does not keep your ordinary Chrome profile in that folder. If an older prototype left a `chrome-profile` folder, treat it as private and never redistribute it.

## 12. Troubleshooting

| Symptom | What to check |
|---|---|
| Python not found | Install Python 3.10+ and enable PATH |
| Component installation fails | Internet connection, proxy, PC management restrictions; note the error text |
| Local environment seems broken | Stop the server, delete only `.venv`, and run `start.bat` again |
| Phone cannot open URL | Server window still open, correct URL, same LAN, guest-network isolation, private-network firewall permission |
| URL shows 127.0.0.1 | Connect the PC to the LAN and restart. 127.0.0.1 on your phone refers to the phone itself |
| Wrong code | Use the latest server code in both places |
| Extension cannot attach | Open a normal web page; managed Chrome installations may prohibit debugger access |
| Blank or frozen preview | Check quality is not Audio controls only; restore minimized Chrome; reconnect; close DevTools for that tab |
| Volume shows --% | Select the actual YouTube video tab, start a video, wait briefly; reload the extension after updates |
| Port already in use | Close the earlier copy; only one instance can use port 8765 |
| Buttons stop responding | Reconnect/reload the extension and refresh the phone page |

For a bug report, include Windows/Chrome versions, phone/browser, reproduction steps and error text. Remove connection codes, cookies, and private tab titles/URLs before posting.

## 13. Intended use and privacy

Trusted home LAN only. HTTP/WS traffic is unencrypted. Do not use public Wi-Fi, router port forwarding, or expose the service to the internet. No external analytics or recording storage is implemented. Protected media, site behavior, and games can impose limits; compatibility is not certified for every game or anti-cheat system.
