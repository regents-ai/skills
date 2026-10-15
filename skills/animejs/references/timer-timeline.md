# Anime.js v4: Timer and Timeline

Reference for `createTimer()` and `createTimeline()` in `animejs` 4.5.0. A **Timer** is a clock with no targets: it counts time on the Anime.js engine and fires callbacks, and it replaces `setTimeout`/`setInterval` when the work has to stay in step with animations (pausing, speed, fps and seeking all apply). A **Timeline** is a Timer with children: animations, timers, synced objects (JS animations, WAAPI animations, native `Animation`s, other timelines), function calls and labels, each placed at a time position. Every API on these pages is "Since 4.0.0" or older, so nothing here needs a newer minor. Where the docs and `dist/modules/**/*.d.ts` disagree, this file follows the types and says so. Behaviour notes marked *(source)* were read from the 4.5.0 runtime or confirmed by running it.

Imports: `import { createTimer, createTimeline } from 'animejs'`, or the subpaths `'animejs/timer'` and `'animejs/timeline'`. Types: `Timer`, `Timeline`, `TimerParams`, `TimelineParams`, `TimelinePosition`, `DefaultsParams` are all exported from `'animejs'`.

Signatures (from the types):

```
createTimer(parameters?: TimerParams): Timer
createTimeline(parameters?: TimelineParams): Timeline      // Timeline extends Timer
TimerParams    = TimerOptions & TickableCallbacks<Timer>
TimelineParams = TimerOptions & { defaults?, playbackEase?, composition? } & TickableCallbacks<Timeline> & { onRender? }
Callback<T>    = (self: T) => any
```

---

## Timer `timer`

`createTimer(params)` builds the timer and calls `init()` on it, so it starts on the next engine frame unless `autoplay: false`.

### Timer playback settings `timer/timer-playback-settings`

Every default except `duration` can be changed for the whole page with `engine.defaults.<name>`. A timer inside a timeline reads these defaults from the timeline's `defaults` instead *(source)*.

| Name | Type | Default | Meaning |
| --- | --- | --- | --- |
| `delay` | `number` ≥ 0 | `0` | ms to wait before the timer starts. |
| `duration` | `number` ≥ 0 | `Infinity` | ms for one iteration. `0` completes the timer as soon as it plays. Values above `1e12` are clamped to `1e12`. Not taken from `engine.defaults.duration` or from timeline `defaults.duration` *(source)*. |
| `loop` | `number \| boolean` | `0` | How many extra times it repeats. `true`, `Infinity` or `-1` (any negative) mean forever. Total iterations = `loop + 1`. |
| `loopDelay` | `number` ≥ 0 | `0` | ms of pause between iterations. |
| `alternate` | `boolean` | `false` | Reverse the direction on every iteration. Only has an effect when there is more than one iteration. |
| `reversed` | `boolean` | `false` | Run the first iteration backwards. Only the iteration time runs backwards; `currentTime` still goes from 0 to `duration`. |
| `autoplay` | `boolean \| ScrollObserver` | `true` | `false` means the timer waits for `play()`. An `onScroll({...})` instance starts it when the scroll thresholds are met. Always forced to `false` for timeline children. |
| `frameRate` | `number` > 0 | `240` | Maximum fps for updates. The display refresh rate (or the browser) caps it. You can change it later through `.fps`. |
| `playbackRate` | `number` ≥ 0 | `1` | Speed multiplier. `0` freezes the timer. You can change it later through `.speed`. |
| `id` | `string \| number` | auto-increment | Only in the types (`TimerOptions`); the docs list `id` as a property only. |
| `priority` | `number` | `1` | Only in the types. Sets the engine's tick order: a lower number ticks earlier *(source)*. |

### Timer callbacks `timer/timer-callbacks`

Every callback has type `(self: Timer) => any` and defaults to a no-op. You can set any of them globally through `engine.defaults.<name>`.

| Name | Fires |
| --- | --- |
| `onBegin` | Once, when the playhead first passes the `delay`. |
| `onComplete` | When every iteration has finished. |
| `onUpdate` | On every frame while running, at the `frameRate`. |
| `onLoop` | Each time an iteration ends. |
| `onPause` | When a running timer pauses (through `pause()`, `cancel()` or `revert()`). |
| `onBeforeUpdate` | Every frame, before the update. It is in the types and the runtime for timers, but the docs cover it only for timelines. |
| `then(callback?)` | Method, not an option. Returns a `Promise` that resolves on completion and then runs `callback(self)`. It resolves immediately if the timer has already completed. Typed as `Promise<any>`. |

