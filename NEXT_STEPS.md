# Ableton MCP Extended - Next Steps

Roadmap for achieving full Ableton control via MCP.

## Completed

### Core Clip & Track Management
- [x] **Delete clip** — `delete_clip(track_index, clip_index)`
- [x] **Create audio track** — `create_audio_track(index)`
- [x] **Delete track** — `delete_track(track_index)`
- [x] **Duplicate clip** — `duplicate_clip(track_index, clip_index, target_index)`

### Mixing
- [x] **Set track volume** — `set_track_volume(track_index, volume)` (0.0–1.0)
- [x] **Set track panning** — `set_track_panning(track_index, panning)` (0.0–1.0, 0.5=center)
- [x] **Mute track** — `set_track_mute(track_index, mute)`
- [x] **Solo track** — `set_track_solo(track_index, solo)`
- [x] **Master/return track support** — `track_index: -1` for master, `-2`/`-3` for returns

### Transport & Scene Control
- [x] **Scene launch** — `fire_scene(scene_index)`
- [x] **Create scene** — `create_scene(index)`
- [x] **Delete scene** — `delete_scene(scene_index)`
- [x] **Set scene name** — `set_scene_name(scene_index, name)`

### Arrangement View
- [x] **Get arrangement info** — `get_arrangement_info()` — transport state, loop, tempo
- [x] **Set song time** — `set_song_time(time)` — with retry logic
- [x] **Set record mode** — `set_record_mode(on)`
- [x] **Set arrangement overdub** — `set_arrangement_overdub(on)`
- [x] **Set back to arranger** — `set_back_to_arranger()`
- [x] **Set arrangement loop** — `set_arrangement_loop(on, start, length)`
- [x] **Get arrangement clips** — `get_arrangement_clips(track_index)` — per-track
- [x] **Get full arrangement** — `get_full_arrangement()` — all tracks, scenes, tempo
- [x] **Record arrangement** — `record_arrangement(sections)` — high-level command with background threading

### Device Control
- [x] **Get device parameters** — `get_device_parameters(track_index, device_index)`
- [x] **Set device parameter** — `set_device_parameter(track_index, device_index, parameter_index, value)`
- [x] **Batch set device parameters** — `batch_set_device_parameters(...)`
- [x] **Load instrument/effect** — `load_instrument_or_effect(track_index, uri)`

---

## Phase 1: Recording Accuracy (High Priority)

The biggest gap — arrangement recording uses `time.sleep` which drifts. Transitions end up 1-2 beats off after long recordings.

- [ ] **Beat-accurate scene timing** — Poll `song.current_song_time` in a tight loop instead of `time.sleep` to fire scenes at exact beat positions. This would eliminate timing drift entirely.
- [ ] **Clip trigger quantization** — `set_clip_trigger_quantization(value)` — set `song.clip_trigger_quantization` to snap scene fires to bar boundaries. Values: 0=None, 4=1 Bar, 5=2 Bars, etc.
- [ ] **Verify recording results** — After `record_arrangement`, automatically call `get_full_arrangement` and validate that clip boundaries match expected positions.

## Phase 2: Missing CRUD Operations

- [ ] **Delete/remove device** — `delete_device(track_index, device_index)` — call `track.delete_device(device_index)`
- [ ] **Duplicate track** — `duplicate_track(track_index)` — call `song.duplicate_track(track_index)`
- [ ] **Set clip loop settings** — `set_clip_loop(track_index, clip_index, loop_start, loop_end, looping)`
- [ ] **Get/set clip notes** — read existing notes from a clip (currently can only add)

## Phase 3: Mixing & Routing

- [ ] **Arm track** — `set_track_arm(track_index, arm)` — set `track.arm`
- [ ] **Send levels** — `set_send_level(track_index, send_index, value)` — set `track.mixer_device.sends[send_index].value`
- [ ] **Track routing** — `set_track_input/output(track_index, routing_type, channel)`
- [ ] **Set time signature** — `set_time_signature(numerator, denominator)`
- [ ] **Metronome** — `set_metronome(on)` — set `song.metronome`

## Phase 4: Automation

Parameter automation within clips — adds movement and expression.

- [ ] **Get clip envelopes** — `get_clip_envelopes(track_index, clip_index)` — read automation data
- [ ] **Set automation point** — `insert_automation_value(track_index, clip_index, parameter_id, time, value)`
- [ ] **Clear automation** — `clear_envelope(track_index, clip_index, parameter_id)`

## Phase 5: Advanced

Nice-to-haves for a complete integration.

- [ ] **Undo** — `undo()` — call `song.undo()`
- [ ] **Redo** — `redo()` — call `song.redo()`
- [ ] **Save** — `save()` — call `song.save()`
- [ ] **Audio clip support** — loading audio files onto audio tracks
- [ ] **Capture MIDI** — `song.capture_midi()`
- [ ] **Groove pool** — apply groove templates to clips
- [ ] **Cross-fader** — control crossfader assignment and position

## Priority Order

1. **Phase 1** (Recording Accuracy) — makes arrangement recording production-ready
2. **Phase 2** (CRUD) — needed for iterating without accumulating dead clips/tracks
3. **Phase 3** (Mixing & Routing) — send levels and routing for complex mixes
4. **Phase 4** (Automation) — adds movement and expression to arrangements
5. **Phase 5** (Advanced) — polish and convenience
