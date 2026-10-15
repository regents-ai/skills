---
name: autolaunch
description: Use autolaunch.sh to understand Revstake and Memestock launches, research auctions, review the paired user's bids and claimable tokens, and watch verified price changes. Covers agent/user benefits, WebMCP and Regents CLI reads and quotes, user-controlled transactions, and deadline-aware monitoring intervals.
---

# Autolaunch: understand launches and track the user's positions

## Purpose and benefit

Autolaunch organizes token launches, auctions and related holdings. Revstake launches connect agent tokens with revenue distributions for token stakers; Memestock launches pair a token with a tokenized stock asset. Current creation policy is Base-only for Revstake, with Memestock auctions on Base or Robinhood. Existing positions still need their actual chain-specific terms checked.

For the agent, public auction data and private portfolio reads provide a structured way to answer what is live, what the user bid on, and what may be claimable. For the user, this reduces missed deadlines and separates account facts from promotional claims. Explain price units, launch state and evidence freshness. Neither an auction, a treasury report nor staking guarantees a return.

Use this skill for research, quotes, draft metadata and monitoring. Wallet bidding, trading, claiming, staking and settlement remain user-controlled in the checked agent contract.

## Access and tool selection

Read the linked live guide and capability schema before acting. Inspect `regents --version` and the relevant command's `--help`; examples below were checked against CLI 1.10.2 on 15 October 2026. Public guides may name a different release. A source command, a listed tool and a successful operation are different evidence; report which you verified. Do not silently downgrade or replace an installed client.

Use the agent's existing SIWA identity and current owner pairing for private access. Missing identity or revoked pairing blocks protected work; use the SIWA setup guide with the user's approval. Never borrow cookies, keys or another agent's identity. Signing in and pairing grant no wallet or spending authority.

In a WebMCP-capable browser, open the actual site and inspect its registered tools. Public reads use their declared inputs. For a protected agent tool, call `prepare_agent_request` with its operation and input, sign the exact returned request with the official SIWA client, then call that tool with `{input, request, proof}`. Keep proof private. If browser signing is unavailable, use a verified CLI command or explicitly label an official-client signed HTTP fallback; never invent a tool or bypass a refusal. Send private CLI bodies through JSON stdin, not shell-interpolated prose.

## CLI and WebMCP map

Prefix CLI entries with `regents autolaunch`. Read input schemas before substituting real IDs.

| Goal | CLI | WebMCP |
| --- | --- | --- |
| Find auctions | `auctions list` | `autolaunch_auctions` |
| Read one auction | `auction ID` | `autolaunch_auction` |
| Estimate a hypothetical bid | `bids quote --auction UUID --amount DECIMAL --max-price DECIMAL` | `autolaunch_bid_quote` |
| Browse tokens | `tokens list` | `autolaunch_tokens` |
| Read one token | No dedicated command verified; public HTTP `GET /api/v1/tokens/ID` | `autolaunch_token` |
| Read a treasury report | `treasury security ADDRESS` | `autolaunch_treasury` |
| Check paired identity | `agents whoami` | `agent_whoami` |
| Read owner positions | `positions` | `autolaunch_my_positions` |
| Read/save text metadata | `drafts revstake show/save`, `drafts memestock show/save` | `autolaunch_revstake_draft`, `autolaunch_revstake_draft_save`, `autolaunch_memestock_draft`, `autolaunch_memestock_draft_save` |
| Read shared account | `account balances`, `account credits-history`, `account points` | `account_balances`, `account_credits_history`, `account_points` |

`agents status` / `agent_status` records latest contact; it is not a passive identity probe. Metadata save requires authority and an open product gate; it does not submit a launch or accept treasury, wallet, stock or chain settings.

## Auctions, bids and claims

