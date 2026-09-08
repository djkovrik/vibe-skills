"""Invocation-local evidence index. Never cache across workspace changes."""
from functools import cached_property
from pathlib import Path
from vibe_protocol import (read_json, compute_workspace_fingerprint, compute_app_spec_fingerprint,
    discover_scoped_instructions, fingerprint_equal, parse_time, valid_time, ProtocolError)
from scoped_evidence import input_fingerprint, receipt_format_errors, receipt_stable, file_inventory


class ValidationContext:
    def __init__(self, root, ledger=None):
        self.root = Path(root).resolve()
        self.ledger = ledger if ledger is not None else read_json(self.root / '.vibe/delivery-ledger.json')
        self.scopes = {}

    @cached_property
    def workspace(self): return compute_workspace_fingerprint(self.root)

    @cached_property
    def inventory(self): return file_inventory(self.root)

    @cached_property
    def app_root(self):
        path = Path(self.ledger['appSpec']['root'])
        return path if path.is_absolute() else self.root / path

    @cached_property
    def app(self): return read_json(self.app_root / 'app-spec.json')

    @cached_property
    def app_fingerprint(self): return compute_app_spec_fingerprint(self.app_root)

    @cached_property
    def instructions(self): return discover_scoped_instructions(self.root)

    def scope(self, scope_id):
        if scope_id not in self.scopes:
            scope = self.ledger.get('verificationScopes', {}).get(scope_id)
            if scope is None: raise ProtocolError(f'unknown verification scope: {scope_id}')
            self.scopes[scope_id] = input_fingerprint(self.root, scope, context=self)
        return self.scopes[scope_id]

    def current(self, receipt):
        if receipt_format_errors(receipt): return False
        if self.preserved(receipt): return True
        if receipt.get('inputScopeId'):
            return fingerprint_equal(receipt['inputFingerprint'], self.scope(receipt['inputScopeId']))
        return fingerprint_equal(receipt.get('workspaceFingerprint'), self.workspace)

    @cached_property
    def preserved_receipts(self):
        from vibe_protocol import decision_valid, sha256_bytes
        preserved = {}
        for revision in self.ledger.get('technicalReconciliations', []):
            if not fingerprint_equal(revision['workspaceFingerprint'], self.workspace) or not fingerprint_equal(revision['appSpecFingerprint'], self.app_fingerprint): continue
            if not decision_valid(self.root, revision['decisionReference'], 'AppSpec', 'spec-change'): continue
            for reference in revision['preservedReceipts']:
                candidate = self.receipts.get(reference['path'])
                if candidate and fingerprint_equal(candidate.get('workspaceFingerprint'), revision['previousWorkspace']) and sha256_bytes((self.root / reference['path']).read_bytes()) == reference['sha256']:
                    preserved[candidate['receiptId']] = candidate
        return preserved

    def preserved(self, receipt):
        return receipt == self.preserved_receipts.get(receipt.get('receiptId'))

    def coverage(self, receipt):
        preserved = self.preserved(receipt)
        return {(r['obligationId'], s) for r in receipt.get('coveredObligations', []) for s in r.get('surfaces', [])
                if not (preserved and s == 'asset-check')}

    @cached_property
    def receipts(self):
        return {p.relative_to(self.root).as_posix(): read_json(p)
                for p in sorted((self.root / '.vibe/receipts').glob('*.json'))}

    @cached_property
    def latest(self):
        latest = {}
        for ref, receipt in self.receipts.items():
            if not self.current(receipt) or not valid_time(receipt.get('completedAt')): continue
            failed = receipt.get('exitCode') != 0 or receipt.get('executionStatus') != 'completed' or not receipt_stable(receipt)
            key = (parse_time(receipt['completedAt']), failed)
            for pair in self.coverage(receipt):
                if pair not in latest or key > latest[pair][0]: latest[pair] = (key, ref, receipt)
        return latest
