# Аудит полноты AppSpec и восстановления контекста

Дата: 2026-09-05. Объект: текущий пакет Protocol 2.0 в `D:/Sources/vibe-skills`, его скрипты, тесты и установка в `C:/Users/Sergey/.codex/skills`.

Это аудит механизма skills, а не заключение о полноте конкретного приложения. Код skills не изменялся. Проверки выполнялись на изолированных временных fixtures.

## Оценка

Основа сильная: полнота больше не определяется памятью разговора или словами «всё готово». Есть обязательства с ID, отдельные статусы, устойчивое состояние в репозитории, привязка evidence к версии файлов и независимый аудит. Однако текущую реализацию нельзя считать надёжно проверенным механизмом для длинных сессий: восстановительный brief теряет значимые поля, несколько переходов жизненного цикла не реализованы, а некоторые обещания протокола валидаторы не проверяют.

Защита от случайного использования устаревшего кода работает лучше, чем восстановление продуктовых решений и точного незавершённого плана. Проверка структурной полноты сильнее проверки смысловой полноты.

## Что уже работает

| Механизм | Реализация и значение |
| --- | --- |
| AppSpec как контракт | Строгая версия 2.0; approved/excluded requirements; отдельные AC; связи с flow/screen; зависимости без циклов; явные CRUD/domain operations и verification surfaces. [Контракт](D:/Sources/vibe-skills/vibe-developer/references/app-spec-contract.md:23), [валидатор](D:/Sources/vibe-skills/vibe-developer/scripts/vibe_protocol.py:234). |
| Реестр обязательств | Ledger создаётся до первой правки, содержит AC и quality gates; незавершённые элементы не должны схлопываться в общий статус. [Инициализация](D:/Sources/vibe-skills/vibe-developer/scripts/init-delivery-ledger.py:43). |
| Контроль актуальности | Хешируются все файлы AppSpec, Git HEAD, diff и незакоммиченные файлы проекта, кроме служебных delivery artifacts. [Fingerprint](D:/Sources/vibe-skills/vibe-developer/scripts/vibe_protocol.py:140). |
| Восстановление | Checkpoint, active AC, owner, границы файлов, next action; распознавание clean / expected-drift / unexpected-drift / stale-evidence. [Workflow](D:/Sources/vibe-skills/vibe-developer/SKILL.md:25). |
| Результаты специалистов | Immutable handoff, base/result fingerprints, проверка изменённых файлов и импорт хеша; сообщение в чате не считается evidence. [Контракт](D:/Sources/vibe-skills/vibe-developer/references/specialist-handoff-contract.md:3). |
| Проверки | Receipt хранит команду, exit code, покрытые obligation/surface pairs и hash лога. Для привязанных receipts агрегатор учитывает последний результат на текущем fingerprint. [Агрегатор](D:/Sources/vibe-skills/vibe-developer/scripts/validate-delivery-ledger.py:179). |
| Независимое завершение | Аудитор должен заново читать спеку и строить inventory до чтения ledger; обязательны audit PASS, final receipt и parity generated reports. Реализация и готовность релиза разделены. [Аудитор](D:/Sources/vibe-skills/vibe-acceptance-auditor/SKILL.md:24), [финальный verdict](D:/Sources/vibe-skills/vibe-developer/scripts/validate-delivery-ledger.py:278). |

## Подтверждённые проблемы

### F1 — P1: восстановительный brief скрывает незавершённую работу и неверно обозначает возможность завершения

В [resume-delivery.py](D:/Sources/vibe-skills/vibe-developer/scripts/resume-delivery.py:116) `blockers` — это только ошибки самого resume. Сохранённые `AC.blockers`, `gate.blocker`, `pendingChecks`, owner и границы активного AC в brief не возвращаются. Есть ID активного AC и dependency blockers, но нет полноценного среза незавершённых обязательств.

`completionEligible` проверяет отсутствие ошибок, stale flag и `clean`, а не закрытие AC/gates, успешность receipts и наличие актуального аудита. Проверка receipts внутри resume сравнивает fingerprint, но не exit code; привязанный audit/request вообще не валидируется.

