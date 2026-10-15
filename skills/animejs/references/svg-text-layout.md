# Anime.js v4: SVG, Text and Layout

Reference for the three "helper" families of Anime.js 4.5.0: SVG utilities (`morphTo`, `createDrawable`, `createMotionPath`), text utilities (`splitText` / `TextSplitter`, plus `scrambleText`), and the auto-layout engine (`createLayout` / `AutoLayout`). Use it when writing or reviewing code that draws strokes, morphs shapes, moves things along a path, splits text into animatable spans, scrambles text, or animates between two DOM layouts (reorder, show/hide, reparent, grid/flex switches). Everything here was checked against the 4.5.0 `.d.ts` files and the shipped ESM source; where the docs and the types differ, the types win and the difference is noted. Fetch any live page with `uv run scripts/animejs_docs.py <path>`.

Imports (all three families are in the main entry and have subpath modules):

| Family | Named imports from `'animejs'` | Namespace object | Subpath |
| --- | --- | --- | --- |
| SVG | `morphTo`, `createDrawable`, `createMotionPath` | `svg.*` | `'animejs/svg'` |
| Text | `splitText`, `scrambleText`, class `TextSplitter` | `text.*` | `'animejs/text'` (since 4.2.0 for `splitText`) |
| Layout | `createLayout`, class `AutoLayout` | none | `'animejs/layout'` |

`text.split()` still exists but is deprecated (logs a warning); use `splitText()`.

Types note: the 4.5.0 declarations reference `NodeJS.Timeout` (`TextSplitter.resizeTimeout`) and `NodeJS.Immediate` (engine). A browser-only TS project with `skipLibCheck: false` and no `@types/node` fails with "Cannot find namespace 'NodeJS'". Either keep `skipLibCheck: true` or add a one-line ambient shim: `declare namespace NodeJS { type Timeout = ReturnType<typeof setTimeout>; type Immediate = number }`.

---

## SVG `svg`

Since 4.0.0. All three return values you feed into `animate()` (or a timeline `.add()`); none of them owns an animation.

### morphTo `svg/morphto`

`morphTo(path2: TargetsParam, precision?: number): FunctionValue`

| Param | Type | Default | Meaning |
| --- | --- | --- | --- |
| `path2` | selector / `SVGPathElement` / `SVGPolylineElement` / `SVGPolygonElement` | required | Shape to morph into. Only the first match is used. |
| `precision` | `number` 0..1 | `.33` | Resampling density: point count = `ceil(totalLength * precision)` of the longer shape. `0` disables resampling and interpolates the raw `d` / `points` strings as-is. |

- Use it as the value of `d` (on `<path>`) or `points` (on `<polygon>`/`<polyline>`).
- Docs say it returns "an Array of start and end strings"; the types say `FunctionValue`. Both are true: it returns a function-based value which, per target, yields `[fromString, toString]`.
- Throws at animation-creation time if either element is not `path`, `polygon` or `polyline`, or if `path2` resolves to nothing.
- With `precision > 0` both shapes are sampled with `getPointAtLength`, so a path can morph into a polygon (output format follows the animated element). With `precision: 0` the two strings must already have compatible structure and the same element type.
- Chained morphs (keyframes or successive tweens) start from the previous tween's end value, not the attribute.

```ts
export function morphShape() {
  return animate(shapeA, { d: morphTo(shapeB, 0.5), duration: 600 });
}
```

### createDrawable `svg/createdrawable`

`createDrawable(selector: TargetsParam, start?: number, end?: number): Array<DrawableSVGGeometry>`

| Param | Type | Default | Meaning |
| --- | --- | --- | --- |
| `selector` | selector / SVG geometry element(s) | required | Docs list `line`, `path`, `polyline`, `rect` (and repeat `SVGPolylineElement`, likely meaning polygon); the code works on any `SVGGeometryElement` (circle, ellipse, polygon too). |
| `start` | `number` 0..1 | `0` | Undocumented. Initial visible start. |
| `end` | `number` 0..1 | `0` | Undocumented. Initial visible end. |

Returns an array of `Proxy` objects wrapping each element, typed `SVGGeometryElement & { draw: `${number} ${number}` }`. Animate the proxies, not the raw elements.

`draw` is a string `"start end"`, both in 0..1 of the stroke length: `'0 1'` full line, `'0 .5'` first half, `'.25 .75'` middle half, `'1 1'` nothing. Keyframe arrays like `['0 0', '0 1', '1 1']` draw on then erase.

