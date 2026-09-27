# Third-party components

The source ZIP does not bundle a Python runtime, Chrome, downloaded packages, media, fonts or third-party logos. The Windows portable ZIP bundles a Python runtime and installed packages. Its `THIRD_PARTY_LICENSES` directory contains the license files found in the build environment, including the Python license. Keep that directory and this notice when redistributing the Windows ZIP. Chrome, media, fonts and third-party logos are not bundled.

| Component | Upstream | License family |
|---|---|---|
| Flask | https://github.com/pallets/flask | BSD-3-Clause |
| Flask-Sock | https://github.com/miguelgrinberg/flask-sock | MIT |
| Werkzeug, Jinja2, Click, ItsDangerous, MarkupSafe | https://palletsprojects.com/ | BSD-3-Clause |
| Blinker | https://github.com/pallets-eco/blinker | MIT |
| simple-websocket | https://github.com/miguelgrinberg/simple-websocket | MIT |
| wsproto, h11 | https://github.com/python-hyper | MIT |
| websocket-client (tests only) | https://github.com/websocket-client/websocket-client | Apache-2.0 |

The installed package metadata and its included LICENSE files are authoritative for each resolved version. Optional/platform-specific transitive packages can vary. `pip list` inside `.venv` shows the actual installed set.

Chrome and YouTube are third-party product names used only to describe compatibility. This project does not imply endorsement or affiliation.
