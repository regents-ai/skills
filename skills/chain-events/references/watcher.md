# The watcher

The code here compiles against Ash 3.33, AshPostgres 2.13 and Phoenix LiveView 1.2.11.
It was not run against a database; Keyfleet's reader, which it follows, is the tested
version. `MyApp` stands for the site's module prefix, and `Actors.System` (whose `role: :system`
the policies check) is the template's own. The example watches ERC-20 `Transfer` logs.

## Files

| File | Holds |
| --- | --- |
| `lib/my_app/chain/client.ex` | The behaviour every chain read goes through |
| `lib/my_app/chain/rpc_client.ex` | The behaviour over JSON-RPC with Req, reading `latest` |
| `lib/my_app/chain.ex` | The domain and its code interfaces |
| `lib/my_app/chain/cursor.ex` | How far each contract has been read |
| `lib/my_app/chain/<event>.ex` | One resource per kind of event row |
| `lib/my_app/chain/changes/record_once.ex` | The check that a row read again matches |
| `lib/my_app/chain/scanner.ex` | One pass (follow Keyfleet's) |
| `lib/my_app/chain/poller.ex` | Runs passes |
| `test/support/chain_stub_client.ex` | The chain a test describes |

## The client

```elixir
defmodule MyApp.Chain.Client do
  @moduledoc """
  The chain as the app reads it, always at `latest`: a JSON-RPC node in
  production, a stand-in held by the test process in tests.
  """

  @type head :: %{number: non_neg_integer(), hash: String.t(), timestamp: DateTime.t()}

  @callback chain_id() :: {:ok, pos_integer()} | {:error, term()}
  @callback head() :: {:ok, head()} | {:error, term()}
  @callback block_hash(non_neg_integer()) :: {:ok, String.t()} | {:error, term()}
  @callback logs(addresses :: [String.t()], topic0s :: [String.t()], from :: non_neg_integer(), to :: non_neg_integer()) ::
              {:ok, [map()]} | {:error, :too_many_results | term()}
  @callback transaction(chain :: map(), hash :: String.t()) :: {:ok, map() | nil} | {:error, term()}
  @callback receipt(chain :: map(), hash :: String.t()) :: {:ok, map() | nil} | {:error, term()}

  def configured, do: Application.fetch_env!(:my_app, MyApp.Chain)[:client]
end
```

The JSON-RPC client asks for `"latest"` wherever a block tag goes and lowercases every
hash and address it returns. `logs/4` answers `{:error, :too_many_results}` when the node
refuses a range for size, so the pass can halve it. Keep the node's URL in an environment
variable and never log it; provider URLs carry keys.

`transaction/2` and `receipt/2` serve `onchain-buttons`' check: `RegentChain.Outcome`
calls them with the review's chain (`chain_id`, `name`, `rpc_url`) and the hash. They
read through the site's own node for `chain_id`, not the review's `rpc_url`, which is the
public address wallets are given. A watcher that only reads logs may leave them out of
its client.

## Domain and cursor

```elixir
defmodule MyApp.Chain do
  use Ash.Domain, otp_app: :my_app

  resources do
    resource MyApp.Chain.Cursor do
      define :cursor, action: :read, get_by: [:chain_id, :name]
      define :open_cursor, action: :open
      define :advance_cursor, action: :advance
      define :stop_cursor, action: :stop, args: [:block]
    end

    resource MyApp.Chain.Transfer do
      define :record_transfer, action: :record
      define :transfers_for, action: :for_holder, args: [:holder]
    end
  end
end
```

```elixir
defmodule MyApp.Chain.Cursor do
  @moduledoc """
  How far one contract's events have been read on one chain. Base confirms a
  block in about two seconds and nothing here waits longer. A reading that
  disagrees with the record sets `rescan_from` and stops the watcher until
  someone corrects the record by hand.
  """
  use Ash.Resource,
    domain: MyApp.Chain,
    data_layer: AshPostgres.DataLayer,
    authorizers: [Ash.Policy.Authorizer]

  postgres do
    table "chain_cursors"
    repo MyApp.Repo
  end

  actions do
    defaults [:read]

    create :open do
      accept [:chain_id, :name, :next_block]
      upsert? true
      upsert_identity :unique_cursor
      upsert_fields []
      upsert_condition expr(false)
      return_skipped_upsert? true
    end

    # Moves only a cursor still where this pass found it and not stopped, so a
    # second machine's pass or a hand correction is never undone.
    update :advance do
      accept [:next_block, :head_block, :head_block_hash, :observed_at]
      require_attributes [:next_block, :head_block, :head_block_hash, :observed_at]
      argument :from, :integer, allow_nil?: false
      validate MyApp.Chain.Validations.CursorUnmoved
    end

    # Keeps the earliest block where the chain disagreed.
    update :stop do
      accept []
      require_atomic? true
      argument :block, :integer, allow_nil?: false, constraints: [min: 0]

      change atomic_update(
               :rescan_from,
               expr(if is_nil(rescan_from) or rescan_from > ^arg(:block), do: ^arg(:block), else: rescan_from)
             )
    end
  end

  policies do
    policy action_type(:read) do
      authorize_if always()
    end

    policy action([:open, :advance, :stop]) do
      authorize_if actor_attribute_equals(:role, :system)
    end
  end

  attributes do
    uuid_primary_key :id
    attribute :chain_id, :integer, allow_nil?: false, public?: true, constraints: [min: 1]
    attribute :name, :string, allow_nil?: false, public?: true
    # The first block not read yet.
    attribute :next_block, :integer, allow_nil?: false, public?: true, constraints: [min: 0]
    attribute :head_block, :integer, public?: true, constraints: [min: 0]
    attribute :head_block_hash, :string, public?: true, constraints: [match: ~r/\A0x[0-9a-f]{64}\z/]
    attribute :observed_at, :utc_datetime_usec, public?: true
    attribute :rescan_from, :integer, public?: true, constraints: [min: 0]
  end

  identities do
    identity :unique_cursor, [:chain_id, :name]
  end
end
```

The cursor check runs inside the `UPDATE`, so a pass holding an old copy of the cursor
gets `StaleRecord` and writes nothing. It is a validation, not
`change filter(expr(...))`, because Ash 3.33.11 drops that filter from a single
record's atomic update (see `ash-data`).

```elixir
defmodule MyApp.Chain.Validations.CursorUnmoved do
  use Ash.Resource.Validation

  @impl true
  def atomic(changeset, _opts, _context) do
    from = Ash.Changeset.get_argument(changeset, :from)

    {:atomic, [:next_block, :rescan_from],
     expr(next_block != ^from or not is_nil(rescan_from)),
     expr(error(Ash.Error.Changes.StaleRecord, %{resource: "cursor", filter: %{next_block: ^from}}))}
  end
end
```

Clearing `rescan_from` after a hand fix is an operator step: add a `:clear` update the
system actor alone may run, a release command that runs it, and a short runbook in the
site's docs, as Keyfleet has in `docs/chain-reader.md`. See
[operator actions](../../ash-security/references/operator-actions.md) for the command
and the record it leaves.

## The event row

```elixir
defmodule MyApp.Chain.Transfer do
  @moduledoc "One `Transfer` log, exactly as the chain gave it. Never rewritten."
  use Ash.Resource,
    domain: MyApp.Chain,
    data_layer: AshPostgres.DataLayer,
    authorizers: [Ash.Policy.Authorizer],
    notifiers: [Ash.Notifier.PubSub]

  @address ~r/\A0x[0-9a-f]{40}\z/
  @hash ~r/\A0x[0-9a-f]{64}\z/

  postgres do
    table "chain_transfers"
    repo MyApp.Repo
  end

  pub_sub do
    module Phoenix.PubSub
    name MyApp.PubSub
    prefix "transfers"
    transform fn notification -> {:transfers_changed, notification.data.to} end
    publish :record, [:to]
  end

  actions do
    defaults [:read]

    read :for_holder do
      argument :holder, :string, allow_nil?: false, constraints: [match: @address]
      filter expr(to == ^arg(:holder) or from == ^arg(:holder))
      prepare build(sort: [block_number: :desc, log_index: :desc])
    end

    create :record do
      accept [:chain_id, :transaction_hash, :log_index, :block_number, :block_hash, :token, :from, :to, :amount]
      upsert? true
      upsert_identity :unique_chain_event
      upsert_fields []
      upsert_condition expr(false)
      return_skipped_upsert? true
      change {MyApp.Chain.Changes.RecordOnce, identity: [:chain_id, :transaction_hash, :log_index]}
    end
  end

  policies do
    policy action_type(:read) do
      authorize_if always()
    end

    policy action(:record) do
      authorize_if actor_attribute_equals(:role, :system)
    end
  end

  attributes do
    uuid_primary_key :id
    attribute :chain_id, :integer, allow_nil?: false, public?: true, constraints: [min: 1]
    attribute :transaction_hash, :string, allow_nil?: false, public?: true, constraints: [match: @hash]
    attribute :log_index, :integer, allow_nil?: false, public?: true, constraints: [min: 0]
    attribute :block_number, :integer, allow_nil?: false, public?: true, constraints: [min: 0]
    attribute :block_hash, :string, allow_nil?: false, public?: true, constraints: [match: @hash]
    attribute :token, :string, allow_nil?: false, public?: true, constraints: [match: @address]
    attribute :from, :string, allow_nil?: false, public?: true, constraints: [match: @address]
    attribute :to, :string, allow_nil?: false, public?: true, constraints: [match: @address]
    # Raw token units, exactly as the log carried them.
    attribute :amount, :decimal, allow_nil?: false, public?: true, constraints: [min: 0]
    create_timestamp :inserted_at
  end

  identities do
    identity :unique_chain_event, [:chain_id, :transaction_hash, :log_index]
  end
end
```

- The identity carries `chain_id`, so the same table can hold Base and Robinhood Chain.
- `upsert_fields []` with `upsert_condition expr(false)` means a row read again changes
  nothing; `return_skipped_upsert? true` hands back the stored row for the check below.
- The `for_holder` read is what pages call. Add reads for pages; do not read the table
  from a page with raw Ecto.
- Aggregates over raw amounts (a balance, a total) are calculations or aggregates on the
  resource, still in raw units.

## Recording once

```elixir
defmodule MyApp.Chain.Changes.RecordOnce do
  @moduledoc """
  Makes a row from one chain event once. The event is held until commit; read
  again, it must match the row already made, or the action is refused and the
  watcher stops at that block.
  """
  use Ash.Resource.Change

  @impl true
  def change(changeset, opts, _context) do
    changeset
    |> Ash.Changeset.before_action(&hold(&1, opts))
    |> Ash.Changeset.after_action(&same_as_recorded/2)
  end

  defp hold(changeset, opts) do
    key = [inspect(changeset.resource) | Enum.map(opts[:identity], &Ash.Changeset.get_attribute(changeset, &1))]
    MyApp.Repo.query!("SELECT pg_advisory_xact_lock(hashtextextended($1, 0))", [Jason.encode!(key)])
    changeset
  end

  defp same_as_recorded(changeset, row) do
    fields = Map.keys(changeset.attributes) -- Ash.Resource.Info.primary_key(changeset.resource)

    if Enum.all?(fields, &same?(Map.fetch!(row, &1), Map.fetch!(changeset.attributes, &1))),
      do: {:ok, row},
      else: {:error, MyApp.Chain.Diverged.exception([])}
  end

  defp same?(%Decimal{} = recorded, %Decimal{} = read), do: Decimal.equal?(recorded, read)
  defp same?(recorded, read), do: recorded == read
end
```

```elixir
defmodule MyApp.Chain.Diverged do
  @moduledoc "A row read again from the chain does not match the one already made."
  use Splode.Error, fields: [], class: :invalid
  def message(_error), do: "conflicts with the record already made from the chain"
end
```

The advisory lock makes two passes recording the same event take turns, so the second
sees the first's row. A row that reads differently comes back as `Diverged`, and the pass
stops the cursor.

## Committing a stretch

```elixir
defmodule MyApp.Chain.Piece do
  @moduledoc """
  Records one stretch of blocks: its rows and the cursor move in one
  transaction, and the page hears about new rows only after it commits.
  """
  alias MyApp.Chain

  @system %MyApp.Actors.System{}

  def commit(cursor, rows, to, head) do
    MyApp.Repo.transact(fn ->
      with {:ok, notifications} <- record(rows),
           {:ok, cursor} <-
             Chain.advance_cursor(
               cursor,
               %{from: cursor.next_block, next_block: to + 1, head_block: head.number,
                 head_block_hash: head.hash, observed_at: DateTime.utc_now()},
               actor: @system
             ),
           do: {:ok, {cursor, notifications}}
    end)
    |> case do
      {:ok, {cursor, notifications}} ->
        Ash.Notifier.notify(notifications)
        {:ok, cursor}

      {:error, error} ->
        if diverged?(error), do: stop(cursor, cursor.next_block), else: {:error, error}
    end
  end

  defp record(rows) do
    Enum.reduce_while(rows, {:ok, []}, fn row, {:ok, notifications} ->
      case Chain.record_transfer(row, actor: @system, return_notifications?: true) do
        {:ok, _row, more} -> {:cont, {:ok, more ++ notifications}}
        {:error, error} -> {:halt, {:error, error}}
      end
    end)
  end

  defp diverged?(%{errors: errors}), do: Enum.any?(errors, &match?(%MyApp.Chain.Diverged{}, &1))
  defp diverged?(_error), do: false

  defp stop(cursor, block) do
    Chain.stop_cursor!(cursor, block, actor: @system)
    {:stopped, block}
  end

  @doc "A raw `Transfer` log as a row: lowercase hex, amount in raw units."
  def row(chain_id, %{"topics" => [_signature, from, to], "data" => "0x" <> amount} = log) do
    %{
      chain_id: chain_id,
      transaction_hash: String.downcase(log["transactionHash"]),
      log_index: quantity(log["logIndex"]),
      block_number: quantity(log["blockNumber"]),
      block_hash: String.downcase(log["blockHash"]),
      token: String.downcase(log["address"]),
      from: topic_address(from),
      to: topic_address(to),
      amount: Decimal.new(String.to_integer(amount, 16))
    }
  end

  defp topic_address("0x" <> <<_padding::binary-size(24), address::binary-size(40)>>),
    do: "0x" <> String.downcase(address)

  defp quantity("0x" <> digits), do: String.to_integer(digits, 16)
end
```

- `Repo.transact/1` wraps the rows and the cursor; if either fails, neither is saved.
- `return_notifications?: true` keeps Ash from sending notices for rows that might still
  roll back; `Ash.Notifier.notify/1` sends them once the transaction has committed.
- A stale cursor (another pass moved it) fails `advance` and the pass ends; the next one
  starts from where the cursor now stands.

## One pass

Write the pass after `Keyfleet.Chain.Scanner`
(`repos/keyfleet/platform/lib/keyfleet/chain/scanner.ex`), which the rules follow:

1. A stopped cursor returns `{:stopped, block}` and reads nothing.
2. Read the head.
3. Read the last 30 recorded blocks again: every recorded row's block must still have the
   same hash (`block_hash/1`), and every log read again goes through `record`, which
   refuses a row that differs. Record a log that was not there before; it is new history.
4. Read forward from `next_block` to the head in stretches, committing each with
   `Piece.commit/4` before asking for the next.
5. Never ask for blocks above the head this pass read; a node that is behind makes a
   shorter pass, never missing history.

## The poller

```elixir
defmodule MyApp.Chain.Poller do
  @moduledoc "Runs a scanner pass every few seconds; a failed pass is retried later, never fatal."
  use GenServer
  require Logger

  @max_delay 60_000

  def start_link(opts), do: GenServer.start_link(__MODULE__, opts)

  @impl true
  def init(opts) do
    send(self(), :tick)
    {:ok, Map.new(opts) |> Map.merge(%{client: MyApp.Chain.Client.configured(), delay: opts[:interval]})}
  end

  @impl true
  def handle_info(:tick, state) do
    cursor = MyApp.Chain.cursor!(state.chain_id, state.name)

    case MyApp.Chain.Scanner.pass(state.client, cursor) do
      :ok ->
        Process.send_after(self(), :tick, state.interval)
        {:noreply, %{state | delay: state.interval}}

      {:stopped, block} ->
        Logger.error("#{state.name} stopped at block #{block}: the chain disagrees with the record")
        {:noreply, state}

      {:error, reason} ->
        delay = min(state.delay * 2, @max_delay)
        Logger.warning("#{state.name} read failed, retrying in #{delay} ms: #{inspect(reason)}")
        Process.send_after(self(), :tick, delay)
        {:noreply, %{state | delay: delay}}
    end
  end
end
```

Start one per contract from the site's supervisor, with `chain_id`, `name` and
`interval` (4 seconds on Base). Before its first pass it must check `client.chain_id()`
equals the cursor's chain and refuse to read at all when it does not, as Keyfleet's
poller does on its first tick. Open the cursor at the
contract's deployment block with `Chain.open_cursor/2`, which leaves an existing one
alone.

## The page

```elixir
defmodule MyAppWeb.HoldingsLive do
  use Phoenix.LiveView

  @impl true
  def mount(_params, _session, socket) do
    holder = socket.assigns.current_wallet
    if connected?(socket), do: Phoenix.PubSub.subscribe(MyApp.PubSub, "transfers:#{holder}")
    {:ok, socket |> assign(holder: holder, reread?: false) |> load()}
  end

  @impl true
  def render(assigns) do
    ~H"""
    <ul id="transfers" phx-update="stream">
      <li :for={{id, transfer} <- @streams.transfers} id={id}>{transfer.amount}</li>
    </ul>
    """
  end

  # A notice is only a hint to read again; many in one second make one read.
  @impl true
  def handle_info({:transfers_changed, _holder}, %{assigns: %{reread?: true}} = socket), do: {:noreply, socket}

  def handle_info({:transfers_changed, _holder}, socket) do
    Process.send_after(self(), :reread, 1_000)
    {:noreply, assign(socket, reread?: true)}
  end

  def handle_info(:reread, socket), do: {:noreply, socket |> assign(reread?: false) |> load()}

  defp load(socket) do
    transfers = MyApp.Chain.transfers_for!(socket.assigns.holder, actor: socket.assigns.current_scope)
    stream(socket, :transfers, transfers, reset: true)
  end
end
```

- Subscribe only when connected; the first render already read the rows.
- A notice starts one read a second later, and more notices in that second join it.
- Every read goes through the code interface with the viewer's actor; the notice
  carries no row data to show.
- For the "catching up" notice, read the cursor through a `fresh?` calculation
  (`observed_at` within 120 seconds and `head_block - next_block` within 300 blocks, as
  Keyfleet's cursor has) and show plain words: "Catching up with the chain. Recent
  activity may take a moment to appear."

## Tests

- **Stub client** holding the chain in the test process (`Process.put`), as
  `test/support/chain_stub_client.ex` in Keyfleet does: a head, raw logs, block hashes,
  and the requests it was asked, so a test can check the ranges asked for.
- **A pass** against the stub: rows appear once; the same pass twice changes nothing; a
  log that reads differently stops the cursor at its block; a changed block hash stops
  it; a refused range is asked for in halves.
- **The page**: a notice leads to one re-read showing the new row. Send the notice with
  `Ash.Notifier.notify/1` or by running the pass in the test.
- Capture expected warnings with `ExUnit.CaptureLog` so the output stays clean.
- **Against a real chain**: anvil tests tagged `:external`, left out of the default run.
