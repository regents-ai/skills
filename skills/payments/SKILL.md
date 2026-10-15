---
name: payments
description: Taking USDC payments on Regent's Phoenix and Ash sites with the shared RegentPayments library — tips, paid actions and fees paid from a person's own wallet on Base through x402, their USDC Balance, and paid tools for agents. Use when adding or changing anything a person or agent pays for, an offer, a pay button, the USDC Balance shown on a page, a paid HTTP endpoint or MCP tool, a paid-fix fee forwarded to REGENT staking, or the words shown for a payment's outcome.
---

# Payments

**Load `ash-stack` first, then `onchain-buttons` for the pay button.** Every Regent site
takes payment the same way, through one shared library: `regent_payments`
(`RegentPayments`) in `repos/elixir-utils/ash_components/payments`, pinned like `regent_identity`:

```elixir
{:regent_payments, git: @elixir_utils, ref: @elixir_utils_ref, sparse: "ash_components/payments"}
```

Read the library's module docs before building; they are the contract. This skill says how
a site fits around it.

## Rules

1. **Regents keeps no balance for anyone.** Available funds stay in the person's own
   wallet; there is no Regent-kept balance, top-up or withdrawal (founder, 2026-09-28,
   confirmed 2026-10-05). A payment goes from the payer's own wallet straight to the
   wallet the offer names, settled by an x402 facilitator. Funds committed to a product
   sit in that product's own escrow under its stated rules (Patchbay Offers) and are
   shown apart from wallet funds. The library stores what was promised and what happened.
   Say "Regents does not keep a balance for you", never "Regent never holds your money".
2. **USDC Balance** is what the person's signed-in Privy wallet holds in USDC on Base,
   read live with `RegentPayments.Balance.usdc_balance_atomic/1`. It gets there when they
   send USDC to their address or buy it by card through Privy. Call it "USDC Balance" on
   every site, never Credits, credit or account balance (founder, 2026-10-05). The
   template's `/showcase/funds` shows funds on other networks, commitments, card
   purchases and cash-outs; the plan is `docs/wallet-funds-plan.md`.
3. **One offer per paid action.** A site writes a module implementing
   `RegentPayments.Offer` for each thing it sells (a tip, a paid fix, a run) and lists it
   in `config :regent_payments, offers: [...]`. The offer freezes the terms (`freeze/2`:
   amount, the wallet paid, what it is for, the sentence the payer sees). It then carries
   out what was bought (`carry_out/4`). The library owns everything between.
4. **Terms are frozen, never taken from the request.** Amount and destination are read
   from the stored intent on every call. Nothing a page or agent sends changes them.
5. **What a payment buys is saved once.** `carry_out/4` runs inside the transaction that
   holds the intent's row lock. The site's row for the effect is written through the same
   repository, with a unique index on the intent id. Anything outside the database (a job,
   a runner, a message) starts only after commit: an `after_transaction` hook or an Oban
   job inserted in the same transaction.
6. **Every press reaches the wallet.** The pay button follows `onchain-buttons`. A repeat
   press signs the same authorization (one nonce per intent and wallet), so USDC moves at
   most once. Never block, hide or dedupe the press to get that.
7. **A timed-out settlement is not retried.** It is left `settlement_pending` for a person
   to check on the chain. The facilitator client runs with no retries on purpose.

## Wiring a site

```elixir
config :regent_payments,
  repo: MySite.Repo,
  ash_domains: [RegentPayments],
  site: "mysite",                       # every row this site writes carries it
  offers: [MySite.Payments.Tip],
  base_rpc_url: System.get_env("BASE_RPC_URL"),
  payment_chain: %{name: "Base", rpc_url: "https://mainnet.base.org"},
  wallet_proof: [name: "MySite", version: "1", endpoint: MySiteWeb.Endpoint]

config :regent_payments, RegentPayments.Facilitator,
  url: X402.Facilitator.Auth.CDP.facilitator_url(),
  auth: {X402.Facilitator.Auth.CDP, api_key_id: id, api_key_secret: secret}
```

- Start `RegentPayments.Supervisor` after the repository.
- The CDP key goes in Fly secrets. `BASE_RPC_URL` may carry a provider key; the library
  never logs it, so don't log it either.
