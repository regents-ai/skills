# Reads a page waits for

A read belongs to whoever asked for it: the account, wallet or route on screen when
it started. An answer that arrives after the page moved on is dropped, and a read
that failed never shows as zero or empty. Keep each page's own state machine
(portfolio, staking, forum) in that page; this covers only how one read lands.

## Use LiveView first

`start_async/3` and `handle_async/3` do the work. Do not stop a read with
`cancel_async/2`: a task killed mid-query takes its database connection down with it
(the pool logs "client exited" and reconnects; reproduced 2026-09-27), and a cancel
does not recall an answer already in the mailbox. Let the read finish; its
generation decides whether the answer lands. `assign_async/3` stamps no read time
and has no owner; use it only for a read whose owner never changes while the page is
open.

## The pattern

The template's `AshTemplateWeb.Read` (`platform/lib/ash_template_web/read.ex`)
is the whole helper: a struct per read and three functions.

```elixir
def mount(_params, _session, socket), do: {:ok, assign(socket, balance: %Read{})}

# owner is what the answer depends on: account id, wallet, route params.
Read.start(socket, :balance, wallet, fn -> Balances.read(wallet) end)
Read.clear(socket, :balance)

def handle_async({Read, _name, _generation} = name, result, socket),
  do: {:noreply, Read.settle(socket, name, result)}
```

- **Generation.** `start` and `clear` move the read to a new generation and name
  the task `{Read, name, generation}`. `settle` lands only the current
  generation's answer, so a slow answer for an earlier owner is dropped even if
  it was already sent.
- **Owner.** `start` for the same owner keeps the last value on screen while it
  refreshes; a new owner starts from nothing, so one wallet's figures never sit
  under another's name.
- **States.** `:idle` (nothing asked), `:loading`, `:ready`, `:empty` (an answer
  of `[]`, `%{}` or `nil`), `:stale` (a refresh failed; the last good value and
  its `read_at` stay, marked as old) and `:error` (failed with no earlier
  value). Render each one. Zero is a real value; a failure has none to show.
- **Freshness per source.** `read_at` is stamped when that read's answer lands,
  never when it starts. Each read on a page has its own; do not show one
  "updated" time for several sources unless every one of them has landed.
- **Cleanup.** In `handle_params`, `clear` every read the new route does not
  show and `start` the ones it does with the new owner. When the signed-in
  account or chosen wallet changes, `clear` or `start` every read it owned in
  the same callback, so no render shows the old owner's figures.
- **Merging reads.** A refresh while a read runs starts a new one; the running
  read finishes and its answer is dropped, so many refresh reasons land one
  answer. When reasons can arrive faster than a read finishes, note them and
  start once from `handle_async` after the running read lands, so reads do not
  pile up. That is the only merging.

## Never merged: wallet actions

`Read` is for reads. A wallet press, its transaction and the server's check of
the wallet's answer are never cancelled, merged, deferred or deduplicated
through it; each press reaches the wallet and gets its own check (see
`onchain-buttons`). Refresh reads after a confirmed action by calling `start`.

A read that finishes inside the callback (a local database read in
`handle_params`, or a controller action) cannot race and needs no generation, but it
still needs its own error state instead of an empty list.

`Ash.count` and `Ash.exists` raise a database failure (`Postgrex.Error`,
`DBConnection.ConnectionError`) where `Ash.read` returns `{:error, _}` (Ash 3.33.11,
reproduced against a missing table). Inside `Read.start` the raise ends the task and
settles as failed. Inside a callback, turn exactly those two exceptions into
`{:error, _}` in the one function that makes the count, with a comment saying why,
and render its error state; never rescue everything. Patchbay's daily allowance does it
(patchbay@07208a0 `platform/lib/patchbay/assist/allowance.ex:137-143`):

```elixir
# Ash hands back a count's own errors, but a database that refuses the
# count raises instead of answering; both come back here as an error.
defp count(query) do
  Ash.count(query, authorize?: false)
rescue
  failure in [Postgrex.Error, DBConnection.ConnectionError] -> {:error, failure}
end
```

Every caller then matches `{:ok, n}` and `{:error, _}`; never `Ash.count!` or a bare
`{:ok, n} =` on a read a page event can reach. The template itself has no count, so
this is the example to copy.

## Proof

`/showcase` (Feedback, "Slow reads") runs the pattern on fixture wallets:
choose the slow wallet then another before it answers; the slow answer never
appears. Tick "Make the next reads fail": a refresh keeps the old reading marked
as old, and a new wallet shows a failure, never zero. Repeat that check in the
browser for each read a page adds: switch owner mid-read and force a failure.
