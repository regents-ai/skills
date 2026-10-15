# Verified Regents reference

## Public result and limits

The saved Is Agentic report at
https://is-agentic.com/api/v1/report?url=regents.sh returned **98/100** with
`scanned_at: 2026-09-17T08:06:46.676Z`, after the Regents-only production release
`5417287311114a7bd5e5b98bdfe2bd30fefe8522`. The marketing/lab homepage declares
Business. This is not a claim that all App/API checks pass, nor a security audit.
Brand search and fuller organizational schema remained real limitations; no postal
address, auth protocol or MCP server was fabricated to obtain the score.

The earlier fully encoded API query returned an older stored result. Verify the
returned timestamp and canonical target, not the spelling of one cached request.
The public stream emits a raw Ora score as well as archive information; that raw
number is not Is Agentic's normalized score. Wait for the stored final report.

Local evidence is under workspace `artifacts/regents-agent-readiness/`. Its release
manifest identifies all staged sources/shared pins. Public-page and owner-mapping
readbacks were separate from browser rendering and schema validation. No test
database was created. Do not put owner records or credentials into skill examples.

## Source map

Relative to `repos/regents` (or its reviewed readiness worktree/revision):

| Behavior | Source |
| --- | --- |
| Accept selection, Vary merging, public-document Markdown, recovery bodies | shared `elixir-utils/agent_access` (`RegentAgentAccess`), plugged in `platform/lib/ash_platform_web/endpoint.ex` |
| Public sources, configured origin, schema and sitemap data | `platform/lib/ash_platform_web/public_documents.ex` |
| Docs/trust/discovery responses | `platform/lib/ash_platform_web/controllers/public_pages_controller.ex` |
| Authoritative public Markdown and read-API definition | `platform/priv/public/` |
| Safe missing-page responses | `platform/lib/ash_platform_web/controllers/error_html.ex`, `error_md.ex`, `error_json.ex` |
| Actual route/pipeline ownership | `platform/lib/ash_platform_web/router.ex` |
| Shared metadata consumer | `platform/lib/ash_platform_web/components/layouts/root.html.heex` |
| Frozen YAML contract headers | `platform/lib/ash_platform_web/plugs/contract_headers.ex` |
| Derived CLI major/digest | `scripts/sync-platform-contract-digest.mjs` in `regents-cli` |

The shared presentation owner is
`repos/design-system/regent_ui/lib/regent/agent_metadata.ex` on the approved
`feat/agent-readiness` branch until its owner integrates that commit. The matching
Regents consumer lives on `feat/regents-agent-readiness`. Check branch availability
and the approved commit before pinning it; do not assume local work is published.

## Non-transferable product details

Regents projects only its explicit public documents before the router; the documents
are database-free. That placement is not a template for authenticated/database-backed
pages in other products. Its claims API is owner-authorized historical data, not an
anonymous ownership lookup or proof of current token holdings.

Keep the existing YAML bytes separate from the new documented read-only OpenAPI
scope. Header major/digest describe the actual YAML. The then-published npm CLI was
older than the source checkout: source/header alignment did not publish a package
or establish every CLI command's production acceptance.

The shared head consumes the product's structured-data map and capability flags.
Metadata encoding is reusable; entity facts, route allowlists, deployment pins,
identity policies and native tool registration are not implicitly transferred.
