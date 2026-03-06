---
name: techno-drums
description: Create minimal and dark techno drum patterns. Use when the user asks for techno drums, minimal techno, dark techno, warehouse techno, or Berlin techno percussion.
---

# Minimal / Dark Techno Drums (Berlin / Warehouse Style)

## Quick Reference
- **Tempo**: 128-138 BPM (130-133 is the sweet spot)
- **Time Signature**: 4/4
- **Feel**: Hypnotic, dark, sparse but driving
- **Key distinction from hardgroove**: Less tom-driven groove, more hypnotic repetition, darker sound palette. Hardgroove leans on syncopated toms for swing; minimal/dark techno leans on relentless ride, heavy velocity shaping, and space between hits.

## Drum Elements (build in this order)

### 1. Kick — Four-on-the-Floor
- Every beat, no exceptions. The kick IS the anchor.
- **Designing in Operator**: Oscillator A set to sine wave with fixed frequency at 40-55 Hz. Add a pitch envelope that sweeps from ~200-400 Hz down to the fundamental in 30-50ms — this creates the transient click on top of the sub body. Set amp envelope decay to ~200-350ms, no sustain. Two critical settings: (1) set the envelope loop mode to **Trigger** so the decay curve plays fully regardless of note length — essential for consistent drum hits; (2) raise the **Phase** parameter to ~180-250° so the sine wave starts near its peak rather than the zero crossing, producing a harder, more precise transient click at the note onset.
- **Layering**: Duplicate the Operator patch on a second chain. First chain handles the sub (pure sine, 40-55 Hz fundamental). Second chain handles the click (short pitch sweep, high-passed at 200 Hz). Group both in an Instrument Rack.
- Velocity: 110-127, consistent. Do NOT vary kick velocity in minimal techno — it must be a metronome.

### 2. Clap — Dry and Tight
- Hits on beats 2 and 4 (standard backbeat).
- Use a tight, short 909-style clap or layer a noise burst (white noise through a band-pass at 1.5-3 kHz, amp decay ~60ms) alongside the clap sample for texture.
- **Synthesized clap in Operator** (alternative to samples): Use the all-parallel algorithm so all 4 oscillators output independently. Set each to white noise with a short decay envelope in Trigger mode. Stagger their attack times: Osc A at 0ms, Osc B at ~30ms, Osc C at ~60ms, Osc D at ~90ms — this simulates multiple hands clapping in quick succession (the Roland 808 technique). Give the last oscillator a noticeably longer decay (150-250ms) — this acts as built-in room ambience, since decaying noise closely approximates short reverb reflections. High-pass the result at ~300 Hz with EQ Eight and boost a narrow band around 1-2 kHz for snap.
- Keep it dry on the channel — send to a short dark reverb return (see Send Effects below). If using the synthesized clap with the long-tail trick above, you may need less send reverb.
- Velocity: 95-110, mostly consistent with subtle 3-5 point variation for life.

### 3. Closed Hi-Hats — Velocity-Sculpted 16ths
- Program on every 16th note, then sculpt with velocity.
- **Velocity pattern** (per beat, 4 sixteenths): strong-weak-medium-weak. Example values: 100-45-75-35.
- This velocity variation is the primary groove engine. Automate filter cutoff from velocity in Simpler/Sampler so quiet hits are also darker.
- Set Simpler release to 0 so note length controls hat duration — draw shorter notes for tighter, more clipped hits.
- Open hat: use sparingly, once every 2-4 bars on an offbeat for a breathing point. Keep it short with fast decay.

### 4. Ride — The Signature Element
- A driving ride on 8th notes or 16th notes is what separates dark/minimal techno from other styles.
- Slightly overdrive the ride sample — run through Saturator with a few dB of drive for metallic, harsh character.
- Velocity: alternate between 85-100 on downbeats and 55-70 on upbeats.
- Convert Simpler to Sampler for velocity-to-filter mapping: lower velocity = more filtered = darker timbre.
- The ride should sit forward in the mix, almost as loud as the hats. It provides the hypnotic drive.

### 5. Percussion — Synthesized Hits
- **FM percussion in Operator**: Use oscillators A+B with FM. Oscillator B modulates A at a high ratio (5:1 or 7:1). Very short amp envelope (decay 20-80ms, no sustain) in **Trigger** mode. Detune for metallic, inharmonic character. For richer membrane-like tones, use the dual-chain algorithm to run two independent sine oscillators (copy Osc A settings to Osc C, then detune C slightly) — the beating between the two frequencies mimics the complex modal vibration of a real drum skin. Each hit should be unique — tune and shape differently.
- **Noise bursts**: White or pink noise through a resonant band-pass filter (800-4000 Hz). Sweep the filter frequency per hit for variety. Amp decay 15-50ms.
- **Resonant clicks**: Operator with a very short sine burst (decay <10ms) at 1-4 kHz. Add slight feedback or resonance for a woody, clicking quality.
- Place percussion on offbeats and syncopated positions — never on the kick.

