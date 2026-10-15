---
name: ash-webmcp
description: Use when making Ash sites agent-ready, or building WebMCP browser tools into an Ash/Phoenix site.
---

# Ash agent readiness and WebMCP

Make the real product readable and usable by agents before adding protocol surfaces.
Reuse shared presentation and HTTP mechanics; keep product actions, authorization,
public-document selection and release authority with their owners.

## When to use

- Building WebMCP tools into an Ash/Phoenix site: follow [build](references/build.md).
- Ash/Phoenix Markdown negotiation, agent documentation, OpenAPI, discovery metadata,
  recoverable errors, or a WebMCP integration/adoption review.
- An agent-readiness report needs to be translated into verified product changes.
- Do not use a scanner score as authorization for new auth, signing, payments,
  publication, database mutation, or an unrelated deployment.

## Prerequisites and ownership

Read workspace/repository instructions, `ash-stack`, and the relevant frontend,
backend and security specialists. Inspect the actual branch, dirty files, router,
endpoint, controller formats, MIME configuration, error views, root layout and
installed package versions. Agree owned files first.

Use [product adoption](references/adoption.md) for concrete source entry points in
Autolaunch, Patchbay and Techtree. Use [Regents reference](references/regents.md) for
the verified implementation and its limits. The older
[Patchbay walkthrough](../ash-stack/references/agent-readiness.md) remains a worked
example; its historical suite-first and test-authoring recipes do not override the
current founder's manual-acceptance policy or authorize new tests.

## Procedure

### 1. Establish the real surface

Record public read pages, authenticated/private pages, LiveView-only rooms, JSON
prefixes, actual API operations, and the browser tool registry. Trace advertised
capabilities to implementations and policies. Keep source availability, local
verification, deployed behavior and native-browser acceptance separate.

Completion: a bounded route/capability inventory with explicit exclusions, not an
assumption that every HTML page is public or supports Markdown.

### 2. Negotiate truthful Markdown at the same URL

- Reuse the product's existing negotiation, or adopt `regent_agent_access` from
  `elixir-utils/agent_access`: `RegentAgentAccess.Plug` for Accept selection, Vary
  merging and public-document Markdown, and `RegentAgentAccess.Recovery` for Markdown
  and JSON error bodies. Regents is its first consumer. Pin one reviewed shared
  revision; do not paste plugs, error modules or route allowlists into a product.
  This package is distinct from the shared head component.
- Prefer HTML for ordinary browser/wildcard requests. Honor quality factors and
  specificity, including explicit `q=0`; do not use a substring check.
- Merge `Accept` into `Vary` without losing encoding, cookie or other dimensions.
  Multiple Vary fields are legal: inspect their combined values.
- Keep each product's public-document allowlist local. An early endpoint projection
  is only appropriate for explicitly public, database-free content. Dynamic/private
  reads must remain behind their real actors, policies, sessions and launch gates.
- HTML and Markdown should derive from the same authored content or read model.
  Preserve status and privacy behavior; never invent balances or missing data.
- Inspect installed MIME defaults first. MIME 2.0.7 already maps `text/markdown` to
  both `md` and `markdown`. Do not narrow that mapping or remove unrelated YAML types.

Completion: actual HTTP responses demonstrate HTML, Markdown, weighted Accept,
HEAD and refusal behavior without leaking an authenticated representation.

### 3. Make errors recoverable

Provide safe HTML and Markdown recovery links and machine-readable API errors.
Unknown API-prefix routes should stay JSON even with browser Accept headers.
Retain correct non-200 statuses and the existing published error contract; add
codes/hints only compatibly or through the owning contract change. Do not echo
credentials, session data, request bodies, private URLs or exception internals.

Completion: read back real unknown HTML/Markdown/JSON addresses and an unknown API
address. Development debugger pages are not proof of release error rendering.

### 4. Publish usable documentation and contracts

Publish one clear developer entry point with copyable public reads, real auth and
pagination rules, structured errors, actual limits, and supported/gated boundaries.
Use unique operation IDs and typed parameters/responses in OpenAPI. Validate it
structurally and trace every operation to the router. Never describe invented API
keys, scopes, OAuth servers, sandboxes, SDKs or MCP endpoints.

