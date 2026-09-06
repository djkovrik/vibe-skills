"""Asset requirements and delivery checks; Pillow is needed only for PNG inspection."""
from __future__ import annotations

import hashlib
import json
import math
import re
import xml.etree.ElementTree as ET
from pathlib import Path, PurePosixPath


def local_path(root: Path, value: str) -> Path:
    if not isinstance(value, str) or not value or "\\" in value or ":" in value:
        raise ValueError("expected repository-relative POSIX path")
    p = PurePosixPath(value)
    if p.is_absolute() or ".." in p.parts:
        raise ValueError("path escapes repository")
    target = (root / value).resolve()
    target.relative_to(root.resolve())
    return target


def positive(value):
    return type(value) in (int, float) and math.isfinite(value) and value > 0


def validate_requirements(app: dict) -> tuple[list[str], list[str]]:
    errors, warnings = [], []
    if not isinstance(app, dict): return ["AppSpec must be an object"], []
    contract = app.get("assetRequirements")
    if contract is None:
        return [], ["Legacy AppSpec has no assetRequirements; reconcile the screen inventory before adding assets. File completeness is not machine-verified."]
    if not isinstance(contract, dict):
        return ["assetRequirements must be an object"], []
    if contract.get("resourceSystem") != "compose-multiplatform-resources":
        errors.append("assetRequirements.resourceSystem must be compose-multiplatform-resources")
    if contract.get("deliveryManifest") != "docs/assets/asset-manifest.json":
        errors.append("assetRequirements.deliveryManifest must be docs/assets/asset-manifest.json")
    gates = app.get("qualityGates")
    gate = next((g for g in gates if isinstance(g, dict) and g.get("id") == contract.get("qualityGateId")), {}) if isinstance(gates, list) else {}
    surfaces = gate.get("verificationSurfaces")
    if gate.get("category") != "repository" or gate.get("requirement") != "required" or not isinstance(surfaces, list) or any(not isinstance(s, str) for s in surfaces) or not {"asset-check", "asset-visual"} <= set(surfaces):
        errors.append("assetRequirements requires a required repository gate with asset-check and asset-visual surfaces")
    items = contract.get("items")
    if not isinstance(items, list):
        return errors + ["assetRequirements.items must be an array"], warnings
    if not items and (not isinstance(contract.get("noAssetsReason"), str) or not contract["noAssetsReason"].strip()):
        errors.append("empty assetRequirements.items requires noAssetsReason")
    ids, paths, names = set(), set(), set()
    for item in items:
        if not isinstance(item, dict):
            errors.append("asset requirement must be an object"); continue
        label = str(item.get("id", "asset"))
        def fail(message): errors.append(f"{label}: {message}")
        ident = item.get("id")
        if not isinstance(ident, str) or not re.fullmatch(r"ASSET-\d{3,}", ident) or ident in ids: fail("invalid or duplicate asset ID")
        else: ids.add(ident)
        if item.get("kind") not in ("icon", "logo", "illustration"): fail("invalid kind")
        if item.get("acquisition") not in ("reuse", "create-vector", "generate-raster", "user-provided"): fail("invalid acquisition")
        for field in ("brief", "themeBehavior", "tintBehavior", "accessibility"):
            if not isinstance(item.get(field), str) or not item[field].strip(): fail(f"{field} is required")
        scenarios = app.get("acceptanceScenarios")
        ac_ids = [a.get("id") for a in scenarios if isinstance(a, dict)] if isinstance(scenarios, list) else []
        for field, available in (("screenIds", app.get("screens") or []), ("acceptanceScenarioIds", ac_ids)):
            values = item.get(field)
            if not isinstance(values, list) or not values or any(not isinstance(v, str) or v not in available for v in values): fail(f"{field} must reference declared obligations/screens")
        name = item.get("resourceName")
        if not isinstance(name, str) or not re.fullmatch(r"[a-z][a-z0-9_]*", name): fail("invalid resourceName")
        size = item.get("displayDp")
        if not isinstance(size, list) or len(size) != 2 or not all(positive(v) for v in size): fail("displayDp requires positive width and height"); size = [0, 0]
        density = item.get("maxDensity")
        if not positive(density): fail("maxDensity must be positive"); density = 1
        if type(item.get("transparent")) is not bool: fail("transparent must be boolean")
        if item.get("kind") == "icon" and item.get("transparent") is not True: fail("icons require a transparent background")
        variants = item.get("variants")
        if not isinstance(variants, list) or not variants: fail("variants are required"); continue
        defaults, modules, formats = 0, set(), set()
        for variant in variants:
            if not isinstance(variant, dict): fail("variant must be an object"); continue
            path = variant.get("path", "")
            try: local_path(Path.cwd(), path)
            except (ValueError, OSError): fail("invalid variant path"); continue
            p = PurePosixPath(path)
            # v1 deliberately uses a universal density export and optional theme override.
            match = re.fullmatch(r"(.+)/src/commonMain/composeResources/(drawable|drawable-dark|drawable-light)/([^/]+)\.(xml|png)", path)
            if not match or p.stem != name: fail("variant must be a named commonMain Compose drawable XML/PNG"); continue
            module, directory, _, fmt = match.groups(); modules.add(module); formats.add(fmt)
            if directory == "drawable": defaults += 1
            if path in paths: fail("duplicate output path")
            paths.add(path)
            if fmt == "png":
                width, height = variant.get("widthPx"), variant.get("heightPx")
                if type(width) is not int or type(height) is not int or width <= 0 or height <= 0: fail("PNG requires positive integer widthPx/heightPx"); continue
                if width < math.ceil(size[0] * density) or height < math.ceil(size[1] * density): fail("PNG resolution is below displayDp * maxDensity")
                if item.get("kind") == "icon" and (width, height) not in ((128, 128), (64, 64)) and not item.get("sizeRationale"): fail("nonstandard icon export requires sizeRationale")
        if defaults != 1: fail("exactly one unqualified drawable fallback is required")
        if len(modules) != 1: fail("variants must share one resource module")
        if len(formats) != 1: fail("variants must share one runtime format")
        if item.get("acquisition") == "generate-raster" and formats != {"png"}: fail("generated raster outputs must be PNG")
        key = (next(iter(modules), ""), name)
        if isinstance(name, str):
            if key in names: fail("duplicate resource name in module")
            names.add(key)
    return errors, warnings


