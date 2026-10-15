# Operator actions

An operator is someone who changes live data outside a customer's own journey:
clearing a stopped reader, binding a deployment, hiding a reported post. No site has an
admin dashboard in production, and the template has no staff page. This is the pattern
for adding one operator action when a product needs it. Staff lists stay per site
(founder decision, 2026-09-28).

## Who is an operator

- **By default, whoever can run the deployment's release commands.** That is the only
  operator most sites need.
- **A staff web page exists only when a product needs one.** It is open to an allowlist
  of wallets. The wallet is the signed-in account's verified wallet, read from the
  session, never from the request (patchbay@ad343c6
  `platform/lib/patchbay_web/plugs/current_profile.ex:30-37`).
- The allowlist is parsed once in `config/runtime.exs`, from one setting, and read with
  `Application.fetch_env!/2`. Never read the environment on every call, and never merge
  two sources.
- Everyone else gets 404, so the page's existence is not revealed (patchbay@ad343c6
  `platform/lib/patchbay_web/plugs/require_moderator.ex:18-26`).

## Authority lives on the resource

- Every staff or operator read and write is an Ash action behind a domain code
  interface, run with an actor.
- The action's policy names the actor it admits: `actor_attribute_equals(:role, :system)`
  for a release command (run as `AshTemplate.Actors.System`), and the staff actor's
  role for a staff page.
- The plug in front of a staff page only decides who sees it. It is never the only
  place authority lives.
- Never `authorize?: false`, for staff or for commands (see
  [shared contract](../../ash-stack/references/shared-contract.md)). Patchbay's
  moderation and Techtree's catalog commands still skip policies; do not copy them.

## Release commands

Keyfleet's are the model (keyfleet@985dc31 `platform/lib/keyfleet/release.ex`,
`platform/rel/overlays/bin/clear-fleet-stop`).

- Each command is one `Release.<command>/n` function run through
  `with_release_repo/1`, which loads the app and starts only the database connection.
  Never `Application.ensure_all_started(@app)` for a one-off command: that starts the
  web server, readers and jobs beside the running site.
- It calls domain code interfaces with `actor: %AshTemplate.Actors.System{}`, which the
  policy admits (keyfleet@985dc31 `platform/lib/keyfleet/chain.ex:145-153`).
- It has one named script in `rel/overlays/bin/`, which takes its argument and passes
  it through an environment variable, never spliced into the code it evaluates:

  ```sh
  #!/bin/sh
  set -eu

  fleet="${1:?usage: clear-fleet-stop <fleet id>}"

  KEYFLEET_RELEASE_COMMAND=migrate KEYFLEET_STOPPED_FLEET="$fleet" exec "$(dirname "$0")/keyfleet" eval 'Keyfleet.Release.clear_fleet_stop(System.fetch_env!("KEYFLEET_STOPPED_FLEET"))'
  ```

- It prints what it changed, in words, and changes nothing when it has nothing to do.
- The operator runs it on the deployment: `fly ssh console --app <app> -C
  "/app/bin/clear-fleet-stop <id>"`.

## A record of what was done

- An operator change that matters writes one row in the same transaction as the
  change, naming who, what and why (patchbay@ad343c6
  `platform/lib/patchbay/forum.ex:174-197`, `forum/moderation_action.ex:22-55`).
- The row holds ids and the reason, never a copy of the content it acted on.
- Rows are never updated or deleted: the resource has create and read actions only.
- Staff read them through a staff-only read action, not a policy bypass.

## How a staff page looks

- Use `Regent.Primitives` (`button`, `field`, `notice`, `empty_state`) and the
  regent_ui panels, never bare `<button>` and `<input>` with classes no stylesheet
  defines.
- Show dates formatted and choices in words, never raw timestamps or atoms, and say
  who made each decision on record.

## Development tools

LiveDashboard, mail previews and any other development tool answer only a visitor on
this machine, and never in production. The template's wallet lab is the model:
`AshTemplateWeb.Showcase` with the `:lab` part lets `/showcase/onchain` answer only when
the showcase setting is `local` (development) and the visitor and address are both
loopback; everywhere else it is the site's own 404. A tool that must not even be
compiled into production goes inside a `dev_routes` block the site turns on in
`config/dev.exs` only, behind the same gate.
