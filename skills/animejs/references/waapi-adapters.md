# Anime.js v4: `waapi.animate()` and adapters (Three.js + custom)

Reference for the two ways Anime.js 4.5.0 reaches beyond its own requestAnimationFrame engine. `waapi.animate()` hands DOM animations to the browser's Web Animations API (small, can run on the compositor, DOM-only, fewer controls). Adapters teach the JS engine (`animate()`, `createTimeline()`, `utils.set()`, `utils.get()`) to drive objects that have no plain numeric properties, with a built-in Three.js adapter and a public API for writing your own. Facts below were checked against `dist/modules/**/*.d.ts` and the shipped JS of 4.5.0; behaviour marked "verified" was exercised in Chrome 152 or Node with three r180.

## Import map

| Import | Gives | Notes |
| --- | --- | --- |
| `import { waapi } from 'animejs'` | `waapi.animate`, `waapi.convertEase` | Also exports the `WAAPIAnimation` class and its types |
| `import { waapi } from 'animejs/waapi'` | same, standalone subpath | Smallest bundle (docs: about 3 KB gzip vs 10 KB for the JS engine) |
| `import 'animejs/adapters/three'` | registers the Three.js adapter as a side effect | `package.json` `sideEffects` covers `dist/modules/adapters/**`, so esbuild keeps it |
| `import { getInstances, commitChanges, threeAdapter } from 'animejs/adapters/three'` | instanced-mesh helpers; importing them also registers the adapter | `threeAdapter` (the registered `Adapter`) is exported in types but not documented |
| `import { registerAdapter } from 'animejs/adapters'` | custom adapter API | Since 4.5.0 |

---

## Web Animation API `web-animation-api`

`waapi.animate(targets: DOMTargetsParam, params: WAAPIAnimationParams): WAAPIAnimation` — Since 4.0.0.

- `targets`: a CSS selector string, `HTMLElement | SVGElement`, `NodeList`, or an array of those. DOM only; plain objects, canvas and WebGL targets need `animate()`. String selectors resolve inside the active `Scope` root.
- `params`: animatable CSS properties plus the playback settings, tween options and the single callback below.
- No match: logs a console warning, returns an animation with `targets.length === 0` and `duration === 0` whose `then()` never resolves (verified).

### When to use WAAPI `web-animation-api/when-to-use-waapi`

| Prefer `waapi.animate()` | Prefer `animate()` |
| --- | --- |
| Motion must stay smooth while the main thread is busy (CPU or network load) | More than ~500 targets |
| Every KB of JS matters on first load | JS objects, canvas, WebGL/WebGPU (and adapter targets) |
| Values the JS engine interpolates poorly: `transform` matrix strings, CSS color functions such as `color(display-p3 ...)` | SVG attributes, DOM attributes, CSS properties WAAPI cannot animate |
| | Complex timelines and keyframes |
| | More control methods and callbacks (see JS-only list) |

### Hardware-accelerated animations `web-animation-api/hardware-accelerated-animations`

| Compositor support | Properties |
| --- | --- |
| All major browsers | `opacity`, `transform`, `translate`, `scale`, `rotate` |
| Some browsers | `clip-path`, `filter` |

- Safari (desktop and iOS) drops off the compositor whenever the easing is a CSS `linear(...)` function. Anime.js turns every non-native ease into `linear(...)`: power eases (`'out(3)'`), named JS eases, spring objects and easing functions. **The default ease `'out(2)'` is one of them**, so a default `waapi.animate()` is main-thread in Safari. Pass a native CSS easing (`'ease-out'`, `'cubic-bezier(...)'`, `'steps(n)'`, `'linear'`) when compositor playback matters.
- Individual transform shorthands (`x`, `translateY`, `rotateX`, ...) route through registered CSS custom properties and can never be accelerated (see below). The native individual properties `translate`, `rotate`, `scale` can.

```ts
waapi.animate(list, {
  opacity: [0, 1],
  translate: ['0 12px', '0 0'],
  ease: 'cubic-bezier(.2, 0, 0, 1)',
  duration: 400,
});
```

### Improvements over native WAAPI `web-animation-api/improvements-to-the-web-animation-api`

Also: `autoplay: onScroll(...)` links a WAAPI animation to a ScrollObserver, and a `Scope` (with `mediaQueries`) owns and reverts WAAPI animations created inside it.