## ASCII Patterns (1 bar = 16 steps, X = hard hit, x = soft hit, O = open hat)

### Pattern 1 — Minimal (sparse, lots of space)
```
Step:  1 . . . 2 . . . 3 . . . 4 . . .
Kick:  X . . . X . . . X . . . X . . .
Clap:  . . . . X . . . . . . . X . . .
Hat:   x . . . x . . . x . . . x . . .
Ride:  . . . . . . . . . . . . . . . .
Perc:  . . . . . . . . . . x . . . . .
```
Stripped to the bone. Hats on quarter notes only. A single percussion hit on the "and" of beat 3 is the only syncopation. Use this for intros, breakdowns, or stripped-back sections.

### Pattern 2 — Driving (busier hats, ride, more percussion)
```
Step:  1 . . . 2 . . . 3 . . . 4 . . .
Kick:  X . . . X . . . X . . . X . . .
Clap:  . . . . X . . . . . . . X . . .
Hat:   X x x x X x x x X x x x X x x x
Ride:  . X . X . X . X . X . X . X . X
Perc:  . . . x . . x . . . . x . x . .
```
Full 16th-note hats with strong velocity shaping (capitals = 90-110, lowercase = 35-65). Ride on 8th-note offbeats. Scattered percussion fills the gaps. This is the main-room, peak-time pattern.

### Pattern 3 — Hypnotic (polyrhythmic, odd-length loops)
```
Step:  1 . . . 2 . . . 3 . . . 4 . . .
Kick:  X . . . X . . . X . . . X . . .
Clap:  . . . . X . . . . . . . X . . .
Hat:   X x x x X x x x X x x x X x x x
Ride:  . X . X . X . X . X . X . X . X
Perc1: x . . x . . x . . x . . x . . x   (5-step cycle: shifts against 16-step bar)
Perc2: . . x . . . . . x . . . . . x .   (3-beat accent cycle over 4/4)
```
The hypnotic quality comes from polyrhythmic percussion. Perc1 repeats every 5 sixteenths, creating a pattern that takes 5 bars to fully cycle. Perc2 accents every 3 beats, phasing against the 4-beat bar. Set these as separate clips with different loop lengths — 5/16 and 3/4 respectively — so they phase naturally over time.

## Send Effects

### Return A — Short Dark Reverb
- Use Convolution Reverb or Reverb with decay 0.4-0.8 seconds (no long tails — keeps it tight)
- High-cut at 3-5 kHz to keep the reverb dark and subterranean
- Low-cut at 200 Hz to prevent mud
- Pre-delay: 10-20ms
- Send clap and percussion to this return at 25-40%

### Return B — Ping-Pong Delay
- Ping-pong delay synced to 1/8 or 3/16 for rhythmic interest
- Feedback: 25-40% (2-3 repeats, not runaway)
- High-pass the delay return at 400-600 Hz so delayed hits stay out of the low end
- Send select percussion hits only — never the kick, rarely the clap

## Processing

### Parallel Compression (Drum Bus)
- Route all drum tracks to a bus. Create a return with Glue Compressor: fast attack (0.1-1ms), fast release (10-50ms), ratio 10:1, threshold slammed low.
- Blend at 25-40% alongside the dry drums for density without killing transients.

### Drum Buss (Ableton)
- Add Drum Buss on the drum group for final glue.
- **Boom**: subtle (10-20%) to add controlled low-end resonance under the kick.
- **Crunch**: soft clip mode, drive at 15-30% for gentle saturation across all elements.
- **Transients**: boost slightly to keep hits snappy after compression.
- **Damping**: pull the high-frequency damping down to 7-9 kHz to darken the overall drum tone — this is the warehouse character.

## Build Order
1. Program kick — four-on-the-floor, design or select a deep, dark kick
2. Add clap on 2 and 4, layer with noise burst for texture
3. Program closed hats on 16ths with velocity shaping (strong-weak-medium-weak)
4. Add ride on 8th-note offbeats, overdrive slightly for metallic character
5. Design 2-3 synthesized percussion hits in Operator (FM hits, noise bursts, clicks)
6. Place percussion in syncopated positions, experiment with odd-length loops for hypnotic phasing
7. Set up send effects: short dark reverb (Return A), ping-pong delay with high-pass (Return B)
8. Send clap and percussion to reverb and delay returns
9. Add parallel compression on the drum bus for density
10. Apply Drum Buss for final glue — use damping to darken the top end
