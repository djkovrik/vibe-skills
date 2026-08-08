# Промпт для создания пакета `vibe-*` skills

## Роль и конечная цель

Ты работаешь в новой сессии Codex в каталоге `D:\Sources\vibe-skills`.

Создай здесь законченный локальный пакет Agent Skills с префиксом `vibe-` для разработки Kotlin Multiplatform мобильных приложений под Android и iOS. Пакет должен уметь принять уже подготовленную спецификацию приложения, спроектировать архитектуру, реализовать приложение, проверить его и подготовить к выпуску.

Используй системный skill `skill-creator` и строго следуй его актуальному `SKILL.md`. Перед любыми действиями полностью прочитай:

- `C:\Users\Sergey\.codex\skills\.system\skill-creator\SKILL.md`;
- `C:\Users\Sergey\.codex\skills\.system\skill-creator\references\openai_yaml.md`;
- `D:\Sources\Android\Blinkly\AGENTS.md`;
- существующие Blinkly skills:
  - `D:\Sources\Android\Blinkly\.ai\skills\mvikotlin\SKILL.md`;
  - `D:\Sources\Android\Blinkly\.ai\skills\decompose\SKILL.md`;
  - `D:\Sources\Android\Blinkly\.ai\skills\decompose-component-tests\SKILL.md`.

Также прочитай инструкции репозитория, если в `D:\Sources\vibe-skills` к моменту запуска появятся `AGENTS.md` или другие локальные instruction-файлы.

Не ограничивайся генерацией каркасов. Заполни все skills прикладными процедурами, ссылками на первичные источники, правилами принятия решений, проверками и краткими рабочими примерами. После создания проверь пакет целиком и установи или синхронизируй его глобально на этом ПК безопасным идемпотентным скриптом.

## Что не нужно делать

- Не создавай отдельные subagents или agent personas. Здесь нужны именно skills, загружаемые по контексту. Делегирование в будущих задачах может выполнять оркестратор, если среда его поддерживает, но оно не является частью формата пакета.
- Не копируй Blinkly целиком и не превращай skills в документацию одного приложения.
- Не фиксируй версии библиотек как вечные истины. Сначала считывай версии и плагины из целевого проекта, а для новых интеграций проверяй актуальную официальную документацию.
- Не переноси проектные идентификаторы, bundle IDs, ad unit IDs, Firebase-файлы, signing secrets и другие значения Blinkly/Tackle.
- Не добавляй в каждый skill лишние `README.md`, changelog или дублирующую документацию. Следуй progressive disclosure из `skill-creator`.
- Не редактируй `D:\Sources\Android\Blinkly` и `D:\Sources\Android\Tackle`: это read-only источники архитектурных паттернов.
- Не внедряй Spec Kit или OpenSpec как обязательную runtime-зависимость skills.
- Не меняй глобальные skills до успешной локальной валидации всего пакета.

## Порядок доверия к источникам

Во всех skills зафиксируй единый приоритет решений:

1. Явные решения пользователя и входная спецификация текущего приложения.
2. `AGENTS.md`, instruction-файлы, код, тесты, version catalog и build logic целевого проекта.
3. Актуальная официальная документация конкретной библиотеки или платформы.
4. Принятые пользователем записи в базе изученных паттернов `vibe-*`.
5. Проверенные архитектурные паттерны Blinkly и сетевые паттерны Tackle.
6. Общие инженерные эвристики.

Если источники расходятся:

- не скрывай конфликт;
- укажи, какие сведения устарели или относятся только к проекту-ориентиру;
- выбери решение по этому порядку;
- при materially different вариантах запроси решение пользователя;
- после выбора добавь тест или проверку, которая фиксирует решение.

## Реестр локальных источников

Все абсолютные пути к кодовым базам и локальным инструкциям храни только в одном файле:

`vibe-developer/references/source-registry.md`

Начальное содержимое реестра:

```text
VIBE_PACKAGE_ROOT = D:\Sources\vibe-skills
BLINKLY_ROOT = D:\Sources\Android\Blinkly
TACKLE_ROOT = D:\Sources\Android\Tackle
SKILL_CREATOR_ROOT = C:\Users\Sergey\.codex\skills\.system\skill-creator
COMPOSE_EXPERT_SKILL = C:\Users\Sergey\.codex\skills-src\compose-skill\skills\compose-expert\SKILL.md
LAZYWEB_SKILL = C:\Users\Sergey\.codex\skills\lazyweb\SKILL.md
```

В остальных skills не повторяй конкретные Blinkly/Tackle paths. Ссылайся относительным путём на:

`../vibe-developer/references/source-registry.md`

Поскольку все `vibe-*` каталоги устанавливаются рядом, этот путь должен работать и в исходном пакете, и после глобальной установки. Добавь в installer post-check, который проверяет этот инвариант для каждого skill.

## Архитектурное решение по пакету

Создай 13 skills:

1. `vibe-developer`
2. `vibe-project-architect`
3. `vibe-domain-engineer`
4. `vibe-decompose-engineer`
5. `vibe-mvikotlin-engineer`
6. `vibe-platform-engineer`
7. `vibe-network-engineer`
8. `vibe-persistence-engineer`
9. `vibe-sync-engineer`
10. `vibe-product-designer`
11. `vibe-visual-testing`
12. `vibe-monetization-engineer`
13. `vibe-test-engineer`

Это skills, а не постоянно работающие агенты. Причина: их знания нужны по этапам, и progressive disclosure позволяет не загружать весь корпус в каждую задачу.

`vibe-developer` является оркестратором. Остальные skills остаются независимо вызываемыми: их frontmatter descriptions должны уверенно срабатывать и при прямом запросе пользователя, и при маршрутизации из оркестратора.

Не используй название `architector`; корректное имя — `vibe-project-architect`.

## Обязательная структура пакета

В корне `D:\Sources\vibe-skills` создай:

```text
vibe-skills-manifest.json
INSTALL.md
install-vibe-skills.ps1
validate-vibe-skills.ps1
vibe-developer/
vibe-project-architect/
vibe-domain-engineer/
vibe-decompose-engineer/
vibe-mvikotlin-engineer/
vibe-platform-engineer/
vibe-network-engineer/
vibe-persistence-engineer/
vibe-sync-engineer/
vibe-product-designer/
vibe-visual-testing/
vibe-monetization-engineer/
vibe-test-engineer/
```

Каждый skill обязан иметь:

```text
<skill>/
  SKILL.md
  agents/
    openai.yaml
  references/
    ... только нужные этому skill материалы
```

Создавай `scripts/` и `assets/` только там, где они действительно нужны.

Frontmatter каждого `SKILL.md`:

- содержит только `name` и `description`;
- использует lowercase hyphen-case;
- description перечисляет не только назначение, но и явные trigger phrases/ситуации;
- не превышает ограничения из актуального `skill-creator`.

