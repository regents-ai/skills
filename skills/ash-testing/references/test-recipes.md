# Focused test recipes

These are behavior specifications, not paste-ready tests. Adapt the application's
real modules, helpers, interface signatures, versioned error shapes, and test isolation.

## Resource/action change

Arrange an allowed actor and required tenant-owned records. Invoke the named domain
interface. Assert the important returned and persisted attributes. Repeat with invalid
input and verify the error's field/path and absence of a partial write. For custom
changes, exercise the action rather than only calling the callback in isolation.

## Policy or tenant change

Arrange two actors and two tenants with distinct records. Test an allowed action and
a forbidden mutation using a valid but foreign ID. Assert unchanged persisted state.
For a filtered read, assert exactly the allowed records or at least the complete
non-disclosure property; do not assume an exception. Include a nested child relation
when the action manages related data. Verify membership, not merely different IDs.

## Nested form change

Construct the real form with scope. Submit invalid child data, observe the nested
field error, and preserve parent values. Submit valid data and verify child persistence.
Test omitted children versus explicitly empty input and a requested removal. Include
one unrelated/cross-tenant child ID to prevent accidental broad lookup/relate behavior.

## Concurrency-sensitive update

State the invariant and the failure schedule: for example, both transactions observe
the same old balance before either writes. Use independent transaction contexts and a
barrier that exposes that schedule, not arbitrary sleeps or two sequential calls.
Assert the allowed final state and meaningful conflict outcome. Document why the
sandbox arrangement actually exercises the competing DB transactions.

## Durable job / external effect

Use the repository's fake remote service and job-testing mode. Assert business state
and enqueueing on success, absence of an enqueued effect on rollback, retry behavior,
and replay of the same idempotency key. Simulate remote success followed by local
acknowledgement failure when that crash window matters. Do not assume mock call-count
assertions alone prove transactional enqueueing.

## Bulk change

Include one failing item among valid items. Configure enough result information to
check status/counts/errors, then verify persisted outcomes match the product's
all-or-nothing or partial-success contract. Exercise required notification behavior
and tenant boundaries. A result struct is not an all-success assertion.

## Migration

Use a disposable database starting from the relevant prior schema. Seed representative
old data, including null/duplicate cases where relevant. Apply the migration, check
preservation and constraints, and run the corresponding actions. Test rollback only
when safe and meaningful; otherwise document forward recovery. Run drift generation
checks separately. Never target production in order to make a test realistic.

## LiveView interaction and async reads

Mount under the intended authenticated scope. Exercise the form/element using stable
selectors. Assert invalid state, successful persistence, and intended navigation.
Use the installed async helper to await completion. Reverse search completion order
and ensure the old result does not overwrite the new query. Test a scope change when
that is supported. Use the browser for hooks, focus, and reconnect behavior.

When browser specs share one sandbox transaction, wait for each page's reads to land
(assert on the loaded content or its `data-state`) before navigating away. Leaving a
page mid-read kills the read's process inside the shared connection, which ends the
transaction and fails every later spec with DBConnection "client exited", far from
the cause.

## Negative assertion quality

A denied request that crashes before reaching authorization is not a good security
test. A uniqueness test that fails for a missing required field proves nothing about
uniqueness. Keep inputs otherwise valid and verify the intended failure reason.
Do not assert internal error prose when a stable error type/field is available.

## Reporting template

```text
Delivered:
  [observable behavior]
Verified:
  [actual command / environment / result]
Not verified:
  [specific check and reason, or none]
Important limitations:
  [migration/external behavior that remains outside this change]
```

Sources: [index](../../ash-stack/references/source-index.md), S05, S29-S33, S43.
