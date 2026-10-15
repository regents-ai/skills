# How each site watches the chain today

Checked 2026-09-26; Keyfleet's row 2026-09-27. Read Autolaunch and Patchbay with `git show origin/main:<path>`; their
local checkouts lag behind.

| Site | Watcher | Row identity | Pages hear through |
| --- | --- | --- | --- |
| Keyfleet (`main` 8f9629f) | `Keyfleet.Chain.Poller` and `Scanner`, at `latest`, cursor per fleet. Sent wallet steps are read by `KeyfleetWeb.OnchainSteps` through `Keyfleet.Chain.Client` at `latest` every 2 s; nothing stored | `[:transaction_hash, :log_index]` | Plain `Phoenix.PubSub` topics (`Keyfleet.Proposals.topic/1`, `Keyfleet.Keys.topic/1`) |
| Autolaunch (`origin/main` 1b0e56c) | `Autolaunch.Indexer`, reading `safe` and `finalized` | `[:chain_id, :block_hash, :log_index]` | Ash `pub_sub` on the listing resources, re-read at most once a second (`AutolaunchWeb.LiveListings`) |
| Regents | None; staking reads the chain directly (`AshPlatform.Staking.RpcClient`) | | |
| Patchbay | None | | |
| Techtree | None | | |

## Models

- The watcher: Keyfleet, `platform/lib/keyfleet/chain/` (`scanner.ex`, `cursor.ex`,
  `changes/record_once.ex`, `poller.ex`), its stub client
  `test/support/chain_stub_client.ex`, and the vote row's `:record` action in
  `lib/keyfleet/proposals/vote.ex`.
- The page: Autolaunch, `platform/lib/autolaunch/auction.ex` (`pub_sub`),
  `platform/lib/autolaunch/auction_activity.ex` (notices sent after a manual transaction
  commits) and `platform/lib/autolaunch_web/live/live_listings.ex` (subscribe when
  connected, one re-read a second).

## Where sites differ from this skill

Each is a backlog item for that site.

1. **Autolaunch waits for `safe` and `finalized`.** The indexer reads both
   (`indexer/chain.ex:36`, `indexer/handler.ex:97-98`), and `Rpc.safe_block/1` is used by
   `regent_facts.ex:101`, `subject_wallet_rpc_client.ex:35` and
   `treasury_chain_client.ex:81`. Rule 1 says `latest`.
2. **Autolaunch's ledger writes rows with `Repo.insert_all`** (`indexer/ledger.ex:517`),
   past Ash's actions, checks and notices.
3. **Autolaunch keys logs by block hash**, so a reorg leaves the old log as a second row
   instead of stopping the watcher.
4. **Keyfleet's rows carry no `chain_id`** in their identity, and its pages hear through
   plain PubSub topics rather than the resource's notifier.
