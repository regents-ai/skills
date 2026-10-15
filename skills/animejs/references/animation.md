# Anime.js v4: getting started, `animate()` and easings

Reference for the core of Anime.js 4.5.0 (npm `animejs`): installing and importing it, the `animate()` function with everything it accepts (targets, property kinds, value syntaxes, per-tween parameters, keyframes, playback settings, callbacks) and the `JSAnimation` object it returns, plus every easing the library ships. Read it before writing or reviewing any `animate()` call in a TypeScript island that runs inside a Phoenix LiveView hook. All names, defaults and types were checked against the 4.5.0 `.d.ts` files and, where the two disagreed, against the shipped JavaScript. Fetch a live page with `uv run scripts/animejs_docs.py <path>`, using the path shown in backticks after each heading. Badges: **JS** means only the JavaScript engine `animate()` has it, **WAAPI** means only `waapi.animate()` has it. No badge means both.

---

## Getting started `getting-started`

### Installation `getting-started/installation`

- npm: `npm install animejs` (in Phoenix, run it inside `assets/`). ESM: `import { animate } from 'animejs'`. CommonJS: `const { animate } = require('animejs')`.
- ESM from a CDN: `https://esm.sh/animejs` or `https://cdn.jsdelivr.net/npm/animejs/+esm`.
- UMD global: `https://cdn.jsdelivr.net/npm/animejs/dist/bundles/anime.umd.min.js` exposes a global `anime` object (`const { animate } = anime`).
- Files in `dist/`: `modules/index.js` (ESM entry), `modules/index.cjs` (CJS entry), `bundles/anime.esm.js`, `bundles/anime.esm.min.js`, `bundles/anime.umd.js`, `bundles/anime.umd.min.js`.

### Module imports `getting-started/module-imports`

Everything is a named export of `'animejs'`, and the package tree-shakes well with esbuild or Vite. The root module also re-exports four namespaces: `easings`, `utils`, `svg`, `text`, plus `globals`. Without a bundler, or where tree shaking is off, import from a subpath so only that module loads:

| Subpath | Main exports |
| --- | --- |
| `animejs/animation` | `animate`, `JSAnimation` |
| `animejs/timer` | `createTimer`, `Timer` |
| `animejs/timeline` | `createTimeline` |
| `animejs/animatable` | `createAnimatable` |
| `animejs/draggable` | `createDraggable` |
| `animejs/layout` | `createLayout` |
| `animejs/scope` | `createScope` |
| `animejs/engine` | `engine` |
| `animejs/events` | `onScroll` and scroll types |
| `animejs/easings` | `eases`, `cubicBezier`, `steps`, `linear`, `irregular`, `spring` |
| `animejs/utils` | `stagger`, `random`, `set`, `$`, `round` ... |
| `animejs/svg` | SVG helpers |
| `animejs/text` | `splitText` ... |
| `animejs/waapi` | `waapi` (an object with `.animate`) |

The package `exports` map also has `animejs/easings/{eases,linear,steps,irregular,cubic-bezier,spring}` and `animejs/adapters`, `animejs/adapters/three`, which the docs do not list. The docs show `import * as waapi from 'animejs/waapi'`. That yields a module namespace whose `animate` is at `waapi.waapi.animate`, so use `import { waapi } from 'animejs/waapi'`. Without a bundler, an `<script type="importmap">` can map `animejs` to `/node_modules/animejs/dist/modules/index.js` and each `animejs/<name>` to `.../dist/modules/<name>/index.js`.

```ts
import { animate as animateOnly } from 'animejs/animation';
import { spring as springOnly, eases as easesOnly } from 'animejs/easings';
```

### Vanilla JS `getting-started/using-with-vanilla-js`

No setup step: import the functions and call them. The docs' demo loops a scale on a logo, makes it draggable, and on each button click fires a new `animate()` for `rotate`. Each call returns an independent object, and calls on the same property replace each other (see `composition`).

React (`getting-started/using-with-react`): create everything inside `createScope({ root }).add(...)` in `useEffect` and return `() => scope.revert()`. The same idea applies to LiveView hooks.

---

## `animate()` `animation`

```
animate(targets: TargetsParam, parameters: AnimationParams): JSAnimation
```

- Import from `'animejs'` or `'animejs/animation'`. The parameters object mixes four kinds of keys: animatable properties, tween parameters, playback settings and callbacks. **Any key that is not a known setting is treated as a property to animate.**
- `waapi.animate(targets, params): WAAPIAnimation` is a lighter version (about 3 KB, against 10 KB for `animate`) built on the browser's Web Animations API. It has fewer features, targets DOM elements only, and returns a different class.
- The returned `JSAnimation` extends `Timer`. It is a thenable (see `then()`).

---

## Targets `animation/targets`

| Kind | Page | Accepts | Notes |
| --- | --- | --- | --- |
| CSS selector | `animation/targets/css-selector` | any `querySelectorAll` string | Queried against `document`, or the root of the active `createScope`. |
| DOM elements | `animation/targets/dom-elements` | `HTMLElement`, `SVGElement`, `SVGGeometryElement`, `NodeList` (runtime also takes `HTMLCollection`) | Preferred inside hooks: query from `this.el`. |
| JS objects **JS** | `animation/targets/javascript-objects` | plain `Object`, class instance | Numeric or color fields are animated in place. |
| Array of targets | `animation/targets/array-of-targets` | `Array` mixing any of the above | Flattened deeply. Duplicates and `null`/`undefined` are dropped. |

Types: `TargetsParam = TargetSelector | TargetSelector[]`, `TargetSelector = HTMLElement | SVGElement | Record<string, any> | NodeList | string`. `animation.targets` is always the resolved flat `Target[]`. If nothing resolves, the library logs `No target found...` and the animation has zero length.

