# Regent skills

Public agent skills for building with Ash, Phoenix and Elixir, and participating in Regent services through Regents CLI or WebMCP.

## Install

Choose skills and the agent to install them for:

```sh
npx skills add regents-ai/skills
```

List available skills without installing:

```sh
npx skills add regents-ai/skills --list
```

Install the complete collection for Codex in the current project:

```sh
npx skills add regents-ai/skills --skill '*' --agent codex --yes
```

Install either participation skill:

```sh
npx skills add regents-ai/skills --skill regents-participate-cli
npx skills add regents-ai/skills --skill regents-participate-webmcp
```

The build skills link to one another. Install the collection to keep those references available. Installing a skill grants no permission to sign requests, publish, spend, or change credentials; each task still needs the relevant authority.

## Skills

| Skill | Purpose |
| --- | --- |
| [ash-stack](skills/ash-stack/SKILL.md) | Choose an Ash workflow for cross-layer features or refactors. |
| [ash-backend](skills/ash-backend/SKILL.md) | Design or simplify Ash resources, actions and domain interfaces. |
| [ash-data](skills/ash-data/SKILL.md) | Change AshPostgres schemas or diagnose SQL and concurrency behavior. |
| [ash-frontend](skills/ash-frontend/SKILL.md) | Build or refine AshPhoenix forms and LiveView interfaces. |
| [ash-security](skills/ash-security/SKILL.md) | Change or review Ash authorization, trusted scopes and field exposure. |
| [ash-testing](skills/ash-testing/SKILL.md) | Design Ash regression tests or remove redundant test coupling. |
| [ash-webmcp](skills/ash-webmcp/SKILL.md) | Use when making Ash sites agent-ready, or building WebMCP browser tools into an Ash/Phoenix site. |
| [elixir-stack](skills/elixir-stack/SKILL.md) | Elixir, Phoenix, Ecto, Oban and OTP judgment for Regent's sites. It covers which standard tool does each job, what never to hand-build, the design check that comes before building or reviewing, and how Regent runs Oban. Load it with regent-workflow and ash-stack before any Elixir work, and whenever the work involves background or retried work, schedules, webhooks or calls to other services, polling, queues, leases, GenServers, PubSub, caches, HTTP clients or a shared Elixir library. |
| [animejs](skills/animejs/SKILL.md) | Motion on Regent's Phoenix LiveView and Ash sites with Anime.js v4 (npm animejs) and the shared motion kit, written as TypeScript hook islands. Use for any animation, transition or motion work on a Regent site (entrances, presses, drawers, lists, counts, celebrations after an action) and whenever code uses animejs — animate, timelines, timers, stagger, easings and springs, splitText, SVG morph/draw/motion path, draggable, animatable, onScroll, auto layout, Scope, engine, utils, WAAPI or the three.js adapter — or a LiveView hook animates server-rendered DOM. Also for choosing between CSS, LiveView JS commands and Anime.js, and for motion that does not play. |
| [onchain-buttons](skills/onchain-buttons/SKILL.md) | Buttons that make a person's wallet act on Regent's Phoenix LiveView and Ash sites — send a transaction (approve, stake, bid, buy, claim, settle, launch) or sign (x402 payment, typed data). Use when adding, changing, reviewing or debugging any wallet or on-chain button, its TypeScript hook, the chain switch, the wallet's answer, the server's check of the result, or the words shown for each outcome. |
| [chain-events](skills/chain-events/SKILL.md) | Watching a chain for contract events on Regent's Phoenix and Ash sites, saving each one to the database once, and showing the saved rows on LiveView pages as they arrive. Use when adding or changing an event watcher, its cursor, the tables it fills, how a reorg or disagreement is handled, how pages hear about new rows, the "catching up" notice, or chain reads the server makes at the latest block. |
| [payments](skills/payments/SKILL.md) | Taking USDC payments on Regent's Phoenix and Ash sites with the shared RegentPayments library — tips, paid actions and fees paid from a person's own wallet on Base through x402, their USDC Balance, and paid tools for agents. Use when adding or changing anything a person or agent pays for, an offer, a pay button, the USDC Balance shown on a page, a paid HTTP endpoint or MCP tool, a paid-fix fee forwarded to REGENT staking, or the words shown for a payment's outcome. |
| [discussions](skills/discussions/SKILL.md) | Forum threads on Regent's Phoenix and Ash sites — a question or post and its replies, likes, view counts, a marked answer and reply filters — rendered with the shared Regent.Discussion component and stored in the site's own Ash resources. Use when adding or changing a discussion, question-and-answer or forum page, a like button on posts, a view count, a "Solved" answer, or agent tools that read or like posts. |
| [regents-participate-cli](skills/regents-participate-cli/SKILL.md) | Participate in authorized Keyfleet rooms, ActiveGraph, marimo notebooks, and Patchbay through Regents CLI, with signed-HTTP gaps and private read-only Autolaunch reporting. For existing agents; excludes identity setup, financial actions, and scheduling. |
| [regents-participate-webmcp](skills/regents-participate-webmcp/SKILL.md) | Participate in authorized Keyfleet rooms, ActiveGraph, marimo notebooks, and Patchbay through WebMCP, with signed-HTTP gaps and private read-only Autolaunch reporting. For existing agents; excludes identity setup, financial actions, and scheduling. |

## skills.sh

[skills.sh](https://skills.sh) lists skills automatically from users' installations through the `skills` CLI. The repository must be public for anonymous users to install it. Installs with telemetry disabled do not contribute to the leaderboard. Publishing the repository alone does not establish a listing or installation count. See the [skills.sh FAQ](https://skills.sh/docs/faq).

## Maintain

Keep each skill in `skills/<name>/SKILL.md` with its supporting files in the same folder. Preserve the name and description metadata, relative references, and authorization boundaries. Keep private workspace instructions and credentials out of the collection.

## License

[MIT](LICENSE). This collection originates from the public skills in [regents-ai/ash-template](https://github.com/regents-ai/ash-template).
