---
name: growl-bass
description: Create growl bass sounds using FM synthesis in Operator. Use when the user asks for growl bass, dubstep bass, FM bass, wobble bass, or aggressive bass sound design.
---

# Growl Bass — FM Synthesis in Operator

## Quick Reference
- **Tempo**: 140-150 BPM (dubstep/bass music)
- **Key**: Minor keys
- **Core idea**: FM synthesis creates harmonic complexity — one oscillator modulates another's frequency, producing growling, vowel-like timbres
- **Character**: Aggressive, vocal-quality bass that "growls" when you automate the modulation amount

## Step 1: Operator FM Setup

### Algorithm / Routing
- Open Operator, go to the routing tab
- Choose an algorithm where **Oscillator B modulates Oscillator A** (B → A)
- Oscillators C and D also feed into A for extra harmonics

### Oscillator A (Carrier — the sound you hear)
- Waveform: Start with **sine wave**
- Go to the oscillator tab and add harmonics to the waveform display
- Adding higher harmonics creates a fuller, grittier carrier tone
- Level: -12 dB

### Oscillator B (Modulator — creates the growl)
- Waveform: **Sine wave** (default)
- Level: Start at **-9 dB** (this is the FM amount — higher = more harmonics/growl)
- **Fine tune**: +33 cents (detuning the modulator creates movement and richness)
- Experiment with **coarse tuning** — different ratios create different timbres:
  - 1:1 ratio = buzzy
  - 2:1 ratio = brighter, more aggressive
  - 0.5:1 ratio = sub-harmonic rumble

### Oscillators C and D (additional modulators)
- Route both to also modulate Oscillator A
- Fine tune both to +33 cents (same as B, for consistency)
- Set levels to different small amounts: e.g., **-12 dB and -15 dB**
- Experiment with adding harmonics to these oscillators too
- More modulator harmonics = sharper, more aggressive sound
- Be careful: too many harmonics + distortion = just noise

## Step 2: Voice & Pitch Settings

### Monophonic
- **Voices**: 1 (monophonic)
- **Glide**: Enable, amount ~100 ms
- Notes slide into each other — essential for expressive bass lines

### Note Technique
- Cut off each note before starting the next for jumps
- Overlap notes for slides
- Use short notes (staccato) for rhythmic growl patterns

## Step 3: The Growl — Macro Control

### Map Modulator Level to Macro
- The key to a growl bass is **automating how much FM modulation happens**
- Map Oscillator D's level to **Macro Knob 1**
- When the macro is low: clean, simple tone
- When the macro is high: growly, harmonically rich, aggressive
- This is your primary performance control

### Dry/Wet Rack for Blend Control
- Group Operator into an Audio Effect Rack
- Create two chains: **Wet** (with effects) and **Dry** (clean sub)
- Map both chain volumes to a single macro knob with **inverted ranges**
- Macro up = more growl effect, less clean sub
- Macro down = more clean sub, less growl
- This gives you a blend between clean and aggressive

## Step 4: Effects Chain (on the Wet chain)

### EQ8 — Shape the Growl
- High-pass below **100 Hz** (the Dry chain handles the sub)
- Boost mid frequencies where the growl lives (500 Hz - 3 kHz)
- Cut harsh frequencies above 8 kHz if needed

### Multiband Processing
- Split into frequency bands and process differently:
  - **Low (30-150 Hz)**: Keep clean, maybe light compression
  - **Mid (150-3500 Hz)**: This is where the growl lives — add distortion, chorus, phaser
  - **High (3500+ Hz)**: Add air, light saturation

### Cabinet (Amp effect)
- Turn mix all the way up
- Adds speaker character and tames harsh digital FM artifacts
- Experiment with different cabinet types

### Saturator / Distortion
- **Saturator** in saturation mode
- Adds warmth and harmonic density
- Can also use the **Color** slider — at 100% it really brings out the formant character
- Keep dry/wet balanced

### Phaser (for vowel movement)
- Creates the "wah" vowel quality
- Automate the dry/wet throughout the track
- More phaser = more obvious vocal quality
- Map to a macro for live control

### Formant Filter
- Activate the format filter in the filter section
- This adds vowel-like character (ah, ee, oh sounds)
- Automate between vowel positions for the classic "talking bass" effect

## Step 5: Automation — Bringing It to Life

### Key Parameters to Automate
1. **FM amount (Oscillator D level)**: The main growl control
2. **Phaser dry/wet**: Vowel movement
3. **Filter cutoff**: Brightness changes
4. **Dry/wet macro**: Sub vs growl blend

### Automation Technique
- Write 4-8 bar automation patterns
- Copy and paste, then modify each repetition slightly
- Layer different automation curves (FM + phaser + filter) for complex movement
- Use faster automation during drops, slower during builds

## Step 6: Final Processing

### EQ8 (after effects)
- Clean up any harsh resonances the FM + distortion created
- Boost high frequencies if the sound lacks presence

### Compressor
- Tame the dynamics (FM synthesis can be very dynamic)
- Fast attack, automatic release
- Moderate ratio (4:1)
- Keeps the level consistent as automation changes the timbre

### Sidechain to Kick
- Essential — the growl bass takes up a lot of space
- Fast attack, medium release

## Build Order
1. Operator: Set routing so B → A, C → A, D → A
2. Oscillator A: sine + harmonics. B/C/D: sine, detuned +33 cents, different levels
3. Set to 1 voice, enable glide
4. Map Oscillator D level to Macro 1 (growl amount)
5. Group into rack with Dry (clean sub) and Wet (growl) chains
6. Wet chain: EQ8 → Cabinet → Saturator → Phaser
7. Automate FM amount + phaser for movement
8. Final EQ + compressor + sidechain