```ts
const items = root.querySelectorAll<HTMLElement>('[data-item]');
return animate(items, { opacity: [0, 1], y: ['1rem', 0], delay: stagger(40) });
```

---

## Animatable properties `animation/animatable-properties`

For DOM targets, each key is classified in this order (taken from the runtime): SVG attribute on an SVG element, then transform name, then a `--` CSS variable, then a key that exists in `element.style` (CSS), then a key that exists on the element object (set as a JS property, e.g. `value`), else an HTML attribute via `setAttribute`. Non-DOM targets always use plain object properties.

| Kind | Page | Rule |
| --- | --- | --- |
| CSS properties | `animation/animatable-properties/css-properties` | Any numeric or color CSS property. Write hyphenated names in camelCase (`backgroundColor`) or as a quoted string (`'background-color'`). Prefer `opacity` and transforms; other properties trigger layout or paint. |
| CSS transforms | `animation/animatable-properties/css-transforms` | Individual transform keys, table below. Works in both JS and WAAPI (WAAPI needs `CSS.registerProperty` support, otherwise it does not animate). |
| CSS variables **JS** | `animation/animatable-properties/css-variables` | Key is the variable name as a string, e.g. `'--radius'`. Numeric or color values only. The way to reach `::before`/`::after`, which read the variable. WAAPI needs a `CSS.registerProperty` registration, otherwise it does not animate. Since 4.0.0. |
| JS object properties **JS** | `animation/animatable-properties/javascript-object-properties` | Numeric fields, color strings, or strings containing numbers (e.g. `'42%'`). |
| HTML attributes **JS** | `animation/animatable-properties/html-attributes` | Numeric or color attributes, e.g. `<input>` `value`. |
| SVG attributes **JS** | `animation/animatable-properties/svg-attributes` | Numeric or color attributes (`baseFrequency`, `scale` on filter primitives, `points`...). See the SVG helpers for paths and drawing. |

### Transform keys

Render order is fixed no matter the key order: `perspective` → `translate` → `rotate` → `scale` → `skew`. Adjacent axis keys are merged into one CSS function (e.g. `translateX` + `translateY` become `translate(x, y)`).

| Key | Short | Default value | Default unit |
| --- | --- | --- | --- |
| `translateX` | `x` | `'0px'` | `px` |
| `translateY` | `y` | `'0px'` | `px` |
| `translateZ` | `z` | `'0px'` | `px` |
| `rotate`, `rotateX`, `rotateY`, `rotateZ` | | `'0deg'` | `deg` |
| `scale`, `scaleX`, `scaleY`, `scaleZ` | | `'1'` | none |
| `skew`, `skewX`, `skewY` | | `'0deg'` | `deg` |
| `perspective` | | `'0px'` | `px` |

- JS `animate()` reads the starting transform only from the element's **inline** `style.transform`. Transforms set by a stylesheet class are ignored, so the animation starts from the defaults. Seed a starting value with `utils.set(el, { x: ... })` first.
- To animate the whole `transform` string, use `waapi.animate(el, { transform: '...' })`.
- Since 4.4.0: fixed render order, and `matrix` / `matrix3d` can no longer be animated (they are still kept when read from inline styles).

A CSS variable used as the animated property:

```ts
utils.set(el, { '--glow': '0px', boxShadow: () => '0 0 var(--glow) currentColor' });
return animate(el, { '--glow': '24px', alternate: true, loop: true });
```

Passing the `var()` string through a function stops `utils.set` from resolving and converting it, so the property keeps pointing at the live variable.

---

## Tween value types `animation/tween-value-types`

A property's value can be any of the following, or an array (keyframes) or a `{ to, from, ... }` object (tween parameters).

| Type | Page | Since | Accepts / behavior |
| --- | --- | --- | --- |
| Numerical | `animation/tween-value-types/numerical-value` | 1.0.0 | `Number`, or a `String` holding at least one number. With no unit, CSS properties take the browser default (`px`). JS `animate()` reuses a unit set earlier on the same target property (`'50%'` then `75` gives `'75%'`). WAAPI adds `px` automatically only for `x/translateX`, `y/translateY`, `z/translateZ`, `perspective`, `top`, `right`, `bottom`, `left`, `width`, `height`, `margin`, `padding`, `borderWidth`, `borderRadius`, `fontSize`. |
| Unit conversion | `animation/tween-value-types/unit-conversion-value` | 2.0.0 | `String` with a different unit from the current one (`'25%'`, `'15rem'`, `'.75turn'`). JS converts from the current unit, which can be unreliable. For predictable output, `utils.set` the unit first or use WAAPI. |
| Relative **JS** | `animation/tween-value-types/relative-value` | 2.0.0 | `'+=N'` adds, `'-=N'` subtracts, `'*=N'` multiplies the current value. A unit is allowed (`'+=45px'`, `'-=45deg'`). |
| Color | `animation/tween-value-types/color-value` | 1.0.0 | HEX `'#F44'` / `'#FF4444'`, HEXA `'#F443'` / `'#FF444433'`, `rgb()`, `rgba()`, `hsl()`, `hsla()`. Named colors (`'red'`) work only with **WAAPI**. |
| Color function **WAAPI** | `animation/tween-value-types/color-function-value` | 4.0.0 | CSS `color()` in any color space, e.g. `'color(display-p3 1 0.27 0.27 / 1)'`. |
| CSS variable | `animation/tween-value-types/css-variable` | 4.2.0 | `'var(--name)'` as a value. JS resolves it once when the animation is created. After changing the variable, call `.refresh()` to read it again. |
| Function based | `animation/tween-value-types/function-based` | 1.0.0 | `(target, index, targets, prevTween) => value`. Called once per target. |

