---
name: trance-bass
description: Create trance basslines. Use when the user asks for trance bass, offbeat bass, trance 16th note bass, or pumping trance bassline.
---

# Trance Basslines — The 3 Essential Types

## Sound Design
- Saw waves + square waves with some FM
- Short punchy filter envelope: low sustain, low decay
  - Filter cutoff envelope is the main shaping tool — fast attack (0-5 ms), decay 80-200 ms, low sustain (10-25%), zero release
  - Sweep range matters: set the envelope amount so the filter opens to the mid-range but not higher — too much sounds thin, too little sounds dull
  - Resonance adds bite at the transient — a small bump (15-30%) gives each note an aggressive click without whistling
- Don't try to perfect the sound in isolation — dial it in against the kick and drums
- The patch will sound small on its own; it comes alive in context

### Bass Layering (Sub + Mid)
- For a fatter sound, split the bass into two layers on separate tracks:
  - **Sub layer**: pure sine or triangle, no filter movement, just solid low end (below ~120 Hz)
  - **Mid layer**: saw/square with the filter envelope and all the movement — this carries the rhythm and texture
- High-pass the mid layer around 100-120 Hz so it doesn't clash with the sub
- Low-pass the sub layer around 120-150 Hz to keep it clean
- This gives you independent control — you can sidechain the mid layer hard while keeping the sub steadier
- Not always necessary: a single bass patch works fine for most tracks, but layering helps when the mix needs both deep weight and rhythmic bite

## Type 1: Offbeat Bass (most human, most danceable)
- Notes on the **upbeats only** (between kicks)
- Fills the space between kicks

```
Beat:  1  .  .  .  2  .  .  .  3  .  .  .  4  .  .  .
Kick:  X  .  .  .  X  .  .  .  X  .  .  .  X  .  .  .
Bass:  .  .  X  .  .  .  X  .  .  .  X  .  .  .  X  .
```

### Note Length is Critical
- Changing note length dramatically changes the groove and texture
- Shorter notes = more percussive, punchy
- Longer notes = more sub, fuller sound
- Note length also affects how much sub bass you get — longer = more sub
- Experiment with length to find the right groove for your track

- This type feels the most natural and danceable

## Type 2: Filled 16ths (busier, driving)
- Fill every 16th note after the kick
- Sidechain is **essential** — without it the groove falls apart

```
Beat:  1  .  .  .  2  .  .  .  3  .  .  .  4  .  .  .
Kick:  X  .  .  .  X  .  .  .  X  .  .  .  X  .  .  .
Bass:  .  X  X  X  .  X  X  X  .  X  X  X  .  X  X  X
```

### Key Details
- Use slightly longer notes than Type 1 (very short notes lose bass at this speed)
- Sidechain compression creates the pumping groove
- The groove comes equally from sidechain as from the notes themselves
- The sidechain release curve shapes the feel: a more logarithmic (gradual) release gives a chewy, smooth pump; a more exponential (sharp) release makes the kick punch a hole that snaps back quickly

## Type 3: Octave Jump 16ths (most energy, most fun)
- Straight 16th notes across the whole bar
- Alternate notes up an octave for energy

```
Beat:  1  .  .  .  2  .  .  .  3  .  .  .  4  .  .  .
Note:  F1 F2 F1 F2 F1 F2 F1 F2 F1 F2 F1 F2 F1 F2 F1 F2
```

### Variations
- Change WHICH note jumps up for different grooves:
  - Every other note up (classic)
  - First and third up, second and fourth down
  - Groups of two up, two down
- Each variation creates a completely different groove from the same technique

- This type has the most energy and drive

## Sidechain Compression Settings
- Triggered by the kick — the bass ducks on every kick hit and swells back up
- **Fast attack** (0-1 ms) so the duck is immediate
- **Release** is the most important parameter — time it to the tempo so the bass swells back just before the next event
  - At 138 BPM, a 16th note is ~109 ms — set release so the bass is fully back by then
  - Shorter release = more of the bass is audible, less dramatic pump
  - Longer release = deeper pump, more dramatic, but can thin out the bass
- **Ratio**: 4:1 to 10:1 — higher ratios give a more obvious pumping effect
- **Threshold**: set so you get 6-12 dB of gain reduction on each kick hit
- You can also use a volume-shaping plugin (like LFOTool or Kickstart) instead of a compressor — draw the exact ducking curve you want, which gives tighter control than a compressor

## General Rules
- **Note length controls the groove** — more than note choice in many cases
- **Sidechain is mandatory** for Types 2 and 3
- **Dial in the sound against the kick**, not in isolation
- Choose the bassline type based on the emotion you want:
  - Type 1 = human, emotional, danceable
  - Type 2 = driving, energetic
  - Type 3 = maximum energy, fun
- **Vary the pattern across sections** — use Type 1 (offbeat) in the breakdown for a spacious feel, then switch to Type 2 or 3 when the track builds back up for a burst of energy
