# Ableton MCP Pro

Drives Ableton Live from Claude. `AbletonMCP_Remote_Script/__init__.py` runs inside Live
and answers JSON on TCP 9877; `MCP_Server/server.py` wraps it as MCP tools. The same
commands work over raw TCP (`{"type": ..., "params": {...}}`), which is how long scripted
jobs run. Production skills live in `.claude/skills/`.

The user's machine: Live 12 Suite **12.0.15**. Live loads the Remote Script through a
symlink in `~/Music/Ableton/User Library/Remote Scripts/`; check where it points before
assuming your edit is live. Details for every point below: [memory.md](memory.md).

## Gotchas

**Reloading.** New Remote Script code needs a full Live quit and reopen. Toggling the
control surface keeps the old module. Probe with a command only the new code has.

**Never record the arrangement over MCP** (`record_arrangement`, `set_record_mode` +
play). It once truncated a whole arrangement on every track. Write the arrangement with:
- `duplicate_clip_to_arrangement`: copies a session clip with its warp, envelopes and
  loop. Audio copies land 32 beats long whatever their loop: trim by dropping a copy at
  the end point and deleting it.
- an empty `create_arrangement_midi_clip` to cut a hole in a MIDI track.
- `create_arrangement_audio_clip`, which auto-warps one-shots to 4/8/16/32 beats: read
  the clip's `length` back before timing it to a downbeat.
Check clip counts on every track after a batch.

**Capturing the master** (for `mixing-guide-mindpath`): audio track with input
Resampling, armed, `play_arrangement`, then `fire_clip` on an **empty** slot = a session
recording that never touches the arrangement. File lands in `<project>/Samples/Recorded/`.
Solo a group first to capture a stem. Start playback, then `set_song_time` while it plays:
a stopped transport restarts from its start marker.

**Transport.** `back_to_arranger` reads True while the arrangement is overridden; writing
False is the button. Before the 2026-10-02 fix the script wrote True, which silenced every
track and made meters read nothing — older notes blaming tempo automation for dead meters
were this bug.

**Reading values.** `get_device_parameters` / `get_track_info` return the **automated
value at the playhead**. A send that "won't stay" has an automation lane: act on the
return or elsewhere. Arrangement automation itself cannot be read over the API.

**Parameter mapping.** Values are normalized 0–1 and the map is linear only for some
parameters (volume: `dB = (pos − 0.85) × 40`, steeper below −18 dB; sends:
`dB = (pos − 1) × 40`). `Utility` Gain, EQ Eight frequency, Reverb decay are not linear:
bisect on the displayed value and read it back. EQ Eight filter type: send `(k+0.5)/7`.

**Meters.** `get_track_output_meter` is deflection: `dBFS ≈ 76 × d − 70`, only for what is
actually playing. For anything that matters, capture audio and measure it.

**Locators** can be placed (`set_song_time` → `ensure_cue_at_current_time`) but never
named. **MIDI pitch 60 is C3** in Live; give pitches as Hz + MIDI number.

**Mixing.** Before blaming one track for the master's peaks or spectrum, mute it and
re-capture. Compare against a profile built from the user's own references
(`make_profile.py`), not the generic profiles.

## Working with the user

The user drives Live's GUI: do not take control of the screen, ask for the clicks. They
save before letting you work and listen after each pass, so change things in measured
passes and report what moved and how to undo it.