def inspect_image(path: Path, requirement: dict, variant: dict) -> list[str]:
    errors = []
    if path.suffix == ".xml":
        try:
            raw = path.read_text(encoding="utf-8-sig")
            vector = ET.fromstring(raw)
            if vector.tag != "vector": errors.append("XML must be a vector drawable")
            ns = "{http://schemas.android.com/apk/res/android}"
            if not any(p.get(ns + "pathData", "").strip() for p in vector.iter("path")): errors.append("vector has no path data")
            for key in ("viewportWidth", "viewportHeight"):
                if not positive(float(vector.get(ns + key, "0"))): errors.append("vector viewport must be positive")
            for key in ("width", "height"):
                if not re.fullmatch(r"[0-9]+(?:\.[0-9]+)?dp", vector.get(ns + key, "")): errors.append("vector requires intrinsic dp size")
            if any("@" in v or "?" in v for e in vector.iter() for v in e.attrib.values()): errors.append("Android resource/theme references are not portable")
        except (ET.ParseError, ValueError, OSError, UnicodeError) as exc: errors.append(f"invalid vector: {exc}")
    else:
        try:
            from PIL import Image
            with Image.open(path) as img:
                img.load()
                if img.format != "PNG": errors.append("file is not PNG")
                if img.size != (variant["widthPx"], variant["heightPx"]): errors.append("PNG dimensions mismatch")
                if requirement["transparent"]:
                    extrema = img.convert("RGBA").getchannel("A").getextrema()
                    if extrema[0] != 0 or extrema[1] == 0: errors.append("PNG must contain transparent background and visible pixels")
        except ImportError: errors.append("PNG inspection requires Pillow; install the assets creator requirements in the verification Python environment")
        except (OSError, ValueError, KeyError, Image.DecompressionBombError) as exc: errors.append(f"invalid PNG: {exc}")
    return errors


