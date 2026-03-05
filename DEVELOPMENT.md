# Ableton MCP Extended - Development Guide

Everything learned from developing and extending this Ableton Live MCP integration.

## Architecture Overview

The system has three components:

1. **MCP Server** (`MCP_Server/server.py`) — A FastMCP Python server that Claude (or any MCP client) communicates with. It exposes tools like `get_session_info`, `create_clip`, `set_device_parameter`, etc. When a tool is called, it opens a TCP socket connection to the Remote Script running inside Ableton.

2. **Remote Script** (`AbletonMCP_Remote_Script/__init__.py`) — A Python `ControlSurface` script that runs inside Ableton Live. It listens on TCP port **9877** for JSON commands from the MCP server. It has direct access to the Ableton Live Object Model (LOM) — tracks, clips, devices, parameters, etc.

3. **Hybrid Server** (`Ableton-MCP_hybrid-server/AbletonMCP_UDP/__init__.py`) — An alternative Remote Script that also supports UDP on port 9878 for low-latency parameter control. Useful as a reference implementation.

### Communication Flow

```
Claude → MCP Server (FastMCP) → TCP socket (port 9877) → Remote Script (inside Ableton)
```

Commands are JSON objects: `{"command": "command_name", "params": {...}}`
Responses are JSON objects: `{"status": "success", "result": {...}}`

## Remote Script Installation & Deployment

### Location

The Remote Script must be installed at:
```
/Applications/Ableton Live 12 Suite.app/Contents/App-Resources/MIDI Remote Scripts/AbletonMCP/
```

The directory contains `__init__.py` (the script) and a `__pycache__/` directory (compiled bytecode).

### Updating the Script

This is the most error-prone part of the workflow. Follow these steps exactly:

