# Anime.js v4 reference: Scope, Engine, Utilities

For Anime.js 4.5.0 (npm `animejs`). This file covers three parts of the library. `createScope` groups every Anime.js object made inside it, so one `revert()` stops them all and puts the DOM back. That is the main tool for tying animations to a component's lifetime, such as a Phoenix LiveView hook's `mounted()` and `destroyed()`. `engine` is the single global loop that drives every Timer, Animation and Timeline, and it holds the global defaults. `utils` holds `stagger`, DOM helpers (`$`, `get`, `set`, `remove`, `cleanInlineStyles`), timing helpers (`sync`, `keepTime`), random helpers, and number helpers that can be chained and used as tween `modifier`s. Names, signatures and defaults below were checked against `dist/modules/**/*.d.ts` and the 4.5.0 source. To read a live page, run `uv run scripts/animejs_docs.py <path>`.

Imports: `import { createScope, engine, utils, stagger, $, get, set } from 'animejs'`. Every utility is exported both on `utils` and by name. Subpaths also work: `'animejs/scope'`, `'animejs/engine'`, `'animejs/utils'`.

---

## Scope `scope`

`createScope(params?: ScopeParams): Scope` (also `new Scope(params)`). Since 4.0.0.

While a Scope runs a constructor or a registered method, it temporarily sets three globals: the active scope, the DOM root used for string selectors, and the default parameters. It puts them back when the call returns. Any Timer, Animation, Timeline, Animatable, Draggable, ScrollObserver, WAAPI animation, TextSplitter, AutoLayout or nested Scope created **synchronously** during that call is registered with the scope.

### Constructor function `scope/add-constructor-function`

| Item | Type | Meaning |
|---|---|---|
| argument | `self: Scope` (typed `scope?: Scope`) | The scope itself. Read `self.matches` here. |
| return (optional) | `ScopeCleanupCallback = (scope?: Scope) => any` | Runs on `revert()` and before every rebuild (`refresh()` or a media query change). Use it to remove listeners and classes the constructor added. |

TS note: `ScopeConstructorCallback` is typed `(scope?: Scope) => ScopeCleanupCallback | void`. Under `strict`, write `self?.matches` or `self!.matches`.

### Register method function `scope/register-method-function`

`scope.add(name: string, fn: (...args: any[]) => any)` stores a wrapper at `scope.methods[name]`. Every call to the wrapper runs `fn` inside the scope, so animations it creates later (from event handlers, `pushEvent` replies, `handleEvent`) use the scope's root and defaults and are reverted with the scope. Arguments pass through, and the wrapper returns what `fn` returns.

### Parameters `scope/scope-parameters`

| Name | Type | Default | Meaning |
|---|---|---|---|
| `root` | `DOMTargetSelector \| ReactRef \| AngularRef` (selector string, element, NodeList, `{current}`, `{nativeElement}`) | `document` | String selectors and `utils.$` inside the scope query only this element's descendants. The first match is used. If nothing matches, the scope **silently falls back to `document`**. `scope/scope-parameters/root` |
| `defaults` | `DefaultsParams` | engine defaults | Default parameters for Timers, Animations and Timelines made in the scope. They are merged over `engine.defaults` **once, when the scope is created**. See the defaults table under Engine. The docs page omits `onPause`, but the type accepts it. `scope/scope-parameters/defaults` |
| `mediaQueries` | `Record<string, string>` (name to media query) | none | Each entry becomes a `MediaQueryList` with a `change` listener. On any change the scope calls `refresh()`. The current booleans are in `scope.matches[name]`. `scope/scope-parameters/mediaqueries` |

### Methods `scope/scope-methods`