def validate_delivery(app: dict, repository: Path) -> tuple[list[str], list[str]]:
    errors, warnings = validate_requirements(app)
    if errors: return errors, warnings
    contract = app.get("assetRequirements")
    if contract is None: return errors, warnings
    root = repository.resolve()
    try:
        manifest = json.loads(local_path(root, contract["deliveryManifest"]).read_text(encoding="utf-8-sig"))
        if not isinstance(manifest, dict) or manifest.get("schemaVersion") != "1.0" or not isinstance(manifest.get("assets"), list): raise ValueError("expected asset manifest 1.0")
    except (OSError, ValueError) as exc: return [f"asset manifest: {exc}"], warnings
    rows = manifest["assets"]
    if any(not isinstance(row, dict) or not isinstance(row.get("id"), str) for row in rows): return ["invalid asset manifest row"], warnings
    delivered = {row["id"]: row for row in rows}
    if len(delivered) != len(rows) or set(delivered) != {i["id"] for i in contract["items"]}: errors.append("asset manifest inventory mismatch")
    for item in contract["items"]:
        row = delivered.get(item["id"])
        if row is None: continue
        label = item["id"]
        def fail(message): errors.append(f"{label}: {message}")
        def checked_file(record):
            if not isinstance(record, dict): raise ValueError("file evidence must be an object")
            path = local_path(root, record.get("path"))
            if not path.is_file(): raise ValueError(f"missing file: {record.get('path')}")
            if hashlib.sha256(path.read_bytes()).hexdigest() != record.get("sha256"): raise ValueError(f"stale file hash: {record.get('path')}")
            return path
        outputs = row.get("outputs", [])
        if not isinstance(outputs, list) or any(not isinstance(o, dict) for o in outputs): fail("invalid outputs"); continue
        if sorted(str(o.get("path")) for o in outputs) != sorted(v["path"] for v in item["variants"]): fail("output variants mismatch")
        variants = {v["path"]: v for v in item["variants"]}
        for output in outputs:
            try:
                path = checked_file(output)
                if output.get("path") in variants:
                    for error in inspect_image(path, item, variants[output["path"]]): fail(error)
                    siblings = [p for p in path.parent.iterdir() if p.is_file() and p.stem == path.stem and p.suffix.lower() in {".xml", ".png", ".svg", ".webp", ".jpg", ".jpeg", ".bmp"}]
                    if len(siblings) != 1: fail("resource name collision in drawable directory")
            except (ValueError, OSError) as exc: fail(str(exc))
        provenance = row.get("provenance", {})
        if not isinstance(provenance, dict): fail("invalid provenance"); provenance = {}
        if provenance.get("method") != item["acquisition"]: fail("acquisition differs from approved requirement")
        for field in ("source", "rights"):
            if not isinstance(provenance.get(field), str) or not provenance[field].strip(): fail(f"provenance.{field} required")
        if item["acquisition"] == "generate-raster":
            try: checked_file(provenance.get("generationRecord"))
            except (ValueError, OSError) as exc: fail(f"generation record: {exc}")
        usages = row.get("usages")
        if not isinstance(usages, list) or not usages: fail("production usages required"); usages = []
        covered = set()
        for usage in usages:
            try:
                path = checked_file(usage)
                if path.suffix != ".kt" or "/src/commonMain/" not in path.as_posix(): raise ValueError("usage must name production commonMain Kotlin")
                source = path.read_text(encoding="utf-8-sig")
                source = re.sub(r"/\*.*?\*/|//[^\n]*", "", source, flags=re.S)
                source = re.sub(r'""".*?"""|"(?:\\.|[^"\\])*"', '""', source, flags=re.S)
                symbol = usage.get("symbol")
                if not isinstance(symbol, str) or not symbol or symbol not in source: raise ValueError("production symbol missing")
                if not re.search(r"\bRes\s*\.\s*drawable\s*\.\s*" + re.escape(item["resourceName"]) + r"\b", source): raise ValueError("Compose Res.drawable reference missing")
                screens = usage.get("screenIds")
                if not isinstance(screens, list) or any(not isinstance(s, str) or s not in item["screenIds"] for s in screens): raise ValueError("invalid usage screen IDs")
                covered.update(screens)
            except (ValueError, OSError) as exc: fail(str(exc))
        if covered != set(item["screenIds"]): fail("production usage screen coverage missing")
        visual = row.get("visualEvidence")
        if not isinstance(visual, list) or not visual: fail("visualEvidence required"); visual = []
        for record in visual:
            try: checked_file(record)
            except (ValueError, OSError) as exc: fail(f"visual evidence: {exc}")
    return errors, warnings
