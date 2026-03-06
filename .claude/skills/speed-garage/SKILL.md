---
name: speed-garage
description: Create speed garage tracks. Use when the user asks for speed garage, UK bass, garage bass music, or bassline garage.
---

# Speed Garage

## Quick Reference
- **Tempo**: 135-145 BPM (can push to 130 or 150)
- **Key**: Minor keys (D minor used in reference)
- **Mix secret**: Kick, bass, main hi-hat, and snare are the LOUDEST — everything else sits underneath

## Kick
- Fat punchy kick — drag start time slightly forward to remove any attack delay
- Convert to mono with Utility
- Minimal processing — get a good kick sample and it needs little work

## Bassline (this IS the melody)
- **Walking bass pattern** over 2 bars (short repeating pattern)
- Walk through scale degrees: e.g. root → 5 → 6 → 6 → 3 → back to root
- Add octave jumps on some notes (same notes, just higher) — makes it seem more complex
- **Notes should NOT be legato** — leave tiny gaps between notes for groove (but keep amp release at ~33% to avoid hard clicks between notes)
- **Sound**: FM synthesis (Operator)
  - Sine wave carrier pitched down 2 octaves, modulator at -12 semitones
  - Detune the modulator slightly (e.g. -12.30 semitones) for that wonky, wobbly character
  - Modulation amount at ~60% — use a fast-decay envelope on it for percussive bite
  - Slight attack on amp envelope creates "reverse bass" illusion
  - **Mono voicing** with glide at 10-15% — extend glide during fills/breakdowns for a woozy feel
  - Phase retrigger on note-on to keep the attack consistent
- **Warmth chain**: Light tube saturation (drive ~20%) into a dimension expander (size 0, low mix) — adds weight without muddying the low end
- **Filter**: Low-pass with no resonance, cutoff around 25%, then modulate cutoff with a fast-decay envelope at full depth — this shapes the plucky attack
- Sidechain to kick — use a compressor with fast attack (~0.5ms), medium release (~80-120ms), ratio 4:1 or higher, threshold set so the bass ducks ~4-6dB on each kick hit

## Drums

### Main Drums (loud)
- Fat open hi-hat hitting as hard as the kick
- Main snare hitting as hard as the kick
- These form the loud "skeleton" of the beat

### Dynamic Snare Rack (quieter, underneath)
- Load multiple different snares/claps into a Drum Rack
- Create a dynamic pattern using various snare sounds
- Auto pan sidechain to duck behind kick
- This layer sits behind the main drums in volume

### Rave Loop
- Essential for live energy — without it drums feel dry
- Sidechain with auto pan to keep it controlled
- Mix it noticeably below kick/bass/hat levels

## Vocal Chop
- Slice vocal by transient ("Slice to MIDI Track")
- Pitch up and create sparse rhythmic pattern
- Some chops may need individual pitch adjustment — unmap from default pitch and set manually
- Add analog-style echo/delay
- Auto pan sidechain + high-pass filter (critical to keep low end clean for mastering)

## Effects & Energy
- Crash every 4 bars with reverb + high-pass
- Small transitional sound right before crash restart (keeps track moving)
- Delay + auto pan sidechain on effects
- All effects serve the track's energy — even decorative sounds mark time

## Build Order
1. Set tempo 135-145 BPM
2. Fat punchy kick (mono)
3. Walking bassline (FM sine, 2-bar pattern with octave jumps)
4. Main hi-hat + snare (loud, at kick level)
5. Dynamic snare rack (multiple snares, underneath main drums)
6. Rave loop (sidechained, mixed low)
7. Vocal chop (sliced, pitched, with echo)
8. Crashes and transition effects
