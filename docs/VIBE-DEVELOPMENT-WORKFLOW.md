# Vibe Development Workflow 2.0

Нормативные источники после начала реализации — утверждённый AppSpec 2.0, репозиторий и каталог .vibe. Память разговора и текстовые отчёты специалистов состоянием delivery не являются.

## Сквозной процесс

    approved AppSpec 2.0
      -> strict validation and canonical inventory
      -> ledger initialization and pre-edit checkpoint
      -> capability packages with early production integration
      -> compile/targeted feedback before final hand-offs
      -> assignment-local immutable hand-offs and scoped receipts
      -> immutable audit request and fresh-context audit
      -> closure manifest (no repeated matrix)
      -> aggregate validator and local/implementation/release verdicts

Protocol 1.x несовместим. Инструменты отвечают unsupported protocol и не мигрируют, не удаляют и не переинициализируют старые artifacts.

## Начало и восстановление turn

Если ledger отсутствует, проверьте AppSpec и инициализируйте его:

    python <skills>\vibe-developer\scripts\validate-app-spec.py --require-current <app-spec>
    python <skills>\vibe-developer\scripts\init-delivery-ledger.py <app-spec> --project-root <repo>

Если ledger существует, первым действием каждого turn запускайте:

    python <skills>\vibe-developer\scripts\resume-delivery.py <repo> --compact

Resume заново обнаруживает AGENTS.md, валидирует AppSpec, canonical inventory, ledger digest, fingerprints, dependencies, сохранённый запрос, обязательные чтения и pending hand-offs. Продолжение определяется `safeToContinue` и указанным next action, а не одним `clean`; expected-drift требует инспекции активного slice; unexpected-drift запрещает новые правки до явного reconciliation; stale-evidence требует повторных checks и audit.

## Checkpoints и slices

Перед реализацией сохраните фактический запрос пользователя и ограничения в файле репозитория. В первом checkpoint передайте `--request-file docs/assignments/REQUEST.md`, owner и непересекающиеся file boundaries. Нормативная проза AppSpec и активные FLOW/SCREEN входят в обязательные чтения автоматически; контракты специалистов добавляются через `--required-read`. Запрос и чтения проверяются по хешам. Checkpoint также обязателен перед расширением границ, после specialist hand-off, до и после долгой проверки и перед завершением turn. Каждая атомарная команда принимает предыдущий ledgerDigest.

Единица выполнения — пакет связанных пользовательских возможностей; отдельные AC остаются единицами приёмки. Например, create/read/update одного редактора выполняются совместно, с соблюдением внутренних зависимостей. В первом пакете подключается настоящий production root и проверяемый save/read/restart flow. Далее каждый пакет подключается к root. Количество verified AC и количество интегрированных флоу показываются отдельно; они не означают процент готовности приложения. AC выполняются в порядке dependsOnAcceptanceScenarioIds. Статус in-progress хранит owner, boundaries, baseline/checkpoint fingerprints, dependencies, changed files, pending checks, hand-off refs, blockers и timestamps. blocked-external допустим только для platform, external и release gates.

Для новых заданий используйте [flow-delivery-contract.md](../vibe-developer/references/flow-delivery-contract.md) и JSON-команды `delivery-work.py`: package → scope → assign → check → handoff → ingest → integrate. Компиляция/целевые тесты запрашиваются до final handoff; runner остаётся сериализованным. Границы и baseline относятся к assignment, а не ко всему накопленному drift AC. Specialist пишет один immutable .vibe/handoffs/<id>.json по [контракту](../vibe-developer/references/specialist-handoff-contract.md). Orchestrator проверяет diff и границы, затем импортирует SHA-256 через ingest-handoff.py. Conversation summary не заменяет hand-off.

Промежуточные checkpoints специалиста наследуют незавершённые проверки, блокеры и required reads. Снятие пункта требует явного `--resolve-pending-check` или `--resolve-blocker` с `--resolution-reason`. Возвращённое задание нельзя продолжить: для новой работы нужен новый assignment ID. Любой непринятый hand-off блокирует итоговую готовность, в том числе если он появился после audit PASS.

## Receipts и audit

