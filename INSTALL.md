# Vibe KMP skills

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

To implement an application, prepare and validate Vibe AppSpec v1, then start a separate session:

```text
Use $vibe-developer. Implement the application from D:\Projects\MyApp\app-spec.
Validate the specification first and do not silently change approved requirements.
```
