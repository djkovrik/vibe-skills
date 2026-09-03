# Vibe AppSpec 1.4 contract

## Contents

- [Boundary](#boundary)
- [Required structure](#required-structure)
- [Identifiers and links](#identifiers-and-links)
- [UI quality contract](#ui-quality-contract)
- [Localization contract](#localization-contract)
- [Architecture contract](#architecture-contract)
- [Atomic behavior contract](#atomic-behavior-contract)
- [Managed entity contract](#managed-entity-contract)
- [Quality gate inventory](#quality-gate-inventory)
- [Legacy migration](#legacy-migration)
- [Monetization and privacy contract](#monetization-and-privacy-contract)
- [Validation](#validation)

## Boundary

Consume an already prepared specification. Do not restart product discovery during implementation. Put unresolved choices in `openQuestions`; do not silently decide them.

## Required structure

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
  assets/
```

`app-spec.json` declares app metadata, requirements, atomic acceptance scenarios, managed-entity operation decisions, flow/screen IDs, capabilities, constraints, localization, architecture, quality gates, and open questions. Additional fields are allowed. `design.md` and `uiQuality` are required for AppSpec 1.1+; `localization` and the localized-text Markdown contract are required for AppSpec 1.2+; `architecture` is required for AppSpec 1.3+; `acceptanceScenarios`, `managedEntities`, and `qualityGates` are required for AppSpec 1.4.

The validator accepts 1.0–1.3 as legacy inputs and warns that they are suitable only for narrow specialist work. A complete or cross-cutting `$vibe-developer` cycle must validate an approved 1.4 specification with `--require-current`. Schema major versions other than 1 and versions newer than this contract are unsupported.

The Markdown files define product intent, design direction, domain semantics, data contracts, quality gates, flows, acceptance scenarios, screen states, accessibility, localization, iconography/assets, preview/golden coverage, and allowed monetization slots.

## Identifiers and links

- Use stable `REQ-NNN`, `FLOW-NNN`, `SCREEN-NNN`, `AC-NNN`, and `QG-NNN` identifiers.
- Put each acceptance scenario in exactly one flow under its own `## AC-NNN` section. That section, rather than a shared flow preamble, contains its own ordered Given/When/Then.
- Keep the union of every requirement's `acceptanceScenarioIds` exactly equal to the IDs in `acceptanceScenarios`; duplicates and orphans are invalid.
- Link every acceptance scenario back to exactly one declared requirement and flow and to one or more declared screens. Its flow file links the same requirement and screens.
- Link screens to requirements and flows.
- Keep filenames equal to their stable flow/screen IDs.

## Atomic behavior contract

For AppSpec 1.4, each `acceptanceScenarios` entry declares `id`, `title`, `requirementId`, `flowId`, `screenIds`, `kind`, `subject`, `operation`, and `verificationSurfaces`. `kind` is one of `action`, `state`, or `failure`. One entry describes one observable outcome and one primary action, state, or failure; split compound outcomes into separate ACs even when they share a flow.

`subject` is the behavior owner or managed entity, `operation` is the single behavior being exercised, and `verificationSurfaces` names the independent surfaces that must demonstrate it, such as `domain-test`, `component-test`, `settings-integration-test`, `platform-test`, or `ui-golden`. Detailed conditions remain in `FLOW-*.md`; the JSON inventory is the stable planning and traceability boundary.

Migration may add `reviewStatus: needs-review`, but such a scenario is invalid for implementation until a human has reviewed it. New approved specs may use `reviewStatus: approved` or omit the optional field.

## Managed entity contract

Every item in `managedEntities` names an `entity` and an `operations` object. The object explicitly contains all four `create`, `read`, `update`, and `delete` cells. Each cell is either:

- `{ "status": "required", "acceptanceScenarioIds": ["AC-NNN"] }`; or
- `{ "status": "not-applicable", "reason": "product-specific explanation" }`.

Additional operation keys such as `rename`, `reuse`, `restore`, or `delete-all` use the same decision shape. A required operation has at least one existing AC whose `subject` equals the entity and whose `operation` equals the operation key. Do not group an omitted behavior into a generic partial status; absence needs an explicit not-applicable decision and reason.

An empty `managedEntities` array is valid only when review has established that the product manages no entities. If migration cannot determine that safely, it leaves a blocking question.

## Quality gate inventory

Every `qualityGates` entry declares a stable `id`, `title`, `category`, `platform`, `requirement`, `verificationMethod`, and `contractSource`. Categories are `repository`, `platform`, `external`, and `release`. `platform` is `all` or one declared app target. `contractSource` points to a normative AppSpec file and optional heading anchor.

`requirement` is `required` or `conditional`; a conditional gate also states its explicit `condition`. Every 1.4 spec contains at least one required repository gate, one required release gate, and one required platform gate for each declared target. Conditional external publication or service checks stay separate so they cannot be mistaken for repository verification.

## UI quality contract

For AppSpec 1.1+:

- `design.md` defines Lazyweb evidence, semantic tokens, typography and line behavior, iconography/assets, the preview/golden matrix, and the post-golden review gate.
- `uiQuality.previewThemes` includes `light` and `dark`.
- `uiQuality.fontScales` includes the default scale and any product-required stress scale.
- `uiQuality.goldenTesting` requires Paparazzi plus ComposablePreviewScanner.
- `uiQuality.designReview` requires the current Lazyweb workflow after approved goldens, declares Material 3 as a review standard where applicable, and fixes the execution contract to a strict ordered queue: one screen per report, exactly one report in flight, and no next submission until the previous report is complete, retrieved, and recorded.
- `uiQuality.iconography.inventoryStatus` is resolved before implementation. Standard actions may use an approved canonical icon set; custom/brand assets must be provided or explicitly waived.
- Every `screens/SCREEN-*.md` contains `Actions and iconography`, `Text layout expectations`, and `Preview and golden matrix`.

Do not start Compose implementation when an icon/asset decision can materially change the screen and remains unresolved. Add a structured `openQuestions` item with `blocking: true`, related screen IDs, and the requested user decision or asset. The validator rejects unresolved blocking questions; non-blocking questions remain warnings.

## Localization contract

For AppSpec 1.2+:

- `app.locales` is the expandable source of truth for supported locales; the template starts with `["en", "ru"]`.
- `localization.defaultLocale` is always `en`; English owns the complete default/base resource set and Russian is the initial additional localization.
- `localization.localeSelection` is always `system-only`; the app has no language picker, persisted locale preference, or app-specific locale override.
- `localization` requires Compose Multiplatform Resources, locale-specific `strings.xml` files, a shared-key strategy, resource-key-only storage for localized local datasets, native platform localization resources as the fallback, and no hardcoded user-facing strings.
- `data.md` contains `Localized text storage` and inventories bundled catalogs/reference data, stable item IDs, shared resource keys, resource ownership, and native-only tables.
- `quality.md` contains `Localization resource checks` covering locale key completeness, valid key mapping, system-locale changes and English fallback, absence of an in-app selector/persisted locale, persistence of IDs/keys rather than translations, and hardcoded-string detection.

Apply the detailed [localized local text contract](localization-contract.md). User-authored and server-owned dynamic content remains data; app-bundled translatable copy remains a resource.

## Architecture contract

For AppSpec 1.3+:

- use standard Kotlin `Result<T>` instead of a generic app-specific Success/Failure wrapper;
- make every production Decompose `Value<Model>` immutable and Store-backed through a dedicated `State -> Model` mapper; router-owned `Value<Child*>` is excluded;
- route Store data/external work through a feature Manager that creates one `Result<T>` with `runCatching`; the Executor consumes it through a shared cancellation-aware `unwrap`;
- keep each component module's public contract at the feature package root, Default/Preview/mappers in `integration`, Store/provider in `store`, and feature Manager/models in `domain`;
- provide a sibling component-module `*ComponentPreview` for every component contract rendered by production Compose, including stateless screens; document the only exception, a navigation-only component with no Compose render surface;
- expose every non-Decompose implementation module that constructs outward dependencies through `di/*Module.kt`: a narrow output interface, optional dependencies interface, same-named top-level factory, and lazy outputs consumed by platform/root composition;
- use a screen or cohesive flow as the default component-module boundary, with documented grouping exceptions;
- host Paparazzi/ComposablePreviewScanner in the Compose UI/resource-owning module by default. A dedicated screenshot module requires an explicit aggregation or plugin/source-set rationale.
- add `quality.md` `Architecture checks` covering these constraints and any documented module/screenshot-host exceptions.

The `architecture.screenshotTestHost` value records the selected host. `architecture.screenshotTestHostRationale` records why it is correct for the target graph; the template selects `compose-ui-module`.

## Monetization and privacy contract

For an AppSpec that enables ads:

- declare Yandex Mobile Ads as the provider and enumerate every allowed slot/format; the lightweight privacy-region flow does not authorize another demand or mediation partner;
- record product/legal decisions for consent copy, protected-region policy, age, advertising identifiers, ATT, personalization, and the public privacy-policy URL; unresolved material choices remain blocking `openQuestions`;
- make `data.md` reference the custom privacy-region endpoint contract, build-configured base URL, strict response validation, maximum 72-hour cache, minimal persisted response plus policy-version-bound choice, and prohibited IP/country/GeoIP/identifier storage;
- give the first ad-eligible flow explicit protected, non-protected, accept, decline, withdrawal, policy-change, expired, offline, malformed, and endpoint-error branches. Every unresolved or declined branch keeps ads hidden and blocks Yandex initialization/requests without blocking the core product;
- specify the app-owned consent screen and Settings withdrawal entry only for a fresh `consentRequired=true` response. Include accept, decline, and privacy-policy actions; do not specify a global popup;
- require `YandexAds.setUserConsent(...)` before every permitted initialization and disable/defer automatic initialization that could bypass the privacy gate;
- add acceptance coverage proving privacy-before-init on Android and iOS with controlled protected, non-protected, and failing/unknown network routes.

Do not label the custom endpoint or app screen as an IAB TCF CMP. A future partner that requires certified CMP/TCF behavior needs a new privacy inventory, explicit product/legal approval, and a replacement integration contract.

## Legacy migration

Migrate an AppSpec 1.3 directory into a new, nonexistent directory:

```powershell
python .\vibe-developer\scripts\migrate-app-spec.py <legacy-app-spec-directory> <new-app-spec-directory>
```

The migrator copies the source tree without changing it, creates the 1.4 JSON inventories, marks inferred acceptance scenarios `needs-review`, and adds blocking questions for scenario approval, managed-entity inventory, and quality-gate confirmation. It refuses an existing output path. Review the generated JSON and flow sections manually, resolve the blocking questions, and validate with `--require-current`; migration output is not an approved implementation hand-off by itself.

## Validation

Run:

```powershell
python .\vibe-developer\scripts\validate-app-spec.py <app-spec-directory>
python .\vibe-developer\scripts\validate-app-spec.py --require-current <app-spec-directory>
```

The validator is read-only. Errors block implementation; warnings require review. It validates contract structure, references, per-AC Given/When/Then, operation decisions, mandatory/conditional gate declarations, blocking questions, and the machine-checkable UI quality contract, not full product correctness. Use the first command only for compatibility or narrow legacy specialist work; the full workflow requires the second command.