What it does to the DOM:
- Sets the `pathLength="1000"` attribute and writes `stroke-dasharray` / `stroke-dashoffset` attributes on every draw update.
- If the stroke has a non-`butt` linecap, it switches inline `stroke-linecap` to `butt` whenever start equals end (so round caps don't leave a dot) and back otherwise.
- On creation, if `pathLength` is not already `1000`, it immediately applies `draw = "start end"`; with the defaults that is `'0 0'`, so **the line disappears as soon as you call `createDrawable()`**, before any animation runs. Pass `0, 1` to keep it visible.
- Elements with `vector-effect: non-scaling-stroke` recompute their scale from `getCTM()` on every frame, which is slow.

```ts
export function drawLine() {
  const [line] = createDrawable(outline); // line starts hidden: draw = '0 0'
  return animate(line, { draw: ['0 0', '0 1'], duration: 800, ease: 'inOutQuad' });
}

export function drawableFullyVisible() {
  return createDrawable('.stroke', 0, 1); // undocumented start/end args
}
```

### createMotionPath `svg/createmotionpath`

`createMotionPath(path: TargetsParam, offset?: number): { translateX: FunctionValue; translateY: FunctionValue; rotate: FunctionValue }`

| Param | Type | Default | Meaning |
| --- | --- | --- | --- |
| `path` | selector / `SVGPathElement` (any `SVGGeometryElement` works) | required | Path to follow. |
| `offset` | `number` 0..1 | `0` | Start position along the path as a fraction of its length. |

Returned object (spread it into `animate()` params):

| Key | Meaning |
| --- | --- |
| `translateX` | x of the point on the path at the current progress |
| `translateY` | y of the point on the path at the current progress |
| `rotate` | tangent angle in degrees at that point |

- Each value is a function-based tween `{ from: 0, to: totalLength, modifier }`, so `ease`, `duration`, `loop` etc. on the animation apply to travel along the path. Use `ease: 'linear'` for constant speed.
- `offset: 0` clamps at the path ends; any non-zero offset wraps around (useful for closed loops).
- When the animated target is an HTML element (not inside the SVG), coordinates are mapped through the path's `getCTM()`, so the element follows the path's on-screen position. That transform is read once when the tween is created; if the SVG is resized later, recreate the animation.
- If `path` does not resolve to an SVG element it logs a warning and returns `undefined` (types claim an object; spreading `undefined` silently adds nothing).

```ts
export function followPath() {
  return animate(car, { ...createMotionPath(track), ease: 'linear', duration: 4000, loop: true });
}
```

---

## Text `text`

### splitText `text/splittext`

Since 4.1.0. `splitText(target, parameters?): TextSplitter` (equivalently `new TextSplitter(target, parameters)`).

| Param | Type (from `.d.ts`) | Meaning |
| --- | --- | --- |
| `target` | `Element \| NodeList \| string \| Array<Element>` | Element to split. **Only the first match is split**; `splitText('p')` with several paragraphs splits one. Loop yourself for many. |
| `parameters` | `TextSplitterParams` | Settings below. |

It wraps lines, words and/or characters in spans while keeping nested markup (links, `em`, etc.; when splitting by lines, nested inline elements are duplicated into each line they span). Word boundaries come from `Intl.Segmenter` (works for CJK, Thai, etc.), with a whitespace split as a fallback; characters use grapheme segmentation, so emoji and combined glyphs stay intact.

If called while an Anime.js `createScope()` is active, the splitter registers with that scope and `scope.revert()` reverts it.

#### TextSplitter settings `text/splittext/textsplitter-settings`

| Setting | Type | Default | Meaning |
| --- | --- | --- | --- |
| `lines` | `boolean \| SplitTemplateParams \| string \| (node) => string` | `false` | Split by rendered line. Line elements land in `split.lines`. |
| `words` | same | `true` | Split by word. Words land in `split.words`. On by default: pass `words: false` to skip. |
| `chars` | same | `false` | Split by grapheme. Characters land in `split.chars`. |
| `debug` | `boolean` | `false` | Outlines wrappers: lines green, words red, chars blue (1px dotted). |
| `includeSpaces` | `boolean` | `false` | Keep the trailing space inside each word (and the last char of the word) as a non-breaking space instead of a separate text node, so spaces move with their word. |
| `accessible` | `boolean` | `true` | Inserts a visually hidden copy of the original HTML as the target's first child and puts `aria-hidden="true"` on every split element, so screen readers read the sentence once. |

`lines`/`words`/`chars` accept: `true` (default wrapper), a split-parameters object, an HTML template string, or (undocumented, in the types as `SplitFunctionValue`) a function `(node?: Node | HTMLElement) => string` returning a template per node.

Default wrappers and data attributes:

| Level | Element | Inline style | Attributes |
| --- | --- | --- | --- |
| line | `span` | `display: block` | `data-line` |
| word | `span` | `display: inline-block` | `data-line`, `data-word` |
| char | `span` | `display: inline-block` | `data-line`, `data-word`, `data-char` |

`data-line` is filled on words and chars even when you do not split by lines, which makes per-line function values easy (`$el => +$el.dataset.line % 2 ? ... : ...`). Indices (`data-word`, `data-char`, `{i}`) count across the whole target, not per line.

If only `lines` is on, words are split internally for measurement and then unwrapped; `split.words` ends up empty.

#### Split parameters `text/splittext/split-parameters`

Object form of `lines` / `words` / `chars`.

| Param | Type (from `.d.ts`) | Default | Meaning |
| --- | --- | --- | --- |
| `class` | `string \| false` | none | CSS class put on each split element (the one with the `data-*` attribute, i.e. the element in the array). Docs say `String \| null`, default `null`; types say `false \| string`. |
| `wrap` | `boolean \| 'hidden' \| 'clip' \| 'visible' \| 'scroll' \| 'auto'` | none | Adds an outer `span` with that `overflow` value around each split element (`true` means `'clip'`). The classic masked slide-up reveal. |
| `clone` | `boolean \| 'top' \| 'right' \| 'bottom' \| 'left' \| 'center'` | none | Inside each split element, renders the text twice: the original plus an absolutely positioned, `inert` duplicate offset by 100% in that direction (`true` means `'center'`, i.e. overlapping). The split element gets `position: relative`. Animate the split element by `-100%` to roll the copy into place; pair with `wrap` to mask it. |

On a Regent site, clip with the kit's `CLIPPED_WORD` / `CLIPPED_CHAR` templates (the
`.split-clip` class) instead of `wrap`: `wrap` writes a `style` attribute into the markup,
which a strict page security policy refuses.