- **Only Regents migrates the tables.** Its release runs `RegentPayments.Migrator.up/1`
  and creates the shared `regent_payments` schema. Every other site reads and writes it,
  seeing only the rows its own `site` wrote. The rows are the record of money that moved:
  `payment_intents` and `payment_receipts` are on the production protected-table lock
  (founder, 2026-09-29), so a migration or reset that deletes from, empties or drops them
  fails, and only Sean lifts it. Tests use the Ecto sandbox or a fresh local database.
- Payments are Base mainnet only (`RegentPayments.USDC`): real USDC, no test network.
  The template's `/showcase/payments` shows the payer's view with sample figures
  and Pay switched off.

## The three doors

| Who pays | Call | Notes |
| --- | --- | --- |
| A person on a page | `RegentPayments.WalletPayment.pay/4` | Unsigned, it answers `{:review, intent, review}`: a `RegentChain.Review` with one signature step for the signed-in wallet. The hook signs it and sends back the `review_id` and signature; the same call then settles. `{:wallet_mismatch, id, note}` carries the note to show beside the button. |
| An agent over HTTP | `RegentPayments.Purchase.prepare/3`, then `execute/3` | No payment answers `{:payment_required, intent}`; send `Purchase.terms/3` as the x402 402 body. A signed `payment-signature` then settles. `on_offer/3` answers a repeated request with the purchase already started. |
| An agent over hosted MCP | `Purchase` with `RegentPayments.MCP` | The tool names the wallet (`MCP.wallet/1`); the payment is in `_meta` (`MCP.payment/1`) and must come from that wallet. An action that moves money without a payment proves the wallet with `RegentPayments.WalletProof`. |

Answer each outcome in customer words: paid, still settling (check again), expired
(prepare again), refused (with the reason), or the payment service unavailable. The
WebMCP tool refusal shape is in `ash-webmcp`.

## Paired agent authority

Verify SIWA before resolving the current pairing and canonical beneficiary. Every
agent payment entry point, including hosted MCP, supplies an explicit `role: :agent`
actor. Its `id` and `acting_agent_id` are the same agent profile UUID;
`beneficiary_profile_id` is the site's owner profile UUID; `human_account_id` is the
canonical positive integer account ID. Include the verified `privy_user_id`,
lowercase `wallet_address` and original `pairing_id`. Do not pass an owner actor or
accept these values from request fields.

The library freezes that authority with the payment terms and locks the original
active pairing before preparation and initial settlement. Revocation or re-pairing
cannot authorize a new settlement against the old episode. Facilitator verification
runs outside the database transaction; the locked transition checks authority again.
The reserved `__regent_payments_agent_authority` payload entry is private server data.
Never serialize a whole intent payload or return it as recovery material.

After settlement is authorized, paid effects receive a
`RegentPayments.CompletionActor`. An offer must check
`AgentAuthority.completion_for?(actor, intent, expected_kind)` and bind its product
action to the stored intent's exact target. This actor may finish only that paid
effect; it grants no owner permissions, ordinary private reads, new purchases or
unrelated product actions. Keep its original beneficiary and pairing attribution.

For recovery after unpairing, authenticate the original agent signer, then use
`Purchase.complete(actor, intent_id)`. Accept no payment signature on this route and
return only intent ID, status and receipt. It never starts or retries settlement.
Legacy pending intents without a frozen wallet or receipt are refused by this new
API; legacy settled/applied intents require the receipt payer to match the signer.
Do not guess historical ownership or widen authorization to make recovery succeed.

The template documents this integration and keeps its payment showcase illustrative;
it does not configure a payable offer. Product sites adopt the shared implementation.

## Fees handed on to REGENT staking

A paid fix's fee settles into the site's operator wallet, then
`RegentPayments.FeeForward` hands it to the REGENT revenue staking contract in two
operator-signed transactions: an approval of exactly the fee, then the deposit. The site
decides when to forward. It stops a second forward of one fee under a row lock on its own
forward record. An answer of `:deposit_unknown` means look on the chain before running
the forward again.

## Checks

- The library's own suite covers the payment path; a site tests its offers' `freeze/2`
  and `carry_out/4` only where the founder agreed tests.
- A person pays a small real amount from a Privy wallet and from a browser-extension
  wallet before release. Say so in the report rather than claiming it.
- `make check-required-fixes` passes with `regent_payments` pinned to a git commit.
