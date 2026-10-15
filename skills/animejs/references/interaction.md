# Anime.js v4 interaction: Animatable, Draggable, onScroll

Reference for the three pointer- and scroll-driven APIs in `animejs` 4.5.0: `createAnimatable` (retarget values many times per second without building new animations), `createDraggable` (drag with bounds, snapping, flick physics and auto-scroll) and `onScroll` (a `ScrollObserver` that plays, scrubs or triggers a Timer, Animation or Timeline from scroll position). Use it to pick the right option names, defaults and return types, and to tear each object down cleanly when a Phoenix LiveView hook is destroyed or the server patches the DOM. Types, defaults and behaviour below were checked against the 4.5.0 `.d.ts` files and compiled source. Where the docs say something else, the types and source win, and the difference is listed under "Docs vs types".

Fetch a live page with `uv run scripts/animejs_docs.py <path>`. Leaf pages sit under the section path with the lower-cased name as the last segment. For example, `containerPadding` is `draggable/draggable-settings/containerpadding` and `setX()` is `draggable/draggable-methods/setx`.

```ts
import { createAnimatable, createDraggable, onScroll, ScrollObserver, scrollContainers } from 'animejs';
// Subpath builds: 'animejs/animatable', 'animejs/draggable', 'animejs/events'
```

---

## Animatable `animatable`

`createAnimatable(targets: TargetsParam, parameters: AnimatableParams): AnimatableObject`

`AnimatableObject = Animatable & Record<string, AnimatableProperty>`. Every property key you declare becomes a method on the returned object. Call it with no arguments to read the value, or with arguments to animate to a new one. Values must be `number` or `number[]`: strings, units and relative values are not accepted, and the unit comes from the `unit` setting. Internally each property is one paused `JSAnimation` using `composition: 'replace'`, restarted from its current value on every call. Use it for cursor followers, pointer-driven transforms and per-frame retargeting instead of creating a new `animate()` on every event.

### Settings `animatable/animatable-settings`

A setting can go at the root, where it applies to every property, or inside a per-property object: `x: { unit: 'rem', duration: 400 }`. A bare number, as in `y: 200`, is shorthand for that property's duration. `0` means the value is set immediately with no transition.

