---
name: techno-bass
description: Create techno basslines using Operator. Use when the user asks for techno bass, minimal techno bass, dark techno bass, warehouse bass, or techno sub bass.
---

# Techno Bass — Operator Sound Design

## Quick Reference
- **Tempo**: 128-145 BPM (130 for deep/minimal, 138-145 for driving/peak-time)
- **Key**: Minor keys preferred — F minor, A minor, C minor are standard. Match the kick's fundamental.
- **Character**: Dark, driving, minimal. The bass serves the groove, not the melody.
- **Best range**: F0 to C2 (MIDI notes 29-48). Most notes cluster around F1-A1.

## How Techno Bass Differs
- **Simpler than other bass styles** — 1-3 notes maximum. Techno bass is rhythmic infrastructure, not a melodic voice.
- **Repetitive by design** — the hypnotic quality comes from subtle timbral shifts over a locked pattern, not from note variation.
- **Serves the kick** — the bass exists in the spaces between kicks. Sidechain ducking is non-negotiable.
- **Timbre over pitch** — filter movement, FM amount, and saturation do more work than note choice.

## Patch 1: Sub Bass (Deep / Minimal Techno)

Pure low-end weight. Felt more than heard. For minimal, deep, and hypnotic techno.

### Operator Settings
- **Algorithm**: 1 (simple, no FM). Disable Oscillators B, C, D.
- **Oscillator A**: Waveform **Sine**, Level **-6 dB**, Coarse **1**, Fine **0**
- **Filter**: Off (or Low-pass 24 dB, cutoff **80%**, resonance **0%** — wide open, just for safety)
- **Amp Envelope**: Attack **5 ms**, Decay **0 ms**, Sustain **100%**, Release **50 ms**
- **Voices**: 1 (mono). **Glide**: Off.
- **Pitch Envelope**: Amount **20%**, Decay **30 ms** — subtle pitch drop on attack for weight

### When to Use
Long sustained notes, half notes or whole notes. Sits beneath the kick. No processing needed beyond sidechain and EQ.

## Patch 2: Distorted Bass (Driving / Peak-Time Techno)

Aggressive, harmonically rich. Cuts through dense percussion. The workhorse techno bass.

### Operator Settings
- **Algorithm**: 2 (B modulates A). Enable Oscillators A and B only.
- **Oscillator A**: Waveform **Sq D** (Square Digital), Level **-6 dB**, Coarse **1**, Fine **0**
- **Oscillator B**: Waveform **Saw D**, Level **-18 dB**, Coarse **2** (one octave up), Fine **0**. B modulates A via FM — this adds gritty, metallic harmonics.
- **Filter**: Low-pass **24 dB** (Ladder), Cutoff **45%**, Resonance **25%**
- **Filter Envelope**: Attack **0 ms**, Decay **200 ms**, Sustain **20%**, Release **30 ms**, Amount **40%**
- **Amp Envelope**: Attack **2 ms**, Decay **300 ms**, Sustain **60%**, Release **50 ms**
- **Voices**: 1 (mono). **Glide**: On, **30 ms**.

### Post-Processing
- **Saturator** (first effect): Drive **8 dB**, Curve **Analog Clip**, Soft Clip **On**, Output **-6 dB**

### When to Use
8th note or 16th note patterns. Pairs with heavy kicks at 135+ BPM. The FM amount (Osc B level) is the main tone-shaping control — automate it for builds.

## Patch 3: Acid-Influenced Bass (Resonant / Warehouse Techno)

Filter-driven movement. The filter IS the instrument. For warehouse, acid-techno crossover, and hypnotic styles.

### Operator Settings
- **Algorithm**: 1 (no FM). Disable Oscillators B, C, D.
- **Oscillator A**: Waveform **Saw D**, Level **0 dB**, Coarse **1**, Fine **0**
- **Filter**: Low-pass **24 dB** (Ladder), Cutoff **30%**, Resonance **60%**
- **Filter Envelope**: Attack **0 ms**, Decay **150 ms**, Sustain **0%**, Release **0 ms**, Amount **50%**
- **Filter FreqVel (velocity sensitivity)**: **60%** — higher velocity = more filter sweep
- **Amp Envelope**: Attack **0 ms**, Decay **250 ms**, Sustain **50%**, Release **60 ms**
- **Voices**: 1 (mono). **Glide**: On, **80 ms**.

### Post-Processing
- **Overdrive**: Drive **50%**, Tone **55%**

### When to Use
16th note patterns with rests and accent variation. Velocity controls the squelch — accented notes at 110-127, normal notes at 60-80. Overlap notes slightly to trigger glide.

