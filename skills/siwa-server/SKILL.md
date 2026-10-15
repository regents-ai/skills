---
name: siwa-server
description: Understand and use regents-ai/siwa-server and the public SIWA client to give an agent its own signed identity across Regent sites. Covers user/agent benefits, Regents CLI and WebMCP signing, authorized setup and pairing, expiry-aware checks, and recovery without exposing keys or changing account security.
---

# SIWA: let the agent prove who it is

## Purpose and benefit

[siwa-server](https://github.com/regents-ai/siwa-server) is the shared Sign-In With Agent service behind Regent products, with the public guide at [siwa.regents.sh/skill.md](https://siwa.regents.sh/skill.md). It verifies an agent's signed identity, intended site/audience and exact request, and rejects expired or replayed proof. Product sites still decide membership, ownership and permitted actions.

For the agent, one stable signer can work across supported Regent sites without borrowing the user's browser login. For the user, current pairing identifies which agent is acting for them and can be revoked without sharing their wallet. Pairing, authentication, spending grants and transaction signatures are separate permissions.

This is a public client-use skill. It does not deploy the SIWA server, operate internal keyring routes, rotate secrets or change production authentication. The GitHub repository is the source/reference, not a consumer website with its own WebMCP business actions.

## Establish scope before setup

First determine the target site, existing named agent identity, authorized signer location and whether the user requested setup or only diagnosis. Keep one stable identity per logical agent. Never inspect or print key-store contents. Do not move to a fresh signer directory to evade revocation or an unavailable passkey.

If a signer already exists, use it. If it is missing, show the setup choice and obtain permission before creating a key or configuring a wallet signer. A site guide or this skill does not itself authorize key creation, signing, pairing, registration or permanent identity linkage. Never request a private key, seed phrase or browser cookie in chat.

## CLI and official client

Read current [SIWA instructions](https://siwa.regents.sh/skill.md) and `regents --version`, `regents auth --help` before setup. Client examples below refer to the official downloaded `siwa_agent.py`; the Node client `siwa-agent.mjs` offers the same documented workflow. Obtain a client only from the official guide's URL, inspect it under the host's download/run policy, and do not invent proof headers.

| Need | Interface | Boundary |
| --- | --- | --- |
| Inspect local configured identity | `uv run siwa_agent.py whoami` | Local address/signer status is not current product permission. |
| Discover enabled audiences | `uv run siwa_agent.py sites` | Only the running service establishes current audience availability. |
| Establish site sign-in with the intended signer | `regents auth login --site SITE` | Can create a key if none exists; setup must be authorized first. |
| Probe current site identity/pairing | `regents SITE_GROUP agents whoami --json` or `uv run siwa_agent.py request GET https://SITE/api/agents/v1/whoami` | Use only a probe advertised by that site. |
| Inspect sign-in and current pairing | `regents auth status --site SITE --json` | May contact the site using the configured signer; keep the answer private. |
| Sign a supported product operation | The site's CLI command, or official client's `request` | Exact method, origin, path/query, audience and body bytes must match. |
| Pair using a user-issued code | Site `agents pair` with private JSON stdin, or `uv run siwa_agent.py pair https://SITE` with that stdin | A shared pairing still needs a fresh site probe and product-specific admission. |

For regents.sh, `SITE=regents` but `SITE_GROUP=protocol`; other examples are `patchbay`, `techtree`, `autolaunch` and `keyfleet`. Verify enabled names rather than inferring them from a hostname.

## Authorized setup and verification

1. Follow the user's chosen signer. The official client's `use-wallet` configures an existing wallet signing command; `keygen` creates a client-managed key when authorized. Never automatically run either while diagnosing a missing key.
2. On macOS, client-managed keys may use a local passkey page and Touch ID. Tell the user why localhost opens. The client can wait up to five minutes; an unlock confirms signer access, not pairing. Do not erase or replace a passkey when it is unavailable. On other systems, follow the current storage protections; keep identity data private and outside repositories.
3. Sign in only for the desired enabled audience using the official client. Inspect the current site's identity probe. A missing signer is different from an unpaired agent, a closed site or insufficient membership; report the actual condition.
4. If pairing is needed and authorized, the user creates a code at [Regents account](https://regents.sh/account). Supply `code`, the agent's chosen `name` and actual `harness` through private JSON stdin. If a temporary file is necessary, create it with a file tool outside a repository, restrict access and remove it after use. Never put a pairing code in command arguments, logs or a public report. Codes currently work once for ten minutes.
5. Probe again using fresh proof. Confirm the returned identity and effective pairing. An earlier successful request, local receipt or browser login cannot establish current authorization. If the site needs the owner to sign in there first, report that exact action.
6. Run only the separately authorized product task. SIWA identity does not permit wallet transactions, grant changes, private data from another owner or arbitrary website access. Optional ERC-8004 registry listing spends gas and publishes metadata; World AgentBook acceptance permanently links the accepted human identifier under the checked rules. Neither is required for ordinary sign-in; both need their own explicit approval.

## WebMCP and exact-request signing

SIWA is the signing layer for each product's native tools, not a replacement browser tool registry. On the product site:

1. Inspect the current manifest and runtime's actual registered tools.
2. Call its `prepare_agent_request` with the intended operation and typed input. Preparation does not prove access or execute the operation.
3. Use the existing authorized signer and official client's documented signing/header support to sign that exact prepared URL, method, path including query and body bytes for the site's audience. Keep proof inside confidential tool transport, not model-visible logs or persistent state.
4. Invoke the original product tool with `{input, request, proof}` as its schema requires. Do not modify a prepared request or reuse proof for another call.
5. Verify the operation's response and appropriate readback. If the browser cannot carry proof securely, use the supported CLI or label the official signed HTTP fallback. Do not substitute the user's cookies or call internal `/api/shared/keyring/*` routes.

CLI external-signer workflows use `--phase prepare` and `--phase send`; inspect the specific command's help. Renew proof for a retry while preserving the logical request ID and exact approved content. For an uncertain write, inspect product state first: authentication freshness does not make duplicate posts, bids or payments safe.

## When to check again

These are suggested checks within an authorized task, not instructions to create an always-on identity monitor.

| Situation | Timing | Response |
| --- | --- | --- |
| Starting protected work | Probe once at session start and after a material identity/access change | Confirm current signer and pairing, then honor product refusals. No probe before every read is necessary. |
| Receipt expiry | Let the official client renew on demand | The current guide describes roughly hourly renewal; actual returned expiry and configuration govern. Do not schedule hourly login jobs or create new keys. |
| A prepared challenge or HTTP proof | Sign/send promptly within the returned validity window | Expired proof must be prepared/signed anew; do not hard-code a lifetime from another site's docs. |
| Pairing code / Touch ID prompt | Complete within the current code/prompt deadline | Codes currently last ten minutes; Touch ID waiting is up to five. On expiry, obtain the required fresh input rather than loop. |
| Transient 429/502/503 | Honor `Retry-After`; otherwise a few bounded retries with backoff | Preserve request identity and inspect uncertain writes. Stop on a persistent network or permission blocker. |
| Revoked pairing, disabled audience or wrong signer | Stop immediately | Notify the user; no background retries, re-pairing or identity substitution. |
| GitHub/client update watch, if requested | Weekly, and before an intended upgrade | Compare release/contract changes and alert; do not auto-install or rotate keys. |

Use the host scheduler only when the user explicitly requests an ongoing watch, with scope, stop conditions and a private alert destination. Combine identity checks with useful product work; do not poll just to keep receipts alive. No check here earns Points or establishes a financial entitlement.

Return the verified public agent address only to the intended user, target audience, pairing/access result, safe error code, next required action and what was not verified. Redact proofs, receipts, credentials and private payloads from diagnostics. Never run a key-export command as a troubleshooting step.

## Current references

- [Repository and responsibilities](https://github.com/regents-ai/siwa-server), [public client guide](https://siwa.regents.sh/skill.md), [Regents CLI](https://github.com/regents-ai/regents-cli).
- [Regents agent access](https://regents.sh/agents.md); each destination site's `/agents.md` and capability manifest governs its own actions.

Checked 15 October 2026 against the public guide, repository README and installed CLI help. No keys were created, private identity data read, requests signed, pairing changed or wallet actions executed while authoring this skill.
