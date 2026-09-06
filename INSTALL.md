# Vibe KMP skills 2.1

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

Installed skills become available on the next turn.

The manifest currently installs 14 skills, including the independent `$vibe-acceptance-auditor`. The manifest, rather than a hard-coded count in the installer, is the source of truth for Copy/Junction installation and post-install checks.

To implement an application, prepare and approve Vibe AppSpec 2.0, then start a separate session:

```text
Use $vibe-developer. Implement the application from D:\Projects\MyApp\app-spec.
Validate the specification with --require-current, initialize the delivery ledger before code changes,
and do not silently change approved requirements. Require a fresh acceptance audit before completion.
```

Protocol 1.x AppSpecs and delivery artifacts are unsupported. The tools do not migrate, delete, or automatically reinitialize them; prepare a newly approved AppSpec 2.0 instead.

## Missing skills and installation health

```powershell
.\install-vibe-skills.ps1 -Mode Junction -MissingOnly
.\.tooling\venv\Scripts\python.exe -B .\check-vibe-installation.py
```

MissingOnly preserves existing entries. Existing junctions immediately use the updated source. Health compares every manifest skill's installed files with this package; it reports missing/stale entries and does not assume the host has refreshed its catalog yet.

## Release validation of protocol changes

Run the deterministic package suite and the separate stateful agent gate before releasing changes to recovery or closure:

```powershell
.\validate-vibe-skills.ps1 -IncludeAgentEvals
```

The agent gate creates a real repository, starts two independent ephemeral executions, and checks saved state, protected file hashes, production behavior, command events and receipts. A missing CLI/tooling failure is a blocked gate, never a pass. These runs use the configured Codex account/model. Ordinary local deterministic validation remains available without this additional agent cost.
