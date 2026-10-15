# Pages and components re-check the session before every push and result

A server push (`handle_info`: a PubSub notification such as a points award or a
Credits change) and a background result (`handle_async`) arrive with no navigation or
event in between. A socket idle past the sign-in lifetime would otherwise read and show
fresh private data with the actor it saved at mount. The session module that holds a
signed-in socket attaches `:handle_params`, `:handle_event`, `:handle_info` and
`:handle_async` hooks that re-read the lease (`leased_account/2`) before the page sees
any navigation, event, message or result:

- Current: `{:cont, socket}` with the principal rebuilt from the account that read
  returned, so the page's handler builds its actor from the refreshed account.
- Lapsed: `{:halt, socket}` with the principal withdrawn and
  `signed_out_reason: :expired`. What arrived is dropped, the page renders signed out
  and says the sign-in ended, and every later message or result meets the same check.
  A navigation (`:handle_params`) goes to the public root instead. No timer, no
  polling.
- A broadcast that reaches every open page often and carries no account data may go
  straight through, so it costs no reads. Only such a message may skip the check.
- Background work goes through `start_async/3`: `assign_async` and `stream_async`
  results never reach `:handle_async` hooks, so they would skip the check.

The rest of this note covers components, whose events and results never reach the
page's hooks.


A page's `attach_hook(:session_authority_event, :handle_event, ...)` never runs for an
event targeted at a LiveComponent (`phx-target={@myself}`, `pushEventTo`). A component
that acts with an actor built from its assigns keeps acting for the person the page
was given at mount, even after that session is signed out elsewhere. Every component
that handles events and acts for a person carries its own check, and acts on the
account as it reads at that event, not on wallets or an actor built earlier. The
reference is ash-template `AshTemplateWeb.Live.Session.check_component_lease/2`.

1. **The page keeps its lease.** The `on_mount` that loads the person assigns
   `session_lease: nil`, and the code that holds a signed-in session assigns the lease
   it already re-reads on its own events (`%{lineage: ..., account_id: ...}`).
2. **One shared check.** The session module exposes a function that attaches a
   `:handle_event` hook and a `:handle_async` hook to the component socket. LiveView
   allows `:handle_event`, `:after_render` and `:handle_async` hooks on components.
   - `lease: nil` (signed out): `{:cont, socket}`.
   - The lease still resolves (the same `leased_account/2` read the page uses):
     `{:cont, take_account.(socket, account)}` with the account that read returned.
     The check never reduces that account to a truth test.
   - Lapsed: `send(self(), {SessionModule, :component_lease_lapsed})` and
     `{:halt, %{}, socket}` for an event, `{:halt, socket}` for a result, which drops
     it. The empty reply answers reply-style events (a wallet
     step asked for gets nothing to send); the page's own `:handle_info` hook takes
     the message, re-reads the lease and withdraws the principal, so the page renders
     signed out. The component runs in the page's process, so `self()` is the page.
3. **Each component opts in** by calling the check first in `mount/1` with its own
   `take_account(socket, account)`, and assigns `lease` in every `update/2` clause
   that takes the page's assigns. A clause that picks fields (`Map.take`, pattern
   match) must name `lease`. `take_account` rebuilds everything the component acts
   with from the account (linked wallets, the actor, then any review built from
   them), and `update/2` calls the same function with the account the page passed,
   so there is one derivation, no second cache and no debounce. A component takes
   `account` from its page, never a prebuilt actor or wallet list.
4. **Every call site passes it:** `lease={@session_lease}`, through any function
   component in between (`attr :lease, :map, required: true`). A component given no
   lease fails on its first event instead of acting, so a missed call site shows at
   once. A page whose component acts for a stand-in account (a local lab) passes
   `lease={nil}`: the session is not the account it acts for.

Check: `grep -rl ":live_component" lib` lists every component; each one with a
`handle_event` or `handle_async` that reads or writes for a person needs steps 3 and 4.
Verify with a scratch test, inside a sandbox that rolls back, that runs the hooks
through `Phoenix.LiveView.Lifecycle` on a socket mounted by the session module: a push
and a result while current (continue, with the account as it reads now), after a
same-account refresh (unchanged), and after the sign-in's `updated_at` is moved past
its lifetime (halt, principal withdrawn, `signed_out_reason: :expired`; for a component,
halted and the page told). Run it once against the old code to see it fail.

The page's disconnect broadcast on sign-out reaches only the node that handled it
unless the site's nodes are clustered; this check covers every event either way.
