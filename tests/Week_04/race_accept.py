import getpass
import json
import threading
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit, urlencode
import websocket

endpoint = input('Endpoint wss, khong token: ').strip()
u = urlsplit(endpoint)
assert u.scheme == 'wss' and u.netloc and not u.query and not u.fragment
assert not u.username and not u.password
oid = input('OrderId moi PLACED v1: ').strip()
tokens = [getpass.getpass('Token D001: '), getpass.getpass('Token D002: ')]
sockets = []
records = [None, None]
setup_error = None
barrier = threading.Barrier(2)

def stamp():
    return datetime.now(timezone.utc).isoformat()

def worker(i):
    request = {'action': 'updateOrderStatus', 'orderId': oid,
               'targetStatus': 'ACCEPTED', 'expectedVersion': 1,
               'requestId': 'W4-RACE-' + uuid.uuid4().hex}
    row = {'actorLabel': ['D001', 'D002'][i], 'request': request}
    try:
        barrier.wait(timeout=10)
        row['sentAt'] = stamp()
        sockets[i].send(json.dumps(request))
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline:
            sockets[i].settimeout(max(0.1, deadline-time.monotonic()))
            msg = json.loads(sockets[i].recv())
            if msg.get('type') == 'RESPONSE' and msg.get('requestId') == request['requestId']:
                row['receivedAt'] = stamp()
                row['response'] = msg
                break
        else:
            row['transportError'] = 'TIMEOUT'
    except Exception as exc:
        row['transportError'] = type(exc).__name__
    records[i] = row

try:
    for token in tokens:
        url = urlunsplit((u.scheme, u.netloc, u.path, urlencode({'token': token}), ''))
        sockets.append(websocket.create_connection(url, timeout=30, suppress_origin=True))
    threads = [threading.Thread(target=worker, args=(i,)) for i in range(2)]
    for t in threads: t.start()
    for t in threads: t.join()
except Exception as exc:
    setup_error = type(exc).__name__
finally:
    for sock in sockets:
        try:
            sock.close()
        except Exception:
            pass
    report = {'orderId': oid, 'attempts': records, 'setupError': setup_error,
              'note': 'Can doi chieu Orders va WorkflowTasks; QUEUED chua phai COMMITTED.'}
    dest = Path('evidence/TanPhat/Week_04/W4-TV1-04_RaceRequestsResponses.json')
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))

