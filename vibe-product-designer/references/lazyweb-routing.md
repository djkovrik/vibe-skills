# Lazyweb routing

Before product UI design, critique, or change:

1. Confirm `lazyweb_get_workflows` exists.
2. On the first Lazyweb use, call it with `operation=list` and `task_context="first run Lazyweb capabilities"`.
3. Run one `lazyweb_search` for a concrete 2–6 word screen pattern and platform.
4. Follow the live workflow guide. For the current `lazyweb-design`, select intent-first:
   - `create`: new screen;
   - `improve`: design quality of an existing screen;
   - `optimize`: conversion/metric of an existing screen.
5. For existing full-resolution screens, use request-upload -> upload raw bytes -> resolve-upload -> pass `image_url`; do not use inline base64.
6. Use `lazyweb-apply-design-best-practices` for craft guidance and `lazyweb-propose-ui-changes` for reviewable proposals.
7. Poll the generated report and open/share its hosted URL.

Do not use retired names such as `lazyweb-design-research`, `deep-design-research`, `design-brainstorm`, or `quick-references` unless the live guide returns them again.

If Lazyweb is unavailable, disclose it and use official platform guidance plus stored target evidence.