Воспроизведено:

- сразу после init, когда AC ещё `not-started`: `completionEligible: true`;
- после сохранения блокера «нужно решение DEC-42» и pending regression: оба отсутствуют в brief, `blockers: []`;
- при текущем receipt с exit code 1: `clean`, `completionEligible: true`;
- при ссылке ledger на отсутствующий audit: тот же результат.

Финальный агрегатор часть этих ситуаций отклонит. Поэтому это не доказательство ложного итогового PASS, а опасный ложный сигнал непосредственно в точке восстановления после потери контекста.

Исправление: разделить `safeToContinue` и `completionEligible`; возвращать полный активный slice, все blockers, pending checks, unresolved gates, обязательные пути для перечитывания; проверять актуальность связанного evidence. Завершение вычислять общей логикой с агрегатором либо вообще не объявлять из resume.

### F2 — P1: штатный цикл GAPS → исправления → новый аудит не замыкается

[Workflow требует новый request и аудит после исправлений](D:/Sources/vibe-skills/vibe-developer/SKILL.md:45). Но [create-audit-request.py](D:/Sources/vibe-skills/vibe-developer/scripts/create-audit-request.py:27) всегда пишет `.vibe/audit-request.json` и [запрещает перезапись](D:/Sources/vibe-skills/vibe-developer/scripts/create-audit-request.py:58). Повторный вызов на закрытом ledger воспроизводимо завершается `refusing to overwrite immutable artifact`.

Версионирования попыток, supersede/archive-команды и документированного перехода между аудитами нет. Аналогичная проблема есть у фиксированного пути результата closure audit. Дополнительно request создаётся до записи новой привязки в ledger: сбой между этими действиями может оставить непривязанный immutable request.

Исправление: хранить immutable attempts по request ID; в ledger менять текущую ссылку атомарно; предусмотреть повторяемое восстановление прерванного создания запроса. Историю аудитов сохранять.

### F3 — P1: временная свежесть evidence проверяется не полностью

В [валидаторе аудита](D:/Sources/vibe-skills/vibe-acceptance-auditor/scripts/validate-closure-audit.py:97) проверяется синтаксис временных отметок check, но не попадание выполнения внутрь окна аудита. Проверка с датой 2025 года была принята для аудита сентября 2026 года, если fingerprint и остальные поля совпадали.

[Агрегатор final receipt](D:/Sources/vibe-skills/vibe-developer/scripts/validate-delivery-ledger.py:235) не требует выполнения после audit PASS. Более того, [положительный end-to-end тест](D:/Sources/vibe-skills/vibe-developer/tests/delivery-ledger/test_delivery_protocol_20.py:132) сам ставит final receipt в 10:10, request — в 10:11, окончание аудита — в 10:12 и ожидает успешное завершение. Это противоречит шагу 14 workflow.

Исправление: нормализовать timestamps к UTC и проверять `request.createdAt <= audit.startedAt <= check.startedAt <= check.completedAt <= audit.completedAt <= final.startedAt`. Предусмотреть отдельные проверки interrupted/failed runs и до-/после-fingerprint, чтобы изменения во время команды не получали доказательство только по состоянию после её завершения.

### F4 — P1: waiver подтверждается существованием файла, а не решением пользователя

[durable_reference в аудиторе](D:/Sources/vibe-skills/vibe-acceptance-auditor/scripts/validate-closure-audit.py:27) проверяет наличие файла и, если указан anchor, вхождение текста. Аналогичный [код в агрегаторе](D:/Sources/vibe-skills/vibe-developer/scripts/validate-delivery-ledger.py:54).

В standalone audit fixture все обязательства удалось перевести в `waived`, указав `project/src/preference_component.py`, удалить checks и сохранить PASS без ошибок валидатора. Исходник не содержит пользовательского решения об исключении требований.

Инструкция аудитору просмотреть решения полезна, но машинная проверка обеспечивает лишь разрешимость ссылки. После сжатия контекста это особенно опасно: потерянную причину исключения может заменить произвольная существующая ссылка.

