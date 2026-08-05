# Test pyramid and doubles

Use Decompose component tests through public contracts as the primary application test layer. They should carry most acceptance-scenario and cross-component behavioral coverage. Map supporting risks to the lowest faithful layer:

- pure domain/value/manager tests;
- Store tests for state-machine transitions;
- component tests for public model/output/navigation/lifecycle;
- persistence/network/sync contract/integration tests;
- platform unit/device tests where native behavior cannot be faked.

When the root component lives in a separate module, prefer that `root` module as the home of the centralized component-test suite: it can assemble the production graph, navigation, lifecycle, outputs, and deterministic fakes in one place. Choose another aggregation location only when root is not separate or the dependency graph makes root-hosted tests invalid, and document the exception.

Prefer deterministic fakes for stateful collaborators, sanitized fixtures for wire data, and mocks only for interaction boundaries. Inject dispatchers, clock, time zone, IDs, and randomness. Keep setup/teardown symmetric.
