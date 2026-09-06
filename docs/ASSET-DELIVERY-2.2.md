# Ассеты в Vibe 2.2

## Что обнаружено

До доработки визуальные требования хранились в `design.md`, таблицах actions/iconography в `screens/SCREEN-*.md` и агрегированном `uiQuality.iconography`. `app-spec/assets/` входил в полный fingerprint спецификации. Product Designer требовал готовые custom/brand assets перед реализацией; валидатор разрешал только `provided`/`not-required`. Это блокировало плановое создание оригинальной графики, но не доказывало полноту фактической поставки: отсутствовала машинная связь «нужный ассет → файл → production UI».

## Новый процесс

1. Product Designer определяет назначение, стиль, варианты и использование всех иконок, лого и иллюстраций. В AppSpec фиксируются `assetRequirements`, ASSET IDs, ссылки на screen/AC, acquisition, dp-размер, плотность, прозрачность и точные Compose Resources paths.
2. `vibe-assets-creator` переиспользует разрешённые ресурсы, рисует простые XML-векторы или создаёт растровые изображения через imagegen. Утверждённый brief позволяет начать работу без готового файла. Запрос пользователя нужен для материально неопределённого решения или точного недоступного внешнего брендинга.
3. Architect обеспечивает resource wiring. Compose Expert подключает все создаваемые runtime-ассеты через Compose Multiplatform Resources и типизированные `Res.drawable` accessors.
4. Assets Creator фиксирует фактические результаты в `docs/assets/asset-manifest.json`: outputs и SHA-256, provenance, generation record, production use sites и визуальные доказательства. Это часть workspace fingerprint; утверждённый AppSpec не изменяется при каждом результате генерации.
5. Visual Testing проверяет production previews/goldens. Обязательный repository gate с `asset-check` и `asset-visual` входит в ledger, pre-audit и итоговую приёмку. Независимый аудитор сравнивает инвентарь с текстом и экранами, проверяет смысл изображения и достижимость UI.

Рабочее состояние остаётся в ledger и specialist recovery packets. После compaction агент читает ASSET IDs, сохранённые outputs/hashes и pending variants; уже созданная графика не генерируется заново из-за потери истории.

## Форматы и размеры

Для простых иконок предпочтителен переносимый XML vector. Для растровых иконок default — PNG 128×128 с реальной прозрачностью. При плотности 4× это покрывает 32 dp; 64×64 допускается, когда достаточно для заявленных `displayDp × maxDensity`. Лого и иллюстрации сохраняют нужную пропорцию и рассчитываются по месту использования. Размер пиксельного файла не задаёт размер Compose-элемента или touch target.

Общие runtime-ресурсы размещаются в `src/commonMain/composeResources/drawable`, с необязательными `drawable-dark`/`drawable-light` и обязательным fallback. SVG можно хранить как исходник, но общий Android+iOS export — XML/PNG. Нативные launcher/store derivatives остаются отдельной платформенной работой.

Основание: [загрузка ресурсов и переносимость XML/SVG](https://kotlinlang.org/docs/multiplatform/compose-multiplatform-resources-usage.html), [настройка ресурсов и qualifiers](https://kotlinlang.org/docs/multiplatform/compose-multiplatform-resources-setup.html), проверено 2026-09-06. Правило 128 px — выбор пакета на основе требуемой плотности, а не ограничение библиотеки.

## Границы проверок и совместимость

Статический валидатор проверяет inventory/variants, paths, хеши, PNG dimensions/alpha, структуру XML и запрещённые Android resource references, коллизии имён и production references. Он не доказывает визуальную семантику, правдивость review note или достижимость косвенной resource mapping. Для этого сохранены реальные build/preview/golden checks и независимый аудит. Промпт генерации без изображения не является поставкой.

Protocol 2.0 сохранён. Старые specs без расширения получают предупреждение, а специальная проверка ассетов их отклоняет. Новые specs и работа с ассетами требуют полного инвентаря; существующие утверждённые документы обновляются через согласованную spec revision, с сохранением истории. PNG inspection требует Pillow; отсутствие зависимости не превращается в успешную проверку.

Основной контракт: [asset-contract.md](../vibe-assets-creator/references/asset-contract.md). Новый skill: [vibe-assets-creator](../vibe-assets-creator/SKILL.md).

## Проверки и установка

Полный deterministic прогон: `VALIDATION PASSED: 15 skills`, 60 Python-тестов, проверки установщика Copy/Junction и Gradle runner. В их числе 11 новых тестов asset delivery: planned intake без файла, actual delivery, legacy boundary, stale hash, ссылка только в комментарии, PNG alpha/размер/плотность, variants/fallback, path escape, дубликаты, XML portability, generation record, aggregate gate, пустой/невалидный inventory и коллизия resource name. Последующее уточнение обработки невалидного inventory также проверено повторным целевым запуском этих 11 тестов.

Независимый forward-test создал реальный XML по утверждённому brief, manifest и recovery checkpoint. Он сохранил отсутствующие build/render/golden evidence как незавершённую проверку и обнаружил конфликт prose с JSON, не изменив защищённые входы. Это проверка поведения skill на изолированном примере; реальная генерация через сервис изображений и компиляция KMP-приложения в этой задаче не выполнялись.

При дополнительном stateful CLI-тесте обнаружена неоднозначная формулировка старого fixture «после проверки очистить pending check», без условия успешности. Она уточнена: только после реализации обеих частей и успешной проверки. В recovery contract явно сохранены pending rerun после неуспеха и `in-progress` для частичной реализации; критерии grading не ослаблялись.

Повторный двухэтапный CLI-прогон завершился `STATEFUL AGENT EVALS PASSED`: оба grading-файла содержат `errors: []`. Второй независимый процесс восстановил задание из репозитория, завершил поведение и сохранил реальный успешный receipt, не меняя защищённые файлы. Логи этой проверки и deterministic suite находятся в локальной `.tooling/`.

`vibe-assets-creator` установлен через Junction. Проверка установленного пакета: `healthy: true`, 15 из 15 skills актуальны. Новый skill доступен на следующем ходе.