| Page (`.../improvements-to-the-web-animation-api/<page>`) | What Anime.js adds on top of `Element.animate()` |
| --- | --- |
| `sensible-defaults` | Default `duration` 1000 ms, `delay` 0, ease `'out(2)'`; the final value stays applied after completion (no manual `fill`/`finished` bookkeeping) |
| `multi-targets-animation` | Any `querySelectorAll` selector or element list in one call; `stagger()` works for `delay`, `duration` and values |
| `default-units` | Bare numbers get units on the properties in the table below |
| `function-based-values` | Values, `duration`, `delay` and `ease` accept `(target, index, targets) => value`, evaluated per target |
| `individual-css-transforms` | `x`, `rotateX`, `scaleY`, `skewX`, ... animate independently (needs `CSS.registerProperty`; without it nothing animates) |
| `individual-property-parameters` | A property value may be an object with its own `to`/`from`/`duration`/`delay`/`ease`/`composition` |
| `spring-and-custom-easings` | Anime.js ease names, `eases.*` functions, `spring()` objects and any `(t) => number` function |

Default units (applied to bare numbers):

| Unit | Properties |
| --- | --- |
| `'px'` | `x`, `y`, `z`, `translateX`, `translateY`, `translateZ` (any name starting `translate`), `perspective`, `width`, `height`, `margin`, `padding`, `top`, `right`, `bottom`, `left`, `borderWidth`, `fontSize`, `borderRadius` |
| `'deg'` | any name starting `rotate` or `skew` (`rotate`, `rotateX/Y/Z`, `skew`, `skewX/Y`) |
| none | everything else (number becomes a unitless string) |

Individual CSS transforms:

| Name | Shorthand | Default value | Default unit |
| --- | --- | --- | --- |
| translateX / translateY / translateZ | x / y / z | `'0px'` | `'px'` |
| rotate, rotateX, rotateY, rotateZ | — | `'0deg'` | `'deg'` |
| scale, scaleX, scaleY, scaleZ | — | `'1'` | — |
| skew, skewX, skewY | — | `'0deg'` | `'deg'` |

How it really works (from source, verified): on the first `waapi.animate()` call on a page, Anime.js calls `CSS.registerProperty` for `--translateX`, `--rotate`, `--scale`, `--skew`, `--perspective`, etc. (`inherits: false`), a global and permanent registration. When a call contains **at least one axis transform** (`x`, `y`, `z` or any transform name ending in X/Y/Z), every transform key in that call animates its `--name` custom property and the element's inline `transform` is overwritten with `translateX(var(--translateX)) rotate(var(--rotate)) ...`. Without an axis transform, `rotate` and `scale` go to the native CSS `rotate`/`scale` properties, and `skew` alone does nothing (there is no CSS `skew` property; the keyframes come out empty).

Individual property parameters (`WAAPITweenOptions`):

| Key | Type | Default | Meaning |
| --- | --- | --- | --- |
| `to` | `WAAPIKeyframeValue` | current computed value | End value, or an array of keyframe values |
| `from` | `WAAPIKeyframeValue` | — | Start value; also written inline immediately |
| `duration` | `number \| WAAPIFunctionValue` | animation `duration` | Per-property duration |
| `delay` | `number \| WAAPIFunctionValue` | animation `delay` | Per-property delay |
| `ease` | `WAAPIEasingParam` | animation `ease` | Per-property ease |
| `composition` | `CompositeOperation` | animation `composition` | Types only; native `'replace' \| 'add' \| 'accumulate'` |

```ts
waapi.animate('.card', {
  opacity: { from: 0, to: 1, duration: 300 },
  y: { from: 24, to: 0, ease: 'out(3)' },
  delay: stagger(40),
  duration: 600,
});
```

Easing (`spring-and-custom-easings`): built-ins are usable as strings or via `eases` (`import { eases } from 'animejs'`); `spring` is a separate named import. Default `'out(2)'`.

| String form | Function | Parameters (defaults) |
| --- | --- | --- |
| `'linear'`, `'linear(0, .5 75%, 1)'` | `linear()` | coordinates |
| `'steps'`, `'steps(10)'` | `steps()` | steps = `10` |
| `'cubicBezier'`, `'cubicBezier(.5,0,.5,1)'` | `cubicBezier()` | x1 `.5`, y1 `0`, x2 `.5`, y2 `1` |
| `'in'`, `'in(1.675)'` | `in()` | power = `1.675` |
| `'out'`, `'out(1.675)'` | `out()` | power = `1.675` |
| `'inOut'`, `'inOut(1.675)'` | `inOut()` | power = `1.675` |

Ease resolution (source): strings starting with `linear`, `cubic-`, `steps` or `ease` pass to the browser unchanged; other Anime.js names are sampled into `linear(...)`; an unknown string silently becomes `'linear'` (verified). When `ease` is a `Spring`, the animation's `duration` is replaced by the spring's `settlingDuration`.

### Parameters and playback settings

