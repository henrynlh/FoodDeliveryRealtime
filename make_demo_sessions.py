"""Generate local-only app demo tokens, never AWS credentials."""
import json
import secrets
from pathlib import Path
r=Path(__file__).parent/'config/LeHuy/Week_02'
r.mkdir(parents=True,exist_ok=True)
sessions={secrets.token_urlsafe(32):{'id':actor,'role':role} for actor,role in
 [('C001','CUSTOMER'),('C002','CUSTOMER'),('D001','DRIVER'),('D002','DRIVER')]}
p=r/'demo_sessions.local.json'
if p.exists():
 raise SystemExit('Local session file already exists; do not overwrite active tokens.')
p.write_text(json.dumps(sessions,indent=2),encoding='utf-8')
print('Created '+str(p)+'. Keep private and do not commit.')
