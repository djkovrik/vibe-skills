# Vibe development workflow

Этот документ описывает пользовательский путь от продуктовой идеи до проверенной реализации. Нормативные технические правила находятся в самих `vibe-*` skills и их contracts; этот workflow определяет порядок и условия перехода между этапами.

## Источники правды

При конфликте применяйте порядок:

1. явные решения пользователя и утверждённый AppSpec;
2. инструкции, код, тесты и build logic целевого репозитория;
3. актуальная официальная документация;
4. принятые reusable patterns пакета;
5. помеченные Blinkly/Tackle adaptations;
6. общие инженерные эвристики.

После начала реализации текущими источниками состояния являются AppSpec и `.vibe/delivery-ledger.json`, а не память разговора или итог специалиста.

## Сквозной процесс

```text
discovery
  -> approved Vibe AppSpec 1.4
  -> validate --require-current
  -> delivery ledger initialization
  -> independent inventory check
  -> architecture scaffolding
  -> vertical acceptance-scenario slices
  -> fresh-context closure audit
  -> full quality/platform/release gates
  -> final ledger validation
```

## 1. Подготовить и утвердить AppSpec 1.4

Продуктовое интервью проходит до `$vibe-developer`. Используйте [актуальный шаблон](../vibe-developer/assets/app-spec-template/app-spec) и [контракт](../vibe-developer/references/app-spec-contract.md). Не переносите нерешённые продуктовые вопросы в реализацию.

`app-spec.json` содержит:

- requirements и отдельную запись `acceptanceScenarios[]` для каждого наблюдаемого outcome;
- `managedEntities[]` с явным решением для каждой CRUD-операции и дополнительных операций;
- `qualityGates[]` со стабильными ID, category/platform, способом проверки и источником контракта;
- flows, screens, capabilities, localization, architecture, UI quality и open questions.

Подробные Given/When/Then остаются в `flows/FLOW-*.md`. Каждый AC имеет собственную секцию и описывает один основной action/state/failure и один наблюдаемый outcome. JSON-ссылка AC на requirement, flow и screens должна совпадать с prose.

Проверка полного цикла:

```powershell
python <vibe-skills>\vibe-developer\scripts\validate-app-spec.py <project>\app-spec --require-current
```

Валидатор проверяет равенство множеств AC в requirements и inventory, собственный Given/When/Then каждого AC, ссылки на flows/screens, все CRUD-ячейки managed entities и обязательные/условные quality gates.

### Legacy AppSpec 1.0–1.3

Legacy specification по-прежнему валидируется с предупреждением без `--require-current`, поэтому узкий specialist может безопасно выполнить локальную задачу. Полный или cross-cutting `$vibe-developer`-цикл legacy не запускает.

Миграция всегда пишет в новый каталог и не перезаписывает исходник:

```powershell
python <vibe-skills>\vibe-developer\scripts\migrate-app-spec.py <legacy-app-spec> <new-review-directory>
```

Перенесённый 1.3-контент сохраняется, но автоматически извлечённые сценарии отмечаются `needs-review`, а неоднозначности становятся blocking questions. Разработка начинается только после ручной проверки, явного approval и успешного `--require-current`.

## 2. Инициализировать delivery ledger

До первой production-правки `$vibe-developer` создаёт:

```powershell
python <vibe-skills>\vibe-developer\scripts\init-delivery-ledger.py <app-spec-directory> --project-root <project-root>
```

Tracked artifacts:

- `.vibe/delivery-ledger.json` — единственный редактируемый источник delivery state;
- `docs/requirement-traceability.generated.md` — детерминированное представление ledger;
- `.vibe/closure-audit.json` и `docs/closure-audit.generated.md` — последний независимый аудит.

Ledger хранит fingerprints всех нормативных AppSpec JSON/Markdown, Git HEAD, binary diff hash и hashes неигнорируемых untracked-файлов. Отдельные AC/gate entries имеют статусы `not-started`, `implemented-unverified`, `verified`, `blocked-external`, `waived`, production/test evidence и verification receipts.

Waiver допустим только со ссылкой на явно зафиксированное решение пользователя. `blocked-external` не заменяет незавершённый repository contract.

