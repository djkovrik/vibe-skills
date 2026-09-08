from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "vibe-developer/scripts"))
from asset_contract import validate_delivery, validate_requirements
from vibe_protocol import validate_app_spec

VECTOR = '''<vector xmlns:android="http://schemas.android.com/apk/res/android" android:width="24dp" android:height="24dp" android:viewportWidth="24" android:viewportHeight="24"><path android:fillColor="#000000" android:pathData="M6,3 L18,3 L18,21 L12,17 L6,21 Z"/></vector>'''


class AssetDeliveryTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).parent / ".test-workspaces" / uuid.uuid4().hex
        self.root.mkdir(parents=True)
        shutil.copytree(ROOT / "vibe-developer/assets/app-spec-template/app-spec", self.root / "app-spec")
        self.app = json.loads((self.root / "app-spec/app-spec.json").read_text())
        self.app["assetRequirements"]["items"] = [self.app["assetRequirements"]["items"][1]]
        self.item = self.app["assetRequirements"]["items"][0]
        self.item["resourceName"] = "ic_bookmark"
        self.item["acquisition"] = "create-vector"
        self.item["variants"] = [{"path":"shared/compose/src/commonMain/composeResources/drawable/ic_bookmark.xml"}]
        self.app["uiQuality"]["iconography"]["customAssetsStatus"] = "planned"
        self.save_spec()
        self.output = self.write(self.item["variants"][0]["path"], VECTOR)
        self.usage = self.write("shared/compose/src/commonMain/kotlin/Bookmark.kt", 'import demo.generated.resources.Res\nimport demo.generated.resources.ic_bookmark\nimport org.jetbrains.compose.resources.painterResource\n@Composable fun Bookmark() { Icon(painterResource(Res.drawable.ic_bookmark), contentDescription = null) }')
        self.visual = self.write("docs/assets/review.md", "Fixture-only review note. Real delivery requires observed preview/golden review, not this synthetic evidence.")
        self.row = {"id": self.item["id"], "outputs": [self.evidence(self.output)], "provenance":{"method":"create-vector","source":"Original vector geometry", "rights":"Original fixture artwork"}, "usages":[dict(self.evidence(self.usage), symbol="Bookmark", screenIds=["SCREEN-001"])], "visualEvidence":[self.evidence(self.visual)]}
        self.manifest = {"schemaVersion":"1.0", "assets":[self.row]}
        self.save_manifest()

    def tearDown(self):
        shutil.rmtree(self.root)

    def write(self, relative, text):
        path = self.root / relative; path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8"); return path

    def evidence(self, path):
        return {"path": path.relative_to(self.root).as_posix(), "sha256":hashlib.sha256(path.read_bytes()).hexdigest()}

    def save_spec(self): self.write("app-spec/app-spec.json", json.dumps(self.app))
    def save_manifest(self): self.write("docs/assets/asset-manifest.json", json.dumps(self.manifest))
    def errors(self): self.save_manifest(); return validate_delivery(self.app, self.root)[0]

    def png(self, alpha=True):
        from PIL import Image
        self.output.unlink(missing_ok=True)
        self.item["variants"] = [{"path":"shared/compose/src/commonMain/composeResources/drawable/ic_bookmark.png", "widthPx":128, "heightPx":128}]
        self.output = self.root / self.item["variants"][0]["path"]
        image = Image.new("RGBA", (128,128), (0,0,0,0 if alpha else 255))
        image.putpixel((64,64), (0,0,0,255)); image.save(self.output)
        self.row["outputs"] = [self.evidence(self.output)]

    def test_planned_creation_passes_intake_without_artwork(self):
        self.output.unlink()
        self.assertEqual([], validate_app_spec(self.root / "app-spec")[1])
        self.assertTrue(any("missing file" in e for e in self.errors()))

    def test_vector_delivery_cli_and_required_inventory(self):
        self.assertEqual([], self.errors())
        result = subprocess.run([sys.executable, str(ROOT / "vibe-assets-creator/scripts/validate-assets.py"), "--app-spec-root", str(self.root / "app-spec"), "--repository", str(self.root)], capture_output=True, text=True)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        del self.app["assetRequirements"]
        errors, warnings = validate_requirements(self.app)
        self.assertIn("assetRequirements is required", errors); self.assertEqual([], warnings)
        self.save_spec()
        result = subprocess.run([sys.executable, str(ROOT / "vibe-assets-creator/scripts/validate-assets.py"), "--app-spec-root", str(self.root / "app-spec")], capture_output=True, text=True)
        self.assertNotEqual(0, result.returncode)

    def test_stale_output_and_unused_comment_are_rejected(self):
        self.output.write_text(VECTOR.replace("#000000", "#111111"))
        self.assertTrue(any("stale file hash" in e for e in self.errors()))
        self.row["outputs"] = [self.evidence(self.output)]
        self.usage.write_text('// Res.drawable.ic_bookmark\nfun Bookmark() {}')
        self.row["usages"][0].update(self.evidence(self.usage))
        self.assertTrue(any("reference missing" in e for e in self.errors()))

    def test_png_alpha_dimensions_and_density(self):
        self.png(); self.assertEqual([], self.errors())
        self.png(alpha=False)
        self.assertTrue(any("transparent background" in e for e in self.errors()))
        self.png(); self.item["variants"][0].update(widthPx=64,heightPx=64)
        self.assertTrue(any("resolution" in e for e in self.errors()))
        self.item["maxDensity"] = 2
        self.assertTrue(any("dimensions mismatch" in e for e in self.errors()))
        from PIL import Image
        image = Image.new("RGBA", (64,64), (0,0,0,0)); image.putpixel((32,32), (0,0,0,255)); image.save(self.output)
        self.row["outputs"] = [self.evidence(self.output)]
        self.assertEqual([], self.errors())

    def test_missing_theme_variant_and_fallback(self):
        dark = {"path":"shared/compose/src/commonMain/composeResources/drawable-dark/ic_bookmark.xml"}
        self.item["variants"].append(dark)
        self.assertTrue(any("output variants mismatch" in e for e in self.errors()))
        self.item["variants"] = [dark]
        self.assertTrue(any("fallback" in e for e in self.errors()))

    def test_external_paths_invalid_references_and_duplicate_inventory(self):
        self.item["variants"][0]["path"] = "../outside.xml"
        self.assertTrue(any("invalid variant path" in e for e in self.errors()))
        self.item["screenIds"] = ["SCREEN-999"]
        self.assertTrue(any("screenIds" in e for e in self.errors()))
        self.app["assetRequirements"]["items"].append(copy.deepcopy(self.item))
        self.assertTrue(any("duplicate asset ID" in e for e in self.errors()))

    def test_vector_android_references_and_blank_paths_rejected(self):
        self.output.write_text(VECTOR.replace("#000000", "@android:color/white"))
        self.row["outputs"] = [self.evidence(self.output)]
        self.assertTrue(any("not portable" in e for e in self.errors()))
        self.output.write_text(VECTOR.replace('android:pathData="M6,3 L18,3 L18,21 L12,17 L6,21 Z"', 'android:pathData=""'))
        self.row["outputs"] = [self.evidence(self.output)]
        self.assertTrue(any("no path data" in e for e in self.errors()))

    def test_generation_requires_actual_record(self):
        self.png()
        self.item["acquisition"] = "generate-raster"; self.row["provenance"]["method"] = "generate-raster"
        self.assertTrue(any("generation record" in e for e in self.errors()))
        record = self.write("docs/assets/generation.json", json.dumps({"fixture":True,"note":"Synthetic generation metadata only for testing file binding."}))
        self.row["provenance"]["generationRecord"] = self.evidence(record)
        self.assertEqual([], self.errors())

    def test_invalid_ledger_fails_preflight_before_asset_walk(self):
        self.output.unlink()
        subprocess.run(["git","init","-q",str(self.root)], check=True)
        spec = importlib.util.spec_from_file_location("asset_test_ledger", ROOT / "vibe-developer/scripts/validate-delivery-ledger.py")
        module = importlib.util.module_from_spec(spec); sys.modules[spec.name] = module; spec.loader.exec_module(module)
        # Readiness rejects corrupt metadata before expensive artifact validation.
        ledger = {"schemaVersion":"2.0", "appSpec":{"root":"app-spec"}, "execution":{}, "acceptanceScenarios":[], "qualityGates":[]}
        path = self.write(".vibe/delivery-ledger.json", json.dumps(ledger))
        result = module.validate_ledger(self.root, path, closure=False)
        self.assertTrue(any("ledgerDigest" in e for e in result.errors), result.errors)
        self.assertTrue(any("missing file" in e for e in self.errors()))

    def test_empty_inventory_and_malformed_extension(self):
        self.assertTrue(validate_delivery([], self.root)[0])
        self.app["assetRequirements"]["items"] = []
        self.assertTrue(any("noAssetsReason" in e for e in self.errors()))
        self.app["assetRequirements"]["noAssetsReason"] = "This surface contains text only by design."
        self.manifest["assets"] = []
        self.assertEqual([], self.errors())
        self.app["assetRequirements"]["items"] = None
        self.save_spec()
        self.assertTrue(any("items must be an array" in e for e in validate_app_spec(self.root / "app-spec")[1]))

    def test_resource_name_collision_is_rejected(self):
        self.write(self.output.relative_to(self.root).as_posix().replace(".xml", ".png"), "invalid old export")
        self.assertTrue(any("resource name collision" in e for e in self.errors()))

if __name__ == "__main__": unittest.main()
