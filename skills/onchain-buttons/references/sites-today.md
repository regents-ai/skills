# How each site does it today

Checked 2026-09-28 against each site's `origin/main` and its held wallet branch. Read with
`git show origin/main:<path>`: some local checkouts lag behind.

| Site | Steps built by | Result checked by | Sends from |
| --- | --- | --- | --- |
| Keyfleet (`main` 3b972bf) | The server: `Keyfleet.WalletSteps.build_steps` (action `:build`, `lib/keyfleet/wallet_steps/`), whose policy `LinkedSigner` admits only a signed-in person building for a wallet their account links; `KeyfleetWeb.WalletPanel` pushes the `RegentChain.Review` before the press | `KeyfleetWeb.OnchainSteps` with `RegentChain.Outcome`, through `Keyfleet.Chain.Client` at `latest`, every 2 s, then "Check again"; nothing stored | Privy's active wallet, only when the account links it |
| Regents (`main` 140eea2c) | Stake: the server, pushed as a review (`hooks/stake_steps.ts`). Redeem: the server, re-encoded in the browser as a check (`wallet_actions/redemption.ts`). The held line (`r02-onchain-steps` 2d61d9e1, carried on by the local `cleanup-0928` 7e5eaba0, both waiting for the founder's fork test) moves both onto the template's `OnchainSteps` and deletes the redeem encoder | The server, after the hook reports the hash | Privy's active wallet |
| Autolaunch (`main` 3f4fbb0) | The server, pushed as a review, for staking (`hooks/autolaunch_reviewed_steps.ts`); bid, launch and subject-wallet use the older `hooks/wallet_presses.ts`. Branch `a02/onchain-steps` f95863d (held for the founder) moves every button onto the template's hook and deletes both | The server at `latest`, every 2 s | The signed-in wallet only |
| Patchbay (`main` 1a3eafb) | The browser signs x402 typed data (`signTypedData` in `platform/assets/js/privy_bridge.tsx`, called from `webmcp/paid_actions.ts`). Branch `p13-server-built-payments` bd91ce0, rebased locally as `p13-on-main` 85834fa (held for the founder), has the server build the authorization as a review | The server, with the signature | The signed-in wallet only, as Privy holds it connected |
| Techtree | No on-chain buttons | | |

## The closest to this skill

Keyfleet, on `main`: every wallet button on the template's files.

- `platform/lib/keyfleet/wallet_steps/`: the Ash action that builds every step
  (`steps.ex`, `build.ex`) and its signer policy (`linked_signer.ex`).
- `platform/lib/keyfleet_web/wallet/onchain_steps.ex` and `wallet/wallet_panel.ex`:
  the review pushed before the press and the 2 s check.
- `platform/assets/js/hooks/onchain_steps.ts` and `wallet_actions/send_step.ts`: the
  template's, without the signature step, which Keyfleet never uses.

## Where sites differ from this skill

Each is a backlog item for that site, not something to copy. The template follows every
rule (`/showcase/onchain`); a site moves onto its files rather than patching its own.

1. **Held work.** Regents' held line, Autolaunch's A02 and Patchbay's P13 each move that
   site onto the template's files. Until they ship, `main` keeps the older paths above:
   Regents redeem re-encodes in the browser, and Autolaunch's `wallet_presses.ts` drops a
   press made before its review arrives (rule 1).
2. **Regents `main` sends from Privy's active wallet without checking that the account
   links it** (rule 3); the held line adds the check.
3. **Keyfleet, signed out, builds no steps**: the sale figures still show and a press asks
   for sign-in. **Clearing a delegate** names the signer, since `RegentChain.Call` refuses
   the zero address (below). **Buy on a key's page** opens the fleet's buy panel instead of
   buying in place.
4. **Not audited yet:** whether any site has an on-chain button with `phx-click`, or one
   inside a `phx-submit` form. Both silently swallow repeat presses (rule 2).
5. **Not audited yet:** which buttons have a state the chain makes certain to fail (a
   sold-out sale, a closed auction, a claim already made) and whether each shows it
   disabled with its reason (rule 1's one exception, 2026-09-28). Until checked, assume
   such a press reaches the wallet and reverts.

## Gaps in `regent_chain` (elixir-utils 28f6ebc, the template's pin)

Found by Keyfleet's move and the Phase 1 review; each is for the shared package, not a
site.

1. `RegentChain.Call` refuses the zero address, so a step cannot name "no one" (clearing a
   delegate).
2. No reader for contract return data or log data: `Event.one` reads fixed-width words
   only, so Keyfleet keeps its own readers (`Keyfleet.Chain.Abi`: `bytes/1`,
   `quantity/1`, `hash/1`, `word/2`, `decode/2`).
3. A review's chain keeps only `chain_id`, `name` and `rpc_url`, so the hook's request to
   add a chain the wallet lacks names Ether as its currency (`send_step.ts`). Right for
   every chain in use today; a chain with another currency needs the review to carry it.
