"""Assignment-local handoffs and registered input scopes for targeted checks.

Global closure evidence deliberately keeps the existing Protocol 2.0 semantics.
"""
from pathlib import Path
import fnmatch
import subprocess
from vibe_protocol import (ProtocolError, canonical_digest, read_json, repository_path,
    sha256_bytes, atomic_write_json, discover_scoped_instructions, fingerprint_equal, _is_delivery_artifact)


def patterns_valid(patterns):
    if not isinstance(patterns, list) or not patterns:
        raise ProtocolError("non-empty repository-relative input patterns required")
    for value in patterns:
        if not isinstance(value, str) or not value or value.startswith('/') or ':' in value or '\\' in value or '..' in value.split('/'):
            raise ProtocolError(f"invalid scope pattern: {value!r}")
    return sorted(set(patterns))


def matches(path, patterns):
    return any(fnmatch.fnmatchcase(path, p) or (p.endswith('/**') and path == p[:-3]) for p in patterns)


def file_inventory(root):
    result = subprocess.run(['git', 'ls-files', '--cached', '--others', '--exclude-standard', '-z'],
        cwd=root, capture_output=True, check=True)
    return sorted(set(result.stdout.decode('utf-8').split('\0')) - {''})


def capture_scope(root, patterns, *, inventory=None):
    patterns = patterns_valid(patterns)
    names = set(name for name in (file_inventory(root) if inventory is None else inventory) if matches(name, patterns) and not _is_delivery_artifact(name))
    # Explicit absent paths must remain inputs (creation/deletion invalidates evidence).
    names.update(p for p in patterns if not any(c in p for c in '*?['))
    files = []
    for name in sorted(names):
        path = repository_path(root, name)
        files.append({'path': name, 'sha256': sha256_bytes(path.read_bytes()) if path.is_file() else None})
    data = {'algorithm': 'sha256', 'patterns': patterns, 'files': files}
    return {**data, 'digest': canonical_digest(data)}


def snapshot_ref(root, data):
    path = root / '.vibe/snapshots' / f"{canonical_digest(data)}.json"
    if path.exists():
        if read_json(path) != data: raise ProtocolError('immutable snapshot conflict')
    else: atomic_write_json(path, data, refuse_existing=True)
    return {'path': path.relative_to(root).as_posix(), 'sha256': sha256_bytes(path.read_bytes())}


def read_snapshot(root, reference):
    path = repository_path(root, reference['path'])
    if not reference['path'].startswith('.vibe/snapshots/') or sha256_bytes(path.read_bytes()) != reference['sha256']:
        raise ProtocolError('snapshot hash/path mismatch')
    return read_json(path)


def input_fingerprint(root, scope, *, context=None):
    """Include scoped content plus all build files, normative spec and instructions."""
    ledger = context.ledger if context else read_json(root / '.vibe/delivery-ledger.json')
    app_root = Path(ledger['appSpec']['root'])
    if not app_root.is_absolute(): app_root = root / app_root
    from vibe_protocol import compute_app_spec_fingerprint
    build_patterns = ['*.gradle', '*.gradle.kts', '*.properties', '**/*.gradle', '**/*.gradle.kts',
        '**/*.properties', 'gradle/**', 'build-logic/**', 'buildSrc/**', 'gradlew', 'gradlew.bat',
        '**/libs.versions.toml', '.gitignore', '**/.gitignore']
    data = {'scopeDigest': canonical_digest(scope),
        'inputs': capture_scope(root, [*scope['patterns'], *build_patterns], inventory=context.inventory if context else None),
        'appSpec': context.app_fingerprint if context else compute_app_spec_fingerprint(app_root),
        'instructions': context.instructions if context else discover_scoped_instructions(root)}
    return {**data, 'digest': canonical_digest(data)}


def registered_scope(root, scope_id):
    ledger = read_json(root / '.vibe/delivery-ledger.json')
    scope = ledger.get('verificationScopes', {}).get(scope_id)
    if not scope: raise ProtocolError(f'unknown verification scope: {scope_id}')
    return scope


