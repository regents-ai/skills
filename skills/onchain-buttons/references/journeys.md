# Listing a page's wallet journeys

How to list what can happen on a page with wallet buttons (founder, 2026-09-27). List by
control, and write the wallet situations every button shares once, not once per button. A
Stake page listed per journey came to 42 rows for 9 controls; listed this way it is the 9
controls, one shared table and a few cases per control.

## 1. The page's controls

List every real control on the page: buttons, inputs, toggles, links that change state.
Mark which ones open the wallet and which transactions each one sends.

Example, Regents Stake: 9 controls; 4 open the wallet and send 6 kinds of transaction
(approve, stake, unstake, claim USDC, claim REGENT, claim and restake).

## 2. Wallet situations, written once

These apply to every wallet button on every site. Copy the table, then mark each row for
this page.

| Group | Situation |
| --- | --- |
| Who is pressing | Signed out |
| | Privy's active wallet is not linked to the signed-in account |
| | No wallet is active in this tab |
| | The person switches to a second wallet linked to the same account (the figures move to it) |
| What the wallet does | A repeat press while the wallet is open |
| | Wrong network: switched, added, or the switch refused |
| | Declined |
| | No ETH for fees |
| | Sped up or cancelled in the wallet (the hash is replaced) |
| Wallet kind | Browser extension |
| | Hardware wallet behind an extension |
| | Phone wallet: the tab sleeps and the page reconnects; typed values come back, values held only on the server do not |
| | Smart wallet (Base app, Coinbase Smart Wallet): the transaction's sender is not the signer |
| | Safe: answers with a Safe transaction id, not a chain hash |
| After sending | Waiting, then done, and the figures on the page refresh |
| | A slow chain, then "Check again" |
| | A reload forgets the page's list of sent steps |
| | Sign-out while a step is on its way |

## 3. Per control, only what changes the outcome

For each control that opens the wallet, list only the cases that change what happens:

- typed values at their edges (empty, zero, more than the balance, too many decimals);
- approval states (none, too small, enough);
- contract states (paused, full, nothing to claim);
- who owns the result (staking or buying for someone else).

## 4. Beyond the buttons

- A screen reader reaches every control and hears every outcome.
- The page works at phone width.
- An agent can read the page's figures.
- An agent can take the same actions, from the same server-built steps.

## 5. Mark every row

| Mark | Meaning | Evidence |
| --- | --- | --- |
| Works | Seen working | The test, or the lab chain run, that showed it |
| Not tried | The code reads right, not yet run | The file and line |
| Gap | Wrong or missing | What happens instead |

## Known gaps in the pattern today

These are open in [hook pattern](hook-pattern.md) and `regent_chain` for every site, so a
page listing will find them. Mark them Gap until they are fixed.

1. **Which linked wallet sends.** Decided 2026-09-27: Privy's active wallet, when it is
   one of the account's linked wallets (rule 3). The template does this; each site
   adopts it from there.
2. **Smart wallets and Safe.** `RegentChain.Outcome.of/4` compares the transaction's
   sender with the signer, so a smart wallet's step reads as not this step, and a Safe
   transaction id never resolves.
3. **No ETH for fees.** `send_step.ts` recognises a refusal for lack of fees only by
   the wallet's "insufficient funds" message; a wallet that words it otherwise reads as
   "may have sent".
4. **Revert words.** A reverted step says only that it did not go through, even when a
   read shows the contract is paused or full.
5. **Replaced hashes.** A step sped up or cancelled in the wallet gets a new hash; the
   server's check keeps reading the old one.
