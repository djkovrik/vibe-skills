# Material 3 foundations

Use this reference for every new screen, redesign, theme, or product-wide UI audit. Material 3 is the default interaction and visual grammar; product identity comes from coherent semantic tokens, content, imagery, and restrained expressive tactics rather than arbitrary custom controls.

## Contents

1. [Authority and adoption](#authority-and-adoption)
2. [Foundation sequence](#foundation-sequence)
3. [Layout and adaptation](#layout-and-adaptation)
4. [Design tokens](#design-tokens)
5. [Color](#color)
6. [Typography](#typography)
7. [Shape](#shape)
8. [Spacing, density, and elevation](#spacing-density-and-elevation)
9. [Motion](#motion)
10. [Icons and imagery](#icons-and-imagery)
11. [Interaction states and inputs](#interaction-states-and-inputs)
12. [Content, accessibility, and localization](#content-accessibility-and-localization)
13. [Expressive product identity](#expressive-product-identity)
14. [Required design output](#required-design-output)
15. [Primary sources](#primary-sources)

## Authority and adoption

- Treat current Material 3 guidance as normative for product-facing Compose UI unless the AppSpec or a platform requirement explicitly says otherwise.
- Prefer M3 Expressive for new or substantially redesigned UI when the required Compose APIs are available and acceptable across all declared targets.
- Use baseline M3 when an expressive API is experimental, missing on a target, disallowed by repository policy, or unsuitable for the product. Preserve the same semantic component and token roles and record the fallback.
- Do not mix Material 2 and Material 3 in new work. Migration work must state which remaining M2 surfaces are temporary.
- Keep familiar Material interaction behavior even when visual tokens are customized.
- Treat the official component page's overview, guidelines, accessibility, and specs tabs as one contract. Read all four for every selected component.

M3 Expressive expands M3; it is not a separate design system. It adds expressive component variants, emphasized typography, a broader shape library, richer color tactics, and physics-based motion. It should strengthen hierarchy and usability, not decorate every element.

## Foundation sequence

Make design decisions in this order:

1. Define the user task, content priority, error risk, accessibility needs, and measurable acceptance behavior.
2. Choose a canonical layout and breakpoint behavior.
3. Choose navigation and containment surfaces.
4. Map actions, selection, communication, and input to canonical components.
5. Assign semantic system and component tokens.
6. Add product expression through typography, color, shape, imagery, and motion.
7. Validate interaction states, input methods, accessibility, localization, and reduced-motion behavior.
8. Produce the preview/golden matrix and Compose hand-off.

Do not begin from a collection of visually attractive components. Begin from hierarchy, tasks, and semantic roles.

## Layout and adaptation

### Scaffold first

Structure each screen as Material scaffold regions:

- bars frame navigation and page context;
- rails hold persistent navigation or contextual controls around panes;
- panes contain primary and supporting content;
- safe regions contain system UI and display cutouts, not primary content.

Assign one inset owner to every edge. Define whether the owning Material component handles it or whether the content pane consumes scaffold padding. Do not apply the same inset twice.

### Breakpoints

Use window width, not device labels or orientation alone:

| Breakpoint | Width | Default starting point |
|---|---:|---|
| Compact | `< 600dp` | One pane; navigation bar or modal expanded rail; 16dp outer margins |
| Medium | `600–839dp` | Usually one pane; rail for one-pane layouts; selective two-pane layouts for low-density content |
| Expanded | `840–1199dp` | Usually two panes; collapsed or expanded navigation rail |
| Large | `1200–1599dp` | Usually two panes; consider fixed and flexible pane combinations |
| Extra-large | `>= 1600dp` | Two panes by default; three panes only when content relationships justify them |

For every breakpoint transition decide what is revealed, divided, resized, repositioned, or swapped. Do not merely stretch compact content.

### Canonical layouts

Start from one of the Material canonical layouts:

- Feed: browsing or discovery through adaptive cards/lists and a reflowing grid.
- List-detail: parent list plus selected detail; separate screens in compact/medium and adjacent panes when space permits.
- Supporting pane: a primary task plus related tools, filters, comments, or secondary information.

State why a custom layout is necessary if none of these fits.

### Grids, grouping, and RTL

- Establish grid columns, bars/rails, panes, margins, and gaps before placing content.
- Use proximity and open space for implicit grouping; use containers, outlines, dividers, or elevation only when explicit grouping adds meaning.
- Use logical `start`/`end` and `leading`/`trailing` terms. Mirror directional layout for RTL but preserve non-directional content such as clocks, media controls, charts, and brand marks when appropriate.
- Support touch, keyboard, mouse/trackpad, stylus, voice, and switch inputs where the target platform exposes them.

## Design tokens

Use the Material token hierarchy:

1. Reference tokens hold raw palette, typeface, and measurement values.
2. System tokens assign semantic roles such as `primary`, `onSurface`, type roles, shape scale, spacing, elevation, and motion.
3. Component tokens map system roles to a component, variant, element, and state.

Rules:

- Never place raw colors, font sizes, radii, spacing, elevation, or animation values in a screen contract.
- Name product additions by semantic purpose, not appearance or screen location.
- Add a custom system token only when Material does not represent a stable product concept.
- Map every custom component back to system tokens and define all interaction states.
- Keep token names stable when underlying values change.
- Record token ownership, light/dark values, platform variations, and component consumers.

## Color

### Schemes and roles

Choose and document one primary color strategy:

- Static baseline for a neutral Material starting point.
- Static brand for consistent product recognition.
- User-generated dynamic color for personalization on supported Android versions.
- Content-based dynamic color for contained, content-led moments.
- A controlled combination, such as a static brand foundation with content-derived color inside a media hero.

Material defines 26+ roles across primary, secondary, tertiary, error, surface, and outline groups. Assign roles, not hex values, to UI elements.

### Pairing and hierarchy

- Pair each container with its documented `on*` role: `primary/onPrimary`, `primaryContainer/onPrimaryContainer`, `surface/onSurface`, and equivalent pairs.
- Use primary roles for the highest-priority actions and selected states, secondary roles for less-prominent emphasis, and tertiary roles for contrasting accents or focused hero moments.
- Use surface-container roles and tonal difference to establish hierarchy before adding shadows.
- Use outline roles for boundaries; do not turn every group into a bordered card.
- Add semantic success, warning, or domain colors as complete accessible role families rather than one raw color.
- Verify light, dark, high-contrast/user-contrast, enabled, disabled, selected, pressed, focused, hovered, and error combinations.
- Never encode state or meaning only with color.

Dynamic wallpaper color is Android-specific. Compose Multiplatform targets need a deterministic static fallback; any content-derived cross-platform scheme needs an explicit implementation and test contract.

## Typography

Use the M3 role system: display, headline, title, body, and label, each in large, medium, and small sizes. M3 Expressive adds emphasized counterparts to the 15 baseline styles.

- Assign every text element a semantic role and hierarchy purpose.
- Use display only for short, high-impact content; headline for major sections; title for contained sections/items; body for reading; label for controls and compact metadata.
- Use emphasized styles for selection, key actions, unread/high-priority information, and intentional editorial moments. Do not bold every heading.
- Keep line height, tracking, weight, and font family bundled in the type token.
- Define normal-scale line count, wrapping, truncation, overflow recovery, and 200% text-size behavior for each role.
- Preserve information and functionality when text grows. Prefer reflow and flexible height over silent truncation.
- Test the real product fonts for EN/RU glyphs, numerals, punctuation, weight availability, and fallback behavior.
- Use one or two editorial treatments at meaningful moments; routine forms and settings should remain scannable.

## Shape

Material's rectangular corner-radius scale is:

| Role | Radius |
|---|---:|
| None | 0dp |
| Extra small | 4dp |
| Small | 8dp |
| Medium | 12dp |
| Large | 16dp |
| Large increased | 20dp |
| Extra large | 28dp |
| Extra large increased | 32dp |
| Extra extra large | 48dp |
| Full | Fully rounded |

- Use shape to group, direct attention, communicate state, and express brand.
- Preserve component-default shape roles unless a product-wide mapping is intentional.
- Use the expressive shape library and asymmetry selectively for imagery, avatars, hero content, or state transitions.
- Do not assign unrelated radii screen by screen.
- Use shape morph only when it clarifies selection, expansion, or transition; provide a reduced-motion/static alternative.

## Spacing, density, and elevation

### Spacing

- Base the spacing system on Material's 8dp scale and approved nested values such as 2dp, 4dp, 6dp, and 10dp where a component spec requires them.
- Map margins, padding, and gaps to semantic spacing tokens.
- Keep spacing stable when text scales unless reflow requires more room.
- Adapt layout spacing to breakpoint and density through tokens, not scattered conditionals.

### Density

- Default interactive targets to at least 48x48dp.
- Increase information density through layout and grouping before shrinking components.
- Never reduce default target size below the accessibility minimum.
- If users can change density, the control itself and all resulting states must remain accessible.

### Elevation

- Use Material elevation levels 0–5 and component defaults.
- Prefer tonal surface differences to heavy shadows.
- Use elevation to communicate overlap and z-order, not general decoration.
- Avoid changing a Material component's default elevation without a documented hierarchy reason.
- Keep the number of elevation levels in a screen small and coherent.

## Motion

Prefer the M3 physics system when supported:

- Expressive scheme for most products, hero moments, and key interactions.
- Standard scheme for highly utilitarian or restrained products.
- Spatial specs for position, size, orientation, and shape.
- Effects specs for color, opacity, and other non-spatial properties.
- Fast/default/slow speeds selected by element scale and interaction scope.

Rules:

- Choose one app-level motion scheme; let Material components inherit it.
- Use the same semantic motion tokens in custom components.
- Prefer springs for interruptible, retargetable, and size-adaptive movement.
- Use transitions to explain navigation, containment, selection, and cause/effect.
- Avoid motion that delays task completion or creates competing focal points.
- Respect reduced-motion settings: replace strong translation, scale, parallax, and morphs with subtle effects or immediate state changes.
- Loading animation must represent an actual process and expose progress semantics when known.

## Icons and imagery

- Use Material Symbols for standard actions and concepts when approved.
- Select one Symbols family—outlined, rounded, or sharp—and a coherent weight/fill strategy.
- Use outlined-to-filled changes for selected navigation or toggle states when the component guidance calls for it.
- Standard icons are normally 24dp; keep the interactive target at least 48dp.
- Use icon-only actions only when the symbol is widely understood and has an accessibility label; provide tooltips on pointer/keyboard platforms when needed.
- Treat decorative imagery as null semantics. Write alt text for meaningful imagery based on its purpose and context, not a visual inventory.
- Require source, license, tint behavior, light/dark variants, and minimum-size behavior for custom or brand assets.

## Interaction states and inputs

Define enabled, disabled, hovered, focused, pressed, dragged, selected, and error states wherever applicable.

- Use the component's state layer and token mappings rather than inventing per-screen opacity.
- Provide at least two cues for important state changes; selection cannot rely on color alone.
- Maintain focus visibility and logical focus order.
- Make the full label row interactive for checkbox, radio, and switch patterns when semantics stay unambiguous.
- Do not hide an essential action behind long press, drag, swipe, or hover without a single-pointer/keyboard alternative.
- Support interruption and reversal for gestures and motion.
- Use predictive back behavior where the Android host supports it, but keep shared navigation intent platform-neutral.

## Content, accessibility, and localization

- Design accessibility by default using Material component semantics, then add explicit semantics only where the built-in contract is insufficient.
- Structure content with meaningful headings and reading order.
- Ensure text contrast, non-text contrast, target size, focus, state announcements, and live-region behavior meet platform and project requirements.
- Keep critical information at the start of labels and notifications.
- Use short, direct, sentence-case labels; describe consequences for destructive or irreversible actions.
- Avoid idioms, ambiguous abbreviations, culture-specific examples without translator context, and concatenated strings.
- Plan for translation expansion; EN is the base locale and RU the initial additional locale under the shared localization contract.
- Provide manual text input alternatives for date/time pickers and accessible alternatives for horizontal carousels.
- Do not auto-dismiss actionable snackbars.

## Expressive product identity

Use these M3 Expressive tactics in a controlled hierarchy:

1. Vary shape to create a distinct silhouette or focus.
2. Use rich but role-correct color to sharpen hierarchy.
3. Use emphasized typography to guide attention.
4. Contain important content with space and surface contrast.
5. Add fluid motion to explain and reward interaction.
6. Adapt components and layouts to context and breakpoint.
7. Combine tactics in one or two hero moments.

A hero moment must be emotionally meaningful or central to the product task. It is brief, focused, accessible, and surrounded by calmer UI. Reject expressive changes that reduce comprehension, overwhelm the screen, obscure state, or force custom behavior where a canonical component works.

## Required design output

For each primary screen or flow provide:

- user task and hierarchy;
- canonical layout and breakpoint table;
- scaffold/inset ownership;
- navigation family and destination count;
- M3 component and variant map;
- color, typography, shape, spacing, elevation, icon, and motion tokens;
- complete interaction/state matrix;
- M3 Expressive adoption and fallback decisions;
- accessibility, localization, text-scale, input-method, and reduced-motion behavior;
- justified custom components and deviations;
- Compose Multiplatform API availability risks;
- light/dark and stress preview matrix.

## Primary sources

Verified 2026-08-11.

- [Material 3 foundations](https://m3.material.io/foundations)
- [Material 3 layout](https://m3.material.io/foundations/layout/layout-overview/overview)
- [Material breakpoints](https://m3.material.io/foundations/layout/breakpoints/overview)
- [Canonical layouts](https://m3.material.io/foundations/layout/canonical-examples/overview)
- [Design tokens](https://m3.material.io/foundations/design-tokens/overview)
- [Color system](https://m3.material.io/styles/color/system/overview)
- [Typography](https://m3.material.io/styles/typography/overview)
- [Shape](https://m3.material.io/styles/shape/overview-principles)
- [Spacing](https://m3.material.io/styles/spacing/overview)
- [Elevation](https://m3.material.io/styles/elevation/overview)
- [Motion physics](https://m3.material.io/styles/motion/overview/how-it-works)
- [Interaction states](https://m3.material.io/foundations/interaction/states/overview)
- [Accessibility-oriented design](https://m3.material.io/foundations/designing/overview)
- [Writing and text resizing](https://m3.material.io/foundations/writing/text-resizing)
- [M3 Expressive overview](https://m3.material.io/building-with-m3-expressive)
- [Material 3 in Compose](https://developer.android.com/develop/ui/compose/designsystems/material3)