```ts
animate(el, { rotate: '+=90', x: '-=2rem', scale: '*=1.5' });
animate(el, { width: '50%' });
```

```ts
el.style.setProperty('--dx', '120px');
const anim = animate(el, { x: 'var(--dx)' });
el.style.setProperty('--dx', '240px');
anim.restart().refresh();
```

### Function-based values

Signature (`FunctionValue`): `(target?: Target, index?: number, targets?: TargetsArray, prevTween?: Tween | null) => number | string | TweenKeyValue | EasingParam | Array<...>`.

| Arg | Meaning |
| --- | --- |
| `target` | the target being set up |
| `index` | its position in `animation.targets` |
| `targets` | the full resolved target array (since 4.4.0; it was `total: number` before, so replace `total` with `targets.length`) |
| `prevTween` | the previous sibling tween's computed end value for the same target and property |

- The function can return a tween value or a tween parameter object (`{ to, duration, ease, ... }`).
- Function values also work for `duration`, `delay`, `ease` and `composition`, but not for `modifier` or `loopDelay`.
- If the function returns `undefined`, `null`, `NaN` or `false`, the value becomes `0`.
- `.refresh()` calls the functions again for property values, but not for `duration`/`delay`.
- TypeScript: a one-argument function on a property key cannot be contextually typed, because the params type is a string-keyed union that also contains one-argument callbacks and modifiers. Annotate it (`(target: Target) => ...`). Functions with zero, two or more arguments are inferred.

```ts
return animate(root.querySelectorAll('li'), {
  x: (target, index, targets) => (targets!.length - index!) * 12,
  y: (target: Target) => Number((target as HTMLElement).dataset.offset ?? 0),
  duration: () => utils.random(600, 900),
  ease: (_t, i) => (i! % 2 ? 'outBack' : 'outQuad'),
});
```

```ts
return animate(root.querySelectorAll('li'), {
  x: (_t, i) => ({ to: i! * 20, duration: 300 + i! * 100, ease: 'out(3)' }),
});
```

---

## Tween parameters `animation/tween-parameters`

Set them at the top level of the params (global: they apply to every property) or inside a property's object (local: they override the global value for that property only). `TweenParamsOptions = { duration, delay, ease, modifier, composition }` plus `TweenValues = { from, to }`.

| Name | Page | Type | Default | Meaning |
| --- | --- | --- | --- | --- |
| `to` | `animation/tween-parameters/to` | tween value, or `[from, to]` pair | current value (when only `from` is given) | End value. Local only. Required unless `from` is set. Since 4.0.0. |
| `from` | `animation/tween-parameters/from` | tween value | current value (when only `to` is given) | Start value; animates from it to the current value. Local only. Required unless `to` is set. Since 4.0.0. |
| `delay` | `animation/tween-parameters/delay` | `number ≥ 0` or function | the animation's `delay` (default `0`) | Wait before the tween starts, in ms. |
| `duration` | `animation/tween-parameters/duration` | `number ≥ 0` or function | the animation's `duration` (default `1000`) | Tween length in ms. Values above `1e12` or `Infinity` are clamped to `1e12`. |
| `ease` | `animation/tween-parameters/ease` | built-in name `string`, `EasingFunction`, `Spring`, or function returning one | `'out(2)'` | Rate-of-change curve for this tween. Since 4.0.0. |
| `composition` **JS** | `animation/tween-parameters/composition` | `'replace' \| 'none' \| 'blend' \| 0 \| 1 \| 2` | `'replace'`, or `'none'` when there are 1000 or more targets | What happens when another animation drives the same property of the same target. Since 4.0.0. |
| `modifier` **JS** | `animation/tween-parameters/modifier` | `(value: number) => number \| string` | identity (docs say `null`) | Changes the numeric value on each frame, before any unit is added back. Most `utils` helpers (`utils.round(0)`, `utils.clamp`, `utils.snap`...) work as modifiers. Since 4.0.0. |

Composition modes:

| Mode | Effect |
| --- | --- |
| `'replace'` / `0` | The new tween takes over the property and cancels the older animation's overlapping tweens. If all of the older animation's tweens are replaced, it pauses (`onPause` fires). |
| `'none'` / `1` **JS** | No bookkeeping. Both animations keep writing to the property and the longer one wins at the end. Faster to create. |
| `'blend'` / `2` **JS** | Additive: values from animations running at once are summed. Best for movement (`translate`, `scale`, `rotate`). Only works when all blended animations play **forward** at the same time. Not supported with multi-keyframe values, colors, `reverse()`, `loop`, `reversed` or `alternate`. |

```ts
return animate(el, {
  x: { to: '16rem', ease: 'inOut(3)', duration: 800 },
  opacity: { from: 0 },
  rotate: { from: '-1turn', to: 0, delay: 200 },
  duration: 600,
  delay: 100,
  ease: 'outQuad',
});
```

Defaults for all of these (and for playback settings and callbacks) live in `engine.defaults`, typed `DefaultsParams`. Changing a value there affects every animation created afterwards in the page:

```ts
engine.defaults.duration = 400;
engine.defaults.ease = 'out(3)';
engine.defaults.composition = 'replace';
```

---

## Keyframes `animation/keyframes`

