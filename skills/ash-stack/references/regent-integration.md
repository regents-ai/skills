# Regent integration

## Authority and acceptance

Start with `regent-workflow`. The founder's
request defines scope, acceptance and the mode (Pairing or Claude only). This pack
supplies engineering guidance, not another approval or tracking process.
Reuse the assignment's acceptance criteria and review evidence.

## Product boundaries

Regents.sh, Techtree, Patchbay, Autolaunch and Keyfleet remain separate Phoenix/Ash apps with
separate deployments. They share one physical PostgreSQL database: each product owns
its schema and migration ledger through its own Repo, and the Regents-owned
`identity/` package owns the shared identity schema (see
`agent-docs/product-boundaries.md` in the Regent workspace). Reuse `design-system/regent_ui` for
presentation primitives and `elixir-utils` for demonstrated shared infrastructure.
Product layouts, navigation and themes may differ. Components own no product
workflow, authorization, wallet state or database access. Keep named actions and
persistence in each product. Extract only code with actual equivalent consumers.

## Wallet actions

All five sites use the wallet identity and transaction-state rules in
`regent-workflow`: Privy's active wallet acts when the server finds it among the
signed-in account's linked wallets, and the page shows its data. Any other wallet
shows no data of its own and sends nothing; the page asks the person to switch to
one of their wallets. Match record and chain as well as signer.

Never preserve pending transactions in browser storage or database recovery
machinery. Do not restore/replay pending transactions on reload or build a recovery
inbox. Show transient interaction feedback and update website state from verified
receipts, canonical events and current chain reads. Confirmed event indexing and
saved creator drafts are not pending-transaction preservation. Existing historical
rows are not authorization for destructive cleanup.

Every distinct press of an on-chain button reaches the wallet, including a second
press while an approval or transaction is pending. Generic outbox, idempotency,
locking, retry and duplicate-operation guidance never authorizes admission state
for user-signed transactions. Do not block, ignore, defer, queue, serialize or
deduplicate a second press. A reverted or duplicate transaction is an accepted
outcome. A literal double-fire of one browser click is not a second press.

One exception (founder decision, 2026-09-28): when the chain's own current state
makes a transaction certain to fail, such as "144/144 Keys sold", the button stays
visible but disabled, and the reason is shown beside it. The button comes back as
soon as that state changes. A pending transaction, or one that might revert, is never
a reason to disable. Report current wallet feedback and verified chain outcomes
without persisting a recovery queue.
For Privy/session work, read [Privy reconciliation](privy-reconciliation.md). Its
login/logout coordination must never become wallet-transaction serialization.

## Claims and retirement

Historical regent.eth claims must survive in Fly Postgres through Ash before their
sole source or dependencies retire. Preserve all source columns, including fields
unmapped by an old resource; compare actual row identities and values, not an old
approximate count. Preserve related credit/allowance evidence until accounted for.
Accounts and Formation may retire after retained features are decoupled. This is
preservation and existing-claim display, not authority for new claims or payments.
Do not read `.env`, `.env.local` or `.envrc`, or access production without the
required exact authority. Keep raw user data out of reports and evaluation fixtures.

## Verification and cleanup

Use the worktree's isolated database, port and pinned dependency context. Never
share destructive test fixtures with another checkout. Verification commands must
not format files or alter dependency locks. A useful domain code interface is not
wrapper waste. Remove a wrapper only after checking callbacks, external callers,
error semantics, actor propagation and meaningful computation it provides.
Before removing a test, identify its protected behavior and whether another test
observes the same failure. Replace incidental source-text/copy locks when needed;
retain ABI, policy, data-integrity and user-visible contract checks.

Use real SQL for relationship reproductions; ETS can hide SQL behavior. Reproduce
a minimal failing/passing pair before adding forms or unrelated relationships.
Only one action per type is primary. For many-to-many changes, confirm the locked
`manage_relationship` input shape and join attributes rather than copying an old
example's field names. Version-matched dependency usage rules supply exact APIs.
