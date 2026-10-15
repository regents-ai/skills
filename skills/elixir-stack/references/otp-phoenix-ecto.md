# OTP, Phoenix and Ecto essentials

## Processes and supervision

- Start every long-lived process under a supervisor in `application.ex`, in
  dependency order (repo, then PubSub, then Oban, then the endpoint).
- A GenServer serialises every call through one mailbox. Use one only for state
  that lives in memory and has a single owner, such as a connection or a rate
  window. Never use one to queue work, cache database rows or poll the database.
- Name dynamic processes through `Registry`; never create atoms from user input.
- Concurrent work inside a request: `Task.async_stream/3` with `max_concurrency`
  and `timeout`, or `Task.Supervisor.async_nolink/2` when a crash must not take the
  caller down.
- Read-mostly lookups go in ETS or `:persistent_term`, not behind `GenServer.call`.
- Turn a string into an atom only through an explicit map of allowed values.
  `String.to_existing_atom/1` fails when the module that defines the atom has not
  been loaded yet, which happens in development and tests.

## Phoenix

- `Phoenix.PubSub` tells processes on every node that something changed. It is not
  durable: whatever must not be lost is written to a table or queued in Oban first,
  and the broadcast only wakes readers up.
- LiveView loads data in `mount` and `handle_params`; slow loads use `assign_async`
  or `start_async`. Lists use streams.
- Controllers stay thin: parse the request, call an Ash action or domain function,
  render. A route carrying secrets or private addresses is declared with
  `log: false`.

## Ecto and Postgres

- Constraints live in the database (unique indexes, foreign keys, checks) and Ash
  identities reflect them.
- Hold a transaction only for database work. Never call HTTP, a chain or a slow
  service inside one.
- Concurrency: `FOR UPDATE SKIP LOCKED` to share rows between workers,
  `pg_advisory_xact_lock` to make one key single-writer, and a compare-and-set
  (`UPDATE ... WHERE value = expected`) to advance shared state safely. Oban
  already uses these for jobs; don't rebuild them for job-like work.
- A sequence number assigned before commit can become visible out of order. When
  readers follow a sequence, read only up to a point every earlier transaction has
  committed past, or write the event log under a lock held through commit.
- Every site shares one production database in its own schema: migrations,
  queries and Oban use the site's prefix.

## HTTP to other services

- Req for everything: set `receive_timeout`, retry only safe requests, and bound
  response size where the answer is untrusted.
- Calls to addresses that users supply must resolve the name, refuse private and
  local addresses, and connect to the address that was checked. That is shared code
  (Regent's `mcp_events` callback module does it); never write a second copy.

## Telemetry

Emit `:telemetry` events for work worth measuring and attach them in the site's
`Telemetry` module. Log a decision with its identifiers, never secrets, signatures
or user text.