| Form | Page | Since | Shape | Timing |
| --- | --- | --- | --- | --- |
| Tween value keyframes | `animation/keyframes/tween-values-keyframes` | 4.0.0 | `prop: [v0, v1, v2, ...]` | The first value is the `from`. Each transition gets `duration / (n - 1)`. A 2-item array `[from, to]` is the quick way to set a start value. |
| Tween parameter keyframes **JS** | `animation/keyframes/tween-parameters-keyframes` | 2.0.0 | `prop: [{ to, ease, duration, delay, modifier }, ...]` | Each keyframe without a `duration` gets `duration / n`. |
| Duration-based keyframes **JS** | `animation/keyframes/duration-based-keyframes` | 2.0.0 | `keyframes: [{ x, y, ease, duration, delay, modifier }, ...]` | Several properties per step. Steps run one after another. Each step without a `duration` gets `duration / n`. |
| Percentage-based keyframes **JS** | `animation/keyframes/percentage-based-keyframes` | 4.0.0 | `keyframes: { '0%': { x, ease }, '50%': {...}, '100%': {...} }` | Like CSS `@keyframes`. Keys are percentages of the total `duration`. Only `ease` can be set per step, and each value must be a plain tween value. The first key gives the `from`. |

- A keyframe's `ease` controls the segment from that keyframe to the next one. The top-level `ease` applies to segments that set none. `playbackEase` (a playback setting) then reshapes time across the whole sequence.
- `delay` in array keyframes adds a gap before that step. The global `delay` only applies to the first keyframe.
- When `playbackEase` is set and no `ease` is given, segments default to `'linear'` instead of `'out(2)'`, so the playback ease alone shapes the motion.

```ts
animate(el, { x: [0, 100, 50], duration: 900 });
animate(el, {
  y: [
    { to: -40, ease: 'out(3)', duration: 300 },
    { to: 0, ease: 'outBounce', duration: 600, delay: 100 },
  ],
});
animate(el, {
  keyframes: [
    { y: -40, duration: 300 },
    { x: 120, scale: 0.8 },
    { y: 0, ease: 'in' },
  ],
  duration: 1500,
});
animate(el, {
  keyframes: {
    '0%': { x: 0, ease: 'out' },
    '40%': { x: 120, y: -30 },
    '100%': { x: 0, y: 0 },
  },
  duration: 2000,
  playbackEase: 'inOut(2)',
});
```

---

## Playback settings `animation/animation-playback-settings`

All are top-level keys. Each default can be changed through `engine.defaults.<name>`.

| Name | Page | Type | Default | Meaning |
| --- | --- | --- | --- | --- |
| `delay` | `.../delay` | `number ≥ 0` or function | `0` | Default delay (ms) for every tween. `onBegin` waits for it. |
| `duration` | `.../duration` | `number ≥ 0` or function | `1000` | Default tween duration (ms). `0` completes as soon as it plays. Clamped to `1e12`. |
| `loop` | `.../loop` | `number \| boolean` | `0` | Number of **extra** iterations. `true`, `Infinity` and `-1` all mean forever. |
| `loopDelay` **JS** | `.../playback-loopdelay` | `number ≥ 0` | `0` | Pause (ms) between iterations. Not function-based. Since 4.0.0. |
| `alternate` | `.../alternate` | `boolean` | `false` | Flip direction on each iteration. Needs `loop` of `1` or more (or `true`). Since 4.0.0. |
| `reversed` | `.../reversed` | `boolean` | `false` | Start playing backwards. Since 4.0.0. |
| `autoplay` | `.../autoplay` | `boolean \| ScrollObserver` | `true` | `false`: wait for `.play()`. `onScroll({...})`: playback driven by scroll thresholds. Forced to `false` inside a timeline. |
| `frameRate` **JS** | `.../framerate` | `number > 0` | `240` | Frame cap (fps), limited in practice by the display and browser. Change later with `anim.fps`. Since 4.0.0. |
| `playbackRate` | `.../playbackrate` | `number ≥ 0` | `1` | Speed multiplier. `0` freezes it. Change later with `anim.speed`. Since 4.0.0. |
| `playbackEase` **JS** | `.../playbackease` | `EasingParam` | `null` | One ease applied to the whole run (all keyframes) instead of per segment. Since 4.0.0. |
| `persist` **WAAPI** | `.../persist` | `boolean` | `false` (`true` for scroll-linked WAAPI animations) | Keep a finished WAAPI animation alive so methods still work on it. Otherwise the browser animation is cancelled and freed when it ends. Since 4.2.0. |
| `id` | not a docs page | `number \| string` | an auto-increment number | Label, readable as `anim.id`. |

(`...` = `animation/animation-playback-settings`.)

`duration` (the animation property) counts every iteration: `(iterationDuration + loopDelay) × (loop + 1) − loopDelay`. With `loop: true` it is `1e12`.

```ts
const anim = animate(el, {
  x: 200,
  loop: 3,
  loopDelay: 250,
  alternate: true,
  reversed: false,
  autoplay: false,
  frameRate: 30,
  playbackRate: 1.5,
  playbackEase: 'inOut',
});
anim.fps = 60;
anim.speed = 0.5;
return anim.play();
```

---

## Callbacks `animation/animation-callbacks`

Every callback receives the animation as its only argument (`Callback<JSAnimation>`). Default: no-op. Change the default globally with `engine.defaults.onX`. All since 4.0.0.

| Name | Page | Fires |
| --- | --- | --- |
| `onBegin` **JS** | `.../onbegin` | Once, when playback starts (after `delay`). |
| `onComplete` | `.../oncomplete` | Once, after the last iteration ends. Also fired by `.complete()` unless muted. |
| `onBeforeUpdate` **JS** | `.../onbeforeupdate` | Each tick, before tween values are computed. Use it to change inputs a `modifier` reads. |
| `onUpdate` **JS** | `.../onupdate` | Each tick at `frameRate` while running, **including** `loopDelay` gaps. |
| `onRender` **JS** | `.../onrender` | Only on ticks that actually write values. Skipped during `delay` and `loopDelay`. Also fired once at creation when `autoplay: false` and a `from` value is set. |
| `onLoop` **JS** | `.../onloop` | Each time an iteration ends and another begins (not after the last). |
| `onPause` **JS** | `.../onpause` | When a running animation stops: `.pause()`, `.cancel()`, `.revert()`, all of its tweens replaced by a `'replace'` animation, or all targets removed with `utils.remove`. |
| `then(cb?)` | `.../then` | Method, not a param. Returns a `Promise` that resolves when the animation completes (immediately if it already has). |

