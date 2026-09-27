# Verification record — 2026-09-26

Executed locally on Linux with Python 3.12; Windows/phone hardware was not available.

Passed:
- Five Python unittest cases: authentication/origin/host checks, HTML/static asset availability, input validation and volume command coalescing, allowlisted archive contents, and binary WebSocket frame relay.
- Node parsing of phone JavaScript and extension JavaScript.
- Mocked player tests for volume, mute, play/pause, seek, and capture-off command.
- Python compilation of app and bootstrap.

Limits:
- The relay test verifies byte transport, not actual Chrome rendering or image decode.
- Player tests use mocks, not a live YouTube page. YouTube's internal player methods may change; the volume code includes an HTML video fallback when methods are absent.
- New touch controls, Windows first-run setup, game foreground behavior, and current iPhone/Android browser behavior require the manual checks in RELEASE_CHECKLIST.md.
- Prior core functionality was confirmed by the user before this polish pass. This does not certify the new release across devices.

## 0.3.1 recovery follow-up

Mocked frontend checks cover one polling loop, stable tab selection, released volume gestures, and returning to pairing after HTTP 403. These do not replace touch-device testing.

## 0.4.0 persistent registration

Additional tests check phone and extension authentication after reloading the registration store, persisted revocation, extension-only revocation, loopback-only bridge registration, and pairing attempt limits. Windows browser lifecycle and real phone-cookie persistence still need device testing.