`WAAPIAnimationParams = Record<string, WAAPIKeyframeValue | WAAPITweenOptions | ...> & WAAPIAnimationOptions`. Value types: `WAAPITweenValue = string | number | string[] | number[]`; `WAAPIFunctionValue = (target: DOMTarget, index: number, targets: DOMTargetsArray) => WAAPITweenValue | WAAPIEasingParam`.

| Setting | Type | Default | Meaning |
| --- | --- | --- | --- |
| `duration` | `number \| WAAPIFunctionValue` | `1000` | Per-iteration duration in ms |
| `delay` | `number \| WAAPIFunctionValue` | `0` | Start delay in ms |
| `ease` | `WAAPIEasingParam \| WAAPIFunctionValue` | `'out(2)'` | Any Anime.js ease, native CSS easing string, `Spring` or function |
| `loop` | `number \| boolean` | `0` | Repeat count; `true`/`Infinity` repeats forever |
| `alternate` | `boolean` | `false` | Flip direction on each repeat |
| `reversed` | `boolean` | `false` | Start playing backwards |
| `autoplay` | `boolean \| ScrollObserver` | `true` | `false` starts paused; `onScroll()` links to scroll |
| `playbackRate` | `number` | `1` | Initial speed multiplier (becomes `speed`) |
| `composition` | `CompositeOperation` | `'replace'` | Native composite op; in types, not in the WAAPI docs pages |
| `persist` | `boolean` | `false` | Since 4.2.0. Keep native animations alive after completion instead of committing styles and cancelling. Forced `true` when linked to `onScroll()`. Global: `engine.defaults.persist = true` |
| `onComplete` | `Callback<WAAPIAnimation>` | no-op | Only callback WAAPI supports |

Types-vs-docs: `WAAPIAnimationOptions` declares `Reversed?` and `Alternate?` (capitalised) while docs and runtime use `reversed` / `alternate`. Lowercase still type-checks through the `Record<string, ... | boolean>` index signature; follow the runtime.

JS-only (docs "JS" badge; not available to `waapi.animate()`): JavaScript object targets, CSS variables as animated properties, JS object properties, HTML attributes, SVG attributes, relative values (`'+=10'`), the JS `composition` modes (`'none'`/`'blend'`), `modifier`, tween-parameter keyframes, duration-based keyframes, percentage-based keyframes, `loopDelay`, `frameRate`, `playbackEase`, callbacks `onBegin`, `onBeforeUpdate`, `onUpdate`, `onRender`, `onLoop`, `onPause`, methods `reset()`, `stretch()`, `refresh()`, properties `id`, `iterationCurrentTime`, `deltaTime`, `iterationProgress`, `currentIteration`, `fps`, `began`, `backwards`. WAAPI-only: `persist`, CSS `color()` function values (`animation/tween-value-types/color-function-value`).

### API differences with native WAAPI `web-animation-api/api-differences-with-native-waapi`

| Native | Anime.js | Mapping |
| --- | --- | --- |
| `iterations` (`.../iterations`) | `loop` | `iterations: 1` = `loop: 0`; `3` = `2`; `Infinity` = `Infinity`/`true`. Accepts `Number` 0..Infinity or `Boolean` |
| `direction` (`.../direction`) | `reversed` + `alternate` | `'normal'` = neither; `'reverse'` = `reversed`; `'alternate'` = `alternate`; `'alternate-reverse'` = both. Docs call the first value `'forward'`; the runtime emits `'normal'` |
| `easing` (`.../easing`) | `ease` | Accepts Anime.js ease names/functions plus native CSS easing strings; default `'out(2)'` not `'linear'` |
| `finished` (`.../finished`) | `then(callback?)` | Returns a `Promise` that settles on completion; callback gets the animation |
| per-element `.animate()` calls | one call for many targets | Each target/property becomes its own native `Animation` in `animation.animations` |
| `fill` | always `'both'` internally | Final state kept by committing inline styles on finish (or by `persist`) |

`then()` details (verified): the callback receives the animation with `then` temporarily set to `null`; the promise resolves to `undefined`, so `await anim.then()` gives nothing back. Types: the callback parameter is `this & { then: null }`, which TypeScript collapses to `never`; use the captured variable:

```ts
const fade = waapi.animate(el, { opacity: 0, duration: 200 });
await fade.then();
fade.revert();
```

### `WAAPIAnimation` instance

