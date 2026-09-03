from __future__ import annotations

import copy
import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = SKILL_ROOT / "assets" / "app-spec-template" / "app-spec"
VALIDATOR = SKILL_ROOT / "scripts" / "validate-app-spec.py"
MIGRATOR = SKILL_ROOT / "scripts" / "migrate-app-spec.py"
SCHEMA = SKILL_ROOT / "assets" / "app-spec.schema.json"


class AppSpec14Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.scratch = Path(__file__).resolve().parent / ".test-workspaces"
        self.scratch.mkdir(exist_ok=True)
        self.root = self.scratch / uuid.uuid4().hex
        self.root.mkdir()

    def tearDown(self) -> None:
        shutil.rmtree(self.root, ignore_errors=True)
        try:
            self.scratch.rmdir()
        except OSError:
            pass

    def copy_template(self, name: str = "spec") -> Path:
        destination = self.root / name
        shutil.copytree(TEMPLATE, destination)
        return destination

    def load(self, spec: Path) -> dict[str, object]:
        return json.loads((spec / "app-spec.json").read_text(encoding="utf-8"))

    def save(self, spec: Path, data: dict[str, object]) -> None:
        (spec / "app-spec.json").write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def validate(self, spec: Path, require_current: bool = True) -> subprocess.CompletedProcess[str]:
        command = [sys.executable, str(VALIDATOR)]
        if require_current:
            command.append("--require-current")
        command.append(str(spec))
        return subprocess.run(command, text=True, capture_output=True, check=False)

    def assert_invalid(self, spec: Path, fragment: str) -> None:
        result = self.validate(spec)
        self.assertNotEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn(fragment, result.stdout)

    def test_schema_is_json_and_current_template_is_valid(self) -> None:
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        self.assertEqual("https://vibe.local/schemas/app-spec-v1.4.json", schema["$id"])
        result = self.validate(TEMPLATE)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("RESULT: VALID", result.stdout)

    def test_legacy_warns_and_require_current_rejects(self) -> None:
        for minor in range(4):
            with self.subTest(version=f"1.{minor}"):
                spec = self.copy_template(f"legacy-{minor}")
                data = self.load(spec)
                data["schemaVersion"] = f"1.{minor}"
                self.save(spec, data)

                compatible = self.validate(spec, require_current=False)
                self.assertEqual(0, compatible.returncode, compatible.stdout + compatible.stderr)
                self.assertIn(f"Legacy AppSpec 1.{minor}", compatible.stdout)

                strict = self.validate(spec, require_current=True)
                self.assertNotEqual(0, strict.returncode)
                self.assertIn("--require-current requires AppSpec 1.4", strict.stdout)

    def test_missing_duplicate_and_mislinked_acceptance_scenarios_fail(self) -> None:
        missing = self.copy_template("missing")
        data = self.load(missing)
        data["acceptanceScenarios"] = data["acceptanceScenarios"][:-1]
        self.save(missing, data)
        self.assert_invalid(missing, "must be equal")

        duplicate = self.copy_template("duplicate")
        data = self.load(duplicate)
        data["acceptanceScenarios"].append(copy.deepcopy(data["acceptanceScenarios"][0]))
        self.save(duplicate, data)
        self.assert_invalid(duplicate, "Duplicate acceptance scenario IDs")

        mislinked = self.copy_template("mislinked")
        data = self.load(mislinked)
        data["acceptanceScenarios"][0]["flowId"] = "FLOW-999"
        self.save(mislinked, data)
        self.assert_invalid(mislinked, "flowId must reference a declared flow")

    def test_each_acceptance_scenario_needs_own_given_when_then(self) -> None:
        spec = self.copy_template()
        flow = spec / "flows" / "FLOW-001.md"
        text = flow.read_text(encoding="utf-8")
        text = text.replace("Then the new value replaces the previous persisted selection.", "The value changes.")
        flow.write_text(text, encoding="utf-8")
        self.assert_invalid(spec, "AC-003 section must contain its own ordered Given/When/Then")

    def test_managed_entity_requires_complete_and_well_formed_decisions(self) -> None:
        missing_crud = self.copy_template("missing-crud")
        data = self.load(missing_crud)
        del data["managedEntities"][0]["operations"]["delete"]
        self.save(missing_crud, data)
        self.assert_invalid(missing_crud, "operations.delete must explicitly decide")

        required_without_ac = self.copy_template("required-without-ac")
        data = self.load(required_without_ac)
        data["managedEntities"][0]["operations"]["delete"] = {
            "status": "required",
            "acceptanceScenarioIds": [],
        }
        self.save(required_without_ac, data)
        self.assert_invalid(required_without_ac, "operations.delete requires acceptanceScenarioIds")

        no_reason = self.copy_template("no-reason")
        data = self.load(no_reason)
        data["managedEntities"][0]["operations"]["delete"] = {"status": "not-applicable"}
        self.save(no_reason, data)
        self.assert_invalid(no_reason, "operations.delete.reason is required")

    def test_missing_mandatory_and_malformed_conditional_quality_gates_fail(self) -> None:
        no_android = self.copy_template("no-android")
        data = self.load(no_android)
        data["qualityGates"] = [gate for gate in data["qualityGates"] if gate["platform"] != "android"]
        self.save(no_android, data)
        self.assert_invalid(no_android, "required platform gate for target android")

        no_condition = self.copy_template("no-condition")
        data = self.load(no_condition)
        del data["qualityGates"][-1]["condition"]
        self.save(no_condition, data)
        self.assert_invalid(no_condition, "condition is required for a conditional quality gate")

    def test_migrator_never_overwrites_and_leaves_review_blocking(self) -> None:
        source = self.copy_template("legacy")
        data = self.load(source)
        data["schemaVersion"] = "1.3"
        data.pop("acceptanceScenarios")
        data.pop("managedEntities")
        data.pop("qualityGates")
        self.save(source, data)
        source_before = (source / "app-spec.json").read_bytes()
        output = self.root / "migrated"

        migrated = subprocess.run(
            [sys.executable, str(MIGRATOR), str(source), str(output)],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, migrated.returncode, migrated.stdout + migrated.stderr)
        self.assertEqual(source_before, (source / "app-spec.json").read_bytes())
        draft = self.load(output)
        self.assertEqual("1.4", draft["schemaVersion"])
        self.assertTrue(draft["acceptanceScenarios"])
        self.assertTrue(all(item["reviewStatus"] == "needs-review" for item in draft["acceptanceScenarios"]))
        self.assertTrue(any(item.get("blocking") and item.get("status") == "open" for item in draft["openQuestions"] if isinstance(item, dict)))
        strict = self.validate(output)
        self.assertNotEqual(0, strict.returncode)
        self.assertIn("needs-review", strict.stdout)
        output_before = (output / "app-spec.json").read_bytes()

        refused = subprocess.run(
            [sys.executable, str(MIGRATOR), str(source), str(output)],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertNotEqual(0, refused.returncode)
        self.assertIn("refusing to overwrite", refused.stdout)
        self.assertEqual(output_before, (output / "app-spec.json").read_bytes())


if __name__ == "__main__":
    unittest.main()