Receipts существуют только как JSON-файлы под .vibe/receipts. Они содержат kind targeted или final, exact argv/tasks, covered obligation/surface pairs, timestamps, текущий fingerprint, exit code и hash лога. Во время реализации targeted receipt может использовать зарегистрированный scope всех входов и транзитивных зависимостей: нерелевантные изменения его не устаревают. Build/spec/instruction inputs добавляются автоматически; при неопределённых зависимостях применяется глобальная проверка. Финальные проверки и аудит остаются глобальными. Для каждой пары учитывается последний актуальный receipt: PASS→FAIL не закрывает пару, FAIL→PASS закрывает только новым успехом.

После закрытия local obligations orchestrator создаёт immutable .vibe/audits/<request-id>/request.json и запускает vibe-acceptance-auditor в указанном fresh context. Audit обязан ссылаться на exact request hash, иметь implementationContextAvailable false, самостоятельно построить canonical shadow inventory и доказать каждую доступную declared surface независимо проверенным integration receipt.

Каждый проверенный check связывается с global `kind: integration` runner receipt через `receiptRef` и `receiptSha256`: валидатор сверяет команду, результат, время, fingerprints, полное покрытие и хеш лога. Audit checks без этой связи и ledger без сохранённого запроса не поддерживаются. Исторические артефакты нельзя преобразовывать или выдавать за актуальные доказательства.

После audit PASS операция close связывает аудит и проверенные integration receipts в closureManifest; повтор полной матрицы не выполняется. Затем генерируются оба Markdown report и запускается один validate-delivery-ledger.py. Он сам проверяет AppSpec, inventory, receipt ordering, audit и report parity и всегда печатает:

- locally-verified;
- implementation-complete;
- release-ready.

Первый verdict допускает незакрытые внешние platform/external/release gates; второй — нет. Waiver действителен только со ссылкой на существующее долговечное решение.

Подробный протокол восстановления после compaction, durable decisions, specialist checkpoints, согласования принятой редакции AppSpec и повторных аудитов: [recovery-contract.md](../vibe-developer/references/recovery-contract.md). Waived/blocked gates требуют реальных решений или блокеров, а не фиктивных успешных команд.

## Создание и поставка ассетов

Product Designer фиксирует все нужные иконки, лого и иллюстрации в `assetRequirements`, связывая их с экранами/AC и описаниями design.md. Assets Creator создаёт XML-векторы или генерирует растровые изображения по утверждённому brief. Compose Expert подключает их только через Compose Multiplatform Resources, Architect обеспечивает resource wiring, Visual Testing проверяет реальные экраны.

Растровые иконки по умолчанию: прозрачный PNG 128×128; 64×64 допускается при достаточном разрешении для заявленных dp и плотности. Простые иконки предпочтительно хранить в XML-векторах. Результаты, происхождение и use sites фиксируются в `docs/assets/asset-manifest.json`; полнота проверяется отдельным repository gate до аудита. [Полный контракт](../vibe-assets-creator/references/asset-contract.md).

## Частота визуальных проверок

Preview compile выполняется во время UI-правок; scanner/Paparazzi проверяется небольшим production smoke-preview в начале. Record/inspect/verify выполняется на стабильном экране или capability, затем только для затронутых снимков. Основные состояния light/dark сохраняются; дополнительные stress-варианты выбираются по риску/pairwise. Ожидающий golden-test AC остаётся implemented-unverified.

Lazyweb research выполняется до дизайна. Полный последовательный review проводится по стабильным экранам один раз; повторяются существенно изменённые экраны и незакрытые findings. По-прежнему только один report в работе. В ожидании можно выполнять независимую работу.

## Current evidence contract

AppSpec 2.0 requires assetRequirements; no legacy-spec compatibility is supported. Specialist handoffs use only registered assignment-local baselines/results. Targeted receipts require inputScopeId and start/end input fingerprints; uncertain dependencies require a conservatively registered whole-repository scope. Global integration and audit checks use kind integration; closure binds a manifest without a post-audit run. Unsupported artifacts are rejected, never converted or relabeled. See [flow delivery contract](../vibe-developer/references/flow-delivery-contract.md).

Недоступные на хосте surfaces фиксируются при intake. Независимый аудит доступной части может подтвердить locallyVerified, сохранив implementationComplete=false до проверки всех AC. Конкурентные пакеты, compact assignment packets, evidence IDs, retry-bind и техническая reconciliation описаны в flow delivery contract.
