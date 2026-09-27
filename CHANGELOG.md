# Changelog

## 0.4.1 beta

- Selecting a tab from the phone now activates that tab in its Chrome window.
- The command does not request window focus, preserving the gaming use case.

## 0.4.0 beta

- One-time registration with persistent per-device credentials.
- Automatic extension reconnect, including a periodic wake-up alarm.
- PC console R/Enter revokes all registrations and live sessions.
- Extension Forget device revokes its own registration.
- Registration hashes are saved atomically and excluded from releases.
- Added restart persistence and revocation tests.

## 0.3.1 beta

- Return to pairing after server restart or expired phone session.
- Prevent duplicate status loops and disruptive tab-picker refreshes.
- Release volume drag state on pointer-up, cancellation and blur.
- Recalculate preview layout after leaving audio-only mode.
- Add mocked frontend recovery checks to CI.

## 0.3.0 beta

- Preserves existing-tab control, video preview, scroll, zoom/pan, typing and YouTube volume.
- Adds playback toggle, ±10-second seek, ±5% volume and audio-controls-only mode.
- Adds preview quality choices, reconnect and explicit extension disconnect.
- Restarts capture when the video bridge opens, improving initial static-frame delivery.
- Clears closed-tab state and invalid connection credentials.
- Adds bounded command queue, request validation and stricter page security policy.
- Moves phone UI into maintainable template/static files.
- Adds isolated first-run setup, bilingual guides, source license, CI and release packaging.

This is a beta source release. Windows/phone/game compatibility still requires the manual release checklist.
