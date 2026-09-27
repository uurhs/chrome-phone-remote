"""Create an isolated environment once; keep normal startup quiet."""
from pathlib import Path
import hashlib
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parent

def main():
    if sys.version_info < (3, 10):
        raise RuntimeError('Python 3.10 or newer is required.')
    env = ROOT / '.venv'
    python = env / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
    if not python.exists():
        print('Preparing Python environment. Please wait...')
        subprocess.run([sys.executable, '-m', 'venv', str(env)], check=True)
    requirements = ROOT / 'requirements.txt'
    digest = hashlib.sha256(requirements.read_bytes()).hexdigest()
    stamp = env / 'requirements.sha256'
    if not stamp.exists() or stamp.read_text() != digest:
        print('Installing components. Internet is required for this step...')
        result = subprocess.run([str(python), '-m', 'pip', 'install', '--disable-pip-version-check', '-r', str(requirements)], capture_output=True, text=True)
        if result.returncode:
            print(result.stdout, result.stderr)
            raise RuntimeError('Installation failed. See docs/USER_GUIDE_EN.md or docs/USER_GUIDE_JA.md.')
        stamp.write_text(digest)
    return subprocess.call([str(python), str(ROOT / 'app.py')], cwd=ROOT)

if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, RuntimeError, subprocess.SubprocessError) as exc:
        print('Startup error:', exc)
        sys.exit(1)
