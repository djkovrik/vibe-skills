#!/usr/bin/env python3
"""Adopt an explicitly approved AppSpec revision without discarding delivery history."""
import argparse
import importlib.util
import sys
import uuid
from pathlib import Path
from vibe_protocol import ProtocolError, atomic_write_json, decision_valid, update_ledger_atomic, utc_now, fingerprint_equal
from recovery_inputs import capture_reads


def reconcile(ledger, root, app_root, decision, classification="requirements"):
    if classification == "technical-paths":
        return reconcile_paths(ledger, root, app_root, decision)
    if not decision_valid(root, decision, "AppSpec", "spec-change"):
        raise ProtocolError("AppSpec revision requires an accepted spec-change decision scoped to AppSpec")
    spec = importlib.util.spec_from_file_location("reconcile_init", Path(__file__).with_name("init-delivery-ledger.py"))
    module = importlib.util.module_from_spec(spec); sys.modules[spec.name] = module; spec.loader.exec_module(module)
    fresh = module.create_ledger(app_root, root)
    if fingerprint_equal(fresh["appSpec"]["fingerprint"], ledger["appSpec"]["fingerprint"]):
        raise ProtocolError("AppSpec has not changed")
    history = root / ".vibe" / "history" / f"spec-{uuid.uuid4()}.json"
    atomic_write_json(history, ledger, refuse_existing=True)
    old_ids = {i["id"] for i in [*ledger["acceptanceScenarios"], *ledger["qualityGates"]]}
    new_ids = {i["id"] for i in [*fresh["acceptanceScenarios"], *fresh["qualityGates"]]}
    # Prose may change the meaning of any AC. Conservatively reopen all current
    # obligations, preserving every old state and receipt in the immutable archive.
    ledger.setdefault("specHistory", []).append({"path":history.relative_to(root).as_posix(), "decisionReference":decision,
        "added":sorted(new_ids-old_ids), "removed":sorted(old_ids-new_ids), "reopened":sorted(old_ids & new_ids), "at":utc_now()})
    if ledger.get("closureAudit", {}).get("requestPath"): ledger.setdefault("auditHistory", []).append(ledger["closureAudit"])
    previous_execution = ledger.get("execution", {})
    for key in ("appSpec", "canonicalInventory", "workspaceFingerprint", "acceptanceScenarios", "qualityGates", "execution", "closureManifest", "closureAudit", "appSpecDocument", "hostAvailability"):
        ledger[key] = fresh[key]
    ledger["execution"]["nextAction"] = "Reread the approved AppSpec revision and decision; select the first dependency-ready AC for revalidation."
    ledger["execution"]["requiredReads"] = sorted(set(previous_execution.get("requiredReads", [])) | {decision})
    if previous_execution.get("durableRequest"):
        ledger["execution"]["durableRequest"] = previous_execution["durableRequest"]
    ledger["execution"]["requiredReadHashes"] = capture_reads(root, ledger)
    ledger["updatedAt"] = utc_now()


