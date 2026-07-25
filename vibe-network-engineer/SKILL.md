---
name: vibe-network-engineer
description: Build and review Kotlin Multiplatform Ktor transport layers, common API contracts, HttpClient ownership and engines, JSON serialization, request/response DTOs and mappers, HTTP/status/error handling, OAuth and bearer refresh, multipart transfer, progress, pagination, idempotency, retry/timeout policies, MockEngine tests, and fixture contracts. Use for REST APIs, HTTP clients, tokens, DTOs, uploads, downloads, or network failures.
---

# Vibe Network Engineer

## When to use

Own API transport and authentication mechanics. Hand snapshot schemas, remote merge, and sync conflict coordination to Sync.

## Inputs

Read AppSpec data/API/auth rules, target contracts, existing client wiring, and current Ktor docs. Use [client-configuration.md](references/client-configuration.md), [contracts-dto-mappers.md](references/contracts-dto-mappers.md), [auth-errors-retries.md](references/auth-errors-retries.md), [upload-download-pagination.md](references/upload-download-pagination.md), [network-testing.md](references/network-testing.md), and [tackle-patterns-and-hazards.md](references/tackle-patterns-and-hazards.md). Local paths live only in the shared [source registry](../vibe-developer/references/source-registry.md).

## Workflow

1. Define domain API/models independent of Ktor.
2. Configure one owned HttpClient with platform engines and explicit close lifecycle.
3. Define internal DTOs, serialization policy, and mappers.
4. Classify transport, timeout, HTTP, auth, serialization, and domain failures.
5. Implement host-safe bearer/OAuth refresh and bounded retries.
6. Add fixture mapper tests and Ktor MockEngine behavior tests.
7. Verify target compilation and cancellation behavior.

## Decision rules

- Keep error bodies single-read and bounded.
- Never swallow `CancellationException`.
- Retry only safe/idempotent operations with bounded policy.
- Use a stable operation ID for idempotency, never object `hashCode()`.
- Keep debug logging out of production wiring and redact secrets.
- Choose `ignoreUnknownKeys`, defaults, and `@SerialName` from API compatibility evidence.

## Validation

Cover success, malformed payload, each failure class, 401 refresh/logout, refresh races, hostile host redirects, timeout/cancellation, retry limits, idempotency stability, pagination edges, transfer progress, and HttpClient closure.

## Escalation/hand-off

Domain owns API semantics; Sync owns snapshots/conflicts; Platform/Architect own engine and native dependency setup; Test Engineer owns broader integration coverage.

## Reusable learning

Propose approved network contracts for [learned-patterns.md](references/learned-patterns.md); do not auto-promote project quirks.

