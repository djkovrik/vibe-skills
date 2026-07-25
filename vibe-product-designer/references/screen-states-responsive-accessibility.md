# Screen states, responsiveness, and accessibility

For every screen decide applicability of loading, content, empty, error, offline, and permission states. Define actions, recovery, navigation, and data freshness in each state.

- Assign each safe-area/system inset to one owner.
- Design compact and expanded widths plus portrait/landscape where supported.
- Test large font scale, long EN/RU strings, RTL when required, keyboard, and screen reader order.
- Use semantic headings, roles, labels, state descriptions, focus order, and minimum touch targets.
- Never encode meaning only by color.
- Respect reduced motion and avoid time-limited interaction without alternatives.

Primary sources:

- https://developer.android.com/guide/topics/ui/accessibility
- https://developer.apple.com/design/human-interface-guidelines/accessibility
- https://www.w3.org/WAI/WCAG22/quickref/

