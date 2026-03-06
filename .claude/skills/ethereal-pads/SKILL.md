---
name: ethereal-pads
description: Create ethereal pads that work in any synth. Use when the user asks for ethereal pads, ambient pads, dreamy pads, lush pads, or wash textures.
---

# Ethereal Pads

## Core Philosophy
Ethereal is about the MUSIC first, not just reverb and delay. Think about what makes a sound ethereal — dreamy chord voicings, layers blending together, static drone notes against moving chords.

## Chord Voicing — Split Across Layers
- **Don't play full chords on one synth** — spread chord voices across 2+ layers
- Layer 1 plays some notes (e.g. root + 5th low), Layer 2 plays others (e.g. 3rd + 7th high)
- Together they form complete chords (major 7ths work especially well for ethereal feel)
- Each layer has its own sound/texture, creating depth

## Chord Choices
- **Major 7th chords** are the most dreamy/ethereal
- Play with inversions — move voices up octaves for more open, epic voicings
- Keep progressions simple but voice them creatively

## Sound Design — Wavetables
- Don't just use basic saw/square/sine — use wavetable positions for richer textures
- The same wavetables used for dubstep bass become ethereal pads when:
  - Played in higher octaves
  - Low-pass filtered
  - Slightly detuned with minimal unison (voices high, amount very low ~1.6%)
- **Wavetable starting point**: try the "Analog/Digital" category — set Unison voices to 4-6, detune 1-2%, filter to LP with cutoff ~60-70% and resonance at 0%
- Keep wavetable position STATIC on chord layers (movement on chords gets messy)
- Save wavetable movement for single-note parts like drones or leads
- **Subtle distortion for organic texture**: add a sign fold or soft clip distortion to the synth effects chain with moderate drive, then use a post-filter (cutoff all the way up, resonance all the way down) and adjust the blend knob to tame the output level. This lets you dial in distortion that changes only the harmonic content without boosting perceived loudness — you can freely adjust the distortion mix without volume jumps. Sign fold is especially good for pads because it creates interesting dissonance between simultaneous notes that soft clip doesn't produce.

## Evolving Filter Movement
- Assign a **slow LFO to the filter cutoff** for gentle, breathing motion across the pad
- Use a sine or triangle LFO shape at a very slow rate (0.1–0.5 Hz) — this creates gradual sweeps that keep the texture alive without drawing attention
- Keep depth moderate so the movement stays subtle — you want the sound to shimmer and drift, not obviously wobble
- Add a slight resonance boost to emphasize the sweep point as it passes through the harmonics
- This pairs especially well with low-passed layers: the cutoff breathes up and down while the overall filter cap keeps everything blended

## The Drone Note
- Add a layer that plays ONE sustained note while chords change underneath
- Pick a note from the scale: major 7th (most dreamy), 5th, root, or 3rd
- This static element against moving chords = very ethereal
- **Simple Operator patch**: sine wave oscillator, no filter, long attack (500ms+), infinite sustain — add a Chorus effect for stereo width
- Use similar sound design as pad layers

## The Hidden Lead
- Add a lead that plays single notes following the chords
- Notes should be chord tones you've already used (5th, root, 7th, 3rd)
- Make it very deep/filtered so it becomes part of the pad wash
- **Wavetable tip**: the "Distortion" category wavetables sound great here — their harmonics cut through the wash subtly
- This is where wavetable movement works well (one LFO slow, one fast)

## Noise Underlayer
- Layer **filtered noise underneath** the pad layers to add analog warmth and air
- Use white or pink noise run through a band-pass or high-pass filter so it sits in the upper frequencies without muddying the low end
- **Route noise to its own filter** (e.g. Filter 2) set to band-pass mode, then enable key tracking on that filter — this makes the noise frequency center follow the played notes so it blends naturally with the synth rather than sitting as a static wash. Turn resonance down on this filter so it stays wide and subtle.
- Keep the noise level very low — it should be felt more than heard, filling in the gaps between harmonic content
- Automate the noise filter cutoff or level across sections (e.g. bring it up in choruses, pull it back in verses) for subtle dynamic shifts
- This works especially well combined with the drone note layer — the noise gives it a tactile, breathy quality

## The Low-Pass Secret
- **Low-pass everything** — this is key to ethereal blending
- Low-pass each layer individually
- Then low-pass AGAIN after reverb/delay on the group
- Without low-pass: sounds in your face, not ethereal
- With low-pass: layers melt together into a wash

## Effects
- Heavy reverb and delay on each layer
- These become part of the sound, not just effects
- The cascading reverb/delay tails are essential to the ethereal quality
- **Reverb**: decay 5-10s, pre-delay 30-60ms, diffusion high — **Delay**: ping-pong mode, 3/16 or dotted 8th time, feedback 30-40%
- **Chorus for width**: add a chorus effect on pad layers with a slow rate (0.5–1 Hz) and moderate depth — this thickens the sound and spreads it across the stereo field without obvious modulation artifacts
- Set chorus feedback around 20–30% for a subtle shimmer; too much feedback makes it metallic
- Place chorus **before** reverb in the chain so the widened signal feeds into the reverb space naturally
- **Chorus-as-reverb trick**: set a chorus effect's tempo to "freeze" mode, turn feedback all the way up, add some depth and delay time — this creates a lush, infinite-sustain reverb-like wash. Link an envelope to the chorus spread amount so each new note ducks the spread briefly, giving you a dynamic reverb that stays clean on attack but builds a rich tail between notes. Layer a real reverb (size ~80%, mix ~30%, low end cut) on top to smooth out the metallic edge

## Build Order
1. Two chord layers splitting the same chord voices between them
2. Add drone note on a dreamy scale degree (major 7th recommended)
3. Add hidden lead playing chord tones with wavetable movement
4. Add a filtered noise underlayer for breathy texture
5. Assign slow LFOs to filter cutoffs for evolving movement
6. Low-pass each layer individually
7. Add chorus for width, then reverb and delay (generous amounts)
8. Low-pass the group/bus after reverb for final blending
