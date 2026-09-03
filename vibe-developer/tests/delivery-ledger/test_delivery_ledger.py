from __future__ import annotations

import importlib.util
import json
import os
import shutil
import stat
import subprocess
import sys
import unittest
import uuid
from pathlib import Path
from typing import Any


os.environ["PYTHONDONTWRITEBYTECODE"] = "1"


def remove_readonly(function: Any, path: str, _error: Any) -> None:
    os.chmod(path, stat.S_IWRITE)
    function(path)


VIBE_DEVELOPER = Path(__file__).resolve().parents[2]
SCRIPTS = VIBE_DEVELOPER / "scripts"
FIXTURE = Path(__file__).resolve().parent / "fixtures" / "app-spec"


def load_script(filename: str, module_name: str) -> Any:
    spec = importlib.util.spec_from_file_location(module_name, SCRIPTS / filename)
    if spec is None or spec.loader is None:
        raise RuntimeError(filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


FINGERPRINT = load_script("compute-workspace-fingerprint.py", "test_fingerprint")
VALIDATOR = load_script("validate-delivery-ledger.py", "test_ledger_validator")


class DeliveryLedgerTest(unittest.TestCase):
    def setUp(self) -> None:
        scratch = Path(__file__).resolve().parent / ".test-workspaces"
        scratch.mkdir(exist_ok=True)
        self.root = (scratch / uuid.uuid4().hex).resolve()
        self.root.mkdir()
        shutil.copytree(FIXTURE, self.root / "app-spec")
        (self.root / "src").mkdir()
        (self.root / "tests").mkdir()
        (self.root / "config").mkdir()
        (self.root / "src" / "App.kt").write_text(
            "class AppComponent { fun saveValue() = Unit }\n", encoding="utf-8"
        )
        (self.root / "tests" / "AppTest.kt").write_text(
            "class AppComponentTest { fun savedValueIsObservable() = Unit }\n",
            encoding="utf-8",
        )
        (self.root / "config" / "quality.yml").write_text(
            "gateConfig: strict\nplatformConfig: android\nreleaseConfig: approved\n", encoding="utf-8"
        )
        (self.root / "tests" / "QualityTest.kt").write_text(
            "fun repositoryQualityPasses() = Unit\nfun androidReleaseBuildPasses() = Unit\nfun releaseAcceptancePasses() = Unit\n",
            encoding="utf-8",
        )
        self.git("init")
        self.git("config", "user.email", "fixture@example.test")
        self.git("config", "user.name", "Fixture")
        self.git("add", ".")
        self.git("commit", "-m", "fixture")
        self.run_script(
            "init-delivery-ledger.py",
            str(self.root / "app-spec"),
            "--project-root",
            str(self.root),
        )

    def tearDown(self) -> None:
        scratch = self.root.parent
        shutil.rmtree(self.root, onerror=remove_readonly)
        try:
            scratch.rmdir()
        except OSError:
            pass

    def git(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", "-C", str(self.root), *arguments],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def run_script(self, filename: str, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPTS / filename), *arguments],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    @property
    def ledger_path(self) -> Path:
        return self.root / ".vibe" / "delivery-ledger.json"

    def read_ledger(self) -> dict[str, Any]:
        return json.loads(self.ledger_path.read_text(encoding="utf-8"))

    def write_ledger(self, ledger: dict[str, Any]) -> None:
        self.ledger_path.write_text(
            json.dumps(ledger, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )

    def make_complete(self, *, release_ready: bool = True) -> dict[str, Any]:
        ledger = self.read_ledger()
        workspace = FINGERPRINT.compute_workspace_fingerprint(self.root)
        receipt = {
            "schemaVersion": "1.0",
            "command": "./gradlew check assembleRelease",
            "exitCode": 0,
            "completedAt": "2026-09-03T12:00:00Z",
            "workspaceFingerprint": workspace,
            "acceptanceScenarioIds": ["AC-001"],
            "qualityGateIds": ["QG-001", "QG-002", "QG-003"],
        }
        receipt_path = self.root / ".vibe" / "receipts" / "verification.json"
        receipt_path.parent.mkdir(parents=True, exist_ok=True)
        receipt_path.write_text(json.dumps(receipt), encoding="utf-8")

        scenario = ledger["acceptanceScenarios"][0]
        scenario.update(
            {
                "status": "verified",
                "productionEvidence": [
                    {"path": "src/App.kt", "symbol": "AppComponent.saveValue", "surface": "public-contract"}
                ],
                "testEvidence": [
                    {
                        "path": "tests/AppTest.kt",
                        "testName": "AppComponentTest.savedValueIsObservable",
                        "surface": "component-test",
                    }
                ],
                "verificationReceipts": [".vibe/receipts/verification.json"],
            }
        )
        for gate in ledger["qualityGates"]:
            if gate["id"] == "QG-002" and not release_ready:
                gate.update(
                    {
                        "status": "blocked-external",
                        "blocker": {"reason": "Signing credentials are external."},
                    }
                )
                continue
            evidence_by_gate = {
                "QG-001": ("gateConfig", "repositoryQualityPasses"),
                "QG-002": ("platformConfig", "androidReleaseBuildPasses"),
                "QG-003": ("releaseConfig", "releaseAcceptancePasses"),
            }
            config_symbol, test_name = evidence_by_gate[gate["id"]]
            gate.update(
                {
                    "status": "verified",
                    "productionEvidence": [
                        {
                            "path": "config/quality.yml",
                            "symbol": config_symbol,
                            "surface": "configuration",
                        }
                    ],
                    "testEvidence": [
                        {
                            "path": "tests/QualityTest.kt",
                            "testName": test_name,
                            "surface": "quality-gate",
                        }
                    ],
                    "verificationReceipts": [{"path": ".vibe/receipts/verification.json"}],
                }
            )
        ledger["workspaceFingerprint"] = workspace
        self.write_ledger(ledger)
        audit_obligations = [
            {
                "id": "AC-001",
                "kind": "acceptance-scenario",
                "scope": "repository",
                "result": "verified",
                "verificationSurfaces": ["component-test"],
                "evidence": [
                    {"path": "src/App.kt", "surface": "production", "symbol": "AppComponent"},
                    {
                        "path": "tests/AppTest.kt",
                        "surface": "component-test",
                        "testName": "savedValueIsObservable",
                    },
                ],
            },
            {
                "id": "Value:create",
                "kind": "managed-operation",
                "scope": "repository",
                "result": "verified",
                "verificationSurfaces": ["component-test"],
                "evidence": [
                    {"path": "src/App.kt", "surface": "production", "symbol": "saveValue"},
                    {
                        "path": "tests/AppTest.kt",
                        "surface": "component-test",
                        "testName": "savedValueIsObservable",
                    },
                ],
            },
        ]
        gate_scopes = {"QG-001": "repository", "QG-002": "platform", "QG-003": "release"}
        for gate in ledger["qualityGates"]:
            audit_obligations.append(
                {
                    "id": gate["id"],
                    "kind": "quality-gate",
                    "scope": gate_scopes[gate["id"]],
                    "result": "blocked-external"
                    if gate["status"] == "blocked-external"
                    else "verified",
                    "verificationSurfaces": ["quality-gate"],
                    "evidence": []
                    if gate["status"] == "blocked-external"
                    else [{"path": "config/quality.yml", "surface": "quality-config"}],
                }
            )
        verified_ids = [
            item["id"] for item in audit_obligations if item["result"] == "verified"
        ]
        audit = {
            "schemaVersion": "1.0",
            "verdict": "PASS",
            "completedAt": "2026-09-03T12:01:00Z",
            "auditorContext": {"fresh": True, "contextId": "ledger-forward-test"},
            "appSpecFingerprint": ledger["appSpec"]["fingerprint"],
            "workspaceFingerprint": workspace,
            "shadowInventory": {
                "requirementIds": ["REQ-001"],
                "acceptanceScenarioIds": ["AC-001"],
                "managedOperationIds": ["Value:create"],
                "qualityGateIds": ["QG-001", "QG-002", "QG-003"],
            },
            "obligations": audit_obligations,
            "checks": [
                {
                    "id": "CHECK-001",
                    "command": "./gradlew check assembleRelease",
                    "exitCode": 0,
                    "completedAt": "2026-09-03T12:01:00Z",
                    "result": "pass",
                    "obligationIds": verified_ids,
                    "workspaceFingerprint": workspace,
                }
            ],
            "findings": []
            if release_ready
            else [
                {
                    "kind": "external-blocker",
                    "obligationIds": ["QG-002"],
                    "summary": "Signing credentials are external.",
                    "evidence": [],
                }
            ],
            "completion": {
                "implementationComplete": True,
                "releaseReady": release_ready,
            },
        }
        (self.root / ".vibe" / "closure-audit.json").write_text(
            json.dumps(audit), encoding="utf-8"
        )
        return ledger

    def validate(self) -> Any:
        return VALIDATOR.validate_ledger(self.root, self.ledger_path)

    def test_init_is_non_overwriting_and_inventory_is_complete(self) -> None:
        ledger = self.read_ledger()
        self.assertEqual("1.0", ledger["schemaVersion"])
        self.assertEqual(["AC-001"], [item["id"] for item in ledger["acceptanceScenarios"]])
        self.assertEqual(
            ["QG-001", "QG-002", "QG-003"],
            [item["id"] for item in ledger["qualityGates"]],
        )
        process = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS / "init-delivery-ledger.py"),
                str(self.root / "app-spec"),
                "--project-root",
                str(self.root),
            ],
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertEqual(2, process.returncode)
        self.assertIn("refusing to overwrite", process.stderr)

    def test_workspace_fingerprint_hashes_changes_and_ignores_delivery_artifacts(self) -> None:
        before = FINGERPRINT.compute_workspace_fingerprint(self.root)
        (self.root / ".vibe" / "receipts").mkdir(exist_ok=True)
        (self.root / ".vibe" / "receipts" / "ignored.json").write_text("{}")
        (self.root / "docs").mkdir()
        (self.root / "docs" / "requirement-traceability.generated.md").write_text("generated")
        self.assertEqual(before, FINGERPRINT.compute_workspace_fingerprint(self.root))
        (self.root / "untracked.txt").write_text("evidence", encoding="utf-8")
        after = FINGERPRINT.compute_workspace_fingerprint(self.root)
        self.assertNotEqual(before["digest"], after["digest"])
        self.assertEqual(["untracked.txt"], [item["path"] for item in after["untrackedFiles"]])

    def test_positive_fixture_is_implementation_complete_and_release_ready(self) -> None:
        self.make_complete()
        result = self.validate()
        self.assertEqual([], result.errors)
        self.assertTrue(result.implementation_complete)
        self.assertTrue(result.release_ready)

    def test_external_release_blocker_preserves_implementation_verdict_only(self) -> None:
        self.make_complete(release_ready=False)
        result = self.validate()
        self.assertEqual([], result.errors)
        self.assertTrue(result.implementation_complete)
        self.assertFalse(result.release_ready)

    def test_stale_workspace_invalidates_ledger_receipt_and_audit(self) -> None:
        self.make_complete()
        (self.root / "src" / "App.kt").write_text(
            "class AppComponent { fun saveValue() = 1 }\n", encoding="utf-8"
        )
        result = self.validate()
        joined = "\n".join(result.errors)
        self.assertIn("workspace.fingerprint.stale", joined)
        self.assertIn("receipt is stale", joined)
        self.assertIn("closure-audit.stale-workspace", joined)
        self.assertFalse(result.implementation_complete)

    def test_stale_app_spec_invalidates_ledger_and_audit(self) -> None:
        self.make_complete()
        flow = self.root / "app-spec" / "flows" / "FLOW-001.md"
        flow.write_text(flow.read_text(encoding="utf-8") + "\nChanged.\n", encoding="utf-8")
        result = self.validate()
        joined = "\n".join(result.errors)
        self.assertIn("app-spec.fingerprint.stale", joined)
        self.assertIn("closure-audit.stale-app-spec", joined)
        self.assertFalse(result.implementation_complete)

    def test_verified_item_requires_real_evidence_symbols_surfaces_and_receipt(self) -> None:
        ledger = self.make_complete()
        scenario = ledger["acceptanceScenarios"][0]
        scenario["productionEvidence"][0]["path"] = "src/Missing.kt"
        scenario["testEvidence"][0]["testName"] = "doesNotExist"
        scenario["testEvidence"][0]["surface"] = "wrong-surface"
        scenario["verificationReceipts"] = []
        self.write_ledger(ledger)
        result = self.validate()
        joined = "\n".join(result.errors)
        self.assertIn("file does not exist", joined)
        self.assertIn("doesNotExist", joined)
        self.assertIn("missing required test surface", joined)
        self.assertIn("zero-exit verification receipt", joined)
        self.assertFalse(result.implementation_complete)

    def test_waiver_requires_explicit_user_decision_reference(self) -> None:
        ledger = self.make_complete()
        scenario = ledger["acceptanceScenarios"][0]
        scenario.update(
            {
                "status": "waived",
                "waiver": {"reason": "User accepted the limitation.", "userDecisionRef": ""},
            }
        )
        self.write_ledger(ledger)
        result = self.validate()
        self.assertIn("userDecisionRef", "\n".join(result.errors))

    def test_fabricated_empty_pass_audit_is_rejected(self) -> None:
        ledger = self.make_complete()
        fake_audit = {
            "schemaVersion": "1.0",
            "verdict": "PASS",
            "completedAt": "2026-09-03T12:01:00Z",
            "appSpecFingerprint": ledger["appSpec"]["fingerprint"],
            "workspaceFingerprint": ledger["workspaceFingerprint"],
            "checks": [],
            "findings": [],
        }
        (self.root / ".vibe" / "closure-audit.json").write_text(
            json.dumps(fake_audit), encoding="utf-8"
        )
        result = self.validate()
        joined = "\n".join(result.errors)
        self.assertIn("auditorContext", joined)
        self.assertIn("shadowInventory", joined)
        self.assertIn("obligations", joined)
        self.assertFalse(result.implementation_complete)

    def test_report_check_detects_drift(self) -> None:
        self.make_complete()
        self.run_script("render-delivery-report.py", str(self.root))
        self.run_script("render-delivery-report.py", str(self.root), "--check")
        report = self.root / "docs" / "requirement-traceability.generated.md"
        report.write_text(report.read_text(encoding="utf-8") + "drift\n", encoding="utf-8")
        process = subprocess.run(
            [sys.executable, str(SCRIPTS / "render-delivery-report.py"), str(self.root), "--check"],
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertEqual(1, process.returncode)
        self.assertIn("out of date", process.stderr)


if __name__ == "__main__":
    unittest.main()