```ts
export async function timerBasic(): Promise<void> {
  const t: Timer = createTimer({
    duration: 1000,
    loop: 2,
    frameRate: 30,
    onUpdate: self => { out.textContent = String(self.iterationCurrentTime); },
    onLoop: self => console.log('iteration', self.currentIteration),
  });
  await t.then();      // resolves on completion; never if cancelled first
  t.speed = 0.5;       // same as playbackRate
  t.fps = 60;          // same as frameRate
}

export function engineDefaults(): void {
  engine.defaults.frameRate = 60;
  engine.defaults.autoplay = false;
}
```

### Timer methods `timer/timer-methods`

Every method returns the timer itself (`this`), so calls can be chained.

| Method | Meaning |
| --- | --- |
| `play()` | Play forwards. If the timer is reversed, it flips the direction first. |
| `reverse()` | Play backwards. |
| `pause()` | Pause and fire `onPause`. Does nothing if already paused. |
| `resume()` | Continue in the current direction. |
| `restart()` | `reset()` then `resume()`. |
| `alternate()` | Flip the direction but keep the same visual position, by mirroring `currentTime`. |
| `complete(muteCallbacks?: boolean \| number)` | Jump to the end and then `cancel()` *(source)*. The parameter is only in the types. |
| `reset(softReset = false)` | Pause and set `currentTime`, `progress`, `reversed`, `began` and `completed` back to their defaults. With `softReset: true` it resets the values without rendering. Since 3.0.0. |
| `cancel()` | Pause, take the timer off the engine loop and free its memory. A later `play()`/`seek()` revives it. |
| `revert()` | Render time 0 with callbacks muted, revert a linked `onScroll()` observer, then `cancel()`. |
| `seek(time, muteCallbacks = false, internalRender?)` | Move `currentTime` to `time` ms (the delay is not counted). A timer that was running keeps running. `internalRender` is only in the types. |
| `stretch(newDuration)` | Set the total duration, which covers all iterations (1000 ms × 3 iterations = 3000). Iteration length, `delay` and `loopDelay` scale by the same factor *(source)*. |
| `init(internalRender?)` | Only in the types for Timer. `createTimer` already calls it. |

### Timer properties `timer/timer-properties`

| Name | Type | Access | Meaning |
| --- | --- | --- | --- |
| `id` | `string \| number` | rw | Identifier. |
| `deltaTime` | `number` | r | ms between the previous frame and this one. |
| `currentTime` | `number` | rw | Overall time in ms, clamped to `[-delay, duration]`. Setting it pauses, seeks, then resumes if the timer was running. |
| `iterationCurrentTime` | `number` | rw | ms inside the current iteration. |
| `progress` | `number` | rw | Overall progress, from 0 to 1. |
| `iterationProgress` | `number` | rw | Progress of the current iteration, from 0 to 1. |
| `currentIteration` | `number` | rw | Index of the current iteration. The setter clamps it to `[0, iterationCount-1]`. |
| `speed` | `number` | rw | The live `playbackRate`. |
| `fps` | `number` | rw | The live `frameRate`. |
| `paused` | `boolean` | rw | A plain flag. Setting it does not call `pause()`/`resume()` and does not fire `onPause`. |
| `began` | `boolean` | rw | A plain flag. |
| `completed` | `boolean` | rw | A plain flag. |
| `reversed` | `boolean` | rw | Setting it calls `reverse()` or `play()`, so it **starts playback** *(source)*. |
| `backwards` | `boolean` | r (typed rw) | True while currently moving backwards. |
| `duration` | `number` | r | Total ms including every iteration and loop delay. It is in the types but missing from the docs table. |
| `iterationDuration`, `iterationCount`, `parent`, `cancelled` | | | Only in the types. `cancelled = true` calls `cancel()`; `cancelled = false` calls `reset(true).play()`. |

---

## Timeline `timeline`

`createTimeline(params)` returns a `Timeline`, and each builder method returns `this`. The timeline's `duration` starts at 0 and grows as children are added. A `duration` option is accepted by the type but ignored *(source)*.

### Add timers `timeline/add-timers`

