#!/usr/bin/env python3
"""JSON-driven package/assignment/check workflow. Orchestrator owns ledger actions."""
import argparse
import importlib.util
import json
import re
import subprocess
import sys
import uuid
from pathlib import Path
from vibe_protocol import (ProtocolError, read_json, update_ledger_atomic, utc_now,
    compute_workspace_fingerprint, atomic_write_json, repository_path, paths_within_boundaries,
    workspace_drift_paths, discover_scoped_instructions, sha256_bytes)
from recovery_inputs import validate_request, capture_reads
from scoped_evidence import (capture_scope, snapshot_ref, read_snapshot, patterns_valid,
    input_fingerprint, registered_scope, active_boundaries, receipt_current, receipt_stable)

SCRIPTS = Path(__file__).resolve().parent


def load(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f'{name}.py')
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


def identifier(value):
    if not isinstance(value, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,100}', value):
        raise ProtocolError('invalid artifact ID')
    return value


def checkpoint(root, ledger, next_action):
    current = compute_workspace_fingerprint(root)
    execution = ledger.setdefault('execution', {})
    execution.update(phase='implementing', nextAction=next_action,
        scopedInstructions=discover_scoped_instructions(root),
        checkpoint={'checkpointId': f'CP-{uuid.uuid4()}', 'createdAt': utc_now(), 'workspaceFingerprint': current})
    errors = validate_request(root, ledger)
    if errors: raise ProtocolError('; '.join(errors))
    execution['requiredReadHashes'] = capture_reads(root, ledger)
    ledger.update(workspaceFingerprint=current, updatedAt=utc_now())


