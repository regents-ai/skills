# Oban recipes

Versions current in Regent: `oban` 2.24, `ash_oban` 0.9 (the first AshOban that
understands Oban 2.24's top-level `cron:`, `pruner:` and `lifeline:` keys). Check the
site's lockfile and read the installed version's docs before relying on an option.

## Add Oban to a site

1. Add `{:oban, "~> 2.24"}`, and `{:ash_oban, "~> 0.9"}` when Ash resources will
   own jobs. The `oban.install` and `ash_oban.install` Igniter tasks set up the same
   pieces when the site uses Igniter.
2. Migration, in the site's own schema (Autolaunch:
   `priv/repo/migrations/20260924081420_add_oban.exs`):

   ```elixir
   def up, do: Oban.Migrations.up(prefix: "mysite_app")
   def down, do: Oban.Migrations.down(prefix: "mysite_app")
   ```

3. Configuration:

   ```elixir
   # config/config.exs
   config :my_app, Oban,
     repo: MyApp.Repo,
     prefix: "mysite_app",
     queues: [default: 10, webhooks: 20],
     # Required with AshOban, even empty: it adds each trigger's sweep here.
     cron: [crontab: []],
     pruner: [max_age: {7, :days}],
     lifeline: [rescue_after: {10, :minutes}]

   # config/test.exs
   config :my_app, Oban, testing: :manual

   # config/runtime.exs, when the site's schema is set at runtime (Patchbay)
   config :my_app, Oban, prefix: database_schema
   ```

   The migration takes the same schema the repo migrates into:
   `Oban.Migrations.up(prefix: prefix() || "public")`.

4. Supervision, after the repo. With AshOban, wrap the config so triggers and
   scheduled actions get their queues and cron entries:

   ```elixir
   {Oban, AshOban.config(Application.fetch_env!(:my_app, :ash_domains),
                         Application.fetch_env!(:my_app, Oban))}
   ```

## A plain worker

```elixir
defmodule MyApp.Workers.SendReceipt do
  use Oban.Worker, queue: :webhooks, max_attempts: 8,
    unique: [keys: [:order_id], period: :infinity, states: :incomplete]

  @impl Oban.Worker
  def perform(%Oban.Job{args: %{"order_id" => id}}) do
    with {:ok, order} <- MyApp.Orders.get(id),
         :ok <- MyApp.Receipts.send(order) do
      :ok
    end
  end
end
```

Args are JSON: string keys, ids rather than structs, and never secrets (jobs are
stored in plain text and shown on dashboards). Read the current record inside
`perform`; it may have changed since the job was queued.

## Queue a job with the change, in one transaction

```elixir
Ash.transact(MyApp.Orders.Order, fn ->
  order = MyApp.Orders.place!(params)
  Oban.insert!(MyApp.Workers.SendReceipt.new(%{order_id: order.id}))
  order
end)
```

Inside an Ash action, queue it from `after_action`, which runs inside the action's
transaction. For a job on the same record, use the AshOban change:
`change run_oban_trigger(:send_receipt)`.

## AshOban trigger: work on every record that matches

A trigger runs an action on each record matching `where`, one job per record at a
time. The scheduler sweeps on `scheduler_cron` (every minute by default; `false`
turns it off), and `AshOban.run_trigger(record, :name)` or `run_oban_trigger` queues
one record straight away.

```elixir
oban do
  triggers do
    trigger :finish do
      action :finish
      where expr(state == :running)
      queue :auction_finishing
      max_attempts 5
      on_error :mark_failed
      worker_module_name MyApp.Auction.Workers.Finish
      scheduler_module_name MyApp.Auction.Schedulers.Finish
    end
  end
end
```

Name the worker and scheduler modules so renaming the trigger does not orphan
queued jobs. `max_attempts` defaults to 1. After the last failed attempt, the
`on_error` update action runs with the error as its `error` argument; make it
change the record so `where` stops matching, or the scheduler keeps re-queuing it.
Autolaunch's `AuctionFinish` and Patchbay's `EventSubscription` are working examples.

- The trigger's action must be an update (or destroy) for `on_error` to run; a
  generic action trigger never calls it.
- An action that calls another service sets `transaction?(false)`, so the call is
  not made inside a database transaction, and `lock_for_update?(false)` on the
  trigger, since the one-job-per-record rule is the lock.
- AshOban logs every failed attempt by default. For outside calls that fail for a
  while as a matter of course, set `log_errors?(false)`: Oban keeps each attempt's
  error on the job, and the final failure is still logged.
- The trigger's uniqueness includes executing jobs, so a job cannot queue a second
  run of itself for the same record: that insert is dropped. Do all the record's
  work in one run (bounded), and let the sweep take up the rest.
- To wake a trigger from another resource's change, queue its sweep with
  `AshOban.schedule(Resource, :trigger)` in that change's `after_action`; the sweep
  is one job however many changes land.

## Ordered delivery to subscribers (webhooks, event feeds)

The pattern for "send each subscriber every event, in order, never skipping one
that failed":

1. **Event log.** Each event is a row written in the same transaction as the change
   that caused it, with a sequence number that is safe to read in commit order.
2. **Subscriber cursor.** Each subscription stores the last sequence number its
   receiver acknowledged, and whether it is active.
3. **One job per subscription.** An AshOban trigger on the subscription with
   `where` "active, unexpired and behind an event of its kind" (an `exists` over the
   event table), or a plain worker unique on the subscription id. The job reads the
   first owed event after the cursor, sends it outside any transaction, and on
   success advances the cursor with a compare-and-set from the value it read. It
   repeats until nothing is owed or a per-run limit is reached.
4. **Wake-up.** When an event row is written, queue the trigger's sweep in the same
   transaction (`AshOban.schedule`), and run the trigger on subscribe and refresh
   (`run_oban_trigger`). The minute sweep catches an event that lands while a job
   for that subscription is already running.
5. **Failure.** Return `{:error, reason}` to retry the same event with backoff.
   When attempts run out, `on_error` stops the subscription and keeps its cursor.
   A refresh switches it back on, and delivery resumes at the same event.
6. **Repeats.** A job can run twice, so the event id is stable and the receiver
   uses it to ignore a repeat. The compare-and-set stops a double run from moving
   the cursor twice.

Oban's job table holds the attempt count, retry time and running state. The
subscription table holds only the cursor, its settings and whether it is active.
There are no lease, attempt or next-attempt columns.

## Testing

```elixir
use Oban.Testing, repo: MyApp.Repo, prefix: "mysite_app"

assert_enqueued worker: MyApp.Workers.SendReceipt, args: %{order_id: order.id}
assert :ok = perform_job(MyApp.Workers.SendReceipt, %{order_id: order.id})
```

For AshOban, `use AshOban.Test, repo: MyApp.Repo` and
`AshOban.Test.schedule_and_run_triggers(MyResource, actor: actor)` run the
scheduler and the jobs it queues.

## Seeing what happens

Oban emits `:telemetry` events for job start, stop and exception; attach them to
the site's metrics (queue depth, failures, run time). Oban Web is a dashboard of
queued, retrying and failed jobs; mount it behind founder-only access.