(`...` = `animation/animation-callbacks`.)

```ts
await animate(el, { opacity: 0, duration: 200 });
const slide = animate(el, { x: 10 });
slide.then(() => console.log(slide.targets.length));
```

`then()` exists so that `await anim` works: while the callback runs, `then` is set to `null` to avoid infinite recursion. In the types this makes the callback's argument `JSAnimation & { then: null }`, which TypeScript reduces to `never`. Use the outer variable (as above), not the argument.

---

## Methods `animation/animation-methods`

All return the animation, so they chain. Page paths are `animation/animation-methods/<name>`.

| Method | Since | Signature | Effect |
| --- | --- | --- | --- |
| `play()` | 1.0.0 | `(): this` | Play forward (flips direction first if reversed). |
| `reverse()` | 1.0.0 | `(): this` | Play backward. |
| `pause()` | 1.0.0 | `(): this` | Stop at the current time. Fires `onPause` if it was running. |
| `restart()` | 1.0.0 | `(): this` | Reset to time 0 and resume. |
| `alternate()` | 1.0.0 | `(): this` | Flip direction and remap `currentTime` to the same visual point. Does not resume a paused animation. |
| `resume()` | 1.0.0 | `(): this` | Continue in the current direction. |
| `complete()` | 4.0.0 | `(muteCallbacks?: boolean \| number): this` | Jump to the end state, fire `onComplete` (unless muted), then `cancel()`. The docs do not list the argument. |
| `cancel()` | 4.0.0 | `(): this` | Pause, leave the engine loop, drop its tweens from composition. Values stay where they are. Can be revived with `play()`/`restart()`/`seek()`. |
| `revert()` | 4.0.0 | `(): this` | Cancel, restore every value this animation touched to what it was before, and revert a linked `onScroll` observer. Use it to destroy an animation. |
| `reset(softReset?)` **JS** | 3.0.0 | `(softReset = false): this` | Pause and reset `currentTime`, `progress`, `reversed`, `began`, `completed`. With `true`, internal state only, no render. |
| `seek(time, muteCallbacks?)` | 1.0.0 | `(time: number, muteCallbacks?: boolean \| number, internalRender?: boolean \| number): this` | Jump to `time` ms (delay excluded). Keeps its play/pause state. The third argument is internal (types only). |
| `stretch(duration)` **JS** | 4.0.0 | `(newDuration: number): this` | Rescale the total duration (all iterations) and every tween, delay and `loopDelay` in proportion. Stretching to `0` makes every tween `0` long, so they stay equal on later stretches. |
| `refresh()` **JS** | 4.0.0 | `(): this` | Re-run function-based and `var()` property values: `from` becomes the current value and `to` is computed again. `duration`/`delay` are not refreshed. |

```ts
anim.play().pause().resume().reverse().alternate().restart();
anim.seek(500, true);
anim.stretch(2000);
anim.refresh();
anim.reset(true);
anim.complete();
anim.cancel();
anim.revert();
```

---

## Properties `animation/animation-properties`

Available on `JSAnimation`. Rows without a badge also exist on `WAAPIAnimation`. The setters for time and progress seek (pausing then resuming if it was running).

| Name | Type | Access | Meaning |
| --- | --- | --- | --- |
| `id` **JS** | `string \| number` | get/set | Identifier. |
| `targets` | `Target[]` | get | Resolved targets. |
| `currentTime` | `number` | get/set | Global time in ms, clamped to `[-delay, duration]`. |
| `iterationCurrentTime` **JS** | `number` | get/set | Time inside the current iteration. |
| `deltaTime` **JS** | `number` | get | ms since the previous frame. |
| `progress` | `number` | get/set | Overall progress, `0`..`1`. |
| `iterationProgress` **JS** | `number` | get/set | Progress of the current iteration, `0`..`1`. |
| `currentIteration` **JS** | `number` | get/set | Current iteration index. |
| `duration` | `number` | get | Total ms including loops and loop delays. |
| `speed` | `number` | get/set | Playback-rate multiplier. |
| `fps` **JS** | `number` | get/set | Frame cap. |
| `paused` | `boolean` | get/set | Paused state. |
| `began` **JS** | `boolean` | get/set | Has started. |
| `completed` | `boolean` | get/set | Has finished. |
| `reversed` **JS** | `boolean` | get/set | Direction flag. Setting it calls `reverse()`/`play()`. |
| `backwards` **JS** | `boolean` | get | Currently moving backwards (e.g. an `alternate` return leg). |
| `cancelled` **JS** | `boolean` | get/set | In the types only. `true` after `cancel()`/`revert()`/`complete()`. Setting `false` resets and plays. |
| `iterationDuration`, `iterationCount` **JS** | `number` | get | In the types only. One iteration's ms, and total iterations (`loop + 1`). |

```ts
anim.currentTime = 250;
anim.progress = 0.5;
anim.iterationProgress = 0.25;
anim.currentIteration = 1;
anim.reversed = true;
anim.id = 'hero';
```

---

## Easings `easings`

Use an easing in `ease` (per tween or global), in `playbackEase`, and in `stagger(..., { ease })`. Import from `'animejs'`, from `'animejs/easings'`, or through the `easings` namespace (`easings.eases.inOut(3)`, `easings.spring(...)`). Type: `EasingParam = string | EaseStringParamNames | EasingFunction | Spring | TweakRegister`, where `EasingFunction = (time: number) => number`.

### Built-in eases `easings/built-in-eases` (since 1.0.0)