- `tl.add(timerParams: TimerParams, position?: TimelinePosition)` creates a child timer. Its `autoplay` is ignored.
- `tl.sync(existingTimer, position?)` adopts a timer you already made (see `sync()` below).
- Give every child timer a `duration`. Without one it is `Infinity`, and the whole timeline becomes about 1e12 ms long *(source)*.

### Add animations `timeline/add-animations`

- `tl.add(targets, animationParams, position?)` creates a child JS animation. Because it is built inside the timeline, its tween values compose with the children already there (a `from` value can pick up where an earlier child left off). Accepts every animation property, tween parameter, playback setting and callback. Since 2.0.0.
- `tl.sync(animate(...), position?)` adopts an existing animation. Its composition was worked out when it was created, so it does not affect the timeline's other children.

### Sync WAAPI animations `timeline/sync-waapi-animations`

- `tl.sync(waapi.animate(...), position?)` or `tl.sync(element.animate(...), position?)`.
- `sync()` sets `persist = true` on Anime.js `WAAPIAnimation`s so they keep responding after they finish *(source)*.
- For a native `Animation`, the length comes from `effect.getTiming().duration`: one iteration, with the WAAPI delay not counted *(source)*.

### Sync timelines `timeline/sync-timelines`

- `tlA.sync(tlB, position?)` nests one timeline inside another. `tlB` is paused and driven by `tlA`.

### Call functions `timeline/call-functions`

- `tl.call(callback, position?)` runs `callback` at that time. It is a zero-length child timer whose `onComplete` calls `callback(timeline)` *(source)*.
- It fires whenever the playhead crosses that time, **forwards or backwards**. It is skipped by `seek(t, true)` *(source)*.

### Time position `timeline/time-position`

The time position is the last argument of `add`, `set`, `sync`, `call` and `label`. Type: `TimelinePosition = number | '+=N' | '-=N' | '*=N' | '<' | '<<' | '<<+=N' | '<<-=N' | string`. For `add(targets, params, pos)` and `set()` it can also be a `stagger(...)` function (`TimelineAnimationPosition`). The rules below come from `timeline/position.js`. "Timeline end" means the current `iterationDuration`: the furthest end of any child added so far.

| Form | Example | Resolves to |
| --- | --- | --- |
| omitted | | Timeline end (the child is appended). |
| absolute | `500`, `'500'` | Exactly that ms. Numeric strings also count as absolute. |
| add | `'+=100'` | Timeline end + 100. The docs say "after the last element", but this means the furthest end, not the most recently added child. |
| subtract | `'-=100'` | Timeline end − 100 (overlap). |
| multiply | `'*=.5'` | Timeline end × 0.5. |
| previous end | `'<'` | End of the most recently added child. **Throws a TypeError on an empty timeline.** |
| previous start | `'<<'` | Start (offset + delay) of the most recently added child. Resolves to 0 on an empty timeline. |
| combined | `'<+=50'`, `'<-=500'`, `'<<+=250'`, `'<<-=100'` | Previous end or start ± N. |
| label | `'intro'` | The label's ms. **An unknown label silently becomes the timeline end.** |
| label + operator | `'intro+=250'`, `'intro-=100'`, `'intro*=2'` | The label's ms, then the operator. **With an unknown label the result is `NaN`**, and the child is lost without any error. |
| stagger | `stagger(50)`, `stagger(50, { start: 'intro' })` | Splits the targets into one child per target, each placed at `start + i*50`. `start` accepts any form above and defaults to the timeline end. When the params have an `id`, the child ids become `id-0`, `id-1`, and so on. |

Labels and `'<'`/`'<<'` are read at the moment of the call, so the order of the chain matters. A label is not a child, so `'<'` right after `.label()` still points at the last real child.

```ts
export function positions(): Timeline {
  return createTimeline({ defaults: { duration: 500, ease: 'out(3)' } })
    .label('intro')                              // at current end (0)
    .add(el, { opacity: [0, 1] })                // appended: 0-500
    .add(el, { x: 100 }, '-=200')                // 200ms before timeline end
    .add(el, { y: 50 }, '<<')                    // same start as previous child
    .add(el, { scale: 1.2 }, '<<+=100')          // 100ms after previous start
    .add(el, { rotate: 90 }, 'intro+=250')       // label plus offset
    .add(items, { y: -10 }, stagger(50, { start: '<' })) // one child per item
    .call(() => console.log('halfway'), '*=.5')
    .label('outro', 1200);
}
```

### Timeline playback settings `timeline/timeline-playback-settings`

