---
name: supersaw-chords
description: Create supersaw chord patches in Wavetable. Use when the user asks for supersaw, big chords, future bass chords, trance pads, dreamy synth, EDM chords, or lush synth layers.
---

# Supersaw Chords — Wavetable

## Quick Reference
- **Origin**: Roland JP-8000 (1996) — multiple detuned sawtooth oscillators stacked
- **Character**: Wide, lush, full — the signature sound of trance, future bass, and EDM
- **Core idea**: Many slightly detuned saw voices create richness through beating/phasing
- **Key insight**: Focus on the synth core settings BEFORE effects — a good supersaw sounds full even dry

## Step 1: Oscillator Setup

### Oscillator 1 (Foundation)
- Wavetable: **Basic Shapes** category → **Saw wave**
- **Unison voices**: 8 (this is where the "super" comes from)
- **Detune amount**: **30%** is the sweet spot (rich without sounding out of tune)
  - 20% = tighter, more focused
  - 40% = wider, more detuned (use for stereo layer)
- Unison mode: **Shimmer** (preferred — adds subtle pitch fluctuation for movement)
  - Classic: voices spread evenly (more static)
  - Shimmer: adds pitch fluctuation (more organic, lush)
  - Super: middle voices closer together, detuned voices on sides (focused center)

### Oscillator 2 (Octave Layer)
- Same wavetable: **Basic Shapes → Saw wave**
- **Pitch**: +12 semitones (one octave up)
- **Unison voices**: 8
- **Detune**: Same as Osc 1 or slightly different for extra width
- Mix slightly quieter than Osc 1 (Osc 2 is the brightness layer, not the foundation)

### Alternative Wavetables
- Instead of Basic Shapes saw, try wavetables from the **Saw** category
- **Quad Saw** or similar multi-saw wavetables can sound even thicker
- Experiment with wavetable position for different tonal colors

### Sub Oscillator
- Enable the **Sub** oscillator for low-end foundation
- Keeps the fundamental strong even when unison voices spread the pitch
- Especially important for chords below C3

## Step 2: Filter Settings

### Low-Pass Filter
- Type: **Low-pass** (LP)
- Cutoff: Start around **70-80%** — don't close it too much for supersaws
- Resonance: Low (0-15%) — high resonance thins out supersaws
- The filter mainly serves to tame harsh high frequencies, not shape the sound dramatically

### Filter Envelope (optional)
- Small positive amount for pluck-style chords
- Longer attack + decay for pad-style evolving chords
- For big stabs: fast attack, medium decay, moderate sustain

## Step 3: Amplitude Envelope

### For Pads
- **Attack**: 50-200 ms (soft entry)
- **Decay**: 500 ms - 1 sec
- **Sustain**: 70-90%
- **Release**: 500 ms - 2 sec (long tail)

### For Stabs/Chords
- **Attack**: 0-10 ms (immediate)
- **Decay**: 200-500 ms
- **Sustain**: 60-80%
- **Release**: 200-500 ms

## Step 4: Making It Mono-Compatible

This is critical — supersaws are very wide but must not disappear on mono systems.

### Utility Trick
- Group Wavetable into an **Instrument Rack** (Ctrl+G)
- Add **Utility** after Wavetable inside the rack
- Set Utility **Width** to reduce stereo width
- Or: set to **Mid** mode to hear only the mono signal — check nothing disappears

### Mid/Side Approach
- Add Utility, set to **Mid/Side** mode
- Turn down **Side** signal to reduce stereo width
- This keeps the mids prominent while taming the super-wide detuned voices
- A supersaw that sounds huge in stereo but vanishes in mono is useless on a club system

### Bass Mono Rule
- Below ~200 Hz should be mono
- Use EQ8 in Mid/Side mode, high-pass the Side channel at 200 Hz

## Step 5: Layering (Instrument Rack)

### Layer 1 — Mono Center Layer
- Wavetable with 8 voices, **20% detune** (tighter)
- Use Utility in Mid/Side mode: reduce sides to **-60 dB** (almost fully mono)
- This creates a strong, focused center signal

### Layer 2 — Stereo Width Layer
- Second Wavetable instance, **40% detune** (wider)
- Utility at **100% width** (full stereo)
- This creates the wide, lush stereo image around the focused center
- Result: strong center + detuned width — best of both worlds

### Layer 3 — Noise Texture (optional)
- Add a Sampler with a noise sample (not Wavetable's built-in noise — too limited)
- Level: **-42 dB** (very subtle, just adds air)
- Loop mode: forward only (not back-and-forth)
- Sample Scale: 50% (reduces pitch sensitivity, prevents phasing on polyphonic play)
- High-pass above 2-4 kHz so it only contributes shimmer

### Chord Device
- Add **Chord** MIDI effect before the instrument rack
- Set one shift to +12 semitones (doubles the chord an octave up)
- This creates automatic octave layering from a single MIDI input
- Can also add shifts at +7 (fifth) or +3/+4 (third) for instant harmonization

## Step 6: Effects

### OTT / Multiband Compression
- The secret weapon for modern supersaws
- Boosts highs and lows while keeping mids quieter
- Use Ableton's **Multiband Dynamics** preset "OTT" or similar
- Dial back the amount (50-70%) — 100% is too squashed

### Reverb
- Medium-large reverb for space
- Pre-delay: 20-40 ms (keeps the attack clear)
- Decay: 2-4 seconds
- High-cut the reverb around 8-10 kHz to prevent harshness

### Chorus / Dimension Expander
- Can add extra width but use sparingly — the unison already provides width
- More useful on the mono layer to give it some movement

### EQ8 (final shaping)
- Cut below 100-150 Hz if there's a dedicated bass
- Gentle high shelf boost at 8-10 kHz for sparkle
- Notch out any resonant frequencies from the unison phasing

## Step 7: Chord Voicings for Supersaws

### Spread Voicings Work Best
- Don't cluster all notes close together
- Spread chord tones across 1-2 octaves
- Root in lower octave, 3rd and 5th higher, 7th on top

### Common Progressions
- **Trance**: Am → F → C → G (vi-IV-I-V)
- **Future Bass**: I → vi → IV → V with 7th extensions
- **Emotional**: i → bVI → bIII → bVII (minor key)

### Velocity
- Full velocity (100-127) for big drops
- Lower velocity (70-90) for breakdowns with filter automation

## Build Order
1. Wavetable: Saw wave, 8 unison voices, 20-40% detune
2. Oscillator 2: Same saw, +12 semitones, 8 voices
3. Enable sub oscillator for low-end anchor
4. Set amplitude envelope (pad or stab style)
5. Group into Instrument Rack, add mono-check Utility
6. Add Chord device (+12 semitones) before instrument
7. Layer 2: Lower-unison focused mono layer
8. Effects: OTT → Reverb → Final EQ
9. Mid/Side EQ: mono below 200 Hz