#### HTML template `text/splittext/html-template`

A string used as the wrapper for every line/word/char.
- Must contain `{value}` at least once (otherwise a warning is logged and that item is dropped); every `{value}` is replaced by the content, so a template can render the character several times (3D faces, shadows).
- `{i}` is replaced by the item index.
- Display styles and `data-*` attributes are added for you. If no element in the template carries `data-line`/`data-word`/`data-char`, the attributes go on the template's outermost element, and that element is what lands in the array.

```ts
export function splitTemplate() {
  return splitText(heading, {
    words: false,
    chars: '<span class="c c-{i}">{value}</span>',
    includeSpaces: true,
  });
}
```

#### When the split happens, and re-splitting

- With `lines` on, the split waits for `document.fonts.ready` and always runs asynchronously (at least one microtask later), because line breaks depend on the final font. **Right after `splitText()` returns, `split.lines`, `split.words` and `split.chars` are still empty.** Without `lines`, words/chars are split synchronously.
- A `ResizeObserver` watches the target. After 150 ms without further resizes, if `offsetWidth` changed, it re-measures. With `lines` on, this rebuilds all line, word and char elements (new nodes), which kills animations that target the old nodes. Without `lines`, it only rewrites `data-line` values.
- To survive both the font wait and re-splits, create animations inside `addEffect()`.

#### TextSplitter methods `text/splittext/textsplitter-methods`

