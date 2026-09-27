import secrets
import logging
import math
import ipaddress
import socket
import sys
import threading
import time
import urllib.parse
from collections import deque
from pathlib import Path
from pairing import Registrations

from flask import Flask, jsonify, make_response, render_template, request
from flask_sock import Sock

RESOURCE_ROOT = Path(__file__).resolve().parent
DATA_ROOT = Path(sys.executable).resolve().parent if getattr(sys, 'frozen', False) else RESOURCE_ROOT
app = Flask(__name__, template_folder=str(RESOURCE_ROOT / 'templates'),
            static_folder=str(RESOURCE_ROOT / 'static'))
app.config['MAX_CONTENT_LENGTH'] = 3_000_000
app.config['SOCK_SERVER_OPTIONS'] = {'ping_interval': 20, 'max_message_size': 3_000_000}
sock = Sock(app)
CODE = f"{secrets.randbelow(1_000_000):06d}"
attempts = {}
registrations = Registrations(DATA_ROOT / '.state' / 'registrations.json')
lock = threading.RLock()
frame_ready = threading.Condition(lock)
queue = deque()
frame = None
version = 0
viewport = (1280, 800)
tabs = []
selected = None
bridge_seen = 0.0
bridge_error = ''
volume_state = {'available': False}




def phone_auth():
    return registrations.valid(request.cookies.get('remote_session', ''), 'phone')


def bridge_auth():
    return registrations.valid(request.headers.get('X-Remote-Token', '') or request.args.get('token', ''), 'bridge')


@app.before_request
def protect():
    host = request.host.split(':')[0]
    try:
        allowed_host = host == 'localhost' or ipaddress.ip_address(host).is_private
    except ValueError:
        allowed_host = False
    if not allowed_host: return jsonify(error='Use the local IP address shown on the PC'), 403
    if request.method == 'POST' and not isinstance(request.get_json(silent=True), dict):
        return jsonify(error='JSON object required'), 400
    if request.path.startswith('/bridge/') or request.path == '/ws/bridge':
        origin = request.headers.get('Origin', '')
        if origin and not origin.startswith('chrome-extension://'): return jsonify(error='Invalid bridge origin'), 403
        if request.remote_addr not in ('127.0.0.1', '::1') or (request.path != '/bridge/pair' and not bridge_auth()):
            return jsonify(error='Invalid bridge code'), 403
    elif not request.path.startswith('/static/') and request.path not in ('/', '/api/pair', '/api/session') and not phone_auth():
        return jsonify(error='接続コードを入力してください。'), 403
    if request.method == 'POST':
        if request.path.startswith('/bridge/'):
            return None
        if request.headers.get('Origin') != request.host_url.rstrip('/'):
            return jsonify(error='アクセス元が一致しません'), 403


@app.get('/')
def index():
    response = make_response(render_template('index.html'))
    response.headers['Cache-Control'] = 'no-store'
    response.headers['Referrer-Policy'] = 'no-referrer'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; connect-src 'self' ws: wss:"
    return response


@app.get('/api/session')
def session():
    authenticated=phone_auth()
    response=jsonify(authenticated=authenticated)
    return phone_cookie(response, request.cookies.get('remote_session')) if authenticated else response


def check_pairing_code():
    address = (request.remote_addr or 'unknown') + (':bridge' if request.path.startswith('/bridge/') else ':phone')
    now = time.monotonic()
    with lock:
        history = [t for t in attempts.get(address, []) if now-t < 60]
        attempts[address] = history
        if len(history) >= 5:
            return jsonify(error='1分後に再試行してください / Try again in one minute'), 429
        if not secrets.compare_digest(str((request.json or {}).get('code', '')).encode('utf-8'), CODE.encode('ascii')):
            attempts[address].append(now)
            return jsonify(error='接続コードが違います / Invalid code'), 403
        attempts.pop(address, None)
    return None


def phone_cookie(response, token):
    response.set_cookie('remote_session', token, httponly=True, samesite='Strict', max_age=365*86400)
    return response


@app.post('/api/pair')
def pair():
    error = check_pairing_code()
    if error is not None: return error
    return phone_cookie(jsonify(ok=True), registrations.issue('phone'))


@app.post('/bridge/pair')
def pair_bridge():
    error = check_pairing_code()
    if error is not None: return error
    return jsonify(token=registrations.issue('bridge'))


def forget_devices():
    global CODE, selected, frame, bridge_seen, volume_state, tabs
    registrations.revoke_all()
    with frame_ready:
        CODE = f"{secrets.randbelow(1_000_000):06d}"
        queue.clear(); attempts.clear(); tabs=[]; selected=None; frame=None; bridge_seen=0
        volume_state={'available':False}
        frame_ready.notify_all()
    return CODE


@app.post('/bridge/forget')
def forget_bridge():
    registrations.revoke(request.headers.get('X-Remote-Token', ''))
    return jsonify(ok=True)


@app.get('/api/tabs')
def list_tabs():
    with lock:
        return jsonify(tabs=tabs, selected=selected, connected=time.monotonic()-bridge_seen<5, error=bridge_error, volume=volume_state)