| Method | Signature (types) | Since | Meaning |
|---|---|---|---|
| `add` | `add(constructor): this` / `add(name, method): this` | 4.0.0 | Constructor form: saves the constructor and runs it right away inside the scope, and runs it again on every refresh. Method form: registers `methods[name]`. `scope/scope-methods/add` |
| `addOnce` | `addOnce(constructor): this` | 4.1.0 | Runs the constructor once. The objects it creates go to a separate "once" list, so they survive refreshes and are reverted only by `revert()`. It is tracked by call order, so **never call it conditionally**. `scope/scope-methods/addonce` |
| `keepTime` | `keepTime(cb: (scope: this) => Tickable): Tickable` | 4.1.0 | Call it inside an `add` constructor. On each refresh it rebuilds the Timer, Animation or Timeline that `cb` returns, and carries over the current iteration, progress, direction and start time, so playback continues without a jump. Tracked by call order, so **never call it conditionally**. Returns the live tickable. `scope/scope-methods/keeptime` |
| `revert` | `revert(): void` | 4.0.0 | Reverts every registered object, newest first, then the once objects. Runs all cleanup callbacks and removes the media query listeners. Then it empties `constructors`, `methods`, `matches`, `mediaQueryLists` and `data`. `scope/scope-methods/revert` |
| `refresh` | `refresh(): this` | 4.0.0 | Reverts the regular (not once) objects and runs their cleanups, then runs every `add` constructor again with fresh `matches`. The scope calls it itself when a media query changes. `data` and once objects are kept. `scope/scope-methods/refresh` |

Methods in the types but not in the docs: `register(revertible)` adds an object to the scope by hand. `execute<T>(cb: (scope) => T): T` runs any callback inside the scope without saving it, which is useful for one-off animations from a hook callback. `handleEvent(e)` is the `MediaQueryList` listener.

Docs vs types: the docs say `revert()` returns the Scope. The `.d.ts` and the source return `void`, so do not chain after `revert()`.

### Properties `scope/scope-properties`

| Name | Type | Meaning |
|---|---|---|
| `data` | `Record<string, any>` | Your own storage for the scope. Emptied by `revert()`, kept by `refresh()`. |
| `defaults` | `DefaultsParams` | The merged defaults in use. |
| `root` | `Document \| HTMLElement \| SVGElement` | The resolved root. |
| `constructors` | `ScopeConstructorCallback[]` | Constructors saved by `add`. |
| `revertConstructors` | `ScopeCleanupCallback[]` | Cleanup callbacks returned by constructors. |
| `revertibles` | `Revertible[]` | Registered objects (Animatable, Timer, Animation, Timeline, WAAPIAnimation, Draggable, ScrollObserver, TextSplitter, Scope, AutoLayout). |
| `methods` | `Record<string, ScopeMethod>` | Registered methods. |
| `matches` | `Record<string, boolean>` | Media query results. Updated at the start of every constructor or method run. |
| `mediaQueryLists` | `Record<string, MediaQueryList>` | The underlying lists. |

Only in the types: `constructorsOnce`, `revertConstructorsOnce`, `revertiblesOnce`, `once: boolean`, `onceIndex: number` (bookkeeping for `addOnce` and `keepTime`).

```ts
export function mountScope(el: HTMLElement): Scope {
  const scope = createScope({
    root: el,
    defaults: { ease: 'out(3)', duration: 400 },
    mediaQueries: { reduced: '(prefers-reduced-motion: reduce)' },
  }).add((self) => {
    const reduced = self?.matches.reduced ?? false;
    animate('.item', { opacity: [0, 1], duration: reduced ? 0 : 400 });
    const onKey = (e: KeyboardEvent) => { if (e.key === 'Escape') el.blur(); };
    el.addEventListener('keydown', onKey);
    return () => el.removeEventListener('keydown', onKey);
  });
  scope.add('pulse', (target: HTMLElement) => {
    animate(target, { scale: [1, 1.1, 1] });
  });
  return scope; // later: scope.methods.pulse(node); on teardown: scope.revert()
}

export function keepTimeInScope(el: HTMLElement): Scope {
  return createScope({ root: el, mediaQueries: { wide: '(min-width: 800px)' } })
    .add((self) => {
      self?.keepTime((s) =>
        animate('.bar', { x: s.matches.wide ? 300 : 120, loop: true, alternate: true }),
      );
    });
}
```

---

## Engine `engine`

`import { engine } from 'animejs'`. A single `Engine` instance, a subclass of `Clock`. It advances all tickables with `requestAnimationFrame` (with `setImmediate` outside a browser). The loop runs only while something is playing.

Execution order: tickables run in the order they were added, unless you set the Timer/Animation/Timeline parameter `priority: number` (default `1`). Lower values run first.

### Parameters `engine/engine-parameters`

