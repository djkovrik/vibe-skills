"""Bind independently reviewed receipts without executing a post-audit matrix."""
import importlib.util
import sys
from pathlib import Path
from vibe_protocol import (ProtocolError, read_json, sha256_bytes, repository_path,
    fingerprint_equal, compute_workspace_fingerprint, utc_now)


def audit_validator():
    path = Path(__file__).resolve().parents[2] / 'vibe-acceptance-auditor/scripts/validate-closure-audit.py'
    spec = importlib.util.spec_from_file_location('closure_manifest_audit', path)
    module = importlib.util.module_from_spec(spec); sys.modules[spec.name] = module; spec.loader.exec_module(module)
    return module


def create(root, ledger):
    binding = ledger['closureAudit']
    request_path = repository_path(root, binding['requestPath'])
    path = repository_path(root, binding['auditPath'])
    data = read_json(path)
    app_root = Path(ledger['appSpec']['root'])
    if not app_root.is_absolute(): app_root = root / app_root
    errors = audit_validator().validate(data, app_root, root, request_path)
    if errors or data.get('verdict') != 'PASS': raise ProtocolError('; '.join(errors) or 'current audit PASS required')
    refs = sorted({c['receiptRef'] for c in data['checks']})
    ledger['closureManifest'] = {'createdAt': utc_now(), 'auditPath': binding['auditPath'],
        'auditSha256': sha256_bytes(path.read_bytes()), 'requestSha256': sha256_bytes(request_path.read_bytes()),
        'workspaceFingerprint': compute_workspace_fingerprint(root), 'appSpecFingerprint': data['appSpecFingerprint'],
        'receipts': [{'path': ref, 'sha256': sha256_bytes(repository_path(root, ref).read_bytes())} for ref in refs]}
    ledger['execution'].update(phase='complete', nextAction='Render reports and run closure validation; resolve external surfaces when available.')


def validate(root, ledger, workspace, app_fingerprint, receipts, required_pairs):
    manifest = ledger.get('closureManifest')
    if not manifest: return ['closure manifest required']
    errors = []
    from validation_context import ValidationContext
    context = ValidationContext(root, ledger)
    try:
        binding = ledger['closureAudit']
        if manifest['auditPath'] != binding['auditPath']: errors.append('manifest audit binding mismatch')
        path = repository_path(root, manifest['auditPath'])
        if sha256_bytes(path.read_bytes()) != manifest['auditSha256']: errors.append('manifest audit hash mismatch')
        if sha256_bytes(repository_path(root, binding['requestPath']).read_bytes()) != manifest['requestSha256']: errors.append('manifest request hash mismatch')
        if not fingerprint_equal(manifest['workspaceFingerprint'], workspace) or not fingerprint_equal(manifest['appSpecFingerprint'], app_fingerprint): errors.append('closure manifest stale')
        coverage = set()
        audit = read_json(path)
        if {r['path'] for r in manifest['receipts']} != {c['receiptRef'] for c in audit['checks']}: errors.append('manifest receipt set differs from audit')
        for ref in manifest['receipts']:
            if sha256_bytes(repository_path(root, ref['path']).read_bytes()) != ref['sha256']: errors.append('manifest receipt hash mismatch')
            receipt = receipts.get(ref['path'])
            if not receipt or receipt['kind'] != 'integration' or receipt['exitCode'] != 0 or receipt['executionStatus'] != 'completed' or not context.current(receipt) or not fingerprint_equal(receipt['startWorkspaceFingerprint'], receipt['workspaceFingerprint']):
                errors.append('manifest requires successful current integration receipts'); continue
            coverage.update(context.coverage(receipt))
        if not required_pairs <= coverage: errors.append('closure manifest coverage incomplete')
    except (ProtocolError, OSError, ValueError, KeyError, TypeError) as exc: errors.append(f'invalid closure manifest: {exc}')
    return errors
