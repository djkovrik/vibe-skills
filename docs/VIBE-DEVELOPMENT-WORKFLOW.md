# Vibe development workflow

Этот документ — основной пользовательский источник правды о том, как работать с набором `vibe-*` skills: от идеи приложения до проверенной реализации. Нормативные технические правила находятся в самих skills и связанных с ними контрактах; этот документ объясняет, когда их применять и что должен предоставить пользователь.

## Источники правды и приоритеты

При расхождениях применяйте следующий порядок:

1. Явные решения пользователя и утверждённый AppSpec.
2. Инструкции, код, тесты и build logic целевого репозитория.
3. Текущие `vibe-*` skills и их контракты.
4. Шаблон AppSpec.
5. Примеры промптов из этого документа.

Примеры промптов — только удобный интерфейс запуска. Они не должны копировать весь технический контракт и не могут отменять требования skills. Если продукту действительно нужно отклонение от стандартной архитектуры, локализации, визуального тестирования или CI, его нужно явно согласовать и записать в AppSpec вместе с причиной и проверками.

Основные нормативные файлы:

- [`vibe-developer/SKILL.md`](../vibe-developer/SKILL.md) — end-to-end orchestration и общие quality gates;
- [`app-spec-contract.md`](../vibe-developer/references/app-spec-contract.md) — формат и обязательные поля AppSpec;
- [`localization-contract.md`](../vibe-developer/references/localization-contract.md) — локализация bundled text и local data;
- [`ci-release-contract.md`](../vibe-developer/references/ci-release-contract.md) — обязательный CI/release baseline;
- [`routing-matrix.md`](../vibe-developer/references/routing-matrix.md) — владельцы узких задач и hand-offs;
- [актуальный шаблон AppSpec](../vibe-developer/assets/app-spec-template/app-spec).

## Два этапа работы

Разделяйте подготовку спецификации и реализацию на две сессии:

```text
product discovery and UI evidence
  -> approved Vibe AppSpec
  -> local validation
  -> separate $vibe-developer session
  -> implementation and specialist hand-offs
  -> tests, goldens, design review, platform and release gates
```

Так продуктовые решения не смешиваются с написанием кода, а `$vibe-developer` получает проверенный контракт и не переизобретает продукт во время реализации.

## Этап 1. Подготовить AppSpec

На этом этапе обычный Codex помогает провести продуктовое интервью. `$vibe-developer` здесь не является интервьюером: его вход — уже согласованный AppSpec или достаточно структурированный implementation brief.

### Что нужно решить с пользователем

До реализации зафиксируйте:

- цели, аудиторию, must-have требования и non-goals;
- Android/iOS targets, минимальные версии и существенные ограничения;
- пользовательские flows, все основные экраны и их состояния;
- domain rules, data sources, offline/sync, platform capabilities и privacy;
- accessibility, поддерживаемые локали и product-specific quality criteria;
- визуальное направление, интерактивные элементы, стандартный набор иконок и необходимые custom/brand assets;
- monetization decisions и допустимые ad slots, если реклама входит в продукт;
- все нерешённые решения в `openQuestions`; материальные блокеры — с `blocking: true`.

Перед проектированием product UI используйте Lazyweb по правилам `vibe-product-designer`. Нерешённые иконки или assets, способные изменить экран, блокируют Compose implementation.

### Рекомендуемый промпт для подготовки спецификации

```text
Помоги спроектировать Kotlin Multiplatform приложение для Android и iOS.
Проведи продуктовое интервью: выясни цели, аудиторию, требования, non-goals,
ограничения, domain/data/platform capabilities, все пользовательские flows,
экраны и их состояния. Код приложения пока не пиши.

До фиксации UI используй Lazyweb по правилам установленного
$vibe-product-designer. Составь инвентарь интерактивных элементов и assets;
попроси утвердить стандартный набор иконок или предоставить необходимые
custom/brand assets. Нерешённые материальные вопросы запиши как blocking
openQuestions и не принимай продуктовые решения молча.

После согласования создай AppSpec по актуальному шаблону
<vibe-skills>/vibe-developer/assets/app-spec-template/app-spec и контракту
<vibe-skills>/vibe-developer/references/app-spec-contract.md; используй
<vibe-skills>/vibe-developer/SKILL.md для orchestration guarantees. Сохрани
результат в <target-repository>/app-spec. Сохрани обязательный технический
профиль шаблона и vibe-* skills; не ослабляй и не заменяй его без явного
согласованного решения. Проверь AppSpec локальным валидатором и исправь ошибки
до передачи в реализацию.
```