| Name | Type | Default | Meaning |
|---|---|---|---|
| `timeUnit` | `'ms' \| 's'` | `'ms'` | Unit for `duration`, `delay` and similar values everywhere. Switching also rescales `engine.defaults.duration` (1000 becomes 1). `engine/engine-parameters/timeunit-seconds-milliseconds` |
| `speed` | `number` (≥ 0, clamped to at least 1e-11) | `1` | Global playback rate multiplier for every tickable. `engine/engine-parameters/speed` |
| `fps` | `number` (> 0) | `240` | Global maximum tick rate. Setting it above `defaults.frameRate` also raises that default. `engine/engine-parameters/fps` |
| `precision` | `number` | `4` | Decimal places for string values (CSS, SVG and DOM attributes) while a tween is running. The first and last frames use full precision. A negative value turns rounding off. It also rounds the values returned by `currentTime` and `iterationCurrentTime` getters and by `utils.get(..., unit)` conversions. `engine/engine-parameters/precision` |
| `pauseOnDocumentHidden` | `boolean` | `true` | When `true`, a `visibilitychange` listener pauses the engine while the tab is hidden and resumes it after. When `false`, tickables catch up on the time they missed when the tab returns. `engine/engine-parameters/pauseondocumenthidden` |
| `useDefaultMainLoop` | `boolean` | `true` | When `false`, the engine never schedules frames, and you must call `engine.update()` from your own loop. (Documented under Properties and `update()`.) |

### Methods `engine/engine-methods`

| Method | Types return | Meaning |
|---|---|---|
| `update()` | `void` | Advances everything by one tick. Use it with `useDefaultMainLoop = false`, for example inside a Three.js `setAnimationLoop`. Docs say it returns the Engine. The types and the source return nothing. `engine/engine-methods/update` |
| `pause()` | `Engine` | Cancels the frame loop and sets `engine.paused = true`. Returns `undefined` at runtime when the loop was already idle. `engine/engine-methods/pause` |
| `resume()` | `this` | Only if `engine.paused` is true: resets each child's time (so nothing jumps forward) and restarts the loop. Returns `undefined` when not paused. `engine/engine-methods/resume` |
| `wake()` (types only) | `this` | Starts the loop if it is idle. Tickables call it themselves. |

### Properties `engine/engine-properties`

| Name | Type | Meaning |
|---|---|---|
| `timeUnit`, `speed`, `fps`, `precision`, `useDefaultMainLoop`, `pauseOnDocumentHidden` | see above | get and set |
| `deltaTime` | `number` | Milliseconds between the last two ticks. |
| `currentTime` | `number` (docs) | **Not in the types, and `undefined` at runtime in 4.5.0.** Only the private `_currentTime` exists. Use `performance.now()` or a Timer's `currentTime` instead. |
| `defaults` (types) | `DefaultsParams` | The global defaults object (see the next table). |
| `paused` (types) | `boolean` | Set by `pause()`, cleared by `resume()`. |
| `reqId` (types) | `number \| NodeJS.Immediate` | Current frame request id. `0` when idle. |

### Defaults `engine/engine-defaults`

