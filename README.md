# Vibe KMP Skills

Локальный пакет из 14 Agent Skills для разработки Kotlin Multiplatform приложений под Android и iOS. Пакет принимает утверждённый Vibe AppSpec 1.4, ведёт долговечный delivery ledger, реализует требования вертикальными slices и допускает итоговый статус только после независимого fresh-context аудита.

Основной пользовательский процесс описан в [VIBE-DEVELOPMENT-WORKFLOW.md](docs/VIBE-DEVELOPMENT-WORKFLOW.md). Установку и режимы Copy/Junction объясняет [INSTALL.md](INSTALL.md).

## Основной цикл

```text
discovery -> approved AppSpec 1.4 -> validation --require-current
-> delivery-ledger initialization -> vertical AC slices
-> fresh acceptance audit -> full quality/release gates -> final ledger validation
```

AppSpec 1.0–1.3 валидируются как legacy, но не запускают полный или cross-cutting `$vibe-developer`-цикл. Их нужно безопасно перенести `migrate-app-spec.py` в новый каталог и вручную утвердить. Узкие прямые задачи specialist skills в legacy-проектах остаются допустимыми.

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

Каждый specialist можно вызывать напрямую для узкой задачи. При orchestration он получает AC/gate IDs и непересекающиеся file boundaries, возвращает evidence package и не меняет ledger. Только `$vibe-developer` пишет ledger и запускает Gradle.

## Проверка AppSpec

```powershell
python .\vibe-developer\scripts\validate-app-spec.py D:\Projects\MyApp\app-spec --require-current
```

Legacy migration всегда пишет в новый каталог:

```powershell
python .\vibe-developer\scripts\migrate-app-spec.py D:\Projects\MyApp\app-spec D:\Projects\MyApp\app-spec-1.4-review
```

Автоматически извлечённые AC остаются `needs-review`; unresolved ambiguity блокирует разработку до ручного утверждения.

## Delivery state

В целевом проекте отслеживаются:

- `.vibe/delivery-ledger.json` — единственный редактируемый источник состояния;
- `docs/requirement-traceability.generated.md` — детерминированный отчёт;
- `.vibe/closure-audit.json` и `docs/closure-audit.generated.md` — последний независимый аудит.

`implementation-complete` означает, что все обязательные AC и repository gates проверены или явно waived, fingerprints актуальны и fresh auditor выдал `PASS`. `release-ready` дополнительно требует закрыть platform/external/release gates; `blocked-external` с ним несовместим.

## Проверка и установка пакета

```powershell
.\validate-vibe-skills.ps1
.\install-vibe-skills.ps1 -Mode Junction
```

Manifest является единственным источником точного списка устанавливаемых skills. Installer проверяет каждую его запись и в Junction, и в Copy mode.
