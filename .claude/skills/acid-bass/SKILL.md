---
name: acid-bass
description: Create acid bass lines with 303-style squelch. Use when the user asks for acid bass, 303 bass, acid techno, acid house, squelchy bass, or resonant filter bass.
---

# Acid Bass — 303-Style Squelch in Operator

## Quick Reference
- **Tempo**: 125-145 BPM (spans acid house through acid techno)
- **Origin**: Roland TB-303 Bass Line synthesizer — a mono synth with saw/square oscillator, resonant low-pass filter, and a unique accent/slide sequencer
- **Character**: Squelchy, rubbery, resonant filter sweeps driven by short decay envelopes. The filter IS the instrument.
- **Best range**: C1 to C2 (MIDI notes 36-48). Acid lines stay low.
- **Use in**: Acid House, Acid Techno, Chicago House, Goa Trance, Hard Trance

## Step 1: Operator Oscillator Setup

### Oscillator A — The Waveform
- Open Operator with default preset
- **Waveform**: **Saw D** (Saw Digital) — the classic 303 waveform. Alternative: **Sq D** for darker, more dubby acid.
- Level: **0 dB**. Disable Oscillators B, C, and D — the 303 is a single-oscillator synth.
- Routing: simplest algorithm (no FM). The sound comes entirely from the filter.

## Step 2: The Filter — This Is Everything

The filter is what makes a 303 a 303. Without these settings, it is just a saw wave.

### Filter Settings
- **Filter type**: Low-pass, **24 dB/octave** (Ladder)
- **Cutoff frequency**: Low — around **30-40%** (roughly 400-800 Hz)
- **Resonance**: HIGH — **60-80%**. This is the squelch. Below 50% it sounds generic. Above 85% it self-oscillates.
- **Filter Envelope Amount (Env)**: **50-70%**. This controls how far the filter opens on each note.

### Filter Envelope — The Squelch Shape
- **Attack**: 0 ms (instant open)
- **Decay**: 100-200 ms (the "blip" duration — shorter = more percussive, longer = more sweep)
- **Sustain**: 0% (filter must close back down)
- **Release**: 0 ms
- This creates the signature envelope: a fast spike that decays back to the cutoff. Every note "squelches" open and shut.

### Amp Envelope
- **Attack**: 0 ms
- **Decay**: 200-400 ms
- **Sustain**: 60-80% (notes sustain but with a punchy attack)
- **Release**: 50-100 ms (short, keeps it tight)

**Staccato variant** (more aggressive, percussive 303 style): Drop decay to **80-150 ms**, sustain to **0-20%**, release to **20-40 ms**. This produces clipped, machine-gun note bursts where the glide between overlapping notes does all the melodic work. Works especially well at higher tempos (135+ BPM) and with heavy distortion.

## Step 3: Voice Settings

- **Voices**: 1 (the 303 is monophonic — non-negotiable)
- **Glide**: Enable, set to **60-120 ms**. Glide mode triggers only on overlapping notes.
- Transpose down one octave if needed to sit in the C1-C2 range

## Step 4: The Three 303 Techniques

### 1. Accent (Velocity = Squelch Amount)
- **Set Filter FreqVel (velocity sensitivity) to 60-80%**
- Higher velocity = more filter envelope = more squelch
- Accented notes: velocity **110-127**. Normal notes: velocity **60-80**.
- Accent placement matters more than note choice — accent every 3rd or 5th note

### 2. Slide (Overlapping Notes = Portamento)
- **Overlapping** MIDI notes = smooth pitch glide. **Non-overlapping** = staccato jump.
- Extend one note to overlap the next by a small amount to trigger slide.
- Slides create the rubbery, stretchy quality that defines acid.

### 3. Note Length Variation
- Mix **short notes** (1/32 or short 1/16) with **longer held notes**
- Short = percussive plucks. Long = sustained squelch with slide potential. Never uniform.

## Step 5: Pattern Programming

