# Primary-source index

Researched on **September 4, 2026**. These are official project documentation,
maintainer guidance, and the Agent Skills specification. No marketplace skill was
copied. The authored workflow and evaluation cases are recommendations, not claims
that the frameworks enforce these choices automatically.

**Version caution:** unversioned documentation URLs move. Even pages within one
package returned different patch versions during research. This index intentionally
records observed differences. Always replace the snapshot with the target project's
installed dependency, matching module/DSL docs, and local usage rules. A failed
versioned URL is not evidence that the package or API does not exist.

The core documentation pages displayed Ash 3.32.3, AshPhoenix 2.3.25, AshPostgres
2.13.0, Phoenix 1.8.13, LiveView 1.2.11, and UsageRules 1.2.7. No compatible release
matrix was compiled or executed.

## S01 — Ash documentation home

[Official reference](https://hexdocs.pm/ash/readme.html)

Framework and extension map; displayed 3.32.3.

## S02 — Ash domains

[Official reference](https://hexdocs.pm/ash/domains.html)

Domain organization and centralized interfaces.

## S03 — Ash code interfaces

[Official reference](https://hexdocs.pm/ash/code-interfaces.html)

Generated interfaces, arguments, and options.

## S04 — Ash.Scope

[Official reference](https://hexdocs.pm/ash/Ash.Scope.html)

Scope extraction, option overrides, callback-context propagation.

## S05 — Ash policies

[Official reference](https://hexdocs.pm/ash/policies.html)

Applicable policies, ordered checks, bypasses, read filtering.

## S06 — Actors and authorization

[Official reference](https://hexdocs.pm/ash/actors-and-authorization.html)

Actor meaning and authorization configuration.

## S07 — Working with LLMs

[Official reference](https://hexdocs.pm/ash/working-with-llms.html)

Ash-first guidance, generators, and available development tools; older sync examples require version checking.

## S08 — UsageRules

[Official reference](https://hexdocs.pm/usage_rules/readme.html)

Displayed 1.2.7; config-based sync, linked rules, optional generated skills.

## S09 — UsageRules documentation search

[Official reference](https://hexdocs.pm/usage_rules/Mix.Tasks.UsageRules.SearchDocs.html)

Project-version defaults and explicit package-version search.

## S10 — UsageRules sync task

[Official reference](https://hexdocs.pm/usage_rules/Mix.Tasks.UsageRules.Sync.html)

Inspect before performing rule generation/sync.

## S11 — Ash generators

[Official reference](https://hexdocs.pm/ash/generators.html)

Installed generator discovery and supported tasks.

## S12 — Ash actions

[Official reference](https://hexdocs.pm/ash/actions.html)

Inputs, context, execution lifecycle, and transaction hooks.

## S13 — Ash update actions

[Official reference](https://hexdocs.pm/ash/update-actions.html)

Atomic updates, deliberate opt-outs, and bulk strategies.

## S14 — Ash relationships

[Official reference](https://hexdocs.pm/ash/relationships.html)

Loading, management semantics, one-to-one uniqueness, manual escape hatches.

## S15 — Ash identities

[Official reference](https://hexdocs.pm/ash/identities.html)

Resource identities and uniqueness.

## S16 — Ash validations

[Official reference](https://hexdocs.pm/ash/validations.html)

Validation behavior and supported callbacks.

## S17 — Ash changes

[Official reference](https://hexdocs.pm/ash/changes.html)

Declarative and custom changes.

## S18 — Ash preparations

[Official reference](https://hexdocs.pm/ash/preparations.html)

Read/action-input preparation; displayed 3.32.0 when opened.

## S19 — Ash calculations

[Official reference](https://hexdocs.pm/ash/calculations.html)

Derived values and load requirements.

## S20 — Ash aggregates

[Official reference](https://hexdocs.pm/ash/aggregates.html)

Relationship summaries.

## S21 — Ash read actions

[Official reference](https://hexdocs.pm/ash/read-actions.html)

Read behavior and pagination.

## S22 — Ash error handling

[Official reference](https://hexdocs.pm/ash/error-handling.html)

Error classes and representation.

## S23 — AshPhoenix.Form

[Official reference](https://hexdocs.pm/ash_phoenix/AshPhoenix.Form.html)

Forms, validation/submission, errors, nested configuration; displayed 2.3.25 on the opened page.

## S24 — AshPhoenix domain extension

[Official reference](https://hexdocs.pm/ash_phoenix/AshPhoenix.html)

Generated form integration.

## S25 — AshPhoenix.LiveView

[Official reference](https://hexdocs.pm/ash_phoenix/AshPhoenix.LiveView.html)

LiveView helpers for Ash reads.

## S26 — Phoenix.LiveView

[Official reference](https://hexdocs.pm/phoenix_live_view/Phoenix.LiveView.html)

Lifecycle, streams, async work; displayed 1.2.11.

## S27 — LiveView JavaScript interoperability

[Official reference](https://hexdocs.pm/phoenix_live_view/js-interop.html)

Hooks, DOM ownership, cleanup and events.

## S28 — LiveView security considerations

[Official reference](https://hexdocs.pm/phoenix_live_view/security-model.html)

HTTP/mount/event authorization and disconnect behavior.

## S29 — Phoenix.LiveViewTest

[Official reference](https://hexdocs.pm/phoenix_live_view/Phoenix.LiveViewTest.html)

Interaction helpers and async completion.

## S30 — AshPostgres migrations

[Official reference](https://hexdocs.pm/ash_postgres/migrations-and-tasks.html)

Named/dev generation, squashing, snapshots, release migration; displayed 2.13.0.

## S31 — AshPostgres migration generator

[Official reference](https://hexdocs.pm/ash_postgres/Mix.Tasks.AshPostgres.GenerateMigrations.html)

Dry-run/check/dev behavior.

## S32 — Testing with AshPostgres

[Official reference](https://hexdocs.pm/ash_postgres/testing.html)

Data-layer test setup; displayed 2.12.0 when opened.

## S33 — Ash testing

[Official reference](https://hexdocs.pm/ash/testing.html)

Resource/action testing guidance.

## S34 — AshOban

[Official reference](https://hexdocs.pm/ash_oban/readme.html)

Ash background-job extension; displayed 0.8.14.

## S35 — AshOban DSL

[Official reference](https://hexdocs.pm/ash_oban/dsl-ashoban.html)

Trigger/worker configuration; displayed 0.8.12 when opened.

## S36 — AshAuthenticationPhoenix

[Official reference](https://hexdocs.pm/ash_authentication_phoenix/readme.html)

Phoenix authentication integration; displayed 2.17.3.

## S37 — AshJsonApi

[Official reference](https://hexdocs.pm/ash_json_api/readme.html)

JSON:API extension and authorization reference; displayed 1.7.1.

## S38 — AshGraphql

[Official reference](https://hexdocs.pm/ash_graphql/AshGraphql.html)

Field loading with actor/tenant; retrieved search result displayed 1.10.1; home-page fetch failed.

## S39 — Reactor

[Official reference](https://hexdocs.pm/reactor/readme.html)

Saga/workflow composition; displayed 1.0.6.

## S40 — AshStateMachine

[Official reference](https://hexdocs.pm/ash_state_machine/readme.html)

Action-oriented state-machine extension.

## S41 — Ash sensitive data

[Official reference](https://hexdocs.pm/ash/sensitive-data.html)

Sensitive metadata and exposure considerations.

## S42 — Phoenix.Component

[Official reference](https://hexdocs.pm/phoenix_live_view/Phoenix.Component.html)

HEEx components, attributes, slots, and forms.

## S43 — Ecto SQL Sandbox

[Official reference](https://hexdocs.pm/ecto_sql/Ecto.Adapters.SQL.Sandbox.html)

Connection ownership and collaborating processes.

## S44 — OpenAI skill authoring and discovery

[Official reference](https://learn.chatgpt.com/docs/build-skills)

SKILL.md, .agents/skills, optional openai.yaml, and explicit/implicit use.

## S45 — Agent Skills specification

[Official reference](https://agentskills.io/specification)

Metadata constraints and progressive disclosure.

## S46 — PostgreSQL constraints

[Official reference](https://www.postgresql.org/docs/current/ddl-constraints.html)

Storage constraints, uniqueness, and referential integrity; current page resolved to PostgreSQL 18.

## S47 — PostgreSQL EXPLAIN

[Official reference](https://www.postgresql.org/docs/current/using-explain.html)

Plan inspection; ANALYZE actually executes the query.

## S48 — Ash codegen task

[Official reference](https://hexdocs.pm/ash/Mix.Tasks.Ash.Codegen.html)

Code-generation task and option discovery.

## S49 — Ash multitenancy

[Official reference](https://hexdocs.pm/ash/multitenancy.html)

Attribute/context strategies and tenant propagation; displayed 3.31.3 on initial fetch.

## S50 — Ash.Query

[Official reference](https://hexdocs.pm/ash/Ash.Query.html)

Loads, input-aware filters/sorts, and documented query escape hatches.

## S51 — AshPhoenix nested forms

[Official reference](https://hexdocs.pm/ash_phoenix/nested-forms.html)

Automatic form configuration and loading existing relationships; search result displayed 2.3.24.

## S52 — Phoenix module documentation

[Official reference](https://hexdocs.pm/phoenix/Phoenix.html)

Phoenix documentation version snapshot: 1.8.13.
