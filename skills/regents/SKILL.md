---
name: regents
description: Use regents.sh as the entry point to Regents Labs products and the paired user's account, name claims, staking position, Credits and Points. Explains the benefit to agents and users, Regents protocol CLI and WebMCP reads, shared identity boundaries and sensible account follow-up intervals.
---

# Regents: choose a service and understand the user's account

## Purpose and benefit

Regents is the entry point to the Regents Labs product family and its shared account. It helps an agent route a task to the right service and, when paired, explain the user's account state. The user gets one place to manage agent pairings and inspect account information, without handing an agent their browser session or wallet.

Start with the user's goal:

| Goal | Destination |
| --- | --- |
| Measure or improve a Skill using controlled evaluations | [Techtree](https://techtree.sh/) |
| Find an answer, report a reproducible problem, or contribute a fix | [Patchbay](https://patchbay.help/) |
| Collaborate in rooms, shared workspaces and fleet governance | [Keyfleet](https://keyfleet.ai/) |
| Research token launches and review bids or holdings | [Autolaunch](https://autolaunch.sh/) |
| Establish the agent's own request identity | [SIWA](https://github.com/regents-ai/siwa-server) |
| Review shared account, name claims, Credits, Points or REGENT staking | Stay on regents.sh |

REGENT staking provides exposure to protocol distributions and emissions under its current rules. Describe the user's actual position and published terms; do not promise income or conflate it with Autolaunch token staking. Product discovery is useful even without an account.

## Access and tool selection

Read the linked live guide and capability schema before acting. Inspect `regents --version` and the relevant command's `--help`; examples below were checked against CLI 1.10.2 on 15 October 2026. Public guides may name a different release. A source command, a listed tool and a successful operation are different evidence; report which you verified. Do not silently downgrade or replace an installed client.

Use the agent's existing SIWA identity and current owner pairing for private access. Missing identity or revoked pairing blocks protected work; use the SIWA setup guide with the user's approval. Never borrow cookies, keys or another agent's identity. Signing in and pairing grant no wallet or spending authority.

In a WebMCP-capable browser, open the actual site and inspect its registered tools. Public reads use their declared inputs. For a protected agent tool, call `prepare_agent_request` with its operation and input, sign the exact returned request with the official SIWA client, then call that tool with `{input, request, proof}`. Keep proof private. If browser signing is unavailable, use a verified CLI command or explicitly label an official-client signed HTTP fallback; never invent a tool or bypass a refusal. Send private CLI bodies through JSON stdin, not shell-interpolated prose.

## CLI and WebMCP

The command prefix is **`regents protocol`**; sign-in uses the site name **`regents`**. These are different labels for the same site.

| Read | CLI | WebMCP |
| --- | --- | --- |
| Product family and documentation | Public website/HTTP; no dedicated product-catalog command assumed | `regents_about`, `regents_products`, `regents_product` |
| Agent identity and current pairing | `regents protocol agents whoami --json` | `regents_agent_whoami` |
| Account display and ENS name | `regents protocol account show --json` | `regents_account` |
| Name claims | `regents protocol account claims --json` | `regents_claims` |
| Staking position | `regents protocol staking position --json` | `regents_stake_position` |
| Credits balance | `regents protocol account balances --json` | `regents_credits_balance` |
| Credits ledger | `regents protocol account credits-history --json` | `regents_credits_history` |
| Current spending grant and usage | `regents protocol account budget --json` | `regents_credits_budget` |
| Points and allowances | `regents protocol account points --json` | `regents_points_summary` |

For tool discovery, `show_regents_webmcp_tools` and the equivalent product cards summarize published tools. They do not prove another site's current browser registration; inspect that site before using it.

## Account review workflow

1. Resolve the user's question and private report destination. For product selection, read public summaries and recommend the service that fits; do not sign in unnecessarily.
2. For private review, probe identity and pairing first. If setup is requested, use `regents auth login --site regents` only with the intended signer; it can create a key when none exists. Pair only using an owner-issued code and the current guide. Do not replace an existing identity.
3. Read only the relevant account surfaces. They resolve the owner from current pairing; a supplied wallet or account ID cannot select someone else's account. Staking covers the verified primary wallet; claims may cover verified owner wallets. State actual coverage.
4. Page claims with `next`; page Credits history with `pagination.next_cursor` in the checked live contract. Send `{}` initially for the signed HTTP POST reads, then `{"after":"CURSOR"}`. The CLI exposes `--after`; older help may call it `next`. If a response differs, inspect its current contract rather than guessing a cursor or declaring the history complete.
5. Compare timestamped snapshots. Keep Points, Credits, held Credits, claim records and wallet assets separate. An unavailable value is unknown, not zero. A Points read earns nothing; a budget read enables nothing.
6. Summarize changes privately with links and freshness. Name claims here are records, not token claims. `regents protocol agents me` records latest contact and is a check-in write; use `whoami` for a passive identity probe.

Account security, pairing management, funding, grants, name actions, staking, unstaking, compounding and claims remain owner actions. These agent reads never approve or execute them. Offer a relevant owner-page link when a decision is needed; do not imply the agent has a transaction command.

## Follow-up contract

The intervals below are suggested starting points, not service promises or permission to run forever. A request to read once ends after one report. Create or update a recurring job only when the user asks to watch, monitor or check back, using the host's supported scheduler. Record the scope, interval, stop condition, private destination and permitted actions; reuse a matching job. A monitoring request authorizes checks and alerts, not posts, spending, compute or wallet signatures.

Prefer available events and returned deadlines over fixed polling. Save cursors, record IDs and timestamped snapshots privately, scoped to this agent and owner. Consume all pages before advancing the checkpoint; never discard unread events. On a reset or expired cursor, rebaseline and disclose any gap. Respect `Retry-After`, back off on repeated failures, and stop protected work on revoked access. Notify only for a meaningful change, a decision or a blocker; avoid repeated unchanged alerts. Never say a schedule exists until the host confirms it.

## When to check again

| Use | Suggested interval | Report when |
| --- | --- | --- |
| Choosing a service | On demand | The user's goal changes; there is no need to keep polling a directory. |
| Following product changes | Weekly; daily during an announced rollout | A relevant capability or availability change appears. Verify on the destination site. |
| Credits and budget during authorized paid work | Before each new spend decision; every 30–60 minutes if monitoring a live task | Budget becomes insufficient, a hold changes, or a relevant ledger entry appears. A read never grants spending authority. |
| Account, name claims and Points | Daily when requested | A meaningful state change or access problem appears. Do not farm check-ins or Points. |
| REGENT staking position and distributions | Daily; after a user-confirmed wallet action, refresh once and follow the returned state | A new claimable amount, position change or data failure. No automatic claim or reinvestment. |

Pairing codes are single-use and currently expire after ten minutes; this is a setup deadline, not a monitoring interval. On revocation, stop private checks and tell the user once.

Return the service recommendation or account changes, coverage, evidence time, any owner action needed, and the confirmed next check if one exists.

## Current references

- [Product directory](https://regents.sh/), [agent access](https://regents.sh/agents.md), [WebMCP schemas](https://regents.sh/capabilities), [HTTP discovery](https://regents.sh/llms.txt), [owner account](https://regents.sh/account).
- [Regents CLI](https://github.com/regents-ai/regents-cli), [SIWA setup](https://siwa.regents.sh/skill.md).

Guides and live manifests were read on 15 October 2026; CLI help was checked. Private reads and native browser execution were not tested during authoring. Recheck current grants, response shapes and deployment availability.
