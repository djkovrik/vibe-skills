import importlib.util
import json
import shutil
import uuid
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("installation_health",ROOT/"check-vibe-installation.py")
module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)


class InstallationHealthTests(unittest.TestCase):
    def test_missing_current_and_stale_are_distinguished(self):
        base=(ROOT/".tooling"/"installation-health-tests").resolve(); root=base/uuid.uuid4().hex
        root.mkdir(parents=True)
        try:
            source=root/"package"; installed=root/"skills"; source.mkdir(); installed.mkdir()
            (source/"vibe-skills-manifest.json").write_text(json.dumps({"skillDirectories":["vibe-fixture"]}))
            (source/"vibe-fixture").mkdir(); (source/"vibe-fixture/SKILL.md").write_text("current")
            self.assertEqual("missing",module.health(source,installed)["skills"][0]["status"])
            (installed/"vibe-fixture").mkdir(); (installed/"vibe-fixture/SKILL.md").write_text("current")
            self.assertTrue(module.health(source,installed)["healthy"])
            (installed/"vibe-fixture/SKILL.md").write_text("stale")
            self.assertEqual("stale",module.health(source,installed)["skills"][0]["status"])
        finally:
            assert root.resolve().parent == base
            shutil.rmtree(root)


if __name__=="__main__": unittest.main()