Основной `SKILL.md`:

- написан в повелительной форме;
- желательно короче 500 строк;
- содержит routing и workflow, а подробности выносит в `references/`;
- не дублирует большие фрагменты официальной документации;
- прямо указывает, какие reference-файлы читать для какого вида задачи;
- не создаёт цепочки ссылок глубже одного уровня;
- содержит разделы `When to use`, `Inputs`, `Workflow`, `Decision rules`, `Validation`, `Escalation/hand-off`, `Reusable learning`.

## Создание каркасов через `skill-creator`

Не создавай skill-каталоги вручную. Для каждого skill используй:

```powershell
python "C:\Users\Sergey\.codex\skills\.system\skill-creator\scripts\init_skill.py" <skill-name> `
  --path "D:\Sources\vibe-skills" `
  --resources <comma-separated-needed-resources>
```

Не используй `--examples`, если затем не удалишь все нерелевантные placeholder-файлы.

После заполнения каждого skill сгенерируй или обнови:

```powershell
python "C:\Users\Sergey\.codex\skills\.system\skill-creator\scripts\generate_openai_yaml.py" `
  "D:\Sources\vibe-skills\<skill-name>"
```

Настрой `agents/openai.yaml` осмысленно:

- короткий `display_name`;
- понятное описание;
- `default_prompt`, который ссылается на skill как `$vibe-...`;
- визуальные поля добавляй только если они действительно нужны;
- не добавляй MCP dependencies в `openai.yaml`, если skill может корректно проверить доступность инструмента во время выполнения.

## Контракт `vibe-developer`

Сделай этот skill точкой входа для полного цикла приложения.

Он должен:

- принять путь к AppSpec или структурированное описание задачи;
- провести preflight целевого репозитория;
- прочитать инструкции и обнаружить стек, версии, модули, source sets, платформы и доступные skills/tools;
- составить dependency-aware план;
- вызвать только нужные specialist skills;
- предотвращать конфликтующие изменения нескольких специалистов;
- управлять проверками, Gradle-командами и итоговой приёмкой;
- сообщать допущения и блокеры;
- не считать задачу завершённой, пока код, тесты, UI golden verification и требуемые platform builds не согласованы;
- предлагать сохранить действительно повторно используемые новые паттерны.

### Preflight оркестратора

Перед планированием:

1. Найди ближайшие `AGENTS.md`/instruction-файлы.
2. Сними `git status`, но не изменяй и не удаляй пользовательские правки.
3. Прочитай `settings.gradle(.kts)`, root build file, `gradle/libs.versions.toml`, convention plugins и platform entry points.
4. Построй карту модулей и зависимостей.
5. Определи Android/iOS targets, Java/Kotlin toolchain, minimum OS/API, package IDs, build variants.
6. Найди существующие domain contracts, DI composition root, Decompose components, Stores, persistence, network, sync, ads, previews и tests.
7. Проверь доступность specialist skills, `compose-expert` и Lazyweb tools.
8. Проверь входную спецификацию и составь список неизвестных.

### Оркестрация этапов

Используй эту последовательность как default, но пропускай ненужные этапы:

```text
AppSpec validation
  -> repository preflight
  -> architecture/module plan
  -> product/design research
  -> domain contracts and invariants
  -> persistence/network/sync/platform capabilities
  -> Decompose component tree
  -> MVIKotlin stores and managers
  -> Compose UI and theme
  -> monetization integration where requested
  -> unit/component/integration tests
  -> previews and Paparazzi goldens
  -> Detekt/coverage/build/platform/release checks
  -> spec-to-implementation convergence report
```

Для изменения существующего приложения сначала выделяй минимальный affected subgraph, а не прогоняй весь pipeline без необходимости.

### Gradle-правила

Перенеси из Blinkly устойчивый протокол запуска:

- используй wrapper целевого проекта;
- предпочитай точечные задачи модулей;
- в PowerShell перенаправляй stdout и stderr в UTF-8 log-файл;
- при успехе опирайся на exit code и не печатай весь лог;
- при падении покажи хвост и targeted search по `FAILED`, `Exception`, `error`, имени задачи;
- удаляй только созданные тобой временные logs;
- не трактуй warnings как причину игнорировать non-zero exit code;
- не обновляй golden snapshots до того, как убедишься, что визуальная разница ожидаема.

Создай в `vibe-developer/scripts/` безопасный reusable runner для Gradle на Windows с параметрами project root, task list и log path. Не зашивай в него Blinkly.

### Итоговый отчёт оркестратора

Требуй:

- что реализовано;
- какие specialist skills были применены;
- какие spec requirement IDs закрыты;
- какие файлы/модули изменены;
- какие проверки прошли;
- какие проверки не удалось запустить и почему;
- известные риски и осознанные отклонения;
- предлагается ли reusable learning.

## Контракты specialist skills

### `vibe-project-architect`

Зона ответственности:

- Gradle modules, source sets и dependency direction;
- version catalogs и convention plugins;
- Android/iOS entry points;
- ручная DI и composition root;
- Detekt, Kover, build types, signing contract, CI и release workflows;
- CocoaPods/Xcode linkage и согласование native SDK versions;
- границы feature/domain/infrastructure/UI модулей;
- migration plan при изменении архитектуры.

Базовые правила:

- интерфейсы и domain model не должны зависеть от UI/infrastructure;
- platform implementations живут в platform source sets;
- dependencies собираются в composition root через interfaces, dependency interfaces, top-level factories и `by lazy`;
- не вводи DI-framework без явного требования;
- не передавай service dependencies в сериализуемые Decompose configs;
- screen-level Decompose component или cohesive flow по умолчанию получает отдельный component module с contract/Default/Preview/Store/Manager/mapper; группировку thin leaves документируй как exception;
- Paparazzi/ComposablePreviewScanner по умолчанию живут в Compose UI/resource-owning module; dedicated screenshot module разрешён только для aggregation или подтверждённой plugin/source-set incompatibility;
- версии извлекай из проекта; новые версии проверяй по официальным источникам;
- держи Android и iOS startup ordering явным;
- для native SDK проверяй Gradle artifact, Podfile, lockfile и Xcode linkage как один контракт;
- включай в архитектурный план quality gates, а не добавляй их после реализации.

Создай references как минимум для:

- `module-boundaries.md`;
- `manual-di.md`;
- `build-logic-and-quality.md`;
- `platform-entrypoints-and-release.md`.

### `vibe-domain-engineer`

Это отсутствовавшая в исходной схеме, но обязательная зона.

Зона ответственности:

- domain entities, value objects, sealed events/errors;
- business invariants и чистые алгоритмы;
- manager/watcher/provider contracts;
- time, timezone, scheduling и recurrence semantics;
- Result-based orchestration на границах;
- разделение calculation, side effects и presentation state;
- cross-feature output contracts.

Базовые правила:

- сначала оформляй vocabulary и invariants из AppSpec;
- держи чистые вычисления отдельно от Store/Component/platform APIs;
- зависимости выражай узкими интерфейсами;
- избегай Android/iOS типов в `commonMain`;
- время передавай через абстракции и тестируй в нескольких time zones;
- повторяющиеся правила выноси в manager/engine/provider;
- errors должны сохранять cause и давать presentation/root слою понятное действие;
- не прячь ошибки в пустых `.catch {}`.

Создай references:

- `domain-modeling.md`;
- `managers-events-errors.md`;
- `time-and-scheduling.md`.

### `vibe-decompose-engineer`

Основой служат официальные Decompose docs и Blinkly `.ai/skills/decompose`.

Зона ответственности:

- component contracts и default/preview implementations;
- parent-child hierarchy и root wiring;
- `ChildStack`, `ChildSlot`, `ChildPages`, `ChildPanels`, `ChildItems`;
- navigation configs, back handling, lifecycle, InstanceKeeper/StateKeeper;
- component outputs и root-level routing.

Базовые правила:

- публичный component contract представляет UI model и callbacks;
- default component делегирует `ComponentContext`;
- UI зависит от component, component не зависит от UI;
- config содержит только immutable serializable navigation arguments, но не dependencies;
- child dependencies передаются в child factory;
- navigation и root creation выполняются на main/UI thread;
- navigation properties создаются один раз, а не через computed getter;
- при click navigation предпочитай операции, устойчивые к double click;
- callback-only feature без UI-visible model остаётся thin component;
- каждый production `Value<Model>` получает retained Store; production component не мутирует `MutableValue<Model>` и не вызывает repository напрямую;
- mapper отделяет raw Store state от immutable component model и exposes `store.asValue().map(stateToModel)`;
- Store data access проходит через feature Manager;
- sibling `*ComponentPreview` может использовать static `MutableValue`, но не Store, `ComponentContext`, Manager или production services;
- labels подписывай до `store.init()`, если bootstrapper способен синхронно выдать startup label.

Создай references:

- `component-contract.md`;
- `navigation-and-root.md`;
- `lifecycle-state-retention.md`;
- `blinkly-adaptations.md`.

### `vibe-mvikotlin-engineer`

Основой служат официальные MVIKotlin docs, Blinkly `.ai/skills/mvikotlin` и `shared/utils` unwrap helpers.

Зона ответственности:

- решение, нужен ли Store;
- `Intent`, `Action`, `Msg`, `State`, `Label`;
- `StoreProvider`, coroutine `Executor`, pure `Reducer`;
- manager integration и mapping;
- startup initialization, labels, retention, logging;
- Store-level tests совместно с `vibe-test-engineer`.

Decision gate:

```text
Только stateless callback/output без UI-visible `Value<Model>`?
  -> Store не нужен.