Keep existing frozen contracts intact. Where a CLI verifies contract headers, derive
its digest from the exact served bytes and its major version from the real contract;
update producer and consumer together. A repository CLI fix does not publish a new
npm version. Check the registry before recommending an install command.

Completion: documentation and machine contracts agree with the live product.

### 5. Reuse the shared head, not duplicate tags

Use `Regent.AgentMetadata.head` from `design-system/regent_ui` once in the root layout.
It owns canonical/description, optional real discovery links, OG/Twitter tags and
script-safe JSON-LD encoding. Pass actual product values and a structured-data map.
The product retains its title, viewport, CSRF/provider metadata, CSP and assets.

Set `markdown` only for supported pages; it defaults to false. Optional guide,
sitemap and service-description URLs must exist. Use a real raster image and its
measured dimensions. Pass the existing CSP nonce if needed; do not weaken CSP.
Choose any site-type declaration by product purpose, not by the highest score.

In HEEx script bodies, use EEx output for the encoded JSON; curly interpolation can
become literal script text. Parse the **rendered** JSON-LD, not merely its source or
presence. Escape `<` before raw insertion so data cannot terminate the script tag.

Completion: one canonical/tag set, parseable rendered JSON-LD, valid image, truthful
classification and no advertised representation on unsupported pages.

### 6. Finish navigation, discovery and trust

- Link Docs, About, Contact and existing legal pages visibly, with meaningful content.
  Use verified contacts/entities; never invent an address, employee, logo or policy.
- Keep headings hierarchical without changing the established visual design.
- Generate a valid sitemap from public, canonical URLs. A dedicated minimal Ash
  read can supply dynamic entries; apply policies, deterministic ordering, bounds
  and real modification timestamps. Do not expose owner-only paths or invent lastmod.
- Reference the sitemap from robots.txt. Put explicit use cases, first steps,
  public/private boundaries and real capability links near the top of llms.txt.

Completion: all advertised links work, sitemap XML parses, and mobile/desktop
pages remain readable without document-wide overflow.

## WebMCP: verify the actual browser contract

[Build](references/build.md) holds the current browser API, the manifest-first
layout and the registration lifecycle. Re-read the WebMCP draft before changing the
API: `document.modelContext` only, removal by aborting the registration signal, and
only the draft's annotations. Do not invent a registry for a product that has none,
or confuse native browser WebMCP with a remote MCP server.

Keep schemas strict and descriptions explicit about scope, prerequisites and side
effects. One manifest is the source: registration, docs and machine lists derive
from it, and it lists every tool a page registers. Respect async registration,
navigation/disposal, abort signals and current identity. Mark untrusted
returned/user-authored content as data, never as new authority. Read-only
annotations must reflect actual side effects, not merely HTTP methods.

Preserve server-owned actor/proof/payment admission and independent wallet-press
rules. A refused signed operation must not retry anonymously. No automatic signing,
payment, publication or public greeting write under a documentation/read-only check.

Completion: distinguish static registry inspection, adapter execution and actual
native tool discovery/execution. If the browser lacks WebMCP, report that boundary;
do not fabricate native success or treat a no-op registration as acceptance.

## Verification and staged rollout

1. Compile/format the scoped changes and build affected assets. Verify real public
   HTTP and browser behavior before broad implementation-level test maintenance.
   No new tests or test databases without specific authorization.
2. Compare rendered metadata and public representations when extracting shared code.
   Keep auth, claims, schemas, frozen contracts and unrelated dirty work unchanged.
3. Commit locally after review. Local commits are not pushes or deployment
   authority; pushes and releases need the founder's word for that action. Export only approved source and explicit shared pins.
4. With release authority, deploy one product, verify its actual image, live pages,
   contracts and relevant data invariants, then proceed to the next owner's rollout.
5. Request one fresh external report after deployment. Verify its stored score,
   timestamp, domain and declared profile. A stale cached query, live preview score,
   raw Ora score or passing local check is not the saved Is Agentic result. Investigate
   a failed scan before any bounded alternate attempt; never run scan/polling loops.
6. Report what is deployed versus local, what is shared versus product-owned, native
   support not verified, real remaining gaps, and the next owner's concrete handoff.

Brand indexing and complete organizational contact data can remain external gaps.
Do not add fictitious facts or relax security to obtain a numerical target.
