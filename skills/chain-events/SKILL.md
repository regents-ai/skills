---
name: chain-events
description: Watching a chain for contract events on Regent's Phoenix and Ash sites, saving each one to the database once, and showing the saved rows on LiveView pages as they arrive. Use when adding or changing an event watcher, its cursor, the tables it fills, how a reorg or disagreement is handled, how pages hear about new rows, the "catching up" notice, or chain reads the server makes at the latest block.
---

# Chain events

**Load `ash-stack` first, then `ash-data` for the tables and `ash-frontend` for the page.**
Buttons that send transactions are `onchain-buttons`. Keyfleet's reader
(`platform/lib/keyfleet/chain/`) is the tested model for everything here.

## Rules

1. **Read at `latest`** (founder decision, 2026-09-22). Base confirms a block in about two
   seconds; nothing waits for `safe`, `finalized` or a confirmation count. A reorg that
   changes recorded history stops the watcher and a person fixes the record by hand.
2. **One poller per contract per chain**, a GenServer under the site's supervisor that runs
   a pass every few seconds and backs off on failure up to a minute. A failed pass is
   logged and retried, never fatal.
3. **A cursor row per chain and contract** holds the first block not read yet, the head
   last seen and when, and `rescan_from` when the watcher is stopped.
4. **Each pass** reads the head, reads the last 30 recorded blocks again, then reads
   forward up to the head in stretches of at most 10,000 blocks, halving a stretch the node
   refuses down to one block.
5. **Rows and the cursor move in one transaction.** The cursor moves only if it still
   stands where the pass found it and is not stopped, so a second machine's pass or a hand
   fix is never undone.
6. **A row is written once and never overwritten.** Identity
   `[:chain_id, :transaction_hash, :log_index]`, upsert with no fields to change, and a
   check that an event read again matches the stored row. A mismatch, or a recorded
   block whose hash has changed, stops the watcher at the earliest such block.
7. **Store what the chain said**: amounts in raw token units as `:decimal`, addresses and
   hashes as lowercase `0x` strings checked by pattern, block number and hash on every row.
   Formatting belongs to the page (`RegentFormat.short_address/1`, `short_hash/1`).
8. **Pages hear after commit.** The event resource publishes through `Ash.Notifier.PubSub`.
   Inside a transaction, create with `return_notifications?: true` and call
   `Ash.Notifier.notify/1` after it commits. The notice only says "read again".
9. **Pages read through code interfaces with the viewer as actor**, subscribe only when
   connected, and re-read at most once a second however many notices arrive.
10. **Say when the record is behind.** Show a "catching up" notice while the head was read
    more than 120 seconds ago or the record is more than 300 blocks behind it.
11. **All four sites share one production database.** A new table or column needs the
    founder's approval before it reaches production.

## References

| File | Covers |
| --- | --- |
| [watcher.md](references/watcher.md) | Client, cursor, event row, record-once check, committing a stretch, poller, the page, tests |
| [sites-today.md](references/sites-today.md) | How each site watches the chain now and where it differs |

How Ash rows reach a page in general (actors, re-reading after a broadcast, streams) is in
`ash-frontend` [Forms and LiveView](../ash-frontend/references/forms-and-liveview.md#useful-liveview-design-choices)
and `ash-backend`; this skill adds only what chain events need.
