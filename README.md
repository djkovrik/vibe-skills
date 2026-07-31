# Vibe KMP Skills

Локальный пакет из 13 Agent Skills для разработки Kotlin Multiplatform приложений под Android и iOS. Skills принимают согласованную спецификацию приложения, проектируют архитектуру, реализуют функциональность, проверяют UI и поведение, затем готовят проект к выпуску.

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

## Рабочий процесс с AppSpec

Работа разделена на две сессии:

1. В первой сессии обычный Codex помогает провести продуктовое интервью и подготовить Vibe AppSpec v1.2. Код приложения на этом этапе не пишется.
2. Спецификация проверяется локальным валидатором. Ошибки и blocking `openQuestions`, включая нерешённые custom icon/assets, нужно устранить до реализации.
3. В отдельной сессии `$vibe-developer` получает путь к AppSpec, проводит preflight репозитория и составляет план.
4. Оркестратор последовательно подключает нужные skills: архитектура → domain/data/platform → navigation/state → UI и icon/assets gate → previews → Paparazzi/ComposablePreviewScanner goldens → full-UI Lazyweb review → тесты и release checks.
5. Работа завершается отчётом о закрытых requirement IDs, изменённых модулях, выполненных проверках, рисках и отклонениях.

```text
product discovery
  -> Vibe AppSpec v1.2
  -> validation
  -> separate $vibe-developer session
  -> implementation and specialist hand-offs
  -> tests, goldens, platform builds, release checks
```

## Структура AppSpec

Готовый шаблон находится в [`vibe-developer/assets/app-spec-template/app-spec`](vibe-developer/assets/app-spec-template/app-spec).

```text
app-spec/
  app-spec.json
  product.md
  design.md
  domain.md
  data.md
  quality.md
  flows/FLOW-*.md
  screens/SCREEN-*.md
  assets/
```

JSON содержит метаданные, requirements, capabilities, `localization`, `uiQuality` и связи. Markdown описывает продукт, дизайн-систему и иконки, domain/data contracts, локализованные локальные данные, quality gates, пользовательские flows, состояния экранов и preview/golden matrix. App-bundled переводы живут в Compose Multiplatform Resources `strings.xml` под общими ключами: английский всегда default/base locale, русский — начальная дополнительная локаль. Domain/persistence хранят только стабильные IDs/keys, а native `actual` при необходимости использует Android/iOS localization resources с тем же английским default. Requirements, acceptance scenarios, flows и screens используют стабильные идентификаторы `REQ-*`, `AC-*`, `FLOW-*` и `SCREEN-*`.

AppSpec можно подготовить вручную, через обычный диалог с Codex, GitHub Spec Kit или OpenSpec. Эти инструменты не являются runtime-зависимостями пакета.

## Проверка и запуск

Проверить спецификацию:

```powershell
python .\vibe-developer\scripts\validate-app-spec.py D:\Projects\MyApp\app-spec
```

Начать реализацию в отдельной сессии:

```text
Используй $vibe-developer. Реализуй приложение по спецификации
D:\Projects\MyApp\app-spec.
Сначала проверь спецификацию и не меняй утверждённые требования молча.
```

Проверить и установить пакет:

```powershell
.\validate-vibe-skills.ps1
.\install-vibe-skills.ps1 -Mode Junction
```

Подробности установки и Copy mode описаны в [`INSTALL.md`](INSTALL.md). Полный список устанавливаемых каталогов хранится в [`vibe-skills-manifest.json`](vibe-skills-manifest.json).
