"""Build an allowlisted, portable Windows ZIP with an embedded Python runtime."""
from __future__ import annotations

import hashlib
import importlib.metadata
import os
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile


ROOT = Path(__file__).resolve().parent
DIST = ROOT / 'dist'
PACKAGE = DIST / 'ChromePhoneRemote'
ARCHIVE = DIST / 'chrome-phone-remote-windows-beta.zip'


def copy_license_notices(destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    copied = 0
    for distribution in importlib.metadata.distributions():
        name = distribution.metadata.get('Name', 'unknown').replace('/', '_').replace('\\', '_')
        version = distribution.version
        for relative in distribution.files or ():
            parts = [part.lower() for part in relative.parts]
            basename = relative.name.lower()
            if not any(part.endswith('.dist-info') for part in parts):
                continue
            if not basename.startswith(('license', 'licence', 'copying', 'notice')):
                continue
            source = Path(distribution.locate_file(relative))
            if source.is_file():
                target = destination / f'{name}-{version}' / relative.as_posix().split('.dist-info/', 1)[-1]
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)
                copied += 1
    if not copied:
        raise RuntimeError('Installed package license files were not found.')

    python_license = next((path for path in (
        Path(sys.base_prefix) / 'LICENSE.txt',
        Path(sys.base_prefix) / 'LICENSE',
        Path(sys.base_prefix).parent / 'LICENSE.txt',
    ) if path.is_file()), None)
    if python_license is None:
        raise RuntimeError('Python runtime license was not found in the build environment.')
    shutil.copy2(python_license, destination / 'Python-LICENSE.txt')


def build() -> Path:
    if os.name != 'nt':
        raise RuntimeError('Build on Windows so the executable runs on Windows.')
    DIST.mkdir(exist_ok=True)
    subprocess.run([
        sys.executable, '-m', 'PyInstaller', '--noconfirm', '--clean', '--onedir',
        '--console', '--name', 'ChromePhoneRemote', '--contents-directory', '_internal',
        '--add-data', f'{ROOT / "templates"}:templates',
        '--add-data', f'{ROOT / "static"}:static',
        str(ROOT / 'app.py'),
    ], check=True, cwd=ROOT)
    if not (PACKAGE / 'ChromePhoneRemote.exe').is_file():
        raise RuntimeError('Windows executable was not generated.')

    shutil.copytree(ROOT / 'extension', PACKAGE / 'extension', ignore=shutil.ignore_patterns('__pycache__'))
    shutil.copytree(ROOT / 'docs', PACKAGE / 'docs', ignore=shutil.ignore_patterns('__pycache__'))
    for name in ('README.md', 'LICENSE', 'SECURITY.md', 'THIRD_PARTY_NOTICES.md'):
        shutil.copy2(ROOT / name, PACKAGE / name)
    copy_license_notices(PACKAGE / 'THIRD_PARTY_LICENSES')

    with zipfile.ZipFile(ARCHIVE, 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(PACKAGE.rglob('*')):
            if path.is_file():
                archive.write(path, path.relative_to(DIST).as_posix())
    print(f'{ARCHIVE} SHA-256 {hashlib.sha256(ARCHIVE.read_bytes()).hexdigest()}')
    return ARCHIVE


if __name__ == '__main__':
    build()
