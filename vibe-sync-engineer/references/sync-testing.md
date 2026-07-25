# Sync testing

Use deterministic in-memory fakes and clocks. Cover:

- signed out/sign in/account switch;
- upload-only/download-only/no-change;
- both-changed conflicts and deterministic ties;
- schema mismatch;
- dedupe and orphan filtering;
- remote apply without local retracking;
- offline, timeout, partial remote/local failure;
- repeated and concurrent sync;
- transaction rollback;
- post-commit effects only after success;
- observable state and last-success updates.

