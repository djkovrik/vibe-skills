# SCREEN-001 — Meal workspace

Linked flow: FLOW-001  
Linked requirements: REQ-001

## Information hierarchy

Preset, history, active draft, draft items, and their contextual actions.

## States

Content, empty, and failure states apply. Offline and permission states are not applicable.

## Actions, outputs, navigation, and validation

Expose every single action named by AC-001 through AC-009 and render its persisted outcome.

## Responsive layout and insets

Respect safe areas, font scaling, compact width, and expanded width.

## Accessibility and localization

Use EN/RU Compose resources with the same keys and expose localized action labels.

## Text layout expectations

Labels remain one line at 100%; at 200% they may wrap without clipping or hiding item actions.

## Actions and iconography

| Element | Treatment | Icon/source | Accessibility | Asset status |
| --- | --- | --- | --- | --- |
| Rename/update | icon + text | Material Symbols | Localized action | approved |
| Reuse/resume | icon + text | Material Symbols | Localized action | approved |
| Delete/discard | icon + text | Material Symbols `delete` | Localized action | approved |

## Preview and golden matrix

| State | Themes | Locale/font scale | Viewport | Stable fixture |
| --- | --- | --- | --- | --- |
| Content | light, dark | EN 100% | compact | populated meal |
| Empty/failure | light, dark | RU 200% | compact | deterministic missing item |

## Allowed ad slots

None.

## Reference assets

None.
