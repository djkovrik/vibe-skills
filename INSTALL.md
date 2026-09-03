# Vibe KMP skills 1.5

Run commands from this package root in PowerShell.

The official `skill-creator` validator requires PyYAML. This workstation uses a package-local `.tooling\venv`; nothing is installed globally. If that ignored environment is absent on another workstation, create a local venv and install PyYAML only after approving the download:

```powershell
python -m venv .\.tooling\venv
.\.tooling\venv\Scripts\python.exe -m pip install PyYAML
```

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

Junction keeps this package as the single editable copy. Copy mode creates independent global copies and requires `-Force` for an explicit resynchronization. Existing real skill directories are moved to timestamped sibling backups before replacement.

After first installation or after changing skill metadata, restart the Codex client if the updated skills are not immediately visible.

The manifest currently installs 14 skills, including the independent `$vibe-acceptance-auditor`. The manifest, rather than a hard-coded count in the installer, is the source of truth for Copy/Junction installation and post-install checks.

To implement an application, prepare and approve Vibe AppSpec 1.4, then start a separate session:

```text
Use $vibe-developer. Implement the application from D:\Projects\MyApp\app-spec.
Validate the specification with --require-current, initialize the delivery ledger before code changes,
and do not silently change approved requirements. Require a fresh acceptance audit before completion.
```

AppSpec 1.0–1.3 remains readable as legacy. A full `$vibe-developer` cycle requires migration into a new directory with `migrate-app-spec.py` and explicit review of all `needs-review` scenarios and blocking questions. Narrow specialist work may still target a legacy repository directly.