def mutate_request(root, request, ledger):
    action = request['action']
    items = {i['id']: i for i in [*ledger['acceptanceScenarios'], *ledger['qualityGates']]}
    if action == 'package':
        pid = identifier(request['packageId'])
        if pid in ledger.get('workPackages', {}): raise ProtocolError('package already registered')
        ids = request['acceptanceScenarioIds'] + request.get('qualityGateIds', [])
        if not ids or len(ids) != len(set(ids)) or any(i not in items for i in ids): raise ProtocolError('invalid package obligations')
        for other in ledger.get('workPackages', {}).values():
            if other.get('status') != 'integrated' and set(ids) & set(other['acceptanceScenarioIds'] + other.get('qualityGateIds', [])):
                raise ProtocolError('integrate overlapping obligations before another package')
        for i in ids:
            unmet = [d for d in items[i].get('dependsOnAcceptanceScenarioIds', []) if d not in ids and items[d]['status'] not in ('verified', 'waived') and not dependency_ready(root, ledger, d)]
            if unmet: raise ProtocolError(f'{i}: external dependencies not closed: {unmet}')
        boundaries = patterns_valid(request['fileBoundaries'])
        if not str(request.get('integrationGoal', '')).strip(): raise ProtocolError('package requires a reachable production integration goal')
        current = compute_workspace_fingerprint(root)
        for i in ids:
            if items[i]['status'] in ('verified', 'waived'): continue
            items[i].update(status='in-progress', owner=request['owner'], fileBoundaries=boundaries,
                baselineFingerprint=current, checkpointFingerprint=current, changedFiles=[],
                pendingChecks=items[i].get('pendingChecks', []), blockers=items[i].get('blockers', []),
                handoffRefs=items[i].get('handoffRefs', []), startedAt=items[i].get('startedAt', utc_now()), updatedAt=utc_now())
        ledger.setdefault('workPackages', {})[pid] = {**request, 'status': 'in-progress'}
        ledger['execution'].setdefault('activePackageIds', []).append(pid)
        ledger['execution'].update(activeAcceptanceScenarioId=None, activeQualityGateId=None)
    elif action == 'contract-ready':
        from evidence_registry import check_anchor
        item = items[request['obligationId']]
        checks = request['behavioralSurfaces']
        if not checks or not set(checks) <= set(item['requiredVerificationSurfaces']) or any('golden' in v for v in checks):
            raise ProtocolError('declare required behavioral dependency surfaces')
        for row in request['contractEvidence']: check_anchor(root, row)
        if not request['contractEvidence'] or not request.get('inspectionNote'): raise ProtocolError('accepted contract evidence required')
        item['dependencyReadiness'] = {k: request[k] for k in ('behavioralSurfaces', 'contractEvidence', 'inspectionNote')}
        if not dependency_ready(root, ledger, item['id']): raise ProtocolError('current successful behavioral checks required')
    elif action == 'scope':
        sid = identifier(request['scopeId'])
        if sid in ledger.get('verificationScopes', {}): raise ProtocolError('scope is immutable; register a new ID for changed inputs')
        if not str(request.get('dependencyRationale', '')).strip() or not request.get('toolchainIdentity'):
            raise ProtocolError('reviewed transitive dependency rationale and toolchain identity required')
        if request.get('modules'):
            from module_scope import resolve_modules
            request['patterns'], request['resolvedModules'] = resolve_modules(request['modules'], request.get('moduleGraph'))
        if any(p in {'**', '*', '**/*'} for p in request['patterns']) and not request.get('fallbackReason'):
            raise ProtocolError('whole-repository scope requires explicit fallbackReason')
        ledger.setdefault('verificationScopes', {})[sid] = {
            'patterns': patterns_valid(request['patterns']), 'dependencyRationale': request['dependencyRationale'],
            'toolchainIdentity': request['toolchainIdentity'],
            'resolvedModules': request.get('resolvedModules', []), 'fallbackReason': request.get('fallbackReason')}
    elif action == 'assign':
        aid = identifier(request['assignmentId'])
        if aid in ledger.get('assignments', {}): raise ProtocolError('assignment already registered')
        allowed = patterns_valid(request['allowedFiles'])
        ids = request['acceptanceScenarioIds'] + request.get('qualityGateIds', [])
        if not ids or any(i not in items for i in ids): raise ProtocolError('invalid assignment obligations')
        for i in ids:
            if items[i].get('status') not in ('in-progress', 'implemented-unverified'):
                raise ProtocolError('start the package/AC before assigning work')
            if not paths_within_boundaries(allowed, items[i].get('fileBoundaries', [])):
                raise ProtocolError('assignment exceeds registered package boundaries')
        # Conservative prefix comparison catches future files, not just today's inventory.
        for other in ledger.get('assignments', {}).values():
            if other.get('status') == 'returned': continue
            for a in allowed:
                for b in other['allowedFiles']:
                    pa, pb = re.split(r'[*?\[]', a)[0], re.split(r'[*?\[]', b)[0]
                    if pa.startswith(pb) or pb.startswith(pa): raise ProtocolError('assignment ownership overlaps active work')
        sid = request.get('inputScopeId')
        if sid: registered_scope(root, sid)
        packet = {k: request.get(k, []) for k in ('contractInputs', 'requiredReads', 'requestedCommands', 'acceptanceCriteria')}
        packet.update(assignmentId=aid, goal=request.get('goal', 'Implement assigned obligations within the registered boundary'),
                      obligationIds=ids, allowedFiles=allowed, forkTurns='none')
        packet_path = root / '.vibe/requests' / f'packet-{aid}.json'
        atomic_write_json(packet_path, packet, refuse_existing=True)
        ledger.setdefault('assignments', {})[aid] = {
            'assignmentId': aid, 'owner': request['owner'], 'allowedFiles': allowed,
            'acceptanceScenarioIds': request['acceptanceScenarioIds'], 'qualityGateIds': request.get('qualityGateIds', []),
            'assignmentBaselineRef': snapshot_ref(root, capture_scope(root, allowed)),
            'inputScopeId': sid, 'startedAt': utc_now(), 'status': 'active',
            'requestRef': request['_requestRef'], 'packetRef': packet_path.relative_to(root).as_posix()}
    elif action == 'bind':
        from check_jobs import bind_receipt
        bind_receipt(root, ledger, request['receiptRef'])
        return  # Binding must not checkpoint concurrent source changes.
    elif action == 'close':
        from closure_manifest import create
        create(root, ledger)
        ledger['updatedAt'] = utc_now()
        return
    elif action == 'availability':
        from delivery_readiness import unavailable_pairs
        ledger['hostAvailability'] = request['hostAvailability']
        requested = [r for r in request['hostAvailability']['surfaces'] if r.get('available') is False]
        if len(unavailable_pairs(ledger)) != len(requested): raise ProtocolError('only documented external/platform limitations may be unavailable')
    elif action == 'reconcile-evidence':
        from evidence_registry import reconcile
        reconcile(root, ledger, request)
    elif action == 'resolve-work':
        ids = set(request.get('resolvedIds', []))
        if not request.get('inspectionNote') or not ids: raise ProtocolError('resolved IDs and inspection note required')
        all_work = {v['id']: (key, v) for item in items.values() for key in ('pendingChecks', 'blockers') for v in item.get(key, [])}
        if not ids <= all_work.keys(): raise ProtocolError('unknown work ID')
        checks = [all_work[i][1] for i in ids if all_work[i][0] == 'pendingChecks']
        if checks:
            from validation_context import ValidationContext
            context = ValidationContext(root, ledger)
            receipt = context.receipts.get(request.get('receiptRef'))
            if not receipt or not context.current(receipt) or not receipt_stable(receipt) or receipt.get('exitCode') != 0 or receipt.get('executionStatus') != 'completed':
                raise ProtocolError('successful current receipt required to resolve checks')
            coverage = {(c['obligationId'], s) for c in receipt['coveredObligations'] for s in c['surfaces']}
            for check in checks:
                expected = {(c['obligationId'], s) for c in check.get('coveredObligations', []) for s in c['surfaces']}
                if not expected or not expected <= coverage: raise ProtocolError('receipt does not resolve requested check coverage')
        for item in items.values():
            for key in ('pendingChecks', 'blockers'):
                item[key] = [v for v in item.get(key, []) if v['id'] not in ids]
        ledger.setdefault('workResolutions', []).append({'at':utc_now(), 'ids':sorted(ids), 'inspectionNote':request['inspectionNote'], 'receiptRef':request.get('receiptRef')})
    elif action == 'integrate':
        package = ledger.get('workPackages', {}).get(request['packageId'])
        if not package: raise ProtocolError('unknown package')
        evidence = request.get('integrationEvidence', [])
        if not evidence: raise ProtocolError('entry point, navigation and restart evidence required')
        for row in evidence:
            path = repository_path(root, row['path'])
            if not path.is_file() or not row.get('symbol') or row['symbol'] not in path.read_text(encoding='utf-8-sig'):
                raise ProtocolError('invalid production integration evidence')
        if not {'entry-point', 'navigation', 'restart'} <= {r.get('role') for r in evidence}:
            raise ProtocolError('entry-point/navigation/restart evidence roles required')
        if not request['receiptRef'].startswith('.vibe/receipts/'): raise ProtocolError('integration receipt must be under .vibe/receipts')
        receipt = read_json(repository_path(root, request['receiptRef']))
        if receipt.get('exitCode') != 0 or receipt.get('executionStatus') != 'completed' or not receipt_current(root, receipt, compute_workspace_fingerprint(root)) or not receipt_stable(receipt):
            raise ProtocolError('successful current integration receipt required')
        covered = {c.get('obligationId') for c in receipt.get('coveredObligations', [])}
        if not covered.intersection(package['acceptanceScenarioIds']): raise ProtocolError('integration receipt must cover package obligations')
        log = receipt['log']
        if sha256_bytes(repository_path(root, log['path']).read_bytes()) != log['sha256']: raise ProtocolError('integration receipt log hash mismatch')
        package.update(status='integrated', integrationEvidence=evidence, integrationReceiptRef=request['receiptRef'])
        ledger['execution']['activePackageIds'] = [p for p in ledger['execution'].get('activePackageIds', []) if p != request['packageId']]
    else: raise ProtocolError(f'unknown ledger action: {action}')
    checkpoint(root, ledger, request.get('nextAction', 'Continue the active package; preserve pending verification.'))