Исправление: durable decision records с ID, типом решения, точным перечнем AC/gates, основанием, источником пользовательского согласования и статусом superseded. Waiver должен ссылаться на применимое решение, а не на произвольный файл.

### F5 — P2: новые решения и изменения AppSpec не имеют полного пути восстановления

Есть предписание начинать каждый turn с resume и checkpoint перед концом turn, но нет отдельного протокола восстановления непосредственно после сжатия внутри продолжающегося turn. У специалистов предписание handoff в основном относится к окончанию работы: промежуточное состояние их собственной длинной задачи обязательным checkpoint не закреплено. При прямом вызове специалиста общий delivery protocol не обязателен.

Новые пользовательские ограничения не требуется немедленно сохранять в конкретный журнал решений. Состояние исполнения сохраняет шаг и файлы, но не обязательно причины решений, отвергнутые подходы и ссылки на необходимый контекст. [Основные правила](D:/Sources/vibe-skills/vibe-developer/SKILL.md:25), [handoff](D:/Sources/vibe-skills/vibe-developer/references/specialist-handoff-contract.md:3).

Кроме того, утверждённое изменение AppSpec корректно делает evidence устаревшим, но штатной команды reconciliation новой редакции спеки с ledger нет. [Checkpoint](D:/Sources/vibe-skills/vibe-developer/scripts/checkpoint-delivery.py:114) обновляет workspace/execution, а AppSpec fingerprint и canonical inventory остаются прежними; [новый audit request](D:/Sources/vibe-skills/vibe-developer/scripts/create-audit-request.py:36) затем отклоняется. Удалять/reinitialize существующий ledger запрещено. Это архитектурный пробел жизненного цикла, найденный по коду; отдельный сценарий изменения спеки не запускался.

Исправление: сохранять существенное steering сразу; добавить компактный recovery packet для orchestrator и незавершённых specialist assignments; включать перечень файлов для перечитывания. Добавить атомарный `reconcile-spec` с diff обязательств, сохранением истории, привязкой принятого решения и явной инвалидизацией затронутого evidence.

### F6 — P2: тесты compaction проверяют знание правил, а не способность продолжить работу

[Сценарий compaction-resume](D:/Sources/vibe-skills/vibe-developer/assets/behavioral-evals/compaction-resume/request.md:3) словами сообщает, что ledger существует и контекст потерян, затем просит перечислить действия. [Runner](D:/Sources/vibe-skills/vibe-developer/tests/run-agent-evals.ps1:29) распаковывает репозиторий skills, не создаёт описанное состояние целевого приложения. [Grader](D:/Sources/vibe-skills/vibe-developer/tests/run-agent-evals.ps1:58) сравнивает verdict, completionClaim и наличие слов вроде `resume`/`reconcil`.

Он не требует фактического вызова resume, сохранения пользовательского изменения, правильного чтения блокера, возобновления pending check или закрытия нужного AC. Реального двухэтапного запуска «выполнение → потеря истории → продолжение» нет. Эти evals также [не входят в обычный запуск валидации](D:/Sources/vibe-skills/validate-vibe-skills.ps1:196).

При этом Python-тесты действительно проверяют отдельные полезные restart-сценарии: drift внутри/вне boundaries, pending handoff, stale receipt. Это проверка функций, а не поведения агента после нескольких сжатий.

Исправление: materialized fixtures; независимый второй запуск без истории; oracle по изменениям файлов, состоянию ledger, вызванным проверкам и сохранённым решениям. Включить interruption во время slice/check/handoff, повторный аудит, изменение спеки, gate-only работу и несколько последовательных восстановлений.

### F7 — P2: обязательный аудитор отсутствует в текущей установке

[Manifest](D:/Sources/vibe-skills/vibe-skills-manifest.json:7) содержит `vibe-acceptance-auditor`, всего 14 skills. В `C:/Users/Sergey/.codex/skills` обнаружено 13 `vibe-*` junctions на текущий репозиторий; аудитора среди них нет. Это согласуется с каталогом skills текущей сессии.

