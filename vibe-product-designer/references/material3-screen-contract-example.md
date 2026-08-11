# Material 3 screen contract example

Use this compact example as the minimum validation shape for a real screen. Replace all example values with traced AppSpec and evidence IDs.

## Identity and evidence

- Screen: `SCREEN-SETTINGS-001`
- Primary task: Review and change independent app preferences.
- Acceptance IDs: `REQ-SETTINGS-001`, `AC-SETTINGS-001`
- Official guidance: Material layout, lists, switches, app bars, interaction states, accessibility.
- Lazyweb evidence: stable research/report URL and selected reference IDs.

## Layout and adaptation

| Width | Layout | Navigation | Content |
|---|---|---|---|
| Compact `<600dp` | Single pane | Flexible navigation bar or back app bar according to hierarchy | One segmented/standard settings list |
| Medium `600–839dp` | Single pane by default | Collapsed rail for a top-level destination | Wider list with bounded readable width |
| Expanded `840–1199dp` | List-detail when categories justify it | Collapsed/expanded rail | Category list plus selected category detail |
| Large/extra-large | Two panes; optional supporting pane only with a real task | Expanded rail when space permits | Bounded panes, no stretched full-width rows |

Inset owners: app bar owns top system inset; adaptive navigation owns its adjacent edge; scaffold content consumes remaining padding once.

## Component map

| Element | M3 component/variant | Why | Fallback |
|---|---|---|---|
| Page context | Small or medium flexible app bar | Title plus back and at most one essential action | Small baseline app bar |
| Preference collection | Expressive list, standard or segmented style | Consistent scannable rows and selected treatment | Baseline list |
| Independent setting | Switch with full-row label target | Binary value applies immediately | None; switch is canonical |
| Mutually exclusive theme | Connected button group or radio group | One visible choice from a small set | Radio group |
| Destructive cache action | Tonal/text button plus confirmation only when consequence is material | Action, not a selection control | Baseline button variant |
| Save feedback | Snackbar without action or persistent with action | Non-blocking process result | Inline status when snackbar host is unavailable |

Custom components: none. Any later addition needs a documented M3 capability gap.

## Token contract

- Color: `surface`/`onSurface` for page; `surfaceContainer*` for grouped rows; `primary` roles for active controls; `error` roles only for destructive/error meaning.
- Typography: app-bar title -> title/headline role; row label -> body/title role; supporting text -> body medium/small; controls -> label role.
- Shape: component defaults; one product-wide list/container mapping only.
- Spacing: M3-aligned semantic tokens for page margin, section gap, row padding, and icon-label gap.
- Elevation: app bar resting/scrolled defaults; lists remain level 0 unless overlap requires otherwise.
- Motion: app-level expressive or standard scheme; effects for switch color, spatial spec for pane transition; reduced motion uses immediate/fade behavior.
- Icons: one approved Material Symbols family; selected/unselected fill changes only where component guidance calls for it.

## State and accessibility matrix

| State | Visual/behavior contract | Semantics |
|---|---|---|
| Loading | Stable skeleton or one group indicator; controls unavailable | Announce purpose once; no decorative progress |
| Content | All rows visible and grouped by task | Heading structure and logical traversal |
| Empty | Explain why no preferences exist and next action if applicable | Message is reachable as normal content |
| Error | Inline recoverable message plus retry; preserve known values | Polite/assertive announcement according to severity |
| Offline | Show data freshness and which changes can be queued | Do not imply successful remote save |
| Disabled control | Use component disabled state only with nearby reason when not obvious | Disabled and reason remain discoverable |
| Focused/hovered/pressed | Use M3 state layers and visible focus | Keyboard/pointer behavior matches platform |
| Selected | Component indicator plus non-color cue | Selected/checked state is announced |

All targets are at least 48x48dp. Switch labels and controls share one unambiguous target. No action relies only on swipe, drag, long press, or hover.

## Text and localization

- All copy and accessibility labels use shared `Res.string.*` keys.
- EN is base; RU is included in the stress preview.
- Row labels may wrap at stress scale; values and actions must remain visible.
- No in-app locale picker.
- Leading/trailing placement mirrors for RTL; non-directional symbols do not.

## API maturity note

- Record repository Compose Multiplatform and Material3 versions.
- Record exact common APIs, stability/opt-ins, Android/iOS availability, and repository policy.
- Use the listed baseline fallback when an expressive API is missing or experimental.
- Keep Android wallpaper dynamic color behind an Android platform boundary with deterministic shared light/dark schemes elsewhere.

## Preview and golden matrix

- Compact content: light and dark.
- Compact loading, error, offline, and disabled states.
- Expanded list-detail: light and dark.
- Largest required font scale with longest RU strings.
- Focused/selected control state where visually distinct.
- Expressive variant and baseline fallback when both are real delivery paths.

The screen passes when every row in this contract is implemented or explicitly waived with evidence, all preview entries are deterministic, and approved goldens verify without objective Material, accessibility, localization, or layout defects.
