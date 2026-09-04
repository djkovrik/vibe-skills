from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path

DEVELOPER = Path(__file__).resolve().parents[2]
SCRIPTS = DEVELOPER / "scripts"
FIXTURE = Path(__file__).resolve().parent / "fixtures" / "app-spec"
sys.path.insert(0, str(SCRIPTS))
from vibe_protocol import compute_workspace_fingerprint, ledger_digest, with_ledger_digest

def module(name, file):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / file); value = importlib.util.module_from_spec(spec); sys.modules[name] = value; spec.loader.exec_module(value); return value
VALIDATOR = module("delivery_validator_20", "validate-delivery-ledger.py")

class DeliveryProtocol20Tests(unittest.TestCase):
    def setUp(self):
        self.scratch = Path(__file__).resolve().parent / ".test-workspaces"; self.scratch.mkdir(exist_ok=True)
        self.root = (self.scratch / uuid.uuid4().hex).resolve(); self.root.mkdir()
        shutil.copytree(FIXTURE, self.root / "app-spec")
        (self.root / "app-spec" / "assets").mkdir(); (self.root / "app-spec" / "assets" / "icon.bin").write_bytes(b"one")
        (self.root / "src").mkdir(); (self.root / "tests").mkdir(); (self.root / "config").mkdir()
        (self.root / "src" / "App.kt").write_text("class AppComponent { fun saveValue() = Unit }\n")
        (self.root / "tests" / "AppTest.kt").write_text("fun savedValueIsObservable() = Unit\n")
        (self.root / "config" / "quality.yml").write_text("repositoryQualityPasses\nandroidBuild\nreleaseCheck\n")
        self.git("init"); self.git("config", "user.email", "x@example.test"); self.git("config", "user.name", "X"); self.git("add", "."); self.git("commit", "-m", "fixture")
        self.exec_script("init-delivery-ledger.py", str(self.root / "app-spec"), "--project-root", str(self.root))
    def tearDown(self): shutil.rmtree(self.root, ignore_errors=True)
    def git(self, *args): subprocess.run(["git", "-C", str(self.root), *args], check=True, capture_output=True)
    def exec_script(self, script, *args, check=True): return subprocess.run([sys.executable, str(SCRIPTS / script), *args], check=check, text=True, capture_output=True)
    @property
    def ledger_path(self): return self.root / ".vibe" / "delivery-ledger.json"
    def ledger(self): return json.loads(self.ledger_path.read_text())
    def save(self, value): self.ledger_path.write_text(json.dumps(with_ledger_digest(value), indent=2) + "\n")
    def start(self):
        digest = self.ledger()["ledgerDigest"]
        self.exec_script("checkpoint-delivery.py", str(self.root), "--expected-ledger-digest", digest, "--phase", "implementing", "--active-ac", "AC-001", "--owner", "test", "--file-boundary", "src/**", "--file-boundary", "tests/**", "--next-action", "Implement AC-001.")
    def receipt(self, name, exit_code, completed, surfaces, kind="targeted", coverage=None):
        directory = self.root / ".vibe" / "receipts"; directory.mkdir(exist_ok=True)
        log = directory / f"{name}.log"; log.write_text(name)
        import hashlib
        value = {"schemaVersion":"2.0","receiptId":f"R-{name}","kind":kind,"argv":["tool","check"],"tasks":["check"],"coveredObligations":coverage or [{"obligationId":"AC-001","surfaces":surfaces}],"startedAt":"2026-09-04T10:00:00Z","completedAt":completed,"workspaceFingerprint":compute_workspace_fingerprint(self.root),"exitCode":exit_code,"log":{"path":f".vibe/receipts/{name}.log","sha256":hashlib.sha256(log.read_bytes()).hexdigest()}}
        path = directory / f"{name}.json"; path.write_text(json.dumps(value)); return f".vibe/receipts/{name}.json"
    def verified_ac(self, refs):
        ledger = self.ledger(); item = ledger["acceptanceScenarios"][0]
        item.update({"status":"verified","productionEvidence":[{"path":"src/App.kt","symbol":"AppComponent","surface":"public-contract"}],"testEvidence":[{"path":"tests/AppTest.kt","testName":"savedValueIsObservable","surface":"component-test"}],"receiptRefs":refs})
        ledger["workspaceFingerprint"] = compute_workspace_fingerprint(self.root); self.save(ledger)

    def test_init_and_clean_resume(self):
        ledger = self.ledger(); self.assertEqual("2.0", ledger["schemaVersion"]); self.assertEqual(ledger_digest(ledger), ledger["ledgerDigest"])
        brief = json.loads(self.exec_script("resume-delivery.py", str(self.root)).stdout); self.assertEqual("clean", brief["driftClassification"])
        duplicate = self.exec_script("init-delivery-ledger.py", str(self.root / "app-spec"), "--project-root", str(self.root), check=False); self.assertNotEqual(0, duplicate.returncode); self.assertIn("refusing to overwrite", duplicate.stderr)
        before = self.ledger_path.read_bytes(); conflict = self.exec_script("checkpoint-delivery.py", str(self.root), "--expected-ledger-digest", "0" * 64, "--phase", "planning", "--next-action", "No-op.", check=False); self.assertNotEqual(0, conflict.returncode); self.assertEqual(before, self.ledger_path.read_bytes())

    def test_restart_inside_and_outside_boundaries(self):
        self.start(); (self.root / "src" / "App.kt").write_text("class Changed\n")
        brief = json.loads(self.exec_script("resume-delivery.py", str(self.root)).stdout); self.assertEqual("expected-drift", brief["driftClassification"]); self.assertIn("reconciliation", brief["nextAction"])
        (self.root / "config" / "quality.yml").write_text("outside\n")
        process = self.exec_script("resume-delivery.py", str(self.root), check=False); brief = json.loads(process.stdout); self.assertEqual("unexpected-drift", brief["driftClassification"])

    def test_pending_handoff_is_discovered_and_ingested(self):
        self.start(); (self.root / "src" / "App.kt").write_text("class AppComponent { fun saveValue() = Unit; fun changed()=Unit }\n")
        fp = compute_workspace_fingerprint(self.root); handoffs = self.root / ".vibe" / "handoffs"; handoffs.mkdir()
        handoff = {"schemaVersion":"2.0","handoffId":"HANDOFF-1","assignmentId":"ASSIGN-1","owner":"specialist","acceptanceScenarioIds":["AC-001"],"qualityGateIds":[],"startedAt":"2026-09-04T10:00:00Z","completedAt":"2026-09-04T10:01:00Z","baseWorkspaceFingerprint":self.ledger()["acceptanceScenarios"][0]["baselineFingerprint"],"resultWorkspaceFingerprint":fp,"allowedFiles":["src/**"],"changedFiles":["src/App.kt"],"productionEvidence":[{"path":"src/App.kt","symbol":"AppComponent","surface":"public-contract"}],"testEvidence":[],"nonGradleChecks":[],"requestedCommands":[],"blockers":[]}
        path = handoffs / "HANDOFF-1.json"; path.write_text(json.dumps(handoff))
        brief = json.loads(self.exec_script("resume-delivery.py", str(self.root)).stdout); self.assertEqual(1, len(brief["pendingHandoffs"]))
        digest = self.ledger()["ledgerDigest"]; self.exec_script("ingest-handoff.py", str(self.root), str(path), "--expected-ledger-digest", digest)
        self.assertEqual("implemented-unverified", self.ledger()["acceptanceScenarios"][0]["status"])
        path.write_text(json.dumps({**handoff, "blockers":["mutated after ingestion"]}))
        self.assertTrue(any("hash-mismatched" in error for error in VALIDATOR.validate_ledger(self.root, self.ledger_path).errors))

    def test_appspec_asset_change_invalidates_ledger(self):
        (self.root / "app-spec" / "assets" / "icon.bin").write_bytes(b"two")
        result = VALIDATOR.validate_ledger(self.root, self.ledger_path)
        self.assertTrue(any("app-spec.fingerprint.stale" in e for e in result.errors))

    def test_resume_classifies_stale_evidence(self):
        ref = self.receipt("stale", 0, "2026-09-04T10:02:00Z", ["component-test"])
        receipt_path = self.root / ref; value = json.loads(receipt_path.read_text()); value["workspaceFingerprint"]["digest"] = "0" * 64; receipt_path.write_text(json.dumps(value))
        ledger = self.ledger(); ledger["acceptanceScenarios"][0].update({"status":"verified","receiptRefs":[ref]}); self.save(ledger)
        brief = json.loads(self.exec_script("resume-delivery.py", str(self.root)).stdout)
        self.assertEqual("stale-evidence", brief["driftClassification"]); self.assertFalse(brief["completionEligible"])

    def test_latest_current_receipt_wins_pass_fail_and_fail_pass(self):
        passed = self.receipt("pass", 0, "2026-09-04T10:02:00Z", ["component-test"])
        failed = self.receipt("fail", 3, "2026-09-04T10:03:00Z", ["component-test"])
        self.verified_ac([passed, failed]); result = VALIDATOR.validate_ledger(self.root, self.ledger_path)
        self.assertTrue(any("latest current receipt" in e for e in result.errors))
        newer = self.receipt("pass2", 0, "2026-09-04T10:04:00Z", ["component-test"])
        self.verified_ac([passed, failed, newer]); result = VALIDATOR.validate_ledger(self.root, self.ledger_path)
        self.assertFalse(any("AC-001: latest current receipt" in e for e in result.errors))

    def test_missing_final_receipt_blocks_completion(self):
        ref = self.receipt("target", 0, "2026-09-04T10:02:00Z", ["component-test"]); self.verified_ac([ref])
        ledger = self.ledger(); gate = ledger["qualityGates"][0]; gate.update({"status":"waived","decisionReference":"app-spec/quality.md#repository-tests"}); ledger["workspaceFingerprint"] = compute_workspace_fingerprint(self.root); self.save(ledger)
        result = VALIDATOR.validate_ledger(self.root, self.ledger_path); self.assertTrue(any("final receipt" in e for e in result.errors)); self.assertFalse(result.implementation_complete)

    def test_audit_request_requires_closed_local_work_and_binds_hash(self):
        digest = self.ledger()["ledgerDigest"]
        refused = self.exec_script("create-audit-request.py", str(self.root), "--expected-ledger-digest", digest, "--auditor-context-id", "fresh-1", check=False)
        self.assertNotEqual(0, refused.returncode); self.assertIn("acceptance scenarios", refused.stderr)
        ledger = self.ledger(); ledger["acceptanceScenarios"][0].update({"status":"waived","decisionReference":"app-spec/quality.md"}); ledger["qualityGates"][0].update({"status":"waived","decisionReference":"app-spec/quality.md"}); self.save(ledger)
        process = self.exec_script("create-audit-request.py", str(self.root), "--expected-ledger-digest", self.ledger()["ledgerDigest"], "--auditor-context-id", "fresh-1")
        self.assertIn("request-sha256", process.stdout); self.assertTrue((self.root / ".vibe" / "audit-request.json").is_file()); self.assertRegex(self.ledger()["closureAudit"]["requestSha256"], r"^[a-f0-9]{64}$")

    def test_failed_final_receipt_and_generated_report_drift_are_rejected(self):
        ref = self.receipt("failed-final", 9, "2026-09-04T10:05:00Z", ["component-test"], kind="final"); self.verified_ac([ref])
        ledger = self.ledger(); gate = ledger["qualityGates"][0]; gate.update({"status":"waived","decisionReference":"app-spec/quality.md"}); ledger["finalReceiptRef"] = ref; ledger["execution"]["phase"] = "final-verification"; ledger["workspaceFingerprint"] = compute_workspace_fingerprint(self.root); self.save(ledger)
        (self.root / "docs").mkdir(); (self.root / "docs" / "requirement-traceability.generated.md").write_text("stale\n")
        result = VALIDATOR.validate_ledger(self.root, self.ledger_path)
        self.assertTrue(any("final receipt failed" in e for e in result.errors)); self.assertTrue(any("generated delivery report" in e for e in result.errors))

    def test_invalid_appspec_cannot_pass_through_ledger_validator(self):
        data = json.loads((self.root / "app-spec" / "app-spec.json").read_text()); data["acceptanceScenarios"][0]["required"] = False; (self.root / "app-spec" / "app-spec.json").write_text(json.dumps(data))
        result = VALIDATOR.validate_ledger(self.root, self.ledger_path); self.assertTrue(any("required is removed" in e for e in result.errors)); self.assertFalse(result.implementation_complete)

    def test_positive_end_to_end_closure(self):
        coverage = [
            {"obligationId":"AC-001","surfaces":["component-test"]},
            {"obligationId":"QG-001","surfaces":["repository-check"]},
            {"obligationId":"QG-002","surfaces":["android-build"]},
            {"obligationId":"QG-003","surfaces":["release-check"]},
        ]
        final_ref = self.receipt("final", 0, "2026-09-04T10:10:00Z", [], kind="final", coverage=coverage); self.verified_ac([final_ref])
        ledger = self.ledger()
        for gate in ledger["qualityGates"]: gate.update({"status":"waived","decisionReference":"app-spec/quality.md"})
        ledger["finalReceiptRef"] = final_ref; ledger["workspaceFingerprint"] = compute_workspace_fingerprint(self.root); self.save(ledger)
        import hashlib
        from vibe_protocol import canonical_inventory, compute_app_spec_fingerprint
        request = {"schemaVersion":"2.0","requestId":"REQUEST-1","createdAt":"2026-09-04T10:11:00Z","ledgerDigest":self.ledger()["ledgerDigest"],"appSpecFingerprint":compute_app_spec_fingerprint(self.root / "app-spec"),"workspaceFingerprint":compute_workspace_fingerprint(self.root),"requiredAuditorContextId":"fresh-1","invocationKind":"fresh-context","implementationContextAvailable":False}
        request_path = self.root / ".vibe" / "audit-request.json"; request_path.write_text(json.dumps(request)); request_hash = hashlib.sha256(request_path.read_bytes()).hexdigest()
        app = json.loads((self.root / "app-spec" / "app-spec.json").read_text()); fp = compute_workspace_fingerprint(self.root)
        obligations = [
            {"id":"AC-001","kind":"acceptance-scenario","scope":"repository","result":"verified","verificationSurfaces":["component-test"],"evidence":[{"path":"tests/AppTest.kt","surface":"component-test"}]},
            {"id":"Value:create","kind":"managed-operation","scope":"repository","result":"verified","verificationSurfaces":["component-test"],"evidence":[{"path":"tests/AppTest.kt","surface":"component-test"}]},
        ] + [{"id":gate["id"],"kind":"quality-gate","scope":gate["category"],"result":"waived","verificationSurfaces":gate["verificationSurfaces"],"evidence":[],"decisionReference":"app-spec/quality.md"} for gate in app["qualityGates"]]
        audit = {"schemaVersion":"2.0","auditId":"AUDIT-1","auditRequest":{"path":".vibe/audit-request.json","requestId":"REQUEST-1","sha256":request_hash},"auditorContext":{"contextId":"fresh-1","invocationKind":"fresh-context","implementationContextAvailable":False},"startedAt":"2026-09-04T10:11:00Z","completedAt":"2026-09-04T10:12:00Z","verdict":"PASS","appSpecFingerprint":request["appSpecFingerprint"],"workspaceFingerprint":fp,"shadowInventory":canonical_inventory(app),"obligations":obligations,"checks":[{"checkId":"AUDIT-CHECK","argv":["tool","check"],"startedAt":"2026-09-04T10:11:00Z","completedAt":"2026-09-04T10:11:30Z","exitCode":0,"workspaceFingerprint":fp,"coverage":[{"obligationId":"AC-001","surface":"component-test"},{"obligationId":"Value:create","surface":"component-test"}]}],"findings":[],"completion":{"implementationComplete":True,"releaseReady":True}}
        audit_path = self.root / ".vibe" / "closure-audit.json"; audit_path.write_text(json.dumps(audit))
        ledger = self.ledger(); ledger["closureAudit"]={"requestPath":".vibe/audit-request.json","requestSha256":request_hash,"auditPath":".vibe/closure-audit.json"}; ledger["execution"]["phase"]="final-verification"; ledger["workspaceFingerprint"]=fp; self.save(ledger)
        self.run_report("render-delivery-report.py", str(self.root)); (self.root / "docs").mkdir(exist_ok=True); audit_renderer = Path(__file__).resolve().parents[3] / "vibe-acceptance-auditor" / "scripts" / "render-closure-audit.py"; subprocess.run([sys.executable, str(audit_renderer), str(audit_path), str(self.root / "docs" / "closure-audit.generated.md")], check=True, capture_output=True)
        result = VALIDATOR.validate_ledger(self.root, self.ledger_path); self.assertTrue(result.implementation_complete, result.errors); self.assertTrue(result.release_ready, result.errors)
        (self.root / "docs" / "closure-audit.generated.md").write_text("drift\n")
        drifted = VALIDATOR.validate_ledger(self.root, self.ledger_path); self.assertTrue(any("generated closure report" in e for e in drifted.errors)); self.assertFalse(drifted.implementation_complete)

    def test_aggregate_always_prints_verdict_lines(self):
        process = self.exec_script("validate-delivery-ledger.py", str(self.root), check=False)
        self.assertIn("implementation-complete:", process.stdout); self.assertIn("release-ready:", process.stdout)

    def run_report(self, script, *args): return self.exec_script(script, *args)

if __name__ == "__main__": unittest.main()
