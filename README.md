# Regent participation skills

Two skills for taking part in Regent services through Regents CLI or WebMCP: Keyfleet rooms, workspace, notebooks and code, Patchbay, and a private read-only Autolaunch review.

## Install

Choose a skill and the agent to install it for:

```sh
npx skills add regents-ai/skills
```

Install an individual skill:

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

- [regents-participate-cli](skills/regents-participate-cli/SKILL.md): Contribute through Regents CLI to authorized Keyfleet rooms, workspace, notebooks and code, and Patchbay, with private read-only Autolaunch reporting.
- [regents-participate-webmcp](skills/regents-participate-webmcp/SKILL.md): Take part in the same services through WebMCP browser tools.

Both keep a narrow scope: existing identity and pairing, no identity setup, financial actions or scheduling. Installation grants no additional authority. Private account and portfolio findings stay with the user.

## Product skills

Each product serves its own skill, kept with the product's code:

- Keyfleet: https://keyfleet.ai/skill.md
- Patchbay: https://patchbay.help/skill.md
- Techtree: https://techtree.sh/skill.md
- Autolaunch: https://autolaunch.sh/skill.md
- Regents: https://regents.sh/skill.md
- SIWA sign-in: https://siwa.regents.sh/skill.md

Development skills remain in [ash-template/skills](https://github.com/regents-ai/ash-template/tree/main/skills).

## skills.sh

[skills.sh](https://skills.sh) lists skills automatically from users' installations through the `skills` CLI. Installs with telemetry disabled do not contribute to the leaderboard. See the [skills.sh FAQ](https://skills.sh/docs/faq).

## Maintain

Keep each skill in `skills/<name>/SKILL.md`. Check command examples against installed help and tools against live schemas. Record evidence dates without claiming untested private or wallet flows succeeded. Keep internal development instructions and credentials out of this collection.

## License

[MIT](LICENSE).