Pass them as a string (`ease: 'outQuad'`, `ease: 'outElastic(.8, 1.2)'`) or as functions on `eases` (`eases.outQuad`, `eases.outElastic(.8, 1.2)`). Every family has four variants: `in<X>`, `out<X>`, `inOut<X>`, `outIn<X>`.

| Family | Names | Parameters (runtime default) |
| --- | --- | --- |
| Linear | `'linear'` (alias `'none'`) | none |
| Power | `'in'`, `'out'`, `'inOut'`, `'outIn'` | `power`: docs give `1.675`, the runtime uses `1.68`. `'out(3)'` = cubic out. |
| Quad, Cubic, Quart, Quint | `'inQuad'` ... `'outInQuint'` | none (powers 2, 3, 4, 5) |
| Sine | `'inSine'` ... `'outInSine'` | none |
| Expo | `'inExpo'` ... `'outInExpo'` | none |
| Circ | `'inCirc'` ... `'outInCirc'` | none |
| Bounce | `'inBounce'` ... `'outInBounce'` | none |
| Back | `'inBack'` ... `'outInBack'` | `overshoot`: docs give `1.70158`, the runtime uses `1.7` |
| Elastic | `'inElastic'` ... `'outInElastic'` | `amplitude` = `1` (clamped `1..10`), `period` = `.3` (clamped `>0..2`) |

The default ease for every tween is `'out(2)'`. Function forms: `eases.in/out/inOut/outIn: (power?) => EasingFunction`, `eases.*Back: (overshoot?) => EasingFunction`, `eases.*Elastic: (amplitude?, period?) => EasingFunction`. Every other `eases.*` entry is already an `EasingFunction`.

WAAPI also takes native CSS strings (`'ease'`, `'ease-in'`, `'ease-out'`, `'ease-in-out'`, `'step-start'`, `'step-end'`, `'steps(6, start)'`, `'cubic-bezier(...)'`, `'linear(...)'`).

### Parametric eases

| Function | Page | Since | Signature (runtime defaults) | Meaning |
| --- | --- | --- | --- | --- |
| `cubicBezier` | `easings/cubic-bezier-easing` | 2.0.0 | `cubicBezier(x1 = .5, y1 = 0, x2 = .5, y2 = 1): EasingFunction` | CSS-style Bézier. `x1`, `x2` must be in `0..1`. `y` values can go past the range (below 0 pulls back first, above 1 overshoots). WAAPI: pass the string `'cubic-bezier(...)'` or `'cubicBezier(...)'`. |
| `linear` | `easings/linear-easing` | 4.0.0 | `linear(...stops: (number \| string)[]): EasingFunction` | Piecewise-linear through the stops (at least 2). A stop is a number (output value, 0 = start, 1 = end, may overshoot) or `'value pct%'` to pin its timing. Timing is not allowed on the first and last stops. Stops without timing are spread evenly. WAAPI: the string `'linear(0, 0.5 50%, 1)'`. |
| `steps` | `easings/steps-easing` | 3.0.0 | `steps(steps = 10, fromStart = false): EasingFunction` | Jumps in equal steps. `fromStart: true` jumps at the start of each step, else at the end. WAAPI: `'steps(5)'`, `'steps(5, start)'`. |
| `irregular` | `easings/irregular-easing` | 4.0.0 | `irregular(length = 10, randomness = 1): EasingFunction` | Linear path through randomized points. `randomness` scales how far they stray. JS only (WAAPI gets it converted to a `linear()` string). Random on every call. |

```ts
animate(el, { x: 100, ease: 'outElastic(1, .5)' });
animate(el, { x: 100, ease: eases.outBack(2.5) });
animate(el, { x: 100, ease: cubicBezier(0.7, 0.1, 0.5, 0.9) });
animate(el, { x: 100, ease: steps(5, true) });
animate(el, { x: 100, ease: linear(0, '0.8 40%', 1) });
animate(el, { x: 100, ease: irregular(12, 0.5) });
waapi.animate(el, { x: 100, ease: 'cubic-bezier(0, 0, 0.58, 1)' });
```

### Spring `easings/spring` (since 3.0.0)

`spring(parameters?: SpringParams): Spring`. The result is a `Spring` object, not a plain function. It carries `.ease` and a computed `.settlingDuration`, and **its settling time replaces the tween's `duration`** (e.g. `spring({ bounce: .2, duration: 300 })` makes an animation about 640 ms long whatever `duration` says). `createSpring()` is a deprecated alias that logs a warning.

Two ways to set it up (the perceived pair wins if either of its keys is set; it resets `mass` to 1 and `velocity` to 0):

| Group | Key | Type | Range | Default | Meaning |
| --- | --- | --- | --- | --- | --- |
| Perceived (SwiftUI model) | `bounce` | `number` | `-1..1` | `0.5` | `0..1`: bouncy. Below `0`: over-damped. Keep it within `-.5..0.5`, because extreme values fight `duration`. |
| Perceived | `duration` | `number` (ms) | `10..10000` | `628` | When the motion looks finished. Not the settle time. |
| Physics | `mass` | `number` | `1..10000` | `1` | More mass means heavier, slower motion. |
| Physics | `stiffness` | `number` | `0..10000` | `100` | Stiffer means faster and snappier. |
| Physics | `damping` | `number` | `0..10000` | `10` | More damping means less oscillation. |
| Physics | `velocity` | `number` | `-10000..10000` | `0` | Starting speed toward the target. |
| Callback **JS** | `onComplete` | `(anim: JSAnimation) => any` | | no-op | Fires when the **perceived** duration is reached, usually well before the animation's own `onComplete` (which waits for the settle time). |

