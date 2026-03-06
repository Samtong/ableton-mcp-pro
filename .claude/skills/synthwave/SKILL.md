---
name: synthwave
description: Create synthwave and retrowave music. Use when the user asks for synthwave, retrowave, outrun, 80s synth, neon synth, or retro electronic.
---

# Synthwave / Retrowave Production

## Quick Reference
- **Tempo**: 100-120 BPM (sweet spot: 108-115)
- **Keys**: Minor keys — A minor, E minor, F# minor, C minor
- **Feel**: Nostalgic, driving, cinematic — neon-lit highways at night
- **Core elements**: Gated reverb drums, analog-style arps, bright detuned leads, warm pads, driving bass

## Drums — Gated Reverb Is Everything

### Snare (the signature sound)
- Short, tight snare sample (acoustic or 808-style) — 707 samples work great
- **Reverb**: Plate or Hall, Decay **3-5 sec**, Size **80-100%**, Dry/Wet **100%**, Pre-delay **0 ms**
- **Gate** after reverb: Threshold **-25 dB**, Return **-30 dB**, Release **50-100 ms**, Lookahead **10 ms** (smooths the gate opening — much cleaner than 1 ms default)
- The gate cuts the reverb tail abruptly — this IS the 80s snare sound
- **Pro technique — parallel rack**: Group EQ8 + Reverb + Gate into an Audio Rack (Ctrl+G), then add a second empty "Dry" chain. This lets you blend the dry snare with the gated reverb independently. Place the EQ8 *before* the reverb to shape what frequencies feed into it (cut lows/highs you don't want reverberating). Optionally add subtle OTT on the wet chain for extra presence.

### Kick, Toms, Hats
- **Kick**: Punchy 808-style, four-on-the-floor, boost at **60 Hz**, click at **3-5 kHz**
- **Toms**: Big pitched toms for fills — same gated reverb as snare, tune to track key
- **Hi-hats**: 8th notes (open hat on offbeats) or steady 16ths, keep dry and crisp
- Hat velocity: accent beats 1 and 3 at 100-110, offbeats at 70-85

### Classic Synthwave Beat
```
Step:  1  2  3  4  5  6  7  8  9  10 11 12 13 14 15 16
Kick:  X  .  .  .  X  .  .  .  X  .  .  .  X  .  .  .
Snare: .  .  .  .  X  .  .  .  .  .  .  .  X  .  .  .
HH:    X  .  X  .  X  .  X  .  X  .  X  .  X  .  X  .
Open:  .  .  .  .  .  .  .  X  .  .  .  .  .  .  .  X
```

## Bass — Analog-Style Saw + Sub

### Operator Setup
- **Oscillator A**: Saw wave, **-6 dB**
- **Oscillator B**: Sine wave (sub layer), same pitch, **-8 dB**
- Routing: **Parallel** (not FM)
- **Voices**: 1 (mono), **Glide**: 30-80 ms
- Filter: Low-pass, Cutoff **600-900 Hz**, Resonance **15-25%**
- Filter envelope: Attack 0, Decay 200 ms, Sustain 60%, Release 100 ms

### Alternative: Wavetable Bass (quick method)
- Duplicate the pad Wavetable patch, switch voice mode to **Mono**
- Drop Osc 1 by **-12 semitones**, Osc 2 by **-24 semitones** (two octaves lower) with slight detune (~7 cents)
- Steepen the filter slope from 12 to **24 dB/oct** for a tighter low end
- Route the **Amp Envelope to Filter Frequency** in the Mod Matrix — gives a plucky, self-closing character on each note
- Use a parallel rack: chorus at **100% wet** on one chain for stereo width, but place an **EQ8 before the chorus** to high-pass the lows (~200 Hz) so chorus only affects upper harmonics. This prevents phase cancellation in the bass range when summed to mono.

### Pattern and Processing
- Driving 8th or **16th notes** following root — 16ths give a more driving, rolling feel
- Offbeat patterns or occasional octave jumps for variation
- **Sidechain** to kick: Attack **0.5 ms**, Release **80-120 ms**, Ratio **4:1**, aim for **3-5 dB** reduction

## Arpeggios — The Signature Element

The arp IS the track in many synthwave songs — it defines harmony and rhythm.

### Synth (Wavetable or Operator)
- Wavetable: Basic Shapes → Saw or Pulse wave
- **Unison**: 2-4 voices, **Detune**: 10-15% (clarity over width)
- Filter: LP, Cutoff **60-75%**, Resonance **20-30%**
- Amp envelope: Attack **0 ms**, Decay **300-500 ms**, Sustain **40-60%**, Release **200 ms**

### Arpeggiator MIDI Effect
- Style: **Up** or **Up/Down**, Rate: **1/16**
- Range: **1-2 octaves**, Gate: **80%**

### Effects
- **Chorus**: Rate 0.3-0.8 Hz, Amount 40-60% — warm analog wobble
- **Delay**: Dotted 8th (3/16), Feedback **30-45%**, Dry/Wet **25-35%**
- High-cut delay at **6-8 kHz** to prevent harshness

## Lead Synth — Bright and Expressive

### Patch Setup
- **2 oscillators**: Both saw waves
- **Oscillator B detune**: **+7 cents** (classic slight detune)
- Filter: LP, Cutoff **80-90%**, Resonance **10-15%**
- Amp envelope: Attack **5-15 ms**, Decay **800 ms**, Sustain **75%**, Release **400 ms**
- **Pitch bend range**: +/- 2 semitones for expressive bends

### Effects Chain
1. **Chorus**: Rate 0.5 Hz, Depth 60% — essential shimmering 80s tone
2. **Delay**: Stereo dotted 8th, Feedback 35%, Dry/Wet 25%
3. **Reverb**: Hall, Decay **3-4 sec**, Dry/Wet **30-40%** — big and spacious

## Pad — Warm Analog Bed

### Patch Setup
- **Oscillator**: Pulse wave with PWM — LFO → Pulse Width at 0.2-0.5 Hz, Amount 30-50%
- Alternative: Two saw oscillators with Osc 2 tuned **+12 semitones** (octave up) and detuned — instant thick 80s pad
- Filter: LP (use **MS2** type for vintage character), Cutoff **50-65%**, Resonance **10-20%**, add a touch of Drive
- Amp envelope: Attack **200-500 ms**, Decay **1 sec**, Sustain **80%**, Release **2-3 sec**
- **Analog pitch drift** (Wavetable): Set LFO1 to sine wave, sync to Beats, Rate **1 bar**, Amount **~40%**. In the Mod Matrix, route LFO1 to filter frequency AND to pitch at a very small amount (~0.43). This simulates the tuning instability of vintage analog synths — the pad slowly drifts and breathes rather than sitting static.
- High-pass at **150-200 Hz** to stay out of the bass range

### Effects
1. **Chorus**: Width and warmth — pad should feel wide and enveloping
2. **Reverb**: Hall, Decay **4-6 sec**, Dry/Wet **40-55%**
- Sits underneath everything — low volume, high reverb, filling the stereo field

## Key Effects — The Synthwave Sound

- **Chorus** (on everything): The most important synthwave effect — emulates classic Juno-106 character. Put on arps, leads, pads, even bass.
- **Reverb** (plate or hall): Plate for leads/snares, Hall for pads. Decay 2-5 sec. Always high-cut at **8-10 kHz** to keep it warm.
- **Delay** (dotted 8th): Creates illusion of more notes. Essential on arps and leads. Feedback 30-45%.
- **Tape saturation**: Saturator (Analog Clip or Soft Sine), Drive **2-4 dB**, Dry/Wet **60-80%** on master bus. Rounds off harsh digital edges.

## Build Order
1. Set tempo (108-115 BPM), key (A minor or E minor)
2. Drums: Kick four-on-floor, snare with gated reverb on 2 and 4, 8th note hats
3. Bass: Operator saw + sine sub, 8th note pattern, sidechain to kick
4. Arpeggio: Wavetable saw/pulse, Arpeggiator 1/16, Chorus → Dotted 8th Delay
5. Pad: Pulse wave with PWM, Chorus → Hall Reverb — keep low in the mix
6. Lead: Detuned saws (+7 cents), Chorus → Delay → Reverb
7. Master: Tape saturation (subtle), final EQ shaping
