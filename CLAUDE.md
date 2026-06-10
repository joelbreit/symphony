# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

This is a creative composition project, not a software application. The task, defined in `goal.md`, is to compose an original symphony as a playable music document — MIDI, MusicXML, ABC notation, or whatever format best serves the work. Claude is the composer.

There is no build system, linter, or test suite. If you introduce tooling (e.g. Python with music21/mido for MIDI generation, or a verovio/abcjs rendering step), document the exact commands here so future sessions can regenerate and verify the output.

## Working process (from goal.md)

1. **Find inspiration first** — settle on a concrete idea or image to anchor the piece before writing notes.
2. **Explore** music theory and practical knowledge for translating that idea into written, playable music.
3. **Plan a scaffolding** for the overall structure: movements, emotional arc, key moments and effects, and any tools needed.
4. **Build it** — melodies, chord progressions, full instrumentation.
5. **Self-assess** — compare the output against what a real, meaningful symphony sounds like, and go up a meta level when the usual LLM output patterns fall short.

## Constraints and conventions

- Target at least a couple of minutes of music; ~15 minutes is the ambition.
- Use symphonic orchestration (full orchestra), not a solo or small-ensemble texture.
- Use files to think: planning and theory notes go in `docs/`; create additional folders (e.g. for scores, generation scripts, rendered audio) as the work demands.
- The final deliverable must be *playable* — verify that generated files actually open and play correctly, don't just emit notation text.
