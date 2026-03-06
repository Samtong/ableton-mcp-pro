---
name: house-chords
description: Create house music chords and stabs. Use when the user asks for house chords, deep house chords, disco chords, house stabs, piano house, or filtered house chords.
---

# House Chords — Programming Guide

## Quick Reference
- **Tempo**: 120-128 BPM (124 for deep house, 126-128 for mainroom)
- **Keys**: Minor for moody/deep (Am, Dm, Gm), major for uplifting/disco (C, F, Bb)
- **Feel**: Groove-driven, hypnotic — chords serve the rhythm, not the other way around
- **Core principle**: Extensions (7ths, 9ths) and rhythm matter more than harmonic complexity

## Chord Types That Define House

### 1. Stab Chords
- Short, punchy, rhythmic hits — offbeat stabs are THE house signature
- Tight amp envelope: attack 0 ms, decay 100-250 ms, sustain 0%, release 50-100 ms
- Band-pass filtered to sit in the midrange (800-2000 Hz)

### 2. Deep House Pads
- Sustained, warm, filtered — sit behind the groove like a blanket
- Long release (1-3 sec), moderate attack (30-100 ms), LP filter at 40-60%
- Slow LFO on filter cutoff (0.1-0.5 Hz) for gentle movement

### 3. Piano House
- Rhodes, Wurlitzer, or acoustic piano — the Chicago/NYC sound
- Spread voicings across 1.5-2 octaves, velocity variation is critical (ghosts at 40-60, accents at 100-120)
- Often layered: piano for attack + pad underneath for sustain

### 4. Disco/Filtered Chords
- Synth or sampled chords through a sweeping low-pass filter — the filter IS the sound
- Automate LP cutoff over 8-16 bars: start muffled (20-30%), sweep to bright (80-90%)

## Voicing Tips
- **Open voicings** sound bigger: spread tones across octaves (C2-G3-B3-E4, not C3-E3-G3-B3)
- **Extensions are essential** — plain triads are too simple for house:
  - Minor 7ths (Am7, Dm7): bread and butter of deep house
  - Major 7ths (Cmaj7, Fmaj7): dreamy, jazzy, soulful house
  - 9ths (Am9, Fm9): deeper complexity — the Kerri Chandler sound
  - Diminished triad (root, +3, +3 semitones): two-semitone gap then one-semitone gap — tense, ambiguous, captures a minimal house vibe. Use as a substitute for standard minor chords to add edge.
- **Inversions**: don't always play root position — move the fewest notes between chords
  - Example: Am7 (A-C-E-G) to Dm7 (A-C-D-F) — only two notes change

## Common Progressions

### Classic House (ii-V-I in C major)
- **Am7 - Dm7 - G7 - Cmaj7** — soulful, jazzy, resolving

### Deep House Two-Chord Vamp
- **Fm9 - Bbm7** — hypnotic, minimal. Also try: Am9 - Em7, Dm9 - Am7

### Disco/Filtered Four-Chord Loop
- **Dm7 - G7 - Cmaj7 - Fmaj7** — descending bass motion, classic disco feel

### Parallel Harmony
- Move a single minor 7th voicing shape in parallel (Cm7 to Dm7 to Fm7)
- Common in tech house — simple but effective

## Rhythm Patterns

### Offbeat Stabs (Most Essential)
- Place chords on the "and" of each beat (eighth-note upbeats)
- Hits at 1.2, 1.4, 2.2, 2.4, 3.2, 3.4, 4.2, 4.4 — instant genre recognition
- Leave beat 1 empty to let the kick breathe

### Syncopated 16th Patterns
- Mix offbeat 8ths with 16th-note anticipations before beat 3
- Vary note lengths: short stabs mixed with one longer sustained note per bar

### Pads Underneath Stabs
- Sustained pad (whole/half notes) under rhythmic stabs — different sounds for each layer

## Sound Design

### Stabs: Operator or Analog
- **Oscillators**: Saw + square (60/40 mix)
- **Amp envelope**: Attack 0 ms, Decay 150-300 ms, Sustain 0%, Release 80 ms
- **Filter**: Band-pass at 800-2000 Hz, resonance 20-30% for nasal bite

### Pads: Wavetable
- **Oscillators**: 2x detuned saws, 4-6 unison voices, detune 15-25%
- **Filter**: Low-pass, cutoff 50-65%, resonance 10-15%
- **Filter LFO**: Sine, rate 0.2-0.4 Hz, amount 15-25%
- **Amp envelope**: Attack 80 ms, Decay 1 sec, Sustain 75%, Release 1.5-2 sec

### Filtered Chords: Any Source + Auto Filter
- Add **Auto Filter**: Low-pass, 24 dB slope
- **LFO**: Triangle/sine, rate synced to 2-4 bars, amount 60-80%
- This single effect can turn any chord into a house chord

## The Filter Sweep (Essential Technique)
- Automate Auto Filter LP cutoff over 8-16 bars
- Start closed (200-400 Hz, muffled) — gradually open to 4-8 kHz (bright, energetic)
- This build-and-release IS the disco/house sound
- Reset at the start of each 16-bar section for repeated builds
- **Bandpass LFO alternative** (great for minimal house): instead of drawing automation by hand, set Auto Filter to **bandpass mode** with **high resonance (60-80%)**, then use its built-in LFO in **sync mode** at a short rate (1/4 to 1 bar). This generates both upward and downward sweeps automatically with more natural variation than hand-drawn envelopes. Tweak the LFO amount knob to taste.

## Effects Chain
- **Chorus**: Chorus-Ensemble, rate 0.5-1 Hz, amount 30-50% — essential for pads, optional for stabs
- **Delay**: Ping Pong Delay for stereo width on stabs — sync to 1/8 or 3/16, feedback 20-35%, dry/wet 15-25%. Adds space without muddying the center.
- **Reverb**: Medium plate, decay 1-2 sec, pre-delay 15-25 ms, high-cut at 6-8 kHz, dry/wet 15-25%
- **Sidechain**: Compressor keyed to kick, threshold -30 dB, ratio 4:1, release 100-150 ms (8:1+ for French house pump)

## Build Order
1. Choose chord type: stabs, pads, piano, or filtered
2. Set up synth (Operator for stabs, Wavetable for pads)
3. Program voicing: open position, add 7ths/9ths
4. Write rhythm: offbeat 8ths for stabs, sustained for pads
5. Add Auto Filter with LFO or automation for movement
6. Apply effects: chorus (pads), reverb (subtle), sidechain to kick
7. Layer if needed: pad underneath stabs, or piano + pad together
8. Automate filter cutoff over 8-16 bars for builds and drops
