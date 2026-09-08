# Изменения цикла Vibe после BagCue

Новый цикл: intake → foundation smoke → параллельные capabilities → readiness → freeze → integration checks → независимый аудит → closure.

## Выполнение и восстановление

`delivery-work.py` сохраняет стадии проверки в `.vibe/jobs`. Receipt публикуется до регистрации в ledger. `retry-bind` повторяет только регистрацию; административный timeout по умолчанию — 30 секунд. Bind идемпотентен по пути и хешу и не обновляет checkpoint исходников. Реальный exit code проверки отделён от результата binding.

Gradle сохраняет потоковый лог, сообщает об отсутствии нового вывода и ограничивает завершение процесса/чтение вывода после timeout. Integration по умолчанию использует одного worker и `--no-parallel`; один mutex сохраняет единственного владельца Gradle на workspace.

`ValidationContext` индексирует последние receipts по obligation/surface и рассчитывает каждый уникальный scope один раз за вызов. Resume не запускает acceptance-validator. Readiness сначала обнаруживает дешёвые blockers. Подготовка audit request и closure manifest вынесена из ledger lock; перед записью состояние перепроверяется.

## Evidence и координация

Текущий evidence хранится в реестре по ID с точным coverage; ledger содержит ссылки. Handoffs остаются неизменяемой историей. `reconcile-evidence` заменяет принятые anchors с причиной и inspection note; потерянное покрытие переоткрывает verification. XML anchors используют элемент и namespace-aware атрибуты. Checks и blockers разрешаются по конкретным IDs.

Несколько независимых пакетов могут быть активны одновременно. Пересекающиеся writers запрещены. `contract-ready` позволяет потребителю начать работу после принятия контракта и актуальных поведенческих проверок, не ожидая отложенных goldens. Assignment packet содержит границы записи, входы, критерии возврата и команды; для нового независимого агента применяется `fork_turns: none`.

Scope можно построить из `modules` и проверенного `moduleGraph`: resolver обходит транзитивные зависимости и отклоняет неизвестные модули. Граф предоставляет архитектор после чтения реальной Gradle-конфигурации. Whole-repository fallback требует причины. `check-batch` объединяет совместимые готовые запросы и сохраняет исходные команды и coverage.

## Приёмка

Одна integration-матрица предшествует независимому аудиту. Аудитор проверяет актуальность и содержательность receipts, переиспользует доказанные результаты и запускает недостающие проверки. Closure manifest связывает аудит и receipts; обязательного повторного прогона после аудита нет. HEAD хранится как происхождение, а идентичность проверки определяется содержимым.

Host matrix автоматически выявляет недоступные iOS surfaces вне macOS; остальные SDK/credentials проверяются и документируются на intake. `locallyVerified` не заменяет `implementationComplete` и `releaseReady`.

Foundation требует настоящий render-smoke с ненулевым scanner, PNG и production resources, включая light/dark и RU/200%. Detekt/Kover подключаются рано. Требования к состояниям UI, privacy, lifecycle, пользовательским сценариям и Lazyweb review сохранены.

Asset contract и AppSpec template используют `shared/compose`. Узкая техническая path-reconciliation сохраняет неизменившееся evidence и переоткрывает asset checks; изменение нормативного смысла остаётся консервативным. Завершённый BagCue не изменялся. Миграции старого delivery-протокола не добавлены.

## Проверка и дальнейшие измерения

Регрессии включают сбой bind, 150 obligations/500 реальных receipt-файлов с подсчётом чтений и пересчётов scope, устаревшее evidence, замену anchors, XML namespaces, ownership conflicts, транзитивные scopes, переиспользование audit receipts и локальную iOS-ограниченную приёмку. Полный запуск — `validate-vibe-skills.ps1`; в Python должны быть доступны PyYAML и Pillow. Дополнительные модельные agent evals включаются отдельно.

`delivery-timing.py` учитывает интервалы очереди, выполнения, binding и явно записанные validation/agent-wait/repair. Перекрытия не суммируются как wall-clock экономия. Цели bind ≤5 с, compact resume ≤10 с и readiness ≤30 с следует подтвердить на следующем сопоставимом полном приложении. Регрессионная проверка сложности не доказывает конкретную длительность всего цикла разработки.

Установщик Copy исключает `.test-workspaces` и `__pycache__`: временные проекты не должны попадать в пакет навыков.