| Property | Type | Meaning |
| --- | --- | --- |
| `targets` | `DOMTarget[]` | Resolved elements |
| `animations` | `Animation[]` | Native animations, one per target and property; emptied by `cancel()` |
| `controlAnimation` | `Animation` | The longest native animation, used for `currentTime` |
| `duration` | `number` | Longest `delay + duration * iterations`; `Infinity` when looping forever |
| `currentTime` | `number` (get/set) | Time in ms; setting seeks every native animation |
| `progress` | `number` (get/set) | `currentTime / duration`, 0..1 |
| `speed` | `number` (get/set) | Playback rate of every native animation |
| `paused`, `completed`, `reversed` | `boolean` | State flags (`reversed` exists on the class even though docs mark it JS-only) |
| `persist` | `boolean` | See settings |
| `autoplay` | `boolean \| ScrollObserver` | As passed |
| `onComplete` | `Callback<this>` | Assignable after creation |
| `muteCallbacks` | `boolean` | Internal: suppresses `onComplete` during seeks and cancel |

| Method | Returns | Effect |
| --- | --- | --- |
| `play()` | `this` | Play forwards (un-reverses if needed) |
| `reverse()` | `this` | Play backwards |
| `pause()` / `resume()` | `this` | Pause / continue in the current direction |
| `alternate()` | `this` | Flip direction without changing paused state |
| `restart()` | `this` | Seek to 0 silently and resume |
| `seek(time, muteCallbacks = false)` | `this` | Jump to `time` ms |
| `complete()` | `this` | Seek to the end (fires `onComplete` unless muted) |
| `cancel()` | `this` | Commit current values inline, cancel natives, release them; no `onComplete`, `then()` stays pending |
| `revert()` | `this` | `cancel()` then restore the inline styles captured at creation |
| `commitStyles()` | `this` | Types only: write current animated values to inline style |
| `forEach(cb \| methodName)` | `this` | Types only: run a callback, or call a named method, on every native `Animation` |
| `then(callback?)` | `Promise` | See above |

Timeline and scroll integration: `createTimeline().sync(waapiAnim, position?)` drives a WAAPI animation from a timeline (`timeline/timeline-methods/sync`); `autoplay: onScroll(...)` links it to scroll.

```ts
waapi.animate(el, { scale: [0.8, 1], autoplay: onScroll({ sync: true }) });
const fade = waapi.animate(el, { opacity: [0, 1], autoplay: false });
createTimeline().sync(fade, 0);
```

### `waapi.convertEase()` `web-animation-api/waapi-convertease`

`waapi.convertEase(fn: EasingFunction, samples = 100): string` — Since 4.0.0. Samples `fn` at `samples + 1` evenly spaced points (rounded to 4 decimals) and returns a CSS `linear(...)` string for native `Element.animate()` or CSS. The docs show only `fn`; the `samples` argument is in the types.

A spring's `ease` is normalised to `spring.settlingDuration`, not `spring.duration` (the perceived duration, much shorter: 628 vs 1700 ms for `stiffness: 150`). The docs demo pairs it with `duration`; pair it with `settlingDuration`, as `waapi.animate()` does internally:

```ts
const s = spring({ stiffness: 150 });
el.animate(
  { translate: ['0px', '200px'] },
  { easing: waapi.convertEase(s.ease), duration: s.settlingDuration, fill: 'forwards' },
);
```

---

## Adapters `adapters`

Since 4.5.0. An adapter maps property names to a getter and a setter on some object class. Once registered, `animate()`, `createTimeline().add()`, `utils.set()` and `utils.get()` accept those objects like any target. Adapters cover JS-engine targets only; `waapi.animate()` never uses them. The registry is a module-level list inside the `animejs` copy that imported it: global to the page, with no unregister call.

### Custom adapters

`registerAdapter(detect?: (t: any) => boolean): Adapter`. The optional `detect` is a gate on the whole adapter: when it returns false for a target, none of the adapter's target adapters or resolvers are asked. The docs show `registerAdapter()` with no argument; `detect` is in the types and source.

| `Adapter` member | Signature | Meaning |
| --- | --- | --- |
| `registerTargetAdapter` | `(detect: (t) => boolean) => TargetAdapter` | Declare a class of targets with a fixed set of property names |
| `registerPropertyResolver` | `(resolver: (target, name) => TargetAdapterEntry \| null) => void` | Match names at tween creation (prefixes, axis suffixes, dynamic names); return `null` to pass |
| `detect`, `targetAdapters`, `propertyResolvers` | fields | Internal state |

`TargetAdapter.registerProperty(name, getter, setter, gate?)`:

| Arg | Type | Meaning |
| --- | --- | --- |
| `name` | `string` | Property name used in animation params |
| `getter` | `(t: any) => any` | Current value (number or a string such as a CSS color); used for implicit `from`, `utils.get`, and revert |
| `setter` | `(target: any, value: number, tween: any) => void` | Receives the interpolated number. For color and complex (multi-number string) tweens `value` is `undefined`; read `tween._numbers` (colors: `[r, g, b, a]` with rgb 0–255) |
| `gate` (opt) | `(t: any) => boolean` | Restrict this name to a subset of the detected targets |

