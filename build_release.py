"""Allowlist-only source ZIP; excludes profiles, tokens, venvs and caches."""
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parent
FILES = ['pairing.py', 'app.py', 'bootstrap.py', 'start.bat', 'requirements.txt', 'requirements-dev.txt',
         'README.md', 'LICENSE', 'SECURITY.md', 'THIRD_PARTY_NOTICES.md', 'CHANGELOG.md',
         'CONTRIBUTING.md', '.gitignore', 'build_release.py']
FOLDERS = ['docs', 'extension', 'static', 'templates', 'tests', '.github']

def build(destination=None):
    destination = Path(destination or ROOT/'dist'/'chrome-phone-remote-0.4.1-beta.zip')
    destination.parent.mkdir(parents=True, exist_ok=True)
    paths = [ROOT/name for name in FILES]
    for name in FOLDERS:
        paths.extend(p for p in (ROOT/name).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ('.pyc', '.log'))
    with zipfile.ZipFile(destination, 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(paths):
            archive.write(path, 'chrome_phone_remote/'+path.relative_to(ROOT).as_posix())
    print(destination)
    return destination

if __name__ == '__main__':
    build()
