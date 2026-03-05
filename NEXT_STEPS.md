# Ableton MCP Extended - Next Steps

Roadmap for achieving full Ableton control via MCP.

## Phase 1: Core Clip & Track Management

Essential CRUD operations that are currently missing.

- [ ] **Delete clip** — `delete_clip(track_index, clip_index)` — call `clip_slot.delete_clip()`
- [ ] **Delete/remove device** — `delete_device(track_index, device_index)` — call `track.delete_device(device_index)`
- [ ] **Create audio track** — `create_audio_track(index)` — call `song.create_audio_track(index)`
- [ ] **Delete track** — `delete_track(track_index)` — call `song.delete_track(track_index)`
- [ ] **Duplicate clip** — `duplicate_clip(track_index, clip_index)` — call `clip_slot.duplicate_clip_to(target_slot)`
- [ ] **Duplicate track** — `duplicate_track(track_index)` — call `song.duplicate_track(track_index)`
- [ ] **Set clip loop settings** — `set_clip_loop(track_index, clip_index, loop_start, loop_end, looping)` — set `clip.loop_start`, `clip.loop_end`, `clip.looping`

## Phase 2: Mixing & Routing

Complete mixer control beyond volume and panning.

- [ ] **Mute track** — `set_track_mute(track_index, mute)` — set `track.mute`
- [ ] **Solo track** — `set_track_solo(track_index, solo)` — set `track.solo`
- [ ] **Arm track** — `set_track_arm(track_index, arm)` — set `track.arm`
- [ ] **Send levels** — `set_send_level(track_index, send_index, value)` — set `track.mixer_device.sends[send_index].value`
- [ ] **Track routing** — `set_track_input/output(track_index, routing_type, channel)` — set `track.input_routing_type`, `track.output_routing_type`, etc.

## Phase 3: Transport & Scene Control

Session and arrangement transport features.

- [ ] **Scene launch** — `fire_scene(scene_index)` — call `song.scenes[scene_index].fire()`
- [ ] **Create scene** — `create_scene(index)` — call `song.create_scene(index)`
- [ ] **Set time signature** — `set_time_signature(numerator, denominator)` — set `song.signature_numerator`, `song.signature_denominator`
- [ ] **Quantization** — `set_clip_trigger_quantization(value)` — set `song.clip_trigger_quantization`
- [ ] **Record** — `start_recording()` — set `song.record_mode`
- [ ] **Metronome** — `set_metronome(on)` — set `song.metronome`

## Phase 4: Arrangement View

Move beyond Session view clips to full arrangement support.

- [ ] **Switch to arrangement view** — need to understand how arrangement is accessed via LOM
- [ ] **Set arrangement position** — `set_current_song_time(time)` — set `song.current_song_time`
- [ ] **Create arrangement clip** — research how to create clips directly in arrangement tracks (may need `track.arrangement_clips` or duplicating from session)
- [ ] **Copy session clip to arrangement** — potential workflow: fire clips at specific song positions while recording into arrangement
- [ ] **Set arrangement loop** — `set_arrangement_loop(start, end, on)` — set `song.loop_start`, `song.loop_length`, `song.loop`
- [ ] **Arrangement overdub** — `song.arrangement_overdub`
- [ ] **Get arrangement clips** — read clips from arrangement timeline for each track

### Arrangement Strategy

**Key LOM properties (confirmed from API docs):**
- `song.current_song_time` — get/set playback position in beats
- `song.record_mode` — get/set recording state (0=off, 1=on)
- `song.arrangement_overdub` — get/set arrangement overdub
- `song.session_record` — get/set session recording
- `song.back_to_arranger` — return to arrangement from session
- `song.loop` / `song.loop_start` / `song.loop_length` — arrangement loop control
- `song.is_playing` — playback state

**There is no direct "create clip at arrangement position" API.** The LOM only exposes arrangement clips for reading, not writing. The proven approaches are:

#### Approach 1: Record Session to Arrangement (recommended)
Record session clips into the arrangement by triggering playback with arrangement record enabled.

Build a `record_session_to_arrangement(scene_index, start_time, bars)` command that:
1. `song.current_song_time = start_time` — seek to position
2. `song.record_mode = 1` — enable arrangement recording
3. `song.scenes[scene_index].fire()` — fire the scene
4. Wait for N bars (calculate from tempo)
5. `song.record_mode = 0` — stop recording
6. `song.stop_playing()` — stop playback

This captures the session clips (with all effects and mixing) into arrangement clips.

#### Approach 2: Layered Recording
For more complex arrangements, record multiple passes:
1. Record drums for 32 bars
2. Record bass for bars 8-32
3. Record chords for bars 16-32
This builds up an arrangement with intro/buildup/drop structure.

#### Required commands to implement:
- [ ] `set_song_time(time)` — set `song.current_song_time`
- [ ] `set_record_mode(on)` — set `song.record_mode`
- [ ] `set_arrangement_overdub(on)` — set `song.arrangement_overdub`
- [ ] `set_back_to_arranger()` — set `song.back_to_arranger = True`
- [ ] `fire_scene(scene_index)` — fire all clips in a scene
- [ ] `set_loop(on, start, length)` — control arrangement loop
- [ ] `get_arrangement_info()` — read `song.current_song_time`, `song.is_playing`, `song.record_mode`, etc.
- [ ] `record_session_to_arrangement(scene_index, start_time, bars)` — high-level command combining the above

## Phase 5: Automation

Parameter automation within clips.

- [ ] **Get clip envelopes** — `get_clip_envelopes(track_index, clip_index)` — read `clip.automation_envelope`
- [ ] **Set automation point** — `insert_automation_value(track_index, clip_index, parameter_id, time, value)`
- [ ] **Clear automation** — `clear_envelope(track_index, clip_index, parameter_id)` — call `clip.clear_envelope(parameter_id)`

## Phase 6: Advanced

Nice-to-haves for a complete integration.

- [ ] **Undo** — `undo()` — call `song.undo()`
- [ ] **Redo** — `redo()` — call `song.redo()`
- [ ] **Save** — `save()` — call `song.save()`
- [ ] **Audio clip support** — loading audio files onto audio tracks (may require browser item loading)
- [ ] **Capture MIDI** — `song.capture_midi()`
- [ ] **Groove pool** — apply groove templates to clips

## Priority Order

For the most immediate impact on music-making workflow:

1. **Phase 4** (Arrangement) — unlocks full song creation, not just loops
2. **Phase 1** (CRUD) — needed for iterating without accumulating dead clips/tracks
3. **Phase 2** (Mixing) — mute/solo especially useful during composition
4. **Phase 3** (Transport) — scene launching for live performance
5. **Phase 5** (Automation) — adds movement and expression
6. **Phase 6** (Advanced) — polish and convenience
