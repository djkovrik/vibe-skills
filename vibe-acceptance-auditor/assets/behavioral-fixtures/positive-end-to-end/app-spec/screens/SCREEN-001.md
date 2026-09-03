# SCREEN-001 — Preference

Linked flow: FLOW-001  
Linked requirements: REQ-001

## Information hierarchy

Title, current value, create/update action, and delete action.

## States

Content and empty states apply. Loading, offline, and permission states are not applicable.

## Actions, outputs, navigation, and validation

Create, read, update, and delete the preference through the public component contract.

## Responsive layout and insets

Respect safe areas, font scaling, compact width, and expanded width.

## Accessibility and localization

Use EN/RU Compose resources with the same keys and expose localized action labels.

## Text layout expectations

Labels remain one line at 100%; at 200% they may wrap without clipping or hiding actions.

## Actions and iconography

| Element | Treatment | Icon/source | Accessibility | Asset status |
| --- | --- | --- | --- | --- |
| Save | icon + text | Material Symbols `save` | Localized action | approved |
| Delete | icon + text | Material Symbols `delete` | Localized action | approved |

## Preview and golden matrix

| State | Themes | Locale/font scale | Viewport | Stable fixture |
| --- | --- | --- | --- | --- |
| Content | light, dark | EN 100% | compact | saved value |
| Empty/stress | light, dark | RU 200% | compact | no value |

## Allowed ad slots

None.

## Reference assets

None.
