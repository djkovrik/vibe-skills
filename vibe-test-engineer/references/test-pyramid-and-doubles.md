# Test pyramid and doubles

Map each risk to the lowest faithful layer:

- pure domain/value/manager tests;
- Store tests for state-machine transitions;
- component tests for public model/output/navigation/lifecycle;
- persistence/network/sync contract/integration tests;
- platform unit/device tests where native behavior cannot be faked.

Prefer deterministic fakes for stateful collaborators, sanitized fixtures for wire data, and mocks only for interaction boundaries. Inject dispatchers, clock, time zone, IDs, and randomness. Keep setup/teardown symmetric.