Есть production `Value<Model>`, observable state, async work, bootstrap, flow subscription
или resume-aware behavior?
  -> retained MVIKotlin Store.

Store выполняет сложные расчёты или объединяет несколько domain sources?
  -> вынести manager/engine и оставить Store orchestration layer.
```

Базовые правила:

- Store остаётся module-internal implementation detail;
- Executor stateful и создаётся фабрикой;
- Reducer — pure object;
- main-thread contract MVIKotlin обязателен;
- `CoroutineExecutor.scope` отвечает за lifecycle async work;
- не создавай generic custom Success/Failure wrapper: используй standard Kotlin `Result<T>`;
- data/external calls Store выполняет только через feature Manager, который создаёт один flat `Result<T>` через `runCatching`;
- `Result` разворачивай централизованным helper, аналогичным Blinkly `unwrap`, с явными success/failure/cancellation branches и корректным nullable success;
- не копируй `unwrap` вслепую: адаптируй package, error policy и cancellation semantics;
- при startup labels используй `autoInit = false`, сначала undistpatched label collector, затем `init()`;
- retain Store через `instanceKeeper.getStore`;
- transient loading state при restoration не должен автоматически становиться persistent truth;
- logging StoreFactory разрешён для debug и не должен случайно попасть в production.

Создай references:

- `store-decision-and-shape.md`;
- `executor-reducer-result.md`;
- `initialization-retention-logging.md`;
- `blinkly-unwrap-pattern.md`.

### `vibe-platform-engineer`

Зона ответственности:

- `expect/actual` и platform factories;
- Android permissions, notification permission, exact alarm permission;
- iOS permissions и lifecycle bridging;
- notifications, alarms, background/resume behavior;
- screen-awake, beeper/haptics и platform services;
- manifests, Info.plist и platform capability configuration.

Базовые правила:

- commonMain определяет минимальный contract, platform source sets реализуют его;
- permission flow моделируй как state machine, включая denied/unavailable/pending;
- запрос permission не смешивай с проверкой;
- после возврата из Settings перепроверяй состояние на AppResumed;
- notification schedules отделяй от физических alarm instances;
- повторяющиеся расписания пересчитывай после reboot/timezone/app update, если платформа требует;
- lifecycle iOS связывай вручную или через актуальные Essenty helpers;
- platform failure преобразуй в domain error/output, не показывай UI прямо из platform service;
- добавляй fake implementations для common tests.

Создай references:

- `expect-actual-and-factories.md`;
- `permissions-lifecycle.md`;
- `notifications-alarms-background.md`;
- `platform-configuration.md`.

### `vibe-network-engineer`

Основой служит Tackle `shared/network`, но все решения сверяй с актуальной официальной Ktor документацией.

Зона ответственности:

- common API contracts;
- HttpClient ownership/configuration;
- platform engines;
- JSON serialization;
- request/response DTO и mappers;
- status/error handling;
- auth/OAuth/token refresh;
- multipart upload/download/progress;
- pagination, idempotency, retry/timeout;
- MockEngine/fixture/contract tests.

Базовые правила:

- domain API interface и models не зависят от Ktor DTO;
- API implementation и DTO остаются internal;
- HttpClient конфигурируется в одном composition point и имеет явного owner/close lifecycle;
- используй `ContentNegotiation` и явный `Json` contract;
- `ignoreUnknownKeys`, defaults и `@SerialName` выбирай осознанно по API compatibility;
- authentication оформляй отдельной policy или Ktor Auth plugin; не отправляй токен на чужой host;
- для 401 определи logout или refresh contract;
- не проглатывай `CancellationException`;
- различай transport, timeout, HTTP, serialization и domain errors;
- error body считывай безопасно один раз;
- retries разрешай только для безопасных/idempotent requests и с ограниченной policy;
- idempotency key должен быть стабильным идентификатором операции, а не `hashCode()` объекта;
- DTO mapping тестируй на реальных обезличенных fixture JSON;
- HTTP behavior тестируй через Ktor `MockEngine`;
- документационные ссылки на endpoint храни рядом с domain API contract.

Явно зафиксируй anti-patterns, которые нельзя копировать из Tackle:

- trailing whitespace в `@SerialName("error_description ")`;
- `hashCode()` модели как idempotency key;
- неявный lifecycle созданного внутри API `HttpClient`;
- обработка только части современных Ktor исключений;
- debug logger, безусловно включённый в production class.

Создай references:

- `client-configuration.md`;
- `contracts-dto-mappers.md`;
- `auth-errors-retries.md`;
- `upload-download-pagination.md`;
- `network-testing.md`;
- `tackle-patterns-and-hazards.md`.

### `vibe-persistence-engineer`

Объедини SQLDelight database и Multiplatform Settings в один persistence skill с явным внутренним routing.

Зона ответственности:

- domain persistence contracts;
- SQLDelight schema, queries, migrations и adapters;
- Android/iOS/test drivers;
- reactive queries и transaction boundaries;
- snapshot export/replace;
- typed Multiplatform Settings;
- defaults, structured values, legacy fallback и change tracking;
- persistence tests.

Routing:

```text
Табличные связанные данные, queries, migrations, reactive lists?
  -> SQLDelight path.

