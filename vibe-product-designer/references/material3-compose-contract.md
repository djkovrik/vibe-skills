# Material 3 Compose Multiplatform contract

Use this reference before handing approved product UI to Compose Expert. It defines what Product Designer must specify and what Compose Expert must verify; it is not a substitute for current API documentation or source inspection.

## Contents

1. [Boundary and precedence](#boundary-and-precedence)
2. [Root theme contract](#root-theme-contract)
3. [Token mapping](#token-mapping)
4. [Component implementation](#component-implementation)
5. [Adaptive layout and navigation](#adaptive-layout-and-navigation)
6. [Insets and system UI](#insets-and-system-ui)
7. [Motion](#motion)
8. [Accessibility and input](#accessibility-and-input)
9. [Multiplatform differences](#multiplatform-differences)
10. [API maturity gate](#api-maturity-gate)
11. [Preview and verification contract](#preview-and-verification-contract)
12. [Required hand-off](#required-hand-off)
13. [Primary sources](#primary-sources)

## Boundary and precedence

Product Designer owns semantic design intent: hierarchy, canonical layout, component/variant choice, tokens, states, adaptive behavior, accessibility, localization, and acceptance criteria.

Compose Expert owns:

- exact current imports, dependencies, annotations, and APIs;
- stable/experimental/target availability;
- composable signatures and slot APIs;
- layout, modifier, inset, focus, semantics, state, effect, and performance implementation;
- Android/iOS platform boundaries;
- deterministic previews and implementation-level tests.

Use this trust order for implementation details:

1. repository version catalog, source sets, and conventions;
2. current Compose Multiplatform/Material3 API and source;
3. current AndroidX Material3 documentation;
4. this design contract.

Never paste an Android-only sample into `commonMain` without verifying every API.

## Root theme contract

Every product UI tree must run under the Material 3 `MaterialTheme` supplied by the app theme.

The app theme must explicitly own:

- light and dark `ColorScheme` values;
- `Typography` roles and real bundled font families/weights;
- `Shapes` roles;
- motion scheme when the selected Material3 version exposes it;
- product-only semantic extensions not represented by M3;
- system theme and platform-specific dynamic-color selection;
- status/navigation/system-bar integration where the platform root owns it.

Rules:

- Use Material3 imports and dependencies for new work. Do not mix `androidx.compose.material.*` controls into a Material3 screen.
- Keep M3 theme roles as the first choice. Add a custom `CompositionLocal` only for a stable product concept that has no suitable M3 role.
- Do not create screen-local themes or override broad token families to fix one component.
- Use component `Defaults` factories and slots before building wrappers with duplicated styling.
- If the repository has an app component library, its primitives must wrap or compose M3 behavior and consume the app theme.

## Token mapping

| Design decision | Compose contract |
|---|---|
| Semantic color roles | `MaterialTheme.colorScheme`; preserve documented `on*` pairs |
| Type roles | `MaterialTheme.typography`; do not hardcode size/weight in screen bodies |
| Rectangular shape roles | `MaterialTheme.shapes`; use expressive shape APIs only after availability check |
| Surface hierarchy | M3 `Surface`/component defaults with tonal and shadow elevation as specified |
| Spacing | App semantic spacing tokens aligned to the M3 spacing scale; no screen-local magic numbers |
| Motion | `MaterialTheme.motionScheme` or current M3 token APIs when available; otherwise a documented app motion abstraction |
| Icons | Compose Resources vectors or approved Material Symbols assets; semantic labels from resources |
| Strings | Compose Multiplatform Resources `Res.string.*`; shared keys across locales |
| Assets/fonts | Compose Multiplatform Resources owned by the UI/resource module |

Product tokens must map to M3 roles rather than replace them wholesale. Example: a branded success family can extend the scheme, while primary actions still use the primary role contract.

## Component implementation

Use canonical M3 composables for actions, containment, communication, navigation, selection, and input. The Product Designer hand-off names semantic component and variant; Compose Expert maps it to the exact available API.

Common families include:

- `Scaffold`, app bars, navigation bar/rail/drawer, tabs, and adaptive navigation suite;
- buttons, icon buttons, FABs, and extended FABs;
- cards, lists, sheets, dialogs, menus, tooltips, and dividers;
- badges, snackbars, loading/progress indicators;
- checkbox, radio button, switch, chips, sliders, segmented/connected selection controls;
- search, text fields, date pickers, and time pickers.

Implementation rules:

- Preserve component semantics and built-in interaction states.
- Prefer default component token mappings. Customize through supported colors, shapes, elevation, content padding, and slot APIs only where the design contract requires it.
- Use M3 wrappers for consistent product defaults only when they reduce repetition or enforce a stable rule; do not create an app wrapper for every component automatically.
- Public reusable composables accept `modifier: Modifier = Modifier`, data and callbacks rather than Stores/services, and slots where content varies.
- A custom control that replaces a canonical component requires a written gap, full state/semantics spec, target-size proof, input alternatives, and preview/test coverage.
- Treat unsupported expressive components as design intents with baseline M3 fallbacks, not invitations to clone private visual behavior.

## Adaptive layout and navigation

Use the M3 breakpoint and canonical-layout contract from [material3-foundations.md](material3-foundations.md).

Compose implementation should prefer current shared Material3 adaptive APIs when available, including:

- window size classes or the repository's equivalent shared breakpoint model;
- adaptive navigation suite behavior that switches navigation bar/rail by available width;
- list-detail and supporting-pane scaffolds for their matching canonical layouts.

Rules:

- Measure the app window, not physical device screen or orientation labels.
- Preserve destination identity and Decompose navigation state while the visual navigation component adapts.
- Keep compact and medium single-pane navigation behavior consistent with expanded multi-pane behavior.
- Define pane order, back behavior, retained selection, empty-detail state, and fold/hinge avoidance.
- If the current shared adaptive artifact is unavailable or incompatible, implement the same M3 breakpoint behavior through a repository-owned abstraction and record the fallback.
- Do not couple the Product Designer contract to Android Navigation Compose; this repository routes navigation through Decompose.

## Insets and system UI

Many Material3 components handle relevant insets through their parameters/defaults. Compose Expert must verify the exact behavior of the version in use.

- Assign one owner for top, bottom, start, and end system insets.
- Pass `Scaffold` content padding to the content root or deliberately consume it once.
- Do not apply status/navigation bar padding both in a bar component and its parent.
- Keep primary content and controls out of display cutouts, hinges, and unsafe regions.
- Support edge-to-edge rendering without hiding focus indicators, snackbars, FABs, sheets, or navigation.
- Verify Android system bars and iOS safe areas separately even when the shared layout is identical.

## Motion

When supported by the selected Material3 artifact:

- set one app-level standard or expressive `MotionScheme`;
- use spatial specs for size/position/shape and effect specs for color/opacity;
- let built-in components inherit the scheme;
- use the same semantic specs in custom components.

If `MotionScheme` is experimental or absent on a target, Compose Expert must choose a repository-approved abstraction using current M3 motion tokens or equivalent specs and keep the design behavior consistent.

Motion requirements:

- all animations have stable labels for diagnostics where APIs support them;
- transitions are interruptible where user input can retarget them;
- reduced-motion mode removes strong translation, scale, parallax, and shape morphing;
- loading/progress animation exposes semantics and stops when the process ends;
- previews/goldens use deterministic settled states unless a dedicated motion test covers the transition.

## Accessibility and input

Prefer semantics already supplied by M3 components. Add or override semantics only when the composition changes the announced contract.

Require:

- accessible name, role, state/value, and available action;
- at least 48x48dp interactive targets;
- visible focus and logical traversal order;
- screen-reader announcements for dynamic results, progress, errors, snackbars, and modal surfaces;
- text and non-text contrast;
- non-color selection/error cues;
- keyboard and pointer behavior on applicable targets;
- a single-pointer/keyboard alternative for drag, swipe, long press, and hover-only behavior;
- manual input alternatives for date/time pickers;
- localized content descriptions and state labels from `Res.string.*`.

Do not add duplicate `contentDescription` to an icon next to text that already names the action. Decorative icons/images use null semantics.

## Multiplatform differences

The core Material3 component API is shared, but platform integration is not.

| Concern | Shared contract | Platform boundary |
|---|---|---|
| M3 components/theme | Prefer `commonMain` | Verify exact target availability |
| User wallpaper dynamic color | Static role contract and fallback | Android 12+ implementation only |
| System dark theme | Shared design behavior | Use current multiplatform API or platform actual |
| System bars/safe areas | Shared inset ownership | Android system bars and iOS safe areas differ |
| Back/predictive back | Shared navigation intent | Platform bridge/Decompose integration |
| Haptics | Semantic event in design | Platform service implementation |
| Pointer/keyboard/hover | Shared state requirements | Behavior varies by Android tablet, iOS pointer, desktop, and web |
| Fonts/resources | `Res.*` contract | Verify loading and glyph rendering per target |

Do not make Android's dynamic color, `LocalContext`, resource IDs, or platform-only lifecycle APIs part of a shared screen contract.

## API maturity gate

Before implementation approval, Compose Expert must produce an availability note containing:

- repository Compose Multiplatform and Material3 versions;
- exact dependency coordinates/conventions already used;
- exact APIs selected for Android and iOS;
- stable, beta, alpha, experimental, or unavailable status;
- required opt-in annotations;
- platform differences;
- baseline M3 fallback;
- tests/previews proving the selected path.

Do not opt into an experimental expressive API solely to match a screenshot. Follow repository policy and request a product/architecture decision when experimental adoption changes maintenance risk.

## Preview and verification contract

Every primary screen and applicable state needs deterministic component-module preview entry points.

Mandatory coverage:

- light and dark;
- content plus applicable loading, empty, error, offline, permission, and disabled states;
- compact layout;
- each materially distinct adaptive layout;
- longest supported locale and largest required font scale;
- selected/focused/error component states when visually important;
- baseline fallback when an expressive variant can differ by target/version.

Golden review checks:

- correct Material component and variant;
- expected M3 defaults or documented customization;
- color-role pairing and surface hierarchy;
- typography roles and emphasis;
- consistent shape, spacing, elevation, and icons;
- state layers, focus, and selection cues;
- inset and pane behavior;
- text scale/localization/RTL resilience;
- touch targets and semantics;
- expressive tactics remain focused and do not overwhelm hierarchy.

## Required hand-off

Provide Compose Expert:

- screen and acceptance IDs;
- approved Lazyweb and official Material evidence;
- canonical layout, scaffold regions, breakpoint/pane table, and inset ownership;
- navigation destinations and adaptive component family;
- per-element M3 component/variant map;
- semantic token table;
- complete UI state and interaction-state matrices;
- copy, line-count, overflow, localization, and RTL rules;
- icons/assets and accessibility labels;
- motion scheme, transitions, and reduced-motion behavior;
- API maturity constraints and acceptable fallbacks;
- exact preview/golden matrix;
- justified deviations and unresolved questions.

## Primary sources

Verified 2026-08-11.

- [Material Design 3 for Jetpack Compose](https://m3.material.io/develop/android/jetpack-compose)
- [Material 3 in Compose](https://developer.android.com/develop/ui/compose/designsystems/material3)
- [Material components in Compose](https://developer.android.com/develop/ui/compose/components)
- [Material 3 insets](https://developer.android.com/develop/ui/compose/system/material-insets)
- [Adaptive apps with Compose Material 3](https://developer.android.com/develop/ui/compose/layouts/adaptive/get-started-with-adaptive-apps)
- [Compose Multiplatform releases](https://github.com/JetBrains/compose-multiplatform/releases)
- [Compose Multiplatform](https://github.com/JetBrains/compose-multiplatform)
- [Material Android is Compose-first](https://m3.material.io/material-is-compose-first)
- [M3 Expressive motion theming](https://m3.material.io/m3-expressive-motion-theming)
