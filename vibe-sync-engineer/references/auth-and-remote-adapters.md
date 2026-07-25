# Authentication and remote adapters

- Keep sign-in UI/platform SDK outside the domain sync manager.
- Pass stable domain identity/auth state into sync.
- Define logout/account-switch behavior for local data and pending work.
- Keep Firestore/Firebase/native details behind a remote snapshot interface.
- Validate platform SDK startup before constructing adapters.
- Scope remote paths/documents to authenticated identity and security rules.
- Do not mix REST transport ownership into sync unless the remote contract explicitly uses it.

Use current official backend SDK/security documentation for the selected provider.

