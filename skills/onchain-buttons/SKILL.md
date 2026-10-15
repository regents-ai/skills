---
name: onchain-buttons
description: Buttons that make a person's wallet act on Regent's Phoenix LiveView and Ash sites — send a transaction (approve, stake, bid, buy, claim, settle, launch) or sign (x402 payment, typed data). Use when adding, changing, reviewing or debugging any wallet or on-chain button, its TypeScript hook, the chain switch, the wallet's answer, the server's check of the result, or the words shown for each outcome.
---

# On-chain buttons

**Load `ash-stack` and `ash-frontend` first.** The wallet rules in
[regent-integration](../ash-stack/references/regent-integration.md#wallet-actions) apply
and are not repeated here. For chain events recorded in the database, use `chain-events`;
for a USDC payment's button, `payments`.

## Rules

1. **Every press reaches the wallet**, including a second press while the first is with
   the wallet or on its way to the chain. A reverted or duplicate transaction is an
   accepted outcome. Never hide, debounce, queue or merge presses, and never set
   `pointer-events: none`. Mark a press in progress with a data attribute and CSS only.
   The one exception (founder decisions, 2026-09-28 and 2026-10-06): the site may block a
   press that is certain to fail. When the chain's own current state, read by the server
   at the latest block, makes the transaction certain to fail, the button stays visible
   but `disabled` with a reason of a few words beside it, and it comes back when that
   state changes. Examples: "144/144 Keys sold"; a Buy whose USDC approval is not on the
   chain yet ("Approve first"); a payment larger than the wallet's USDC. A pending
   transaction, a repeat press, or one that only might revert is never a reason to
   disable. See [hook pattern](references/hook-pattern.md#markup).
2. **A hook's own click listener handles the press.** LiveView ignores a second
   `phx-click` on an element while the first is waiting for the server (lab: three presses,
   one event), and disables every button in a form while its `phx-submit` is in flight
   (lab). So an on-chain button has no `phx-click`, is never inside a `phx-submit` form,
   and never waits for a server round trip before the wallet opens when the step is
   already on the page.
3. **Privy's active wallet sends, when it is one of the account's own** (founder decision
   "1 a", 2026-09-27: "the Privy active wallet is the only wallet that can make actions, and so if the user wallet differs, make them switch"). The hook reports the active wallet; when it is one of the
   signed-in account's linked wallets, the panel shows its figures and the server builds
   the steps for it. When it is not linked, or none is active, the figures stay on the
   account's own wallet, a note beside the button names both short addresses and asks
   the person to switch, and a press sends nothing and says why. Signed out, the active
   wallet's figures show and the button asks for sign-in. The account's linked wallets
   come from `AccessContext.linked_wallets/1` (`nil` signed out), never a hard-coded
   list. See [which wallet sends](references/hook-pattern.md#which-wallet-sends).
4. **The server builds every step** (founder decision, 2026-09-27): it encodes the
   calldata and pushes the review to the panel before the button is pressed. The
   browser never encodes a transaction. See
   [hook pattern](references/hook-pattern.md#the-server-builds-the-steps).
5. **Before sending**, switch the wallet to the step's chain (add it when the wallet
   answers 4902), then check the account is the step's signer and make `eth_chainId`
   the last read before `eth_sendTransaction`.
6. **An approval is a step of its own.** The next step's button appears as soon as the
   approval is sent; nothing waits for it to land before the next press can reach the
   wallet.
7. **The hook reports only what the wallet said**: the hash, or why nothing was sent.
   Each report names the review it was sent from, and `handleEvent` payloads carry the
   component's DOM id, since every hook on the page hears every `push_event`.
8. **The server checks the result at the latest block** (founder decision, 2026-09-26):
   read the receipt every 2 s, confirm the transaction's sender, target and calldata are
   the step's, and show pending, done or reverted. Stop after a set number of reads and
   offer "Check again". Never use `safe` or `finalized`, never count confirmations, never
   store pending transactions. The chain watcher (`chain-events`) records the outcome for
   good.
9. **Words are for customers**: say what happened and what to do, never an error code.
   See the outcome table in [hook pattern](references/hook-pattern.md#outcomes-and-words).

## References

| File | Covers |
| --- | --- |
| [hook-pattern.md](references/hook-pattern.md) | The template's reference files, the review, which wallet sends, a press, the server's check, outcomes and words, checks |
| [journeys.md](references/journeys.md) | Listing a page's wallet journeys: controls, the shared wallet situations, per-control cases, marks; known gaps in the pattern |
| [sites-today.md](references/sites-today.md) | How each site does it now, where it differs from these rules, and which checkout to read |

## Checks

- Before a page with wallet buttons ships, list its journeys as
  [journeys.md](references/journeys.md) describes and mark every row.
- Run the page's wallet situations on a lab chain the way the template's
  `/showcase/onchain` workshop does (see [hook pattern](references/hook-pattern.md#checks)).
- Sites keep their own test policy; the template has no test suite. LiveView tests do not
  run hooks.
- A person checks real Privy and a browser-extension wallet on a lab chain before
  release; say so in the report rather than claiming it.
- Motion on the button comes from the kit (`data-press-label`, see `animejs`).
