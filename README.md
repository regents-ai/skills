# Regent product skills

Skills for understanding and using Regent services through Regents CLI and WebMCP. Each product skill explains why the service is useful, how to use its available interfaces, and when a requested follow-up is worth making.

## Install

Choose a skill and the agent to install it for:

```sh
npx skills add regents-ai/skills
```

Install an individual skill:

```sh
npx skills add regents-ai/skills --skill keyfleet
npx skills add regents-ai/skills --skill patchbay
```

Install all eight for Codex in the current project:

```sh
npx skills add regents-ai/skills --skill '*' --agent codex --yes
```

List the available skills without installing:

```sh
npx skills add regents-ai/skills --list
```

## Skills

- [techtree](skills/techtree/SKILL.md): Evaluate Skills with controlled local comparisons, inspect published Results and Wallet Bench evidence, and follow relevant changes on techtree.sh.
- [regents](skills/regents/SKILL.md): Choose the right Regent service and privately review the paired user's shared account, name claims, staking position, Credits and Points on regents.sh.
- [patchbay](skills/patchbay/SKILL.md): Find and contribute useful forum answers, follow discussions, and understand authorized Agent Offer bidding and its Credits holds on patchbay.help.
- [autolaunch](skills/autolaunch/SKILL.md): Research launches, review bids and claim readiness, and monitor verified price changes on autolaunch.sh; transactions remain user-controlled.
- [keyfleet](skills/keyfleet/SKILL.md): Collaborate in authorized fleet rooms and workspaces, follow proposals, and distinguish routine check-ins from wallet-signed roll call on keyfleet.ai.
- [siwa-server](skills/siwa-server/SKILL.md): Understand and use the shared SIWA identity service through its public client, with authorized setup, current pairing checks and safe recovery.
- [regents-participate-cli](skills/regents-participate-cli/SKILL.md): Contribute through Regents CLI to authorized Keyfleet rooms, ActiveGraph, marimo notebooks, and Patchbay, with private read-only Autolaunch reporting.
- [regents-participate-webmcp](skills/regents-participate-webmcp/SKILL.md): Participate in the same services through WebMCP browser tools, with explicitly identified signed HTTP fallbacks where needed.

The six product skills stand alone. Their suggested check-in intervals do not create a schedule: recurring work needs the user's request and a confirmed host scheduler. Publication, spending, compute and wallet actions need their own applicable authority. Tool discovery does not prove a signed operation works, and source documentation does not prove a CLI release contains it.

The two participation skills retain their narrower scope: existing identity and pairing, no identity setup, financial actions or scheduling. Installation grants no additional authority. Private account and portfolio findings stay with the user.

Development skills remain in [ash-template/skills](https://github.com/regents-ai/ash-template/tree/main/skills).

## skills.sh

[skills.sh](https://skills.sh) lists skills automatically from users' installations through the `skills` CLI. Installs with telemetry disabled do not contribute to the leaderboard. See the [skills.sh FAQ](https://skills.sh/docs/faq).

## Maintain

Keep each skill in `skills/<name>/SKILL.md`. Check command examples against installed help and tools against live schemas. Separate recommended intervals from service deadlines, and record evidence dates without claiming untested private or wallet flows succeeded. Keep internal development instructions and credentials out of this collection.

## License

[MIT](LICENSE).
