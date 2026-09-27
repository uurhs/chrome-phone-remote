"""Persistent registrations. Only token hashes are stored on disk."""
import hashlib
import json
import os
import secrets
import threading
from pathlib import Path

class Registrations:
    def __init__(self, path):
        self.path = Path(path)
        self.lock = threading.RLock()
        self.devices = {}
        if self.path.exists():
            data = json.loads(self.path.read_text(encoding='utf-8'))
            if data.get('version') != 1 or not isinstance(data.get('devices'), dict):
                raise ValueError('Invalid registration file. Restore it or remove .state with the server stopped.')
            self.devices = data['devices']

    def _save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix('.tmp')
        with open(temporary, 'w', encoding='utf-8') as stream:
            json.dump({'version': 1, 'devices': self.devices}, stream)
            stream.flush()
            os.fsync(stream.fileno())
        try: os.chmod(temporary, 0o600)
        except OSError: pass
        os.replace(temporary, self.path)

    def issue(self, kind):
        if kind not in ('phone', 'bridge'): raise ValueError('Invalid device type')
        token = secrets.token_urlsafe(32)
        with self.lock:
            self.devices[hashlib.sha256(token.encode()).hexdigest()] = kind
            self._save()
        return token

    def valid(self, token, kind):
        if not isinstance(token, str) or not token or len(token)>256: return False
        with self.lock:
            return self.devices.get(hashlib.sha256(token.encode()).hexdigest()) == kind

    def revoke(self, token):
        with self.lock:
            self.devices.pop(hashlib.sha256(token.encode()).hexdigest(), None)
            self._save()

    def revoke_all(self):
        with self.lock:
            self.devices.clear()
            self._save()
