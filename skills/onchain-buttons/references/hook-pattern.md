# The hook pattern

The template carries the working reference. Copy these files and replace the example's
steps; the paths are under `platform/` in ash-template. They compile against
`regent_chain` 0.2.0 (elixir-utils 7a876e8), Phoenix LiveView 1.2 and viem 2.55, and
were run in a browser against a lab chain at `/showcase/onchain`. The same component runs
on a real account at `/showcase/wallet`, on Base Sepolia.

## Files

| File | Holds |
| --- | --- |
| `lib/ash_template_web/components/onchain_example.ex` | The example component: builds the review, renders the buttons, owns the words |
| `lib/ash_template_web/onchain_steps.ex` | `AshTemplateWeb.OnchainSteps`: the server half every wallet component shares |
| `lib/ash_template/chain_client.ex` | Reads at `latest` for the review's chain: `transaction/2`, `receipt/2`, `balance/2` |
| `assets/js/hooks/onchain_steps.ts` | The hook: presses, the review, reports what the wallet said |
| `assets/js/wallet_actions/send_step.ts` | One send or signature: chain switch, account check, why it failed |
| `assets/js/wallet_actions/connected_wallet.ts` | `activeEthereumWallet()`: Privy's active wallet in this tab |
| `lib/ash_template/access_context.ex` | `AccessContext.linked_wallets/1`: the signed-in account's own wallets, lowercase and each once, or `nil` signed out |
| `lib/ash_template_web/live/wallet_showcase_live.ex` | The example as a product page runs it: the real account, Privy's active wallet, the `:wallet_chain` setting (Base Sepolia) |
| `lib/ash_template_web/live/onchain_showcase_live.ex`, `assets/js/hooks/onchain_lab.ts` | The local workshop and its stand-in wallet |

Register `OnchainSteps` in the `hooks` passed to `LiveSocket`. The hook element needs an
`id`; LiveView skips a hook without one.

## Markup

```heex
<section id={@id} phx-hook="OnchainSteps">
  <form phx-change="change" phx-submit="change" phx-target={@myself}>
    <input name="amount" value={@amount} data-onchain-input="amount" />
  </form>
  <p aria-live="polite" hidden={!@review}>{@review && review_line(@review)}</p>
  <P.button data-onchain-step="record">Record</P.button>
</section>
```

- Lines above the buttons (the review, the "from" line, the wrong-wallet note) are always
  in the page and shown or hidden with `hidden`, never added with `:if`. A line appearing
  above a pressed button otherwise makes the page update replace that button, and focus
  leaves it (Regents 65b20d87).
- A button stays on the page after its step is sent, the last step of a flow included,
  and a further press sends that step again. Only its label or the status line changes.
  A flow that hides its button once nothing is "next" stops a repeat press reaching the
  wallet while the first is slow (rule 1; Autolaunch A02 review). Once the server has
  confirmed the last step, the flow may end on "Done" without a button.

- Whenever a person types an amount, the step names what the press sends, read from the
  review itself (founder decision, 2026-09-27: a review screen, not browser-built
  steps): "Approve 5 USDC", "Buy 5 Credits". Keep it to that label; why the step exists
  and how long it takes go in a `Regent.Primitives.tip` beside it (STYLE.md, "Few words
  on screen"). A done step shows a tick, a waiting one a dashed box.
- A button names its step with `data-onchain-step`. It has no `phx-click` and sits
  outside any form (rule 2). It is `disabled` in one case only: the server's own read of
  the chain says the step is certain to fail (sold out, the sale has closed, the claim is
  already made, the approval the step spends is not on the chain yet, the wallet holds
  too little). Then a few words beside it give that reason, and the server enables it
  again when the read changes. Never disable it because a press is pending,
  or because the transaction might revert, and never use `aria-disabled="true"` or CSS
  to make an enabled button inert.
- Every field the review depends on carries `data-onchain-input="name"`, matching the
  review's `inputs`. A group of radio buttons sharing one name reports the chosen value;
  a checkbox reports "true" or "false".
- The component holds one hidden line marked `data-onchain-lost` with its own words
  ("This page lost its connection, so nothing was sent. Press again once it's back.").
  The hook shows it when a press could not reach the server; the next render hides it.
- The hook marks a button `data-awaiting-wallet="true"` while the wallet has any of its
  presses, and only removes it when the last one is answered. Style it; never block with
  it.

## The server builds the steps

```elixir
alias RegentChain.{Call, Review}

review =
  Review.new(socket.assigns.id, signer, chain, [
    Review.step("approve", token, Call.encode("approve(address,uint256)", [pool, amount])),
    Review.step("stake", pool, Call.encode("stake(uint256)", [amount])),
    Review.signature("sign", typed_data)
  ], %{"amount" => amount_as_typed})

OnchainSteps.put_review(socket, review)
```

- `chain` is `%{chain_id:, name:, rpc_url:}`; `rpc_url` is https, or http on this
  machine for a lab chain. It is the public address a wallet adds the chain with. The
  server reads results through its own node for `chain_id` (the template's
  `:chain_nodes` setting), so a private node or a lab fork sees what the steps sent.
- `Call.encode/2` takes the exact function signature and raises on an argument that
  does not fit, so a step that cannot be built never reaches the page. `Review.step/4`
  takes wei as a fourth argument when the step pays native currency.
- Prove every signature against the contract's pinned ABI when the module compiles, so a
  signature that drifted from the deployed contract stops the build instead of reaching
  a wallet. Regents' Stake steps do it (regents@2d61d9e1
  `platform/lib/ash_platform/staking/steps.ex`, with `declared!/3` in
  `wallet_actions/abi.ex`):

  ```elixir
  @abi_path Path.expand("../../../contracts/abi/revenue-staking.json", __DIR__)
  @external_resource @abi_path
  @abi @abi_path |> File.read!() |> Jason.decode!()
  @after_compile __MODULE__

  @doc false
  def __after_compile__(_env, _bytecode),
    do: Enum.each(Map.values(@calls), &Abi.declared!(@abi, "function", &1))
  ```

  `declared!/3` finds the ABI entry of that kind and name, rebuilds its signature from
  the input types (a tuple becomes its component list) and raises unless it matches
  exactly. `@external_resource` recompiles the module when the ABI file changes.