## Pattern Types

### Pattern 1 — Driving 8th Notes (Root Note Pulse)
```
Beat:  1  .  +  .  2  .  +  .  3  .  +  .  4  .  +  .
Note:  F1 .  F1 .  F1 .  F1 .  F1 .  F1 .  F1 .  F1 .
Vel:   100.  80 .  100.  80 .  100.  80 .  100.  80 .
```
Locked to the kick. Alternating velocity creates movement without changing notes. Use with Patch 1 or 2.

### Pattern 2 — Offbeat (Between Kicks)
```
Beat:  1  .  +  .  2  .  +  .  3  .  +  .  4  .  +  .
Kick:  X  .  .  .  X  .  .  .  X  .  .  .  X  .  .  .
Note:  .  .  F1 .  .  .  F1 .  .  .  F1 .  .  .  Ab1.
Vel:   .  .  90 .  .  .  90 .  .  .  90 .  .  .  110.
```
Bass on the "and" of each beat. Creates space for the kick. The Ab1 (MIDI 44) on the last offbeat adds tension. Use with Patch 2.

### Pattern 3 — Syncopated 16ths with Rests
```
Beat:  1  .  +  .  2  .  +  .  3  .  +  .  4  .  +  .
Note:  F1 .  F1 F1 .  .  F1 .  F1 .  .  F1 .  Eb1.  .
Vel:   110.  70 90 .  .  110.  80 .  .  70 .  110.  .
Slide: .  .  .  >  .  .  .  .  .  .  .  >  .  .  .  .
```
`>` = overlap into next note for glide. Rests on beats 2 and 3+ create rhythmic breathing. Use with Patch 3. MIDI notes: F1=29, Eb1=27, Ab1=32.

## Effects Chain (after Operator + Saturator/Overdrive)

### 1. EQ Eight
- **High-pass**: 30 Hz, 24 dB/oct — removes sub-rumble below useful range
- **Cut at 200-400 Hz**: -3 dB wide bell — reduces boxiness and mud
- **Low-pass**: 3 kHz, 12 dB/oct — optional, keeps bass out of hi-hat territory

### 2. Compressor (Sidechain)
- **Sidechain Input**: Kick drum track (or dedicated kick sidechain bus)
- **Ratio**: 4:1
- **Attack**: 0.1 ms (instant)
- **Release**: 100-150 ms (tune to BPM — at 140 BPM, 120 ms lets bass breathe back before next kick)
- **Threshold**: Adjust until getting 4-6 dB of gain reduction on each kick hit

### 3. Utility
- **Width**: 0% (mono). Bass must be mono below 200 Hz — no exceptions.

## Automation Ideas

These create the evolution that keeps a repetitive pattern interesting over 8-32 bars:

- **Filter cutoff** (Operator): Slow sweep from 30% to 55% over 8 bars, then drop back. Use `set_clip_envelope` on the Filter Freq parameter.
- **FM amount** (Osc B level on Patch 2): Increase from -18 dB to -8 dB during builds for rising aggression. Automate via clip envelope on Osc-B Level.
- **Resonance**: Push from 25% to 50% during breakdowns, pull back on drops.
- **Saturator drive**: Increase 2-4 dB during the final 4 bars before a drop.
- **Note length variation**: Shorten notes from 1/8 to 1/16 over 4 bars for increasing urgency. Duplicate the clip and edit note lengths.

## Build Order

1. `create_midi_track` — name it "Techno Bass"
2. `load_instrument_or_effect` — load **Operator**
3. Set Operator parameters via `set_device_parameter` for chosen patch (1, 2, or 3)
4. `load_instrument_or_effect` — add **Saturator** (Patch 2) or **Overdrive** (Patch 3). Skip for Patch 1.
5. Set Saturator/Overdrive parameters via `set_device_parameter`
6. `load_instrument_or_effect` — add **EQ Eight**
7. Set EQ: high-pass 30 Hz, cut 200-400 Hz via `set_device_parameter`
8. `load_instrument_or_effect` — add **Compressor**, enable sidechain from kick track
9. Set Compressor: ratio 4:1, attack 0.1 ms, release 120 ms via `set_device_parameter`
10. `load_instrument_or_effect` — add **Utility**, set Width to 0%
11. `create_clip` — 2 or 4 bars at the song's tempo
12. `add_notes_to_clip` — program the pattern (see Pattern Types above)
13. `set_clip_envelope` — automate filter cutoff over 4-8 bars for movement
14. `set_track_volume` — set bass to **-8 dB** as starting point, adjust after kick relationship is set