Небольшие пользовательские опции/метаданные/flags?
  -> Multiplatform Settings path.

Atomic cross-entity replacement?
  -> database transaction.

Сложный settings value?
  -> explicit JSON/string codec + fallback test.
```

Базовые правила:

- domain interface отделён от SQLDelight implementation;
- generated entities не выходят за infrastructure boundary;
- mappers и column adapters явны;
- связанные writes транзакционны;
- reactive query преобразуется в Flow и исполняется на injected dispatcher;
- test driver запускает ту же schema;
- timestamps, enums и collections имеют стабильное encoding;
- default values являются частью product contract;
- legacy parsing покрывается тестом;
- локальный change tracking отделён от sync metadata, чтобы remote apply не выглядел как user edit;
- migration никогда не заменяется destructive reset без явного разрешения.

Создай references:

- `sqldelight-schema-queries.md`;
- `drivers-adapters-transactions.md`;
- `reactive-and-snapshot-persistence.md`;
- `multiplatform-settings.md`;
- `persistence-testing.md`.

### `vibe-sync-engineer`

Это отдельная обязательная зона, вычлененная из Blinkly.

Зона ответственности:

- authentication state и user identity boundary;
- remote DTO/schema version;
- local/remote snapshot mapping;
- per-domain timestamps/change tracking;
- conflict resolution, merge и replace;
- dedupe/orphan filtering;
- sync state, retry и user-facing errors;
- platform Firebase/Firestore adapters или другой backend.

Базовые правила:

- sync manager зависит от domain persistence/settings/auth/remote interfaces;
- remote DTO version проверяется явно;
- несовместимая schema не применяется молча;
- remote payload использует переносимые примитивы и стабильные serializers;
- conflict resolution документируется как deterministic policy;
- timestamps сравниваются отдельно для независимых data domains;
- remote apply не должен повторно отметить все данные как локально изменённые;
- merge сохраняет referential integrity, удаляет дубликаты и фильтрует orphan rows;
- side effects после merge, например reschedule reminders, выполняются только после успешной transaction;
- sync state observable и содержит auth/sync/error/last success;
- offline, partial failure, repeated sync и concurrent edits покрыты тестами.

Создай references:

- `sync-contract-and-state.md`;
- `snapshot-schema-and-mappers.md`;
- `conflicts-merge-tracking.md`;
- `auth-and-remote-adapters.md`;
- `sync-testing.md`.

### `vibe-product-designer`

Зона ответственности:

- product UI/UX;
- screen flow и information hierarchy;
- design research через Lazyweb;
- Compose design system: color, typography, shapes, spacing, icons;
- light/dark/system theme;
- responsive/insets/accessibility/localization;
- screen/state implementation coordination;
- hand-off в `vibe-visual-testing`.

Не дублируй Compose API corpus. Для конкретных Compose API, state, effects, layouts, performance, navigation integration и platform interop используй установленный skill `compose-expert`/`compose-expert:compose-expert`.

### Обязательный Lazyweb routing

Перед проектированием, критикой или изменением product UI:

1. Проверь наличие `lazyweb_get_workflows`.
2. В первой Lazyweb-сессии вызови `lazyweb_get_workflows` с:
   - `operation = "list"`;
   - `task_context = "first run Lazyweb capabilities"`.
3. Для конкретного screen pattern сначала сделай один быстрый `lazyweb_search`.
4. Для полноценной работы используй текущий `lazyweb-design`:
   - `objective=create` для нового экрана;
   - `objective=improve` для качества существующего;
   - `objective=optimize` для conversion/metric existing screen.
5. Для существующего экрана передавай screenshot через upload flow, не inline base64.
6. Для design craft guidance используй `lazyweb-apply-design-best-practices`.
7. Для reviewable proposals используй `lazyweb-propose-ui-changes`.
8. Не используй retired workflow names вроде `lazyweb-design-research`, `deep-design-research`, `design-brainstorm` и `quick-references`, если live workflow guide не вернул их снова.

Если Lazyweb недоступен:

- сообщи об этом;
- продолжи только с официальными platform guidelines и уже сохранёнными проектными evidence;
- не выдавай собственный вкус за конкурентное исследование.

Базовые правила UI:

- каждый screen имеет loading/content/empty/error/offline/permission states, где применимо;
- все app-bundled пользовательские строки и локализуемые поля локальных catalog/database/seed/reference datasets хранятся только в Compose Multiplatform Resources locale-specific `strings.xml`; английский всегда default/base locale, русский — начальная дополнительная локаль, последующие locale resource sets используют те же ключи;
- активная локаль определяется только языком системы; не создавай in-app language picker, persisted locale preference, `selectedLocale` state или app-specific locale override;
- domain, Store/component state, persistence, sync и seed data содержат только language-neutral IDs/stable localization keys, никогда resolved translations, per-locale columns/maps или hardcoded product copy;
- когда Compose resources недоступны в native `actual`, Android/iOS implementation использует native localization resources со стабильными ключами и без translated literals в коде;
- component model остаётся UI-oriented и не раскрывает Store state;
- theme tokens централизованы;
- light/dark variants проверяются визуально;
- поддерживаются font scaling, touch targets, contrast, content descriptions и reduced motion;
- preview не должен требовать real network/database/platform services;
- golden screenshots — результат утверждённого design state, а не источник истины без spec;
- после design change вызывай visual-testing skill.

Создай references:

- `lazyweb-routing.md`;
- `design-system-and-theme.md`;
- `screen-states-responsive-accessibility.md`;
- `compose-expert-handoff.md`;
- `design-to-golden-loop.md`.

### `vibe-visual-testing`

Зона ответственности:

- preview components и deterministic fake data;
- `@Preview` coverage;
- ComposablePreviewScanner;
- host Paparazzi/ComposablePreviewScanner in the Compose UI/resource-owning module by default; require a documented aggregation or plugin/source-set constraint for a dedicated screenshot-test module;
- generated parameterized Paparazzi tests;
- stable screenshot IDs;
- record/verify workflow;
- golden review, failure diffs и CI artifacts.

Базовые правила:

- previews — часть test surface;
- сканируй только project package trees, не весь classpath;
- при необходимости включай private previews;
- cache scan result или preview list, чтобы не сканировать на каждый test;
- сгенерированный test source должен зависеть от compile step;
- custom generator допустим и предпочтителен для project-specific setup;
- применяй Android preview parameters к Paparazzi device/config;
- используй stable IDs, независимые от parameter order;
- кодируй unsafe filename characters;
- `record` изменяет goldens только после визуального просмотра;
- `verify` обязателен в CI;
- failures загружаются как artifacts;
- snapshots при большом объёме хранятся через Git LFS;
- platform/native views, которые Paparazzi не может отрисовать, получают preview-safe seam, но production behavior проверяется отдельно;
- учитывай, что Paparazzi намеренно не включает `LocalInspectionMode` глобально.

Ориентируйся на Blinkly custom `GenerateComposablePreviewPaparazziTestsTask` и `BlinklyPaparazzi`, но обобщи package names, theme, fonts, locales и devices.

Создай references:

- `preview-contract.md`;
- `scanner-and-test-generation.md`;
- `paparazzi-rule-and-identifiers.md`;
- `golden-review-and-ci.md`;
- `blinkly-visual-testing-adaptation.md`.

### `vibe-monetization-engineer`

Переименуй исходный `marketer` в более точный `monetization-engineer`.

Зона ответственности:

- product-safe ad placement;
- Lazyweb research по monetization UX;
- Yandex Mobile Ads Compose Multiplatform integration как приоритетный/default вариант;
- Android/iOS native setup;
- privacy/consent/age/location policies;
- ad lifecycle, loading/failure/visibility;
- adaptive inline/sticky, interstitial, rewarded и app-open decision;
- release validation и техническая аналитика без PII.

Базовые правила:

- placement сначала оценивается как product decision, затем как SDK task;
- используй Lazyweb и `vibe-product-designer` для точек показа;
- не перекрывай основной контент и системную навигацию;
- fullscreen ads показывай только в естественных паузах;
- rewarded ads всегда opt-in и дают обещанную награду ровно один раз;
- consent gate обязательно геозависимый: custom privacy-region endpoint определяет необходимость consent по IP сетевого выхода, а приложение хранит минимальный response и choice, привязанный к `policyVersion`;
- не показывай глобальный allow/deny popup всем пользователям: app-owned consent form появляется только при свежем `consentRequired=true` и содержит accept, decline и privacy-policy actions;
- не инициализируй Yandex SDK и не загружай рекламу после decline или пока endpoint/choice отсутствует, невалиден, просрочен либо unresolved; любой endpoint/transport error fail closed только для рекламы;
- не определяй регион через locale, SIM, time zone, device location или bundled country list; не сохраняй IP, country, GeoIP data, advertising ID или request identity;
- вызывай `YandexAds.setUserConsent(...)` перед каждой разрешённой инициализацией и отключай/defer automatic Yandex initialization, если она может обойти privacy gate;
- не называй custom endpoint IAB TCF CMP и используй этот lightweight flow только с Yandex Ads; партнер, требующий certified CMP/TCF, требует нового privacy inventory и явного product/legal approval;
- не предполагай consent, location tracking или age status;
- ad request по умолчанию содержит только необходимый ad unit ID;
- ad unit IDs приходят из build config/environment и отличаются по platform/build type;
- preview/test builds не делают real ad requests;
- ad load failure не ломает основной пользовательский сценарий;
- SDK version в Gradle и CocoaPods согласована;
- iOS static/dynamic framework restrictions проверяются по актуальной документации и Xcode linkage;
- Firebase и Yandex startup order проверяется явно;
- SKAdNetwork entries и release diagnostics являются частью приёмки;
- не включай ATT или персонализацию автоматически: это отдельное product/legal решение.

Создай references:

- `placement-and-format-decisions.md`;
- `yandex-kmp-integration.md`;
- `privacy-region-endpoint.md`;
- `privacy-and-request-policy.md`;
- `ios-cocoapods-xcode-preflight.md`;
- `ad-lifecycle-testing-release.md`.

### `vibe-test-engineer`

Расширь исходный `unit-tester`: он отвечает за весь non-visual test pyramid.

Зона ответственности:

- pure domain/manager tests;
- Store tests;
- Decompose component tests через публичный contract как основной способ покрытия поведения приложения;
- navigation/lifecycle/resume tests;
- persistence/network/sync tests;
- fakes/mocks/fixtures;
- coroutine virtual time;
- coverage quality gates.

Базовые правила:

- основной application-level coverage строится на Decompose component tests; pure/infrastructure/native contracts получают более узкие тесты там, где это точнее;
- если root component живёт в отдельном модуле, основной centralized component-test suite по умолчанию размещается в модуле `root`; другое размещение требует естественной module/dependency причины;
- component tests используют real `DefaultStoreFactory`, `DefaultComponentContext`, controlled `LifecycleRegistry` и injected test dispatchers;
- отключение MVIKotlin main-thread assertion допускается только в test setup и обязательно откатывается в teardown;
- lifecycle create/resume/pause/destroy воспроизводится явно;
- output/error assertions идут через публичный component contract;
- Store internals не тестируются из component test напрямую;
- virtual time покрывает delays/cooldowns/resume transitions;
- навигация проверяется по active `ChildStack` child и back dispatcher;
- failure path проверяет сохранение cause;
- fake settings/database/network должны быть детерминированы;
- JSON mappers проверяются fixture payload;
- SQLDelight tests используют test driver и реальную schema;
- sync tests охватывают conflict, dedupe, orphan, schema mismatch и remote-apply tracking;
- coverage — сигнал о пропусках, а не замена содержательным assertions;
- visual assertions принадлежат `vibe-visual-testing`.

Создай references:

- `test-pyramid-and-doubles.md`;
- `mvi-store-tests.md`;
- `decompose-component-test-harness.md`;
- `persistence-network-sync-tests.md`;
- `coverage-and-ci.md`.

## Канонические паттерны Blinkly, которые нужно обобщить

Используй Blinkly как основной implementation reference для следующих решений:

- shared Compose UI для Android/iOS;
- ручная DI через module interface, dependencies interface, top-level factory и `by lazy`;
- отдельный platform root factory;
- feature modules с component contract/default/preview, integration mapper, Store for every UI-visible production model, and manager-mediated data access;
- standard Kotlin `Result<T>` + Manager `runCatching` + cancellation-aware Executor `unwrap`, without custom generic Success/Failure wrappers or nested Results;
- thin components без Store для callback-only экранов;
- Store state -> mapper -> component model;
- retained Stores через InstanceKeeper;
- label collector до manual `store.init()` при startup events;
- central domain error/output model и root event routing;
- manager/engine для сложной логики;
- SQLDelight contract/implementation/adapters/transactions/reactive flows/test driver;
- Multiplatform Settings с typed contract, defaults, codecs и fallback;
- auth + Firestore sync со schema version, snapshot DTO, domain timestamps и merge;
- notifications/alarms с логическим schedule и физическими alarm instances;
- permission state machines и re-check на resume;
- theme, localization, ads host и privacy-first ad request;
- Compose-owned preview scanner -> generated Paparazzi parameterized tests -> CI verify;
- Detekt Compose/Decompose rules, Kover и CI quality gates;
- centralized component integration tests, предпочтительно в отдельном модуле root component.

Не делай Blinkly правилом там, где target AppSpec или актуальная документация требуют иного.

## Что считать неканоничным

Не переносить автоматически:

- текущие номера версий Blinkly/Tackle;
- имена модулей, packages и классов;
- exact thresholds без project decision;
- bundle/application IDs и ad unit IDs;
- Firebase/Yandex ordering без проверки target SDK versions;
- silent catch blocks;
- TODO-like exception swallowing;
- Tackle DTO typos и idempotency через `hashCode`;
- устаревшие Ktor engine/plugin APIs;
- exact test source-set/package names; при этом отдельный root component module остаётся предпочтительным местом для основного component-test suite, если dependency direction это допускает.

## Стандартизованный вход: Vibe AppSpec v1.3

Создай в `vibe-developer/assets/app-spec-template/` шаблон hand-off спецификации:

```text
app-spec/
  app-spec.json
  product.md
  domain.md
  data.md
  quality.md
  flows/
    FLOW-*.md
  screens/
    SCREEN-*.md
  assets/
    ...
