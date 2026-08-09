# Vibe KMP Skills

Локальный пакет из 13 Agent Skills для разработки Kotlin Multiplatform приложений под Android и iOS. Skills принимают согласованную спецификацию приложения, проектируют архитектуру, реализуют функциональность, проверяют UI и поведение, затем готовят проект к выпуску.

## Начало работы

Основной пользовательский процесс, формат AppSpec, актуальные примеры промптов и граница между решениями пользователя и обязательными гарантиями skills описаны в [`docs/VIBE-DEVELOPMENT-WORKFLOW.md`](docs/VIBE-DEVELOPMENT-WORKFLOW.md). Используйте его как точку входа вместо копирования технического чек-листа в каждый промпт.

Коротко: сначала в отдельной сессии подготовьте и утвердите Vibe AppSpec, затем проверьте его валидатором и передайте `$vibe-developer` для реализации.

## Состав пакета

Главная точка входа — [`vibe-developer`](vibe-developer/SKILL.md). Он проверяет AppSpec и целевой репозиторий, строит dependency-aware план и подключает только нужных специалистов:

- [`vibe-project-architect`](vibe-project-architect/SKILL.md) — модули, Gradle, DI, CI и release;
- [`vibe-domain-engineer`](vibe-domain-engineer/SKILL.md) — domain model, инварианты, ошибки и расчёты;
- [`vibe-decompose-engineer`](vibe-decompose-engineer/SKILL.md) — компоненты, navigation и lifecycle;
- [`vibe-mvikotlin-engineer`](vibe-mvikotlin-engineer/SKILL.md) — Stores и state-machine orchestration;
- [`vibe-platform-engineer`](vibe-platform-engineer/SKILL.md) — Android/iOS API, permissions, alarms и notifications;
- [`vibe-network-engineer`](vibe-network-engineer/SKILL.md) — Ktor, REST, OAuth, DTO и retries;
- [`vibe-persistence-engineer`](vibe-persistence-engineer/SKILL.md) — SQLDelight, migrations и Settings;
- [`vibe-sync-engineer`](vibe-sync-engineer/SKILL.md) — snapshots, conflicts и offline sync;
- [`vibe-product-designer`](vibe-product-designer/SKILL.md) — Lazyweb research, UI/UX, themes и accessibility;
- [`vibe-visual-testing`](vibe-visual-testing/SKILL.md) — previews, Paparazzi и goldens;
- [`vibe-monetization-engineer`](vibe-monetization-engineer/SKILL.md) — безопасные ad placements и Yandex Ads KMP;
- [`vibe-test-engineer`](vibe-test-engineer/SKILL.md) — весь non-visual test pyramid.

Каждый specialist можно вызывать напрямую для узкой задачи. Матрица владельцев и hand-off правил находится в [`routing-matrix.md`](vibe-developer/references/routing-matrix.md).

## Проверка и запуск

Проверить спецификацию:

```powershell
python .\vibe-developer\scripts\validate-app-spec.py D:\Projects\MyApp\app-spec
```

Начать реализацию в отдельной сессии:

```text
Используй $vibe-developer. Реализуй приложение по спецификации
D:\Projects\MyApp\app-spec.
Сначала проверь спецификацию, выполни repository preflight и не меняй
утверждённые требования или обязательный технический профиль молча.
```

Проверить и установить пакет:

```powershell
.\validate-vibe-skills.ps1
.\install-vibe-skills.ps1 -Mode Junction
```

Подробности установки и Copy mode описаны в [`INSTALL.md`](INSTALL.md). Полный список устанавливаемых каталогов хранится в [`vibe-skills-manifest.json`](vibe-skills-manifest.json).
