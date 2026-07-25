# Placement and format decisions

Research placement through Product Designer and Lazyweb before SDK work.

- Inline: use as a regular content item where its size and interruption are acceptable.
- Sticky: reserve non-overlapping space; respect system navigation/insets.
- Interstitial: show only at a natural pause, never during critical input/navigation.
- Rewarded: explicit opt-in, clear reward, exactly-once grant, recoverable failure.
- App-open: avoid surprising foreground interruptions and respect startup/consent state.

Define frequency, loading placeholders, failure collapse, accessibility labels, and prohibited contexts in AppSpec. Do not infer a slot from available screen space.

Official format guidance:

- https://ads.yandex.com/helpcenter/en/dev/compose-multiplatform/quick-start