- **Match the kick's fundamental**: Analyze the kick drum's root frequency (e.g., ~54 Hz = A) and write the acid line in that key so the bass and kick reinforce each other rather than clash. Use a spectrum analyzer on the kick to find it.
- **Root note dominant**: Most notes = root or octave. Acid is about rhythm and filter, not melody.
- **Minor key preferred**: Acid techno and acid house patterns almost always use minor intervals (minor 3rd, minor 7th) for dark, driving tension.
- **16th note grid** with gaps (rests) for breathing room.
- **Odd accents**: Place accents off the beat for tension.
- **Reduce pattern length**: Try 15 or 13 steps instead of 16 — cycles against the bar for hypnotic drift.

### Example Pattern 1 — Classic Acid (16 steps)
```
Step:   1  2  3  4  5  6  7  8  9  10 11 12 13 14 15 16
Note:   C1 .  C1 C1 .  C2 C1 .  C1 .  C1 C1 .  Eb1 C1 .
Accent: x  .  .  x  .  x  .  .  .  .  x  .  .  x  .  .
Slide:  .  .  .  >  .  >  .  .  .  .  .  >  .  >  .  .
```

### Example Pattern 2 — Rolling Acid Techno
```
Step:   1  2  3  4  5  6  7  8  9  10 11 12 13 14 15 16
Note:   C1 C1 C2 C1 C1 .  C1 Bb0 C1 C1 C2 C1 .  C1 C1 Eb1
Accent: x  .  x  .  .  .  .  x  .  .  x  .  .  .  .  x
Slide:  .  .  >  .  .  .  .  >  .  .  >  .  .  .  .  >
```
- `>` means this note slides INTO the next note (overlap the MIDI notes)
- `x` means accented (velocity 110-127). Unaccented notes use velocity 60-80.
- `.` in the Note row means rest (no note)

## Step 6: Distortion — Essential for Modern Acid

The original 303 was run through guitar pedals and overdriven mixers. Distortion is not optional.

### Saturator (first effect after Operator)
- **Drive**: 10-15 dB, **Curve**: Soft Sine or Analog Clip, **Soft Clip**: On
- **Output**: Compensate by lowering -6 to -10 dB
- Alternative: **Overdrive** for more aggressive edge — Drive 40-60%, Tone 60-70%

## Step 7: Effects Chain

1. **Saturator** — see Step 6
2. **EQ Eight** — high-pass at **40 Hz**, slight cut at 200-300 Hz if boomy
3. **Compressor** — 4:1, fast attack, auto release. Tames resonance spikes.
4. **Delay** — dotted 1/8 note, feedback 20-30%, high-pass delay return at 300 Hz. Alternative: **Ping Pong Delay** for stereo width — keep feedback low (15-25%) to avoid runaway resonance buildup from the already-distorted signal.
5. **Reverb** (optional) — short decay (0.5-1s), high-cut 3 kHz, roll off below 400 Hz. Spring character works well.

## Step 8: The Acid Trick — Independent Filter Automation

Automate the filter **base cutoff** and **resonance** independently across 4-8 bars:
- **Cutoff**: Slow sweeps up over 4 bars, sudden drops back down
- **Resonance**: Push higher during breakdowns, pull back during drops
- High resonance + high cutoff = screaming. High resonance + low cutoff = bubbling.
- Automating both with different curves creates maximum movement.

## Build Order
1. Operator: Saw D on Oscillator A only, disable B/C/D
2. Filter: 24 dB low-pass, cutoff 30-40%, resonance 60-80%
3. Filter envelope: 0 attack, 150 ms decay, 0 sustain, 0 release. Envelope amount 50-70%.
4. Amp envelope: 0 attack, 300 ms decay, 70% sustain, 80 ms release
5. Voices: 1, glide enabled at 80 ms
6. Set filter FreqVel to 70% (velocity controls squelch)
7. Program pattern: 16th notes, rests, accents on off-beats, slides via overlapping notes
8. Saturator: drive 12 dB, Soft Sine, output -8 dB
9. EQ Eight: high-pass at 40 Hz
10. Compressor: 4:1, fast attack, auto release
11. Optional: dotted 1/8 delay, short spring reverb
12. Automate filter cutoff and resonance over 4-8 bars
