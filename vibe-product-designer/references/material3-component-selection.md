# Material 3 component selection

Use this reference whenever choosing, replacing, or auditing UI controls and surfaces. Select by semantic job and behavior before visual style.

## Contents

1. [Selection method](#selection-method)
2. [Actions and app chrome](#actions-and-app-chrome)
3. [Communication and progress](#communication-and-progress)
4. [Containment and collections](#containment-and-collections)
5. [Navigation and search](#navigation-and-search)
6. [Selection and input](#selection-and-input)
7. [M3 Expressive replacements](#m3-expressive-replacements)
8. [Component specification contract](#component-specification-contract)
9. [Compose Multiplatform availability gate](#compose-multiplatform-availability-gate)
10. [Anti-patterns](#anti-patterns)
11. [Primary sources](#primary-sources)

## Selection method

For each element answer in order:

1. What task or information does it represent?
2. Is it an action, destination, selection, input, status, message, or container?
3. What is its prominence: highest, high, medium, or low?
4. Is it persistent, contextual, temporary, or modal?
5. Is selection single, multiple, independent binary, or a value on a range?
6. Must all options remain visible?
7. What changes across compact, medium, expanded, large, and extra-large windows?
8. Which states, input methods, and accessibility behavior are required?
9. Is the chosen variant available and acceptable on every declared Compose Multiplatform target?

Read the selected component's official overview, guidelines, accessibility, and specs pages before finalizing the design. Component defaults are the starting contract; customization must preserve semantics, target size, states, and role pairings.

## Actions and app chrome

| Component | Use when | Key rules |
|---|---|---|
| App bar | Describing the current page and exposing navigation plus 1–2 essential actions | Keep actions contextual; move additional actions to a toolbar or menu; prefer search/small/flexible expressive variants when available |
| Button | Triggering a labeled action | Choose elevated, filled, tonal, outlined, or text by prominence; keep labels concise and sentence case; avoid button overload |
| Toggle button | A button also represents selection | Expose selected state and use non-color feedback; do not substitute for an independent setting switch |
| Icon button | A familiar minor action fits a clear system icon | Always label semantically; use tooltip on pointer/focus platforms; outlined-to-filled state can show selection |
| Standard button group | Grouping related actions with expressive interaction | May mix variants and widths deliberately; each button remains a separate focusable action |
| Connected button group | Single/multi/required selection among compact related options | Preferred expressive replacement for segmented buttons when supported |
| Split button | One primary action has a compact menu of related alternatives | Leading area performs the action; trailing area always opens the menu; both need 48dp targets |
| FAB | One screen has a single most important persistent action | Use only one primary FAB role; medium is the expressive default; remove it when the action is unavailable instead of disabling it |
| Extended FAB | The primary action needs a label for clarity or emphasis | Use on long scrolling views; label should remain concise; use expressive small/medium/large variants when available |
| FAB menu | A FAB needs 2–6 closely related actions | Open only from a FAB, never an extended FAB; keep the close control focused and unobstructed |
| Toolbar | Several persistent or contextual page actions are needed | Docked for global actions; floating for contextual actions; do not show a bottom toolbar with a navigation bar |

Prominence order is contextual, but a common starting hierarchy is FAB/extended FAB, filled button, tonal/elevated button, outlined button, text button, then icon button or link for minor actions. Do not place several highest-emphasis actions on one screen.

## Communication and progress

| Component | Use when | Key rules |
|---|---|---|
| Badge | An icon or destination has unread/status/count information | Small badge signals presence; large badge contains a short count/label; keep content to four characters including `+`; announce meaning with its anchor |
| Snackbar | Reporting a brief completed or upcoming process without blocking work | Only one at a time; at most one action; actionable snackbars do not auto-dismiss; use dialog for a required decision |
| Tooltip | An element needs additional context | Plain for icon/action labels; rich for a longer explanation; must appear for keyboard focus as well as hover where applicable |
| Loading indicator | A short indeterminate process of roughly 200ms–5s needs attention | Preferred expressive replacement for most indeterminate circular progress; never decorative; provide a non-gesture refresh action |
| Progress indicator | Showing determinate progress or a longer/ongoing process | Linear or circular; keep a consistent configuration for the same process; announce progress and purpose |

Do not attach an indicator to every asynchronous item. Prefer a stable skeleton or group-level progress when many items load together.

## Containment and collections

| Component | Use when | Key rules |
|---|---|---|
| Card | Related content and actions form one scannable subject | Use elevated, filled, or outlined based on separation needs; do not nest independent actions inside a card whose whole surface is clickable |
| List | A vertical collection should be scanned, selected, or acted on | Keep item structure and anchors consistent; prefer expressive standard/segmented lists when available; selection needs a non-color cue |
| Carousel | Visual items benefit from horizontal browsing | Choose multi-browse, uncontained, hero, center-aligned hero, or full-screen by content; provide `Show all` or equivalent on vertically scrolling pages |
| Bottom sheet | Compact/medium screens need supplementary anchored content | Standard preserves interaction with main content; modal blocks through a scrim; content is secondary, not the primary task |
| Side sheet | Medium/expanded windows need supplementary contextual content | Standard remains visible with primary content; modal temporarily overlays it; always expose a close affordance |
| Dialog | Critical information or a decision must interrupt the flow | Use sparingly and for one task; basic or full-screen; keep dismissal, focus, scrolling, and destructive consequences explicit |
| Divider | Grouping cannot be communicated clearly with open space | Use to group sections or show hierarchy, not between every item; decorative semantics |

Prefer whitespace and surface-container roles before adding a card, divider, border, or shadow. A screen made entirely of cards usually lacks hierarchy.

## Navigation and search

| Component | Use when | Key rules |
|---|---|---|
| Flexible navigation bar | Compact/medium windows have 3–5 equal primary destinations | Destinations remain stable across screens; always show icon and label; one destination is active |
| Collapsed navigation rail | Medium through extra-large windows have 3–7 destinations | Keep it at the leading edge; may include a FAB; use as the default expressive rail |
| Expanded navigation rail | Larger windows need rail destinations plus drawer-like labels/functionality | Preferred expressive replacement for navigation drawer; collapse only when content needs space |
| Navigation drawer | Legacy/baseline or temporary modal navigation is required | Not preferred in M3 Expressive; use expanded rail when possible and record any fallback |
| Tabs | Peer content categories share one hierarchy level | Primary tabs define major content under the app bar; secondary tabs subdivide a content region; do not use for sequential steps |
| Search bar | Search is a visible task within a view | Use contained expressive style when supported; announce suggestions/results; provide clear input and focus behavior |
| Search app bar | Search is the dominant global entry point | Replaces a normal page-title app bar when search is the primary function |
| Search icon button | Search is a secondary action | Opens a clearly labeled search surface; do not hide a primary search task behind it |

Navigation adapts by window size and destination count, not by visual preference. Define destination preservation, selected state, back behavior, and pane behavior before selecting the component.

## Selection and input

| Component | Use when | Key rules |
|---|---|---|
| Checkbox | Zero, one, or multiple related options may be selected | Use for multi-select lists and parent/child indeterminate states; make label and control one target |
| Radio button | Exactly one option from a visible set is selected | Expose all options; once selected, provide an explicit “None” choice if deselection is valid |
| Switch | An independent binary setting takes effect immediately | Use for on/off settings, not mutually exclusive alternatives; do not add a separate Save action for the switch itself |
| Chip | A contextual option helps the current task | Assist, filter, input, or suggestion variants have different semantics; chips are not general-purpose buttons |
| Connected button group | Two to five compact related options need single/multi selection | Preferred expressive choice where all options should remain visible |
| Menu | A temporary compact set of actions or choices can be hidden | Use toolbar when actions must remain visible; menu selection needs shape/color plus another cue when necessary |
| Slider | A value or range changes continuously and should preview immediately | Standard, centered, or range; horizontal/vertical and size variants depend on API support; provide value semantics and alternate input |
| Date picker | Selecting a date or range benefits from calendar context | Docked for larger contexts; modal/modal input for compact; always offer manual text entry |
| Time picker | Selecting hours/minutes benefits from dial or structured input | Modal dial/input; always offer manual entry and support 12/24-hour locale conventions |
| Text field | Free-form or structured text must be entered | Filled has more emphasis; outlined has less; keep labels/supporting/error text concise and actionable; preserve visible state |

Selection control shortcut:

- Multiple related choices: checkbox.
- Exactly one visible choice: radio button or connected button group for a compact set.
- Independent on/off setting with immediate effect: switch.
- Contextual filter/assist/input/suggestion: chip.
- Numeric/intensity range with immediate feedback: slider.
- Many temporary choices: menu.

## M3 Expressive replacements

Prefer these current recommendations when the repository's Compose version and targets support them:

| Baseline/older pattern | Preferred expressive pattern |
|---|---|
| Medium or large app bar | Medium flexible or large flexible app bar |
| Baseline navigation bar | Flexible navigation bar |
| Baseline navigation rail | Collapsed or expanded navigation rail |
| Navigation drawer | Expanded navigation rail |
| Segmented buttons | Connected button group |
| Small FAB | FAB, medium FAB, or large FAB based on hierarchy |
| Baseline extended FAB | Small, medium, or large expressive extended FAB |
| Stacked small FABs/speed dial | FAB menu |
| Bottom app bar | Docked toolbar |
| Indeterminate circular progress for a short wait | Loading indicator |
| Baseline list/menu/search where expressive variant is available | Expressive list, vertical menu, or contained search |

Do not imitate a missing expressive component with a visually similar custom control unless its complete behavior, accessibility, state, and motion contract can be implemented and tested. Baseline M3 is the safe fallback.

## Component specification contract

For every selected component record:

- semantic job and user task;
- official component and variant;
- prominence and placement;
- persistent/contextual/temporary/modal behavior;
- content and slot inventory;
- size, shape, spacing, elevation, and color-role mapping;
- typography and icon roles;
- enabled, disabled, hovered, focused, pressed, dragged, selected, loading, and error states as applicable;
- motion scheme and reduced-motion behavior;
- touch, keyboard, pointer, voice/switch, and gesture behavior;
- accessibility role, name, state/value, focus order, announcements, and alternative actions;
- compact/medium/expanded adaptation;
- text scaling, localization expansion, and RTL behavior;
- Compose API, stability annotation, target availability, and fallback;
- deviation from Material defaults and evidence-based rationale.

## Compose Multiplatform availability gate

The live Material catalog can be newer than the Compose Multiplatform Material3 artifact in a repository.

Before approving implementation:

1. Inspect the repository's Compose Multiplatform and Material3 versions.
2. Verify the exact component/variant API in common code for Android and iOS targets.
3. Record whether the API is stable, experimental, alpha-only, or absent.
4. Respect repository policy for experimental opt-ins.
5. Select a baseline M3 semantic fallback when availability differs.
6. Keep Android-only dynamic color and system UI behavior behind platform boundaries.
7. Add previews/tests for the chosen variant and fallback where both can occur.

Design can target the expressive semantic intent before the API is available, but delivery cannot be declared complete without a compilable and tested implementation path.

## Anti-patterns

Reject:

- custom `Row`/`Box` controls that reproduce an existing Material component;
- selecting components only because their silhouette looks attractive;
- several filled buttons or FAB-level actions competing on one screen;
- switches for mutually exclusive options or radio buttons for independent settings;
- chips used as permanent primary actions;
- dialogs for passive status messages;
- navigation components with changing destination sets between screens;
- icon-only unfamiliar actions without labels/tooltips;
- nested clickable surfaces;
- disabled FABs instead of removing an unavailable primary action;
- actionable snackbars that disappear before interaction;
- horizontal carousel content without an accessible all-items path;
- visual expressive replacements copied without target/API verification.

## Primary sources

Verified 2026-08-11.

- [Material 3 components catalog](https://m3.material.io/components)
- [Material components in Compose](https://developer.android.com/develop/ui/compose/components)
- For a selected component use `https://m3.material.io/components/{component}/overview`, `/guidelines`, `/accessibility`, and `/specs`.
- [M3 Expressive overview](https://m3.material.io/building-with-m3-expressive)
- [Material 3 in Compose](https://developer.android.com/develop/ui/compose/designsystems/material3)
