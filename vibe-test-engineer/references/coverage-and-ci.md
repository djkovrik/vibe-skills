# Coverage and CI

- Configure Kover report filters before measuring a baseline. Coverage must describe the production behavior the test strategy is expected to protect, not the entire repository.
- Include the smallest package/class patterns that cover:
  - domain entities with behavior, value objects, pure algorithms, Managers, Watchers, Providers, and other domain decision logic;
  - production Decompose behavior: `*Default` component implementations, retained Stores and Store providers, Executors/Reducers, navigation/config logic, and State-to-component-Model mappers.
- Exclude Compose rendering, previews/sample data, generated sources, resource accessors, DTO-only/schema-generated code, SQLDelight-generated implementations, platform/DI/composition-root glue, and other passive or framework-owned code. Do not include persistence, network, sync, or platform implementations merely to raise the denominator; add them only when the AppSpec identifies their behavior as part of the coverage gate.
- Derive filters from the target module/package graph rather than copying Blinkly package names. Use Kover `includes` as the positive scope and narrow `excludes` only for generated/passive exceptions; inspect the XML/HTML class inventory to prove that intended domain and Decompose classes are present and unrelated classes are absent.
- In a multi-module build, aggregate only modules needed to execute tests or supply in-scope classes. A test-host module may participate without adding its own production classes to the report.
- After filters are fixed, run the complete deterministic test set and generate Kover XML plus numeric line coverage before adding a verification bound. Record the measured percentage and report path.
- Immediately set the initial CI minimum to `floor(current line coverage percentage)` as a whole-number percentage. This preserves the measured baseline while allowing less than one percentage point of rounding. If repeat runs differ, fix nondeterminism first; only when it cannot be removed may the bound use the lowest of at least three clean runs, with a documented maximum two-point margin and owner. Never choose an aspirational threshold above the passing baseline, a generic copied threshold, or omit the gate because current coverage is low.
- Run `koverVerify` immediately after setting the bound and require it in local `check`, `AnalysisAndTest.yml`, and `MeasureTestCoverage.yml`. The XML report, numeric-only task, and verification rule must use the same filters, tests, aggregation, line counter, and threshold.
- Keep the committed threshold from decreasing silently. A reduction requires an explicit rationale and approval; coverage improvement may raise it after a clean baseline run.
- Set coverage expectations by risk/module and inspect uncovered decision branches.
- Do not add meaningless assertions to raise a percentage.
- Run focused tests first, then aggregate KMP/Android/iOS checks.
- Publish test reports and actionable failure artifacts.
- Keep flaky retry/quarantine visible and time-bounded.
- Fail CI on non-zero task exit codes; do not infer success from log text.
- Keep visual verification in Visual Testing and combine its status only at the pipeline level.

Primary reference: https://kotlin.github.io/kotlinx-kover/gradle-plugin/

Blinkly adaptation: its Kover include/exclude structure is useful evidence through the shared source registry, especially the focus on domain and component implementation classes. Re-derive packages, exclusions, and the initial threshold from the target repository; never copy Blinkly's package names or coverage value.