Change them by assigning to `engine.defaults.<name>`. (The docs' snippet writes `engine.engine.defaults`. That is a typo.) The values shown are the 4.5.0 runtime defaults.

| Name | Type | Default | Meaning |
|---|---|---|---|
| `playbackEase` | `EasingParam` | `null` | Easing applied to the whole playback, on top of each tween's ease. |
| `playbackRate` | `number` | `1` | Speed of each tickable. |
| `frameRate` | `number` | `240` | Maximum fps of each tickable. |
| `loop` | `number \| boolean` | `0` | Number of repeats. `true` repeats forever. |
| `reversed` | `boolean` | `false` | Plays backwards. |
| `alternate` | `boolean` | `false` | Reverses direction on each loop. |
| `autoplay` | `boolean \| ScrollObserver` | `true` | Starts playing on creation. |
| `duration` | `number \| FunctionValue` | `1000` | Tween or timer length, in `timeUnit`. |
| `delay` | `number \| FunctionValue` | `0` | Delay before start. |
| `loopDelay` | `number` | `0` | Pause between loops. |
| `ease` | `EasingParam \| FunctionValue` | `'out(2)'` | Tween easing. |
| `composition` | `'none' \| 'replace' \| 'blend'` | `'replace'` | How new tweens combine with running tweens on the same property. |
| `modifier` | `(v: any) => any` | identity | Changes every computed value before it is rendered. |
| `onBegin` `onUpdate` `onRender` `onLoop` `onComplete` `onPause` | `Callback<Tickable>` (`onRender`: `Callback<Renderable>`) | no-op | Lifecycle callbacks. |
| `onBeforeUpdate`, `id`, `keyframes`, `persist` | types only | no-op / `null` / `null` / `false` | In `DefaultsParams` but not on the docs page. |

```ts
export function externalLoop(): () => void {
  engine.useDefaultMainLoop = false;
  let id = 0;
  const frame = () => {
    engine.update();
    id = requestAnimationFrame(frame);
  };
  id = requestAnimationFrame(frame);
  return () => {
    cancelAnimationFrame(id);
    engine.useDefaultMainLoop = true;
  };
}
```

---

## Utilities `utilities`

### stagger() `utilities/stagger`

`stagger(value, params?: StaggerParams): StaggerFunction<number | string>`. Since 2.0.0. The result is a function-based value, `(target?, index?, targets?, prevTween?, timeline?) => T`, that you can use in three places:
- time parameters such as `delay` and `duration` (`utilities/stagger/time-staggering`)
- any animatable property value, including inside `{ from, to }` (`utilities/stagger/values-staggering`)
- the position argument of `timeline.add()`, which gives each target its own staggered child animation, and calls that child's callbacks once per target (since 4.0.0, `utilities/stagger/timeline-positions-staggering`).

Value types (`utilities/stagger/stagger-value-types`):

| Form | Types overload | Meaning |
|---|---|---|
| numerical | `number` or `string` holding a number (`'1rem'`) | Each target adds this step. The unit is kept. `.../numerical-value` |
| range | `[number, number]` or `[string, string]` | Spreads values evenly from the first to the second across the targets. The unit comes from the second item. `.../range-value` |

Parameters (`utilities/stagger/stagger-parameters/*`):

| Name | Type | Default | Since | Meaning |
|---|---|---|---|---|
| `start` | `number \| string` (a timeline position string only works in a timeline position) | `0`, or the timeline's current end in a timeline position | 2.0.0 | Number added to every output. With a range value, `start` **replaces** the range's first number, and the range only sets the step. `stagger-start` |
| `from` | `number \| 'first' \| 'center' \| 'last' \| 'random' \| number[]` | `0` | 2.0.0 | Index where the stagger starts. `[x, y]` or `[x, y, z]` gives a 0-1 origin inside the grid and needs `grid`. `'random'` shuffles the order. `stagger-from` |
| `reversed` | `boolean` | `false` | 2.0.0 | Reverses the distribution. `stagger-reversed` |
| `ease` | `EasingParam` (a spring works too) | `'linear'` | 2.0.0 | Eases how values are spread across targets. `stagger-ease` |
| `grid` | `[cols, rows] \| [cols, rows, depth] \| true` | `null` | 2.0.0; `true` 4.4.0; 3D 4.5.0 | Measures distance in a grid instead of along a line. `true` builds the grid from each target's `getBoundingClientRect()` centre or its numeric `{x, y, z}`. Any numeric `z` switches to 3D. `stagger-grid` |
| `axis` | `'x' \| 'y' \| 'z'` | none | 2.0.0 (`'z'` 4.5.0) | Uses the signed distance along one grid axis only. `'z'` needs a 3D grid. `stagger-grid-axis` |
| `modifier` | `(value: number) => number \| string` | none | 2.0.0 | Runs on each final number, before the unit is added back. `stagger-modifier` |
| `use` | `string` (attribute or property name). The types also accept `(target, i, total) => number` | `null` | 4.1.0 | Takes the order from that attribute or property. The values must be integers starting at `0`. An out-of-range value falls back to the natural index. `stagger-use` |
| `total` | `number` | `null` (target count) | 4.1.0 | Overrides the count. Set it when the highest `use` index is below the target count and you also use `from`, `reversed` or `ease`. `stagger-total` |
| `jitter` | `number \| [number, number]` | `null` | 4.5.0 | Adds random noise. A number gives ±value. A pair grows from the first value (closest target) to the second (farthest), following `ease`. `stagger-jitter` |
| `seed` | `boolean \| number` | `false` | 4.5.0 | Makes `jitter` and `from: 'random'` repeatable. `true` uses seed 0. A number is used as the seed. |

```ts
declare const cells: HTMLElement[];
export function staggers(): void {
  animate(cells, {
    scale: [0, 1],
    delay: stagger(40, { grid: [8, 4], from: 'center', ease: 'inOutQuad' }),
  });
  animate(cells, { y: stagger(['-1rem', '1rem'], { from: [0.5, 0], grid: [8, 4], axis: 'y' }) });
  animate(cells, { delay: stagger(60, { use: 'data-order', total: 4, reversed: true }) });
  animate(cells, { delay: stagger(50, { jitter: [0, 30], seed: 7 }) });
  createTimeline()
    .add('.a', { x: 100 })
    .label('afterA')
    .add(cells, { x: 100 }, stagger(80, { start: 'afterA-=200' }));
}
```

### DOM and target helpers

| Function | Signature (types) | Since | Meaning |
|---|---|---|---|
| `$` `utilities/dollar-sign` | `$(targets: DOMTargetsParam): DOMTargetsArray`, plus overloads for JS objects and mixed targets | 4.0.0 | Returns a flat, de-duplicated array of targets. A string selector queries the active scope's `root` (or `document` outside a scope). It also marks each target with internal symbols. |
| `get` `utilities/get` | `get(el, prop): string` · `get(jsObj, prop): number \| string` · `get(el, prop, unit: string): string` · `get(targets, prop, unit: boolean /* false */): number` | 2.0.0 | Reads the current value from the **first** target. A unit string converts the value (rounded to `engine.precision`). `false` strips the unit and returns a number. Returns `undefined` when nothing matches, or when `unit` is given for a value that is not a plain number, such as a color. The types do not include `undefined`. |
| `set` `utilities/set` | `set(targets: TargetsParam, params: AnimationParams): JSAnimation` | 2.0.0 | Applies values right away through a JSAnimation of near-zero duration, with `composition: 'none'` unless you give one. Function values and staggers work. Call `.revert()` on the result to restore what was there before. It will not create a DOM attribute the element does not already have. For repeated writes, use an Animatable. |
| `cleanInlineStyles` `utilities/clean-inline-styles` | `cleanInlineStyles<T extends JSAnimation \| Timeline>(r: T): T` | 4.0.0 | Removes the inline CSS and transform values this animation or timeline wrote, and restores any inline values that existed before. It leaves attributes and JS object properties alone, and removes a `style` attribute left empty. It also **pauses** the animation. It is meant to be passed as `onComplete`. |
| `remove` `utilities/remove` | `remove(targets, renderable?: JSAnimation \| Timeline \| WAAPIAnimation, propertyName?: string): TargetsArray` | 2.0.0 | Stops the targets' tweens: all of them, only the ones in `renderable`, or only one property. An animation left with no tweens is cancelled. Current inline values stay as they are. The types also accept a WAAPI animation. The docs list only Animation and Timeline. |

```ts
declare const box: HTMLElement;
export function getSet(): void {
  const raw: string = utils.get(box, 'width');
  const inRem: string = utils.get(box, 'width', 'rem');
  const px: number = utils.get(box, 'width', false);
  const state = { progress: 0 };
  const p: number | string = utils.get(state, 'progress');
  const setter = utils.set(box, { opacity: 0.5, x: 10 });
  setter.revert();
  void [raw, inRem, px, p];
}
```

### Timing helpers

| Function | Signature (types) | Since | Meaning |
|---|---|---|---|
| `sync` `utilities/sync` | `sync(callback?: (timer: Timer) => any): Timer` | 4.0.0 | Runs `callback` on an engine tick, as the `onComplete` of a Timer lasting 1 time unit. Use it when writing to `engine.speed` or to an animation's `speed` from input events. |
| `keepTime` `utilities/createtimekeeper` | `keepTime<T extends Tickable \| ((...a) => void) \| void>(ctor: (...args) => T): (...args) => T` | 4.1.0 | Wraps a function that returns a tickable. Each call to the wrapper reverts the previous tickable and builds a new one at the same iteration, progress, direction and start time. Arguments pass through to `ctor`. If `ctor` returns a plain function instead of a tickable, nothing is tracked. |

```ts
export function trackedRebuild(): () => void {
  let distance = 100;
  const build = utils.keepTime(() => animate(box, { x: distance, loop: true, alternate: true }));
  build();
  return () => {
    distance = 200;
    build();
  };
}
```

### Random helpers

| Function | Signature (types) | Since | Meaning |
|---|---|---|---|
| `random` `utilities/random` | `random(min = 0, max = 1, decimalLength = 0): number` | 2.0.0 | Returns a number from min to max, **both included**. With `decimalLength = 0` it is an integer, so `random()` returns only 0 or 1. The docs mark min and max as required. The types give them defaults. |
| `createSeededRandom` `utilities/createseededrandom` | `createSeededRandom(seed?, seededMin = 0, seededMax = 1, seededDecimalLength = 0): RandomNumberGenerator` | 2.0.0 (per docs) | Returns a repeatable generator with the same call shape as `random`. The generator's own arguments default to the `seeded*` values. With no seed it uses an internal counter (0, 1, 2, … in call order), not a fixed 0 as the docs say. |
| `randomPick` `utilities/random-pick` | `randomPick<T>(items: string \| T[]): string \| T` | 4.0.0 | Returns one random item or character. The return type is a union, so cast or narrow it. The docs also accept a `NodeList`, which works at runtime, but the types reject it. |
| `shuffle` `utilities/shuffle` | `shuffle(items: any[], rnd?: RandomNumberGenerator): any[]` | 4.0.0 | Shuffles the array **in place** (Fisher-Yates) and returns the same array. Pass `rnd` for a repeatable order. |

```ts
export function randoms(): void {
  const rng = utils.createSeededRandom(42);
  const order = utils.shuffle([1, 2, 3, 4], rng);
  const colors = ['red', 'blue'];
  const pick = utils.randomPick(colors) as string;
  const r: number = utils.random(0, 10, 2);
  void [order, pick, r];
}
```

### Number helpers (all chainable) `utilities/chain-able-utility-functions`

Each helper has a full form and a partial form. Pass the value as well and you get the result. Leave the value out and you get a chainable function `(v: number) => number`. That function also has every chainable helper as a method, and each method feeds the previous output into the next step. The library decides by **counting arguments**: fewer than the full signature always returns a function.

| Function | Full form | Partial form | Returns | Meaning |
|---|---|---|---|---|
| `round` `utilities/round` | `round(v, decimalLength)` | `round(decimalLength)` | `number` | Rounds. A negative `decimalLength` returns `v` unchanged. |
| `clamp` `utilities/clamp` | `clamp(v, min, max)` | `clamp(min, max)` | `number` | Limits `v` to the range. |
| `snap` `utilities/snap` | `snap(v, increment: number \| number[])` | `snap(increment)` | `number` | Moves to the nearest multiple, or to the nearest value in the array. |
| `wrap` `utilities/wrap` | `wrap(v, min, max)` | `wrap(min, max)` | `number` | Wraps around like a modulo into [min, max). |
| `mapRange` `utilities/map-range` | `mapRange(v, inLow, inHigh, outLow, outHigh)` | `mapRange(inLow, inHigh, outLow, outHigh)` | `number` | Maps linearly without clamping. |
| `lerp` `utilities/lerp` | `lerp(start, end, progress)` | `lerp(start, end)`, which takes progress | `number` | Interpolates linearly. The docs' chain list calls it `interpolate()`, but no such export exists. |
| `damp` `utilities/damp` | `damp(start, end, deltaTime, factor)` | `damp(start, end, deltaTime)`, which takes factor (types only) | `number` | A lerp that does not depend on frame rate: `lerp(start, end, 1 - exp(-factor * deltaTime * 0.1))`. `factor` 0 returns start and 1 returns end. |
| `roundPad` `utilities/round-pad` | `roundPad(v: number \| string, decimalLength)` | `roundPad(decimalLength)` | `string` | Returns a fixed-decimal string (`toFixed`). |
| `padStart` `utilities/pad-start` | `padStart(v, totalLength, padString)` | `padStart(totalLength, padString)` | `string` | `String(v).padStart(...)`. The docs allow a string `v`. The types say `number`. |
| `padEnd` `utilities/pad-end` | `padEnd(v, totalLength, padString)` | `padEnd(totalLength, padString)` | `string` | `String(v).padEnd(...)`. |
| `degToRad` `utilities/deg-to-rad` | `degToRad(degrees)` | `degToRad()` | `number` | Degrees to radians. |
| `radToDeg` `utilities/rad-to-deg` | `radToDeg(radians)` | `radToDeg()` | `number` | Radians to degrees. |

Chains are plain functions, so you can pass one straight to a tween's `modifier`.

```ts
export function chains(): void {
  const label: string = utils.round(3.14159, 2).toString();
  const fmt = utils.clamp(0, 100).round(1);
  const n: number = fmt(123.456);
  animate(box, { innerHTML: 100, modifier: utils.round(0).padStart(3, '0') });
  const smooth = utils.damp(0, 100, 16);
  void [label, n, smooth(0.2)];
}
```

Exported but undocumented and internal: `utils.forEachChildren`, `utils.addChild`, `utils.removeChild` (helpers for the engine's internal linked lists). Do not use them.

---

## Docs vs types and source disagreements

- `scope.revert()` returns `void`, not the Scope.
- `engine.update()` returns `void`, not the Engine. `engine.pause()` and `resume()` can return `undefined` (see the table).
- `engine.currentTime` is documented but missing from the types and `undefined` at runtime.
- `engine.engine.defaults` in the docs is a typo for `engine.defaults`.
- The damp page's snippet calls `utils.lerp(start, end, deltaTime, amount)`, which should be `damp`. Its example says `damp(0, 100, 8, 0.5)` is `50`. The real result is about `32.97`.
- The chain list names `interpolate()`. The real export is `lerp`, and `damp` can also be chained, though the list omits it.
- `randomPick`: the docs accept a `NodeList`. The types accept only `string | T[]`.
- `remove`: the types also accept a `WAAPIAnimation`.
- `stagger` `use`: the types also accept a function `(target, i, total) => number`.
- Scope `root`: the types also accept React `{current}` and Angular `{nativeElement}` refs.
- `createSeededRandom()` without a seed uses an auto-incrementing seed, not a fixed `0`.
- `get` can return `undefined`, which its overloads do not show.
- The docs' `mapRange(...).round(1)` example shows string results (`'0.5'`). `round` returns numbers.
- The library's own `.d.ts` files mention `NodeJS.Immediate` and `NodeJS.Timeout` (in `engine.d.ts` and `text/split.d.ts`). With `skipLibCheck: false` and no `@types/node`, tsc reports TS2503. Either add `@types/node` or keep `skipLibCheck: true`.

## Gotchas

- Scope context only lasts while the call runs. Code that runs later (`setTimeout`, promise callbacks, `addEventListener` handlers defined in a constructor, LiveView `handleEvent`) runs **outside** the scope. There, string selectors query all of `document` and new objects are not registered. Route that code through `scope.add('name', fn)` and call `scope.methods.name(...)`, or wrap it in `scope.execute(() => ...)`.
- A `root` selector that matches nothing silently falls back to `document`. In a hook, pass `this.el`, not a selector.
- Scope `defaults` copy `engine.defaults` when the scope is created. Later changes to `engine.defaults` do not reach existing scopes.
- `addOnce` and `keepTime` are matched to their slot by call order. Calling them conditionally, or a different number of times on each refresh, attaches the wrong saved constructor.
- A media query change runs `refresh()`, which **reverts** everything made by `add` constructors. Inline styles go back to their earlier values and animations restart from zero, unless they were built with `keepTime`. State kept in constructor closures is lost. Keep state in `scope.data`, which survives refreshes.
- `revert()` empties `constructors` and removes the media query listeners. A reverted scope does not come back on `refresh()`. Create a new one.
- A `stagger()` function measures on its first call and then keeps the result: target count, distances, grid measurements (`grid: true` reads `getBoundingClientRect` only once), the `from: 'random'` order, the jitter samples and the timeline offset. Make a new `stagger()` for each animation or target set. Do not share one across animations or keep it after the DOM changes.
- With a range stagger, `start` replaces the range's first value: `stagger([10, 20], { start: 100 })` gives 100 to 110.
- `utils.set` **changes the params object you pass**. It adds `duration` (about 1e-11) and `composition`. Do not reuse that object for `animate`.
- `utils.set` made inside a scope is registered and reverted with it, so the values you set are undone on `revert()` and on every refresh.
- `utils.cleanInlineStyles` pauses the animation. Calling it mid-animation freezes the animation and removes its styles.
- `utils.cleanInlineStyles` restores the inline values found **when the animation was created**. An animation created while another was mid-flight on the same element captures that half-way frame, and its clean-up puts it back (lab: cards stuck at `translateY(16px); opacity: 0`). A `{from: x}` value also takes its end from that frame. Revert the element's previous animation before starting the next; the template's `play()` does.
- `utils.get` reads only the first target. For DOM elements, the unit-less form returns a string with its unit (`'10px'`).
- `utils.round(x)` with one argument returns a **function** (x is taken as the decimal count). To round to a whole number, write `round(x, 0)`. The same rule applies to every chainable helper called with fewer arguments.
- `utils.random()` returns 0 or 1. It is not `Math.random()`. Use `random(0, 1, 3)` for decimals.
- `shuffle` changes the array you pass. Copy it first if order matters elsewhere, for example the array from `utils.$`.
- `engine.pause()` is not a hard freeze. Creating or resuming any Timer or Animation afterwards calls `engine.wake()`, which starts the frame loop again while `engine.paused` stays `true`. Checked in 4.5.0 source and by a runtime probe. To freeze one component, pause its own objects, or its scope's `revertibles`, instead.
- `engine.timeUnit = 's'` affects the whole app and rescales only `defaults.duration`. Hard-coded `duration: 800` values elsewhere now mean 800 seconds. Do not switch it on a page shared with other islands.
- `engine.speed`, `fps`, `precision`, `timeUnit`, `pauseOnDocumentHidden`, `useDefaultMainLoop` and `engine.defaults` are global to the page. A LiveView hook that changes them affects every island and every other hook.
- With `useDefaultMainLoop = false`, nothing moves until something calls `engine.update()`. That includes `utils.sync` callbacks.
- `engine.precision` also rounds the values reported by `currentTime` getters. Lowering it to save work makes those reports coarser.

## Lifecycle and cleanup

LiveView can patch or remove hook DOM at any moment. Build everything for a hook inside one Scope rooted at `this.el`, and call `scope.revert()` in `destroyed()`. Anything created outside the scope's synchronous context needs its own teardown.

- **Scope**: stop and restore with `scope.revert()`. It reverts every registered object, runs every cleanup callback, and removes its own `MediaQueryList` `change` listeners. It does **not** remove DOM listeners, classes or attributes your constructors added themselves, unless the returned cleanup does. It does not remove listeners bound elsewhere to `scope.methods.x`. A method wrapper still runs after `revert()`, and any objects it creates are registered with the emptied scope, which nothing will revert again. Remove those listeners yourself. A scope created inside another scope's constructor is reverted by the parent.
- **Scope refresh**: `refresh()` (also triggered by media queries) reverts and rebuilds the `add` objects. Objects from `addOnce` or `keepTime` stay. It is not teardown.
- **engine**: nothing to tear down per component. It owns one `visibilitychange` listener on `document`, added at module load and never removed. Its frame loop stops by itself when no tickable is active. If a hook set `useDefaultMainLoop = false` or changed any global setting, restore it in `destroyed()`. If a hook runs its own `engine.update()` loop, cancel that loop.
- **`utils.set` result (JSAnimation)**: `.revert()` restores the earlier inline style, transform, attribute or JS property values. Attributes it created are removed, attributes that already existed get their old values back, and a `style` attribute left empty is removed. If you never revert it, the inline values stay. Made inside a scope, it is reverted with the scope.
- **`utils.sync` result (Timer)**: ends itself after one time unit and leaves nothing behind. `.cancel()` stops it before the callback runs. Made inside a scope, it is registered with the scope.
- **`utils.keepTime` wrapper**: the wrapper has no state to clean. Each tickable it builds must be reverted: `revert()` the last returned tickable, or build it inside a scope. Calling the wrapper again reverts the previous one first.
- **`utils.cleanInlineStyles(anim)`**: removes that animation's inline CSS and transforms and pauses it. It does not cancel the animation, restore attributes, or unregister it. Use `anim.revert()` for a full restore.
- **`utils.remove(targets, …)`**: detaches tweens and cancels animations left empty. Inline values stay as they are, with no restore.
- **`stagger()` functions, number and random helpers, `get`**: plain functions with no DOM effects, listeners or timers. Nothing to clean. Throw staggers away along with their animation.
- **`utils.$` and any animated element**: Anime.js adds hidden symbol properties to each target it touches (registration flags and a transform cache). They are not removed and are harmless, but the transform cache means Anime.js rebuilds `transform` from its own record of values. If LiveView or other code rewrites the `style` attribute of an element that is still animating, the next frame can overwrite that change. Revert the scope before the server replaces animated nodes, or keep animated nodes out of patching with `phx-update="ignore"`.