```

Создай:

- `vibe-developer/assets/app-spec.schema.json`;
- `vibe-developer/references/app-spec-contract.md`;
- `vibe-developer/references/spec-kit-mapping.md`;
- `vibe-developer/scripts/validate-app-spec.py`.

Используй JSON, а не YAML, чтобы validation script работал на Python stdlib без дополнительной YAML dependency.

### `app-spec.json`

Обязательные поля:

```json
{
  "schemaVersion": "1.3",
  "app": {
    "name": "",
    "summary": "",
    "targets": ["android", "ios"],
    "locales": ["en", "ru"]
  },
  "requirements": [
    {
      "id": "REQ-001",
      "title": "",
      "priority": "must",
      "status": "approved",
      "acceptanceScenarioIds": ["AC-001"]
    }
  ],
  "flows": ["FLOW-001"],
  "screens": ["SCREEN-001"],
  "capabilities": {
    "network": false,
    "database": false,
    "settings": true,
    "sync": false,
    "authentication": false,
    "notifications": false,
    "exactAlarms": false,
    "ads": false
  },
  "constraints": {
    "offlineMode": "",
    "privacy": [],
    "accessibility": [],
    "performance": []
  },
  "localization": {
    "defaultLocale": "en",
    "localeSelection": "system-only",
    "resourceSystem": "compose-multiplatform-resources",
    "resourceFileFormat": "strings.xml",
    "keyStrategy": "shared-key-across-locales",
    "localDataTextStorage": "resource-keys-only",
    "nativeFallback": "platform-localized-resources",
    "hardcodedUserFacingStrings": false
  },
  "architecture": {
    "resultType": "kotlin-result",
    "componentModel": "immutable-value",
    "stateOwner": "mvikotlin-store",
    "stateMapping": "store-state-to-component-model",
    "storeDataAccess": "manager-result-unwrap",
    "managerResultCapture": "runCatching",
    "previewComponent": "separate-preview-implementation",
    "componentModuleStrategy": "screen-or-flow-boundary",
    "screenshotTestHost": "compose-ui-module",
    "screenshotTestHostRationale": "The Compose module owns previews, resources, generated Android tests, and snapshots."
  },
  "openQuestions": []
}
```

Разреши дополнительные поля для расширения, но отклоняй неизвестную major schema version.

### Markdown-части

`product.md`:

- problem, audience, goals, non-goals;
- user stories и success metrics;
- assumptions и product constraints.

`domain.md`:

- glossary;
- entities/value objects;
- invariants;
- time/scheduling rules;
- error semantics.

`data.md`:

- local tables/settings;
- bundled local catalogs/seed/reference data: stable item IDs, shared localization keys, Compose `strings.xml` owner и native fallback tables; никаких translated values в persistence/seed/code;
- remote APIs/auth;
- offline/cache;
- sync/conflict policy;
- privacy/retention.

`quality.md`:

- NFR;
- test matrix;
- accessibility/localization;
- completeness shared localization keys для всех `app.locales`, system-locale change/EN fallback/key-mapping/persistence round-trip tests, отсутствие language picker/persisted locale/app override и scan hardcoded user-visible strings;
- security/privacy;
- release acceptance.

Каждый `FLOW-*.md`:

- stable ID и цель;
- entry/exit conditions;
- ordered steps;
- branches;
- interrupted/resume behavior;
- Given/When/Then acceptance scenarios с stable IDs.

Каждый `SCREEN-*.md`:

- stable ID и linked flow/requirements;
- information hierarchy;
- states: loading/content/empty/error/offline/permission;
- actions and outputs;
- navigation;
- validation;
- responsive/insets;
- accessibility;
- localization;
- allowed ad slots;
- reference assets.

### AppSpec validation

Validator должен:

- работать read-only;
- проверять UTF-8 JSON и schemaVersion;
- проверять обязательные файлы;
- проверять уникальность IDs;
- проверять ссылки requirements -> acceptance scenarios -> flows/screens;
- проверять, что capability согласована с data/flow sections;
- для AppSpec 1.2+ проверять обязательный localization contract и соответствующие `data.md`/`quality.md` sections;
- для AppSpec 1.3+ проверять обязательный architecture contract для Kotlin Result, Store-backed component models, Manager/unwrap, Preview implementations, component module strategy и screenshot-test host;
- для AppSpec 1.3+ требовать `quality.md` section `## Architecture checks`;
- выдавать errors и warnings раздельно;
- не генерировать spec и не исправлять её молча.