Подробности и команды находятся в [delivery-ledger-contract.md](../vibe-developer/references/delivery-ledger-contract.md).

## 3. Проверить inventory до реализации

Оркестратор независимо сопоставляет:

- requirement ↔ AC ↔ flow/screen prose;
- managed entity ↔ create/read/update/delete/additional operations ↔ AC;
- required/conditional gate ↔ verification method ↔ platform/category.

Противоречия и пробелы блокируют coding. Ledger не считается доказательством корректности AppSpec.

## 4. Реализовать вертикальными slices

После минимального architecture scaffolding планируйте работу по AC. Каждый slice проходит полностью:

```text
public production contract
  -> data/domain behavior
  -> Store/component state
  -> UI/platform wiring
  -> required tests
  -> targeted verification receipt
  -> ledger evidence
```

Specialist получает AC/gate IDs и допустимые file boundaries. Он возвращает evidence package: production path/symbol/surface, test path/exact name/surface, нужные команды, выполненные non-Gradle checks и blockers. Specialist не пишет ledger и не заявляет completion.

Параллелить можно только slices без общих файлов и контрактов. Только `$vibe-developer` владеет ledger и запускает Gradle. `run-gradle.ps1` сериализует процессы по canonical project path, ограничивает ожидание/выполнение и записывает receipt с реальным exit code только после завершения команды.

После milestone оркестратор перечитывает AppSpec и ledger. Незакрытый AC/gate остаётся отдельной записью; формулировки `implemented baseline`, `mostly complete` или общий `partial` не заменяют item-level состояние.

## 5. Выполнить fresh closure audit

После закрытия всех локальных entries implementers останавливаются. Новый `$vibe-acceptance-auditor` запускается в изолированном контексте без implementation history. Он:

- самостоятельно строит shadow inventory из JSON и flow/screen prose;
- не доверяет ledger или implementer report;
- проходит каждый contract через public API, data/state, UI/platform wiring и требуемые тестовые surfaces;
- не меняет AppSpec, production code, tests или ledger;
- пишет только closure audit artifacts и выдаёт `PASS`, `GAPS` или `BLOCKED`.

При `GAPS` оркестратор назначает исправления и после свежих evidence запускает другого чистого auditor. Любое изменение AppSpec/workspace делает прежний `PASS` недействительным.

Если isolated sub-agent недоступен, `$vibe-developer` не объявляет completion. Пользователь запускает отдельную чистую сессию `$vibe-acceptance-auditor`, затем возвращает свежие audit artifacts.

## 6. Финальные gates и verdicts

После audit `PASS` оркестратор выполняет единый полный Gradle/quality/release gate, обновляет receipts, проверяет generated-report drift и запускает финальную ledger validation.

- `implementation-complete`: все обязательные AC и repository gates `verified` или явно `waived`, fingerprints актуальны, audit свежий и имеет `PASS`.
- `release-ready`: дополнительно закрыты platform, external и release gates; `blocked-external` не допускается.

Committed CI/release automation и реально настроенные GitHub/Firebase/Google Play/Google Cloud prerequisites сообщаются отдельно. Отсутствующие credentials могут сохранить `implementation-complete`, но не `release-ready`, если соответствующие gates не waived явным решением.

## Пример запуска

```text
Используй $vibe-developer. Реализуй приложение по утверждённой спецификации
<target-repository>/app-spec в <target-repository>.
Требуй AppSpec 1.4, создай delivery ledger до первой правки, реализуй вертикальными
AC-slices и не объявляй completion без fresh $vibe-acceptance-auditor PASS и финальной
ledger validation. Не меняй утверждённые product decisions молча.
```

Для одного SQLDelight query, Store transition, preview fix или другой узкой задачи вызывайте owning specialist напрямую; полный workflow не нужен и legacy 1.3 сам по себе такую работу не блокирует.

## Spec Kit и OpenSpec

Их можно использовать как необязательный discovery/planning слой:

```text
constitution -> specify -> clarify -> plan -> checklist -> tasks -> analyze
-> conversion to approved Vibe AppSpec 1.4 -> validation -> $vibe-developer
```

Они не заменяют AppSpec, ledger или независимый closure audit.
