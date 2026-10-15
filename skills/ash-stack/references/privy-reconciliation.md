# Privy browser and Regent session reconciliation

Use this for Regent browser sign-in, sign-out, session restoration, linked-wallet
hydration, or Privy bridge failures. Privy browser state and Regent server
authority are related but not interchangeable.

## Keep three state machines separate

The product's acting wallet is Privy's active wallet when the server finds it among
the verified session's linked wallets (founder, 2026-09-27: "the Privy active wallet is the only wallet that can make actions, and so if the user wallet differs, make them switch"). Then the page shows
that wallet's data and the server builds its steps. Any other selection, including
an extension account that is not linked, shows none of its private data and sends
nothing; the page asks the person to switch to one of their own wallets. Linking a
new wallet happens through Privy and a fresh verified session, never from the page's
own report of a wallet.
Use the shared `regent-workflow` rule: never preserve pending transactions; refresh
website state from verified chain evidence instead of restoring transaction queues.

1. `usePrivy().ready/authenticated` is Privy's browser authentication state.
2. `useWallets().ready/wallets` is connected-wallet hydration for wallet actions.
3. Regent's server session and `SessionAuthority` exist only after server-side
   verification and product authorization. A sign-in lasts 30 days from the last
   bind or refresh (founder, 2026-09-28): the session cookie's `max_age` sets the
   limit, and `SessionAuthority` reads the same value and treats an older bound
   row as reset.

Never use a missing token, an empty wallet list, `walletsReady: false`, bridge
import failure, a timeout, or a rejected sync as evidence that Privy logged the
user out. Those states are unknown or unavailable, not `authenticated: false`.
Wallet hydration must not suppress a distinct wallet-button press or gate auth reconciliation. Resolve the requested wallet interaction and report its own outcome.

| Privy state | Existing Regent session | Reconciliation |
| --- | --- | --- |
| not ready, unavailable, or failed to sync | either | Preserve it silently. Do not POST/DELETE a session or reload. |
| ready and authenticated | signed in | No session mutation. Token and wallet hydration continue independently. |
| ready and authenticated after explicit login | anonymous | Obtain the required proofs, verify them server-side, establish one local session, then replace the document. |
| ready and explicitly unauthenticated | signed in | Revoke the local session once, then reload once. Wallet readiness is irrelevant. |
| ready and explicitly unauthenticated | anonymous | No-op. |

Re-read the current document/session marker immediately before destructive
reconciliation. An async continuation from a replaced document owns nothing.
Share concurrent deletion work and gate reload per document so explicit logout
and provider reconciliation cannot delete or reload twice.

Passive reconciliation is background work, not a user action. Bridge import,
readiness, token hydration, wallet hydration, timeout, and sync failures should
be recorded only through redacted diagnostics; they must not produce a global
account-error toast. Show auth feedback only when an explicit user action such
as Sign in, Sign out, link, or unlink actually failed at the boundary that action
promised.

## Token and persistence boundary

- The access token proves authentication and session identity. Verify its
  signature, issuer, audience, expiry, subject, and session claims on the server.
- The identity token carries linked identity/profile data. Verify it with the
  identity-token path, bind it to the same Privy user, and do not require an
  access-token-only session claim from it. If it includes an optional session
  claim, require it to match.
- `getAccessToken()` may refresh a token; null or a transient failure is not a
  logout signal while Privy remains authenticated. Use bounded backoff only when
  a protected request actually needs a refreshed token.
- Browser `authenticated` state controls presentation and reconciliation. It is
  never sufficient authorization for a protected server action.
- Reconciliation is not profile synchronization. Do not write user, wallet, or
  profile tables on hook hydration or every page load. Any necessary product
  record creation/linking belongs to the explicit, verified session-establishment
  action and must be idempotent.
- A stable same-account page load must not rotate cookies/CSRF state, renew the
  local session, write the database, or reload merely because hooks rendered.
- Linked wallets are profile evidence; connected wallets are transaction
  providers. Neither is final onchain ownership truth.

## Explicit logout

When provider logout must continue in a replacement document:

1. Write and read back a short-lived, single-use handoff before local deletion.
2. Revoke the Regent session first. If revocation fails, do not reload or call
   provider logout; show a retryable error.
3. Reload once immediately after successful revocation so anonymous UI does not
   wait for LiveView timing.
4. The new document consumes the handoff once and makes one bounded provider
   logout attempt. Stale handoffs must expire and may not create reload loops.
5. Import, readiness, timeout, or provider-logout failure after successful local
   revocation is best-effort cleanup. Keep the anonymous UI and do not tell the
   user that successful sign-out failed.

Login, logout, and recovery attempts should be single-flight. Scope retry budgets
to one operation and reset them after a stable success; do not use a permanent
page-lifetime latch that makes later recovery impossible. After any `await`, use
current provider callbacks/state rather than stale React captures.

## Browser checks before release

The template's sign-in test (`mix test`) covers only the server step that saves
the account after sign-in. Before a sign-in change ships, a person also
runs these cases in a browser, with real Privy and a browser-extension wallet, on
an origin the Privy application admits, and says in the report which were run:

- signing in while the access token or wallets are still loading;
- an empty connected-wallet list, which must not sign the person out;
- the signed-out state showing before the wallet is ready;
- a bridge that fails to load, get ready or sync, keeping the local session;
- background reconciliation and clean-up after sign-out failing without any
  message on the page;
- handoff storage that is unavailable or unconfirmed, and a failed local DELETE;
- sign-out racing automatic reconciliation, a quick double click, and a page
  replaced mid-flight: one deletion and one reload;
- a change of account or selected wallet, which is not a sign-out;
- the server refusing forged, expired, wrong-audience, swapped-subject and
  mismatched-session proofs (send them with `curl`; each refusal raises
  `ash_template.privy.session_refused.total` with its stage and reason);
- logs that record the step and time taken but never tokens, cookies, raw linked
  accounts, authorization headers or provider objects.

Until a person has run sign-in, refresh, protected navigation, sign-out and
reload with real Privy and a real wallet, say the change is unchecked. Use a free
port the Privy application admits, and never stop an unrelated server to claim a
preferred one.

Official references:

- https://docs.privy.io/basics/react/setup
- https://docs.privy.io/wallets/wallets/get-a-wallet/get-connected-wallet
- https://docs.privy.io/authentication/user-authentication/tokens
- https://docs.privy.io/user-management/users/identity-tokens