Skill отвечает за чтение и validation hand-off, но не за продуктовое интервью и генерацию исходной спецификации.

### Связь со Spec Kit

Зафиксируй как рекомендуемый, но необязательный upstream workflow GitHub Spec Kit:

```text
constitution -> specify -> clarify -> plan -> checklist -> tasks -> analyze
  -> export/map into Vibe AppSpec v1
  -> separate implementation session with $vibe-developer
```

Причины рекомендации:

- Markdown artifacts;
- user stories и priorities;
- Given/When/Then acceptance;
- requirements и entities;
- success criteria;
- clarify/checklist/analyze quality gates;
- официальная поддержка Codex.

Не привязывай `vibe-*` к конкретным slash commands. Пользователь может подготовить AppSpec вручную или через другой процесс, включая OpenSpec. `spec-kit-mapping.md` должен описывать mapping, а не требовать установленный CLI.

## Самообучение без бесконтрольного дрейфа

Каждый specialist skill должен уметь распознать reusable learning, но не менять skill автоматически.

Считать паттерн кандидатом, если выполнено хотя бы одно:

- он повторился в двух независимых features;
- он решает стабильную cross-cutting проблему;
- он заменяет неоднозначное правило проверяемым контрактом;
- он подтверждён официальной документацией и target tests;
- пользователь явно назвал его новым архитектурным правилом.

