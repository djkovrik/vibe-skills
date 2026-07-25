# Domain modeling

Start with the AppSpec glossary and acceptance scenarios.

- Model identity-bearing concepts as entities and validated concepts as value objects.
- Encode closed business alternatives with sealed types.
- Put invariants at construction or operation boundaries.
- Keep serializers, SQL rows, HTTP DTOs, Compose models, and platform types outside the core model.
- Prefer pure functions for calculations and explicit outputs for decisions.
- Tie each invariant to an acceptance ID and boundary test.

Blinkly adaptation: central external interfaces and business managers show one way to isolate app rules from components and infrastructure. Generalize the boundary, not names or thresholds.

