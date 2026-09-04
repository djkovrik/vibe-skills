from __future__ import annotations

import copy
import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "assets" / "app-spec-template" / "app-spec"
VALIDATOR = ROOT / "scripts" / "validate-app-spec.py"
SCHEMA = ROOT / "assets" / "app-spec.schema.json"

class AppSpec20Tests(unittest.TestCase):
    def setUp(self):
        self.scratch = Path(__file__).resolve().parent / ".test-workspaces"; self.scratch.mkdir(exist_ok=True)
        self.root = self.scratch / uuid.uuid4().hex; self.root.mkdir()
    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)
    def copy(self, name="spec"):
        target = self.root / name; shutil.copytree(TEMPLATE, target); return target
    def load(self, root): return json.loads((root / "app-spec.json").read_text(encoding="utf-8"))
    def save(self, root, data): (root / "app-spec.json").write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    def invoke_validator(self, root): return subprocess.run([sys.executable, str(VALIDATOR), "--require-current", str(root)], text=True, capture_output=True)
    def invalid(self, root, text):
        result = self.invoke_validator(root); self.assertNotEqual(0, result.returncode, result.stdout + result.stderr); self.assertIn(text, result.stdout)

    def test_schema_and_template_are_protocol_20(self):
        self.assertEqual("https://vibe.local/schemas/app-spec-v2.0.json", json.loads(SCHEMA.read_text())["$id"])
        result = self.invoke_validator(TEMPLATE); self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_any_1x_is_unsupported_and_migrator_refuses(self):
        spec = self.copy(); data = self.load(spec); data["schemaVersion"] = "1.4"; self.save(spec, data)
        self.invalid(spec, "unsupported protocol")
        migrated = subprocess.run([sys.executable, str(ROOT / "scripts" / "migrate-app-spec.py"), str(spec), str(self.root / "out")], text=True, capture_output=True)
        self.assertNotEqual(0, migrated.returncode); self.assertIn("unsupported protocol", migrated.stderr)
        self.assertFalse((self.root / "out").exists())

    def test_approved_and_excluded_requirements(self):
        spec = self.copy(); data = self.load(spec)
        data["requirements"].append({"id": "REQ-002", "title": "Deliberately absent", "status": "excluded", "reason": "Product decision DEC-001."})
        self.save(spec, data); self.assertEqual(0, self.invoke_validator(spec).returncode)
        data["requirements"][-1]["acceptanceScenarioIds"] = []
        self.save(spec, data); self.invalid(spec, "excluded requirement must not have")
        data = self.load(self.copy("wont")); data["requirements"][0]["priority"] = "wont"; self.save(self.root / "wont", data); self.invalid(self.root / "wont", "must be must, should, or could")

    def test_scenario_required_is_removed_and_dependencies_are_acyclic(self):
        spec = self.copy(); data = self.load(spec); data["acceptanceScenarios"][0]["required"] = False; self.save(spec, data); self.invalid(spec, "required is removed")
        cycle = self.copy("cycle"); data = self.load(cycle); data["acceptanceScenarios"][0]["dependsOnAcceptanceScenarioIds"] = ["AC-003"]; self.save(cycle, data); self.invalid(cycle, "dependency cycle")

    def test_each_ac_keeps_own_given_when_then(self):
        spec = self.copy(); path = spec / "flows" / "FLOW-001.md"; path.write_text(path.read_text().replace("Then the new value replaces the previous persisted selection.", "The value changes."), encoding="utf-8")
        self.invalid(spec, "own ordered Given/When/Then")

if __name__ == "__main__": unittest.main()
