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

Lazyweb supplies evidence about real product patterns; current official Material 3 guidance supplies the normative component, accessibility, token, and Compose contract. When they conflict, preserve Material semantics and label the Lazyweb pattern as inspiration or a proposed deviation.

For the post-golden gate:

1. Inventory every declared primary screen and risk-bearing state from the AppSpec and put the screens in an explicit review order.
2. Use the actual Paparazzi PNG for an existing screen; never substitute a design description when a golden exists.
3. Run the current `lazyweb-design` improve workflow with exactly one screen per report and exactly one report in flight for the task. Never batch multiple screens into a report or parallelize report creation through concurrent tool calls, agents, or branches.
4. Wait for the current screen report to reach terminal completion, retrieve/open it, and record its URL, exact screen/state/theme coverage, and findings before submitting any next report. Review light and dark; when one report cannot cover both, finish their separate reports sequentially before moving to the next screen. Add font-scale/long-locale states when text rendering is a declared risk.
5. A single representative screen is not a full-app review. Continue the ordered queue until every declared screen is covered or explicitly blocked/waived.
6. Review ordered flows against AppSpec acceptance scenarios. Use `lazyweb_get_flows` only when the current live workflow calls for ordered product-journey evidence; never use it for the first-run capability guide.
7. Treat terminal plan/limit responses as terminal. Do not fabricate evidence or silently replace Lazyweb with taste.
8. Classify findings as contract defect, Material 3/accessibility defect, evidence-backed improvement, or subjective preference. Fix/waive accordingly and re-run affected goldens.

Do not use retired names such as `lazyweb-design-research`, `deep-design-research`, `design-brainstorm`, or `quick-references` unless the live guide returns them again.

If Lazyweb is unavailable, disclose it and use official platform guidance plus stored target evidence.
