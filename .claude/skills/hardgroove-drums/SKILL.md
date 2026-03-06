---
name: hardgroove-drums
description: Create hardgroove techno drum patterns. Use when the user asks for hardgroove drums, techno drums with groove, or driving techno percussion.
---

# Hardgroove Techno Drums

## Quick Reference
- **Tempo**: 140-145 BPM (142 is the sweet spot)
- **Time Signature**: 4/4
- **Feel**: Driving, groovy, layered percussion

## Drum Elements (build in this order)

### 1. Kick
- Four-on-the-floor pattern (every beat)
- Hard, punchy kick
- Duplicate the kick clip on a second track, make the hits very short (0.1 beats) — this becomes a sidechain trigger for bass and loops

### 2. Toms (the groove layer)
- Pitched-down toms that groove over the bassline
- Create a syncopated pattern that fits between kicks
- Pitch down from default (-3 to -7 semitones)
- Tune toms in musical intervals relative to each other — perfect 4ths or 5ths work well (e.g., if one tom sits at F, place the second at Bb or C). This gives the tom pattern a melodic quality that interlocks with the bassline rather than clashing
- High-pass filter to keep out of the kick's frequency range
- Convert to mono
- Layer an acoustic percussion sample (conga, bongo, or djembe hit) underneath the electronic tom — blend at ~20-30% to add organic texture without losing the electronic punch
- This is the signature hardgroove element — the toms create the "groove" in hardgroove

### 3. Hi-Hats
- Layer TWO hi-hat sources:
  - **Programmed**: Tight, punchy closed hat — straight 16th notes for drive
  - **Loop**: A second hi-hat loop layered on top for organic groove and swing
- The combination of programmed + loop hats creates the characteristic groove feel
- **Choke groups**: Put open and closed hats in the same choke group so the closed hat cuts off the open hat's tail — this replicates how a real hi-hat behaves and is essential for groove. In Drum Rack, go to the I/O section and assign both pads to the same Choke group. Vary where the closed hat chops the open hat to create rhythmic interest
- **Velocity for drive**: Set on-beat hat hits (landing with the kick) to *lower* velocity and off-beat hits to *higher* velocity — this creates a pushing, driving feel. The quieter on-beat hats recede behind the kick while the louder off-beat hits pull the listener forward

### 4. Claps
- Layer TWO clap sources:
  - **Programmed**: Clap on beats 2 and 4
  - **Loop**: A clap/snap loop for extra groove between the main hits
- Keep clap loops short and punchy

## MIDI Pattern (4-bar, 16th note grid)

Kick (note 36): Beats 1, 2, 3, 4 every bar — velocity 100-127
Toms (note 41-43): Syncopated — hit on offbeats and &'s, velocity 80-110
Closed Hat (note 42): Every 16th note, velocity alternating 70/90/70/90
Clap (note 39): Beats 2 and 4, velocity 100

## Pattern Variations (2 bars each)

### Variation 1 — Driving (straight toms)

```
Beat:  1 . . . 2 . . . 3 . . . 4 . . . 1 . . . 2 . . . 3 . . . 4 . . .
Kick:  X . . . X . . . X . . . X . . . X . . . X . . . X . . . X . . .
Tom:   . . X . . . X . . . X . . . X . . . X . . . X . . . X . . . X .
Hat:   x x x x x x x x x x x x x x x x x x x x x x x x x x x x x x x x
Clap:  . . . . X . . . . . . . X . . . . . . . X . . . . . . . X . . .
```

Relentless straight tom hits on every "and" create a steamroller effect. The toms lock in a constant call-and-response with the kick.

### Variation 2 — Syncopated (swung toms)

```
Beat:  1 . . . 2 . . . 3 . . . 4 . . . 1 . . . 2 . . . 3 . . . 4 . . .
Kick:  X . . . X . . . X . . . X . . . X . . . X . . . X . . . X . . .
Tom:   . X . . . . . X . . X . . X . . . . X . . . . X . X . . . . X .
Hat:   x x x x x x x x x x O x x x x x x x x x x x x x x x O x x x x x
Clap:  . . . . X . . . . . . . X . . . . . . . X . . . . . . . X . . .
```

Toms land on "e" and "uh" positions for a lopsided, swinging groove. The open hat (O) on the "and" of beat 3 adds a breathing point in the pattern.

### Variation 3 — Minimal (stripped back)

```
Beat:  1 . . . 2 . . . 3 . . . 4 . . . 1 . . . 2 . . . 3 . . . 4 . . .
Kick:  X . . . X . . . X . . . X . . . X . . . X . . . X . . . X . . .
Tom:   . . . . . . . . . . X . . . . . . . . . . . . . . . . X . . . .
Hat:   x . x . x . x . x . x . x . x . x . x . x . x . x . x . x . x .
Clap:  . . . . X . . . . . . . X . . . . . . . X . . . . . . . X . . .
```

A single unexpected tom hit per bar (the "and" of 3 in bar 1, the "uh" of 3 in bar 2) keeps the groove hypnotic. Hats on 8th notes only — use this variation for breakdowns or intros where space matters.

## Mixing
- Kick loudest, everything else sits below
- Toms: filtered, mono, tucked under the kick
- Hats: panned slightly for width, not too loud
- Keep total level below clipping — turn things down as you layer
- **Parallel compression on the drum bus**: Send all drum tracks to a return track with a compressor set to fast attack (~1ms), fast release (~30ms), high ratio (8:1 or above), and threshold pulled way down so it's slamming hard. Blend this crushed signal at 30-50% alongside the dry drums — this adds density and sustain to the groove without killing the transients on the main bus
- **Transient shaping**: Add a transient shaper (or Drum Buss in Ableton) on the drum bus. Boost attack slightly and reduce sustain to tighten hits and keep the rhythm snappy. Focus the effect in the 2-5kHz range where the "click" and "snap" of percussion lives

## Production Notes
- The groove comes from layering — programmed patterns + loops together
- Don't just use loops alone. The foundation (kick + programmed hats + claps) must groove on its own first
- Sidechain everything to the kick trigger track
- **Micro-shift notes off-grid**: For percussion and tom hits, try nudging individual notes slightly before the grid line (turn off snap, then drag). Notes that land just ahead of the beat create an urgent, pushing feel that accentuates syncopation. This is subtle — a few ticks is enough. Don't shift the kick; keep it locked to the grid as the anchor