def receipt_format_errors(receipt):
    errors = []
    kind = receipt.get('kind')
    if receipt.get('schemaVersion') != '2.0' or kind not in {'targeted', 'integration'}:
        errors.append('unsupported receipt protocol/kind')
    if receipt.get('executionStatus') not in {'completed', 'interrupted', 'workspace-changed'} or not isinstance(receipt.get('startWorkspaceFingerprint'), dict):
        errors.append('receipt requires executionStatus and startWorkspaceFingerprint')
    if kind == 'targeted':
        if not receipt.get('inputScopeId') or not all(isinstance(receipt.get(k), dict) and receipt[k].get('digest') for k in ('startInputFingerprint', 'inputFingerprint')):
            errors.append('unsupported targeted receipt format: inputScopeId and input fingerprints required')
    elif any(k in receipt for k in ('inputScopeId', 'startInputFingerprint', 'inputFingerprint')):
        errors.append('integration receipts require global inputs')
    return errors


def receipt_current(root, receipt, workspace):
    if receipt_format_errors(receipt): return False
    if receipt.get('inputScopeId'):
        if receipt.get('kind') != 'targeted': return False
        try:
            current = input_fingerprint(root, registered_scope(root, receipt['inputScopeId']))
            return fingerprint_equal(receipt.get('inputFingerprint'), current)
        except (ProtocolError, OSError, ValueError, KeyError): return False
    return receipt.get('kind') in {'integration', 'final'} and fingerprint_equal(receipt.get('workspaceFingerprint'), workspace)


def receipt_stable(receipt):
    if receipt_format_errors(receipt): return False
    if receipt.get('inputScopeId'):
        return fingerprint_equal(receipt.get('startInputFingerprint'), receipt.get('inputFingerprint'))
    return receipt.get('kind') in {'integration', 'final'} and fingerprint_equal(receipt.get('startWorkspaceFingerprint'), receipt.get('workspaceFingerprint'))


def assignment_errors(root, data, ledger):
    assignment = ledger.get('assignments', {}).get(data.get('assignmentId'))
    if not assignment: return ['unregistered scoped assignment']
    errors = []
    request = assignment.get('requestRef', {})
    try:
        if sha256_bytes(repository_path(root, request['path']).read_bytes()) != request['sha256']:
            errors.append('assignment request changed after registration')
    except (ProtocolError, OSError, KeyError): errors.append('assignment request is missing')
    for key in ('owner', 'allowedFiles', 'acceptanceScenarioIds', 'qualityGateIds', 'assignmentBaselineRef'):
        if data.get(key) != assignment.get(key): errors.append(f'assignment {key} mismatch')
    base = read_snapshot(root, assignment['assignmentBaselineRef'])
    current = capture_scope(root, assignment['allowedFiles'])
    result = data.get('resultScopeFingerprint')
    if result != current: errors.append('assignment-owned result is stale')
    before = {f['path']: f['sha256'] for f in base['files']}
    after = {f['path']: f['sha256'] for f in current['files']}
    changed = sorted(p for p in before.keys() | after.keys() if before.get(p) != after.get(p))
    if sorted(data.get('changedFiles', [])) != changed: errors.append('changedFiles do not match assignment delta')
    if assignment.get('inputScopeId'):
        expected = input_fingerprint(root, registered_scope(root, assignment['inputScopeId']))
        if data.get('inputFingerprint') != expected: errors.append('assignment input contracts are stale')
    return errors


def active_boundaries(ledger):
    execution = ledger.get('execution', {})
    ids = [i for pid in execution.get('activePackageIds', [])
           for i in ledger.get('workPackages', {}).get(pid, {}).get('acceptanceScenarioIds', []) + ledger.get('workPackages', {}).get(pid, {}).get('qualityGateIds', [])]
    ids += [execution.get('activeAcceptanceScenarioId'), execution.get('activeQualityGateId')]
    return [p for item in [*ledger.get('acceptanceScenarios', []), *ledger.get('qualityGates', [])]
        if item.get('id') in ids for p in item.get('fileBoundaries', [])]