1. Resolve the watchlist, paired owner, relevant chains and private reporting destination. Read public auctions first. Filter using actual CLI options and page with `pagination.next_cursor` while more remain. Follow each record's canonical URL; do not manufacture auction page paths.
2. Read the selected auction's state, quote token/address/decimals, minimum, clearing price, stored-data time and `estimated_end_at` when returned. An estimated end time may change and does not establish finality. Auction clearing price is denominated in its quote token; it is not a live USD market price.
3. A bid quote uses stored figures and places nothing. Report warnings and the assumptions, including amount and maximum price. Never treat an estimate as an executable quote or successful bid.
4. For private positions, probe current pairing and ensure the owner has signed in to Autolaunch. Read `positions`; it covers the owner's verified primary wallet, not every linked wallet. Report bids, holdings, staked and claimable amounts only where returned. Keep chain, token and units attached to values. If the chain read fails, report unavailable, not an empty portfolio.
5. Track each bid using its identifiers and returned page links, amounts, maximum price and permitted-action/status fields. `claim_ready`, `withdraw_ready` or `can` are eligibility information, not permission or confirmation that value moved.
6. For a claim or new bid, show the exact position and canonical owner page. Explain the state and requested action. The checked agent interface exposes no command to execute it; let the user's wallet handle it. After the user supplies a confirmed transaction, refresh the receipt and position. Do not claim completion from a submitted or pending transaction, auto-resend it or reconstruct a pending-operation queue.

Metadata draft edits are separate from this read-only loop. With an explicit edit request, read first, save only permitted strings, and read back; a lost response calls for a read before retry. Respect `prelaunch_read_only` and other denials.

## Price movement without misleading comparisons

Token detail can include a stored price and a nullable recording time. Label it a stored observation, not a live quote. For a market-price alert, agree on chain, token contract, pool/source, quote currency, maximum data age, baseline period and movement threshold. Use an approved timestamped source and compare like with like. Token symbols alone are not identifiers.

For a valid positive baseline, percentage change is `100 × (current / baseline − 1)`. A missing/zero baseline, unknown timestamp, different quote asset or stale observation means no defensible movement percentage. Do not compare an auction clearing price with a secondary-market pool price. Avoid duplicate alerts until a new threshold crossing or the user's reset condition. With no agreed threshold, report observations and request one before enabling threshold alerts; never choose trades on the user's behalf.

## Follow-up contract

The intervals below are suggested starting points, not service promises or permission to run forever. A request to read once ends after one report. Create or update a recurring job only when the user asks to watch, monitor or check back, using the host's supported scheduler. Record the scope, interval, stop condition, private destination and permitted actions; reuse a matching job. A monitoring request authorizes checks and alerts, not posts, spending, compute or wallet signatures.

Prefer available events and returned deadlines over fixed polling. Save cursors, record IDs and timestamped snapshots privately, scoped to this agent and owner. Consume all pages before advancing the checkpoint; never discard unread events. On a reset or expired cursor, rebaseline and disclose any gap. Respect `Retry-After`, back off on repeated failures, and stop protected work on revoked access. Notify only for a meaningful change, a decision or a blocker; avoid repeated unchanged alerts. Never say a schedule exists until the host confirms it.

## When to check again

| Use | Suggested interval | Deadline or event handling |
| --- | --- | --- |
| Browsing new launches | Every 6–24 hours | Notify only for launches matching the user's criteria. |
| Watching an active auction or existing bid | Every 15–30 minutes; every 5 minutes in the final hour if requested | Refresh changed end times, bid standing and warnings. Offer reminders 1 hour and 10 minutes before the current end; no automatic bid. |
| Auction just ended / awaiting final state | Every 5–15 minutes initially; hourly if still pending | Wait for a confirmed terminal state and actual position eligibility. Ended is not necessarily settled or claimable. |
| Token claims or refunds | Check when eligibility opens, then daily while outstanding | Alert once when newly ready; use the actual deadline if one exists. Do not invent an expiry or repeatedly urge a claim. Stop once confirmed complete or dismissed. |
| Price movements | Every 15–60 minutes for an active watch; daily for a portfolio summary | Honor the user's threshold and source freshness. A 5-minute watch needs a source that updates that often and explicit user interest. |
| Confirmed user wallet action | Refresh once, then every 1–5 minutes only until indexed or a bounded timeout | Report a chain/indexing discrepancy rather than treating it as a reason to resend. |

Return private positions with coverage and timestamps, changed auction/claim state, valid price comparisons, relevant links and any owner decision. Never publish a portfolio to a room or forum.

## Current references

- [Product](https://autolaunch.sh/), [agent permissions](https://autolaunch.sh/agents.md), [WebMCP schemas](https://autolaunch.sh/capabilities), [documentation](https://autolaunch.sh/docs), [HTTP discovery](https://autolaunch.sh/llms.txt).
- [Regents CLI](https://github.com/regents-ai/regents-cli).

Checked 15 October 2026: live guides/manifests, installed help and public auction reads. Private portfolio access, native signed browser execution and wallet flows were not exercised. Read current deployment gates and returned state at use time.
