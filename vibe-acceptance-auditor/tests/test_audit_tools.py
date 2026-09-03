from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_script(name: str):
    path = ROOT / "scripts" / name
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


validator = load_script("validate-closure-audit.py")
renderer = load_script("render-closure-audit.py")


def valid_audit() -> dict:
    hash_a = "a" * 64
    hash_b = "b" * 64
    hash_c = "c" * 64
    app_fingerprint = {
        "algorithm": "sha256",
        "files": [{"path": "app-spec.json", "sha256": hash_a}],
        "digest": hash_b,
    }
    workspace_fingerprint = {
        "algorithm": "sha256",
        "gitHead": "0123456789abcdef",
        "binaryDiffSha256": hash_a,
        "untrackedFiles": [],
        "digest": hash_c,
    }
    return {
        "schemaVersion": "1.0",
        "verdict": "PASS",
        "completedAt": "2026-09-03T10:00:00Z",
        "auditorContext": {"fresh": True, "contextId": "forward-test"},
        "appSpecFingerprint": app_fingerprint,
        "workspaceFingerprint": workspace_fingerprint,
        "shadowInventory": {
            "requirementIds": ["REQ-001"],
            "acceptanceScenarioIds": ["AC-001"],
            "managedOperationIds": [],
            "qualityGateIds": ["QG-001"],
        },
        "obligations": [
            {
                "id": "AC-001",
                "kind": "acceptance-scenario",
                "scope": "repository",
                "result": "verified",
                "verificationSurfaces": ["public-contract", "component-test"],
                "evidence": [
                    {"path": "src/preference_component.py", "surface": "production", "symbol": "create_preference"},
                    {"path": "test/test_preference_component.py", "surface": "component-test", "testName": "test_create_preference_is_observable"},
                ],
            },
            {
                "id": "QG-001",
                "kind": "quality-gate",
                "scope": "repository",
                "result": "verified",
                "verificationSurfaces": ["repository"],
                "evidence": [{"path": "verify_fixture.py", "surface": "quality-config"}],
            },
        ],
        "checks": [
            {
                "id": "CHECK-001",
                "command": ".\\gradlew.bat test detekt",
                "exitCode": 0,
                "completedAt": "2026-09-03T10:00:00Z",
                "result": "pass",
                "obligationIds": ["AC-001", "QG-001"],
                "workspaceFingerprint": workspace_fingerprint,
            }
        ],
        "findings": [],
        "completion": {"implementationComplete": True, "releaseReady": True},
    }


class AuditValidationTest(unittest.TestCase):
    def test_valid_pass_with_real_evidence(self):
        repo = ROOT / "assets" / "behavioral-fixtures" / "positive-end-to-end" / "project"
        audit = valid_audit()
        self.assertEqual([], validator.validate(audit, audit["appSpecFingerprint"], audit["workspaceFingerprint"], repo))

    def test_pass_is_invalid_after_workspace_change(self):
        audit = valid_audit()
        changed = dict(audit["workspaceFingerprint"])
        changed["digest"] = "d" * 64
        errors = validator.validate(audit, audit["appSpecFingerprint"], changed)
        self.assertIn("stale workspace fingerprint", errors)

    def test_verified_scenario_requires_production_test_and_receipt(self):
        audit = valid_audit()
        audit["obligations"][0]["evidence"] = [
            {"path": "src/preference_component.py", "surface": "production", "symbol": "create_preference"}
        ]
        audit["checks"][0]["obligationIds"] = ["QG-001"]
        errors = validator.validate(audit, None, None)
        self.assertTrue(any("exact test evidence" in error for error in errors))
        self.assertTrue(any("no successful audit-time check: AC-001" in error for error in errors))

    def test_gaps_cannot_claim_completion(self):
        audit = valid_audit()
        audit["verdict"] = "GAPS"
        errors = validator.validate(audit, None, None)
        self.assertIn("GAPS cannot claim completion", errors)

    def test_external_release_blocker_preserves_implementation_only(self):
        audit = valid_audit()
        audit["completion"]["releaseReady"] = False
        audit["shadowInventory"]["qualityGateIds"].append("QG-RELEASE")
        audit["obligations"].append({
            "id": "QG-RELEASE",
            "kind": "quality-gate",
            "scope": "release",
            "result": "blocked-external",
            "verificationSurfaces": ["play-console"],
            "evidence": [],
        })
        audit["findings"].append({
            "id": "FINDING-001",
            "kind": "external-blocker",
            "obligationIds": ["QG-RELEASE"],
            "summary": "Store credentials are unavailable.",
            "evidence": [],
        })
        self.assertEqual([], validator.validate(audit, None, None))

    def test_render_is_deterministic_and_complete(self):
        first = renderer.render(valid_audit())
        second = renderer.render(json.loads(json.dumps(valid_audit())))
        self.assertEqual(first, second)
        self.assertIn("Verdict: `PASS`", first)
        self.assertIn("AC-001", first)
        self.assertIn(f"Workspace fingerprint: `{'c' * 64}`", first)


if __name__ == "__main__":
    unittest.main()
