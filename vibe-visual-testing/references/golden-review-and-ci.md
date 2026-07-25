# Golden review and CI

Paparazzi provides record, verify, report, and failure/diff outputs. Use task names and directories from the target plugin version.

- Record only after product intent is approved.
- Inspect every new/materially changed image.
- Do not bless unrelated diffs.
- Verify in CI and upload failure/report artifacts.
- Use Git LFS for large snapshot sets.
- Keep deterministic environment/toolchain inputs.
- Report the record/verify exit code.

Primary sources:

- https://cashapp.github.io/paparazzi/
- https://github.com/cashapp/paparazzi

