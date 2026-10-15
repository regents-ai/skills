# Version-aware documentation workflow

## Find the project and available tools

Read the applicable `AGENTS.md`, `mix.exs`, `mix.lock`, formatter, toolchain pins, and
CI. In a monorepo locate the app that owns the requested route/resource. In an umbrella,
check where the lockfile and dependencies actually live. The inventory script prints
candidate roots and warns about missing files; it does not choose one for you.

Use the installed dependency checkout for Git/path dependencies. A package's `main`
branch can be ahead of the installed release. A HexDocs default page can describe a
different release from the next page you click. Check the displayed version, not only
the URL. Do not claim a latest-release compatibility matrix from this pack's snapshot.

## Search order

1. Relevant existing implementation and tests, then applicable dependency usage rules.
2. Installed module docs/source and the exact dependency's DSL reference.
3. Official versioned HexDocs; changelog or source tag for a suspected behavior change.
4. Community examples only as leads, checked against the sources above.

Look for both `deps/<package>/usage-rules.md` and the `usage-rules/` directory. Some
packages split nearly all useful content into sub-rules. Read the relevant files;
reading a five-line top-level summary is not sufficient. Avoid loading every rule in
the ecosystem for every task.

Regent sites install `usage_rules` as a development dependency (template
`platform/mix.exs`, `>= 1.2.8` for EEF-CVE-2026-82710). Its block at the end of the
app's `AGENTS.md` links every Ash, Phoenix and Elixir rule file in `deps/`. Look up
the locked version's docs with it:

```sh
mix usage_rules.docs AshPhoenix.Form.submit/2
mix usage_rules.search_docs "atomic update"
mix usage_rules.search_docs "AshPhoenix.Form submit" --query-by title
```

Leave `-p` off inside a project: search then covers exactly the locked versions. On
1.2.8, `-p ash` searches the newest release on Hex whatever the lockfile says, and
`-p ash@3.33.11` finds nothing, despite the task's help. Narrow a search with the
module name in the query instead. Read the actual result, not merely its search
summary. Keep searches to public symbols, not private code or
customer data.

If Tidewave or another development MCP is already connected, inspect its available
tools and use documented read-only documentation/log queries. Do not assume tool names,
start or stop the user's server, or execute data-changing runtime evaluation just to
inspect docs. Fall back to local source and HexDocs when the runtime tool is absent.

## Keeping the rule links in step

The site's `mix.exs` holds the `usage_rules:` config; `mix usage_rules.sync` rewrites
only the marked block at the end of `AGENTS.md`, and `mix precommit` runs
`usage_rules.sync --check`, so a dependency change that adds or drops a rule file
fails until the block is synced. Change the config, never the block. Sites copy the
template's config:

```elixir
usage_rules: [
  file: "AGENTS.md",
  usage_rules: [
    {:usage_rules, sub_rules: []},
    {:usage_rules, sub_rules: :all, main: false, link: :markdown},
    {:ash, link: :markdown},
    {~r/^ash_/, link: :markdown},
    {:phoenix, sub_rules: ["phoenix", "liveview", "html"], link: :markdown},
    {:req_llm, link: :markdown}
  ]
]
```

The usage_rules docs section is written out in full; everything else is a link, so the
file stays short. Phoenix's `ecto` and `elixir` rules are left out: Ash owns data
access, and usage_rules already links its own Elixir rules. The tool does not write
skills here. Keep the six `ash-*` names reserved for this authored pack; if generated
skills are ever wanted, give them distinct names such as `ash-upstream-rules`.

When adding it to a site: the dependency is `only: :dev` where `mix precommit` runs in
dev, as in the template, and `only: [:dev, :test]` where `preferred_envs` runs
precommit in test, or the check cannot find the task. The first `mix usage_rules.sync`
asks a yes/no question, so run it with `--yes`; `--check` asks nothing. Put the block in
the `AGENTS.md` beside the site's `mix.exs` so its `deps/` links resolve.

## Record only useful evidence

For a disputed API, note the installed version, module/function or DSL section, and
what was verified. Do not archive entire documentation pages in every PR. Refresh
knowledge when the lockfile changes, a missing API appears, or a documented bug fix
matters. An unsuccessful search is a reason to inspect source, not to invent syntax.

Sources: [source index](source-index.md), especially S01, S07, S08, S09, S10.
