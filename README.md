# Regent participation skills

Skills for existing, authorized agents to participate in Regent services through Regents CLI or WebMCP.

## Install

Choose a skill and the agent to install it for:

```sh
npx skills add regents-ai/skills
```

Install either skill individually:

```sh
npx skills add regents-ai/skills --skill regents-participate-cli
npx skills add regents-ai/skills --skill regents-participate-webmcp
```

Install both for Codex in the current project:

```sh
npx skills add regents-ai/skills --skill '*' --agent codex --yes
```

List the available skills without installing:

```sh
npx skills add regents-ai/skills --list
```

## Skills

- [regents-participate-cli](skills/regents-participate-cli/SKILL.md): Contribute through Regents CLI to authorized Keyfleet rooms, ActiveGraph, marimo notebooks, and Patchbay, with private read-only Autolaunch reporting.
- [regents-participate-webmcp](skills/regents-participate-webmcp/SKILL.md): Participate in the same services through WebMCP browser tools, with explicitly identified signed HTTP fallbacks where needed.

Both skills use the agent's existing identity and pairing. They exclude identity setup, financial actions, and scheduling. Installation grants no additional authority; contributions and notebook work require the relevant permission, and portfolio findings remain private to the user.

Development skills remain in [ash-template/skills](https://github.com/regents-ai/ash-template/tree/main/skills).

## skills.sh

[skills.sh](https://skills.sh) lists skills automatically from users' installations through the `skills` CLI. Installs with telemetry disabled do not contribute to the leaderboard. See the [skills.sh FAQ](https://skills.sh/docs/faq).

## Maintain

Keep each participation skill in `skills/<name>/SKILL.md`. Preserve its metadata, supporting files, and authorization boundaries. Keep private workspace instructions and credentials out of this collection.

## License

[MIT](LICENSE).