`TargetAdapterEntry = { get, set, gate? }` is what resolvers return.

Resolution order for each target and property (source, verified):

1. For each adapter in registration order (skipping those whose `detect` fails), check its target adapters. **The first target adapter whose `detect` matches owns the target**: if it lists the name (and the gate passes), that entry wins; if not, no other adapter's target adapters are checked.
2. Otherwise, for each adapter in order, ask its property resolvers; the first non-`null` result wins.
3. Otherwise the engine writes `target[name] = value` directly.

The entry is resolved once when the tween is created, so an adapter registered later does not affect animations that already exist.

```ts
const lib = registerAdapter((t) => t instanceof Gauge);
const gauge = lib.registerTargetAdapter((t) => t instanceof Gauge);
gauge.registerProperty('level', (t: Gauge) => t.level, (t: Gauge, v) => t.setLevel(v));
gauge.registerProperty(
  'tint',
  (t: Gauge) => `rgb(${t.tint.r}, ${t.tint.g}, ${t.tint.b})`,
  (t: Gauge, _v, tween) => {
    const [r, g, b] = tween._numbers as number[];
    t.tint = { r, g, b };
  },
);
lib.registerPropertyResolver((t, name) =>
  t instanceof Gauge && name.startsWith('dial_')
    ? { get: () => 0, set: (target: Gauge, v: number) => target.setLevel(v) }
    : null,
);
animate(new Gauge(), { level: 100, tint: '#0f0' });
```

### Three.js adapter `adapters/threejs-adapter`

Since 4.5.0. Load with `import 'animejs/adapters/three'`. `three` (and `@types/three`) are optional peer dependencies, `>=0.150.0`. The adapter imports `three` itself, so the bundle must resolve one copy of `three` shared with your scene code.

It flattens `mesh.position`, `mesh.rotation`, `mesh.material` and uniform values onto flat names, converts angles to degrees, and parses any Anime.js color value (hex, `rgb()`, `hsl()`, `var(--x)`) into `THREE.Color` (written in sRGB via `setRGB(..., SRGBColorSpace)`).

Supported targets: `Object3D` and subclasses (`Mesh`, `Group`, lights, cameras, `Sprite`, `Points`, `Scene`, `Audio`, ...), `Material`, `Texture`, `Fog` / `FogExp2`, TSL `UniformNode`, bare `Color` and `Vector2/3/4`, and instance proxies from `getInstances()`.

Automatic detection for names without an explicit mapping:

| Field on the target | Name to animate |
| --- | --- |
| Scalar or boolean | the field name (engine writes it directly) |
| `Color` | the field name; accepts any color value |
| `Vector2/3/4` | field name + `X`/`Y`/`Z`/`W` (e.g. `normalScaleX`, `offsetY`, `centerX`) |
| Numeric field named `rotation` or `angle` | the field name, in degrees (e.g. `SpotLight.angle`, `Texture.rotation`) |
| `Euler` field named `rotation`/`angle` on a non-`Object3D` | `rotationX/Y/Z`, in degrees |

```ts
mesh.material.transparent = true;
animate(mesh, { x: 2, rotateY: 180, opacity: 0.5, color: '#ff8800', duration: 800 });
utils.set(scene, { background: 'var(--surface)' });
```

CSS variables on non-DOM targets resolve against `document.documentElement`, and the value is read when the tween is built: a later theme switch does not change a running animation.

### Object properties `adapters/threejs-adapter/threejs-object-property-adapter`

`Object3D` (every subclass):

| Name | Maps to | Unit |
| --- | --- | --- |
| `x` / `y` / `z` | `position.x/y/z` | — |
| `rotateX` / `rotateY` / `rotateZ` | `rotation.x/y/z` | degrees |
| `scaleX` / `scaleY` / `scaleZ` | `scale.x/y/z` | — |
| `scale` | all three scale axes | — |
| `skewX` / `skewY` / `skewZ` | shear (see transforms) | degrees |
| `transformOriginX/Y/Z`, `transformOrigin` | pivot shift; `'x y z'` string | geometry units |
| `visible` | `visible` (types/source; not in docs table) | boolean |

`Mesh` material shortcuts:

| Name | Maps to | Notes |
| --- | --- | --- |
| `opacity` | `material.opacity`; every entry of an array material | Sets `visible = false` at 0. Needs `material.transparent = true` to show. Not on lights. Objects without a material store it privately |
| `color` | `material.color` (on lights: `light.color`) | Any color value |

Other built-in mappings:

