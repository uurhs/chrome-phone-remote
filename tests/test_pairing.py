import json
import tempfile
import unittest
from pathlib import Path
import app as remote
from pairing import Registrations

class PersistentPairingTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path=Path(self.temp.name)/'registrations.json'
        remote.registrations=Registrations(self.path)
        remote.attempts.clear()
        self.client=remote.app.test_client()
        self.origin={'Origin':'http://localhost'}

    def test_phone_and_extension_survive_store_reload(self):
        self.client.post('/api/pair',json={'code':remote.CODE},headers=self.origin)
        token=self.client.post('/bridge/pair',json={'code':remote.CODE}).json['token']
        # Simulate a new process reading the same file and issuing a different initial code.
        remote.registrations=Registrations(self.path)
        remote.CODE='987654'
        self.assertTrue(self.client.get('/api/session').json['authenticated'])
        self.assertEqual(self.client.post('/bridge/poll',json={},headers={'X-Remote-Token':token}).status_code,200)
        self.assertNotIn(token,self.path.read_text())
        self.assertFalse(remote.registrations.valid(token,'phone'))

    def test_revoke_all_invalidates_both_types_and_persists(self):
        self.client.post('/api/pair',json={'code':remote.CODE},headers=self.origin)
        token=self.client.post('/bridge/pair',json={'code':remote.CODE}).json['token']
        remote.forget_devices()
        self.assertFalse(self.client.get('/api/session').json['authenticated'])
        self.assertEqual(self.client.post('/bridge/poll',json={},headers={'X-Remote-Token':token}).status_code,403)
        self.assertFalse(Registrations(self.path).valid(token,'bridge'))

    def test_bridge_pairing_is_loopback_only_and_rate_limited(self):
        r=self.client.post('/bridge/pair',json={'code':remote.CODE},environ_base={'REMOTE_ADDR':'192.168.1.50'})
        self.assertEqual(r.status_code,403)
        for _ in range(5):
            self.assertEqual(self.client.post('/bridge/pair',json={'code':'wrong'}).status_code,403)
        self.assertEqual(self.client.post('/bridge/pair',json={'code':remote.CODE}).status_code,429)

    def test_extension_forget_does_not_forget_phone(self):
        self.client.post('/api/pair',json={'code':remote.CODE},headers=self.origin)
        token=self.client.post('/bridge/pair',json={'code':remote.CODE}).json['token']
        self.assertEqual(self.client.post('/bridge/forget',json={},headers={'X-Remote-Token':token}).status_code,200)
        self.assertFalse(remote.registrations.valid(token,'bridge'))
        self.assertTrue(self.client.get('/api/session').json['authenticated'])
