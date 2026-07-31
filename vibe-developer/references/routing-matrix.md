# Routing matrix and desk simulation

## Routing prompts

Each row contains four forward prompts and the expected route.

| Owner | Positive direct | Positive orchestrated | Negative near-miss | Overlap and hand-off |
| --- | --- | --- | --- | --- |
| Developer | “Use `$vibe-developer` to implement this AppSpec end to end.” | “Add offline reminders, UI, tests, and release checks.” | “Add one SQLDelight query.” -> Persistence | “Ship a feature spanning API, cache, UI, and notifications.” -> Developer sequences all owners |
| Project Architect | “Create a KMP convention plugin and module.” | “Scaffold modules and release gates for this AppSpec.” | “Implement recurrence calculation.” -> Domain | “Add an iOS SDK pod used by a platform service.” -> Architect owns linkage; Platform owns service |
| Domain | “Model recurrence, DST, and invariants.” | “Define business contracts before Stores.” | “Reduce loading state after an intent.” -> MVIKotlin | “Compute a dashboard from three repositories.” -> Domain manager; MVIKotlin orchestrates |
| Decompose | “Add a stateless callback screen component.” | “Build the onboarding component tree.” | “Add async observable state.” -> MVIKotlin after contract | “Add Store-backed tab navigation.” -> Decompose owns component/navigation; MVIKotlin owns Store |
| MVIKotlin | “Add a retained MVIKotlin Store.” | “Implement observable async state for SCREEN-004.” | “Forward a button click to parent.” -> Decompose | “Store currently performs pricing math.” -> Domain extracts calculation; MVIKotlin keeps orchestration |
| Platform | “Handle exact-alarm permission and resume.” | “Implement notifications/reminders capability.” | “Create SQL schedule tables.” -> Persistence | “Persist logical reminders and register alarms.” -> Persistence owns rows; Platform owns registrations |
| Network | “Implement a REST OAuth API with Ktor.” | “Add the AppSpec remote API transport.” | “Resolve Firestore snapshot conflicts.” -> Sync | “OAuth identity triggers snapshot sync.” -> Network owns token transport; Sync owns coordination |
| Persistence | “Add SQLDelight tables and typed settings.” | “Implement offline cache/settings.” | “Map a REST response DTO.” -> Network | “Apply a remote snapshot atomically.” -> Persistence owns transaction; Sync owns merge policy |
| Sync | “Resolve versioned snapshot conflicts.” | “Implement offline remote coordination.” | “Retry an idempotent HTTP PUT.” -> Network | “Remote reminders changed.” -> Sync merges; Platform reschedules after commit |
| Product Designer | “Research and design this settings screen.” | “Define UI evidence, hierarchy, themes, icon inventory, preview matrix, and post-golden review.” | “Fix a `LaunchedEffect` recomposition bug.” -> Compose Expert | “Finalize the UI.” -> Product Designer defines/ reviews; Compose Expert renders; Visual Testing records/verifies |
| Visual Testing | “Add Paparazzi goldens for all preview states.” | “Turn every primary screen/state into light/dark preview/golden CI.” | “Choose a better empty-state hierarchy.” -> Product Designer | “Paparazzi cannot render a native ad view.” -> Visual Testing adds seam; Platform/Monetization test native behavior |
| Monetization | “Integrate Yandex inline ads safely.” | “Implement the requested ads capability.” | “Redesign the feed hierarchy.” -> Product Designer | “Enable personalized ads.” -> user/product/legal decides; Monetization implements only approved policy |
| Test Engineer | “Test Decompose component behavior.” | “Cover non-visual acceptance scenarios.” | “Update screenshot snapshots.” -> Visual Testing | “Test a Store-backed component.” -> Test Engineer owns harness; Decompose/MVIKotlin clarify contracts |

Localized local catalog hand-off: Domain owns stable item IDs/key semantics; Persistence stores only IDs/keys; Project Architect owns Compose resource generation/module wiring; Product Designer and Compose resolve common `strings.xml` resources; Platform owns Android/iOS native resource fallbacks; Test Engineer checks key completeness and hardcoded-string policy; Visual Testing renders declared locales.

## Reference desk simulation

For a new Android+iOS KMP app with onboarding, home tabs, OAuth REST, SQLDelight cache, settings, offline mode, Firestore-like sync, notifications, exact reminders, light/dark UI, Yandex inline ads, EN/RU, component tests, and Paparazzi:

| Concern | Owner and sequence |
| --- | --- |
| scaffold/modules, CI/release | Project Architect |
| entities, recurrence, errors | Domain |
| OAuth/REST/DTO | Network |
| cache/settings/migrations | Persistence |
| snapshot versions/conflicts | Sync |
| permissions/reminders/lifecycle | Platform |
| onboarding/tabs/root navigation | Decompose |
| observable async screen state | MVIKotlin |
| evidence, hierarchy, theme, accessibility, EN/RU | Product Designer -> Lazyweb -> Compose Expert |
| placements/privacy-safe SDK setup | Monetization + Product Designer/product/legal |
| domain/Store/component/data tests | Test Engineer |
| preview matrix and icon/asset decisions | Product Designer -> user for unresolved assets -> Compose Expert |
| previews/scanner/Paparazzi/CI diffs and coverage inventory | Visual Testing |
| post-golden full-UI Lazyweb review and approved-fix loop | Product Designer -> Compose Expert -> Visual Testing |
| localized local catalogs and bundled text | Domain IDs/keys -> Persistence key storage -> Architect resource wiring -> Product Designer/Compose resources -> Platform native fallback -> Test/Visual verification |
| final quality/platform/release gates | Project Architect, coordinated by Developer |

No responsibility is intentionally shared without an explicit hand-off.