Не считать кандидатом:

- одноразовый bug fix;
- workaround конкретной версии без срока/условия удаления;
- project-specific identifier;
- непроверенное предположение;
- стилистическое предпочтение без measurable benefit.

При обнаружении:

1. Кратко предложи пользователю сохранить паттерн.
2. Назови target skill/reference.
3. Приведи evidence: affected files/tests/docs.
4. Укажи scope, trade-offs и migration impact.
5. Ничего не меняй без явного согласия.
6. После согласия обнови минимальный reference-файл, validation example и knowledge index.

Создай:

- `vibe-developer/references/knowledge-index.md`;
- у каждого specialist — `references/learned-patterns.md`.

Формат записи:

```text
ID:
Status: accepted | deprecated
Date:
Scope:
Decision:
Evidence:
Consequences:
Validation:
Supersedes:
```

Не создавай отдельный changelog в каждом skill.

## Manifest, установка и синхронизация

### `vibe-skills-manifest.json`

Храни:

- package name;
- package version;
- schema version;
- exact список 13 skill directories;
- expected relative shared registry path;
- install mode defaults.

### `install-vibe-skills.ps1`

Сделай скрипт:

- с `CmdletBinding(SupportsShouldProcess)`;
- с параметрами `-Mode Junction|Copy`, `-Destination`, `-Force`, `-WhatIf`;
- default destination: `$env:CODEX_HOME\skills`, если `CODEX_HOME` задан, иначе пользовательский `.codex\skills`;
- default mode: `Junction`, чтобы source package был единственной редактируемой копией;
- работает только с exact каталогами из manifest;
- не затрагивает чужие skills;
- проверяет, что source и destination — абсолютные ожидаемые каталоги;
- перед заменой real directory сохраняет его в timestamped backup рядом;
- отличает directory, junction и symlink;
- не следует reparse point при recursive copy/delete;
- в Copy mode синхронизирует только listed skill directories;
- сначала вызывает package validation;
- после установки проверяет каждый global `SKILL.md`, `agents/openai.yaml` и sibling source-registry link;
- печатает подтверждённый результат и backup paths;
- при ошибке прекращает работу без частично объявленного успеха.

В `INSTALL.md` опиши:

```powershell
# Проверка
.\validate-vibe-skills.ps1

# Рекомендуемая установка единой рабочей копией
.\install-vibe-skills.ps1 -Mode Junction

# Копирование, если junction нежелателен
.\install-vibe-skills.ps1 -Mode Copy

# Просмотр изменений
.\install-vibe-skills.ps1 -Mode Copy -WhatIf

# Явная повторная синхронизация copy-mode
.\install-vibe-skills.ps1 -Mode Copy -Force
```

Укажи, что после первой установки или изменения metadata может потребоваться перезапуск Codex client.

## Валидация skills

Создай `validate-vibe-skills.ps1`, который:

1. Проверяет manifest и exact список directories.
2. Проверяет отсутствие незаполненных placeholders.
3. Проверяет frontmatter каждого `SKILL.md`.
4. Проверяет, что name совпадает с directory.
5. Проверяет наличие meaningful description.
6. Проверяет все relative file links.
7. Проверяет `agents/openai.yaml`.
8. Запускает официальный:

```powershell
python "C:\Users\Sergey\.codex\skills\.system\skill-creator\scripts\quick_validate.py" `
  "D:\Sources\vibe-skills\<skill-name>"