The instance exposes get/set `bounce`, `duration`, `stiffness`, `damping`, `mass`, `velocity` (setting one recomputes the curve), plus `settlingDuration`, `completed`, `parent`. With no arguments, `spring()` equals `bounce .5, duration 628` and settles in about 1760 ms.

```ts
animate(el, { x: 100, ease: spring({ bounce: 0.3, duration: 400 }) });
animate(el, {
  x: 100,
  ease: spring({ stiffness: 120, damping: 14, mass: 1, velocity: 0, onComplete: (anim) => anim.targets }),
});
```

A `Spring` stores the last animation that used it (`parent`) and one `completed` flag. If you need its `onComplete`, create one spring per animation:

```ts
return items.map((item) =>
  animate(item, { y: 0, ease: spring({ bounce: 0.25, onComplete: (a) => a.targets }) }),
);
```

---

## Rewriting v3 code

Source: the library's GitHub wiki page "Migrating from v3 to v4", checked against 4.5.0. v4 does
not reject v3 option names; it animates them as properties (Gotcha 1), so convert every one.

| v3 | v4 |
| --- | --- |
| `import anime from 'animejs'`; `anime({targets, ...})` | `import {animate} from 'animejs'`; `animate(targets, {...})` |
| `easing: 'easeOutQuad'` | `ease: 'outQuad'` (drop the `ease` prefix everywhere). Default is now `'out(2)'` |
| `easing: 'spring(1, 80, 10, 0)'` | `ease: spring({mass: 1, stiffness: 80, damping: 10, velocity: 0})`. The wiki's `createSpring()` is deprecated in 4.5 and logs a warning |
| `easing: () => t => ...` | `ease: t => ...` (pass the easing function itself) |
| `{value: x, duration}` per property or keyframe | `{to: x, duration}` |
| `direction: 'reverse'` / `'alternate'` | `reversed: true` / `alternate: true` |
| `loop: n` meant n plays in total | `loop: n` means n repeats after the first play |
| `endDelay` | `loopDelay`; it only pauses between loops, never after the last one |
| `round: 100` | `modifier: utils.round(2)` (argument is decimal places) |
| `begin`, `update`, `complete`, `change` | `onBegin`, `onUpdate`, `onComplete`, `onRender`. `onBegin` now waits for `delay` |
| `loopBegin`, `loopComplete` | one `onLoop` |
| `changeBegin`, `changeComplete` | removed |
| `animation.finished.then(...)` | `animation.then(...)` |
| `anime.timeline({easing, duration})` | `createTimeline({defaults: {ease, duration}})`; children now honour their own `loop` |
| `stagger(n, {direction: 'reverse', easing})` | `stagger(n, {reversed: true, ease})` |
| `play()` resumed in the last direction; `reverse()` toggled | `play()` always forward, `reverse()` always backward, `resume()` keeps direction, `alternate()` toggles |
| `anime.path(el)` → `{x, y, angle}` | `svg.createMotionPath(el)` → `{translateX, translateY, rotate}` |
| `strokeDashoffset: [anime.setDashoffset, 0]` | `animate(svg.createDrawable(el), {draw: '0 1'})` |
| `anime.get` / `set` / `remove` / `random` | `utils.get` / `utils.set` / `utils.remove` / `utils.random` |
| `animation.tick(t)` | `engine.useDefaultMainLoop = false` plus `engine.update()` from your own loop |
| `anime.suspendWhenDocumentHidden` | `engine.pauseOnDocumentHidden` |
| `anime.running` | removed |

## Where the docs and the 4.5.0 types or runtime disagree

- `spring` `bounce`/`duration`: the JSDoc in the types says the default is `0`. The runtime uses `0.5`/`628`, as the docs say.
- `modifier` default: the docs say `null`. The runtime default is an identity function.
- Power ease default: the docs and the type string literals say `1.675`, the runtime uses `1.68`. Back overshoot: the docs say `1.70158`, the types and runtime use `1.7`.
- `complete(muteCallbacks?)`, `seek(..., internalRender?)`, the `cancelled` property, `iterationDuration` and `iterationCount` are in the types but not in the docs.
- `TweenValues` / `TweenObjectValue` in the types include `fromTo`. The 4.5.0 runtime never reads it, so do not use it.
- `priority` is typed on `TimerOptions` (so `animate` accepts it), but it is not a known default key, so `animate()` would also treat it as a property to animate.
- `import * as waapi from 'animejs/waapi'` (as the docs show) gives a namespace with no `animate`. Use `import { waapi } from 'animejs/waapi'`.
- The WAAPI option types spell `Reversed` and `Alternate` with capitals, while the docs use `reversed`/`alternate`. The lowercase keys still type-check through the index signature.
- `then(cb)`: the callback argument's type reduces to `never` (see Callbacks).
- The `.d.ts` files name `NodeJS.Immediate` (engine) and `NodeJS.Timeout` (text splitter). A browser-only project with `skipLibCheck: false` and no `@types/node` fails to compile. Add `@types/node`, set `skipLibCheck: true`, or declare an empty `NodeJS` namespace.

---

## Gotchas