1. **Delete the old file first, then copy:**
   ```bash
   rm "/Applications/Ableton Live 12 Suite.app/Contents/App-Resources/MIDI Remote Scripts/AbletonMCP/__init__.py"
   cp AbletonMCP_Remote_Script/__init__.py "/Applications/Ableton Live 12 Suite.app/Contents/App-Resources/MIDI Remote Scripts/AbletonMCP/__init__.py"
   ```
   macOS app bundle protection can cause `cp` to silently fail (it reports success but doesn't actually overwrite). Always `rm` first.

2. **Verify the copy worked:**
   ```bash
   wc -l "/Applications/Ableton Live 12 Suite.app/Contents/App-Resources/MIDI Remote Scripts/AbletonMCP/__init__.py"
   ```
   Compare line count with your source file.

3. **Delete the bytecode cache:**
   ```bash
   rm -rf "/Applications/Ableton Live 12 Suite.app/Contents/App-Resources/MIDI Remote Scripts/AbletonMCP/__pycache__"
   ```
   Ableton caches compiled `.pyc` files. If you don't clear this, it will keep running the old version.

4. **Fully restart Ableton Live.** Toggling the Control Surface in Preferences (Link/Tempo/MIDI → set to None → set back to AbletonMCP) does NOT reliably reload the script. A full quit and relaunch is required.

5. **Restart the MCP server** after Ableton is back up and the Control Surface is active.

## Adding New Commands

### Threading Model

Ableton's Live Object Model is NOT thread-safe. The Remote Script handles this with two execution paths:

- **Read-only commands** (e.g., `get_session_info`, `get_track_info`, `get_device_parameters`) can run directly on the TCP socket thread. They only read state and don't modify anything.

- **State-modifying commands** (e.g., `create_clip`, `set_device_parameter`, `fire_clip`) MUST be scheduled on Ableton's main thread using:
  ```python
  self.schedule_message(0, task)
  ```
  These use a `Queue` to pass the result back to the socket thread, which waits for the response.

### Step-by-Step: Adding a New Command

#### 1. Remote Script (`AbletonMCP_Remote_Script/__init__.py`)

**For a read-only command**, add handling in the socket thread's command dispatch (around where `get_session_info` is handled):
```python
elif command == "your_new_command":
    result = self._your_new_method(params.get("param1"), params.get("param2"))
```

**For a state-modifying command**, add it to the list of modifying commands and add routing in `main_thread_task`:
```python
# In the modifying commands list:
if command in ["create_clip", "add_notes_to_clip", ..., "your_new_command"]:

# In main_thread_task routing:
elif command == "your_new_command":
    result = self._your_new_method(params.get("param1"), params.get("param2"))
```

Then implement the method:
```python
def _your_new_method(self, param1, param2):
    try:
        # Access Ableton objects via self._song
        track = self._song.tracks[track_index]
        # Do stuff...
        return {"status": "done", "detail": "..."}
    except Exception as e:
        self.log_message("Error in your_new_method: " + str(e))
        raise
```

#### 2. MCP Server (`MCP_Server/server.py`)

Add a new `@mcp.tool()` function:
```python
@mcp.tool()
def your_new_command(ctx: Context, param1: int, param2: str) -> str:
    """Description of what this command does."""
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("your_new_command", {
            "param1": param1,
            "param2": param2
        })
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error in your_new_command: {str(e)}")
        return f"Error: {str(e)}"
```

If it's a modifying command, add it to the `is_modifying_command` list in the server as well.

## Mixing — Track Volume & Panning

### Setting Levels

Use `set_track_volume(track_index, volume)` and `set_track_panning(track_index, panning)` to mix tracks.

- **Volume**: normalized 0.0–1.0 (0.0 = silent, 0.85 = default, 1.0 = max)
- **Panning**: normalized 0.0–1.0 (0.0 = full left, 0.5 = center, 1.0 = full right)

### Master Track

Use `track_index: -1` to target the master track. This works for:
- `set_track_volume` / `set_track_panning`
- `get_device_parameters` / `set_device_parameter` / `batch_set_device_parameters`
- `load_instrument_or_effect` (for loading effects on master)

Return tracks can be accessed with `track_index: -2` (Return A), `-3` (Return B), etc.

### Typical Techno Mix Starting Points

| Track | Volume | Pan |
|-------|--------|-----|
| Kick | 0.85 | Center (0.5) |
| Bass | 0.75 | Center (0.5) |
| Chords/Pads | 0.55 | Center (0.5) |
| Snare | 0.70 | Center (0.5) |
| Hi-Hat | 0.58 | Slight right (0.62) |
| Clap | 0.63 | Slight left (0.38) |

### Master Chain

A typical master chain for techno: Glue Compressor → EQ Eight → Limiter. Load presets via URI (e.g., `query:AudioFx#Glue%20Compressor:FileId_48034` for "Mastering - Gentle Limiter").

## Device Parameter Control

Parameters are accessed by track index → device index → parameter index.

### Normalized Values

All parameter values use a **normalized 0.0–1.0 range**, regardless of the parameter's actual range. The conversion is:
```
actual_value = param.min + normalized_value * (param.max - param.min)
normalized_value = (param.value - param.min) / (param.max - param.min)
```

### Workflow

1. Call `get_device_parameters(track_index, device_index)` to see all parameters with their names, current values, ranges, and indices.
2. Call `set_device_parameter(track_index, device_index, parameter_index, value)` to set a single parameter.
3. Call `batch_set_device_parameters(track_index, device_index, parameter_indices, values)` to set multiple parameters at once (more efficient for effect presets).

## Browser & Loading Instruments/Effects

### Browser Paths

Use `get_browser_tree()` to explore the browser hierarchy, then `get_browser_items_at_path()` to drill down.

- Instrument URIs look like: `query:Synths#Analog:Bass:FileId_45525`
- Effect URIs look like: `query:AudioFx#Compressor`

### Loading Tips

- `load_instrument_or_effect` with a browser URI is the most reliable way to add instruments and effects to tracks.
- `load_drum_kit` is unreliable for loading specific kits — it loads a drum rack but the kit selection often fails. Better to use individual drum synth instruments (DS Kick, DS Snare, DS HH, DS Clap) on separate tracks.

## Clip & Note Programming

### Creating Clips

- Clips are created at a specific slot index. If a clip already exists at that slot, the command fails with "Clip slot already has a clip."
- Solution: use incrementing slot indices, or check which slots are free first.
- `create_clip(track_index, clip_index, length)` — length is in beats (4.0 = 1 bar at 4/4).

### MIDI Notes

Notes are added with `add_notes_to_clip`:
```python
{
    "track_index": 0,
    "clip_index": 0,
    "notes": [
        {"pitch": 60, "start_time": 0.0, "duration": 0.5, "velocity": 100},
        {"pitch": 62, "start_time": 0.5, "duration": 0.5, "velocity": 80}
    ]
}
```

- `pitch`: MIDI note number (C1=24, C2=36, C3=48, C4=60, G1=31, G2=43)
- `start_time`: position in beats from clip start
- `duration`: length in beats
- `velocity`: 0–127

### Useful MIDI Reference for Techno

| Note | MIDI | Use |
|------|------|-----|
| C1   | 24   | Sub bass root |
| G1   | 31   | Sub bass fifth |
| C2   | 36   | Bass root |
| C3   | 48   | Mid bass |
| C4   | 60   | Middle C / kick trigger |

DS instruments (DS Kick, DS Snare, etc.) respond to any MIDI note — pitch 60 works fine for triggering them.

## Arrangement Recording

The LOM does NOT support creating arrangement clips directly — they are read-only. The only way to build an arrangement is to **record session clips into the arrangement**.

### Available Commands

- `get_arrangement_info()` — read song time, record mode, loop, transport state, song length
- `set_song_time(time)` — seek to a position in beats
- `set_record_mode(on)` — enable/disable arrangement recording
- `set_arrangement_overdub(on)` — layer recordings on existing arrangement
- `set_back_to_arranger()` — return playback to arrangement from session
- `set_arrangement_loop(on, start, length)` — control arrangement loop
- `fire_scene(scene_index)` — launch all clips in a scene at once

### Scene-Based Recording Workflow (Recommended)

The best approach for building arrangements is to organize clips into scenes, then fire scenes at timed intervals while recording:

1. **Set up scenes** — each scene represents a section of the arrangement. Place clips only on the tracks that should play in that section. Empty slots act as stop buttons.

   | Scene | Section | Active Tracks |
   |-------|---------|--------------|
   | 0 | Intro | Kick |
   | 1 | Buildup | Kick, Bass, Hi-Hat |
   | 2 | Breakdown | Kick, Bass, Chords, Snare, Hi-Hat |
   | 3 | Drop | All |
   | 4 | Outro | Kick, Hi-Hat, Clap |

2. **Use `duplicate_clip`** to copy the same clip pattern into multiple scene rows. Use `delete_clip` to clean up unused clips.

3. **Record the arrangement:**
   ```
   stop_playback()
   set_back_to_arranger()
   set_song_time(0)              # seek to start
   set_record_mode(True)         # enable recording
   fire_scene(0)                 # intro — kick only
   sleep(14.8)                   # wait 8 bars (at 130 BPM: 8 * 4 * 60/130 = 14.77s)
   fire_scene(1)                 # buildup
   sleep(14.8)                   # wait 8 bars
   fire_scene(2)                 # breakdown
   sleep(14.8)                   # wait 8 bars
   fire_scene(3)                 # drop
   sleep(29.5)                   # wait 16 bars
   fire_scene(4)                 # outro
   sleep(14.8)                   # wait 8 bars
   set_record_mode(False)        # stop recording
   stop_playback()
   ```

4. **Play back the arrangement:**
   ```
   set_back_to_arranger()        # switch to arrangement playback
   set_song_time(0)              # seek to start
   start_playback()
   ```

### Why NOT to Use Muting

Do NOT use `set_track_mute` during recording to create sections. Muting silences the output but **clips are still recorded into the arrangement on all tracks**. You end up with a flat arrangement where every track has clips the whole time. Scene-based recording creates proper clip boundaries — tracks only have arrangement clips where they were actually playing.

### Session Clip Management

- `delete_clip(track_index, clip_index)` — remove a clip from a slot
- `duplicate_clip(track_index, clip_index, target_index)` — copy a clip to another slot (use `-1` to auto-find next empty slot)
- `set_track_mute(track_index, mute)` / `set_track_solo(track_index, solo)` — for auditioning during composition

### Erasing Arrangement Content

There's no API to delete arrangement clips. To erase leftover content, record an empty scene (one with no clips) over the section you want to clear:
```
set_song_time(192)              # seek to where you want to erase from
set_record_mode(True)
fire_scene(0)                   # scene 0 has no clips — records silence
sleep(20)                       # cover the leftover duration
set_record_mode(False)
stop_playback()
```

## Scene Management

- `create_scene(index)` — create a new scene row. Use `-1` to append at end.
- `delete_scene(scene_index)` — delete a scene row.
- `set_scene_name(scene_index, name)` — label scenes (e.g., "Intro", "Drop", "Outro").

## Track Management

- `create_audio_track(index)` — create an audio track. Use `-1` to append at end.
- `delete_track(track_index)` — remove a track.

## Reading the Arrangement

- `get_arrangement_clips(track_index)` — get clips for a single track.
- `get_full_arrangement()` — get all tracks with clips, scenes, tempo, time signature, and song length in one call. Only returns tracks that have arrangement clips.

## High-Level Recording: `record_arrangement`

The `record_arrangement(sections)` command handles the entire recording workflow in a single call:

```python
record_arrangement([
    {"scene_index": 0, "bars": 8},   # Intro
    {"scene_index": 1, "bars": 8},   # Buildup
    {"scene_index": 2, "bars": 8},   # Breakdown
    {"scene_index": 3, "bars": 16},  # Drop
    {"scene_index": 4, "bars": 8},   # Outro
])
```

It automatically: stops playback, seeks to beat 0, enables recording, fires each scene in sequence with correct timing, then stops recording and playback.

### Threading Architecture

`record_arrangement` runs differently from other commands:
- It executes on the **socket thread** (not main thread) to avoid deadlocks
- Timing (`time.sleep`) runs on a **background thread** so Ableton's UI stays responsive
- Ableton operations (fire scene, set record mode) are dispatched to the **main thread** via `schedule_message(0, task)` with `threading.Event` synchronization
- The MCP server uses a 600s timeout for this command (vs 10-15s for normal commands)

### Stale `self._song` Reference

The cached `self._song = self.song()` reference becomes invalid when Ableton swaps the song document (e.g., during restart or loading a new project). The C++ signature error `None.None(Song) did not match C++ signature: None(TPyHandle<ASong>)` is the symptom. Fix: refresh `self._song = self.song()` at the start of `_process_command`.

## Known Issues & Gaps

### `set_song_time` Unreliable Seeking

`set_song_time(time)` often doesn't land at the requested position on the first call. The Remote Script now retries up to 5 times with a tolerance of 0.5 beats. Still sometimes needs `set_back_to_arranger()` called first.

### No Arrangement Clip Deletion

Cannot delete or trim individual arrangement clips via the API. Only workaround is recording an empty scene (no clips) over the section to erase it.

### Recording Timing Drift (~4 beats)

Scene transitions drift ~4 beats (1 bar) over a 48-bar recording at 130 BPM. The recording uses `song.current_song_time` polling (not `time.sleep`), but scene firing isn't quantized — there's latency between detecting the target beat and the scene actually firing. Fix: set `song.clip_trigger_quantization` to snap fires to bar boundaries.

### Arrangement Clips Are Read-Only

The LOM only supports reading arrangement clips, not creating/modifying/deleting them. The only way to build an arrangement is recording from session view. The only way to erase is recording silence.

## Clip Automation

### Setting Automation Envelopes

Use `set_clip_envelope(track_index, clip_index, device_index, parameter_index, points)` to add automation to session clips. Points are `{"time": float, "value": float}` where value is normalized 0.0-1.0.

The implementation interpolates between points with 0.25-beat steps to create smooth ramps (the LOM's `insert_step` only supports flat steps, so many small steps approximate a ramp).

```python
# Sweep Auto Filter Frequency from 0.2 to 0.6 and back over a 28-beat clip
set_clip_envelope(
    track_index=5, clip_index=1,
    device_index=1, parameter_index=1,
    points=[
        {"time": 0, "value": 0.2},
        {"time": 7, "value": 0.5},
        {"time": 14, "value": 0.6},
        {"time": 21, "value": 0.35},
        {"time": 27, "value": 0.2}
    ]
)
```

### Reading Envelopes

Use `get_clip_envelope(track_index, clip_index, device_index, parameter_index)` to read automation data. Returns sampled values at 1-beat intervals across the clip length.

### Clearing Envelopes

Use `clear_clip_envelope(track_index, clip_index, device_index, parameter_index)` to remove automation.

### Automation in Arrangements

Automation can only be set on session clips, not arrangement clips. When recording the arrangement with `record_arrangement`, the session clip automation gets baked into the arrangement automatically.

## Audio Clip Loading

### What Works
- **MIDI clips**: Fully supported — create with `create_clip`, add notes with `add_notes_to_clip`
- **Instruments/effects**: Load via `load_instrument_or_effect(track_index, uri)` using browser URIs
- **.alc Live Clips on MIDI tracks**: Manual drag-and-drop works (loads both instrument and clip)

### What Doesn't Work (Yet)
- `browser.load_item()` for .alc files only loads the device chain, not the audio/MIDI clip itself
- `ClipSlot.create_clip()` in the Remote Script API only accepts a `double` (length), not file paths
- The LOM's file-path-based audio clip creation may be Max for Live specific

### Workaround
For audio clips, manually drag from Ableton's browser. For MIDI clips from .alc files, drag manually — the instrument rack and clip both load correctly.

## Common Gotchas

1. **Silent `cp` failure**: Always `rm` then `cp` when updating the Remote Script in the app bundle.
2. **Stale `__pycache__`**: Always delete it after updating the script.
3. **Script not reloading**: Toggle in Preferences doesn't work — full Ableton restart required.
4. **Clip slot occupied**: Can't overwrite clips — use a new slot index.
5. **Thread safety**: Never modify Ableton state from the socket thread — schedule it on the main thread. Exception: `record_arrangement` manages its own threading.
6. **Parameter ranges**: Always use normalized 0.0–1.0 values, not the raw parameter ranges.
7. **Muting ≠ not recording**: Muted tracks still record into arrangement. Use scene-based recording instead.
8. **`set_song_time` needs multiple calls**: Retry loop in Remote Script handles this, but sometimes still needs `set_back_to_arranger()` first.
9. **Session clips keep playing**: After arrangement recording, call `set_back_to_arranger()` to return to arrangement playback.
10. **Stale `self._song`**: Refreshed at start of every `_process_command`. Symptom: C++ signature mismatch error.
11. **`receive_full_response` timeout override**: Don't hardcode timeouts in `receive_full_response` — let `send_command` set the socket timeout based on command type.