По пути репозитория инструкции аудитора доступны, поэтому ручной fallback возможен. Но discovery установленного `$vibe-acceptance-auditor` нельзя считать обеспеченным. Штатный validator проверяет пакет и тестовые Copy/Junction installations, а не паритет текущей пользовательской установки.

Исправление: синхронизировать установку и добавить install-health check: manifest ↔ installed directories ↔ доступные capabilities. В рамках аудита установка не менялась.

## Дополнительные ограничения

- **Смысловая полнота остаётся обязанностью аудитора.** [Canonical inventory](D:/Sources/vibe-skills/vibe-developer/scripts/vibe_protocol.py:215) строится из JSON; проверка Given/When/Then ищет слова в тексте. Требование, упомянутое только в prose и не перенесённое в JSON, автоматически в inventory не попадёт. Это не основание убирать семантический аудит; полезно требовать source anchors для нормативных положений и явную таблицу их сопоставления с AC/gates, включая действия, состояния, ошибки и платформенные ветки.
- **Изоляция аудитора декларируется.** Сравнение context ID и `implementationContextAvailable: false` проверяет согласованность записанных полей, но не реальную историю запуска. Нужны host-issued metadata или проверяемая квитанция запуска; сами поля не доказывают независимость. [Код](D:/Sources/vibe-skills/vibe-acceptance-auditor/scripts/validate-closure-audit.py:68).
- **Атомарная запись не равна конкурентному compare-and-swap.** [update_ledger_atomic](D:/Sources/vibe-skills/vibe-developer/scripts/vibe_protocol.py:94) читает digest, выполняет mutate и replace без блокировки всего участка. Два пересекающихся вызова могут прочитать одинаковый digest и потерять одно обновление. Единственный orchestrator снижает риск; конкурентный запуск не воспроизводился.
- **Project Architect остался на менее строгом handoff.** Его [инструкция](D:/Sources/vibe-skills/vibe-project-architect/SKILL.md:53) требует evidence package, но не immutable JSON Protocol 2.0 с assignment/base/result fingerprints, как другие специалисты. Стоит унифицировать контракт.
- **Fingerprint консервативен.** Git commit меняет HEAD даже при прежнем дереве кода; это инвалидирует receipts. Такой выбор безопасен, но повышает стоимость длинной доставки. Нужна явная стратегия checkpoint/evidence после commit, а не неявное ослабление проверок.

## Выполненная проверка

Запущен `validate-vibe-skills.ps1 -SkipInstallerWhatIf`: exit code 0, `VALIDATION PASSED: 14 skills`. Прошли 27 Python-тестов (4 + 6 + 5 + 12), тесты Copy/Junction installer и Gradle runner. Ошибки, выводимые при проверке намеренно невалидных AppSpec fixtures, ожидаемы.

Дополнительные probes: init/resume, item blocker и pending check, failed current receipt, missing audit binding, повторный audit request, check до аудита, произвольный source file как waiver. Результаты приведены в F1–F4. Локальный вспомогательный скрипт: `.tooling/audit_protocol_probes.py`; он использует disposable fixtures и не меняет реализацию skills.

Не запускались платные/долгие agent evals, реальные приложения и DishReady regression. Работа агента под фактическим многократным сжатием контекста этим аудитом не измерялась. Выводы о таких сессиях основаны на контракте, реализованных recovery paths и качестве тестов.

## Рекомендуемая последовательность

1. Исправить F1–F4 и добавить регрессии на воспроизведённые случаи; проверить полный цикл GAPS → fix → audit PASS → final.
2. Добавить durable decisions, восстановление промежуточных specialist assignments и reconciliation принятой редакции AppSpec.
3. Сделать реальные stateful recovery evals и включить их в отдельный обязательный quality gate пакета.
4. Проверять текущую установку, унифицировать handoff и подтверждать реальную изоляцию аудитора.

Критерий готовности улучшений: новый агент без истории разговора восстанавливает точное незавершённое обязательство и его ограничения, сохраняет пользовательские изменения, повторяет нужные проверки, успешно проходит повторный цикл аудита и не может выдать завершение на старом либо неподтверждённом evidence.