def reconcile_paths(ledger, root, app_root, decision):
    import copy
    from vibe_protocol import validate_app_spec, compute_app_spec_fingerprint, compute_workspace_fingerprint, read_json, sha256_bytes
    if not decision_valid(root, decision, 'AppSpec', 'spec-change'): raise ProtocolError('accepted AppSpec decision required')
    new, errors, _ = validate_app_spec(app_root)
    if errors: raise ProtocolError('; '.join(errors))
    old = ledger.get('appSpecDocument')
    if not old: raise ProtocolError('original AppSpec document required')
    before, after = copy.deepcopy(old), copy.deepcopy(new)
    changes = []
    old_assets = {a['id']: a for a in before.get('assetRequirements', {}).get('items', [])}
    for asset in after.get('assetRequirements', {}).get('items', []):
        previous = old_assets.get(asset['id'])
        if not previous or len(previous['variants']) != len(asset['variants']): raise ProtocolError('not a technical path correction')
        for a, b in zip(previous['variants'], asset['variants']):
            if a['path'] != b['path']:
                if not b['path'].startswith('shared/compose/src/commonMain/composeResources/') or not (root / b['path']).is_file():
                    raise ProtocolError('corrected resource path must exist in shared/compose')
                changes.append({'assetId': asset['id'], 'oldPath': a['path'], 'newPath': b['path']})
                a['path'] = b['path']
    if before != after or not changes: raise ProtocolError('revision changes requirements; use requirements classification')
    fp = compute_app_spec_fingerprint(app_root)
    old_files = {f['path']:f['sha256'] for f in ledger['appSpec']['fingerprint']['files'] if f['path'] != 'app-spec.json'}
    if old_files != {f['path']:f['sha256'] for f in fp['files'] if f['path'] != 'app-spec.json'}:
        raise ProtocolError('normative prose/assets changed; use requirements classification')
    workspace = compute_workspace_fingerprint(root)
    spec_path = (app_root/'app-spec.json').resolve().relative_to(root).as_posix()
    def inputs(value): return {f['path']:f['sha256'] for f in value['workingFiles'] if f['path'] != spec_path}
    if inputs(workspace) != inputs(ledger['workspaceFingerprint']): raise ProtocolError('runtime inputs changed during technical correction')
    preserved = []
    for path in (root/'.vibe/receipts').glob('*.json'):
        receipt = read_json(path)
        if fingerprint_equal(receipt.get('workspaceFingerprint'), ledger['workspaceFingerprint']):
            preserved.append({'path':path.relative_to(root).as_posix(), 'sha256':sha256_bytes(path.read_bytes())})
    archive = root / '.vibe/history' / f'technical-{uuid.uuid4()}.json'
    atomic_write_json(archive, ledger, refuse_existing=True)
    ledger.setdefault('technicalReconciliations', []).append({'at':utc_now(), 'decisionReference':decision,
        'changes':changes, 'historyRef':archive.relative_to(root).as_posix(), 'previousWorkspace':ledger['workspaceFingerprint'], 'workspaceFingerprint':workspace,
        'previousAppSpec':ledger['appSpec']['fingerprint'], 'appSpecFingerprint':fp, 'preservedReceipts':preserved})
    ledger['appSpec']['fingerprint'] = fp; ledger['appSpecDocument'] = new
    ledger['workspaceFingerprint'] = workspace
    ledger['execution']['checkpoint']['workspaceFingerprint'] = workspace
    for item in ledger['acceptanceScenarios'] + ledger['qualityGates']:
        if 'asset-check' in item['requiredVerificationSurfaces'] and item['status'] == 'verified': item['status'] = 'implemented-unverified'
    ledger['closureManifest'] = None
    if ledger.get('closureAudit', {}).get('requestPath'): ledger.setdefault('auditHistory', []).append(ledger['closureAudit'])
    ledger['closureAudit'] = {'requestPath': None, 'auditPath': None}
    ledger['execution'].update(phase='reconciling', nextAction='Rerun asset-check and obtain a fresh audit; unchanged receipts retain provenance.')
    ledger['execution']['requiredReadHashes'] = capture_reads(root, ledger)
    ledger['updatedAt'] = utc_now()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", type=Path)
    parser.add_argument("--app-spec", type=Path, required=True)
    parser.add_argument("--decision-reference", required=True)
    parser.add_argument("--expected-ledger-digest", required=True)
    parser.add_argument("--classification", choices=("requirements", "technical-paths"), default="requirements")
    args = parser.parse_args(); root = args.project_root.resolve()
    app_root = args.app_spec.resolve() if args.app_spec.is_absolute() else (root / args.app_spec).resolve()
    try:
        result = update_ledger_atomic(root / ".vibe" / "delivery-ledger.json", args.expected_ledger_digest,
            lambda ledger: reconcile(ledger, root, app_root, args.decision_reference, args.classification))
        print(f"ledger-digest: {result['ledgerDigest']}"); return 0
    except (ProtocolError, OSError, ValueError) as exc: print(f"ERROR: {exc}"); return 1


if __name__ == "__main__": raise SystemExit(main())
