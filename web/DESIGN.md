# Design Language — "The Window" web experience

The page exists to do one thing: make a stranger stop scrolling, with the sound
off, and decide the music is worth turning on. Every choice below serves that.

## The governing idea

The symphony is about a window of attention: a mind kindled in darkness, blazing
through its span, closing in peace. The piano roll doesn't just *display* the
music — it **enacts the concept**:

- The viewport is a dark room. The playhead is not a line; it is a **column of
  light** — the window of the present moment.
- Notes **ahead** of the playhead are barely-there glass slivers (dim, low alpha):
  the future, unkindled.
- Notes **crossing** the playhead ignite: full brightness, soft bloom.
- Notes **behind** fade slowly over ~2.5s of scroll, like memory inside a context
  window — not gone abruptly, but cooling.

With sound off, this still reads as something alive moving through darkness.
The idle state (before first play) shows the **whole symphony at once** — an
18-minute constellation of 13,000 notes compressed into one wide strip, the
four-movement architecture legible as bands of density and color. That image is
the "convince them" moment.

## Palette

Background is a near-black room with a faint blue cast (never pure black —
this is a concert hall, not a terminal).

```
--bg          #0b0e14   (the room)
--bg-raised   #121826   (cards, control bar)
--line        #1e2638   (hairlines, piano-roll lanes)
--text        #e8e6df   (warm off-white, like house lights)
--text-dim    #8a8fa3
--gold        #d9a84e   (accent: "the Answer" — buttons, playhead core)
```

Note colors group by **orchestral family** — sixteen distinct hues would read as
confetti; families read as *choirs*. Within a family, members get shade steps.

| Family | Base hue | Members (light → dark) |
|---|---|---|
| Strings | **amber/gold** | Vln I `#ffd27a` · Vln II `#f0b75a` · Vla `#d99a43` · Vc `#b87c33` · Cb `#8f5d28` |
| Woodwinds | **aqua/teal** | Fl `#9fe8e0` · Ob `#6cd3c8` · Cl `#45b5ad` · Bsn `#2e8f8a` |
| Brass | **rose/copper** | Hn `#e8a08a` · Tpt `#f07d6a` · Tbn `#c05a50` |
| Color & pulse | **violet/ice** | Timp `#7d6aa8` · Hp `#a98fd6` · Cel `#cfd9ff` · Perc `#5d5878` |

Rationale: strings carry most notes, so they get the warm "light" family —
the roll glows gold by default, matching the gold accent. Winds cut through as
cool aqua, brass as heat, percussion/harp/celesta as night colors. At the coda,
when only celesta/harp/strings remain, the screen literally cools toward
starlight — the design ends the way the piece does.

## Typography

- Display: **Cormorant Garamond** (600) — concert-program serif, used for the
  title, movement numerals (I · II · III · IV), and section labels.
- UI: **Inter** (400/500) — controls, legend, metadata.
- Title treatment: `SYMPHONY No. 1 in C minor` small caps over a large
  italic `“The Window”`.

## Layout (mobile-first)

```
┌──────────────────────────────┐
│  title block (compact)       │  ← collapses to one line once playing
│  motto staff (SVG, G–C–Eb–D) │
├──────────────────────────────┤
│                              │
│   THE ROLL (canvas, fills    │  ← the hero; ≥55% of viewport height
│   remaining space)           │
│   section label overlay      │  ← "II · the warm branch", fades in/out
├──────────────────────────────┤
│  seek strip (full-piece      │
│  minimap with played-area)   │
│  ▶  I II III IV   03:12      │  ← control bar, thumb-reachable
│  instrument legend (chips)   │  ← horizontal scroll on mobile
└──────────────────────────────┘
```

- Time flows left → right; playhead column fixed at 38% of width.
- Pitch is vertical (C1 bottom → C8 top), with faint octave-C lane lines.
- Desktop: same structure, wider time window (~14s visible vs ~8s on mobile),
  legend always visible.

## Motion

- The roll scrolls continuously (rAF, canvas) — no jank; everything else is
  still. One moving thing in a calm frame.
- Notes ignite with a 120ms bloom when crossing the playhead (soft radial
  glow at the intersection).
- Section labels crossfade (400ms) at section boundaries.
- Idle: the constellation strip slowly breathes (opacity 0.85→1.0, 6s cycle).
  No autoplaying gimmicks.

## Interaction

- **Play** — single gold circle button; starts Movement I (or wherever seek is).
- **Movement pills** I–IV — jump between movements; auto-advance at movement end.
- **Seek strip** — the full-piece constellation doubles as the scrub bar;
  movement boundaries ticked; tap/drag anywhere.
- **Legend chips** — tap an instrument to spotlight it (its notes full
  brightness, all others drop to 25% alpha). Tap again to clear. One at a time;
  this is a lens, not a mixer.
- **Section labels** — poetic, from the program notes ("the Question, assembled",
  "the fork in the path", "the Answer"). They narrate without requiring sound.

## Score rendering (deferred, by design)

The motto staff in the header is hand-drawn SVG (five lines, four notes — the
Question) and the Answer appears beneath it when Movement IV's chorale plays.
A full engraved score (Verovio/OSMD) is heavy (+1–2MB WASM) and competes with
the roll for attention; it stays out of v1. The data pipeline already exports
everything a measure-view would need, so it can be added later without rework.

## Performance budget

- Note data: ~13k notes ≈ 350KB JSON → ~80KB gzipped. Loaded per movement.
- Audio: AAC m4a per movement (~1MB/min, ~19MB total), loaded lazily per
  movement, `preload="metadata"`.
- Canvas: only notes within the visible time window are drawn per frame;
  binary search into a time-sorted array. 60fps on a mid-range phone.
- No UI framework beyond React; no chart libs; fonts via Google Fonts with
  `display=swap`.