def dependency_ready(root, ledger, obligation_id):
    from validation_context import ValidationContext
    from evidence_registry import check_anchor
    item = next(i for i in ledger['acceptanceScenarios'] if i['id'] == obligation_id)
    ready = item.get('dependencyReadiness')
    if not ready: return False
    try:
        for row in ready['contractEvidence']: check_anchor(root, row)
        context = ValidationContext(root, ledger)
        return all((obligation_id, surface) in context.latest and not context.latest[(obligation_id, surface)][0][1]
                   for surface in ready['behavioralSurfaces'])
    except (ProtocolError, OSError, ValueError, KeyError): return False


def handoff(root, request):
    ledger = read_json(root / '.vibe/delivery-ledger.json')
    assignment = ledger.get('assignments', {}).get(request['assignmentId'])
    if not assignment or assignment.get('status') != 'active': raise ProtocolError('active registered assignment required')
    baseline = read_snapshot(root, assignment['assignmentBaselineRef'])
    result = capture_scope(root, assignment['allowedFiles'])
    before = {f['path']: f['sha256'] for f in baseline['files']}; after = {f['path']: f['sha256'] for f in result['files']}
    hid = identifier(request.get('handoffId', f'HANDOFF-{uuid.uuid4()}'))
    data = {key: assignment[key] for key in ('assignmentId', 'owner', 'allowedFiles', 'acceptanceScenarioIds', 'qualityGateIds', 'assignmentBaselineRef', 'startedAt')}
    data.update(schemaVersion='2.0', evidenceMode='assignment', handoffId=hid, completedAt=utc_now(),
        resultScopeFingerprint=result, changedFiles=sorted(p for p in before.keys() | after.keys() if before.get(p) != after.get(p)))
    for key in ('productionEvidence', 'testEvidence', 'nonGradleChecks', 'requestedCommands', 'blockers'):
        data[key] = request.get(key, [])
    data['supersedes'] = request.get('supersedes', [])
    if assignment.get('inputScopeId'): data['inputFingerprint'] = input_fingerprint(root, registered_scope(root, assignment['inputScopeId']))
    issues = load('ingest-handoff').validate_handoff(data, root, compute_workspace_fingerprint(root))
    if issues: raise ProtocolError('; '.join(issues))
    path = root / '.vibe/handoffs' / f'{hid}.json'; atomic_write_json(path, data, refuse_existing=True)
    return {'handoffRef': path.relative_to(root).as_posix()}


