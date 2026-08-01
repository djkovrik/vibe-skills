# Learned patterns

ID: DECOMPOSE-001
Status: accepted
Date: 2026-08-01
Scope: Production Decompose components with UI-visible models and Compose previews.
Decision: Expose an immutable `Value<Model>` from a `*ComponentDefault` through retained Store State and a dedicated mapper. Do not mutate production `MutableValue<Model>` or call repositories directly. Use a sibling Store-free `*ComponentPreview` for previews. Router-owned `Value<Child*>` and stateless callback-only components are excluded.
Evidence: Blinkly `shared/component/main` and peer screen modules; BulbMatch showed drift through repository-backed production `MutableValue` components.
Consequences: More Store/provider/mapper files for simple stateful screens, but one testable state owner and deterministic previews.
Validation: Component tests drive public callbacks and assert mapped models; architecture review rejects direct repository access and production mutable model mirrors.
Supersedes: none
