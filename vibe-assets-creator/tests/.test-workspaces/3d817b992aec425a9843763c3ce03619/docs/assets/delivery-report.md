# ASSET-002 resource hand-off

Created `composeApp/src/commonMain/composeResources/drawable/ic_bookmark.xml`: original outlined bookmark with a V-shaped notch, 24 dp intrinsic size and 24 x 24 viewport, 2-unit black stroke, transparent fill and unpainted background. The XML is also its editable source. A single unqualified fallback supports content-color tinting in both themes; no raster export or generated artwork is involved.

SHA-256: `59a33be8a8c68917732305c6c0c8b5bc2419e98b4f01dbfc1706437cc6c63e25`.

The manifest records the actual output and existing `Bookmark` usage hashes. Accessor hand-off: `demo.generated.resources.Res`, `demo.generated.resources.ic_bookmark`, and `painterResource(Res.drawable.ic_bookmark)` from `org.jetbrains.compose.resources`. These imports and reference already occur in the unchanged fixture Kotlin. Resource accessor generation and compilation have not been run. The SCREEN-001 association is the approved inventory mapping; reachable screen usage has not been demonstrated.

## Checks actually completed

- Requirement-only validator: exit 0, valid true, no warnings; executed before editing and again for recorded evidence.
- XML parsing and attribute/geometry checks: passed. Transparent fill, black 2-unit stroke, positive 24-unit viewport, 24 dp intrinsic dimensions, and no Android resource/theme references were verified from XML. The round-join stroke envelope is analytically within x=5..19 and y=2..22; this is not a rendered clipping or optical-size assessment.
- Delivery validator: exit 1, with only `ASSET-002: visualEvidence required`. Output/usage hashes, inventory, path, and portable XML checks reported no errors.
- All original AppSpec files, existing Kotlin, and AGENTS.md match their baseline hashes.

Actual commands, timestamps, stdout and exit codes are in `check-results.json`. No successful gate receipt is claimed. The orchestrator must record its own asset check through run-check.py when completing QG-006.

## Remaining evidence and decisions

`visualEvidence` intentionally remains empty. No preview, contact sheet, production screenshot, visual inspection or golden verification exists. The fixture explicitly lacks resource generation/build and screenshot tooling. Android and iOS resource compatibility, typed accessor generation, actual 24 dp optical size, stroke rendering, light/dark contrast and production clipping remain unverified. Visual Testing must render the actual resource in required screen/state/theme previews and verify goldens; Product Designer must review the resulting icon in context.

The frozen design.md and SCREEN-001.md still call ASSET-002 a save icon and mention ASSET-001 back, whereas the approved assetRequirements and fixture request specify this custom bookmark. Developer/Product Designer must reconcile the normative intent through the accepted spec-revision process; no AppSpec bytes were modified here.

Existing Bookmark.kt has no explicit size modifier, a null contentDescription, and no demonstrated parent screen. It is a fixed fixture fragment, not evidence of localized action semantics, intended tint in context, screen reachability or build completeness. Compose Expert must verify the real integration at explicit 24 dp, Material content tint and one localized action label without duplicate adjacent semantics; Architect supplies the real resource/build tasks. No Gradle task names are invented because this fixture has no build configuration or wrapper.

Next action: retain this XML and its hash; resolve the frozen prose discrepancy upstream, provide real build/preview infrastructure, then obtain and inspect production render/golden evidence, add actual evidence hashes to the manifest, and rerun delivery validation. ASSET-002 file creation is complete; AC-001 and QG-006 are not declared complete.
