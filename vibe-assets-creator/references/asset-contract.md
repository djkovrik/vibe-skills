# Asset requirements and delivery

## Sources of truth

`app-spec/app-spec.json.assetRequirements` is the frozen machine-readable inventory. `design.md` owns the visual direction and links ASSET IDs; screen files map actions/states to the same IDs, including intentional no-icon decisions. `app-spec/assets/` contains supplied reference/source material, not a mutable generation-output directory. Every AppSpec byte is normative and fingerprinted.

`docs/assets/asset-manifest.json` records the current delivered files and evidence, not a second task-status ledger. It is versioned production documentation and remains inside the workspace fingerprint. `.vibe/delivery-ledger.json` tracks AC/gate progress; specialist recovery packets preserve unfinished asset work. Store generation records and visual review under `docs/assets/`; actual runtime files live in Compose Resources. Update the manifest when code or asset hashes change, before checks and the final audit.

## Requirement contract

New AppSpecs include `assetRequirements` even if its inventory is empty (then explain `noAssetsReason`). Existing 2.0 specs without it retain compatibility with a warning; the asset validator rejects an absent inventory. On asset work or new delivery planning, reconcile it into the approved spec before ledger initialization or through `reconcile-spec.py` for an existing ledger. Never silently rewrite an approved spec to pass a new rule.

Each item is required. Removing a needed asset changes scope and follows the existing decision/spec-revision flow. There is no `ready` boolean that bypasses file validation. Planned creation/generation is valid at intake: `uiQuality.iconography.customAssetsStatus` may be `planned` when the structured inventory contains a create/generate item. Exact unavailable third-party brand inputs remain blocking `openQuestions`; creating an original app logo from an approved brief does not require user-supplied art.

```json
{
  "resourceSystem": "compose-multiplatform-resources",
  "deliveryManifest": "docs/assets/asset-manifest.json",
  "qualityGateId": "QG-006",
  "items": [{
    "id": "ASSET-001",
    "kind": "icon",
    "acquisition": "create-vector",
    "brief": "A simple outlined bookmark matching the approved action icon family.",
    "screenIds": ["SCREEN-001"],
    "acceptanceScenarioIds": ["AC-001"],
    "resourceName": "ic_bookmark",
    "displayDp": [24, 24],
    "maxDensity": 4,
    "transparent": true,
    "themeBehavior": "One tintable resource for light and dark themes.",
    "tintBehavior": "Use the surrounding Material content color.",
    "accessibility": "Localized bookmark action label; no duplicated adjacent text semantics.",
    "variants": [{"path": "composeApp/src/commonMain/composeResources/drawable/ic_bookmark.xml"}]
  }]
}
```

Use unique ASSET IDs, existing screen/AC IDs and stable lowercase resource names. `kind` is icon/logo/illustration. `acquisition` is reuse/create-vector/generate-raster/user-provided. The referenced required repository gate has `asset-check` and `asset-visual` surfaces and a normative `quality.md` source. Attach per-item production evidence to its AC and the complete inventory to the gate.

PNG variants additionally declare positive integer `widthPx` and `heightPx`. Each item has exactly one unqualified fallback; theme overrides share its module, name and format. This first contract supports `drawable`, `drawable-dark` and `drawable-light`, using a universal density export with explicit Compose display size. Other qualifiers require extending the validator and contract together, not bypassing its path checks. Include every selected/unselected resource as a separate item when its name differs.

## Delivery evidence

The manifest has `schemaVersion: "1.0"` and an `assets` array with exactly the requirement IDs. Each row contains:

- `id` and `outputs`: exact variant `path` and actual lowercase `sha256` for each delivered file;
- `provenance`: `method` matching acquisition, `source` (source URL/project file/tool), and `rights` (license/attribution, supplied authorization or original/generated origin; do not assert legal clearance without evidence);
- for generation, `provenance.generationRecord`: project file `path`/`sha256` describing actual tool invocation, prompt, input/output references, selected result and export steps; record observed tool/model information only;
- `usages`: production commonMain Kotlin `path`, `sha256`, `symbol`, `screenIds`. It must contain the typed `Res.drawable` reference, including through a shared resource mapping. Auditor follows that mapping to reachable screens;
- `visualEvidence`: actual local files with `path`/`sha256`, including reviewed previews/contact sheet and a review note identifying themes, actual display sizes, variants, findings and their disposition. Point to existing visual-test artifacts; do not duplicate them needlessly.

An empty inventory still has an empty delivery manifest. The static checker verifies equality, hashes, image parsing, PNG dimensions/real alpha, portable vector references and production resource references. It cannot determine that a path draws the intended symbol, that a visual-review note is truthful or that an indirect mapping is reachable. Product Designer reviews meaning/style and Visual Testing verifies real screen rendering. Auditor compares the inventory against all screens/prose, inspects image evidence and follows usages; a fabricated note, placeholder or unused resource is a gap despite a passing static check.

Run requirement-only validation before editing; include `--repository` for delivery validation. PNG inspection requires `python -m pip install -r <skill>/scripts/requirements.txt` in the verification environment (or an existing runtime with Pillow). Missing tooling is a failed check, not a skipped PNG inspection.

## Format and size policy

Simple monochrome icons should be portable XML vectors, commonly with 24 dp intrinsic dimensions and transparent unpainted space. Raster icons default to transparent RGBA PNG at 128×128 pixels. At 4× density, 24 dp needs 96 px and 32 dp needs 128 px; 64 px only covers 16 dp at 4× or 32 dp at 2×. These are package defaults derived from sampling needs, not Compose restrictions. Require at least `ceil(displayDp × maxDensity)` pixels per dimension. Declare `sizeRationale` for icon exports outside 64/128; larger illustrated icons may need larger exports. Preserve logo/illustration aspect ratios and choose their resolution from actual placement.

Set explicit UI dimensions; never let a 128 px bitmap imply a 128 dp icon or a smaller touch target. Preserve useful padding and inspect the silhouette at its smallest usage size. Transparency must include clear background pixels and visible artwork; alpha-channel presence alone does not prove it. Do not flatten to white or ship a checkerboard. Avoid embedded localized text; render it from string resources when practical.

All generated runtime artwork is accessed through Compose Multiplatform Resources. Build with the target resource plugin/version and verify Android and iOS target tasks; a parser alone does not establish runtime compatibility. Keep exact platform launcher/store derivatives with Platform/Architect because their size/mask/background constraints differ.

Official references checked 2026-09-06: [resource setup and qualifiers](https://kotlinlang.org/docs/multiplatform/compose-multiplatform-resources-setup.html), [resource loading, vector portability and Material Symbols](https://kotlinlang.org/docs/multiplatform/compose-multiplatform-resources-usage.html). The latter documents SVG's Android limitation and removing Android color/theme references from vector XML. Recheck these sources when target-library behavior changes.