```

9. Запускает AppSpec validator на bundled valid fixture.
10. Убеждается, что bundled invalid fixtures отклоняются.
11. Проверяет installer в `-WhatIf`.
12. Возвращает non-zero exit code при любой ошибке.

На момент подготовки этого промпта `quick_validate.py` в системном Python завершался с `ModuleNotFoundError: yaml`. Не обходи официальный validator. Выполни preflight зависимости и, если `PyYAML` всё ещё отсутствует, запроси разрешение установить его в отдельное локальное virtual environment внутри package tooling или другим безопасным способом. Не устанавливай пакет глобально молча.

## Forward tests для routing

Для каждого skill создай 3–5 realistic prompts и проверь:

- positive direct trigger;
- positive orchestrated trigger;
- negative near-miss, который должен выбрать другой skill;
- overlap case и ожидаемый hand-off.

Храни компактную routing matrix в:

`vibe-developer/references/routing-matrix.md`

Примеры обязательных distinctions:

- stateless screen component -> Decompose, не MVIKotlin;
- сложный business calculation -> Domain, Store только orchestrates;
- SQLDelight table -> Persistence;
- REST API -> Network;
- Firestore snapshot conflicts -> Sync;
- permission/exact alarm -> Platform;
- Compose API/recomposition -> Compose Expert через Product Designer;
- UI evidence/design -> Product Designer + Lazyweb;
- screenshot goldens -> Visual Testing;
- ad placement -> Monetization + Product Designer;
- component behavior test -> Test Engineer;
- Gradle module/convention plugin -> Project Architect.

## Проверка полноты на эталонном сценарии

После создания skills проведи read-only desk simulation:

> Новое KMP-приложение Android+iOS получает AppSpec с onboarding, home tabs, REST API с OAuth, SQLDelight cache, settings, offline mode, Firestore-like sync, notifications и exact reminders, light/dark Compose UI, Yandex inline ads, EN/RU, component tests и Paparazzi goldens.

Покажи, что routing покрывает:

- project scaffold и modules;
- domain;
- network/auth;
- database/settings;
- sync/conflicts;
- platform permissions/reminders;
- Decompose navigation;
- MVIKotlin stores/managers;
- UI research/design/Compose;
- monetization/privacy;
- tests;
- previews/goldens;
- CI/release.

Если ответственность потеряна или дублируется без явного owner, исправь skill boundaries до установки.

## Обязательные первичные источники

Разложи ссылки по relevant reference-файлам. Не копируй страницы целиком; сохрани durable rules и ссылки.

### MVIKotlin

- https://arkivanov.github.io/MVIKotlin/
- https://arkivanov.github.io/MVIKotlin/store/
- https://arkivanov.github.io/MVIKotlin/view/
- https://arkivanov.github.io/MVIKotlin/binding_and_lifecycle/
- https://arkivanov.github.io/MVIKotlin/state_preservation/
- https://arkivanov.github.io/MVIKotlin/logging/

Особенно зафиксируй:

- unidirectional flow;
- Store as single source of truth;
- main-thread contract;
- Bootstrapper/Executor/Reducer;
- labels as uncached events;
- manual initialization for startup labels;
- state preservation vs whole Store retention;
- debug-only nature logging.

### Decompose

- https://arkivanov.github.io/Decompose/
- https://arkivanov.github.io/Decompose/component/overview/
- https://arkivanov.github.io/Decompose/navigation/overview/
- https://arkivanov.github.io/Decompose/extensions/overview/
- https://arkivanov.github.io/Decompose/tips-tricks/overview/
- https://arkivanov.github.io/Decompose/faq/

Особенно зафиксируй:

- UI-independent lifecycle-aware components;
- strict parent-child context hierarchy;
- root/main-thread creation;
- configs as immutable serializable arguments, not dependencies;
- StateKeeper/InstanceKeeper/back handling;
- duplicate config/double-click hazards;
- manual lifecycle control on non-Android platforms.

### Paparazzi и ComposablePreviewScanner

- https://github.com/cashapp/paparazzi
- https://cashapp.github.io/paparazzi/
- https://github.com/sergio-sastre/ComposablePreviewScanner#paparazzi
- https://github.com/sergio-sastre/ComposablePreviewScanner/blob/master/paparazzi-plugin/README.md

Особенно зафиксируй:

- record/verify/report/failure directories;
- Git LFS;
- package-scoped preview scanning;
- private previews и source-set compilation;
- stable screenshot IDs;
- custom generator допустим, потому что showcase plugin не обещает project-specific support.

### Yandex Mobile Ads Compose Multiplatform

- https://ads.yandex.com/helpcenter/ru/dev/compose-multiplatform
- https://ads.yandex.com/helpcenter/ru/dev/compose-multiplatform/quick-start
- при проблемах русской страницы используй официальный английский эквивалент:
  https://ads.yandex.com/helpcenter/en/dev/compose-multiplatform/quick-start
- https://github.com/yandexmobile/yandex-ads-multiplatform
- локальная инструкция:
  `D:\Sources\Android\Blinkly\docs\yandex-inline-ads-macos-guide.md`

Сверяй текущие требования. В июле 2026 official quick start уже отличался от Blinkly snapshot по версии SDK и части platform requirements. Не фиксируй конкретную версию в skill.

### SQLDelight/KMP

- https://kotlinlang.org/docs/multiplatform/multiplatform-ktor-sqldelight.html
- при реализации migrations/adapters/flows добавляй ссылки на актуальные официальные SQLDelight docs.

### Ktor

- https://ktor.io/docs/client-create-multiplatform-application.html
- https://ktor.io/docs/client-serialization.html
- https://ktor.io/docs/client-response-validation.html
- https://ktor.io/docs/client-bearer-auth.html
- https://ktor.io/docs/client-testing.html

### Spec hand-off

- https://github.github.com/spec-kit/
- https://github.github.com/spec-kit/reference/agentic-sdd.html
- https://github.com/github/spec-kit/blob/main/templates/spec-template.md
- https://github.com/github/spec-kit/blob/main/templates/plan-template.md
- альтернативный, но необязательный вариант:
  https://github.com/Fission-AI/OpenSpec

### Локальные implementation sources

Через source registry укажи relevant directories/files, а не сотни отдельных absolute paths:

- Blinkly root build logic, version catalog, convention plugins и CI;
- Blinkly `shared/component`, `shared/domain`, `shared/database`, `shared/settings`;
- Blinkly `shared/alarm`, `shared/notifier`, `shared/compose`;
- Blinkly `shared/component/sync`;
- Blinkly root common component tests;
- Tackle `shared/network`;
- Tackle domain API contracts и exception model;
- Tackle JSON mapper fixtures/tests.

## Требования к качеству созданного содержимого

- Каждое правило либо связано с официальным источником, либо явно помечено как Blinkly/Tackle adaptation.
- Каждый specialist имеет owner boundary и hand-off rules.
- Ни один specialist не дублирует `vibe-developer` orchestration.
- `vibe-product-designer` не дублирует `compose-expert`.
- `vibe-visual-testing` не принимает product design decisions.
- `vibe-test-engineer` не обновляет goldens.
- `vibe-monetization-engineer` не включает tracking/consent без product/legal input.
- `vibe-network-engineer` и `vibe-sync-engineer` разделены: transport/API против snapshot/auth/conflict coordination.
- `vibe-domain-engineer` и `vibe-mvikotlin-engineer` разделены: business rules против state-machine orchestration.
- `vibe-persistence-engineer` явно маршрутизирует SQLDelight и settings.
- Все scripts используют UTF-8 и безопасные literal paths в PowerShell.
- Все destructive filesystem operations ограничены exact manifest targets и имеют `ShouldProcess`/backup.
- Проверки не объявляются успешными без exit code evidence.

## Финальный результат сессии

Выполни работу полностью:

1. Покажи короткий план.
2. Создай все 13 skills через `init_skill.py`.
3. Заполни SKILL/reference/script/asset files.
4. Сгенерируй `agents/openai.yaml`.
5. Создай AppSpec template/schema/validator.
6. Создай manifest, validator, installer и `INSTALL.md`.
7. Проведи forward routing tests и desk simulation.
8. Запусти official validation для каждого skill.
9. Исправь все ошибки.
10. Установи или синхронизируй skills глобально в Junction mode, если пользователь не потребовал Copy mode.
11. Выполни post-install validation.
12. В финале сообщи:
    - созданные skills;
    - ключевые изменения исходной схемы;
    - local и global paths;
    - install mode;
    - результаты validation;
    - как передавать AppSpec;
    - известные ограничения;
    - какие reusable patterns были зафиксированы.

Не останавливайся на описании того, что следовало бы создать. Итогом следующей сессии должны быть реально созданные, проверенные и установленные skills.
