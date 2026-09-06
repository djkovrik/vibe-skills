# ASSIGN-ASSET-FORWARD-001

Owner: vibe-assets-creator. Standalone forward evaluation delegated by skill-creator.
Obligations: ASSET-002, AC-001, QG-006.

Request: create the required approved custom bookmark icon from app-spec/app-spec.json, prepare resource delivery evidence, and report what can be delivered and what remains unverified.

Boundaries: composeApp/src/commonMain/composeResources/drawable/ic_bookmark.xml, docs/assets/**, .vibe/**. Do not edit AppSpec, existing Kotlin, AGENTS.md, or any file outside this fixture. Build/resource generation and screenshot tooling are unavailable. Never invent rendering or build evidence.

Approved source: app-spec/app-spec.json assetRequirements ASSET-002: original outline bookmark, V-shaped notch, 24 dp viewport, 2-unit black strokes, unpainted transparent background. Destination: composeApp/src/commonMain/composeResources/drawable/ic_bookmark.xml. Acquisition: create-vector. One shared tintable fallback; Material content tint; no generation or external source needed.

Manifest: docs/assets/asset-manifest.json. Existing usage: composeApp/src/commonMain/kotlin/Bookmark.kt, Bookmark, Res.drawable.ic_bookmark. This source is fixed and is not build/reachability evidence.

Observed mismatch: design.md and SCREEN-001.md still describe ASSET-002 as save and ASSET-001 as back, with no custom artwork. The explicit approved fixture request and assetRequirements govern creation here. Keep these normative files unchanged; report reconciliation as unresolved upstream.

Next action: checkpoint, create XML and actual hashes, run delivery validation, report missing visual/build evidence honestly. No screenshots, generation outputs or variants have been obtained.