| Target | Name | Maps to | Notes |
| --- | --- | --- | --- |
| Lights | `color` | `color` | All lights |
| `HemisphereLight` | `groundColor` | `groundColor` | |
| Lights | `intensity`, `distance`, `decay`, ... | direct field | via fallthrough; `SpotLight.angle` in degrees |
| `PerspectiveCamera` | `fov` (deg), `aspect`, `focalLength` (mm, via `setFocalLength()`), `near`, `far`, `zoom` | fields | Each write calls `updateProjectionMatrix()` |
| `OrthographicCamera` | `left`, `right`, `top`, `bottom`, `near`, `far`, `zoom` | fields | Each write calls `updateProjectionMatrix()` |
| `Scene` | `background` | `background` | Creates a `Color` on first write if the background is not one |
| `Audio`, `PositionalAudio` | `volume` | `setVolume()` | |
| `PositionalAudio` | `refDistance`, `rolloffFactor`, `maxDistance` | `setRefDistance()`, `setRolloffFactor()`, `setMaxDistance()` | |
| `Fog`, `FogExp2` | `color` | `color` | `near`, `far`, `density` via direct access |
| `Texture` | `offsetX/Y`, `repeatX/Y`, `centerX/Y` | `offset`, `repeat`, `center` axes | |
| `Texture` | `rotation` | `rotation` | degrees; rotates around `center` |
| `UniformNode` | `color` | `value` | `Color`-valued nodes |
| `UniformNode` | `x`, `y` / `z` / `w` | `value.x/y/z/w` | x,y: Vector2+; z: Vector3+; w: Vector4 |
| `UniformNode` | `value` | `value` | Scalars and booleans (direct write) |

### Extended transforms `adapters/threejs-adapter/threejs-transforms-adapter`

- Position, rotation and scale per axis as above; rotations assume Euler order `'XYZ'`. With another `rotation.order` the names no longer mean what they say; use a `Quaternion` outside the adapter.
- `skewX`: shear of y by x, `tan(skewX)`. `skewY`: shear of x by y. `skewZ`: shear of z by x. Applied after position/rotation/scale, skipped when 0.
- `transformOrigin*` moves the pivot used by rotation and skew, like the CSS property, in the geometry's units. `transformOrigin` takes a 3-token `'x y z'` string (arrays of two strings animate between origins).
- Implementation: the first skew/origin write replaces that object's `updateMatrix` with a wrapper that applies the shear after the normal compose. The wrapper stays for the object's lifetime.
- Visibility toggle: writing `opacity`, `scale` or any scale axis to 0 through the adapter sets `visible = false`; a non-zero value sets it back to `true`. Direct writes (`mesh.scale.x = 0`) do not toggle it.

### Materials and uniforms `adapters/threejs-adapter/materials-and-uniforms`

| Source | Naming | Example |
| --- | --- | --- |
| Scalar/boolean material field | field name | `metalness`, `roughness`, `opacity`, `wireframe` |
| `Color` material field | field name | `color`, `emissive`, `specular`, `sheenColor` |
| `Vector` material field | name + axis | `normalScaleX`, `clearcoatNormalScaleY` |
| `ShaderMaterial` uniform (number or `Color`) | uniform name | `uTime`, `uTint` |
| `ShaderMaterial` uniform (`Vector2/3/4`) | uniform name + axis | `uOffsetY`, `resolutionX` |
| TSL slot holding `uniform(...)` (`material.colorNode = uniform(new Color())`) | slot name / slot name + axis | `colorNode`, `offsetNodeY` |
| Bare `UniformNode` | `value`, `color`, `x`–`w` | `animate(uniform(0), { value: 1 })` |

Mesh material mapping: on a `Mesh`, any of the material names above (fields, uniforms, TSL slots) resolves through `mesh.material`, so `animate(mesh, { metalness: 1, uTime: 1 })` equals targeting the material. A field that exists on the mesh itself always wins. With an array material the adapter reads the first material and writes all of them.

Not handled: uniforms whose value is a `Texture`, `Matrix3` or `Matrix4`, plus `UniformArrayNode` and `BufferNode`. Boolean `ShaderMaterial` uniforms are not handled either (verified: `utils.set(shader, { uFlag: false })` writes a stray `shader.uFlag = 0` and leaves the uniform alone). Animate texture transforms on the texture, or animate the numeric fields directly.

```ts
shader.uniforms.uTime = { value: 0 };
shader.uniforms.uTint = { value: new THREE.Color('#f00') };
shader.uniforms.uOffset = { value: new THREE.Vector2() };
animate(shader, { uTime: 1, uTint: '#0ff', uOffsetY: 0.5 });
const shared = uniform(0); // from 'three/tsl'
animate(shared, { value: 1 });
```

### Instanced and batched meshes `adapters/threejs-adapter/threejs-instanced-and-batched-meshes`