Пользовательскому промпту не нужно перечислять `Kotlin Result`, `unwrap`, `Value<Model>`, Paparazzi и остальные внутренние правила. Фраза про актуальный шаблон, контракт и обязательный технический профиль защищает промпт от рассинхронизации со skills. Конкретные product decisions, напротив, нельзя прятать в skills: они должны быть явно получены от пользователя и записаны в AppSpec.

## Формат Vibe AppSpec

Текущий обязательный формат для новых спецификаций — Vibe AppSpec v1.3:

```text
app-spec/
  app-spec.json             # metadata, requirements, links and machine-checkable contracts
  product.md                # audience, goals, non-goals and user stories
  design.md                 # Lazyweb evidence, design tokens, icon/assets and preview matrix
  domain.md                 # entities, invariants, rules, errors and time semantics
  data.md                   # API, database, settings, offline, sync and localized local data
  quality.md                # architecture, tests, accessibility, privacy and release gates
  flows/
    FLOW-*.md               # user journeys and Given/When/Then acceptance scenarios
  screens/
    SCREEN-*.md             # states, actions, text behavior and golden coverage
  assets/                   # approved product-specific assets
```

`app-spec.json` нужен для машинной проверки. Markdown-файлы нужны для обсуждения продуктового намерения, поведения и acceptance criteria. Используйте стабильные идентификаторы `REQ-NNN`, `FLOW-NNN`, `SCREEN-NNN` и `AC-NNN`; связывайте requirements с acceptance scenarios, flows и screens.

Для новых приложений не создавайте структуру вручную по памяти: копируйте [актуальный шаблон](../vibe-developer/assets/app-spec-template/app-spec), затем заменяйте пример реальными решениями. Дополнительные поля разрешены, но обязательные поля текущего контракта удалять нельзя.

## Обязательный технический профиль

Эти правила не являются пользовательскими предпочтениями по умолчанию. Они принадлежат skills, отражаются в AppSpec и проверяются при реализации.

Blinkly и Tackle остаются помеченными reference adaptations, а не прямым шаблоном для копирования. Обязательны не случайные детали конкретного reference app, а уже извлечённые и закреплённые в текущих skills, contracts, template и checks правила. К исходникам reference app обращаются через `source-registry.md` только когда это действительно нужно.

| Область | Обязательная гарантия | Основной владелец |
| --- | --- | --- |
| Component state | Каждый production Decompose `Value<Model>` — immutable, backed retained Store и отдельным `State -> Model` mapper; router-owned `Value<Child*>` и полностью stateless callback components — оговорённые исключения | Decompose + MVIKotlin |
| Data boundary | Stateful Store работает с data/external operations через feature Manager; используется стандартный Kotlin `Result<T>`, одна `runCatching` boundary и cancellation-aware `unwrap`, без `Result<Result<T>>` | MVIKotlin + Domain |
| Modules | Экран или cohesive flow — стандартная component-module boundary; группировка допустима только с зафиксированной причиной | Project Architect + Decompose |
| Preview implementation | Для deterministic Compose previews создаётся sibling Preview component implementation | Decompose + Product Designer |
| Visual coverage | Для каждого primary screen и applicable state обязательны light/dark previews; stress variants выбираются по рискам font scale, locale и device/layout | Product Designer + Visual Testing |
| Golden tests | Paparazzi и ComposablePreviewScanner размещаются в Compose UI/resource-owning module; отдельный host требует архитектурного обоснования | Project Architect + Visual Testing |
| Design review | После утверждённых goldens выполняется полный Lazyweb review: строго по одному screen/report за раз, затем approved fixes и повторная golden verification | Product Designer + Visual Testing |
| Localization | `en` — полный default/base locale, `ru` — начальная дополнительная локаль, выбор языка только системный; bundled text хранится в resources, domain/persistence — только stable IDs/keys | Все владельцы по localization contract |
| Behavioral tests | Acceptance coverage возглавляют Decompose component tests через public contracts; централизованный suite живёт в отдельном `root` component module, когда dependency graph это позволяет | Test Engineer |
| CI and release | После readiness gate создаются пять baseline workflows и `docs/CI-RELEASE-SETUP.md`; отсутствие внешних credentials отмечается честно и не отменяет scaffolding | Project Architect |