1. **Unknown keys become properties.** Any key not in `engine.defaults` is animated. v3 options such as `easing`, `direction: 'alternate'`, `endDelay`, or a misspelled `onCompete` (as in the docs' own spring example) are not errors. On DOM targets they turn into CSS or attribute tweens, and on objects they are written onto the object. v4 uses `ease`, `alternate`, `loopDelay`, `onComplete`.
2. **Unknown ease strings fall back to linear silently.** `'ouIn(5)'` (a typo in several docs examples) plays linear with no warning. The strings `'steps(...)'`, `'linear(...)'`, `'cubicBezier(...)'` and `'irregular(...)'` log a warning and also play linear in JS `animate()`: import the function instead. Those strings only work in `waapi.animate()`.
3. **Stylesheet transforms are invisible to JS `animate()`.** It reads only inline `style.transform`, so a class-applied `translate` or `scale` is ignored and later overwritten. Seed the value with `utils.set` or use WAAPI.
4. **`loop: 3` means 4 plays.** `loop` counts repeats. `alternate` needs `loop ≥ 1` to show the return leg.
5. **Spring overrides `duration`**, and the animation's `onComplete` waits for the settle time (often 2 to 3 times the perceived `duration`). Put UI-follow-up logic in the spring's own `onComplete`, or chain on the perceived time.
6. **`'blend'` restrictions**: forward play only, no keyframe arrays, colors, `loop`, `reversed`, `alternate` or `reverse()`.
7. **Composition default switches at 1000 targets** to `'none'`, so large staggered sets stop replacing earlier animations on the same properties.
8. **Units stick.** After a `'%'` tween, a unitless number on the same property keeps `%`. Cross-unit conversions (`px`→`%`, `px`→`rem`) are computed once from layout and can be off, so set the unit first.
9. **`var()` values are resolved once.** Changing the CSS variable later does nothing until `.refresh()`. Animating the variable itself (`'--x': ...`) is the live alternative.
10. **Function values that return nothing become `0`**. A `dataset` read on a missing attribute sends the element to 0 rather than leaving it alone.
11. **`refresh()` does not recompute `duration`/`delay`.** Create a new animation for new timing.
12. **String selectors query the whole document** unless a Scope is active, in which case they resolve against its `root`. In a hook, create animations inside `createScope({root: this.el})` so a second instance of the same component elsewhere is not animated too.
13. **`autoplay` is ignored inside timelines**, and `autoplay: false` with a `from` value still renders the `from` state immediately (one `onRender` at creation).
14. **Durations are in ms** unless `engine.timeUnit = 's'` is set, which changes every duration, delay and spring value globally.
15. **`engine.defaults` is global and lives as long as the JS bundle.** In LiveView the bundle survives live navigation, so a changed default leaks into every later page. Set defaults once at app boot or not at all.
16. **The engine pauses when the tab is hidden** (`engine.pauseOnDocumentHidden = true`) and catches up on return. Do not use animation callbacks as timers.
17. **WAAPI animations end and are cancelled** unless `persist: true`. Calling `alternate()`/`resume()` on a finished one then does nothing.

---

## Lifecycle and cleanup

Context: these objects run inside LiveView hooks, and the server can patch or remove the DOM at any time. Create them inside the hook's Scope and call `scope.revert()` in `destroyed()`; the canonical hook is in [liveview-islands.md](liveview-islands.md#canonical-hook-lab). The notes below say what each object leaves behind if it is torn down on its own.

- **`JSAnimation` (`animate()`)**
  - Stop and restore: `revert()`. It cancels, then puts back each touched value as it was when the animation was created: the original inline style or attribute is rewritten, and a property that had none is removed (`style.removeProperty`, `removeAttribute`). An emptied `style=""` attribute is removed. It also reverts a linked `onScroll` observer. Object targets get their original field value back only if it was truthy.
  - Stop and keep the current look: `pause()` (still registered, resumable) or `cancel()` (leaves the engine loop and composition). `complete()` jumps to the end state, fires `onComplete`, then cancels.
  - Leaves behind until reverted: inline `style` entries (including a composed `transform`), attributes, and changed object fields. On each registered element it also keeps hidden symbol properties, including a per-element transform cache that is never cleared. No event listeners and no observers, unless `autoplay` is an `onScroll()` observer, whose cleanup `revert()` handles.
  - Not cleaned up automatically when elements leave the DOM. A looping animation keeps ticking against detached nodes until cancelled. Only `utils.remove(target)` detaches targets, and it fires `onPause` once none are left.
  - `revert()`, `cancel()` and `pause()` fire `onPause`. Make `onPause` safe to run during teardown (no `pushEvent` after `destroyed`).
  - `then()`/`await` never resolves after `cancel()`/`revert()`. An `async` hook method awaiting an animation that gets destroyed hangs forever and keeps its closure alive. Race it against a teardown signal, or use `onComplete`.
  - LiveView patching makes the element's attributes match the server's markup, so a re-render of an element that Anime styled can remove its inline `style`. Anime's per-element transform cache survives that, and the next transform tween on the element writes back every cached transform part. The patch rules and fixes are in [liveview-islands.md](liveview-islands.md#what-a-liveview-patch-does-to-animejss-dom-writes).
- **`WAAPIAnimation` (`waapi.animate()`, `persist`)**: `cancel()` runs `commitStyles()` first, so the current values stay as inline styles and the browser animations are freed. `revert()` cancels and then restores the inline styles it recorded at creation, removing the ones that were empty, and drops an empty `style` attribute. Without `persist`, each browser animation commits its styles and cancels itself when it finishes. With `persist: true` it stays alive until cancelled or reverted, so always tear it down in `destroyed()`. Individual transforms are written as `transform: translateX(var(--translateX)) ...` with registered custom properties. `cancel()`/`revert()` also leave `then()` unresolved. No listeners or observers unless scroll-linked. Full details in the WAAPI reference.
- **`Spring` (`spring()`)**: plain data with no DOM, listeners or engine registration. Nothing to clean up. It holds a reference to the last animation that used it (`parent`), so drop it with the animation, and do not share one spring whose `onComplete` you rely on.
- **Easing functions** (`cubicBezier`, `steps`, `linear`, `irregular`, `eases.*`): pure functions with no state or cleanup. `irregular()` is random on each call, so build it once if several animations must share a curve.
- **`engine` / `engine.defaults`**: a single global instance. Nothing to tear down per hook, but any default you change stays for the whole page session (see Gotcha 15). The engine's own frame loop stops by itself when nothing is running.