`getInstances(mesh: InstancedMesh | BatchedMesh): (Instance | null)[]` returns one proxy per slot. Pass the whole array, a slice or a single proxy to `animate()` / `utils.set()`. Deleted `BatchedMesh` slots are `null`. Proxies read their starting transform and color from the mesh when created.

The array is the same object on every call for a given mesh. It is resized in place **when `getInstances(mesh)` is called again**: after changing `mesh.count` or calling `addInstance()` / `deleteInstance()`, call it again before animating new slots (verified: the length does not change on its own).

`commitChanges(mesh): void` flushes queued matrix writes. Writes are batched and flushed from the mesh's `onBeforeRender`, which runs only when the mesh is actually rendered. Call it yourself before reading `mesh.instanceMatrix` (raycasting, bounds, export) between a tick and the next render.

| Proxy name | Maps to |
| --- | --- |
| `x` / `y` / `z` | slot position |
| `rotateX` / `rotateY` / `rotateZ` | slot rotation, degrees |
| `scaleX` / `scaleY` / `scaleZ` / `scale` | slot scale |
| `skewX` / `skewY` / `skewZ` | slot shear, degrees |
| `transformOriginX/Y/Z`, `transformOrigin` | slot pivot shift |
| `color` | `mesh.setColorAt(id, color)` (creates `instanceColor` on first use) |
| `visible` | `mesh.setVisibleAt(id, v)`, `BatchedMesh` only; no-op on `InstancedMesh` |
| `opacity` | the shared `mesh.material.opacity`, so every slot changes |

To hide one `InstancedMesh` slot, animate its `scale` to 0; to fade one slot you need a per-instance alpha in the shader driven by `color`. `getInstances()` replaces `mesh.onBeforeRender` with an accessor: assigning your own handler still works (it is chained), but reading it back returns the wrapper, so `mesh.onBeforeRender === fn` is false.

```ts
const instances = getInstances(mesh);
animate(instances, { y: 1, scale: [0, 1], color: '#0af', delay: stagger(10) });
commitChanges(mesh);
```

### Common gotchas page `adapters/threejs-adapter/threejs-adapter-common-gotchas`

Covered above and in the list below: rotation order, `transparent` for opacity fades, visibility toggle only through the adapter, shared materials, group fades, a single Three.js copy, unsupported uniform types, instance proxy limits.

---

## Gotchas

1. The default WAAPI ease `'out(2)'` is sent to the browser as `linear(...)`, which keeps Safari off the compositor. Use native easing strings for animations that must survive main-thread load.
2. `{ rotate: 45 }` animates the native, accelerated CSS `rotate` property; `{ x: 10, rotate: 45 }` moves `rotate` into a `var(--rotate)` inside an inline `transform` that cannot be accelerated. Adding one axis key changes how every transform key in the call behaves.
3. `skew` in `waapi.animate()` does nothing unless the same call also has an axis transform (`x`, `skewX`, `rotateY`, ...).
4. Axis transforms overwrite the element's inline `transform` for the whole element and cache every transform name ever animated on it; `revert()` restores the whole `transform` value, which also wipes transforms from other WAAPI animations still running on that element.
5. A new `waapi.animate()` on the same element and property cancels the older native animation (after committing its current value). If that leaves the older `WAAPIAnimation` with nothing running, its `onComplete` fires and its `then()` resolves early (verified). Do not treat `onComplete` as "played to the end".
6. `cancel()` never resolves `then()` or calls `onComplete`, and a call with zero matched targets never resolves either. Do not `await` a WAAPI animation in teardown code without a guard.
7. `WAAPIAnimation.revert()` leaves a linked `onScroll()` observer alive (the JS `animate()` version reverts it). Revert the observer yourself or use a `Scope`.
8. `then()` resolves to `undefined`, and in TypeScript its callback argument is `never`; keep a reference to the animation.
9. After a normal (non-`persist`) completion, the native animations are cancelled and the final values sit in the inline `style` attribute. Calling `reverse()`, `seek()` and similar methods on a finished animation acts on cancelled native animations and is unreliable (the docs warn about this); set `persist: true` to keep controlling a finished animation.
10. `persist: true` animations never complete: no `onComplete`, `then()` stays pending, and native animations keep running (filling) until `cancel()`/`revert()`.
11. An unknown ease string silently becomes `'linear'`; no warning.
12. `CSS.registerProperty` runs once per page for `--translateX`, `--rotate`, `--scale`, `--skew`, `--perspective`, etc. Page CSS that uses custom properties with those exact names gets their typed syntax (`<angle>`, `<number>`, `<length-percentage>`).
13. `waapi.convertEase(spring.ease)` must be paired with `spring.settlingDuration`, not `spring.duration`.
14. Three.js opacity fades need `material.transparent = true`, or the mesh stays fully opaque.
15. Material writes are shared: animating `metalness` or `color` on one mesh changes every mesh using that material. Clone the material per mesh to scope it.
16. `Group` has no material, so intermediate `opacity`/`color` values do nothing to children, but `opacity: 0` still sets `group.visible = false` and hides the whole subtree at once (verified). To fade a subtree, target its meshes.
17. Two copies of `three` in the bundle break the adapter's `instanceof Object3D` checks silently; targets from the other copy get plain property writes.
18. The first matching target adapter owns a target. A custom adapter registered after the Three.js adapter cannot add names to `Object3D` through `registerTargetAdapter`; it has to use `registerPropertyResolver` (and only for names the Three.js adapter does not already map).
19. Reverting an animation of `scene.background` from `null` or a texture leaves a black `Color`, not the original value (verified).
20. Instanced proxies flush only in `onBeforeRender`; a mesh that is not rendered (culled, removed, render loop stopped) keeps a stale `instanceMatrix` until `commitChanges(mesh)`.
21. Types defect in 4.5.0: `adapters/three/adapter.d.ts` references an undeclared `TargetAdapterEntry`, and `engine.d.ts` / `text/split.d.ts` use the `NodeJS` namespace. `tsc` with `skipLibCheck: false` fails on these even in correct code; use `skipLibCheck: true` (or install `@types/node` for the `NodeJS` part).