| Name | Type | Default | Since | Meaning |
| --- | --- | --- | --- | --- |
| `defaults` | `DefaultsParams` | engine defaults | 2.0.0 | Defaults for children: tween parameters (except `from`/`to`), playback settings and callbacks. Merged over `engine.defaults`. Child timers take `delay`, `loop`, `loopDelay`, `reversed`, `alternate`, `frameRate`, `playbackRate` and the callbacks from here, but not `duration` *(source)*. |
| `delay` | `number` ≥ 0 | `0` | 2.0.0 | ms before the timeline starts. This also delays `onBegin`. |
| `loop` | `number \| boolean` | `0` | 2.0.0 | Same as for Timer (`true`, `Infinity` or negative = forever). |
| `loopDelay` | `number` ≥ 0 | `0` | 4.0.0 | ms between iterations. |
| `alternate` | `boolean` | `false` | 4.0.0 | Flip direction on each iteration. |
| `reversed` | `boolean` | `false` | 4.0.0 | Start playing backwards. |
| `autoplay` | `boolean \| ScrollObserver` | `true` | 2.0.0 | `false` means it waits for `play()`. `onScroll()` ties playback to scroll. |
| `frameRate` | `number` > 0 | `240` | 4.0.0 | fps cap. You can change it later through `.fps`. |
| `playbackRate` | `number` ≥ 0 | `1` | 4.0.0 | Speed multiplier (0 freezes it). You can change it later through `.speed`. |
| `playbackEase` | `EasingParam` | `null` | 4.0.0 | An easing applied to the timeline's overall progress, on top of each child's own `ease`. |
| `composition` | `boolean` | `true` | only in the types | Not documented. When true, each `add()` pre-renders the timeline at the new child's time so its values compose with the earlier children *(source)*. |
| `id`, `priority` | | | only in the types | Same as for Timer. |

### Timeline callbacks `timeline/timeline-callbacks`

Every callback has type `(self: Timeline) => any`, defaults to a no-op and can be set globally through `engine.defaults`. All of them are Since 4.0.0.

| Name | Fires |
| --- | --- |
| `onBegin` | When the timeline starts, after its `delay`. |
| `onComplete` | When every iteration has finished. |
| `onBeforeUpdate` | Every frame, before the children's values are updated. |
| `onUpdate` | Every running frame, at the `frameRate`. |
| `onRender` | Only on frames where something is actually drawn. Not during `delay`/`loopDelay`, and not when no child renders. |
| `onLoop` | At the end of each iteration. |
| `onPause` | On `pause()`, `cancel()` or `revert()`. Also fires on its own when every child tween is overridden by another animation with `composition: 'replace'`, or when every target is removed and no timers are left. (The docs call the argument "the animation"; it is the timeline.) |
| `then(callback?)` | Method. Returns a `Promise` that resolves on completion (see Timer). |

### Timeline methods `timeline/timeline-methods`

Every method returns `this`.

| Method | Since | Meaning |
| --- | --- | --- |
| `add(targets, params, position?)` / `add(timerParams, position?)` | 2.0.0 | Create a child animation or a child timer (see above). If neither the first nor the second argument is an object, it returns `undefined` *(source)*. |
| `set(targets, params, position?)` | 4.0.0 | Change property values instantly at that time. Internally it is an `add()` with `duration: 1e-11` and `composition: 'replace'`, and it **writes those two keys into the object you pass** *(source)*. |
| `sync(synced?, position?)` | 4.0.0 | Adopt a `JSAnimation`, `Timer`, `Timeline`, Anime.js `WAAPIAnimation` or native `Animation`. The object is paused and a hidden linear child drives its `currentTime` from 0 to its duration *(source)*. |
| `label(name: string, position?)` | 4.0.0 | Store `labels[name]` as a resolved ms value. If `position` is left out, it uses the timeline end. |
| `remove(targets, propertyName?)` | 4.0.0 | Three forms: `remove(animOrTimerOrTimeline)`, `remove(targets)`, `remove(targets, 'prop')`. It removes tweens, and removes children that end up empty. The timeline pauses once nothing is left. `duration` is not recomputed; to change the shape, build a new timeline. |
| `call(callback, position?)` | 4.0.0 | Run a function at that time (see above). |
| `init()` | 4.0.0 | Render every child's starting state now. Children with explicit `from` values otherwise only apply them when the playhead reaches them. |
| `play()` | 2.0.0 | Play forwards. |
| `reset(softReset = false)` | 3.0.0 | Same as for Timer, and it also resets the children's flags. |
| `reverse()` | 4.0.0 | Play backwards. |
| `pause()` | 2.0.0 | Pause. |
| `restart()` | 2.0.0 | Go back to 0, reset the children's values, and play. |
| `alternate()` | 2.0.0 | Flip the direction and keep the visual position. |
| `resume()` | 2.0.0 | Continue in the current direction. |
| `complete()` | 4.0.0 | Jump to the end, then cancel. |
| `cancel()` | 4.0.0 | Pause, cancel every child, and leave the engine loop. |
| `revert()` | 4.0.0 | Cancel, put the children's animated values back to how they were before, clean up the inline styles, and revert a linked `onScroll()`. |
| `seek(time, muteCallbacks = false)` | 2.0.0 | Move `currentTime`. |
| `stretch(newDuration)` | 4.0.0 | Scale the total duration. Children durations and **label times** are scaled too. |
| `refresh()` | 4.0.0 | Re-run the function-based values of the children: each `from` becomes the current value and each `to` becomes the new result. `duration`/`delay` are not recomputed. Useful inside `onLoop`. |

