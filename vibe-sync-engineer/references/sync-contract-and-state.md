# Sync contract and state

Define a manager depending only on auth identity, local snapshot/settings contracts, remote service, clock, and post-commit effects.

Expose an observable state containing:

- authentication/identity state;
- idle/syncing/success/error;
- last successful sync;
- retryability or required user action.

Make concurrent trigger behavior explicit: serialize, coalesce, or cancel by policy. Preserve causes and never turn partial failure into success.

Blinkly adaptation: a sync Store observing a domain manager is one implementation; keep the manager contract independent of UI.