## Lifecycle and cleanup

These objects will live inside Phoenix LiveView hooks, where the server can patch or remove the DOM at any time. Create them in `mounted()`, keep a handle (or a `Scope`), and tear them down in `destroyed()`. `createScope({ root: this.el })` registers every `waapi.animate()` and `animate()` created inside `.add()` and scopes string selectors to the hook element; `scope.revert()` reverts them all.

```ts
const scope = createScope({ root }).add(() => {
  waapi.animate('.item', { opacity: [0, 1], delay: stagger(30) });
});
return () => scope.revert();
```

- **`WAAPIAnimation` (running)**: `pause()` freezes it in place. `cancel()` commits the current values to inline style, cancels the natives and leaves those inline styles. `revert()` does the same, then restores the inline styles captured at creation (removing the `style` attribute if it ends up empty; verified). No event listeners or observers. Leftovers after `revert()` when axis transforms were used: the `--translateX`/`--rotate`/... custom properties stay inline (harmless once `transform` is restored, verified), and the page-wide `CSS.registerProperty` registrations cannot be undone.
- **`WAAPIAnimation` (completed, `persist: false`)**: nothing is running; the final values remain as inline styles. `revert()` still removes them (verified). `cancel()` has no visible effect.
- **`WAAPIAnimation` with `persist: true` or `onScroll()`**: native animations stay attached to the element until `cancel()`/`revert()`. Unlike `JSAnimation.revert()`, `WAAPIAnimation.revert()` does **not** revert a linked `ScrollObserver` (source), which keeps its scroll listeners and observers; call `(anim.autoplay as ScrollObserver).revert()` yourself, or create both inside a `Scope` (the observer registers with the scope too) and call `scope.revert()`.
- **Server patches**: LiveView DOM patching resets attributes to the server-rendered markup, which can erase the inline styles a WAAPI animation committed (the "keeps final value" behaviour). Keep animated state off elements the server re-renders, or protect the element or its `style` attribute as described in [liveview-islands.md](liveview-islands.md#what-a-liveview-patch-does-to-animejss-dom-writes). If the server removes an element mid-animation, its native animations stop with it, but the `WAAPIAnimation` still holds the element and any linked observer; call `revert()`/`scope.revert()` in `destroyed()` anyway.
- **`animate()` on Three.js or custom-adapter targets**: returns a normal `JSAnimation`. `pause()` freezes; `cancel()` stops and leaves the current values on the objects; `revert()` stops and writes the start values back through the adapter setters (verified for position incl. 0, rotation, scale with the visibility flag, opacity, colors). No DOM, listeners or observers are involved. Permanent side effects that `revert()` does not undo: the `updateMatrix` wrapper on objects that received skew/origin writes, the `onBeforeRender` accessor installed by `getInstances()` (kept per mesh in a `WeakMap`, collected with the mesh), a `Color` created for `scene.background`, and adapter registrations themselves (global, no unregister).
- **Render loop and GPU resources**: the adapter only mutates objects; whatever renders the scene (`createTimer({ onUpdate })`, `renderer.setAnimationLoop`) must be stopped separately (`timer.revert()`, `setAnimationLoop(null)`), and Three.js geometries, materials, textures and the renderer need their own `dispose()` calls plus removal of `renderer.domElement` in `destroyed()`.
