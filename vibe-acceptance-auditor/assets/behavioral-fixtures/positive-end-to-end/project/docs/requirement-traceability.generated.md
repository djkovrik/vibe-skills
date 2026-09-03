# Claimed traceability

This fixture claim is not audit evidence; the auditor must independently inspect and run the named surfaces.

| Obligation | Claimed production symbol | Claimed test/check |
| --- | --- | --- |
| AC-001 / Preference:create | `PreferenceComponent.create_preference` | `PreferenceComponentContractTest.test_create_preference_is_observable` |
| AC-002 / Preference:read | `PreferenceComponent.read_preference` | `PreferenceComponentContractTest.test_read_preference_returns_current_value` |
| AC-003 / Preference:update | `PreferenceComponent.update_preference` | `PreferenceComponentContractTest.test_update_preference_replaces_value` |
| AC-004 / Preference:delete | `PreferenceComponent.delete_preference` | `PreferenceComponentContractTest.test_delete_preference_restores_empty_state` |
| QG-001 | `verify_fixture.py` | `python verify_fixture.py` exit 0 |
| QG-002 | `verify_fixture.py` | `python verify_fixture.py` exit 0 |
| QG-003 | `verify_fixture.py` | `python verify_fixture.py` exit 0 |
| QG-004 | conditional external publication | condition not active |
