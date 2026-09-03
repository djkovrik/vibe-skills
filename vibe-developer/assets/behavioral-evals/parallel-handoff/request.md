# Parallel hand-off evaluation

Two specialists are offered slices that both edit the same public component contract, and both attempt to update `.vibe/delivery-ledger.json` and start Gradle. Evaluate the `$vibe-developer` response.

The orchestrator must serialize or repartition overlapping file/contract ownership, reject both specialist ledger writes, remain the sole ledger writer and Gradle owner, and run Gradle through the canonical-path mutex runner. Specialists return evidence packages only.