@app.post('/api/action')
def action():
    data = request.get_json(silent=True) or {}
    name = data.get('action')
    try:
        if name not in ('select','new','navigate','reload','back','forward','click','scroll','type','enter','volume','mute','playpause','seek','quality'):
            raise ValueError('不明な操作です')
        item = {'action': name}
        if name == 'select':
            item['id'] = int(data['id'])
        if name == 'navigate':
            value = str(data.get('value', '')).strip()[:2048]
            if not value:
                raise ValueError('URLまたは検索語を入力してください')
            item['value'] = value if value.startswith(('http://','https://')) else 'https://www.google.com/search?q='+urllib.parse.quote(value)
        if name == 'quality':
            if data.get('value') not in ('low', 'balanced', 'high', 'off'): raise ValueError('Invalid quality')
            item['value'] = data['value']
        if name == 'seek':
            item['value'] = max(-30, min(30, int(data['value'])))
        if name == 'volume':
            item['value'] = max(0, min(100, int(data['value'])))
        if name == 'type':
            item['value'] = str(data.get('value',''))[:2000]
        if name in ('click','scroll'):
            if not all(math.isfinite(float(data[k])) for k in ('x','y')): raise ValueError('Invalid coordinates')
            if name == 'scroll' and not math.isfinite(float(data['dy'])): raise ValueError('Invalid scroll')
            with lock:
                w,h = viewport
            item['x'] = min(max(float(data['x']),0),1)*w
            item['y'] = min(max(float(data['y']),0),1)*h
            if name == 'scroll': item['dy'] = max(-800,min(800,float(data['dy'])))
        with lock:
            if time.monotonic()-bridge_seen>5:
                return jsonify(error='Chrome拡張機能が接続されていません'), 503
            if name == 'volume' and queue and queue[-1].get('action') == 'volume':
                queue[-1]['value'] = item['value']
            elif name == 'scroll' and queue and queue[-1].get('action') == 'scroll':
                queue[-1]['dy'] = max(-800, min(800, queue[-1]['dy'] + item['dy']))
                queue[-1]['x'], queue[-1]['y'] = item['x'], item['y']
            else:
                if len(queue) >= 64: return jsonify(error='操作待ちです。少し待ってください / Please wait'), 429
                queue.append(item)
        return jsonify(ok=True)
    except (ValueError,KeyError,TypeError) as exc:
        return jsonify(error=str(exc)), 400


@app.post('/bridge/poll')
def bridge_poll():
    global tabs, selected, bridge_seen, bridge_error, volume_state
    data = request.get_json(silent=True) or {}
    with lock:
        bridge_seen = time.monotonic()
        if isinstance(data.get('tabs'), list): tabs = data['tabs']
        if 'selected' in data: selected = data['selected']
        bridge_error = str(data.get('error') or '')
        if isinstance(data.get('volume'), dict): volume_state = data['volume']
        return jsonify(queue.popleft() if queue else {})


@app.post('/bridge/selected')
def bridge_selected():
    global selected, frame, version, volume_state
    with lock:
        selected = request.json.get('id')
        volume_state = {'available': False}
        frame = None
        version += 1
    return jsonify(ok=True)


@sock.route('/ws/bridge')
def bridge_video(ws):
    global frame, version, viewport
    if request.remote_addr not in ('127.0.0.1', '::1') or not bridge_auth():
        return
    dimensions = None
    while True:
        incoming = ws.receive(timeout=1)
        if not bridge_auth(): break
        if incoming is None and ws.connected: continue
        if incoming is None:
            break
        if isinstance(incoming, str):
            try:
                info = __import__('json').loads(incoming)
                if info.get('type') == 'dimensions':
                    dimensions = (int(info['id']), float(info['width']), float(info['height']))
            except (ValueError, KeyError, TypeError):
                dimensions = None
            continue
        if isinstance(incoming, bytes) and incoming.startswith(b'\xff\xd8') and len(incoming)<2_000_000:
            with frame_ready:
                if dimensions and dimensions[0] == selected:
                    frame = incoming
                    if 0 < dimensions[1] <= 20000 and 0 < dimensions[2] <= 20000:
                        viewport = (dimensions[1], dimensions[2])
                    version += 1
                    frame_ready.notify_all()


@sock.route('/ws/phone')
def phone_video(ws):
    if not phone_auth() or request.headers.get('Origin') != request.host_url.rstrip('/'):
        return
    seen = -1
    while phone_auth():
        with frame_ready:
            frame_ready.wait_for(lambda: frame is not None and version != seen, timeout=1)
            current, seen = frame, version
        if not phone_auth(): break
        if current is None:
            continue
        try:
            ws.send(current)
        except Exception:
            break


def local_ip():
    s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    try:
        s.connect(('192.0.2.1',80))
        return s.getsockname()[0]
    except OSError:
        return '127.0.0.1'
    finally:s.close()


if __name__=='__main__':
    print('\nChrome Phone Remote 0.4.1 beta')
    print('PC Chrome extension and phone connection code:',CODE)
    print('Phone URL: http://'+local_ip()+':8765/')
    print('Registered devices reconnect automatically. Keep this window open.')
    print('Type R + Enter to forget ALL devices. Q + Enter to stop.\n')
    logging.getLogger('werkzeug').setLevel(logging.ERROR)
    from werkzeug.serving import make_server
    try:
        server=make_server('0.0.0.0', 8765, app, threaded=True)
        def console():
            while True:
                try: command=input().strip().lower()
                except EOFError: return
                if command=='r': print('All registrations removed. New pairing code:', forget_devices())
                elif command=='q': server.shutdown(); return
        threading.Thread(target=console,daemon=True).start()
        server.serve_forever()
    except KeyboardInterrupt:
        print('Stopped.')
