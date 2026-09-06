# Vibe Development Workflow 2.0

Нормативные источники после начала реализации — утверждённый AppSpec 2.0, репозиторий и каталог .vibe. Память разговора и текстовые отчёты специалистов состоянием delivery не являются.

## Сквозной процесс

    approved AppSpec 2.0
      -> strict validation and canonical inventory
      -> ledger initialization and pre-edit checkpoint
      -> dependency-ordered vertical AC slices
      -> immutable specialist hand-offs
      -> targeted receipts
      -> immutable audit request and fresh-context audit
      -> one covering final receipt
      -> aggregate validator and two verdicts

Protocol 1.x несовместим. Инструменты отвечают unsupported protocol и не мигрируют, не удаляют и не переинициализируют старые artifacts.

## Начало и восстановление turn

Если ledger отсутствует, проверьте AppSpec и инициализируйте его:

    python <skills>\vibe-developer\scripts\validate-app-spec.py --require-current <app-spec>
    python <skills>\vibe-developer\scripts\init-delivery-ledger.py <app-spec> --project-root <repo>

Если ledger существует, первым действием каждого turn запускайте:

    python <skills>\vibe-developer\scripts\resume-delivery.py <repo>

Resume заново обнаруживает AGENTS.md, валидирует AppSpec, canonical inventory, ledger digest, fingerprints, dependencies и pending hand-offs. clean разрешает продолжение; expected-drift требует инспекции активного slice; unexpected-drift запрещает новые правки до явного reconciliation; stale-evidence требует повторных checks и audit.

## Checkpoints и slices

Перед первой правкой AC укажите owner и непересекающиеся file boundaries через checkpoint-delivery.py. Checkpoint также обязателен перед расширением границ, после specialist hand-off, до и после долгой проверки и перед завершением turn. Каждая атомарная команда принимает предыдущий ledgerDigest.

AC выполняются в порядке dependsOnAcceptanceScenarioIds. Статус in-progress хранит owner, boundaries, baseline/checkpoint fingerprints, dependencies, changed files, pending checks, hand-off refs, blockers и timestamps. blocked-external допустим только для platform, external и release gates.

Specialist пишет один immutable .vibe/handoffs/<id>.json по [контракту](../vibe-developer/references/specialist-handoff-contract.md). Orchestrator проверяет diff и границы, затем импортирует SHA-256 через ingest-handoff.py. Conversation summary не заменяет hand-off.

## Receipts и audit

Receipts существуют только как JSON-файлы под .vibe/receipts. Они содержат kind targeted или final, exact argv/tasks, covered obligation/surface pairs, timestamps, текущий fingerprint, exit code и hash лога. Для каждой пары учитывается последний receipt на текущем fingerprint: PASS→FAIL не закрывает пару, FAIL→PASS закрывает только новым успехом.

После закрытия local obligations orchestrator создаёт immutable .vibe/audits/<request-id>/request.json и запускает vibe-acceptance-auditor в указанном fresh context. Audit обязан ссылаться на exact request hash, иметь implementationContextAvailable false, самостоятельно построить canonical shadow inventory и доказать каждую declared surface audit-time check.

После audit PASS выполняется один final receipt, покрывающий все verified obligation/surface pairs. Затем генерируются оба Markdown report и запускается один validate-delivery-ledger.py. Он сам проверяет AppSpec, inventory, receipt ordering, audit и report parity и всегда печатает:

- implementation-complete;
- release-ready.

Первый verdict допускает незакрытые внешние platform/external/release gates; второй — нет. Waiver действителен только со ссылкой на существующее долговечное решение.

Подробный протокол восстановления после compaction, durable decisions, specialist checkpoints, согласования принятой редакции AppSpec и повторных аудитов: [recovery-contract.md](../vibe-developer/references/recovery-contract.md). Waived/blocked gates требуют реальных решений или блокеров, а не фиктивных успешных команд.

## Создание и поставка ассетов

Product Designer фиксирует все нужные иконки, лого и иллюстрации в `assetRequirements`, связывая их с экранами/AC и описаниями design.md. Assets Creator создаёт XML-векторы или генерирует растровые изображения по утверждённому brief. Compose Expert подключает их только через Compose Multiplatform Resources, Architect обеспечивает resource wiring, Visual Testing проверяет реальные экраны.

Растровые иконки по умолчанию: прозрачный PNG 128×128; 64×64 допускается при достаточном разрешении для заявленных dp и плотности. Простые иконки предпочтительно хранить в XML-векторах. Результаты, происхождение и use sites фиксируются в `docs/assets/asset-manifest.json`; полнота проверяется отдельным repository gate до аудита. [Полный контракт](../vibe-assets-creator/references/asset-contract.md).
