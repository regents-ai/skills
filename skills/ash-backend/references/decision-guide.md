# Choosing the Ash construct

| Requirement | First construct to inspect | Avoid |
| --- | --- | --- |
| Persisted domain entity | Resource + existing data layer | Parallel Ecto schema for the same entity |
| Business operation | Named action | State mutations scattered across handlers |
| Stable application API | Domain code interface | Thin wrapper layer over every Ash function |
| Transient operation input | Action argument | Persisting input-only flags or credentials |
| Stored property | Typed attribute | Unstructured maps for important invariants |
| Derived display/domain value | Calculation | Persisted stale duplication without reason |
| Count/sum/summary of relations | Aggregate | Loading all children and reducing in a view |
| Read shaping | Read action/preparation | Duplicated controller-specific query logic |
| Reject invalid data | Validation | Hidden mutation during validation |
| Change action behavior | Built-in or module change | Ad hoc LiveView writes |
| Relationship edits | Action argument + managed relationship | Blind foreign-key reassignment |
| Uniqueness | Identity + verified database constraint | Only a pre-insert existence check |
| Non-CRUD operation | Generic action, possibly a plain Elixir function behind it | Fake database resource for a pure helper |
| External persistence semantics | Documented manual action/data layer | Bypassing the action boundary everywhere |
| Finite state transitions | Named actions; existing state-machine extension if useful | Public unrestricted status updates |
| Multi-step workflow | Existing composition, action hooks, or Reactor when justified | Assuming every workflow needs a new engine |

This is a decision aid, not a list of mandatory abstractions. Inspect the relevant
DSL entry and the actual resource before implementing a row.

## Before/after reviews

**Too broad:** a `save` action accepts all attributes, including `owner_id`,
`organization_id`, and `status`, because a generator produced them.
**Better:** separate permitted user edits from trusted ownership assignment and
privileged transitions. Verify the created record and negative cases.

**Too eager:** a custom calculation loops over records, querying each one's children.
**Better:** identify expression/aggregate support or batched calculation loading, then
measure query growth at realistic row counts. Do not claim every calculation executes
in SQL; the calculation and data layer decide that.

**Too optimistic:** a bulk update is reported as successful because it returned a
result object. **Better:** request and interpret enough result information to detect
partial failure. Define whether the product expects all-or-nothing or best-effort.

**Too coupled:** a LiveView sends a webhook and flips a status field directly.
**Better:** one action enforces the transition and records required durable work;
the UI renders the resulting state. Keep presentation-specific flash text in the UI.

## Patterns the sites already use

**Notify after the commit.** Inside a transaction, run each action with
`return_notifications?: true`, hand the notifications out of the transaction with its
result, and call `Ash.Notifier.notify/1` only once it has committed. A page that rereads
on the notification then finds the new row, and a rollback sends nothing
(autolaunch@3f4fbb0 `platform/lib/autolaunch/wallet_attempts.ex:48-60`):

```elixir
with {:ok, {response, notifications}} <- transact(lease, &verify_locked(&1, attempt)) do
  Ash.Notifier.notify(notifications)
  {:ok, response}
end
```

**Insert once.** A row that is written the first time and never changed after is an
upsert on its identity that updates nothing: `upsert? true`, `upsert_identity`,
`upsert_fields []`, `upsert_condition expr(false)` and `return_skipped_upsert? true`.
A second write of the same row returns the one already there, with no read before the
write (keyfleet@4993c64 `platform/lib/keyfleet/keys/key_attachment.ex:137-141`).

**Keyset pages.** A list that can grow is read a bounded page at a time, by keyset,
with the page required so no caller reads it all (regents@140eea2c
`platform/lib/ash_platform/names/claim.ex:71-76`):

```elixir
read :mine do
  primary? true
  prepare build(sort: [id: :asc])

  pagination do
    required? true
    keyset? true
    default_limit 50
    max_page_size 50
  end
end
```

The page keeps the rows in a stream and asks for the next page with the last page's
`after` cursor.

## Debug an unfamiliar DSL/compiler error

Reduce it to the resource, action, extension, or generated interface that fails. Check
the lockfile version and installed module/DSL docs. Check resource/domain registration,
required extensions, accepted attribute versus argument names, and relationship action
availability. Compare against a nearby compiling example. Make one narrow change and
compile. Do not cycle through guessed DSL names or upgrade dependencies as a first fix.

Sources: [index](../../ash-stack/references/source-index.md), S02, S03, S12-S22.
