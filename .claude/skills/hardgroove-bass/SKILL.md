---
name: hardgroove-bass
description: Create hardgroove techno basslines. Use when the user asks for hardgroove bass, techno bassline, or driving techno bass.
---

# Hardgroove Techno Bass

## Quick Reference
- **Tempo**: 140-145 BPM
- **Character**: Heavy, simple, driving
- **Key**: Keep it minimal — 2-3 notes max

## Sound Design
- Start with a **square wave** (or saw pushed past square for fatness)
- For more aggressive tones, try **FM synthesis**: In Operator, use oscillator B (sawtooth) to modulate oscillator A (sine/square) — increase the FM amount gradually to add gritty, metallic harmonics. This is the go-to technique for modern hardgroove bass that cuts through dense percussion
- EQ: Cut muddy sub frequencies below ~30Hz
- EQ: Cut mids and highs — bass should stay in the low end only
- **Saturation/distortion**: Add Saturator or Overdrive *after* EQ to add harmonic presence. Use "Analog Clip" or "Medium Curve" mode in Saturator for warm grit — drive at 6-12dB, then pull the output back down. This helps the bass translate on small speakers without adding mud
- Sidechain compress to the kick (use the short kick duplicate as trigger)
- Convert to **mono** — no stereo width on the bass

## Operator Patch (step by step)
- **Oscillator A**: Square wave, level -6dB
- **Oscillator B**: Saw wave, level -18dB, coarse +12 (one octave up). Set routing so B modulates A (FM) — this adds the gritty harmonic content
- **Filter**: Low-pass 24dB, cutoff 40%, resonance 20%, envelope amount 30%, decay 150ms. **Turn off key tracking** — keep the filter cutoff fixed regardless of which note is playing. This gives a consistent tonal character across the pattern and makes the bass sit more predictably in the mix
- **Amp envelope**: Attack 0ms, Decay 200ms, Sustain 70%, Release 50ms
- **Glide**: On, time 30ms — gives note transitions that locked-in feel

## Pattern Style
- **Simple is key** — just 2-3 notes in the pattern
- Rhythmically locks with the kick — the bass "bounces off" the kick in a call-and-response. The groove comes from this interplay, not from the bass alone
- **Notes as percussion**: Think of pitch changes as rhythmic accents rather than melody. Hardgroove bass doesn't need to be perfectly in key — the rhythm and energy matter more than harmonic correctness
- **Note length is a groove tool**: Shorten notes so they end before the next one starts (leave a small gap). This creates a much groovier, more percussive feel than back-to-back legato notes. Also match the synth's amp release to the note length — a long release on short notes defeats the purpose, so keep release tight (under 100ms) when using short staccato notes
- Common keys: F, G, A (low octave, MIDI notes 29-45)
- Pattern length: 2-4 bars

## Example Pattern (key of F, 2 bars)

```
Beat:  1  .  .  .  2  .  .  .  3  .  .  .  4  .  .  .  |  1  .  .  .  2  .  .  .  3  .  .  .  4  .  .  .
Note:  F1 .  .  .  .  .  F1 .  .  .  Ab1.  .  .  .  .  |  F1 .  .  .  .  .  F1 .  .  .  Eb1.  .  .  .  .
```

MIDI notes: F1=29, Ab1=32, Eb1=27

## Example Pattern 2 — Busier 4-bar variation (key of F)

```
Bar 1: F1 .  .  F1 .  .  F1 .  .  .  Ab1.  .  .  .  .
Bar 2: F1 .  .  .  .  .  F1 .  F1 .  .  .  Eb1.  .  .
Bar 3: F1 .  .  F1 .  .  F1 .  .  .  Ab1.  .  Ab1.  .
Bar 4: F1 .  .  .  .  F1 .  .  Eb1.  .  .  F1 .  .  .
```

Same 3 notes (F1, Ab1, Eb1) but with 16th-note rhythmic variation — double hits and offbeat placements create forward momentum without adding melodic complexity.

## Acid Variation
- Use **Analog** or **Operator** with a resonant low-pass filter — crank resonance to 50-70% for that squelchy character
- **Automate filter cutoff + resonance** per-note or over bars using clip envelopes. Sweep cutoff from 20% to 60% on accented notes for the classic acid stab
- **Glide/slide between notes** is essential for the 303 feel — set glide time to 40-60ms and overlap notes slightly in the piano roll to trigger legato slides
- This hardgroove-meets-acid crossover is extremely common in the genre — many hardgroove tracks are essentially acid techno with heavier kicks

## Ableton Instruments
- **Operator** with square wave oscillator — simple and effective
- **Analog** with square oscillator
- Add **Glue Compressor** after for punch
- Add **EQ Eight** to shape the low end

## Mixing
- Bass should be the second loudest element after the kick
- Sidechain is critical — bass must duck on every kick hit. Set sidechain compressor release to ~100-150ms at 142 BPM — this lets the bass breathe back in just before the next kick lands. Too fast (under 50ms) sounds unnatural; too slow (over 200ms) and the bass never fully returns. Use LFO Tool or Shaper for more precise ducking curves if available
- No reverb or delay on the bass
- Keep it mono — `Utility` plugin set to mono

## Tom Bass Variation
An alternative to synth bass is using **tuned toms** (especially 707/909 tom samples) as the bassline source — this gives a more tribal, percussive low-end character. Load tom samples into a Drum Rack or Simpler, tune them down, and write a repetitive rhythmic pattern. Layer a short 1-bar tom pattern with a longer 2-bar pattern on top for evolving complexity. Group the tom tracks together, sidechain the group to the kick, optionally low-pass the group, and convert to mono. This approach is extremely common in hardgroove and gives a rawer, more organic feel than synth bass.

## Production Notes
- The bass + kick relationship is the foundation — get this right first before adding anything else
- Don't overcomplicate the bass pattern — hardgroove bass is minimal by design
