# Build WebMCP tools into an Ash site

WebMCP lets a page expose tools to the browser's agent. Protected agent operations
authenticate the agent through per-request SIWA proof and resolve its current owner
pairing. A signed-in customer's tab does not supply agent authority. A hosted `/mcp`
endpoint is a separate transport and must enforce the same product authorization.

Checked against the WebMCP Editor's Draft at webmachinelearning/webmcp `729ae01`
(2026-09-26) and Chrome's WebMCP docs (updated 2026-09-21). The API changed several
times in 2026; re-read the draft before relying on anything below.

## The browser API today

```ts
const scope = new AbortController()
await document.modelContext.registerTool(
  {
    name: "search_threads",          // 1–128 chars of [A-Za-z0-9_.-], unique per page
    title: "Search threads",
    description: "Search public threads by words. Reads only; needs no sign-in.",
    inputSchema: {type: "object", properties: {q: {type: "string"}}, required: ["q"], additionalProperties: false},
    annotations: {readOnlyHint: true, untrustedContentHint: true},
    async execute(input, {signal}) { /* returns any JSON-serializable value */ },
  },
  {signal: scope.signal},
)
scope.abort() // the only way to remove it
```

- The entry point is `document.modelContext` (secure pages only). It moved there
  from `navigator` on 2026-05-27. Detect it with `"modelContext" in document`; use
  nothing else. No `navigator` branch and no polyfill.
- `registerTool` returns a promise. It rejects on a duplicate name, a bad name, an
  empty description, a denied `tools` permission or a page that is not origin-keyed.
- `provideContext`, `clearContext`, `unregisterTool` and `requestUserInteraction`
  are gone from the draft. Remove a tool by aborting the signal it was registered with.
- Annotations are `readOnlyHint`, `untrustedContentHint`, `consequentialHint` and
  `debugging`, all default false. MCP's `destructiveHint`, `idempotentHint` and
  `openWorldHint` are not WebMCP; do not send them. There is no `outputSchema`.
- `execute(input, {signal})` gets the parsed input and the agent's abort signal.
  Whatever it returns is JSON-stringified for the agent. A rejected promise reaches
  the agent as a bare failure, so return a result that says what went wrong and
  how to fix the call instead of throwing.
- The browser does not validate input against the schema (JSON Schema 2020-12).
  Validate in `execute` and again on the server.
- `document.modelContext` fires `toolchange`, `toolactivated` and `toolcancel`.
  `getTools()` lists what the browser holds; use it to confirm registration.
- Declarative forms (`toolname`, `tooldescription`, `toolparamdescription` on a
  `<form>`) are still a TODO in the draft. Use the imperative API.

Headers and browsers:

- Send `Permissions-Policy: tools=(self)`. Never send `Origin-Agent-Cluster: ?0`.
- Chrome runs WebMCP as an origin trial ("WebMCP", Chrome 149–156). The token is
  public, tied to one host and expires; keep it beside a comment naming its host and
  expiry, and send it as an `Origin-Trial` response header next to the
  Permissions-Policy, so Chrome knows it before reading `tools`. Locally, turn on
  `chrome://flags/#enable-webmcp-testing` instead. Edge 150 has a trial too;
  ChatGPT's in-app browser supports it; Firefox and Safari do not.

## How the pieces fit in an Ash site

```
priv/tool_manifest.json ──► MyApp.Capabilities (compile time)
        │                      ├─► /capabilities JSON, developers table, hosted MCP list
        │                      └─► llms.txt and docs pages
        └─► assets/js/webmcp/tools.ts ──► document.modelContext.registerTool
                                              │ execute(input, {signal})
                                              ▼
                     prepare exact request → existing SIWA signer
                     → named JSON operation (credentials omitted, signal)
                                              ▼
                     SIWA verification → current pairing → Domain interface (user + agent)
                                              ▼
                                         Ash policies decide
```

### 1. One manifest is the source of truth

Keep every tool the site registers in one JSON file, read by Elixir at compile time
and imported by the browser code. Registration, docs and machine lists are derived
from it; nothing is typed twice. Patchbay's `platform/priv/tool_manifest.json` with
`Patchbay.Forum.Capabilities` is the working reference.

Each entry: `name`, `title`, `description`, `input_schema`, `annotations`, plus the
facts docs need: `requires` (`none`, `siwa_and_pairing`),
`state_changing`, `payment` (`none`, `moves_usdc`), the HTTP route behind it, and
`scope` (`site` or the page that registers it). Include page-scoped tools and the
shared profile tools too, so the published list never denies a tool a page registers.

