import argparse
import getpass
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode
import websocket

p = argparse.ArgumentParser()
p.add_argument('--request', required=True)
p.add_argument('--out', required=True)
a = p.parse_args()
body = json.loads(Path(a.request).read_text(encoding='utf-8-sig'))
assert isinstance(body, dict) and isinstance(body.get('requestId'), str)
endpoint = input('Endpoint wss (khong kem token): ').strip()
u = urlsplit(endpoint)
assert u.scheme == 'wss' and u.netloc and not u.username and not u.password
params = [(k, v) for k, v in parse_qsl(u.query) if k != 'token']
params.append(('token', getpass.getpass('Token phien thu: ')))
url = urlunsplit((u.scheme, u.netloc, u.path, urlencode(params), ''))
result = {'sentAt': datetime.now(timezone.utc).isoformat(), 'request': body}
sock = None
try:
    sock = websocket.create_connection(url, timeout=30, suppress_origin=True)
    sock.send(json.dumps(body))
    deadline = time.monotonic() + 30
    while time.monotonic() < deadline:
        sock.settimeout(max(0.1, deadline - time.monotonic()))
        reply = json.loads(sock.recv())
        if reply.get('type') == 'RESPONSE' and reply.get('requestId') == body['requestId']:
            result['response'] = reply
            break
    else:
        result['transportError'] = 'TIMEOUT'
except Exception as exc:
    result['transportError'] = type(exc).__name__
finally:
    if sock:
        sock.close()
    dest = Path(a.out)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2))
