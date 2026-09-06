from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path

AUDITOR = Path(__file__).resolve().parents[1]
DEVELOPER_SCRIPTS = AUDITOR.parent / "vibe-developer" / "scripts"
sys.path.insert(0, str(DEVELOPER_SCRIPTS))
from vibe_protocol import canonical_inventory, compute_app_spec_fingerprint, compute_workspace_fingerprint
sys.path.insert(0, str(AUDITOR.parent / "vibe-developer" / "tests"))
from protocol_fixture_support import decision_fixture, launch_fixture, coverage_fixture, audit_receipt_fixture

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path); module = importlib.util.module_from_spec(spec); sys.modules[name] = module; spec.loader.exec_module(module); return module
VALIDATOR = load("audit_validator_20", AUDITOR / "scripts" / "validate-closure-audit.py")

class AuditProtocol20Tests(unittest.TestCase):
    def setUp(self):
        self.scratch = Path(__file__).resolve().parent / ".test-workspaces"; self.scratch.mkdir(exist_ok=True)
        self.root = (self.scratch / uuid.uuid4().hex).resolve(); self.root.mkdir()
        fixture = AUDITOR / "assets" / "behavioral-fixtures" / "positive-end-to-end"
        shutil.copytree(fixture / "app-spec", self.root / "app-spec"); shutil.copytree(fixture / "project", self.root / "project")
        (self.root / "app-spec" / "assets").mkdir(exist_ok=True); (self.root / "app-spec" / "assets" / "pixel.bin").write_bytes(b"x")
        decision_fixture(self.root, ["AC-001", "Preference:update", "QG-001", "QG-002", "QG-003"])
        subprocess.run(["git", "-C", str(self.root), "init"], check=True, capture_output=True); subprocess.run(["git", "-C", str(self.root), "config", "user.email", "x@example.test"], check=True); subprocess.run(["git", "-C", str(self.root), "config", "user.name", "X"], check=True); subprocess.run(["git", "-C", str(self.root), "add", "."], check=True); subprocess.run(["git", "-C", str(self.root), "commit", "-m", "fixture"], check=True, capture_output=True)
        (self.root / ".vibe").mkdir()
        self.app = json.loads((self.root / "app-spec" / "app-spec.json").read_text())
        self.app_fp = compute_app_spec_fingerprint(self.root / "app-spec"); self.workspace_fp = compute_workspace_fingerprint(self.root)
        self.request = {"schemaVersion":"2.0","requestId":"AUDIT-REQUEST-1","createdAt":"2026-09-04T09:59:00Z","ledgerDigest":"a"*64,"appSpecFingerprint":self.app_fp,"workspaceFingerprint":self.workspace_fp,"requiredAuditorContextId":"fresh-1","invocationKind":"fresh-context","implementationContextAvailable":False}
        self.request_path = self.root / ".vibe" / "audits" / "AUDIT-REQUEST-1" / "request.json"; self.request_path.parent.mkdir(parents=True); self.request_path.write_text(json.dumps(self.request))
        launch_fixture(self.root, self.request_path, self.request)
    def tearDown(self): shutil.rmtree(self.root, ignore_errors=True)
    def audit(self):
        surface_map = VALIDATOR.expected_surface_map(self.app); gates = {g["id"]:g for g in self.app["qualityGates"]}
        obligations=[]; coverage=[]
        for item_id, surfaces in surface_map.items():
            kind = "quality-gate" if item_id.startswith("QG-") else "managed-operation" if ":" in item_id else "acceptance-scenario"
            scope = gates[item_id]["category"] if item_id in gates else "repository"
            obligations.append({"id":item_id,"kind":kind,"scope":scope,"result":"verified","verificationSurfaces":surfaces,"evidence":[{"path":"project/src/preference_component.py","surface":surface} for surface in surfaces]})
            coverage += [{"obligationId":item_id,"surface":surface} for surface in surfaces]
        audit = {"schemaVersion":"2.0","auditId":"AUDIT-1","auditRequest":{"path":".vibe/audits/AUDIT-REQUEST-1/request.json","requestId":"AUDIT-REQUEST-1","sha256":hashlib.sha256(self.request_path.read_bytes()).hexdigest()},"auditorContext":{"contextId":"fresh-1","invocationKind":"fresh-context","implementationContextAvailable":False},"startedAt":"2026-09-04T10:00:00Z","completedAt":"2026-09-04T10:01:00Z","verdict":"PASS","appSpecFingerprint":self.app_fp,"workspaceFingerprint":self.workspace_fp,"sourceCoverage":coverage_fixture(self.root / "app-spec", list(surface_map)),"shadowInventory":canonical_inventory(self.app),"obligations":obligations,"checks":[{"checkId":"CHECK-1","argv":["python","verify_fixture.py"],"startedAt":"2026-09-04T10:00:00Z","completedAt":"2026-09-04T10:00:30Z","exitCode":0,"executionStatus":"completed","startWorkspaceFingerprint":self.workspace_fp,"workspaceFingerprint":self.workspace_fp,"coverage":coverage}],"findings":[],"completion":{"implementationComplete":True,"releaseReady":True}}
        audit_receipt_fixture(self.root, audit["checks"][0])
        return audit
    def validate(self, audit): return VALIDATOR.validate(audit, self.root / "app-spec", self.root, self.request_path)

    def test_valid_request_bound_audit(self): self.assertEqual([], self.validate(self.audit()))
    def test_wrong_shadow_inventory_is_rejected(self):
        audit=self.audit(); audit["shadowInventory"]["acceptanceScenarioIds"].pop(); self.assertTrue(any("shadowInventory" in e for e in self.validate(audit)))
    def test_surface_requires_matching_evidence_and_check(self):
        audit=self.audit(); target=audit["obligations"][0]; target["evidence"]=[]; self.assertTrue(any("has no evidence" in e for e in self.validate(audit)))
        audit=self.audit(); pair=audit["checks"][0]["coverage"].pop(0); self.assertTrue(any(pair["obligationId"] in e and "audit-time check" in e for e in self.validate(audit)))
    def test_fictitious_waiver_is_rejected(self):
        audit=self.audit(); target=audit["obligations"][0]; target["result"]="waived"; target["decisionReference"]="docs/no-such-decision.md#DEC-1"; self.assertTrue(any("durable decision" in e for e in self.validate(audit)))
    def test_stale_request_after_asset_change_is_rejected(self):
        audit=self.audit(); (self.root / "app-spec" / "assets" / "pixel.bin").write_bytes(b"y"); errors=self.validate(audit); self.assertTrue(any("stale audit request" in e for e in errors))
    def test_implementation_context_must_be_unavailable(self):
        audit=self.audit(); audit["auditorContext"]["implementationContextAvailable"]=True; self.assertTrue(any("must be false" in e for e in self.validate(audit)))

    def test_check_must_be_inside_audit_window(self):
        audit=self.audit(); audit["checks"][0].update(startedAt="2025-01-01T00:00:00Z",completedAt="2025-01-01T00:01:00Z")
        self.assertTrue(any("inside audit window" in e for e in self.validate(audit)))

    def test_equivalent_utc_offsets_are_ordered_by_time(self):
        audit=self.audit(); audit["checks"][0].update(startedAt="2026-09-04T13:00:00+03:00",completedAt="2026-09-04T13:00:30+03:00")
        self.assertEqual([],self.validate(audit))

    def test_source_file_cannot_waive_obligations(self):
        audit=self.audit()
        for item in audit["obligations"]: item.update(result="waived",decisionReference="project/src/preference_component.py")
        audit["checks"]=[]
        self.assertTrue(any("durable decision" in e for e in self.validate(audit)))

    def test_prose_sections_cannot_disappear_from_audit(self):
        audit=self.audit(); audit["sourceCoverage"].pop()
        self.assertTrue(any("source coverage mismatch" in e for e in self.validate(audit)))

    def test_self_declared_context_without_host_launch_is_insufficient(self):
        self.request_path.with_name("launch.json").unlink()
        self.assertTrue(any("launch evidence" in e for e in self.validate(self.audit())))

    def test_interrupted_check_and_changed_start_fingerprint_are_rejected(self):
        audit=self.audit(); audit["checks"][0]["executionStatus"]="interrupted"
        self.assertTrue(any("interrupted" in e for e in self.validate(audit)))
        audit=self.audit(); audit["checks"][0]["startWorkspaceFingerprint"]={}
        self.assertTrue(any("start fingerprint" in e for e in self.validate(audit)))

    def test_audit_check_requires_receipt_and_rejects_invented_command(self):
        audit = self.audit(); audit["checks"][0].pop("receiptRef")
        self.assertTrue(any("receipt invalid" in e for e in self.validate(audit)))
        audit = self.audit(); audit["checks"][0]["argv"] = ["never-executed-command"]
        self.assertTrue(any("receipt argv mismatch" in e for e in self.validate(audit)))

    def test_audit_receipt_and_log_tampering_are_rejected(self):
        audit = self.audit(); check = audit["checks"][0]; path = self.root / check["receiptRef"]
        path.write_text(path.read_text() + "\n")
        self.assertTrue(any("receipt hash mismatch" in e for e in self.validate(audit)))
        audit = self.audit(); receipt = json.loads((self.root / audit["checks"][0]["receiptRef"]).read_text())
        (self.root / receipt["log"]["path"]).write_text("altered output")
        self.assertTrue(any("log hash mismatch" in e for e in self.validate(audit)))

    def test_audit_receipt_scope_and_outcome_must_match(self):
        for field, value in (("coverage", []), ("exitCode", 7), ("completedAt", "2026-09-04T10:00:31Z")):
            with self.subTest(field=field):
                audit = self.audit(); audit["checks"][0][field] = value
                self.assertTrue(any(f"receipt {field} mismatch" in e for e in self.validate(audit)))

    def test_audit_receipt_cannot_escape_receipt_directory(self):
        audit = self.audit(); audit["checks"][0]["receiptRef"] = "../receipt.json"
        self.assertTrue(any("receipt invalid" in e for e in self.validate(audit)))

if __name__ == "__main__": unittest.main()