```elixir
defmodule MyApp.Capabilities do
  # Read once at compile time from the project tree.
  @manifest_path "priv/tool_manifest.json"
  @external_resource @manifest_path
  @manifest Jason.decode!(File.read!(@manifest_path))
  def manifest, do: @manifest
  def tools, do: @manifest["tools"]
  def site_tools, do: Enum.filter(tools(), &(&1["scope"] == "site"))
end
```

The browser side keeps only the `execute` functions; the definition comes from the
manifest:

```ts
import manifest from "../../../priv/tool_manifest.json" with {type: "json"}
const tools = manifest.tools.filter(tool => tool.scope === "site").map(tool => ({
  name: tool.name, title: tool.title, description: tool.description,
  inputSchema: tool.input_schema, annotations: tool.annotations, execute: executors[tool.name],
}))
```

### 2. A tool is a thin door to an Ash action

- Protected agent executors use the manifest's signed HTTP operation. The controller
  resolves the verified agent and current pairing, then calls the same product
  domain interface used by the human UI (`MyApp.Forum.post_reply(input, actor: actor)`).
  Ash policies enforce ownership and membership for that actor. Do not forward an
  agent call to a LiveView event that inherits the customer's session authority.
- Identity never comes from tool input or browser cookies. Keep the verified agent
  and its benefiting user separate through the product action and stored outcome.
- Use the shared signed transport described below: it omits credentials, refuses
  redirects and sends the exact prepared bytes with the supplied proof. Public
  reads also omit credentials. Pass the agent's `signal` through.
- A write cancelled after the request left returns `{outcome: "unknown"}` with how to
  check, never "cancelled".
- Keep results small and bounded. Refuse rather than truncate data into a lie.
- A refusal is `isError: true` with the site's one error shape as `structuredContent`:
  `{error: {code, message, hint}}`, the same as its JSON errors, plus the message and
  hint as the text content. Anything more (field messages as `details`,
  `retry_after_seconds`) goes inside `error`. No other refusal shape, in page tools or
  hosted MCP tools.

### 3. Mark what a tool does, truthfully

- `readOnlyHint: true` only when the action changes nothing, whatever the HTTP method.
- `untrustedContentHint: true` whenever the result carries text customers or agents
  wrote. Put that text under a field the result labels as data, never as instructions.
- `consequentialHint: true` for anything that moves money, publishes, or cannot be
  undone, so the agent asks the customer first.
- The description says when to use the tool, what it needs (sign-in, profile,
  wallet) and whether money moves. Schemas are typed with `additionalProperties: false`.

### 4. Wallets and payments

A tool marked `payment: moves_usdc` takes the payment through the shared
`RegentPayments.Purchase`, as the site's pages and HTTP doors do (`payments`).

A customer-wallet transaction goes through the same wallet step as its button:
the server prepares the transaction, the customer's active linked wallet approves
it, and the existing transaction rules apply. Every distinct press reaches that
wallet; never queue or deduplicate it. SIWA request authentication is separate:
the named agent uses its own existing signer, and a refusal never retries unsigned.

### 5. Register once, remove cleanly

- Site-wide tools: register once per document from the app entry, on `pageshow`,
  and abort on `pagehide`, so the back/forward cache cannot leave duplicates. LiveView
  navigation keeps the document, so they stay registered.
- Page-scoped tools: a LiveView hook with `phx-update="ignore"` registers in `mounted`
  and aborts in `destroyed`. `reconnected` re-registers.
- Give each group one `AbortController`. If any registration in the group fails,
  abort the group so the page never holds half a set.
- After registering, read `getTools()` and show the result in a quiet status
  attribute (`data-webmcp-status`: `connected`, `unsupported`, `error`), not in
  customer copy.

### 6. The shared profile tools

The legacy shared profile tools use the customer's Privy session. That behavior
does not meet the signed-agent contract. Do not register those executors as agent
tools during adoption. Expose only product-authorized profile operations through
signed routes that retain the agent and beneficiary; keep account-security actions
owner-only. List every supported replacement in the manifest with `scope: "site"`.
The human profile UI may continue using its authenticated owner session.

## Checks

1. Compile and typecheck. Tests only where the founder agreed them; a fake
   `modelContext` proves the adapter, not the browser.
2. The HTTP routes behind each tool: public reads, signed agent requests and
   unpaired/revoked/cookie-only refusals. A refused write returns a fixable error.