```ts
export function syncAll(): Timeline {
  const js = animate(el, { x: 200, autoplay: false });
  const wa = waapi.animate(el, { opacity: [1, 0.5], duration: 400 });
  const native: Animation = el.animate([{ color: 'red' }, { color: 'blue' }], { duration: 300 });
  const child = createTimeline().add(el, { y: 20 });
  const pos: TimelinePosition = 'intro';
  return createTimeline()
    .label('intro', 0)
    .sync(js, pos)
    .sync(wa, '<<')
    .sync(native, 100)
    .sync(child, '+=0');
}

export function setInitRemove(): Timeline {
  const tl = createTimeline({ autoplay: false })
    .set(el, { opacity: 0 }, 0)
    .add(el, { x: { from: 120 } }, 100)
    .add({ duration: 800, onUpdate: self => { out.textContent = String(self.progress); } }, 0)
    .init();                         // render every child's start state now
  tl.remove(el, 'x');                 // drop only the x tween
  return tl;
}

export function scrollAutoplay(): Timeline {
  return createTimeline({ autoplay: onScroll({ target: el }) })
    .add(el, { x: 100 });
}
```

### Timeline properties `timeline/timeline-properties`

These are the Timer properties plus the following:

| Name | Type | Access | Meaning |
| --- | --- | --- | --- |
| `labels` | `Record<string, number>` | rw | Label name → ms. `stretch()` scales these values. |
| `duration` | `number` | r | Total ms including loops. Grows with each `add`/`sync`/`call`. |
| `defaults` | `DefaultsParams` | rw | The merged child defaults. Only in the types. |
| `composition` | `boolean` | rw | Only in the types (see settings). |
| `onRender` | `Callback<Timeline>` | rw | Only in the types, as a property. |

---

## Docs vs types (4.5.0)

- Timer `onBeforeUpdate`, and the `id` and `priority` settings, are in `TimerParams` but not on the timer pages.
- The Timeline `composition?: boolean` option is only in the types.
- `complete(muteCallbacks?)` and the third `seek` parameter `internalRender` are only in the types.
- The docs show an optional `position` argument when removing objects. The type is `remove(targets: TargetsParam, propertyName?: string)`, with no position. Animations, timers and timelines are accepted as plain targets.
- `call()` is typed `Callback<Timer>`, but the runtime passes the timeline.
- `then()` is typed `Promise<any>`, although the JSDoc says `Promise<this>`.
- Timer `duration`/`delay` are typed `TweenParamValue` (functions allowed). For timers and timelines the runtime ignores function values: `duration` becomes `Infinity` and `delay` falls back to the default.
- `TimelineParams` accepts `duration`, but the timeline ignores it.
- `backwards` is typed as writable; the docs say it is read-only. The Timer `duration` property exists but is left out of the docs table. `Timer.init()` and `resetTime()` are public in the types but not documented for Timer.
- The time-position page lists `timeline.sync(labelName, position)`. That is a docs typo: the first argument is the object to sync.
- The docs say `restart()` only plays when `autoplay` is true. The 4.5.0 runtime always resumes (docs vs runtime, not types).
- The `.d.ts` files reference `NodeJS.Immediate`/`NodeJS.Timeout` (`engine.d.ts`, `text/split.d.ts`). With `skipLibCheck: false`, `tsc` fails unless `@types/node` is installed.

