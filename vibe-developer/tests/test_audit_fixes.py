"""Regression coverage for the September completeness and recovery audit."""
import importlib.util
import json
import sys
import unittest
from pathlib import Path

TESTS = Path(__file__).resolve().parent
SCRIPTS = TESTS.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))
spec = importlib.util.spec_from_file_location("fixes_delivery_fixture", TESTS / "delivery-ledger/test_delivery_protocol_20.py")
D = importlib.util.module_from_spec(spec); sys.modules[spec.name] = D; spec.loader.exec_module(D)


class AuditFixesTests(unittest.TestCase):
    def setUp(self):
        self.case = D.DeliveryProtocol20Tests(); self.case.setUp(); self.root = self.case.root
    def tearDown(self): self.case.tearDown()
    def specialist(self, *extra):
        return self.case.exec_script("specialist-state.py", "checkpoint", str(self.root), "--assignment-id", "ASSIGN-1",
            "--owner", "domain", "--obligation-id", "AC-001", "--file-boundary", "src/**",
            "--required-read", "docs/assignment.md", "--next-action", "Continue the saved assignment", *extra, check=False)
    def specialist_resume(self):
        return json.loads(self.case.exec_script("specialist-state.py", "resume", str(self.root), "--assignment-id", "ASSIGN-1", check=False).stdout)
    def resume(self):
        return json.loads(self.case.exec_script("resume-delivery.py", str(self.root), check=False).stdout)
    def checkpoint(self, *extra):
        return self.case.exec_script("checkpoint-delivery.py", str(self.root), "--expected-ledger-digest", self.case.ledger()["ledgerDigest"],
            "--phase", "implementing", "--active-ac", "AC-001", "--owner", "domain", "--file-boundary", "src/**",
            "--next-action", "Implement the saved request", *extra, check=False)

    def test_specialist_keeps_old_checks_and_blockers_on_next_checkpoint(self):
        self.assertEqual(0, self.specialist("--pending-check", "Rerun regression", "--blocker", "Need decision").returncode)
        original = {p:p.read_bytes() for p in (self.root / ".vibe/recovery").glob("*.json")}
        self.assertEqual(0, self.specialist("--pending-check", "Run integration").returncode)
        brief = self.specialist_resume()
        self.assertCountEqual(["Rerun regression", "Run integration"], [x["description"] for x in brief["packet"]["pendingChecks"]])
        self.assertEqual(["Need decision"], [x["description"] for x in brief["packet"]["blockers"]])
        self.assertFalse(brief["safeToContinue"])
        for path, content in original.items(): self.assertEqual(content, path.read_bytes())

    def test_specialist_requires_explicit_reasoned_resolution(self):
        self.specialist("--pending-check", "Rerun regression", "--blocker", "Need decision")
        self.assertNotEqual(0, self.specialist("--resolve-blocker", "Need decision").returncode)
        self.assertNotEqual(0, self.specialist("--resolve-blocker", "Unknown", "--resolution-reason", "Approved").returncode)
        packet = self.specialist_resume()["packet"]
        resolved = self.specialist("--resolve-blocker", packet["blockers"][0]["id"], "--resolution-reason", "Captured DEC-1")
        self.assertEqual(0, resolved.returncode, resolved.stdout)
        brief = self.specialist_resume()
        self.assertTrue(brief["safeToContinue"])
        self.assertEqual(["Rerun regression"], [x["description"] for x in brief["packet"]["pendingChecks"]])
        self.assertEqual(0, self.specialist("--resolve-pending-check", packet["pendingChecks"][0]["id"], "--resolution-reason", "Successful runner receipt").returncode)
        self.assertEqual([], self.specialist_resume()["packet"]["pendingChecks"])

    def test_specialist_inherits_reads_when_argument_is_omitted(self):
        self.assertEqual(0, self.specialist().returncode)
        result = self.case.exec_script("specialist-state.py", "checkpoint", str(self.root), "--assignment-id", "ASSIGN-1",
            "--owner", "domain", "--obligation-id", "AC-001", "--file-boundary", "src/**", "--next-action", "Finish the saved request", check=False)
        self.assertEqual(0, result.returncode, result.stdout)
        self.assertEqual(["docs/assignment.md"], self.specialist_resume()["packet"]["requiredReads"])

    def test_returned_assignment_is_terminal_and_preserves_transferred_checks(self):
        self.specialist("--pending-check", "Orchestrator must run Gradle")
        self.assertEqual(0, self.specialist("--status", "returned").returncode)
        brief = self.specialist_resume()
        self.assertFalse(brief["safeToContinue"]); self.assertTrue(brief["assignmentReturned"])
        self.assertEqual(["Orchestrator must run Gradle"], [x["description"] for x in brief["packet"]["pendingChecks"]])
        self.assertNotEqual(0, self.specialist().returncode)

    def test_missing_request_blocks_start_atomically_and_resume(self):
        ledger = self.case.ledger(); ledger["execution"].pop("durableRequest"); self.case.save(ledger)
        before = self.case.ledger_path.read_bytes()
        refused = self.checkpoint()
        self.assertNotEqual(0, refused.returncode); self.assertIn("durable request missing", refused.stderr)
        self.assertEqual(before, self.case.ledger_path.read_bytes())
        ledger["execution"]["phase"] = "implementing"; self.case.save(ledger)
        self.assertFalse(self.resume()["safeToContinue"])
        self.assertEqual(0, self.checkpoint("--request-file", "docs/assignment.md").returncode)
        self.assertTrue(self.resume()["safeToContinue"])

    def test_resume_always_includes_normative_prose_and_active_sources(self):
        self.assertEqual(0, self.checkpoint().returncode)
        brief = self.resume(); names = {Path(p).name for p in brief["requiredReads"]}
        self.assertTrue({"product.md", "domain.md", "data.md", "design.md", "quality.md", "FLOW-001.md", "SCREEN-001.md", "assignment.md"} <= names)
        self.assertTrue(brief["safeToContinue"])
        ledger = self.case.ledger(); ledger["execution"]["requiredReadHashes"] = []; self.case.save(ledger)
        self.assertFalse(self.resume()["safeToContinue"])

    def test_changed_request_requires_explicit_recapture(self):
        self.assertEqual(0, self.checkpoint().returncode)
        (self.root / "docs/assignment.md").write_text("New user constraint: preserve the existing ID format.")
        self.assertFalse(self.resume()["safeToContinue"])
        refused = self.checkpoint("--reconcile-drift", "Inspected the user request")
        self.assertNotEqual(0, refused.returncode); self.assertIn("durable request changed", refused.stderr)
        accepted = self.checkpoint("--reconcile-drift", "Inspected the user request", "--request-file", "docs/assignment.md")
        self.assertEqual(0, accepted.returncode, accepted.stderr)
        self.assertTrue(self.resume()["safeToContinue"])

    def test_missing_required_read_is_rejected_without_overwriting_ledger(self):
        before = self.case.ledger_path.read_bytes()
        result = self.checkpoint("--required-read", "docs/missing-contract.md")
        self.assertNotEqual(0, result.returncode)
        self.assertEqual(before, self.case.ledger_path.read_bytes())


if __name__ == "__main__": unittest.main()
