#!/usr/bin/env python3
"""Validate and atomically import an immutable specialist hand-off 2.0."""
from __future__ import annotations
import argparse
import hashlib
import sys
from datetime import datetime
from pathlib import Path
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
from vibe_protocol import ProtocolError, compute_workspace_fingerprint, paths_within_boundaries, read_json, update_ledger_atomic, utc_now, workspace_drift_paths
from scoped_evidence import assignment_errors, active_boundaries
from recovery_inputs import capture_reads

def nonempty(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())

def timestamp(value: object) -> bool:
    if not isinstance(value, str):
        return False
    try:
        datetime.fromisoformat(value.replace('Z', '+00:00'))
        return True
    except ValueError:
        return False

def validate_handoff(data: dict, root: Path, current: dict) -> list[str]:
    errors: list[str] = []
    if data.get('evidenceMode') != 'assignment' or 'baseWorkspaceFingerprint' in data or 'resultWorkspaceFingerprint' in data:
        return ['unsupported hand-off format: assignment evidence is required']
    if data.get('schemaVersion') != '2.0':
        errors.append('unsupported protocol: hand-off must be 2.0')
    for field in ('handoffId', 'assignmentId', 'owner', 'startedAt', 'completedAt', 'assignmentBaselineRef', 'resultScopeFingerprint', 'allowedFiles', 'changedFiles', 'productionEvidence', 'testEvidence', 'nonGradleChecks', 'requestedCommands', 'blockers'):
        if field not in data:
            errors.append(f'missing required field: {field}')
    for field in ('acceptanceScenarioIds', 'qualityGateIds'):
        if not isinstance(data.get(field), list):
            errors.append(f'{field} must be an array')
    if not data.get('acceptanceScenarioIds') and (not data.get('qualityGateIds')):
        errors.append('hand-off must cover at least one AC or gate')
    if not timestamp(data.get('startedAt')) or not timestamp(data.get('completedAt')) or data.get('startedAt', '') > data.get('completedAt', ''):
        errors.append('hand-off requires ordered RFC3339 timestamps')
    allowed, changed = (data.get('allowedFiles'), data.get('changedFiles'))
    if not isinstance(allowed, list) or not allowed:
        errors.append('allowedFiles must be non-empty')
    if not isinstance(changed, list):
        errors.append('changedFiles must be an array')
    if isinstance(allowed, list) and isinstance(changed, list) and (not paths_within_boundaries(changed, allowed)):
        errors.append('changedFiles escape allowedFiles boundaries')
    errors.extend(assignment_errors(root, data, read_json(root / '.vibe/delivery-ledger.json')))
    for collection in ('productionEvidence', 'testEvidence'):
        if not isinstance(data.get(collection), list):
            errors.append(f'{collection} must be an array')
            continue
        for index, item in enumerate(data[collection]):
            if not isinstance(item, dict) or not nonempty(item.get('path')) or (not nonempty(item.get('surface'))):
                errors.append(f'{collection}[{index}] requires path and surface')
            elif not (root / item['path']).is_file():
                errors.append(f'{collection}[{index}].path does not exist')
    for index, check in enumerate(data.get('nonGradleChecks', [])):
        if not isinstance(check, dict) or not isinstance(check.get('argv'), list) or (not isinstance(check.get('exitCode'), int)):
            errors.append(f'nonGradleChecks[{index}] requires argv and exitCode')
    if not isinstance(data.get('requestedCommands'), list):
        errors.append('requestedCommands must be an array')
    else:
        for index, command in enumerate(data['requestedCommands']):
            if not isinstance(command, dict) or not isinstance(command.get('argv'), list) or (not isinstance(command.get('tasks'), list)) or (not isinstance(command.get('coveredObligations'), list)):
                errors.append(f'requestedCommands[{index}] requires argv, tasks, and coveredObligations')
    return errors

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('project_root', type=Path)
    parser.add_argument('handoff', type=Path)
    parser.add_argument('--ledger', type=Path)
    parser.add_argument('--expected-ledger-digest', required=True)
    parser.add_argument('--inspection-note', default='')
    args = parser.parse_args()
    root, handoff_path = (args.project_root.resolve(), args.handoff.resolve())
    ledger_path = (args.ledger or root / '.vibe' / 'delivery-ledger.json').resolve()
    try:
        expected_dir = (root / '.vibe' / 'handoffs').resolve()
        if handoff_path.parent != expected_dir or handoff_path.suffix.lower() != '.json':
            raise ProtocolError('hand-off must be an immutable JSON file directly under .vibe/handoffs')
        data = read_json(handoff_path)
        current = compute_workspace_fingerprint(root)
        errors = validate_handoff(data, root, current)
        if errors:
            raise ProtocolError('; '.join(errors))
        digest = hashlib.sha256(handoff_path.read_bytes()).hexdigest()
        relative = handoff_path.relative_to(root).as_posix()

        def mutate(ledger: dict) -> None:
            issues = assignment_errors(root, data, ledger)
            if issues:
                raise ProtocolError('; '.join(issues))
            previous = ledger.get('execution', {}).get('checkpoint', {}).get('workspaceFingerprint', {})
            if previous.get('gitHead') != current.get('gitHead') or not paths_within_boundaries(workspace_drift_paths(previous, current), active_boundaries(ledger)):
                raise ProtocolError('unexpected workspace drift: inspect and checkpoint reconciliation before ingest')
            supersedes = data.get('supersedes', [])
            if supersedes and (not args.inspection_note.strip()):
                raise ProtocolError('inspect superseded handoffs before disposition')
            for old_ref in supersedes:
                from vibe_protocol import repository_path
                old_path = repository_path(root, old_ref)
                if old_path.parent != root / '.vibe/handoffs' or old_path == handoff_path:
                    raise ProtocolError('supersedes must name another handoff in this repository')
                old = read_json(old_path)
                if old.get('evidenceMode') != 'assignment' or 'baseWorkspaceFingerprint' in old or 'resultWorkspaceFingerprint' in old:
                    raise ProtocolError('cannot supersede an unsupported hand-off format')
                if old.get('assignmentId') != data['assignmentId']:
                    raise ProtocolError("cannot supersede another assignment's handoff")
                old_hash = hashlib.sha256(old_path.read_bytes()).hexdigest()
                if any((h.get('path') == old_ref for h in ledger.get('ingestedHandoffs', []))):
                    raise ProtocolError('supersedes is only for unimported attempts')
                ledger.setdefault('ingestedHandoffs', []).append({'handoffId': old['handoffId'], 'path': old_ref, 'sha256': old_hash, 'ingestedAt': utc_now(), 'supersededBy': relative, 'inspectionNote': args.inspection_note})
            if any((item.get('sha256') == digest for item in ledger.get('ingestedHandoffs', []))):
                raise ProtocolError('hand-off is already ingested')
            acs = {item.get('id'): item for item in ledger.get('acceptanceScenarios', [])}
            gates = {item.get('id'): item for item in ledger.get('qualityGates', [])}
            for item_id in data.get('acceptanceScenarioIds', []):
                if item_id not in acs:
                    raise ProtocolError(f'unknown acceptance scenario: {item_id}')
                entry = acs[item_id]
                boundaries = entry.get('fileBoundaries', data['allowedFiles'])
                if not paths_within_boundaries(data['changedFiles'], boundaries):
                    raise ProtocolError(f'hand-off conflicts with ledger boundaries for {item_id}')
                entry['handoffRefs'] = sorted(set(entry.get('handoffRefs', []) + [relative]))
                entry['productionEvidence'] = entry.get('productionEvidence', []) + data['productionEvidence']
                entry['testEvidence'] = entry.get('testEvidence', []) + data['testEvidence']
                entry['changedFiles'] = sorted(set(entry.get('changedFiles', []) + data['changedFiles']))
                entry['pendingChecks'] = entry.get('pendingChecks', []) + data['requestedCommands']
                entry['blockers'] = entry.get('blockers', []) + data['blockers']
                entry['status'] = 'implemented-unverified' if not data['blockers'] else 'in-progress'
                if entry['blockers'] or any((a.get('status') != 'returned' and a.get('assignmentId') != data['assignmentId'] and (item_id in a.get('acceptanceScenarioIds', [])) for a in ledger.get('assignments', {}).values())):
                    entry['status'] = 'in-progress'
                entry['updatedAt'] = utc_now()
            for item_id in data.get('qualityGateIds', []):
                if item_id not in gates:
                    raise ProtocolError(f'unknown quality gate: {item_id}')
                gate = gates[item_id]
                if not gate.get('fileBoundaries') or not paths_within_boundaries(data['changedFiles'], gate['fileBoundaries']):
                    raise ProtocolError(f'hand-off conflicts with gate assignment boundaries for {item_id}')
                gates[item_id]['productionEvidence'] += data['productionEvidence']
                gates[item_id]['testEvidence'] += data['testEvidence']
                gate['handoffRefs'] = sorted(set(gate.get('handoffRefs', []) + [relative]))
                gate['pendingChecks'] = gate.get('pendingChecks', []) + data['requestedCommands']
                gate['blockers'] = gate.get('blockers', []) + data['blockers']
                gate['status'] = 'implemented-unverified' if not data['blockers'] else 'in-progress'
                if gate['blockers'] or any((a.get('status') != 'returned' and a.get('assignmentId') != data['assignmentId'] and (item_id in a.get('qualityGateIds', [])) for a in ledger.get('assignments', {}).values())):
                    gate['status'] = 'in-progress'
                gate['updatedAt'] = utc_now()
            ledger.setdefault('ingestedHandoffs', []).append({'handoffId': data['handoffId'], 'path': relative, 'sha256': digest, 'ingestedAt': utc_now(), 'inspectionNote': args.inspection_note})
            ledger['assignments'][data['assignmentId']]['status'] = 'returned'
            ledger['execution']['checkpoint'] = {'checkpointId': data['handoffId'], 'createdAt': utc_now(), 'workspaceFingerprint': current}
            ledger['execution']['requiredReadHashes'] = capture_reads(root, ledger)
            ledger['workspaceFingerprint'] = current
            ledger['execution']['phase'] = 'reconciling'
            ledger['execution']['nextAction'] = 'Inspect the imported diff and run the requested targeted checks.'
            ledger['updatedAt'] = utc_now()
        ledger = update_ledger_atomic(ledger_path, args.expected_ledger_digest, mutate)
    except (ProtocolError, OSError, ValueError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        return 1
    print(f"ingested: {data['handoffId']} ({digest})")
    print(f"ledger-digest: {ledger['ledgerDigest']}")
    return 0
if __name__ == '__main__':
    raise SystemExit(main())