| Method | Returns | Meaning |
| --- | --- | --- |
| `addEffect(effect)` | `this` | Registers `effect(split)`, run after every (re)split. The effect may return an Animation / Timeline / Timer (it is reverted before the next split and recreated with its playback position kept) or a cleanup function (called before each new line calculation and on `revert()`). If the split is already done, runs at once; otherwise after the first split. Chainable. |
| `revert()` | `this` | Stops the resize observer and pending timer, runs every effect cleanup / reverts every effect animation, and resets `$target.innerHTML` to the HTML captured when `splitText()` was called. Removes the debug outlines and accessible copy with it. |
| `refresh()` | `void` (docs say `TextSplitter`; types say `void`, so don't chain) | Restores `html` into the target and splits again, then re-runs effects. Read these fields before calling it: `$target`, `html`, `debug`, `includeSpaces`, `accessible`, `lineTemplate`, `wordTemplate`, `charTemplate`. |

Effects re-run when: the first split completes after fonts load; the target's width changes while splitting by lines (even if the line breaks come out the same); `refresh()` is called.

```ts
export function splitWithEffect(): TextSplitter {
  const split = splitText(heading, { lines: { wrap: 'clip' }, words: true });
  split.addEffect(({ lines }: TextSplitter) =>
    animate(lines, { y: ['100%', '0%'], delay: stagger(80), ease: 'out(3)' }),
  );
  return split; // later: split.revert()
}

export function splitWithListeners(split: TextSplitter) {
  split.addEffect((s: TextSplitter) => {
    const onEnter = (e: Event) => animate(e.currentTarget as HTMLElement, { scale: [1, 1.2, 1] });
    s.words.forEach((w: HTMLElement) => w.addEventListener('pointerenter', onEnter));
    return () => s.words.forEach((w: HTMLElement) => w.removeEventListener('pointerenter', onEnter));
  });
}

export function replaceSplitText(split: TextSplitter, html: string) {
  split.html = html; // e.g. the server-patched innerHTML
  split.refresh();
}
```

#### TextSplitter properties `text/splittext/textsplitter-properties`

| Property | Type (`.d.ts`) | Meaning |
| --- | --- | --- |
| `$target` | `HTMLElement` | The split element. |
| `html` | `string` | Original `innerHTML` captured at construction; what `revert()`/`refresh()` restore. |
| `debug` | `boolean` | Debug outlines on/off. |
| `includeSpaces` | `boolean` | See settings. |
| `accessible` | `boolean` | See settings. |
| `lines` | `any[]` (HTMLElements) | Line elements. |
| `words` | `any[]` | Word elements (the docs table mislabels this "lines"). |
| `chars` | `any[]` | Char elements (same mislabel in docs). |
| `lineTemplate` / `wordTemplate` / `charTemplate` | `string \| false \| SplitFunctionValue` | Resolved templates (objects are compiled to strings). |

Also public in the types but undocumented: `linesOnly`, `effects`, `effectsCleanups`, `cache`, `ready` (true once a line split has happened or lines are off), `width`, `resizeTimeout`, `resizeObserver`, `split(clearCache?)`, `splitNode(node)`.

### scrambleText `text/scrambletext`

Since 4.4.0. `scrambleText(params?: ScrambleTextParams): FunctionValue<ScrambleTextTween>`. Use it as the value of `innerHTML` in `animate()` (not `textContent`). Characters cycle through random glyphs, then settle left-to-right (or per `from`) into the final text.

#### scrambleText parameters `text/scrambletext/scrambletext-parameters`

| Param | Type | Default | Meaning |
| --- | --- | --- | --- |
| `text` | `string \| (target, index, targets) => string` | target's original text | Text to end on. |
| `chars` | `string \| fn` | `'a-zA-Z0-9!%#_'` | Glyph pool. Literal chars, ranges (`'a-f'`, `'A-Z0-9'`, by code point), or a preset: `lowercase`, `uppercase`, `numbers`, `symbols` (`!%#_\|*+=`), `braille`, `blocks`, `shades`. A literal `-` must be first or last. |
| `override` | `boolean \| string` | `true` | Look of the text before the wave reaches it: `true` scrambled with `chars`; `false` original text; `''` start empty (animates only to the end length); `' '` blanks; other string = its own glyph pool (ranges and presets allowed). |
| `ease` | `EasingParam` | `'linear'` | Easing of the reveal wave. |
| `cursor` | `boolean \| number \| string` | `''` (none) | Glyphs shown at the wave front: `true` = `'_'`, number = char code, string used as-is (multi-char = wider cursor). |
| `revealRate` | `number` | `60` | Characters entering the reveal per second; with `settleDuration` it sets the auto duration. |
| `revealDelay` | `number \| fn` | `0` | ms inside the animation before the wave starts. Since 4.4.0. |
| `settleRate` | `number` | `30` | Glyph changes per second while a character is scrambling. Since 4.4.0. |
| `settleDuration` | `number` | `300` | ms each character scrambles before landing. Since 4.4.0. |
| `delay` | `number \| fn` | `0` | ms before the whole scramble starts. |
| `duration` | `number \| fn` | auto | Overrides the computed duration when `> 0`; auto = `(length - 1) * 1000 / revealRate + settleDuration` (+ `revealDelay`). Since 4.4.0. |
| `perturbation` | `number` 0..1 | `0` | Random jitter of each character's start/end; at `1` characters overlap and land out of order. |
| `from` | `'auto' \| 'left' \| 'center' \| 'right' \| 'random' \| number` | `'auto'` | Where the wave starts. `'auto'` = left when the text grows, right when it shrinks; a number is a character index. |
| `reversed` | `boolean` | `false` | Invert the order (e.g. `'center'` then goes edges-inward). |
| `seed` | `number` | `0` | Non-zero makes the random sequence repeatable; `0` is unseeded. |

#### scrambleText callbacks `text/scrambletext/scrambletext-callbacks`

| Callback | Signature | Default | Meaning |
| --- | --- | --- | --- |
| `onChange` | `(text: string, progress: number) => void` | noop | Fires each time the glyphs refresh (at `settleRate`), with the current string and eased progress 0..1. Not fired for the first and last frames. |

```ts
export function scrambleTo(value: string) {
  return animate(counter, {
    innerHTML: scrambleText({ text: value, chars: 'numbers', from: 'right', seed: 7 }),
  });
}
```

---

## Layout `layout`

Since 4.3.0. `createLayout(root: DOMTargetSelector, params?: AutoLayoutParams): AutoLayout`. FLIP-style engine: it measures a subtree, you change the DOM (classes, order, `display`, parent, added nodes), then it animates every element from the old measurements to the new ones. It can animate things CSS cannot transition: `display` changes, flex/grid switches, DOM reordering, moving an element to another parent, and a hidden element "becoming" a visible one elsewhere.

Two ways to drive it (usage: `layout/usage`):
- `layout.record()` → mutate the DOM → `layout.animate(params?)`.
- `layout.update(mutator, params?)`, which does all three. The docs warn it may not fit every framework; fall back to the manual pair when the DOM change happens outside your callback (for LiveView the server patches, so use the manual pair, see the hook sketch below).

`createLayout()` itself records immediately, so `animate()` can be called right after a mutation without an explicit `record()`.

Usage recipes in the docs (`layout/usage/<page>`): `specifying-a-root` (one layout per root, independent), `css-display-property-animation` (switching `display` values including `none`), `staggered-layout-animation` (`delay: stagger()`), `dom-order-change-animation` (re-append in a new order), `enter-layout-animation` (append new children), `exit-layout-animation` (hide with `display: none`, then remove after the timeline resolves), `swap-parent-animation` (move a child to a sibling container; give the destination a higher z-index), `animate-modal-dialog` (a `<dialog>` root plus explicit `children` and shared layout ids so a card appears to grow into the modal).

### Root `layout/usage/specifying-a-root`

| Param | Type | Default | Meaning |
| --- | --- | --- | --- |
| `root` | CSS selector / DOM element | required | The measured subtree. Its size is animated; its **position never is** (so siblings outside the layout don't jump). Only HTML elements are tracked. |

### Settings `layout/layout-settings`

| Setting | Type (`.d.ts`) | Default | Meaning |
| --- | --- | --- | --- |
| `children` | `DOMTargetSelector \| Array<DOMTargetSelector>` | `'*'` | Which descendants are animated targets. Descendants of a target that are not themselves targets are "frozen": they are not tweened, they jump to their new state at the midpoint (see `swapAt`). Use it to keep reflowing text blocks still, and to include elements outside the root that share a layout id. Docs type it `String \| Array<String>`. |
| `delay` | `number \| FunctionValue` | `0` | Default delay per element (ms). Accepts `stagger()`. |
| `duration` | `number \| FunctionValue` | `350` | Default duration per element (ms). Accepts `stagger()`. When `ease` is a spring, the spring's settling duration replaces it. |
| `ease` | `EasingParam \| FunctionValue` | `'inOut(3.5)'` | Default easing or `spring()`. |
| `properties` | `Array<string>` | see below | Extra CSS properties to measure and interpolate, including custom properties (`'--my-var'`). Position and size are always handled. |

Default animated properties: `opacity`, `fontSize`, `color`, `backgroundColor`, `borderRadius`, `border`, `filter`, `clipPath`. Keys used in the constructor's `enterFrom` / `leaveTo` / `swapAt` are added automatically.

Also accepted by the types (undocumented on the settings page): `id` (timeline id; also becomes `layout.id`), `playbackEase`, every Timer parameter (`loop`, `alternate`, `reversed`, `autoplay` including a scroll observer, `frameRate`, `playbackRate`, `loopDelay`, …) and every Timeline callback. `delay`/`duration`/`ease`/state params/callbacks can all be overridden per call in `animate(params)` / `update(fn, params)`.

### States parameters `layout/states-parameters`

Each takes an object of CSS properties (values `number | string | FunctionValue`) plus optional `delay`, `duration`, `ease` overrides for that phase. Transform shorthands (`x`, `y`, `scale`, `rotate`) are **not supported** here; write a full `transform` string.

| State | Default | Applies to |
| --- | --- | --- |
| `enterFrom` | `{ opacity: 0 }` | Starting values for elements entering: newly inserted under the root, or going from `display: none` / `visibility: hidden` to visible. |
| `leaveTo` | `{ opacity: 0 }` | End values for elements leaving: becoming `display: none` or `visibility: hidden`. (Elements removed from the DOM are not part of the new measurement and cannot animate out.) |
| `swapAt` | `{ opacity: 0, ease: 'inOut(1.75)' }` | Midpoint values for frozen (non-target) descendants whose size changed inside a target whose size also changed: they tween to these values by 50% and back to their real values by 100%, with the new layout swapped in at the midpoint. `{ opacity: 1 }` removes the fade. |

Per-call state objects are merged over the constructor ones (per-call keys win; missing timing keys fall back to the call's `delay`/`duration`/`ease`, then the layout defaults). Reading the source: a per-call state property animates only if its name is already known to the layout (default list, `properties`, or a constructor state); `transform` is always handled.

After each `animate()`/`update()` the instance exposes `entering`, `leaving` and `swapping` arrays (cleared and refilled on every call).

### Layout methods `layout/layout-methods`

| Method | Returns | Meaning |
| --- | --- | --- |
| `record()` | `AutoLayout` | Snapshot the current state as the "from" state. If a layout animation is in flight it is measured mid-flight, then cancelled, so a new transition continues from where things visually are. |
| `animate(params?)` | `Timeline` | Measure the new state, diff against the last snapshot, build and start a timeline. Per-call params: `delay`, `duration`, `ease`, `playbackEase`, `id`, `enterFrom`, `leaveTo`, `swapAt`, Timer params, callbacks. If nothing changed, returns an already completed timeline. |
| `update(callback, params?)` | `Timeline` | `record()`, then `callback(layout)`, then `animate(params)`. |
| `revert()` | `AutoLayout` | Jump every running layout animation to its end state, clear both snapshots, remove the `data-layout-id` attributes it wrote, and restore CSS transitions on the next frame. The DOM ends in its real current state. Call `record()` again before animating after a revert. |

```ts
export function makeLayout(): AutoLayout {
  return createLayout(list, {
    children: '.card',
    duration: 400,
    delay: stagger(30),
    ease: 'out(3)',
    properties: ['boxShadow', '--card-alpha'],
    enterFrom: { opacity: 0, transform: 'scale(.9)', duration: 250 },
    leaveTo: { opacity: 0, transform: 'translateY(-12px)' },
    swapAt: { opacity: 1 },
    onComplete: () => {},
  });
}

export function removeWithExit(layout: AutoLayout): Timeline {
  const tl = layout.update(() => {
    item.style.display = 'none';
  });
  tl.then(() => layout.leaving.forEach(($el) => $el.remove()));
  return tl;
}
```

### Layout id attribute `layout/layout-id-attribute`

Every recorded element gets `data-layout-id` (auto values look like `node-12`). You can set it yourself. Matching is by id, not by node identity: if two elements share an id and one is hidden (`display: none` / `visibility: hidden`) while the other is visible, the layout animates one into the other. That is how a card can morph into a copy in a modal or a different container without moving the node. Elements outside the root are only picked up when they match `children` and share an id with an element inside the root.

### Layout callbacks `layout/layout-callbacks`

Layout animations take all Timeline callbacks (`onBegin`, `onBeforeUpdate`, `onUpdate`, `onRender`, `onLoop`, `onPause`, `onComplete`), in `createLayout()` params or per call. `.then()` exists on the `Timeline` returned by `animate()` / `update()`, not on the `AutoLayout` (the docs' settings diagrams show `createLayout(...).then(...)`, which does not exist in the types).

Callback behaviour visible in the source:
- Your `onComplete` fires when the transition finishes **and also when it is interrupted** by a new `record()`/`update()` (the internal pause handler calls it).
- If `animate()` finds no change, your `onComplete` is **not** called (the returned timeline is simply complete). A self-scheduling loop driven by `onComplete` stops there; `.then()` still resolves.

### Layout properties `layout/layout-properties`

| Property | Type (`.d.ts`) | Meaning |
| --- | --- | --- |
| `params` | `AutoLayoutParams` | Params passed to `createLayout()` (with defaults filled in). |
| `root` | `DOMTarget` | Resolved root. |
| `children` | `LayoutChildrenParam` | The `children` selector(s), re-queried on every record. |
| `enterFromParams` / `leaveToParams` / `swapAtParams` | `LayoutStateParams` | Resolved state params. |
| `properties` | `Set<string>` | Interpolated CSS properties. |
| `oldState` / `newState` | `LayoutSnapshot` | Previous and latest measurements. Helpers: `getNode(el)` → `LayoutNode`, `getComputedValue(el, prop)` → `number \| string`; also `forEachNode(cb)`, `forEachRootNode(cb)`, `nodes: Map<string, LayoutNode>`, `scrollX`, `scrollY`. |
| `timeline` | `Timeline` (null before first animate) | Timeline of the last `animate()`/`update()`. |
| `animating` / `swapping` / `entering` / `leaving` | `Array<DOMTarget>` | Elements in each role during the last `animate()`. Read them right after `update()`. |
| `id` | `number \| string` | Layout id (also the timeline id). |

Undocumented but public: `absoluteCoords` (true when the root is `position: fixed/absolute`), `recordedProperties`, `pendingRemoval`, `transitionMuteStore`, `transformAnimation` (a WAAPI animation used for elements that carry a CSS `transform`, synced into the timeline).

### What happens to the DOM during a transition

While a layout timeline runs:
- The root gets the class `is-animated` (and `position: relative` if it was static).
- Each target gets inline `position: absolute` (`fixed` for fixed/absolute roots), `left/top/margin-left/margin-top: 0`, `translate`, explicit `width`/`height`, `min-width/min-height: auto`, `max-width/max-height: none`; `display: grid` elements are forced to `display: block !important`.
- Frozen descendants get the same size and translate styles, and their new values are set at the midpoint.
- Measured elements have `transition: none !important` inline during record/animate; the original value is restored one frame after completion.
- Transformed ancestors of the root have `transform: none` briefly while measuring.
- If the page scrolled between record and animate, scroll is restored to the recorded position on the next frame.

On completion, inline styles are restored to what they were before the animation, except that elements with a CSS transform keep an inline `transform` equal to their final computed transform.

### Common auto layout gotchas `layout/common-auto-layout-gotchas`

Docs list, with fixes:
- Descendants of `children` targets fade out and back: they are frozen and use `swapAt` (default opacity 0). Add them to `children`, or set `swapAt: { opacity: 1 }`.
- The root's position jumps: root position is never animated. Use its parent as the root.
- Text reflows mid-transition (mostly Firefox, when `fontSize` animates with width/height): use `white-space: nowrap` where wrapping isn't needed.
- Inline elements beside bare text don't move: elements next to text nodes are excluded from position animation. Wrap the loose text in spans.
- Transform shorthands in state params do nothing: use `transform: '...'`.
- SVG elements and their descendants are never tracked.

---

## LiveView hooks (layout)

Server patches change the DOM outside any `update()` callback, so use the manual pair:
`record()` in `beforeUpdate`, `animate()` in `updated`, with `data-layout-id` rendered by the
server on the root and every child. The browser-verified hook and its limits (removed items
do not animate out) are in [liveview-islands.md](liveview-islands.md#layout-on-server-driven-lists-lab).

Do not use `children: '[data-layout-id]'` as a selector: after the first record every element under the root carries that attribute.

---

## Gotchas

1. `createDrawable()` hides the stroke on creation (initial draw `'0 0'`) unless you pass `start, end` or the element already has `pathLength="1000"`.
2. `createDrawable()` rewrites `pathLength`; any other code relying on the original `pathLength` or dash attributes breaks.
3. `morphTo` throws on anything but `path`/`polygon`/`polyline`; the error appears when `animate()` is called, not when `morphTo()` is.
4. `morphTo(x, 0)` interpolates raw attribute strings: point counts and commands must already match.
5. `createMotionPath()` bakes the path's screen transform into the tween for HTML targets; after the SVG resizes, rebuild the animation. An invalid path gives `undefined` and a console warning.
6. `splitText()` splits only the first matching element.
7. With `lines`, the split is asynchronous; arrays are empty until fonts are ready. Animate inside `addEffect()`.
8. With `lines`, every width change rebuilds all span elements; animations and listeners attached outside `addEffect()` are lost silently.
9. `words` defaults to `true`; `{ chars: true }` also wraps words. Pass `words: false` for flat chars.
10. `accessible: true` puts a hidden copy of the original HTML inside the target. Selectors like `#target a` or `querySelector` inside the target can match the hidden copy, and any `id` in the original markup is duplicated.
11. `revert()` and `refresh()` write `split.html` back into the target. `html` is captured at construction; if the content changed since (server patch, your own edit), set `split.html` first or you restore stale text.
12. `refresh()` returns `void` in the types; don't chain it.
13. `scrambleText` writes `innerHTML`: target text containing `<` or `&` is parsed as markup, and any child elements in the target are flattened to text.
14. `scrambleText` without `text` goes back to the first text it ever saw on that element (cached per element). Pass `text` explicitly when content changes.
15. `scrambleText` sets its own tween `duration` and a linear tween `ease`; `duration`/`ease` on the surrounding `animate()` are ignored for that property. Put them inside `scrambleText({...})`.
16. Layout: removing a node from the DOM gives no exit animation. Hide it (`display: none`), animate, then remove it in `.then()`. The same applies to server-side removals (e.g. LiveView stream deletes): they cannot animate out through the layout.
17. Layout: `onComplete` fires on interruption, and does not fire when no change was detected.
18. Layout: during a transition targets are absolutely positioned with inline sizes; CSS selectors or JS that read layout (`getBoundingClientRect`, grid placement) during that window see the animated state. Grid containers are temporarily `display: block`.
19. Layout: CSS transitions on measured elements are muted during the transition and restored one frame after; a CSS transition you expected to run at the same moment will not.
20. Layout: per-call state properties unknown to the layout at construction are ignored; declare them in the constructor's state params or `properties`.
21. Layout: `createLayout()` measures and tags every element under the root immediately, so create it after the root's content is in the DOM.

## Lifecycle and cleanup

Context: inside a Phoenix LiveView hook the server can patch or remove any of these nodes at any time. Morphdom patches can remove attributes and inline styles that the client added to an element the server re-renders.

- **`morphTo` / `createMotionPath` values**: no object of their own. Stop them through the animation that uses them (`anim.revert()` restores the original `d` / `points` / transform styles; `anim.cancel()` or `pause()` just stops). Nothing observed or listened to.
- **Drawables (`createDrawable`)**: no revert method. Stop the animation with `pause()`/`cancel()`/`revert()`; none of these undo what the proxy writes. `pathLength="1000"`, `stroke-dasharray`, `stroke-dashoffset` and possibly inline `stroke-linecap` stay on the element with the last drawn value. Remove them yourself if the element must go back to its original look. No listeners or observers.
- **`TextSplitter` (`splitText`)**: call `split.revert()` in `destroyed()` (and before re-splitting). It disconnects the `ResizeObserver`, clears the pending resize timer, runs effect cleanups / reverts effect animations, and restores `innerHTML` from `split.html` (removing all spans, debug outlines and the accessible copy). Without `revert()`, the observer stays attached to the element. Listeners you add inside effects are only removed if the effect returns a cleanup. Animations created outside `addEffect()` are not reverted by it. If the server re-renders the split element's content, the split spans are replaced and `split.words` etc. point at detached nodes; either mark the element `phx-update="ignore"` (client owns the text), or call `split.revert()` in `beforeUpdate` and `splitText()` again in `updated` (verified in a browser, see [liveview-islands.md](liveview-islands.md#what-a-liveview-patch-does-to-animejss-dom-writes)). If created inside `createScope()`, `scope.revert()` reverts it.
- **`scrambleText` animations**: stop with the animation's `pause()`/`cancel()`/`revert()`. Stopping mid-way leaves scrambled glyphs in `innerHTML`; whether `revert()` puts the original text back was not verified, so write the final or original text yourself (or `complete()` the animation) when stopping early. The per-element original-text cache is a `WeakMap` and needs no cleanup. No observers or listeners.
- **`AutoLayout` (`createLayout`)**: call `layout.revert()` in `destroyed()` or before throwing the instance away. It completes the running timeline and transform animation (so inline positioning is restored), removes every `data-layout-id` the layout wrote, clears both snapshots, and restores muted CSS transitions on the next animation frame. It leaves behind: any `data-layout-id` values you set yourself, and the final inline `transform` on elements that had a CSS transform. It creates no observers and no event listeners. To stop a single transition without reverting the layout, use `layout.timeline.cancel()` (or `pause()`), but prefer `record()` (which cancels) or `revert()` (which restores inline styles). If created inside `createScope()`, `scope.revert()` reverts it. A server patch that lands mid-transition can strip the inline styles or ids from patched elements; the next `record()` then measures whatever the patch left, so give animated elements stable server-rendered `data-layout-id`s and let transitions finish (or `revert()`) before large patches.
