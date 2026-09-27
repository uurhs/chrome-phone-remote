"""Start the packaged server on a Windows runner and check its real HTTP routes."""
from pathlib import Path
import os
import subprocess
import time
import urllib.request


root = Path(__file__).resolve().parent
exe = root / 'dist' / 'ChromePhoneRemote' / 'ChromePhoneRemote.exe'
environment = dict(os.environ, PYTHONUNBUFFERED='1')
process = subprocess.Popen([str(exe)], cwd=exe.parent, stdin=subprocess.PIPE,
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                           text=True, env=environment)
try:
    for attempt in range(60):
        if process.poll() is not None:
            raise RuntimeError(f'Executable exited early with code {process.returncode}')
        try:
            with urllib.request.urlopen('http://127.0.0.1:8765/', timeout=1) as response:
                assert response.status == 200
                assert b'Chrome Phone Remote' in response.read()
            with urllib.request.urlopen('http://127.0.0.1:8765/api/session', timeout=1) as response:
                assert b'"authenticated":false' in response.read()
            break
        except (OSError, AssertionError):
            time.sleep(0.5)
    else:
        raise RuntimeError('Packaged server did not respond within 30 seconds')
    print('Packaged executable and HTTP routes work.')
finally:
    if process.poll() is None:
        process.stdin.write('q\n')
        process.stdin.flush()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.terminate()
            process.wait(timeout=5)