def run(root, request):
    action = request['action']
    if action == 'handoff': return handoff(root, request)
    if action == 'check-batch':
        from check_queue import combine
        combined = combine(request['checks'])
        combined.update(action='check', jobId=request.get('jobId', f'CHECK-{uuid.uuid4()}'))
        path = root / '.vibe/requests' / f"batch-{combined['jobId']}.json"
        atomic_write_json(path, combined, refuse_existing=True)
        combined['_requestRef'] = {'path':path.relative_to(root).as_posix(), 'sha256':sha256_bytes(path.read_bytes())}
        return run(root, combined)
    if action == 'timing':
        from vibe_protocol import parse_time
        if request['category'] not in {'validation', 'agent-wait', 'repair', 'queue', 'execution', 'binding'}: raise ProtocolError('unknown timing category')
        if parse_time(request['completedAt']) < parse_time(request['startedAt']): raise ProtocolError('invalid timing interval')
        path = root / '.vibe/timing' / f"{identifier(request.get('timingId', str(uuid.uuid4())))}.json"
        atomic_write_json(path, request, refuse_existing=True)
        return {'timingRef':path.relative_to(root).as_posix()}
    if action == 'ingest':
        ledger = read_json(root / '.vibe/delivery-ledger.json')
        if not request.get('inspectionNote'): raise ProtocolError('inspect diff before ingest; supply inspectionNote')
        result = subprocess.run([sys.executable, str(SCRIPTS/'ingest-handoff.py'), str(root),
            str(repository_path(root, request['handoffRef'])), '--expected-ledger-digest', request.get('expectedLedgerDigest', ledger['ledgerDigest']),
            '--inspection-note', request['inspectionNote']], capture_output=True, text=True)
        if result.returncode: raise ProtocolError(result.stderr)
        return {'result': result.stdout.strip()}
    if action == 'retry-bind':
        from check_jobs import bind_completed
        state = bind_completed(root, request['receiptRef'], identifier(request['jobId']), request.get('administrativeTimeoutSeconds', 30))
        return {'receiptRef': request['receiptRef'], 'bindingStatus': state}
    if action == 'check':
        from check_jobs import event, bind_completed
        job_id = identifier(request.get('jobId', f'CHECK-{uuid.uuid4()}'))
        if (root / '.vibe/jobs' / f'{job_id}.json').exists():
            raise ProtocolError('check job already exists; resume/retry-bind without executing it again')
        event(root, job_id, 'queued')
        if request.get('runner') == 'gradle':
            process = subprocess.Popen(['pwsh', '-NoProfile', '-File', str(SCRIPTS/'run-gradle.ps1'),
                '-ProjectRoot', str(root), '-RequestPath', str(repository_path(root, request['_requestRef']['path']))],
                cwd=root, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            ref = None
            for line in process.stdout:
                print(line, end='', flush=True)
                if line.startswith('Running log: '): event(root, job_id, 'running', logPath=line[13:].strip())
                if line.startswith('Receipt: '):
                    ref = Path(line[9:].strip()).resolve().relative_to(root).as_posix()
                    event(root, job_id, 'receipt-written', receiptRef=ref)
            code = process.wait()
            if ref is None:
                event(root, job_id, 'runner-failed', exitCode=code)
                return {'exitCode': code or 1, 'jobId': job_id}
            receipt = read_json(root / ref)
        else:
            event(root, job_id, 'running')
            path, receipt = load('run-check').run_check(root, request['argv'], request['coveredObligations'],
                request.get('kind', 'targeted'), request.get('timeoutSeconds', 1800), request.get('inputScopeId'))
            ref = path.relative_to(root).as_posix()
        state = bind_completed(root, ref, job_id, request.get('administrativeTimeoutSeconds', 30))
        return {'receiptRef': ref, 'exitCode': receipt['exitCode'], 'executionStatus': receipt['executionStatus'],
                'bindingStatus': state, 'jobId': job_id}
    ledger = read_json(root / '.vibe/delivery-ledger.json')
    if action == 'bind':
        updated = update_ledger_atomic(root / '.vibe/delivery-ledger.json', request.get('expectedLedgerDigest', ledger['ledgerDigest']),
            lambda value: mutate_request(root, request, value))
        return {'ledgerDigest': updated['ledgerDigest'], 'bindingStatus': 'bound'}
    if action == 'close':
        import copy
        from closure_manifest import create
        from vibe_protocol import fingerprint_equal
        prepared = copy.deepcopy(ledger)
        create(root, prepared)
        def bind_closure(value):
            if not fingerprint_equal(compute_workspace_fingerprint(root), prepared['closureManifest']['workspaceFingerprint']):
                raise ProtocolError('workspace changed during closure preparation')
            value['closureManifest'] = prepared['closureManifest']
            value['execution'] = prepared['execution']
            value['updatedAt'] = utc_now()
        updated = update_ledger_atomic(root / '.vibe/delivery-ledger.json', request.get('expectedLedgerDigest', ledger['ledgerDigest']), bind_closure)
        return {'ledgerDigest': updated['ledgerDigest'], 'nextAction': updated['execution']['nextAction']}
    current = compute_workspace_fingerprint(root)
    previous = ledger.get('execution', {}).get('checkpoint', {}).get('workspaceFingerprint', {})
    drift = workspace_drift_paths(previous, current)
    if (not paths_within_boundaries(drift, active_boundaries(ledger))) and not request.get('reconcileDrift'):
        raise ProtocolError('inspect unexpected drift and supply reconcileDrift')
    def mutate(value):
        if request.get('reconcileDrift'):
            value.setdefault('reconciliations', []).append({'at': utc_now(), 'reason': request['reconcileDrift'], 'paths': drift})
        mutate_request(root, request, value)
    updated = update_ledger_atomic(root / '.vibe/delivery-ledger.json', request.get('expectedLedgerDigest', ledger['ledgerDigest']), mutate)
    return {'ledgerDigest': updated['ledgerDigest'], 'nextAction': updated['execution']['nextAction']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('project_root', type=Path); parser.add_argument('--request', required=True)
    args = parser.parse_args(); root = args.project_root.resolve()
    try:
        path = repository_path(root, args.request)
        request = read_json(path)
        request['_requestRef'] = {'path': path.relative_to(root).as_posix(), 'sha256': sha256_bytes(path.read_bytes())}
        result = run(root, request); print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result.get('exitCode', 0) == 0 and result.get('executionStatus', 'completed') == 'completed' else 1
    except (ProtocolError, OSError, ValueError, KeyError, TypeError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr); return 1


if __name__ == '__main__': raise SystemExit(main())
