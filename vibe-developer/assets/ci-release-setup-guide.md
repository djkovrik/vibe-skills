# <App name>: CI and release setup

> Generated with the CI workflows. This checklist describes external state that source control cannot configure or prove. Do not mark an item complete without verifying it in the named console.

## Workflow inventory

Document `AnalysisAndTest.yml`, `MeasureTestCoverage.yml`, `CodeCoverageBadge.yml`, `CreateAndroidRelease.yml`, and `PublishAndroidRelease.yml`, including triggers, default branch, release order, and retry behavior.

## GitHub

- [ ] Protect `<default branch>` and require the quality/coverage checks used by this repository.
- [ ] Verify repository Actions permissions and allow only the permissions declared by the workflows.
- [ ] Create the protected `google-play-internal` environment; configure required reviewers and deployment branches/tags.
- [ ] Create repository variable `COVERAGE_GIST_ID` and secret `GIST_SECRET`; document the project-unique badge filename and README URL.
- [ ] Create the signing and publication secrets listed below without copying their values into this file:
  - `ANDROID_KEYSTORE_BASE64`
  - `ANDROID_KEYSTORE_PASSWORD`
  - `ANDROID_KEY_ALIAS`
  - `ANDROID_KEY_PASSWORD`
  - `GOOGLE_PLAY_SERVICE_ACCOUNT_JSON`
- [ ] Verify Git LFS checkout when snapshots or other required assets use LFS.

## Android upload key

- [ ] Enable Play App Signing and create a dedicated upload key for `<package ID>`; never use the debug key.
- [ ] Store at least two encrypted backups separately from Git and record alias, expiry, SHA-1, and SHA-256 fingerprints in the approved secret inventory.
- [ ] Base64-encode the keystore without printing it to logs and store it as `ANDROID_KEYSTORE_BASE64`.

## Firebase

- [ ] Create or select `<Firebase project>` and register Android app `<package ID>`.
- [ ] Enable only the Firebase products approved by the AppSpec: `<products>`.
- [ ] Download the current configuration to `<repository path>` and follow the repository's committed/secret-file policy.
- [ ] Verify Crashlytics delivery and symbolized mapping for the exact Internal-test `versionName`/`versionCode` without sending prohibited user data.
- [ ] Record approved Analytics, consent, age, location, and privacy decisions: `<decisions>`.

## Google Play Console

- [ ] Create `<app name>` with package `<package ID>`, default language `<locale>`, and the production owner account.
- [ ] Enable Play App Signing and register the upload certificate.
- [ ] Complete localized store listings for `<locales>`, support contacts, and the public privacy-policy URL.
- [ ] Complete App access, Content rating, Target audience, Ads, Data safety, and all current policy forms from actual SDK behavior.
- [ ] Create Internal testing and its tester list.
- [ ] Upload the first AAB manually if Play Developer API cannot see a newly created package until bootstrap.

## Google Cloud Console

- [ ] In `<Google Cloud project>`, enable Google Play Android Developer API.
- [ ] Create a dedicated release-automation service account and JSON key.
- [ ] Invite its email in Play Console and grant only app-scoped permissions needed to view app data and manage Internal releases.
- [ ] Store the complete JSON as GitHub secret `GOOGLE_PLAY_SERVICE_ACCOUNT_JSON`; do not commit or paste it elsewhere.

## First end-to-end run

- [ ] Confirm `AnalysisAndTest` and coverage workflows pass on `<default branch>`.
- [ ] Run `Create Android release` with the intended SemVer bump and every required localized note.
- [ ] Verify the tag, GitHub prerelease, signed APK/AAB, R8 mapping, optional native symbols, and Internal-track release.
- [ ] Perform physical-device install/upgrade, critical-flow, permissions, offline, accessibility, privacy, Crashlytics, and monetization acceptance applicable to the AppSpec.
- [ ] Record anything not executed as `NOT RUN`, not `PASS`.

## Retry, promotion, and rollback

Retry an external failure with `Publish Android release` for the same immutable tag. If source or artifacts change, create a new SemVer tag and `versionCode`. Promote the exact accepted AAB from Internal testing through controlled Play Console releases; never let CI auto-promote directly to production.
