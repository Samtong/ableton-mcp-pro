# House → Techno Arrangement — Design

## Context

The project (`face_aaaa Project`) has a Session View full of individual drum/synth
loops across 12 tracks (4 of them group/folder tracks) but almost no content in
Arrangement View. The goal is to build a full Arrangement using a classic
house→techno DJ-style structure, driven by genre convention and track roles
(inferred from track names), not by mirroring the ad-hoc scene groupings the
user had already sketched in Session View.

Tempo is 128 bpm for the House portion, stepping up to 135 bpm at the
House→Techno transition.

## Track roles (from track names / session clip inspection)

| Track | Index | Role |
|---|---|---|
| KICK | 10 | Main kick (steady 4-on-the-floor loops) |
| KICK AD | 11 | Additional/layered kick (reinforcement for techno) |
| CLAP | 5 | Clap hits |
| SNARE AD H | 6 | Snare — used for build rolls |
| CHH | 1 | Closed hi-hat |
| OHH | 3 | Open hi-hat accent (one short clip) |
| RIDE | 2 | Ride cymbal — main techno percussive element |
| SYNTH | 8 | Chords/stabs (house) + acid pedal C/G (techno bassline) |
| 0, 4, 7, 9 | — | Group/folder tracks (Hats, Snares/Claps, Synths, Kicks) — no clips of their own |

## Decisions

- **Clean slate**: delete all existing Arrangement content (the leftover
  `SYNTH` clip at 0–32 and any test locators) before building.
- **Tempo**: `Song.tempo` automation is not exposed by the Live Object Model /
  Remote Script API (verified — no `automation_envelope` accessor exists for
  Song-level tempo, only for clip/device parameters). Confirmed not worth
  building a `.als` XML-editing workaround for this. The arrangement will be
  built entirely in beats/bars, which are tempo-independent — the user will
  draw the 128→135 ramp by hand on the Master track's "Song Tempo"
  automation lane afterward.
- **Locators**: mark each section boundary with a named locator (reusing the
  `add_locator`/`get_locators`/`delete_locator` tools built earlier this
  session).
- **Source material**: existing Session clips are reused as the audio source
  for each element, but *which* clip plays *when* is chosen by genre
  convention, not by the user's original scene layout.
- **Looping**: most session clips (4–32 beats) are shorter than their target
  section length. Where Live's `create_arrangement_audio_clip` clip doesn't
  natively loop across the full section, set `looping=true` with
  `loop_start`/`loop_end` matching the source length via `set_clip_loop`,
  then rely on the clip's `length` (arrangement duration) to cover the full
  section.

## Structure (176 bars @ mixed tempo, ≈5.3 min)

| Section | Bars | Beats | Elements |
|---|---|---|---|
| House Intro | 1–16 | 0–64 | Kick solo (1–8), then Clap + CHH enter (9–16) |
| House Groove | 17–32 | 64–128 | + SYNTH chords (Giorgio Lopez sample), OHH accents |
| Transition | 33–48 | 128–192 | Strip back, SNARE AD H build (16ths), RIDE creeps in — **tempo ramp 128→135 drawn here by hand** |
| Techno Groove | 49–80 | 192–320 | KICK + RIDE + SYNTH acid pedal, sparse/hypnotic |
| Techno Build | 81–96 | 320–384 | + KICK AD, SNARE AD H build, RIDE intensifies |
| Techno Drop | 97–136 | 384–544 | Full stack: KICK + KICK AD + CLAP + RIDE + Acid + SNARE fills |
| Techno Outro | 137–176 | 544–704 | Elements drop out one by one → Kick + Ride only, DJ-friendly |

Locators are placed at each section's start beat, named per the table above.

## Out of scope

- Tempo automation curve (manual, by the user).
- New mixing/effects work beyond what's needed to place clips (no new
  device chains, no additional automation besides what's noted above).
- Preserving the user's original scene-based freeze clips (`02_H2T_intro...`
  etc.) — they are not reused as reference material for this pass.
