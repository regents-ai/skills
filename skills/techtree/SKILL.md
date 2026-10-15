---
name: techtree
description: Use techtree.sh to discover and evaluate agent Skills, compare baseline and candidate runs, inspect published Results and Wallet Bench evidence, and monitor relevant changes. Explains user and agent benefits, local Regents CLI workflows, browser WebMCP reads, publication limits and check-in intervals.
---

# Techtree: measure whether a Skill helps

## Purpose and benefit

Techtree helps a person decide whether an agent Skill improves real work. It provides fixed task sets called Climbs, tools to build tasks from a Skill, baseline-versus-candidate comparisons, and public Result bundles. For the agent, this replaces guessing with task-level evidence and a controlled improvement loop. For the user, it makes regressions, costs and limitations visible before adopting a change.

Use it to compare a new Skill against no Skill or an earlier version, inspect a published result, or follow evidence about a harness or wallet tool. Match the task, model, harness and evaluation conditions to the user's situation. A good result on one task set is not a universal capability claim. Published results are participant-attested and integrity-checked; neither that label nor a rerun establishes independent reproduction.

## Access and tool selection

Read the linked live guide and capability schema before acting. Inspect `regents --version` and the relevant command's `--help`; examples below were checked against CLI 1.10.2 on 15 October 2026. Public guides may name a different release. A source command, a listed tool and a successful operation are different evidence; report which you verified. Do not silently downgrade or replace an installed client.

Use the agent's existing SIWA identity and current owner pairing for private access. Missing identity or revoked pairing blocks protected work; use the SIWA setup guide with the user's approval. Never borrow cookies, keys or another agent's identity. Signing in and pairing grant no wallet or spending authority.

In a WebMCP-capable browser, open the actual site and inspect its registered tools. Public reads use their declared inputs. For a protected agent tool, call `prepare_agent_request` with its operation and input, sign the exact returned request with the official SIWA client, then call that tool with `{input, request, proof}`. Keep proof private. If browser signing is unavailable, use a verified CLI command or explicitly label an official-client signed HTTP fallback; never invent a tool or bypass a refusal. Send private CLI bodies through JSON stdin, not shell-interpolated prose.

## CLI: run experiments on the user's machine

Techtree's evaluation engine is local. A browser-only agent can research and hand off a recipe, but opening the site does not start an experiment.

1. Inspect `regents techtree doctor`, `regents techtree forge --help` and the current [agent guide](https://techtree.sh/agents.md). Check prerequisites before installing engines or changing the user's environment.
2. Run `regents techtree forge inspect-skill PATH`. This reads the Skill without executing it. Explain the files and any refusal.
3. Prepare tasks with `regents techtree forge plan SOURCE_ID --provider PROVIDER --model MODEL`. Show the returned review of provider, transmitted data and limits. Follow its exact next command only after the user approves that review. Construction and acceptance have their own returned steps; do not synthesize approval flags.
4. Compare the same collection and provider/model using `forge run --arm baseline --collection COLLECTION_ID --provider PROVIDER --model MODEL` and `forge run --arm candidate --collection COLLECTION_ID --provider PROVIDER --model MODEL --skill PATH`. Prefix both with `regents techtree`. Add an earlier Skill to the baseline only when that is the intended comparison. Each model-spending review needs the user's approval.
5. Read `regents techtree forge status ID`; compare finished arms with `regents techtree forge compare BASELINE_RUN_ID CANDIDATE_RUN_ID`. Report improved, regressed, mixed, unchanged or inconclusive as actually returned. After revising from training evidence, use held-out results to judge the revision; do not leak held-out tasks into improvement context.
6. For fixed Climbs, inspect `regents techtree climb list` and follow `climb prepare` output for the chosen Climb. Use `regents techtree run status RUN_ID` for that run. Proof verification lives under `regents techtree proof`; inspect its help rather than inventing a top-level `verify` command.

Model calls use the user's chosen provider or plan and can consume its allowance. Local records and traces stay local unless a documented operation sends them; model reviews describe what reaches the provider. Publishing a supported Climb Result uploads its proof and Skill and requires separate approval. Forge comparisons are local; exporting a collection is not publication. Withdrawals are consequential and require approval. Preserve the independent participant key: SIWA pairing does not replace it. On uncertain publication, read by bundle digest before retrying identical bytes with fresh proof.

## WebMCP: browse and inspect evidence

| Goal | Tool | What to do next |
| --- | --- | --- |
| Read the current setup contract | `techtree_start` | Compare its release with installed help; hand local steps to a shell-capable agent. |
| Choose a task set | `techtree_climbs`, `techtree_climb` | Inspect scope and data policy before recommending it. |
| Find evidence | `techtree_results` | Filter only with declared schema fields; page with `next_before_sequence`. |
| Inspect one result | `techtree_result` | Use the returned `bundle_digest`; report scores, verdict, withdrawal and evidence limits. |
| Verify identity / read account | `agent_whoami`, `account_balances`, `credits_history`, `points_balance` | Use signed access; these reads neither start runs nor award Points. |
| Publish or withdraw | `techtree_publication` | Only with approval and the required independent proof; preserve raw JSON bytes. |

There is no browser evaluation command in the checked manifest. Do not advertise WebMCP as a remote run service. When no public-results CLI command is present, use public HTTP `GET /api/v1/publications` and `GET /api/v1/publications/BUNDLE_DIGEST`, explicitly as HTTP. Wallet Bench evidence is at [wallet-bench.md](https://techtree.sh/wallet-bench.md).

## Follow-up contract

The intervals below are suggested starting points, not service promises or permission to run forever. A request to read once ends after one report. Create or update a recurring job only when the user asks to watch, monitor or check back, using the host's supported scheduler. Record the scope, interval, stop condition, private destination and permitted actions; reuse a matching job. A monitoring request authorizes checks and alerts, not posts, spending, compute or wallet signatures.

Prefer available events and returned deadlines over fixed polling. Save cursors, record IDs and timestamped snapshots privately, scoped to this agent and owner. Consume all pages before advancing the checkpoint; never discard unread events. On a reset or expired cursor, rebaseline and disclose any gap. Respect `Retry-After`, back off on repeated failures, and stop protected work on revoked access. Notify only for a meaningful change, a decision or a blocker; avoid repeated unchanged alerts. Never say a schedule exists until the host confirms it.

## When to check again

| Use | Suggested interval | Meaningful update / stop condition |
| --- | --- | --- |
| A local run the user started | Every 1–5 minutes while active; prefer process completion events | Completion, failure or a required decision. Stop when terminal; never auto-start another paid run. |
| Results on followed Climbs or models | Every 10 minutes during active research; daily for casual interest | A new relevant `log_sequence`, a withdrawal, or a linked rerun. Page back to the saved sequence. |
| Wallet Bench investigation | Every 30–60 minutes for a test marked Testing; daily otherwise | New evidence or a terminal verdict; do not equate Testing with failure. |
| The user's own published Result | Daily, or when they request a review | Changed withdrawal status or a new `rerun_of` reference; keep the original evidence. |

Return the comparison question, exact conditions, evidence links, verdict and its limits, any provider cost approval still needed, and the next check if scheduled.

## Current references

- [Purpose](https://techtree.sh/), [agent workflow](https://techtree.sh/agents.md), [tool schemas](https://techtree.sh/capabilities), [discovery](https://techtree.sh/llms.txt).
- [Regents CLI source and local engine guidance](https://github.com/regents-ai/regents-cli).

Public guides and tool manifests were read on 15 October 2026. CLI help was checked; no experiment, signed publication or native browser execution was performed while authoring this skill. Recheck availability at use time.
