# CI and Android release baseline

Use this contract during the late-stage Project Architect pass. Adapt the BulbMatch workflow topology to the target repository; never copy project names, module paths, package IDs, task names, thresholds, branch names, SDK versions, or action versions without verification.

## Readiness gate

Start this pass as soon as all of the following succeed locally or in an existing trusted CI environment:

- Detekt;
- Kover verification and XML report generation;
- a task that prints only numeric line coverage;
- the required Android debug assembly;
- applicable iOS tests/framework linkage and other project-specific build gates.

Do not wait for signing keys, Firebase access, Google Play access, or GitHub secrets. Commit workflows with explicit missing-secret failures and create the setup guide in the same change.

## Inspect before generating

Derive the default branch, JDK, Gradle wrapper, Android application module, package ID, version inputs, APK/AAB/mapping/symbol paths, Kover report path and threshold, screenshot task/report paths, migration checks, iOS modules/workspace/scheme/Xcode requirements, Firebase usage, release verifier, and localized release-note locales from the target repository and AppSpec. Verify current action versions in official sources. Pin third-party or release-mutating actions to full commit SHAs; use least-privilege permissions everywhere.

## Required workflows

Create these five files under `.github/workflows/` even when their credential-dependent jobs cannot yet run end to end:

1. `AnalysisAndTest.yml`
   - Trigger on push and pull request to the derived default branch plus `workflow_dispatch`.
   - Use per-ref concurrency with cancellation and `contents: read` by default.
   - Run Android Detekt, tests, `koverVerify`, screenshot verification, migrations or validators, compilation, debug assembly, and applicable artifact/platform compatibility checks.
   - Run iOS tests, framework linkage, CocoaPods/workspace build, or the repository's equivalent on a compatible macOS/Xcode runner when iOS is in scope.
   - Upload reports with `if: always()` and screenshot diffs/failures with `if: failure()`.
2. `MeasureTestCoverage.yml`
   - Trigger for pull requests to the default branch and use per-PR concurrency.
   - Generate the Kover XML report, enforce the repository's overall and changed-line thresholds, and publish one updated PR comment only for same-repository branches. Do not expose write tokens to fork code.
   - Upload the XML report even when the threshold/comment step fails.
3. `CodeCoverageBadge.yml`
   - Trigger on default-branch pushes plus `workflow_dispatch` and serialize updates.
   - Run the numeric line-coverage task, reject unexpected output, and update a project-unique dynamic badge using `GIST_SECRET` and `COVERAGE_GIST_ID` unless the repository already has an approved equivalent.
   - Add the workflow and badge URLs to the README when a README exists.
4. `CreateAndroidRelease.yml`
   - Use a manual dispatch with SemVer bump and localized release-note inputs derived from supported store locales.
   - Authorize the configured release actor/role and default branch, validate note length, calculate a monotonic Google Play `versionCode`, create an annotated SemVer tag and GitHub prerelease, attach localized note files, then call the reusable publish workflow with inherited secrets.
   - Set only the prepare job's `contents` permission to write and disable cancellation for release creation.
5. `PublishAndroidRelease.yml`
   - Support SemVer tag pushes, manual retry of an existing tag, and `workflow_call` from release creation. Serialize by release tag and target a protected `google-play-internal` environment.
   - Check out the exact tag, validate SemVer and ancestry from the default branch, and reuse localized notes from inputs or the matching GitHub prerelease.
   - Fail clearly when signing or Google Play secrets are missing. Decode the upload keystore only in the runner temporary directory.
   - Validate the target Firebase configuration when Firebase is used. Build signed release APK and AAB from explicit version inputs; locate and verify signatures, R8 mapping, optional native symbols, and project-specific release invariants.
   - Upload artifacts, then publish the AAB, mapping, notes, and available symbols to Google Play Internal testing. Never auto-promote to production.

Keep target-specific validators when they protect real release invariants. Do not carry BulbMatch-only OCR, catalog hashes, ad IDs, Xcode paths, repository-owner policy, or package values into another project unless its own specification requires them.

## Required repository guide

Create `docs/CI-RELEASE-SETUP.md` in the target repository in the same change as the workflows. Use [the guide template](../assets/ci-release-setup-guide.md), replace every placeholder, remove irrelevant examples, and preserve these sections:

- generated workflow inventory, triggers, and dependency order;
- GitHub default branch protection, Actions permissions, protected environment, required reviewers/deployment branches, repository variables, secrets, coverage gist/token, and optional Git LFS checkout;
- Android upload key creation, encrypted backups, fingerprints, Base64 conversion, and the exact signing secret names;
- Firebase project/app registration, exact package ID, required products, configuration-file path and repository policy, Crashlytics/mapping verification, and privacy choices;
- Google Play app creation, Play App Signing, store listing/locales, policy/Data safety forms, Internal testing, testers, and the first-AAB manual bootstrap when required;
- Google Cloud project, Google Play Android Developer API, least-privilege service account, Play Console invitation/app-scoped permissions, JSON key handling, and `GOOGLE_PLAY_SERVICE_ACCOUNT_JSON`;
- first end-to-end dry run, expected artifacts, manual device acceptance, retry semantics, and promotion/rollback policy.

Always include GitHub, Firebase, Google Play, and Google Cloud Console headings. If a surface is genuinely not used, mark it `NOT APPLICABLE`, cite the repository/AppSpec reason, and remove corresponding workflow inputs rather than leaving misleading steps.

Never include secret values, private keys, service-account JSON, live tokens, or fabricated console state. Use `[ ]` checkboxes for external work and record exact identifiers/paths that are safe to commit. State that committed automation is not proof of configured external state.

## Validation

- Parse every YAML file and inspect expressions, event inputs, reusable-workflow contracts, permissions, concurrency, and artifact paths.
- Run a local action linter when available and all referenced Gradle tasks that do not require credentials.
- Verify that every workflow task/path exists and that no target-specific placeholder remains.
- Verify that every workflow secret/variable/environment appears in the guide and every guide name exactly matches YAML.
- Confirm tag/version calculations against first release, patch, minor, major, retry, duplicate-tag, and out-of-range cases.
- Report credential-dependent publication as `NOT RUN`, never `PASS`, until a real Internal-track upload succeeds.

## Source adaptation

This baseline is adapted from the BulbMatch CI/release source group in [source-registry.md](source-registry.md) as inspected on 2026-08-03. Treat that repository as structural evidence only and revalidate external action/platform details against current official documentation.
