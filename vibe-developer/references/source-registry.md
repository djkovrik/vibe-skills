# Local source registry

Keep all machine-specific absolute source paths here. Other `vibe-*` skills must link to this file instead of repeating them.

```text
VIBE_PACKAGE_ROOT = D:\Sources\vibe-skills
BLINKLY_ROOT = D:\Sources\Android\Blinkly
TACKLE_ROOT = D:\Sources\Android\Tackle
SKILL_CREATOR_ROOT = C:\Users\Sergey\.codex\skills\.system\skill-creator
COMPOSE_EXPERT_SKILL = C:\Users\Sergey\.codex\skills-src\compose-skill\skills\compose-expert\SKILL.md
LAZYWEB_SKILL = C:\Users\Sergey\.codex\skills\lazyweb\SKILL.md
```

## Source groups

- Blinkly build/release: root Gradle files, `gradle/libs.versions.toml`, `build-logic/`, convention plugins, platform apps, and `.github/workflows/`.
- Blinkly architecture: screen/flow modules under `shared/component/`, their contract/`integration/*Default`/`integration/*Preview`/Store/Manager/mapper files, `shared/domain/`, `shared/database/`, `shared/settings/`, `shared/alarm/`, `shared/notifier/`, `shared/compose/`, `shared/component/sync/`, `shared/utils/Unwrap.kt`, `shared/utils/StoreExt.kt`, and root common component tests.
- Blinkly visual testing: `shared/compose/build.gradle.kts`, its generated preview-test task, Android unit-test Paparazzi helpers, and `shared/compose/src/test/snapshots/`.
- Tackle networking: `shared/network/`, domain API contracts and exception model, mapper tests, and JSON fixtures.
- Blinkly advertising: `docs/yandex-inline-ads-macos-guide.md`.

Treat these as read-only adaptation evidence. Never copy project IDs, secrets, versions, packages, ad unit IDs, signing data, Firebase files, or app-specific thresholds.
