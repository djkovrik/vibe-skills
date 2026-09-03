# Compaction/resume evaluation

Continue a partially implemented AppSpec after all prior conversation has been compacted away. Use only the supplied approved AppSpec 1.4, `.vibe/delivery-ledger.json`, current repository, receipts, and closure audit. Do not accept a prose claim that a milestone was complete.

The evaluator must recompute AppSpec/workspace fingerprints, stop on stale state, preserve each unfinished AC/gate as an individual entry, and resume from the first dependency-ready non-verified slice. It must not recreate or overwrite the ledger.
