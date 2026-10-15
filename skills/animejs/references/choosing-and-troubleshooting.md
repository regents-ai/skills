# Choosing the tool, cost, and when nothing moves

Sizes were measured with esbuild 0.25.4 (`--bundle --minify`, gzip -9) against animejs
4.5.0. LiveView behaviour comes from phoenix_live_view 1.2.11 (source and lab).

## Choose the tool

Take the first row that fits.

| The page needs | Use | Why |
| --- | --- | --- |
| A press, drawer, sheet, menu, list, count, tabs, headline or card cascade | The motion kit's markup (`data-press-label`, `data-panel`, `data-variant`, `data-cascade`), see [liveview-islands.md](liveview-islands.md#the-standard-motion-kit-template) | Every site moves the same way; no new code |
| Show, hide or swap classes from a click, with no state in the browser | `JS.show`, `JS.hide`, `JS.transition`, `phx-remove` with CSS classes | Runs with the patch, survives it, no hook |
| A look while an event is on its way to the server | LiveView's `phx-click-loading`, `phx-submit-loading` or `phx-change-loading` classes in CSS | Built in; the class goes when the reply lands. Style only: never `pointer-events: none` or `disabled` on an on-chain button |
| One element, a few properties, fire and forget | `waapi.animate()` (4.7 KiB) or CSS | Smallest; the browser runs it off the main thread. See [waapi-adapters.md](waapi-adapters.md) |
| Sequences, staggers, springs, interruptions, a server moment to celebrate | Anime.js `animate()` / `createTimeline()` in a hook | Precise control and clean teardown through a Scope |
| A list the server reorders, adds to or removes from | `createLayout()` | Measures before and after the patch; see [liveview-islands.md](liveview-islands.md#layout-on-server-driven-lists-lab) |
| Drag, scroll-linked motion, words or letters | `createDraggable()`, `onScroll()`, `splitText()` | Only these do it; check the cost below |

## Cost

What each set of imports adds to `app.js` (gzip). The kit already pays for `animate`, so a
site pays only the difference for the parts it adds. Regents, Keyfleet and the template cap
`app.js` at 175 KiB gzip (`assets/test/budgets.budget.ts`).

| Imports | Gzip |
| --- | --- |
| `animate` | 12.4 KiB |
| `animate`, `createScope`, `stagger` | 14.9 KiB |
| … + `createAnimatable` | 15.4 KiB |
| … + `createTimeline` | 15.9 KiB |
| … + `svg` | 16.0 KiB |
| … + `splitText` | 17.4 KiB |
| … + `onScroll` | 19.2 KiB |
| … + `createDraggable` | 22.2 KiB |
| … + `createLayout` | 23.4 KiB |
| `waapi` alone | 4.7 KiB |
| Everything (`import * as anime`) | 41.9 KiB |

Import names, never the namespace. A part used on one page only (like the `/animations`
lab) can be loaded lazily with `import()`, but keep anything that must hear the first
`phx:page-loading-stop` in the main bundle.

## When nothing moves

Work down the list; the first ones are the most common.

1. **The page gets no animation frames.** A hidden browser preview or a background tab
   draws nothing, and the engine pauses while the document is hidden. Check in a visible
   window or headless Playwright (see [Checks](liveview-islands.md#checks)).
2. **It was not meant to move.** Reduced motion is on (system setting or a
   `[data-motion='reduced']` ancestor), the press came from the keyboard, or the hook
   mounted on the first page load and skipped its entrance on purpose
   ([When a hook mounts](liveview-islands.md#when-a-hook-mounts-lab)).
3. **The hook never mounted.** The name is missing from the `hooks` passed to `LiveSocket`,
   or the element has no `id` (LiveView logs "no DOM ID for hook" and skips it).
4. **The selector matched nothing.** Inside a Scope, strings match only under its `root`;
   outside one they match the whole document, including other copies of the component.
5. **The option name is wrong.** Unknown keys, including v3 names such as `easing`,
   `direction` or `endDelay`, are animated as properties without an error, and an unknown
   ease string plays linear ([animation.md Gotchas](animation.md#gotchas)).
6. **A patch undid it.** A re-render of that element removed the inline style, a
   `data-layout-id` or the split spans in the same moment
   ([What a patch does](liveview-islands.md#what-a-liveview-patch-does-to-animejss-dom-writes)).
7. **The server moment went elsewhere.** The `push_event` name differs from the
   `handleEvent` name, or the payload's id does not match `this.el.id`. Every hook listening
   for a name receives it, so a missing filter moves the wrong copy.
8. **It moved from the wrong place.** A transform set by a class is invisible to
   `animate()`, which reads only the inline style; seed it with `utils.set` or use WAAPI.
   An element with `display: none` has no size to measure.
9. **It stutters or lags.** A CSS `transition` on the same property smooths every frame the
   script writes; remove the transition from that element. Something changed
   `engine.defaults` for the whole page ([animation.md Gotchas](animation.md#gotchas)).
10. **It ends stuck half-way.** A move started over another one restored the half-way
    frame. Start moves with the kit's `play()` ([the kit](liveview-islands.md#the-standard-motion-kit-template)).