- `Review.signature/2` takes EIP-712 typed data as `eth_signTypedData_v4` takes it. The
  server keeps its copy; the page reports only the signature.
- A review never changes. Its `id` comes from everything in it, so a new signer, chain,
  step or input is a new review. `put_review/2` pushes it only when the id changes, and
  pushes `nil` when no wallet may act.
- Build the review whenever the signer or a figure changes (`update/2`, the form's
  `change`, the active-wallet event), so it is on the page before anyone presses.
- A step with a time limit in it (a Permit2 allowance expiry, a bid or swap deadline) is
  rebuilt by the server before the limit comes: when its approval confirms, when it
  reverts, and on a timer well inside the limit (every 10 minutes for a 15-minute
  deadline). The page always holds a step that can still land, and a press never waits
  for a rebuild (Autolaunch A02 review: a press after the deadline reverted, and the
  same expired step was offered again).

## Which wallet sends

Founder decision "1 a", 2026-09-27: Privy's active wallet is the only wallet that acts,
and only when the signed-in account links it.

- The page passes the component `linked={AccessContext.linked_wallets(@access_context)}`:
  the account's own `wallet_addresses`, lowercase and each once, or `nil` signed out.
  Never a hard-coded list and never a wallet the browser names.
- The hook pushes `onchain_active_wallet` with the address (or `nil`) when it mounts and
  on every `ash:wallet-state`.
- `OnchainSteps.active_wallet/1` reads it; `OnchainSteps.signer(linked, active)` is the
  wallet that may act, or `nil` when signed out, when none is active, or when the account
  does not link it.
- With no signer there is no review. `OnchainSteps.mismatch_note/2` names both short
  addresses and asks the person to switch when the wallet app has another wallet open
  ("Your wallet is on 0x9a8b..c1d2, which isn't linked to this account. Switch to
  0x1234..abcd.").
- `OnchainSteps.shown_wallet(linked, own, active)` is the wallet the panel shows figures
  for: the signer, or with none the account's own wallet
  (`AccessContext.own_wallet/1`), so a wrong or missing active wallet never empties the
  panel. Signed out, it is the active wallet. The line naming it says "Paying from" or
  "Sending from" only for the signer; any other shown wallet is just "Wallet", so the
  panel never names a wallet nothing will send from beside the note asking to switch.
- Every figure read for the shown wallet counts against a read allowance
  (`Limits.spend(:wallet_read, who)`). A panel that also shows figures signed out, where
  the wallet can be one the browser reports, counts every read against the visitor's
  client address (`{:client, client_key}`), as the wallet example does; a panel shown only
  signed in counts against the account (`{:human, id}`), as the Buy panel does. Past it,
  the figure already shown stays, and one not read yet shows as unavailable. Figures are read again
  when the wallet changes and when a step lands, never on each check while it is on its way.
- A figure taken from a confirmed step's receipt (an approval's amount) applies only when
  that step's signer is the shown wallet.

## A press

The hook's own click listener runs every press on its own:

1. **No active wallet**: it reports `wallet_unavailable` and the server's note says why.
   It never opens Privy's connect step (founder decision "1 a").
2. **No review yet, or the form differs from the review's `inputs`** (the person pressed
   before the first review arrived, or typed and pressed before the new one did), on a
   component with `data-onchain-input` fields: it sends `prepare_and_send` with the form
   and the step. The component takes the form as the page's own, builds the review and
   replies `%{review: review, send: name}`, and the hook sends that. An empty reply is
   `step_unknown`; no reply at all (a lost connection) shows the `data-onchain-lost` line.
3. **Otherwise** it sends the step from the review it holds, if the active wallet is the
   review's signer.

`press(review, name, push)` returns what it reported (`{transaction_hash}`, `{signature}`
or `{reason}`), so an agent tool can take the same path as a person's press.