## Gotchas

- `'+='`, `'-='` and `'*='` are measured from the furthest child end, not from the most recently added child. Use `'<'` / `'<<'` when you mean "relative to the one just added".
- `'<'` on an empty timeline throws. `'<<'` resolves to 0 there.
- A misspelled label with no operator silently appends at the timeline end. With an operator (`'lbl+=100'`) it becomes `NaN` and the child never plays. Nothing warns you in either case.
- A timer added to a timeline without a `duration` lasts forever, so the timeline never completes and `then()` never resolves.
- Timeline `defaults` callbacks (`onUpdate` and the rest) also apply to child timers and animations. Each child calls them with itself as the argument, not the timeline.
- `set()` changes the params object you pass (it adds `duration` and `composition`). Do not reuse that object for a later `add()`.
- A child with explicit `from` values keeps its current look until the playhead reaches it. Call `init()` if the starting state should show at once (for example, hidden before a reveal).
- `remove()` does not shorten `duration`, so removing some children leaves gaps. Removing every child cancels the timeline.
- `call()` callbacks run when scrubbing or reversing backwards across them, too. Make them idempotent, or check `self.backwards`.
- `complete()` also cancels. Call `play()`/`restart()` to run it again.
- A `then()` promise never resolves if the object is cancelled or reverted first. An `await` on it hangs forever.
- Timers and timelines are thenables. Returning one from an `async` function, or `await`ing it, waits for completion rather than handing back the object.
- Setting `reversed` starts playback. Setting `paused`, `began` or `completed` only flips a flag and does not stop the engine; use `pause()` / `resume()`.
- `frameRate` can only lower the update rate. It never goes above the display refresh rate.
- A `sync()`ed native `Animation` with several iterations or a WAAPI delay is placed using the length of one iteration only.
- `stretch()` on a Timer scales its `delay` and `loopDelay` as well as its duration.

## Lifecycle and cleanup

In a LiveView hook, create these objects in `mounted()` and dispose of them in `destroyed()`. Before replacing them in `updated()`, dispose of the old ones first. The server can remove or re-patch the element at any moment, and an animation left running keeps references to detached nodes and keeps writing inline styles onto whatever node it still holds.

- **Timer**
  - `pause()` stops it but keeps it resumable.
  - `cancel()` stops it and takes it off the engine loop. Use this in `destroyed()`.
  - `revert()` does what `cancel()` does, and first renders time 0 with callbacks muted and reverts a linked `onScroll()` observer.
  - A Timer writes nothing to the DOM itself. Only your callbacks do, so undo what they wrote yourself.
  - It leaves no listeners or observers behind, except an `autoplay: onScroll()` observer, which stays linked and registered with its scroll container after `cancel()`. Use `revert()` when `autoplay` is an `onScroll()`.
- **Timeline**
  - `revert()` is the full teardown. It cancels every child, removes the linked `onScroll()` observer, and puts back each `add()`/`set()` child's inline style, attribute and transform values exactly as they were before the timeline touched them. An inline property that did not exist is removed, and an empty `style=""` attribute is removed too.
  - `cancel()` stops it without restoring anything, so the inline styles stay.
  - Objects adopted with `sync()` are only rewound to their starting time. Their own inline styles stay, and the 4.5.0 `revert()` does not call their `revert()`. Revert each synced animation or timeline yourself, or create them all inside one `createScope()` and call `scope.revert()`.
  - It creates no listeners of its own, and never splits the DOM.
- **"Before" means before creation.** Inline values are captured when each child is created. If LiveView patches the element's `style` attribute afterwards, `revert()` restores the older value. Mark animated nodes `phx-update="ignore"`, or animate a wrapper the server does not patch, and rebuild the timeline after a patch instead of reusing it.
- **Scope.** Timers and timelines, including every child, register with the active `createScope()` when they are created. A single `scope.revert()` in `destroyed()` covers all of them.

```ts
export function hookLike(root: HTMLElement): () => void {
  const tl = createTimeline({ loop: true }).add(root, { opacity: [0.4, 1] });
  const tick = createTimer({ duration: 2000, loop: true, onLoop: () => tl.refresh() });
  return () => {
    tick.cancel();   // stops callbacks, frees the engine slot
    tl.revert();     // restores inline styles captured before animating
  };
}
```
