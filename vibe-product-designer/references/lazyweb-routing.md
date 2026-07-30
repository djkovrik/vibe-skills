# Lazyweb routing

Before product UI design, critique, or change:

1. Confirm `lazyweb_get_workflows` exists.
2. On the first Lazyweb use, call it with `operation=list` and `task_context="first run Lazyweb capabilities"`.
3. Run one `lazyweb_search` for each concrete 2–6 word primary-screen pattern and platform before design.
4. Follow the live workflow guide. For the current `lazyweb-design`, select intent-first:
   - `create`: new screen;
   - `improve`: design quality of an existing screen;
   - `optimize`: conversion/metric of an existing screen.
5. For existing full-resolution screens, use request-upload -> upload raw bytes -> resolve-upload -> pass `image_url`; do not use inline base64.
6. Use `lazyweb-apply-design-best-practices` for craft guidance and `lazyweb-propose-ui-changes` for reviewable proposals.
7. Poll the generated report and open/share its hosted URL.

For the post-golden gate:

1. Inventory every declared primary screen and risk-bearing state from the AppSpec.
2. Use the actual Paparazzi PNG for an existing screen; never substitute a design description when a golden exists.
3. Run the current `lazyweb-design` improve workflow per primary screen. Review both light and dark; when a single report cannot cover both, run separate reports. Add font-scale/long-locale states when text rendering is a declared risk.
4. Record report URLs and exact screen/state/theme coverage. A single representative screen is not a full-app review.
5. Review ordered flows against AppSpec acceptance scenarios. Use `lazyweb_get_flows` only when the current live workflow calls for ordered product-journey evidence; never use it for the first-run capability guide.
6. Treat terminal plan/limit responses as terminal. Do not fabricate evidence or silently replace Lazyweb with taste.
7. Classify findings as contract defect, Material 3/accessibility defect, evidence-backed improvement, or subjective preference. Fix/waive accordingly and re-run affected goldens.

Do not use retired names such as `lazyweb-design-research`, `deep-design-research`, `design-brainstorm`, or `quick-references` unless the live guide returns them again.

If Lazyweb is unavailable, disclose it and use official platform guidance plus stored target evidence.
