# Vibe KMP Skills

Локальный пакет из 14 Agent Skills для разработки Kotlin Multiplatform приложений под Android и iOS. Protocol 2.0 принимает только утверждённый Vibe AppSpec 2.0, восстанавливает работу из репозитория и `.vibe`, реализует требования вертикальными slices и допускает итоговый статус только после request-bound fresh-context аудита.

Основной пользовательский процесс описан в [VIBE-DEVELOPMENT-WORKFLOW.md](docs/VIBE-DEVELOPMENT-WORKFLOW.md). Установку и режимы Copy/Junction объясняет [INSTALL.md](INSTALL.md).

## Основной цикл

```text
discovery -> approved AppSpec 2.0 -> strict validation
-> ledger checkpoint -> vertical AC slices and immutable hand-offs
-> targeted receipts -> audit request -> fresh audit -> final receipt -> aggregate validation
```

AppSpec и delivery artifacts 1.x являются несовместимыми: инструменты возвращают `unsupported protocol`, не мигрируют, не удаляют и не переинициализируют их автоматически.

## Skills

Главная точка входа — [vibe-developer](vibe-developer/SKILL.md). Независимую полноту проверяет [vibe-acceptance-auditor](vibe-acceptance-auditor/SKILL.md).

- [vibe-project-architect](vibe-project-architect/SKILL.md) — модули, Gradle, DI, CI/release;
- [vibe-domain-engineer](vibe-domain-engineer/SKILL.md) — domain model, инварианты и расчёты;
- [vibe-decompose-engineer](vibe-decompose-engineer/SKILL.md) — components, navigation и lifecycle;
- [vibe-mvikotlin-engineer](vibe-mvikotlin-engineer/SKILL.md) — Stores и state orchestration;
- [vibe-platform-engineer](vibe-platform-engineer/SKILL.md) — Android/iOS APIs и capabilities;
- [vibe-network-engineer](vibe-network-engineer/SKILL.md) — Ktor, REST, OAuth и transport;
- [vibe-persistence-engineer](vibe-persistence-engineer/SKILL.md) — SQLDelight, migrations и Settings;
- [vibe-sync-engineer](vibe-sync-engineer/SKILL.md) — snapshots, conflicts и offline sync;
- [vibe-product-designer](vibe-product-designer/SKILL.md) — UI evidence, Material 3 и accessibility;
- [vibe-visual-testing](vibe-visual-testing/SKILL.md) — previews, Paparazzi и goldens;
- [vibe-monetization-engineer](vibe-monetization-engineer/SKILL.md) — Yandex Ads и privacy gate;
- [vibe-test-engineer](vibe-test-engineer/SKILL.md) — non-visual test pyramid.

Каждый specialist можно вызывать напрямую для узкой задачи. При orchestration он получает assignment/AC/gate IDs и непересекающиеся boundaries, записывает immutable `.vibe/handoffs/<id>.json` и не меняет ledger. Только `$vibe-developer` инспектирует/импортирует hand-off, атомарно пишет ledger и запускает Gradle.

## Проверка AppSpec

```powershell
python .\vibe-developer\scripts\validate-app-spec.py D:\Projects\MyApp\app-spec --require-current
```

## Delivery state

В целевом проекте отслеживаются:

- `.vibe/delivery-ledger.json` — единственный редактируемый источник состояния;
- `.vibe/handoffs/*.json` и `.vibe/receipts/*.json` — immutable evidence;
- `.vibe/audits/<request-id>/request.json` и `.vibe/audits/<request-id>/audit.json` — request-bound независимый аудит;
- оба файла `docs/*.generated.md` — проверяемые детерминированные проекции.

`implementation-complete` требует закрыть все AC и repository gates, последний успешный receipt для каждой surface, единый final receipt, свежий audit `PASS` и parity отчётов. `release-ready` дополнительно требует закрыть platform/external/release gates; `blocked-external` с ним несовместим.

## Проверка и установка пакета

```powershell
.\validate-vibe-skills.ps1
.\install-vibe-skills.ps1 -Mode Junction
```

Manifest является единственным источником точного списка устанавливаемых skills. Installer проверяет каждую его запись и в Junction, и в Copy mode.
