"""Current evidence is referenced once; handoff bytes remain immutable history."""
import xml.etree.ElementTree as ET
from vibe_protocol import ProtocolError, repository_path, canonical_digest, utc_now


def check_anchor(root, row):
    path = repository_path(root, row.get('path'))
    if not path.is_file(): raise ProtocolError(f'evidence file missing: {row.get("path")}')
    anchor = row.get('anchor')
    if anchor:
        if anchor.get('kind') != 'xml': raise ProtocolError('unsupported anchor kind')
        if not anchor.get('element') or not isinstance(anchor.get('attributes'), dict):
            raise ProtocolError('XML anchor requires element and namespace-aware attributes')
        try: tree = ET.parse(path)
        except ET.ParseError as exc: raise ProtocolError(f'invalid XML evidence: {exc}') from exc
        if not any(e.tag == anchor['element'] and all(e.get(k) == v for k, v in anchor['attributes'].items()) for e in tree.iter()):
            raise ProtocolError(f'XML anchor not found: {row["path"]}')
    else:
        symbol = row.get('symbol') or row.get('testName')
        if not symbol or symbol not in path.read_text(encoding='utf-8-sig'):
            raise ProtocolError(f'symbol/testName not found: {row["path"]}: {symbol}')


def register(root, ledger, row, kind, ids, source):
    check_anchor(root, row)
    coverage = row.get('coverage')
    if coverage is None:
        if len(ids) != 1: raise ProtocolError('multi-obligation handoff requires explicit evidence coverage')
        coverage = [{'obligationId': ids[0], 'surface': row['surface']}]
    items = {i['id']: i for i in ledger['acceptanceScenarios']+ledger['qualityGates']}
    if not coverage: raise ProtocolError('empty evidence coverage')
    for pair in coverage:
        if pair.get('obligationId') not in ids or pair.get('surface') != row['surface']:
            raise ProtocolError('evidence coverage escapes assignment/surface')
        if pair['surface'] not in items[pair['obligationId']]['requiredVerificationSurfaces'] and kind == 'testEvidence':
            raise ProtocolError('unknown evidence surface')
    record = {**row, 'coverage': coverage, 'kind': kind}
    eid = 'EV-' + canonical_digest(record)
    ledger.setdefault('evidence', {}).setdefault(eid, {**record, 'source': source})
    for pair in coverage:
        refs = items[pair['obligationId']].setdefault(kind, [])
        if eid not in refs: refs.append(eid)
    return eid


def resolve(ledger, refs):
    rows = []
    for ref in refs:
        if not isinstance(ref, str) or ref not in ledger.get('evidence', {}):
            raise ProtocolError(f'unknown evidence ID: {ref}')
        rows.append(ledger['evidence'][ref])
    return rows


def ingest(root, ledger, data, source):
    ids = data.get('acceptanceScenarioIds', []) + data.get('qualityGateIds', [])
    for kind in ('productionEvidence', 'testEvidence'):
        for row in data.get(kind, []): register(root, ledger, row, kind, ids, source)


def reconcile(root, ledger, request):
    if not request.get('reason') or not request.get('inspectionNote'): raise ProtocolError('reconciliation requires reason and inspectionNote')
    old = request.get('oldEvidenceIds', [])
    ids = request.get('obligationIds', [])
    if not old or not ids or any(e not in ledger.get('evidence', {}) for e in old): raise ProtocolError('unknown old evidence/obligations')
    new_ids = []
    for row in request.get('newEvidence', []):
        if row.get('kind') not in ('productionEvidence', 'testEvidence'): raise ProtocolError('invalid evidence kind')
        new_ids.append(register(root, ledger, row, row['kind'], ids, request.get('_requestRef')))
    if set(new_ids) & set(old): raise ProtocolError('replacement must not retire its own new evidence')
    for item in ledger['acceptanceScenarios'] + ledger['qualityGates']:
        if item['id'] not in ids: continue
        for kind in ('productionEvidence', 'testEvidence'):
            item[kind] = [ref for ref in item.get(kind, []) if ref not in old]
        surfaces = {pair['surface'] for row in resolve(ledger, item['testEvidence']) for pair in row['coverage'] if pair['obligationId'] == item['id']}
        if not item['productionEvidence'] or not set(item['requiredVerificationSurfaces']) <= surfaces:
            if item['status'] == 'verified': item['status'] = 'implemented-unverified'
    ledger.setdefault('evidenceHistory', []).append({
        'at': utc_now(), 'oldEvidenceIds': old, 'obligationIds': ids,
        'newEvidenceIds': new_ids,
        'reason': request['reason'], 'inspectionNote': request['inspectionNote']})


def work_item(value, prefix):
    row = dict(value) if isinstance(value, dict) else {'description': value}
    return {**row, 'id': row.get('id', prefix + canonical_digest(row))}
