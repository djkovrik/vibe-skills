"""Durable check lifecycle; command outcome and administrative outcome are separate."""
import json
import subprocess
import sys
import time
from pathlib import Path
from vibe_protocol import atomic_write_json, read_json, utc_now, sha256_bytes, ProtocolError


def event(root, job_id, stage, **fields):
    path = root / '.vibe/jobs' / f'{job_id}.json'
    data = read_json(path) if path.exists() else {'jobId': job_id, 'events': []}
    data.update(fields, stage=stage)
    data['events'].append({'stage': stage, 'at': utc_now(), **fields})
    atomic_write_json(path, data)
    print(json.dumps({'jobId': job_id, 'stage': stage, **fields}), flush=True)
    return data


def bind_completed(root, ref, job_id, timeout=30):
    """A retry only invokes bind; it never has the original check argv."""
    if not 0 < timeout <= 300: raise ProtocolError('administrative timeout must be in (0, 300]')
    event(root, job_id, 'receipt-written', receiptRef=ref)
    event(root, job_id, 'binding')
    started = time.monotonic()
    request = root / '.vibe/requests' / f'bind-{job_id}.json'
    atomic_write_json(request, {'action': 'bind', 'receiptRef': ref})
    try:
        result = subprocess.run([sys.executable, str(Path(__file__).with_name('delivery-work.py')),
            str(root), '--request', request.relative_to(root).as_posix()], capture_output=True, text=True, timeout=timeout)
        if result.returncode: raise ProtocolError(result.stderr.strip() or result.stdout.strip())
    except (subprocess.TimeoutExpired, OSError, ProtocolError) as exc:
        event(root, job_id, 'binding-pending', receiptRef=ref, error=str(exc),
              durationSeconds=time.monotonic()-started)
        return 'binding-pending'
    event(root, job_id, 'bound', receiptRef=ref, durationSeconds=time.monotonic()-started)
    return 'bound'


def bind_receipt(root, ledger, ref):
    from vibe_protocol import repository_path
    from scoped_evidence import receipt_format_errors
    path = repository_path(root, ref)
    if path.parent != root / '.vibe/receipts': raise ProtocolError('receipt path required')
    receipt = read_json(path)
    errors = receipt_format_errors(receipt)
    if errors: raise ProtocolError('; '.join(errors))
    digest = sha256_bytes(path.read_bytes())
    existing = ledger.setdefault('boundReceipts', {}).get(ref)
    if existing and existing != digest: raise ProtocolError('bound receipt hash changed')
    log = receipt['log']
    if sha256_bytes(repository_path(root, log['path']).read_bytes()) != log['sha256']:
        raise ProtocolError('receipt log hash mismatch')
    items = {i['id']: i for i in ledger['acceptanceScenarios']+ledger['qualityGates']}
    from vibe_protocol import verification_surface_map
    from validation_context import ValidationContext
    known = verification_surface_map(ValidationContext(root, ledger).app)
    for coverage in receipt['coveredObligations']:
        if coverage['obligationId'] not in known or not set(coverage['surfaces']) <= set(known[coverage['obligationId']]): raise ProtocolError('unknown receipt obligation/surface')
        if coverage['obligationId'] not in items: continue
        item = items[coverage['obligationId']]
        if not set(coverage['surfaces']) <= set(item['requiredVerificationSurfaces']):
            raise ProtocolError('unknown receipt surface')
        item['receiptRefs'] = sorted(set(item.get('receiptRefs', []) + [ref]))
    ledger['boundReceipts'][ref] = digest
    ledger['updatedAt'] = utc_now()
