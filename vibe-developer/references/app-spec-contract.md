# Vibe AppSpec Protocol 2.0

## Boundary and compatibility

AppSpec 2.0 is the only implementation input accepted by `$vibe-developer`. Any 1.x artifact fails with `unsupported protocol`; migration, compatibility mode, automatic deletion, and automatic reinitialization are intentionally absent. A new 2.0 specification must be explicitly prepared and approved.

The required tree is:

```text
app-spec/
  app-spec.json
  product.md
  design.md
  domain.md
  data.md
  quality.md
  flows/FLOW-*.md
  screens/SCREEN-*.md
  assets/**
```

Every regular file anywhere in this tree is normative, including binary assets and otherwise unrecognized extensions. `compute_app_spec_fingerprint()` hashes the relative path and exact bytes of all of them. Adding, removing, renaming, or changing any file invalidates ledger fingerprints, receipts, audit requests, and audits.

## Requirements and atomic scenarios

Requirements have one of two shapes:

- active: `status: approved`, `priority: must|should|could`, and a non-empty unique `acceptanceScenarioIds` array;
- excluded: `status: excluded`, a non-empty product-specific `reason`, and no `acceptanceScenarioIds` field.

`wont` and scenario-level `required` are removed. Every declared acceptance scenario is an obligation; optionality is expressed only by excluding its requirement. The union of active requirement links equals the scenario inventory exactly, with one owning requirement per AC.

Each scenario declares `id`, `title`, `requirementId`, `flowId`, non-empty `screenIds`, `kind`, `subject`, one `operation`, non-empty `verificationSurfaces`, and `dependsOnAcceptanceScenarioIds` (an empty array is valid). Dependencies reference existing ACs, may not self-reference, and must form a directed acyclic graph. External package dependencies must be verified/waived or have an accepted current behavioral contract under the flow contract; this does not change final AC verification. Related scenarios inside one registered capability package may be implemented together in dependency order; verification obligations remain independent.

Each AC has its own `## AC-NNN` flow section with ordered Given/When/Then. One AC represents one externally observable action, state, or failure. Flow and screen filenames equal their IDs.

## Managed operations and quality gates

Each managed entity explicitly decides `create`, `read`, `update`, and `delete`, plus any domain-specific operations. A decision is either `{status: required, acceptanceScenarioIds:[...]}` or `{status: not-applicable, reason:"..."}`. Required links must match both scenario `subject` and `operation`.

Each quality gate declares `id`, `title`, `category`, `platform`, `requirement`, `verificationMethod`, `contractSource`, and non-empty `verificationSurfaces`. Categories are `repository`, `platform`, `external`, and `release`; requirement is `required` or `conditional`, with a non-empty condition for the latter. Include a required repository gate, a required release gate, and a required platform gate for each target.

The existing localization, architecture, UI-quality, monetization, privacy, and unresolved-question contracts remain normative in the JSON and Markdown. Blocking open questions prevent approval. In particular, English remains the base locale, locale selection remains system-only, Compose UI retains deterministic preview/golden coverage, and ads retain the privacy-before-initialization contract.

## Shared inventory and validation

All Protocol tools import `vibe_protocol.canonical_inventory`; no validator may maintain a private inventory interpretation. The canonical inventory contains approved requirement IDs, excluded requirement IDs, all AC IDs, required managed-operation IDs, and all quality-gate IDs.

Run:

```powershell
python .\vibe-developer\scripts\validate-app-spec.py --require-current <app-spec-directory>
```

The compatibility flag is accepted for a stable command line, but validation is always strict 2.0. Validation is read-only and checks requirement states, links, per-AC Given/When/Then, dependency cycles, operation decisions, gate coverage, file structure, and blocking questions.

## Asset requirements (package 2.2)

Every AppSpec requires `assetRequirements` as defined in the [asset contract](../../vibe-assets-creator/references/asset-contract.md). Intake validates approved briefs, IDs, output destinations and sizes, allowing planned creation/generation. Delivery validates actual output via the required asset gate. Runtime files and mutable delivery evidence are outside the frozen AppSpec; accepted scope changes use spec reconciliation. Missing assetRequirements is an intake error; legacy-spec compatibility is absent.
