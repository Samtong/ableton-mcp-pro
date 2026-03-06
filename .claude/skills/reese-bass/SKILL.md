---
name: reese-bass
description: Create Reese bass sounds using Operator. Use when the user asks for Reese bass, detuned saw bass, neuro bass, D&B bass, or warbling sub bass.
---

# Reese Bass — Operator

## Quick Reference
- **Origin**: Kevin Saunderson's "Just Want Another Chance" (1988) — two detuned sawtooth oscillators creating a phasing, warbling bass
- **Character**: Thick, rich, detuned texture with beating/phasing effect
- **Best range**: C0 to C1 (MIDI notes 24-36)
- **Use in**: Drum & Bass, Neurofunk, Dubstep, Techno

## Step 1: Operator Oscillator Setup

### Basic Patch
- Open Operator with default preset
- **Oscillator A**: Set waveform to Saw D (Saw Digital)
- **Oscillator B**: Enable, set waveform to Saw D
- Set both A and B levels to **-12 dB** (makes them equal volume)

### Critical: Parallel Routing
- Go to the **routing tab** (bottom right of Operator)
- Switch to the algorithm where **all oscillators run in parallel** (not in series)
- This bypasses FM synthesis — without this it sounds like garbage, not a Reese

### Detuning (the core of the Reese sound)
- **Oscillator B Fine tune**: +25 cents (creates the phasing/beating effect)
- Experiment with values 15-35 cents — higher = faster beating

### Sub Layer
- **Oscillator C**: Enable, leave as **sine wave** (do NOT detune this one)
- Mix in to taste — this reinforces the low-end that detuned saws can lack
- Keep C at default pitch (no detuning, no transposing)

## Step 2: Voice Settings

### Monophonic Setup
- **Voices**: Set to 1 (monophonic — bass should only play one note)
- **Glide**: Enable, set to **100-300 milliseconds**
  - Short gap between MIDI notes = jump to next note
  - Overlapping notes = smooth slide (portamento)

### Pitch Envelope (optional, for attack character)
- Enable pitch envelope in the pitch tab
- Small amount — gives an initial pitch "hit" on note attack
- Classic old-school Reese technique for adding punch

### Spread (use carefully)
- A small amount of spread (10-24%) adds stereo width
- Too much causes phasing issues in the low end
- Can be fixed with mid/side EQ later (see Step 4)

## Step 3: Effects Chain

### Glue Compressor (first in chain)
- Enable **soft clipping**
- Crank makeup gain
- Pull threshold down slightly (~5 dB of compression)
- Creates saturation on transients and glues the sound

### Auto Filter — Notch (for movement)
- Filter type: **Notch**
- LFO: Enable, set rate fairly low
- Sweep the frequency around to create the classic Reese "movement"
- Alternative: automate the filter frequency manually for more control
- Notch filter range: sweep between **200 Hz - 2 kHz** for best effect

### Auto Filter — Low-Pass (for dark Reese)
- Filter type: **Low-pass**
- Slope: **12 dB/octave** for darker sound (24 dB/octave for even more aggressive)
- Cutoff: Start around **250 Hz**, automate upward during builds
- Automate throughout the track for movement
- **Filter Drive**: Add a bit for extra grit

### Chorus (after the filter)
- Adds width and depth to a low-passed Reese
- Turn rate down, mix to taste
- Especially helpful when the low-pass makes the sound too thin

### Erosion (for airy high-end)
- Mode: **Wide Noise**
- Adds breathy, airy texture to the top end
- Adjust width and amount subtly — too much gets noisy
- Place before the final compressor

### Reverb (subtle)
- Decay: **500 ms to 2.5 seconds**
- High-cut the reverb to keep it dark (no ringing high-end)
- Helps show the movement of filter sweeps

### Final Glue Compressor
- Another Glue Compressor at the end
- Compress by about **5 dB**, enable soft clipping
- Tames dynamics and adds final saturation layer

## Step 4: Advanced Techniques

### Mid/Side EQ (essential for club playback)
- Add EQ8 after the effects chain
- Switch to **Mid/Side mode**
- On the **Side** channel: high-pass at **200 Hz** (x4 slope)
- This removes stereo information from the low end
- Keeps bass mono below 200 Hz (critical for club systems)

### Distortion Options
- **Amp** effect: Clean boost, output set to Dual, dry/wet low
- **Vinyl Distortion**: Very subtle (0.10) — adds slight stereo difference and character
- **Saturator**: For more aggressive grit

### Notch EQ Automation (phaser-like effect)
- Add EQ8 with a narrow notch
- Automate the notch frequency between **1 kHz and 10 kHz**
- Creates a phaser-like sweeping effect
- Don't sweep below 1 kHz — takes away bass impact

### Sidechain to Kick
- Sidechain compressor keyed to kick drum
- EQ the sidechain input to pick up only below ~100 Hz
- Fast attack, automatic release
- Prevents muddiness between kick and bass

### Phaser (for fills and drops)
- Place before final compression
- Keep dry/wet low for subtle movement
- Increase for fills and drops, automate back down
- Too much feedback gets distracting

## Build Order
1. Operator: Saw D on A+B, parallel routing, detune B by +25 cents
2. Add sine sub on Oscillator C
3. Set to 1 voice, enable glide (100-300 ms)
4. Glue Compressor with soft clipping
5. Auto Filter (notch) with LFO or automation for movement
6. Optional: Low-pass filter + chorus for dark Reese
7. Erosion for airy high-end texture
8. Mid/Side EQ: high-pass sides at 200 Hz
9. Final Glue Compressor (~5 dB, soft clip)
10. Sidechain to kick