Технические гарантии закреплены на нескольких уровнях:

1. specialist skills определяют реализацию и hand-offs;
2. `app-spec.json` хранит обязательные `architecture`, `localization` и `uiQuality` contracts;
3. `quality.md` задаёт architecture, localization, visual и release checks;
4. валидатор блокирует структурные нарушения до реализации;
5. `$vibe-developer` сверяет реализацию с requirement/acceptance IDs и не считает работу завершённой без применимых quality gates.

Так правила остаются обязательными, но не размножаются и не устаревают в каждом пользовательском промпте.

## Проверить AppSpec

Из корня `vibe-skills`:

```powershell
python .\vibe-developer\scripts\validate-app-spec.py <target-repository>\app-spec
```

Или абсолютным путём:

```powershell
python <vibe-skills>\vibe-developer\scripts\validate-app-spec.py <target-repository>\app-spec
```

Ошибки и unresolved blocking questions останавливают реализацию. Warnings и non-blocking questions нужно показать и осознанно разобрать, но не смешивать с failures.

## Этап 2. Реализовать AppSpec

Начинайте реализацию в отдельной сессии:

```text
Используй $vibe-developer. Реализуй приложение по утверждённой спецификации
<target-repository>/app-spec в репозитории <target-repository>.
Сначала проверь AppSpec валидатором и выполни repository preflight.
Покажи dependency-aware план и не меняй утверждённые продуктовые требования
или обязательный технический профиль молча. Выполни все применимые quality,
visual, platform, CI и release gates; недоступные внешние проверки явно отметь.
```

`$vibe-developer` выбирает только затронутые стадии и передаёт каждую границу одному владельцу. Типичная полная последовательность:

```text
AppSpec validation -> repository preflight -> architecture
-> product/design evidence -> icon and asset gate
-> domain -> persistence/network/sync/platform
-> Decompose -> MVIKotlin -> Compose -> monetization
-> non-visual tests -> previews -> Paparazzi/scanner -> approved goldens
-> full-UI Lazyweb review -> approved fixes and golden re-verification
-> Detekt/Kover/build readiness -> CI/release baseline
-> quality/platform/release checks
```

Для узкой задачи вызывайте профильный skill напрямую, пользуясь [`routing-matrix.md`](../vibe-developer/references/routing-matrix.md). Не запускайте полный application workflow ради одного SQLDelight query, Store transition или preview fix.

## Когда работа считается завершённой

Финальный отчёт должен содержать:

- закрытые requirement и acceptance IDs;
- изменённые модули и использованные owners;
- выполненные команды с успешными exit codes;
- непройденные или недоступные проверки и точную причину;
- риски, отклонения и явно согласованные waivers;
- состояние goldens и полного post-golden Lazyweb review;
- состояние CI/release automation отдельно от внешней настройки GitHub, Firebase, Google Play и Google Cloud.

Наличие сгенерированного кода само по себе не означает завершение. Применимые component tests, visual matrix, golden verification, platform builds и quality gates являются частью результата.

## Spec Kit и OpenSpec

GitHub Spec Kit и OpenSpec можно использовать как дополнительный discovery/planning слой:

```text
constitution -> specify -> clarify -> plan -> checklist -> tasks -> analyze
-> conversion to Vibe AppSpec -> validation -> $vibe-developer
```

Они необязательны и не заменяют Vibe AppSpec. Перед реализацией результат всё равно нужно преобразовать в текущий формат AppSpec и проверить локальным валидатором.