| Name | Type | Default | Meaning |
| --- | --- | --- | --- |
| `unit` | `string` (CSS unit) | none (the property's natural unit) | Unit appended to the numeric value, such as `'rad'` for `rotate` or `'rem'` for `x`. Takes effect per property. |
| `duration` | `number >= 0` \| function-based value | `1000` | Transition time in ms for each retarget. Function-based values and `stagger()` are allowed, one per target. |
| `ease` | `EasingParam` | `'out(2)'` | Easing for each retarget. `out*` eases respond better than `in*`, which feel sluggish at the start. |
| `modifier` | `(v: number) => number \| string` | `noop` | Changes the rendered value, as in `utils.snap(n)`, `utils.wrap(a, b)` or `v => -v`. The getter returns the modified value. |
| `composition` | `TweenComposition` | `'replace'` | In the types only, not the docs. The animatable forces `replace` at the animation level. |
| `onBegin`, `onUpdate`, `onRender`, `onComplete`, `onPause`, `onLoop`, `onBeforeUpdate` | `Callback<JSAnimation>` | `noop` | In the types only, not the docs. Root-level `on*` keys go to an internal `callbacks` animation that plays when any property starts moving and completes when every property animation has stopped. `createDraggable` relies on this. |

### Methods `animatable/animatable-methods`

| Call | Returns | Meaning |
| --- | --- | --- |
| `anim.prop()` (getters) | `number \| number[]` | Current value. A multi-value property, such as an RGB color, returns the internal live array, so copy it before changing it. |
| `anim.prop(value, duration?, ease?)` (setters) | `AnimatableObject` (chainable) | Animates from the current value to `value`. A `duration` or `ease` passed here stays in effect for later calls on that property. |
| `revert()` | `this` | Reverts every property animation, which restores or removes the inline styles it wrote. It also replaces every property method with a no-op that returns `undefined`. |

### Properties `animatable/animatable-properties`

| Name | Type | Meaning |
| --- | --- | --- |
| `targets` | `(HTMLElement \| SVGElement \| JSTarget)[]` | Resolved targets. The list is emptied by `revert()`. |
| `animations` | `Record<string, JSAnimation>` | One paused animation per declared property. You can attach callbacks per property, as in `anim.animations.x.onRender = ...`. |
| `callbacks` | `JSAnimation \| null` | In the types only. The shared animation that fires root-level `on*` callbacks. |

```ts
export function animatableFollower(root: HTMLElement, dot: HTMLElement): () => void {
  const follower: AnimatableObject = createAnimatable(dot, {
    x: { duration: 400, ease: 'out(4)' },
    y: { duration: 400, ease: 'out(4)' },
    scale: 200,
  });
  const onMove = (e: PointerEvent) => {
    const r = root.getBoundingClientRect();
    follower.x(e.clientX - r.left).y(e.clientY - r.top);
  };
  root.addEventListener('pointermove', onMove);
  const currentX = follower.x() as number;
  void currentX;
  return () => {
    root.removeEventListener('pointermove', onMove);
    follower.revert();
  };
}

export function animatableColor(swatch: HTMLElement): void {
  const a = createAnimatable(swatch, { backgroundColor: 0 });
  a.backgroundColor([164, 255, 79], 250, 'outQuad');
  const rgb = [...(a.backgroundColor() as number[])];
  void rgb;
}
```

The getter and setter share one overloaded type, so cast the getter's result (`as number` or `as number[]`).

---

## Draggable `draggable`

`createDraggable(target: TargetsParam, parameters?: DraggableParams): Draggable`

Only the first element the target resolves to is used. A plain JS object can also be dragged, through an internal proxy that reads and writes its `x`, `y`, `width` and `height`. Position is written through an internal Animatable, on `translateX` and `translateY` unless `mapTo` changes that. The parameters object mixes axis parameters, settings and callbacks.

### Axes parameters `draggable/draggable-axes-parameters`

`snap` and `modifier` can be set at the root (both axes) or inside `x: {...}` / `y: {...}`. A per-axis value takes precedence.

| Name | Type | Default | Meaning |
| --- | --- | --- | --- |
| `x` | `boolean \| DraggableAxisParam` | `true` | Enables the horizontal axis (`false` locks it) or configures it with an object. |
| `y` | `boolean \| DraggableAxisParam` | `true` | Same for the vertical axis. |
| `snap` | `number \| number[] \| (d: Draggable) => number \| number[]` | `0` | Rounds the release destination to a step, or to the nearest value in an array. A function value is re-evaluated by `refresh()` and after resizes. |
| `modifier` | `TweenModifier` | `noop` | Changes the rendered axis value, as in `utils.wrap(-200, 0)` or `utils.snap(16)`. |
| `mapTo` | `string` | `null` in the docs; the effective value is `'translateX'` / `'translateY'` | Writes the axis value to another property, such as `'rotate'`, `'rotateY'` or `'z'`. |
| `composition` | `TweenComposition` | none | In the types only. Passed to the internal Animatable for that axis. |

### Settings `draggable/draggable-settings`

Settings marked "fn" also accept `(draggable) => value`, which is re-evaluated by `refresh()`. `refresh()` runs by itself after the container or target is resized.

| Name | Type | Default | Meaning |
| --- | --- | --- | --- |
| `trigger` | `DOMTargetSelector` | the target | Element that starts the drag. The target is still the element that moves. |
| `container` | `DOMTargetSelector \| number[]` (`[top, right, bottom, left]`), fn | `null` (page / `window`, unbounded) | Bounding element, or explicit bounds relative to the start position. An element container that overflows also auto-scrolls. |
| `containerPadding` | `number \| number[]` (`[t, r, b, l]`), fn | `0` | Insets the bounds, in px. A single number applies to all four sides. |
| `containerFriction` | `0..1`, fn | `0.8` | Resistance past the bounds while dragging: `0` is free and `1` is a hard wall. |
| `releaseContainerFriction` | `0..1`, fn | the `containerFriction` value | Same resistance, applied to the flick after release. |
| `releaseMass` | `number` (0–10000) | `1` | Mass of the release spring. Lower values move faster. Ignored when `releaseEase` is a spring. |
| `releaseStiffness` | `number` (0–10000) | `80` | Stiffness of the release spring. Lower values move more slowly. Ignored when `releaseEase` is a spring. |
| `releaseDamping` | `number` (0–10000) | `20` in the source (the docs say `10`) | Damping of the release spring. Lower values bounce more at the bounds. Ignored when `releaseEase` is a spring. |
| `velocityMultiplier` | `number >= 0`, fn | `1` | Scales the flick velocity: `0` removes the throw and `2` doubles it. |
| `minVelocity` | `number >= 0`, fn | `0` | Lower limit on release velocity. |
| `maxVelocity` | `number >= 0`, fn | `50` | Upper limit on release velocity. |
| `releaseEase` | `EasingParam` | `eases.outQuint` | Ease for the release, snap and back-in-bounds motion. Passing `spring({...})` replaces `releaseMass`, `releaseStiffness` and `releaseDamping`, and the spring's own `velocity` is replaced by the drag velocity. |
| `dragSpeed` | `number`, fn | `1` | Scales how far the target moves per unit of pointer movement. `0` blocks dragging and a negative value inverts it. |
| `dragThreshold` (4.2.1) | `number \| { mouse?: number; touch?: number }`, fn | `{ mouse: 3, touch: 7 }` | Distance in px the pointer must move before a drag starts. A single number applies to both pointer types. |
| `scrollThreshold` | `number`, fn | `20` | How many px past the visible edge the target must go before the container auto-scrolls. |
| `scrollSpeed` | `number`, fn | `1.5` | Auto-scroll speed. `0` turns auto-scroll off. |
| `cursor` | `boolean \| { onHover?: string; onGrab?: string }`, fn | `{ onHover: 'grab', onGrab: 'grabbing' }` | Cursor styles, applied only when `(pointer:fine)` matches. `false` turns them off. |

### Callbacks `draggable/draggable-callbacks`

Each callback is `Callback<Draggable>`, which is `(self: Draggable) => any`, and each defaults to `noop`. You can replace one at runtime through the property of the same name.

| Name | Fires when |
| --- | --- |
| `onGrab` | The pointer goes down on the trigger, after running motion has stopped and the bounds have been re-measured. |
| `onDrag` | Each pointer move once the drag threshold has been passed. |
| `onUpdate` | The rendered position actually changes, whether from dragging, the release motion or `setX`/`setY` (unless `muteCallback` is set). |
| `onRelease` | The pointer comes up after a grab, even if no drag happened. It runs after the release motion has started, so calling `stop()` inside it cancels that motion. |
| `onSnap` | The snapped value changes, either at release or during a drag. The drag check uses the raw position, so it fires even when the element is not visibly snapping. Add `modifier: utils.snap(n)` to make the movement match. |
| `onSettle` | The target has come fully to rest after a release. |
| `onResize` | The container or target has changed size (debounced 150 ms), before values are recomputed. |
| `onAfterResize` | After the resize `refresh()` has run. Call `self.animateInView()` here to bring the target back inside. |

### Methods `draggable/draggable-methods`

| Method | Returns | Meaning |
| --- | --- | --- |
| `disable()` | `this` | Stops input, removes listeners, reverts the `touch-action`, cursor, `pointer-events` and z-index inline styles, and adds the class `is-disabled` to the target. The position is kept. |
| `enable()` | `this` | Re-attaches listeners, sets `touch-action` on the trigger and removes `is-disabled`. It is called by the constructor. |
| `setX(x: number, muteCallback = false)` | `this` (`undefined` if the x axis is disabled) | Moves the target instantly. Setting `draggable.x = n` does the same with the callback on. `true` suppresses `onUpdate`. |
| `setY(y: number, muteCallback = false)` | `this` (`undefined` if the y axis is disabled) | Same for y. |
| `animateInView(duration = 350, gap = 0, ease = 'inOutQuad')` | `this` | Stops any motion, re-measures, then animates the target back inside the visible area of the container, `gap` px from the edges. |
| `scrollInView(duration = 350, gap = 0, ease = 'inOutQuad')` | `this` | Animates the container's scroll until the target's destination is inside the scroll threshold. Does nothing when `container` is an array. |
| `stop()` | `this` | Stops the drag ticker, the release and overshoot motion, container scroll animations, and any outside `animate()` running on the draggable's `x`, `y`, `progressX` or `progressY`. |
| `reset()` | `this` | `stop()`, moves the target to `0, 0` and clears pointer, velocity and state flags. |
| `revert()` | `this` | `reset()` and `disable()`, removes `is-disabled`, reverts the internal tickers and Animatable (which removes the inline transform), and disconnects the ResizeObserver. |
| `refresh()` | `void` (the docs say `this`) | Re-evaluates function-valued parameters and re-measures bounds. Values it recomputes: `snap`, `container`, `containerPadding`, `containerFriction`, `releaseContainerFriction`, `dragSpeed`, `dragThreshold`, `scrollSpeed`, `scrollThreshold`, `minVelocity`, `maxVelocity`, `velocityMultiplier` and `cursor`. |

A `Draggable` can itself be the target of an animation, as in `animate(draggable, { x: [-100, 100], loop: true })`, because `x`, `y`, `progressX` and `progressY` are setters. `stop()` cancels such animations.

### Properties `draggable/draggable-properties`

Types come from `draggable.d.ts`. "rw" marks setters you can use. Many fields are public but internal.

| Name | Type | Meaning |
| --- | --- | --- |
| `x`, `y` | `number` (rw) | Current position. Setting it calls `setX`/`setY`. |
| `progressX`, `progressY` | `number` (rw) | Position as 0–1 across the container bounds. Only meaningful with a `container`. |
| `snapX`, `snapY` | `number \| number[]` (rw) | Snap increment per axis. |
| `dragSpeed`, `dragThreshold`, `scrollSpeed`, `scrollThreshold`, `minVelocity`, `maxVelocity`, `velocityMultiplier`, `containerFriction`, `releaseContainerFriction` | `number` (rw) | Resolved setting values. `dragThreshold` holds the value for the current pointer type. |
| `containerPadding` | `[number, number, number, number]` (rw) | Resolved padding. |
| `cursor` | `boolean \| DraggableCursorParams` (rw) | Resolved cursor setting. |
| `releaseEase` | `EasingFunction` (rw) | Parsed release ease. |
| `releaseXSpring`, `releaseYSpring` | `Spring` | Release springs. The docs call this a single `releaseSpring`, which does not exist. |
| `hasReleaseSpring` | `boolean` | `true` when `releaseEase` was a spring. |
| `containerBounds` | `[t, r, b, l]` | Computed movement limits. |
| `containerArray` | `number[] \| null` | The array form of `container`, if one was given. |
| `$container`, `$target`, `$trigger` | `HTMLElement` | Resolved elements. `$container` is `document.body` when there is no container. |
| `$scrollContainer` | `Window \| HTMLElement` | Element that auto-scrolls. |
| `velocity` | `number` | Current speed, clamped to `[minVelocity, maxVelocity]`. |
| `angle` | `number` | Movement direction in radians. |
| `xProp`, `yProp` | `string` | Properties the axes write to (`translateX` / `translateY` or the `mapTo` values). |
| `destX`, `destY` | `number` | Current release or snap destination. |
| `deltaX`, `deltaY` | `number` | Change since the last render. |
| `enabled`, `grabbed`, `dragged`, `released`, `updated`, `manual`, `contained`, `canScroll`, `initialized`, `fixed`, `useWin`, `isFinePointer` | `boolean` | State flags. `fixed` means the target is `position: fixed`, `useWin` means the page is the container, `initialized` turns true after the first ResizeObserver callback, and `manual` means the position is being set programmatically. |
| `disabled` | `[number, number]` | `1` for each locked axis. |
| `snapped` | `[number, number]` | Last snapped x, y. |
| `scroll` | `{ x: number; y: number }` | Container scroll position. |
| `coords` | `[x, y, prevX, prevY]` | Internal coordinates. |
| `pointer` | 8-tuple of numbers | Current, previous and working pointer positions. The docs say 4 values. |
| `scrollView` | `[w, h]` | Scrollable size. |
| `dragArea` | `[x, y, w, h]` | Visible container rect. |
| `scrollBounds`, `targetBounds` | `[t, r, b, l]` | Internal bounds. |
| `window` | `[w, h]` | Viewport size. |
| `activeProp` | `string` | Main axis property: `yProp`, or `xProp` when y is locked. Nothing reads it in 4.5.0. |
| `animate` | `AnimatableObject` | The internal Animatable that drives position. |
| `parameters` | `DraggableParams` | The original parameters object, which `refresh()` reads again. |
| `onGrab` … `onAfterResize` | `Callback<this>` (rw) | The eight callbacks. |

The docs also list `pointerVelocity` and `pointerAngle`. Neither exists in 4.5.0.

```ts
export function draggableCard(card: HTMLElement, board: HTMLElement, onDrop: (x: number, y: number) => void): Draggable {
  return createDraggable(card, {
    container: board,
    containerPadding: () => (board.clientWidth < 600 ? 8 : 24),
    x: { snap: 40 },
    y: { snap: 40 },
    releaseEase: spring({ stiffness: 150, damping: 15 }),
    dragThreshold: { mouse: 3, touch: 10 },
    cursor: { onHover: 'grab', onGrab: 'grabbing' },
    onSettle: self => onDrop(self.x, self.y),
    onAfterResize: self => { self.animateInView(300, 8); },
  });
}

export function draggableKnob(knob: HTMLElement): Draggable {
  return createDraggable(knob, {
    y: false,
    x: { mapTo: 'rotate', modifier: utils.wrap(-180, 180) },
    container: [0, 360, 0, -360],
  });
}
```

---

## onScroll / ScrollObserver `events/onscroll`

`onScroll(parameters?: ScrollObserverParams): ScrollObserver`. The section index is `events`.

To attach an observer, either pass it as the `autoplay` value of `animate()`, `createTimer()`, `createTimeline()` or `waapi.animate()`, or create it on its own and call `.link(obj)`. Observers that share a container element share one internal `ScrollContainer`, stored in the exported `scrollContainers` Map. That container owns the scroll listener, a ResizeObserver and the timers. The observer finishes setting up on the next frame, so `target`, offsets and `progress` are not ready until then.

### Settings `events/onscroll/scrollobserver-settings`

| Name | Type | Default | Meaning |
| --- | --- | --- | --- |
| `container` | `TargetsParam` (selector or element; the first match is used) | `null` → `document.body` / `window` | Scrolling element to watch. |
| `target` | `TargetsParam` | the first DOM target of the linked animation (for a Timeline, of the first child that has one), otherwise `document.body` | Element whose position is compared against the thresholds. |
| `debug` | `boolean` | `false` | Draws threshold rulers inside the container, one colour per observer. The left side marks container positions and the right side target positions. |
| `axis` | `'x' \| 'y'`, fn | `'y'` | Scroll direction to track. |
| `repeat` | `boolean`, fn | `true` | With `false`, the observer reverts itself after the first completion, once the linked object has also completed. |
| `id` | `number \| string` | an auto-incremented index | In the types only. Used in the debug labels. |
| `enter`, `leave` | see thresholds | `'end start'`, `'start end'` | Where observing starts and stops. |
| `sync` | see sync modes | `'play pause'` | How the linked object follows the scroll. |

"fn" means `(observer: ScrollObserver) => value`, which `refresh()` re-evaluates. The function-valued parameters are `repeat`, `axis`, `enter` and `leave`.

### Thresholds `events/onscroll/scrollobserver-thresholds`

A threshold is met when a point on the container lines up with a point on the target. Three syntaxes are accepted, with type `ScrollThresholdValue | ScrollThresholdParam | fn`:

| Form | Example | Meaning |
| --- | --- | --- |
| Object | `{ target: 'top', container: 'bottom' }` | Explicit sides. A missing side takes the default (`enter`: target `start`, container `end`; `leave`: target `end`, container `start`). |
| Single value | `'bottom'` or `100` | Container side only. The target side takes its default. |
| Pair string | `'bottom top'` | **Container first, target second.** |

Defaults: `enter: 'end start'`, which starts when the target's start reaches the container's end. `leave: 'start end'`, which stops when the target's end reaches the container's start.

Value grammar. Each part can combine the forms below. Leaf paths: `.../numeric-values`, `.../positions-shorthands`, `.../relative-position-values`, `.../min-max`.

| Kind | Examples | Meaning |
| --- | --- | --- |
| Number | `100`, `-25` | px from the element's start edge. |
| Unit string | `'1rem'`, `'2em'` | Converted to px against the target element. |
| Percentage | `'10%'` | Percentage of that element's size along the axis. |
| Keyword | `'top'`, `'left'`, `'start'` = 0; `'center'` = 50%; `'bottom'`, `'right'`, `'end'` = 100% | Keywords do not depend on the axis: `'top'` means the start edge even when `axis: 'x'`. |
| Relative | `'center+=1em'`, `'top-=100%'`, `'bottom*=.5'` | `+=`, `-=` and `*=` applied to the value on their left. |
| Min / max | `'min'`, `'max'`, `'max-=50'` | Clamps to the smallest or largest scroll position that can actually be reached. Use it when an element near the top or bottom of the page could never meet the threshold. |

### Sync modes `events/onscroll/scrollobserver-synchronisation-modes`

The `sync` value (`boolean | number | string | EasingParam`) is read in this order:

| Value | Mode | Behaviour |
| --- | --- | --- |
| `false`, `0` | none | The linked object is paused by `link()` and stays paused. Only callbacks run. |
| `true`, `1`, `'linear'` | playback progress (`.../playback-progress`) | Linked progress equals scroll progress between `enter` and `leave`. |
| number in `(0, 1)` | smooth scroll (`.../smooth-scroll`) | Progress eases toward the scroll position each frame. Smaller values catch up more slowly. |
| an easing string or function (`'inOutCirc'`, `'out(3)'`, `eases.outQuad`) | eased scroll (`.../eased-scroll`) | Progress is remapped through the ease. |
| any other string | method names (`.../method-names`) | Space-separated method names on the linked object. Unknown names do nothing. |

Method-name positions:

| Count | Mapping | Example |
| --- | --- | --- |
| 1 | enter | `'play'` |
| 2 | enter, leave | `'play pause'` (default) |
| 3–4 | enterForward, leaveForward, enterBackward, leaveBackward | `'play pause reverse reset'`, `'resume pause reverse reset'` |

Any method with no arguments works, such as `play`, `pause`, `resume`, `reverse`, `restart`, `reset`, `complete`, `cancel` or `revert`.

### Callbacks `events/onscroll/scrollobserver-callbacks`

Each callback is `Callback<ScrollObserver>` and defaults to `noop`. When the target comes into view, the order is: the sync method, then `onEnter`, then `onEnterForward` or `onEnterBackward`. Leaving follows the same order.

| Name | Since | Fires when |
| --- | --- | --- |
| `onEnter` | 4.0.0 | Each time the `enter` threshold is crossed in either direction. It also fires once when the page loads sitting exactly on a threshold. |
| `onEnterForward` | 4.0.0 | Entering while scrolling forward (down or right). |
| `onEnterBackward` | 4.0.0 | Entering while scrolling backward. |
| `onLeave` | 4.0.0 | Each time the `leave` threshold is crossed in either direction. |
| `onLeaveForward` | 4.0.0 | Leaving while scrolling forward. |
| `onLeaveBackward` | 4.0.0 | Leaving while scrolling backward. |
| `onUpdate` | 4.0.0 | Each scroll tick while in view, plus the tick on which it leaves. During smooth sync it also fires while progress is catching up. |
| `onSyncComplete` | 4.0.0 | The linked object has reached the end of its sync. Only fires when `sync` is on. |
| `onResize` | 4.3.3 | The container was resized (debounced 250 ms), after the observer has refreshed. |

### Methods `events/onscroll/scrollobserver-methods`

| Method | Returns | Meaning |
| --- | --- | --- |
| `link(obj: Tickable \| WAAPIAnimation)` | `this` | Attaches a Timer, Animation, Timeline or WAAPI animation. Only one object can be linked; a new call replaces the previous one. The object is paused first, and WAAPI animations are set to `persist`. Passing an object as `autoplay: onScroll(...)` does the same thing. |
| `refresh()` | `this` | Re-evaluates `repeat`, `axis`, `enter` and `leave` and re-measures bounds. Container resizes already trigger it; call it yourself when the target's layout moves without the container changing size. |
| `revert()` | `this` (`undefined` if already reverted) | Detaches the observer and removes its debug markup. Once the last observer on a container is gone, the container's scroll listener, ResizeObserver and timers are removed too. The linked object is **not** reverted. |

The types also list `debug()`, `removeDebug()`, `updateBounds()` and `handleScroll()`. These are internal.

### Properties `events/onscroll/scrollobserver-properties`

| Name | Type | Meaning |
| --- | --- | --- |
| `id` | `string \| number` | Identifier. |
| `index` | `number` | Creation index. |
| `container` | `ScrollContainer` | Shared container record (`.element`, `.scrollX`/`.scrollY`, `.width`/`.height`, `.velocity`, ...). |
| `target` | `HTMLElement` | Observed element, set on the next frame. |
| `linked` | `Tickable \| WAAPIAnimation` | Linked object. |
| `repeat` | `boolean` | Resolved `repeat`. |
| `horizontal` | `boolean` | `true` when `axis` is `'x'`. |
| `enter`, `leave` | `ScrollThresholdParam \| ScrollThresholdValue \| ScrollThresholdCallback` | Resolved thresholds. `refresh()` overwrites them from the params. |
| `sync` | `boolean` | Whether any sync mode is on. |
| `syncEase` | `EasingFunction` | In the types only. The ease used in eased mode. |
| `syncSmooth` | `number` | In the types only. The smoothing factor used in smooth mode (`1` means exact). |
| `velocity` | `number` (getter) | Scroll velocity of the container. |
| `backward` | `boolean` (getter) | Last scroll direction was backward. |
| `scroll` | `number` (getter) | Scroll position of the container along the axis. |
| `progress` | `number` (getter) | 0–1 between `enter` and `leave`. |
| `completed`, `began`, `isInView` | `boolean` | Lifecycle flags. |
| `reverted`, `ready` | `boolean` | In the types only. Set up / torn down. |
| `offset`, `offsetStart`, `offsetEnd`, `distance` | `number` | Target offset in the scroll content, the scroll positions where `enter` and `leave` are met, and the distance between them. |
| `thresholds`, `coords` | arrays | In the types only. Resolved threshold tokens and pixel values, used by the debug display. |

```ts
export function scrollScrub(panel: HTMLElement, scroller: HTMLElement): () => void {
  const anim = animate(panel, {
    x: '15rem',
    ease: 'linear',
    autoplay: onScroll({
      container: scroller,
      enter: 'bottom-=50 top',
      leave: 'top+=60 bottom',
      sync: 0.25,
    }),
  });
  return () => { anim.revert(); }; // also reverts the observer given through autoplay
}

export function scrollTriggered(section: HTMLElement, items: HTMLElement[]): () => void {
  let offset = 40;
  const tl = createTimeline({ autoplay: false }).add(items, { opacity: [0, 1], y: [20, 0] });
  const observer: ScrollObserver = onScroll({
    target: section,
    enter: () => `bottom-=${offset} top`,
    leave: { target: 'bottom', container: 'top' },
    sync: 'play pause reverse reset',
    onEnterForward: self => { void self.progress; },
  }).link(tl);
  const retune = (next: number) => { offset = next; observer.refresh(); };
  retune(80);
  return () => {
    observer.revert(); // link() does not tie the two lifetimes together
    tl.revert();
  };
}
```

---

## Docs vs types (4.5.0)

- `import { events } from 'animejs'` does not compile, because 4.5.0 has no `events` namespace export. Use `import { onScroll } from 'animejs'` or `'animejs/events'`.
- Draggable `releaseDamping` defaults to `20` in the source. The docs say `10`.
- Draggable `refresh()` returns `void`. The docs say it returns the draggable, so don't chain from it.
- Draggable properties: `releaseSpring` is really `releaseXSpring`/`releaseYSpring`. `pointerVelocity` and `pointerAngle` do not exist. `containerArray` is `number[] | null`, not a list of elements. `pointer` has 8 entries, not 4.
- `animateInView` and `scrollInView`: `gap` is a `number`, not a `Boolean` as the docs say, and defaults to `0`. The default ease is `inOutQuad`.
- `setX`/`setY` are typed to return `this` but return `undefined` when that axis is disabled.
- `mapTo` is documented with default `null`. The value actually used is `translateX`/`translateY`.
- The docs' callbacks overview snippet shows `containerStiffness` and `containerEase`. These are not options. The real names are `releaseStiffness` and `releaseEase`.
- Options that exist in the types but not the docs: Animatable `composition` and `on*` callbacks; Draggable per-axis `composition`; ScrollObserver `id`. `ScrollObserver.link()` also accepts a `WAAPIAnimation`.
- The 4.5.0 `.d.ts` files reference `NodeJS.Timeout` and `NodeJS.Immediate`. With `skipLibCheck: false` and no `@types/node`, `tsc` fails inside `engine.d.ts` and `text/split.d.ts`. Add `@types/node` or set `skipLibCheck: true`.

## Gotchas

- In `createAnimatable`, a root-level `duration` overrides the per-property number shorthand (checked: `{ x: 500, duration: 100 }` animates `x` over 100 ms, and `r: 0` stops being instant). Put per-property settings in object form, `x: { duration: 500 }`, which does take precedence over the root.
- A `duration` or `ease` passed to an Animatable setter stays in effect for every later call on that property.
- After `animatable.revert()`, each property method returns `undefined`, so a chain like `a.x(1).y(2)` throws. Remove your own event listeners before reverting.
- Setting a Draggable field at runtime (`dragSpeed`, `snapX`, `containerPadding`, `cursor`, `$container`, ...) is overwritten on the next `refresh()`, and a refresh runs after every container or target resize. To change a setting while it runs, give it as a function and call `refresh()`.
- `snap` only rounds the release destination. To snap while dragging, add `modifier: utils.snap(n)`.
- On `mousedown` and `touchstart`, the trigger calls `stopPropagation()`, so pointer-down listeners on ancestors never see the event. A pointer-down on an `<input type="range">` inside the trigger is ignored.
- While enabled, the trigger has an inline `touch-action`: `none` when both axes are on, `pan-x` when x is locked, and `pan-y` when y is locked. This blocks native touch scrolling that starts on the trigger.
- During a drag the trigger gets `pointer-events: none` (so the drop does not fire a click), `document.body` gets the grab cursor, and `selectstart` is cancelled. Each grab also writes a higher inline `z-index` to the target, and that value stays until `disable()` or `revert()`.
- `disable()` adds the class `is-disabled` to the target. Watch for clashes with your CSS, and for server patches that rewrite `class`.
- Without `container`, the drag has no bounds and `progressX`/`progressY` are meaningless.
- With a spring `releaseEase`, `releaseMass`, `releaseStiffness` and `releaseDamping` are ignored, and so is the spring's own `velocity`.
- `onRelease` also fires on a tap with no drag, because only the grab is checked.
- In a threshold pair string the container comes first, as in `'bottom top'`. A number on its own sets only the container side.
- `sync: 0` or `false` means no sync at all, and the linked object stays paused. For smoothing, use a value strictly between 0 and 1.
- A `sync` string that is a valid easing name switches to eased mode. `'linear'` means exact progress sync, not an ease. Any other string is split into method names, and misspelled names fail silently.
- `repeat: false` makes the observer revert itself once it completes.
- `ScrollObserver.revert()` leaves the linked animation and its inline styles in place. `animation.revert()` reverts an observer only if it came in through `autoplay`; one attached with `link()` must be reverted separately.
- The observer is set up on the next frame. Do not read `target`, `offsetStart` or `progress` synchronously after `onScroll()`.
- A container resize is picked up automatically. A target that moves without the container resizing, such as content inserted above it, needs `refresh()`.
- `debug: true` appends `div.animejs-onscroll-debug` inside the container and may set an inline `position: relative` on it. When a sticky ancestor is re-measured, it is briefly switched to `position: static`.

## Lifecycle and cleanup

These objects run inside LiveView hooks, where the server can patch or remove the elements they hold at any time. Create them in `mounted()` and tear them down in `destroyed()`. Also tear down and recreate them when a patch replaces the elements they hold. Put animated and dragged elements inside a `phx-update="ignore"` root (not on the root itself), so patches do not remove the inline `style` and `class` changes these objects make (other options: [liveview-islands.md](liveview-islands.md#what-a-liveview-patch-does-to-animejss-dom-writes)). All three register with an active `createScope()`, so `scope.revert()` tears down everything created inside it.

- **Animatable**
  - Tear down with `revert()`. It restores or removes every inline style the property animations wrote and empties `targets` and `animations`.
  - It adds no listeners or observers of its own. The pointer or scroll listeners that feed it belong to you, so remove them first.
  - There is no pause or stop method. An idle Animatable costs no frames, but it keeps references to its targets until reverted.
- **Draggable**
  - `revert()` tears down everything: listeners on the trigger and document, the ResizeObserver on the container and target, the inline `touch-action`, cursor, `pointer-events`, `z-index` and `transform` styles, the internal tickers, and the `is-disabled` class.
  - `disable()` is a softer, reversible pause. It keeps the transform and the ResizeObserver, and it adds `is-disabled`.
  - `stop()` only halts motion. `reset()` returns the target to 0,0 but leaves everything attached.
  - Document-level listeners exist only while a grab is in progress.
  - If a patch replaces the container or target, revert and create a new instance. `refresh()` re-queries a selector container, but the ResizeObserver still watches the old nodes.
- **ScrollObserver**
  - `revert()` detaches the observer and removes its debug element and debug inline style. When it is the last observer on a container, it also removes that container's scroll listener, ResizeObserver and timers and deletes the entry from `scrollContainers`.
  - It does not revert or pause the linked object. Call `linked.revert()` to remove the inline styles, or `cancel()` or `pause()` to keep the current state.
  - If `debug` is on and a patch has already removed the debug element, `revert()` throws while trying to remove it. Only use `debug` in development and inside an ignored root.
  - An observer that is never reverted keeps a scroll listener on the container, or on `window` for the default container.
- **Linked Timer, Animation or Timeline**
  - `revert()` restores inline styles and also reverts an observer passed as `autoplay`.
  - `cancel()` stops it and leaves its styles in place.
