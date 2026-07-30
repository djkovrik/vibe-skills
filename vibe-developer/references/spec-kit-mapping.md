# Spec Kit mapping

Spec Kit is a recommended upstream workflow, not a dependency:

```text
constitution -> specify -> clarify -> plan -> checklist -> tasks -> analyze
  -> map/export to Vibe AppSpec v1
  -> separate implementation session with $vibe-developer
```

Map artifacts as follows:

| Upstream concept | Vibe AppSpec |
| --- | --- |
| feature intent, audience, success criteria | `product.md` |
| user stories and priorities | `requirements` plus `product.md` |
| design research, design system, typography, icon/asset decisions | `design.md` plus `uiQuality` |
| Given/When/Then scenarios | `flows/FLOW-*.md` and requirement acceptance IDs |
| entities, rules, edge cases | `domain.md` |
| API, storage, offline, sync | `data.md` |
| plan/checklist/quality gates | `quality.md` |
| screen/flow artifacts | `screens/` and `flows/` |
| unresolved clarifications or required user assets | structured `openQuestions`; set `blocking: true` when implementation must wait |

Preserve stable IDs while mapping. Validate the exported AppSpec and resolve errors before implementation.

Primary sources:

- https://github.github.com/spec-kit/
- https://github.github.com/spec-kit/reference/agentic-sdd.html
- https://github.com/github/spec-kit/blob/main/templates/spec-template.md
- https://github.com/github/spec-kit/blob/main/templates/plan-template.md

OpenSpec is an optional alternative: https://github.com/Fission-AI/OpenSpec
