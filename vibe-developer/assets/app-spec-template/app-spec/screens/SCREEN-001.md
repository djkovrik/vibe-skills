# SCREEN-001 — Preference

Linked flow: FLOW-001  
Linked requirements: REQ-001

## Information hierarchy

Title, current value, choices, and save action.

## States

Content and error states apply. Loading, empty, offline, and permission states are not applicable.

## Actions, outputs, navigation, and validation

Select a supported value, save it, emit success or retryable failure, then navigate back.

## Responsive layout and insets

Respect safe areas, font scaling, and compact/expanded widths.

## Accessibility and localization

Provide EN/RU strings, labels, roles, and minimum touch targets.

## Text layout expectations

The title, current-value label, and save label remain one line at 100% font scale in EN/RU on the compact reference phone. At 200%, the choice rows and action may grow or wrap without clipping, overlap, missing glyphs, or loss of the save action. Use explicit `maxLines` and overflow only where truncation is approved.

## Actions and iconography

| Element | Treatment | Icon/source | Accessibility | Asset status |
| --- | --- | --- | --- | --- |
| Navigate back | icon | Material Symbols `arrow_back` / auto-mirrored equivalent | Back action label | approved |
| Save preference | icon + text | Material Symbols `save` | One localized Save action | approved |
| Preference choice | text with selected-state indicator | Material 3 radio/selection indicator | Selected state announced | approved |

## Preview and golden matrix

| State | Themes | Locale/font scale | Viewport | Stable fixture |
| --- | --- | --- | --- | --- |
| Content/default | light, dark | EN 100% | compact phone | default value selected |
| Content/long text | light, dark | RU 200% | compact phone | longest supported labels |
| Content/expanded | light, dark | EN 100% | expanded width | centered/max-width form layout |
| Error/save failure | light, dark | EN 100% | compact phone | deterministic retryable error |

## Allowed ad slots

None.

## Reference assets

None.
