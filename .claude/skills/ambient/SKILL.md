---
name: ambient
description: Create ambient electronic music. Use when the user asks for ambient, ambient pads, ambient textures, dreamy ambient, or lush ambient drones.
---

# Ambient Electronic Music

## Quick Reference
- **Tempo**: Flexible (140 BPM works — it mostly controls how long chords sustain)
- **Key**: Minor keys (F# minor used in reference)
- **Core idea**: Simple patches + heavy reverb/delay = cascading overtones

## Chord Layer 1 (Foundation)

### Chord Progression
- Keep it simple — basic triads but with creative inversions
- **Spread voicings**: take middle note of triad up an octave (more open, epic sound)
- Go further: take the 3rd up TWO octaves on some chords
- Each chord can have different inversions — same chord, different voicing textures
- Example in F# minor: i → bVI → bIII (all with spread voicings)

### Sound Design
- **Keep patches simple** — two detuned saw waves with low-pass filter + vibrato
- Basic patches work BETTER than complex ones for ambient
- Complex patches create chaos when combined with heavy reverb
- **Slow modulation** keeps pads alive: route a slow LFO (0.1–0.5 Hz) to filter cutoff, oscillator pitch (±3–7 cents), or wavetable position so the timbre gently drifts over time — the ear stays interested without any melodic change
- **Wavetable position modulation** is especially powerful for ambient — instead of (or in addition to) modulating the filter, route an LFO to the wavetable position itself. A slow sine LFO (~0.06 Hz) at 50% depth on the position creates a gently undulating timbre that sweeps through different waveform shapes. This works best with wavetable categories that have smooth timbral transitions (e.g. "Dual Saw", "Harmonic Series", or "Complex" tables in Wavetable)
- **Concrete Wavetable patch** (slowly evolving pad):
  - Osc 1: Basic Shapes → Saw, unison 2 voices, detune 15%
  - Osc 2: Basic Shapes → Sine, pitched +7 semitones (a fifth up), level lower than Osc 1
  - Filter: LP 12dB, cutoff 55%, resonance 0%; LFO 1 → filter cutoff, rate 0.2 Hz, amount 20%
  - Amp envelope: Attack 800ms, Decay 2s, Sustain 80%, Release 3s
  - The detuned saw provides body, the fifth adds harmonic interest, and the slow LFO keeps the timbre drifting

### Effects (this is where the magic happens)
- **Reverb**: 84%+ wet, very long decay — reverb IS part of the sound
  - Set **pre-delay** to 40–80 ms to preserve note articulation even at high wet levels
  - Push **diffusion** above 80% for smooth, cloudlike tails — lower diffusion gives grainier, more metallic reflections
  - Roll off highs with the reverb's **damping** control so tails darken over time and stay out of the way
- **Delay**: generous amounts — creates cascading chord tails that ring into each other
- **Limiter trick**: put a limiter after reverb, turn up input gain → creates "distressed" compression that brings out reverb tails (not for mixing — for sound design)

## Chord Layer 2 (Additive Voices)
- Don't play full chords — play individual notes from the scale
- These notes COMBINE with Layer 1 to create one complex chord
- Example: 3rd, 9th, 4th, root — notes already in the chords but in different octaves
- Creates rich, layered ambient harmonics
- **Sound**: slightly different from Layer 1 — sine + square detuned with low-pass
- **Crystal drip texture**: for a sparkly, percussive shimmer on Layer 2, use a **band-pass filter** (not low-pass) on the second oscillator and modulate both the wavetable position AND the band-pass frequency with the same **random-waveform LFO at high speed** (~10 Hz, amount 100%). The random jumps through the wavetable combined with the narrow band-pass window create unpredictable "dripping" tones that glitter above the pad — drench in reverb and they become crystalline ambient texture
- **Alternative Operator patch** (different texture from Layer 1):
  - Oscillator A: sine wave (carrier); Oscillator B: square wave at -18dB for subtle FM
  - Same long envelope as the Wavetable patch (Attack 800ms, Decay 2s, Sustain 80%, Release 3s)
  - Gives a glassier, more bell-like quality that contrasts with the saw-based Layer 1
- Same heavy reverb/delay treatment
- Can apply limiter on the GROUP of both layers for even more compression effect

## Key Principles

### Less is More with Patches
- Resist making complex synth sounds
- Two detuned saw waves + filter = perfect starting point
- Let the reverb and delay create all the complexity

### Reverb as Sound Design
- Think of reverb not as an effect but as core to the sound
- Overtones from high-wet reverb create "free" harmonics
- Chords ringing into each other through reverb = the ambient sound

### The Limiter Trick
- Put limiter after reverb chain
- Turn ceiling to 0 dB, increase input gain
- Squashes reverb tails creating compressed, distressed texture
- Works on individual layers or on the group

### Envelope-Driven Harmonic Sweeps
- Use **envelope 2** to simultaneously modulate both the **wavetable position** and the **filter frequency** with a very long decay (6–11 seconds) and sustain at zero — the sound starts bright and harmonically complex, then slowly darkens and simplifies over many seconds
- This creates a classic "sweeping pad" where a single held note evolves dramatically without any LFO: the envelope opens the filter and pushes the wavetable to a rich position on key press, then gradually pulls both back down
- For an extra layer, route the same envelope to **oscillator 2 gain** so the brighter oscillator fades out entirely over the sweep, leaving only the warm base sound underneath

### Voice Spreading
- Same chord can sound completely different based on which octave each note is in
- Don't just stack notes close together — spread them across 2-3 octaves
- This is what makes "simple" progressions sound complex and deep

### Granular Textures & Field Recordings
- **Granular synthesis** turns any sample into an evolving ambient texture — feed a sustained note, vocal snippet, or field recording into a granular engine (Granulator II in Ableton, or third-party), set grain size small (20–80 ms), scatter the position, and apply pitch randomization for shimmering clouds
- **Pitch-shifted layers**: duplicate a pad or recording, pitch it down 12 semitones (one octave) and blend it in quietly underneath — adds sub-harmonic weight without new melodic content; pitching UP 12 semitones and drenching in reverb creates ethereal shimmer layers
- **Field recordings** (rain, room tone, distant traffic) layered very quietly give ambient tracks a sense of physical space — high-pass around 200 Hz and feed them through the same reverb as your pads so everything lives in the same "room"

## Build Order
1. Write chord progression with creative inversions/voicings
2. Simple saw pad sound (two detuned saws + low-pass + vibrato)
3. Add heavy reverb (80%+ wet) and delay
4. Optional: limiter after reverb for compressed texture
5. Add Layer 2 with individual scale notes that combine with Layer 1
6. Different but similar sound on Layer 2 (sine + square)
7. Same reverb/delay treatment on Layer 2
8. Optional: group limiter for final compression effect
