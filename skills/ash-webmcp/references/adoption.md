# Product-owned adoption handoff

These are inspected source entry points, not claims that a particular commit is
live. Re-read each repository's AGENTS.md, branch/status and current implementation.
Other agents may already have implemented parts of this work. Do not overwrite it.

## Shared boundary

Use `Regent.AgentMetadata.head` from the reviewed design-system revision. Replace
local equivalent tags instead of adding a second set. The caller supplies brand,
page URLs, image dimensions, classification, actual discovery routes and JSON-LD.
Do not copy Regents' Business declaration into products merely to raise scores.

For HTTP negotiation and recovery, add `regent_agent_access` from
`elixir-utils/agent_access` at one pinned revision and follow its README: the plug
goes in the endpoint just before the router, and the product's Markdown and JSON
error modules call `RegentAgentAccess.Recovery`. It was extracted from the proven
Regents implementation with byte-identical responses and is on `elixir-utils` main
from revision `6565ba2ffa49a27b6f2a063e9cf1c51b5e705fe3`; Regents production runs it.
Do not duplicate plugs/error renderers across products.
Keep public-document selection, actors, queries, routes and gate placement local.
A generic early plug must not bypass another app's authentication or database policy.

Each product owner applies the five deliverables: same-URL public Markdown and
recoverable errors; useful developer docs/real OpenAPI; canonical/share/schema and
sitemap; actionable llms.txt; visible trust/navigation and correct headings.
Preserve already-working surfaces instead of rebuilding a Regents-shaped site.

## Autolaunch — `repos/autolaunch`

Read:
- `platform/lib/autolaunch_web/router.ex`, `endpoint.ex`, `autolaunch_web.ex`.
- `platform/lib/autolaunch_web/components/layouts/root.html.heex`.
- `platform/assets/js/public_tools.ts` and its actual import/registration path.
- `platform/priv/static/llms.txt`, existing YAML contract and `cli/` contract checks.

Observed entry points include `/api/v1/auctions`, `/api/v1/auctions/:id`,
`/api/v1/auctions/:id/bid-quote`, `/api/v1/tokens` and treasury-security reads.
Trace controller semantics before classifying the POST quote as a write: HTTP method
alone does not establish side effects. The public browser tools deliberately omit
credentials and do not use wallet hooks; preserve that boundary and cancellation.
The shared profile tools on the same pages do use the Privy session.

Keep `Autolaunch.Prelaunch`, signed-in session authority, profile APIs, drafts,
wallet interactions, chain/currency context and frozen `contracts/v1` gates intact.
Start with public docs/marketing/read surfaces; do not project an owner portfolio or
create form through an anonymous endpoint plug. Verify the actual read-only flags
and import lifecycle before claiming native WebMCP support.

## Patchbay — `repos/patchbay`

Read:
- `platform/lib/patchbay_web/router.ex`, `md.ex` and the existing negotiation code.
- `platform/lib/patchbay_web/controllers/pages_controller.ex`, blog Markdown views,
  sitemap controller, error views and existing OpenAPI files.
- `platform/lib/patchbay_web/components/layouts/root.html.heex`.
- `platform/priv/tool_manifest.json` with `Patchbay.Forum.Capabilities` (the tool
  source), `platform/assets/js/webmcp/forum_tools.js`, `webmcpify.js` and `room_hook.js`.

Patchbay already has Markdown/controller views, trust/developer routes, sitemap and
WebMCP room infrastructure. Review and adopt the missing shared metadata rather than
replacing these with Regents modules. `/webmcp/rooms/:slug` is explicitly HTML-only;
do not advertise a Markdown alternate there. Preserve session/CSRF, forum identity,
profile requirements, wallet-author proof and payment-intent boundaries.

`/api/agent/hello` is a guarded POST, not a free read-only help action. Preserve
HelloProof admission and disclose any greeting write. Capability descriptions must
agree with global versus page-scoped registrations and actual native readiness.
Keep dynamic sitemap reads policy-scoped and bounded; do not expose private inboxes.

## Techtree — `repos/techtree`

Read:
- `platform/AGENTS.md`, `platform/lib/techtree_web/router.ex` and `endpoint.ex`.
- `platform/lib/techtree_web/components/layouts/root.html.heex`, `md.ex`,
  `controllers/pages_controller.ex` with `priv/pages/*.md`, `open_api.ex` and
  `controllers/sitemap_controller.ex`.
- `platform/priv/tool_manifest.json`, `platform/lib/techtree/capabilities.ex` and
  `platform/assets/js/public_tools.js`; `/llms.txt` is `priv/pages/llms.txt`, served by
  `controllers/agent_guide_controller.ex` with the tool table filled in.
- `platform/lib/techtree_web/controllers/skill_controller.ex` and the public API
  controllers for bootstrap, catalog, objects, climbs, publications and keys.

Techtree follows [build](build.md) for five read-only, sign-in-free site tools
(`techtree_start`, `techtree_climbs`, `techtree_climb`, `techtree_results`,
`techtree_result`), each a thin read of an existing `/api/v1` route or `/skill.md`, all
`readOnlyHint` and `untrustedContentHint`. Live since main `825ddb5` (2026-09-27) and on
`release/v0.3.0`. Every browser page sends `Permissions-Policy: tools=(self)` and sets
`data-webmcp-status` on the html element. There is no origin-trial token yet, so
ordinary Chrome needs the WebMCP flag. Publishing stays with the CLI and its key: a
Privy profile never grants publication-key authority; preserve publication rate limits,
integrity checks and frozen proof bytes.

The home, About, Contact and Privacy pages answer `text/markdown` through Techtree's own
`md.ex`, not `regent_agent_access`. The shared profile tools install only beside
`[data-regent-profile]`, which no page renders since the profile page was withdrawn, so
the manifest leaves them out. The strict CSP and page-specific provider permissions
must remain intact; structured data is inert data, not an excuse to add executable
inline scripts. Leave retired profile and development preview routes retired. No paid
model runs or publication for readiness verification. Techtree's remaining steps onto
the template are in the workspace's `docs/backlogs/techtree.md`.

## Per-owner acceptance and release

For each product, record the actual URLs, auth boundaries and representations before
editing. Complete and review its scoped changes; verify real HTTP, structured data,
image, navigation and mobile/desktop behavior. Validate native tools only where the
browser supports them. Record capability boundaries when it does not.

Obtain that product's release approval, stage exact shared pins, deploy only that
product and read it back before the next rollout. The Regents score does not prove
another product ready, and this handoff does not authorize three deployments.
