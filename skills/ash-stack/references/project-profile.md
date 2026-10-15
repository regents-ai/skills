# Optional project profile template

Fill this from inspection, not guesses. Keep it in the project's existing agent notes
or an agreed `docs/agent-context.md`; do not duplicate an existing equivalent.

```text
Application root / umbrella layout:
Lockfile path and SHA-256:
Elixir / OTP pins:
Ash / AshPhoenix / AshPostgres / Phoenix / LiveView versions:
Data layer and test database setup:
Domain/resource conventions and one representative file:
Trusted scope type and actor/tenant resolution:
Authentication and LiveView on_mount modules:
Installed Ash extensions relevant to this project:
Named domain/form interface example and its actual signature:
Component, CSS, and JS-hook conventions:
Job/side-effect implementation:
Focused test, formatter, compile, codegen-check, and CI commands:
Release/migration owner and prohibited external operations:
Unknowns requiring investigation:
Last checked against commit or lock hash:
```

Do not include credentials, database URLs, session secrets, user tokens, or private
customer data. A profile is a cache; the repository and lockfile remain authoritative.
