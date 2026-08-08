# Golden review and CI

Paparazzi provides record, verify, report, and failure/diff outputs. Use task names and directories from the target plugin version.

- Record only after product intent is approved.
- Inspect every new/materially changed image.
- Do not bless unrelated diffs.
- Treat record and verify as separate gates: record creates the proposed baseline; a successful verify proves only that rendering matches that baseline, not that the UI is well designed.
- After the initial approved record, hand all golden paths plus an explicit screen order and coverage inventory to Product Designer for the mandatory Lazyweb/full-UI review. Require one screen per report, exactly one report in flight, and receipt/recording of the current report before the next screen is submitted; never parallelize the queue.
- Re-record only findings whose fix is approved. Run complete verify afterward so a local fix cannot hide cross-screen drift.
- Verify in CI and upload failure/report artifacts.
- Use Git LFS for large snapshot sets.
- Keep deterministic environment/toolchain inputs.
- Report the record/verify exit code.
- Report snapshot counts by screen/state/theme and any declared coverage gaps or waivers.

Primary sources:

- https://cashapp.github.io/paparazzi/
- https://github.com/cashapp/paparazzi
