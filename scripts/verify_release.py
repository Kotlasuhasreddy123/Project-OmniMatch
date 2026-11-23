"""Read-only installation checks; no sign-in, record changes or secret output."""
from __future__ import annotations
import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

PAGES = ('/', '/login/', '/session/', '/verify/', '/inbox/', '/timeline/',
         '/research/', '/preview/', '/models/', '/validation/', '/guide/',
         '/policies/', '/licenses/', '/credentials/')
PROTECTED = ('/inbox', '/timeline/DEMO-RELEASE-CHECK')


def request(url):
    started = time.perf_counter()
    try:
        with urlopen(url, timeout=30) as response:
            data = response.read()
            return response.status, data, round(time.perf_counter()-started, 3)
    except HTTPError as error:
        return error.code, b'', round(time.perf_counter()-started, 3)
    except (OSError, URLError):
        return 0, b'', round(time.perf_counter()-started, 3)


def verify(frontend, backend):
    checks=[]
    for page in PAGES:
        status, _, seconds=request(frontend.rstrip('/')+page)
        checks.append(dict(check='frontend '+page, expected=200, actual=status,
                           passed=status==200, seconds=seconds))
    for endpoint in PROTECTED:
        status, _, seconds=request(backend.rstrip('/')+'/api/v1'+endpoint)
        checks.append(dict(check='unauthenticated '+endpoint, expected=401,
                           actual=status, passed=status==401, seconds=seconds))
    for endpoint, fields in (('/health', ('qdrant_connected','whisper_loaded')),
                             ('/auth/config', ('configured',))):
        status, data, seconds=request(backend.rstrip('/')+'/api/v1'+endpoint)
        try:
            body=json.loads(data)
        except (ValueError, TypeError):
            body={}
        selected={field: body.get(field) for field in fields}
        checks.append(dict(check=endpoint, actual=selected,
                           passed=status==200 and all(value is True for value in selected.values()),
                           seconds=seconds))
    return dict(checked_at=datetime.now(timezone.utc).isoformat(),
                checks=checks, passed=all(row['passed'] for row in checks),
                scope='HTTP routes, loaded services, configured auth and unauthenticated denial only',
                live_sign_in_verified=False, microphone_verified=False,
                clinical_accuracy_validated=False)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--frontend', default='http://localhost:3000')
    parser.add_argument('--backend', default='http://localhost:8000')
    parser.add_argument('--output', type=Path, default=Path('output/installation-verification.json'))
    args=parser.parse_args()
    result=verify(args.frontend,args.backend)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))
    raise SystemExit(0 if result['passed'] else 1)
