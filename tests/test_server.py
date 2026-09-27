import json,sys,tempfile,threading,unittest,urllib.request,zipfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import app as remote
import build_release
class ServerTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);remote.registrations=remote.Registrations(Path(self.tmp.name)/'registrations.json');self.c=remote.app.test_client();remote.attempts.clear();remote.queue.clear();remote.bridge_seen=0
        self.h={'Origin':'http://localhost'}
    def pair(self):return self.c.post('/api/pair',json={'code':remote.CODE},headers=self.h)
    def bridge(self):
        token=self.c.post('/bridge/pair',json={'code':remote.CODE}).json['token']
        return self.c.post('/bridge/poll',json={'tabs':[],'selected':3},headers={'X-Remote-Token':token},environ_base={'REMOTE_ADDR':'127.0.0.1'})
    def test_auth(self):
        self.assertEqual(self.c.get('/api/tabs').status_code,403)
        self.assertEqual(self.pair().status_code,200)
        self.assertTrue(self.c.get('/api/session').json['authenticated'])
        self.assertEqual(self.c.post('/api/action',json={'action':'reload'},headers={'Origin':'http://evil.example'}).status_code,403)
        self.assertEqual(self.c.get('/',headers={'Host':'evil.example'}).status_code,403)
    def test_assets(self):
        r=self.c.get('/');self.assertIn(b'id="volume"',r.data)
        self.assertIn('blob:',r.headers['Content-Security-Policy'])
        asset=self.c.get('/static/remote.js');self.assertEqual(asset.status_code,200);asset.close()
    def test_commands(self):
        self.pair();self.bridge()
        self.assertEqual(self.c.post('/api/action',json=[],headers=self.h).status_code,400)
        for v in (10,20,30):self.assertEqual(self.c.post('/api/action',json={'action':'volume','value':v},headers=self.h).status_code,200)
        self.assertEqual(len(remote.queue),1);self.assertEqual(remote.queue[0]['value'],30)
        self.assertEqual(self.c.post('/api/action',json={'action':'quality','value':'invalid'},headers=self.h).status_code,400)
        self.assertEqual(self.c.post('/api/action',json={'action':'click','x':'nan','y':0},headers=self.h).status_code,400)
    def test_release(self):
        with tempfile.TemporaryDirectory() as d:
            path=build_release.build(Path(d)/'release.zip')
            with zipfile.ZipFile(path) as z:
                names=z.namelist();self.assertTrue(any(n.endswith('docs/USER_GUIDE_EN.md') for n in names))
                self.assertFalse(any('/.venv/' in n or '/chrome-profile/' in n or '/__pycache__/' in n or '/.state/' in n for n in names))
class RelayTests(unittest.TestCase):
    def test_frame(self):
        import websocket
        from werkzeug.serving import make_server
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup)
        remote.registrations=remote.Registrations(Path(temp.name)/'registrations.json')
        server=make_server('127.0.0.1',0,remote.app,threaded=True)
        threading.Thread(target=server.serve_forever,daemon=True).start()
        base=f'http://127.0.0.1:{server.server_port}'
        def post(path,data,headers):
            return urllib.request.urlopen(urllib.request.Request(base+path,json.dumps(data).encode(),headers={'Content-Type':'application/json',**headers}))
        phone=bridge=None
        try:
            remote.attempts.clear()
            r=post('/api/pair',{'code':remote.CODE},{'Origin':base});cookie=r.headers['Set-Cookie'].split(';')[0]
            token=json.load(post('/bridge/pair',{'code':remote.CODE},{}))['token']
            post('/bridge/selected',{'id':5},{'X-Remote-Token':token})
            address=base.replace('http:','ws:')
            phone=websocket.create_connection(address+'/ws/phone',origin=base,header={'Cookie':cookie},timeout=3)
            bridge=websocket.create_connection(address+'/ws/bridge?token='+token,origin='chrome-extension://test',timeout=3)
            bridge.send(json.dumps({'type':'dimensions','id':5,'width':1000,'height':700}))
            sample=b'\xff\xd8relay-test\xff\xd9';bridge.send_binary(sample)
            self.assertEqual(phone.recv(),sample)
            remote.forget_devices()
            try: self.assertEqual(phone.recv(), '')
            except websocket.WebSocketConnectionClosedException: pass
        finally:
            if phone:phone.shutdown()
            if bridge:bridge.shutdown()
            server.shutdown()
if __name__=='__main__':unittest.main()