3. Native discovery: Chrome with the flag (or the trial token on the real host) and
   the Model Context Tool Inspector extension. The tools appear with the manifest's
    names and annotations; run each public read, then a protected read and write as
    a signed agent paired with a test beneficiary on a local server only.
4. Report which of the three you proved: the manifest and adapter, the adapter against
   the site, or the browser's own discovery and execution.

## Reference code

Patchbay, relative to `repos/patchbay/platform`:

| What | Where |
| --- | --- |
| Manifest and its Elixir reader | `priv/tool_manifest.json`, `lib/patchbay/forum/capabilities.ex` |
| Site-wide tools and executors | `assets/js/webmcp/forum_tools.js`, `forum_lifecycle.js` |
| Scoped registration with rollback | `assets/js/webmcp/webmcpify.js` (`createToolScope`) |
| Page-scoped tools in a LiveView hook | `assets/js/webmcp/room_hook.js`, `invocation_bridge.js` |
| Permissions-Policy and trial header | `lib/patchbay_web/plugs/browser_policy.ex` |
| Paid tools | `assets/js/webmcp/paid_actions.js` |

Patchbay predates parts of the current draft and of this guide: it still falls back
to `navigator.modelContext`, sends MCP-only annotations, marks site-wide tools with
`doors.page` instead of `scope`, and leaves its room and profile tools out of the
manifest. Follow this guide where they differ.

Autolaunch's historical public-read layout is a smaller manifest example:
`platform/assets/js/public_tools.ts` imports `platform/priv/tool_manifest.json`,
and `/developers` and `/llms.txt` derive their tables from it. Its legacy shared
profile executors must be replaced or omitted under the signed-agent contract;
do not copy their owner-session authority into a new agent tool.

Techtree, relative to `repos/techtree/platform`, is the smallest: five read-only site
tools in `priv/tool_manifest.json`, read by `Techtree.Capabilities` (`manifest`, `tools`,
`site_tools`) and registered by `assets/js/public_tools.js`, which records
`data-webmcp-status`; the Docs page and `/llms.txt` list them from the manifest.

The template is the signed-access reference. `priv/tool_manifest.json` includes
public discovery, signed identity and protected account, note and room operations.
`assets/js/public_tools.ts` prepares and forwards signed requests through the shared
transport; `AshTemplateWeb.Plugs.AgentWallet` resolves the agent and pairing.
Read the current manifest for exact tool coverage, and
`docs/signed-agent-access-release.md` for what has and has not been accepted. Historical product examples above are
layout references, not evidence of signed-access adoption.

## Unified Regent agent access (approved 9 October 2026)

Every protected agent tool and CLI operation uses per-request SIWA signing with
its existing signer. Public reads, discovery and pairing bootstrap remain public.
Never use ambient Privy cookies as an agent-tool fallback. The server resolves
current pairing and canonical user; retain the acting agent and enforce product
ownership. Mutations lock the exact pairing in their transaction. Queued work
rechecks before starting. Security, pairing and grant management remain owner-only.

Use `elixir-utils/agent_access/assets/signed_tools.ts`, copied by
`mix regent_agent_access.assets`, for manifest-restricted request preparation and
exact-byte forwarding. Bind it to the server's configured trusted origin. It is
transport only: signer access must be supplied and demonstrated by each runtime.
No arbitrary URL/signing proxy, browser keys, replayed proofs or automatic retries.
Declare typed inputs in `operation_input_schema`; the shared transport validates
its bounded JSON Schema subset before preparing a request. Use declared array
items and object properties instead of encoding structured product data as strings.
Opaque JSON objects must opt into `additionalProperties: true` and a byte bound.

For a product whose own proof covers exact JSON text, declare
`request_body: {encoding: "raw_json", field: "raw_body", maxBytes: 2097152}`
and require that string field. The helper validates JSON but sends its original
UTF-8 bytes. Only declared path fields may accompany it; arbitrary headers and
URLs are never accepted. Keep the product's independent proof checks on the server.

Keep logical operation IDs across retries. Preserve harmless unrelated headers by
ignoring them; validate every authority-bearing proof header strictly.

Reference source is ash-template. Its unified integration is unreleased until the
native desktop/web-agent demonstration, shared pins and coordinated deployment
pass. Source inspection and mocked broker tests are not native acceptance. Record
source, released client and deployed versions separately, along with first failure,
assistance and blocked cases. Product `/agents.md` is the contract; `/skill.md` is
the product entry and `/llms.txt` its index. Developer Skills stay separate. Link
SIWA-maintained signing guidance instead of copying the protocol here.