Before any send or signature, `send_step.ts` switches the wallet to the step's chain
(adding it on 4902), checks the account is the signer, makes `eth_chainId` the last read,
and checks Privy has not swapped the wallet meanwhile. The hook then reports:

- `step_sent` `{review_id, step, transaction_hash}`
- `step_signed` `{review_id, step, signature}`
- `step_failed` `{step, reason}`

## The server's check

`OnchainSteps` keeps the page's last 32 reviews and 8 sent steps in a
`RegentChain.Presses`, in assigns only. A reload forgets them; the chain watcher
(`chain-events`) and the page's normal reads show what landed.

- `OnchainSteps.sent/2` finds the review by `review_id` and starts reading at once, then
  every 2 s, with `start_async({:onchain_step, hash}, …)`. Each read is
  `RegentChain.Outcome.of(ChainClient, review, step, hash)` at `latest`.
- `Outcome.of/4` answers `:pending` until the receipt exists, then `:confirmed` or
  `:reverted`. A hash whose chain, sender, target, calldata or value is not the step's
  as that review built it is `{:error, :not_this_step}`.
- After 90 reads with no receipt the step is stalled; the page offers "Check again",
  which calls `OnchainSteps.check_again/2`.
- A report for a review the page no longer holds is never checked against a later
  review; it shows the "not this step" words.
- `OnchainSteps.signed/2` returns the review's own typed data with the signature, for
  the component to verify and use.

The component forwards `handle_async({:onchain_step, hash}, result, socket)` to
`OnchainSteps.checked/3`.

## Outcomes and words

The hook sends only reason codes; the words live in `OnchainSteps.failure_note/4` and
`describe/2`.

| Reason or outcome | Meaning | Words |
| --- | --- | --- |
| Signed out | No account | "Sign in to send this. Nothing was sent." |
| `wallet_unavailable`, none active | Signed in, but no wallet is open in the wallet app | "You're signed in with 0x1234..abcd, but your wallet app has no wallet open. Open 0x1234..abcd there, then press again. Nothing was sent." |
| Active wallet not linked | Another wallet is open in the wallet app | "Your wallet is on 0x9a8b..c1d2, which isn't linked to this account. Switch to 0x1234..abcd. Nothing was sent." |
| `step_unknown` | No step by that name for these figures | "This can't be sent as it stands. Check the details above, then press again. Nothing was sent." |
| `wallet_unavailable`, mid-press | Privy swapped the wallet during the press | "Your wallet changed during the press, so nothing was sent. Press again." |
| `network_mismatch` | The wallet would not move to the chain, or moved away | "Your wallet is on a different network. Switch it to Base, then press again. Nothing was sent." |
| `wallet_declined` | The person said no (4001) | "Your wallet declined this. Nothing was sent." |
| `insufficient_funds` | The wallet refused for lack of fees | "Your wallet doesn't have enough on Base to pay the network fee. Nothing was sent." |
| `send_unconfirmed` | The wallet failed after the send began | "Your wallet may have sent this. Check your wallet activity." |
| `:pending` | Sent, no receipt yet | "Sent. Waiting for Base." |
| `:confirmed` | The receipt succeeded | "Done." |
| `:reverted` | The receipt failed | "This did not go through and nothing moved." |
| Stalled | 90 reads, no receipt | "Base has not confirmed this yet. Check again, or look in your wallet activity." |
| Not this step | The hash is not what the review built | "This transaction is not the one this page prepared, so it can't be followed here. Check it in your wallet activity." |

A component names its steps and writes its own reverted words per action (what usually
causes it, what to do).

## Approvals

An approval is its own step with its own button ("Approve USDC"). Approve exactly the
amount the next step needs. When the approval is sent, the next button shows at once; a
press on it before the approval lands still reaches the wallet, and if it reverts the
words say so. Whether an approval is needed is read on the server at `latest` when the
review is built.

## Signing instead of sending

A `Review.signature/2` step asks for `eth_signTypedData_v4` after the same chain and
account checks. The server verifies the signature against its own typed data and does
the rest. A declined signature is `wallet_declined`. Agents sign in with SIWA
(`elixir-utils/siwa`), which is not a button.

## Checks

- The template has no test suite. Its proof is the workshop: run `anvil --port 58600`,
  then `mix phx.server`, and open `/showcase/onchain`. The stand-in wallet has lab
  accounts A and B (linked) and C (not linked), a network choice, a refusal to switch, a
  decline and a slow mode. Run every row of the table above there before changing the
  pattern. `/showcase/wallet` then runs the same buttons with real Privy sign-in and a
  real wallet on Base Sepolia; a press there needs a little Base Sepolia test ETH.
- Sites keep their own test policy. A site that keeps a Vitest suite proves with a
  stand-in wallet that two presses in a row both reach `eth_sendTransaction`, that a
  decline reports `wallet_declined`, and that nothing is sent on the wrong chain or
  account.
- LiveView tests do not run hooks.
