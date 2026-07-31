# Screen states, responsiveness, and accessibility

For every screen decide applicability of loading, content, empty, error, offline, and permission states. Define actions, recovery, navigation, and data freshness in each state.

- Assign each safe-area/system inset to one owner.
- Design compact and expanded widths plus portrait/landscape where supported.
- Test large font scale, long EN/RU strings, RTL when required, keyboard, and screen reader order.
- Use production Compose `strings.xml` resources and identical keys across declared locales for app-bundled copy and local catalog text; never replace them with hardcoded preview labels.
- Use semantic headings, roles, labels, state descriptions, focus order, and minimum touch targets.
- Never encode meaning only by color.
- Respect reduced motion and avoid time-limited interaction without alternatives.
- Mark labels expected to remain one line at normal scale. Define `maxLines`, overflow, abbreviation prohibition, and what may wrap at the required stress scale.
- Include the longest supported locale and real production font in preview fixtures; do not use short placeholder strings to make a layout pass.
- Audit text-only interactive elements for a useful leading/trailing icon, while retaining text where recognition or accessibility would suffer.
- Give every semantic icon an action/meaning label; decorative icons use null semantics and never duplicate adjacent text.

Primary sources:

- https://developer.android.com/guide/topics/ui/accessibility
- https://developer.apple.com/design/human-interface-guidelines/accessibility
- https://www.w3.org/WAI/WCAG22/quickref/
