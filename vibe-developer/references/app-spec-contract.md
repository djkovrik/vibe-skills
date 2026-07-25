# Vibe AppSpec v1 contract

## Contents

- [Boundary](#boundary)
- [Required structure](#required-structure)
- [Identifiers and links](#identifiers-and-links)
- [Validation](#validation)

## Boundary

Consume an already prepared specification. Do not restart product discovery during implementation. Put unresolved choices in `openQuestions`; do not silently decide them.

## Required structure

```text
app-spec/
  app-spec.json
  product.md
  domain.md
  data.md
  quality.md
  flows/FLOW-*.md
  screens/SCREEN-*.md
  assets/
```

`app-spec.json` declares app metadata, requirements, flow/screen IDs, capabilities, constraints, and open questions. Additional fields are allowed. Reject any schema major other than `1`.

The Markdown files define product intent, domain semantics, data contracts, quality gates, flows, acceptance scenarios, screen states, accessibility, localization, and allowed monetization slots.

## Identifiers and links

- Use stable `REQ-NNN`, `FLOW-NNN`, `SCREEN-NNN`, and `AC-NNN` identifiers.
- Put each acceptance scenario in one flow and include Given/When/Then.
- Link requirements to acceptance IDs.
- Link screens to requirements and flows.
- Keep filenames equal to their stable flow/screen IDs.

## Validation

Run:

```powershell
python .\vibe-developer\scripts\validate-app-spec.py <app-spec-directory>
```

The validator is read-only. Errors block implementation; warnings require review. It validates contract structure and references, not full product correctness.

