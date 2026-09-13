# MIDIjourney Ports — Design

## Context

[MIDIjourney](https://github.com/pollinations/MIDIjourney) is a Max for Live device
that generates one MIDI clip from a text prompt with an embedded LLM. Its GUI, LLM
backend, prompt history and temperature control are irrelevant here: the Claude
session driving the MCP server already plays those roles.

Four things it does are real gaps in ableton-mcp-pro, plus one Live 12 capability
that serves the same purpose (key awareness). This spec covers only those.

Constraints that shape the design:

- The Remote Script is installed by copying **only** `AbletonMCP_Remote_Script/__init__.py`
  into Live. Anything it needs must live in that file.
- The MCP server runs both as `python MCP_Server/server.py` and as the
  `MCP_Server.server:main` entry point, so sibling-module imports need a fallback.
- No test suite exists. New tests use stdlib `unittest` (no new dependency).
- The Remote Script imports `_Framework.ControlSurface`; tests stub it via `sys.modules`.

## A. Clip and track colors

**Remote Script**

- `set_clip_color(track_index, clip_index, color_index=None, rgb=None)` — main thread.
  Exactly one of `color_index` (0–69, Live's palette) or `rgb` (int `0xRRGGBB`).
  Returns the values read back: `{"color": int, "color_index": int}`. Live snaps
  arbitrary RGB to its nearest palette entry, so the read-back is the truth.
- `set_track_color(track_index, color_index=None, rgb=None)` — same contract,
  track resolved through `_get_track` (so `-1` master, `-2`/`-3` returns).
- `get_track_info` gains `color` / `color_index` on the track and on each clip.
  `get_arrangement_clips` and `get_full_arrangement` gain them on each clip.
  All reads go through `_safe` so a track kind that refuses the property yields `null`.

**MCP server**

- `set_clip_color(track_index, clip_index, color=None, color_index=None, key=None)`
  — exactly one of: `color` as `"#RRGGBB"`, `color_index`, or `key` (e.g. `"F minor"`,
  `"F#m"`, `"Bb"`, `"8A"`). A `key` resolves through the Camelot table to an RGB
  and the response names the Camelot code.
- `set_track_color(track_index, color=None, color_index=None)`.

**Camelot table** — `MCP_Server/camelot.py`, pure functions:

- `camelot_code(key: str) -> str` returns e.g. `"4A"`; raises `ValueError` on an
  unparseable key. Accepts `"F minor"`, `"f min"`, `"Fm"`, `"F#m"`, `"Gb major"`,
  `"Bb"` (bare note = major), `"Bbmaj"`, and Camelot codes themselves (`"8a"`).
  Enharmonics resolve (`Gb` = `F#`). Built from theory, not copied from
  MIDIjourney, whose table has duplicates (`g# minor` in both 1 and 8,
  `c# major` in both 3 and 10) and two identical colors.
- `color_for_key(key: str) -> int` — 12 hues 30° apart, one per Camelot number;
  A (minor) and B (major) of the same number share the hue, which is the point of
  the wheel: same color = relative keys, neighbouring color = compatible keys.

## B. Reading the user's selection

**Remote Script** — `get_selected_context()`, read-only (socket thread). Returns:

```json
{
  "selected_track": {"index": 3, "name": "BASS"},
  "selected_scene": {"index": 1, "name": "Drop"},
  "highlighted_clip_slot": {"track_index": 3, "clip_index": 1, "has_clip": true, "clip_name": "Bass A"},
  "detail_clip": {"name": "Bass A", "view": "session", "track_index": 3, "clip_index": 1},
  "selected_device": {"index": 0, "name": "Operator"},
  "current_song_time": 32.0,
  "is_playing": false
}
```

- Track index uses the project convention: `-1` master, `-2 - i` for return `i`.
- `detail_clip.view` is `"session"` (with `clip_index`) or `"arrangement"`
  (with `arrangement_clip_index` and `start_time`), found by identity against
  the slots / `arrangement_clips` of the owning track.
- Any section Live cannot resolve is `null` rather than an error; this call must
  never fail just because nothing is selected.

**MCP server** — `get_selected_context()` returns the JSON.

## C. Note validation

Module-level pure function `validate_notes(notes)` in `__init__.py`. Returns the
list of `(pitch, start_time, duration, velocity, mute)` tuples Live expects, or
raises `ValueError` naming the offending notes (index + reason, first 5, then a count).

| Field | Rule | Default |
|---|---|---|
| `pitch` | integer 0–127 (integral floats accepted) | **required** |
| `start_time` | number ≥ 0 | **required** |
| `duration` | number > 0 | 0.25 |
| `velocity` | number 0–127 | 100 |
| `mute` | bool | false |

`bool` is rejected where a number is expected (`True` is an `int` in Python).

Behaviour change: `pitch` and `start_time` were silently defaulted to 60 and 0.
A note missing its pitch is a bug in the caller; landing it on C3 hides the bug.

Applied before any mutation in `_add_notes_to_clip` and `_create_arrangement_midi_clip`.

## D. Compact CSV notation

`MCP_Server/notation.py`, pure functions:

- `notes_to_csv(notes) -> str` — header `pitch,start,dur,vel,mute`, one row per
  note sorted by `(start, pitch)`, numbers with trailing zeros stripped
  (`1.0` → `1`, `0.250` → `0.25`), `mute` as `0`/`1`.
- `csv_to_notes(text) -> list[dict]` — inverse. Header optional; blank lines and
  `#` comment lines ignored; `mute` column optional. Raises `ValueError` with the
  line number on a malformed row.

MCP server changes:

- `get_clip_notes(track_index, clip_index, format="json")` and
  `get_arrangement_clip_notes(..., format="json")` accept `format="csv"`, returning
  a `# clip "<name>" length=<beats> notes=<n>` comment line followed by the CSV.
  `json` stays the default so nothing existing changes.
- `add_notes_to_clip` accepts `notes` as either the existing list of dicts or a CSV
  string, converted with `csv_to_notes` before sending. Validation (C) still runs
  in the Remote Script.

## E. Song scale (Live 12)

**Remote Script**

- `get_session_info` gains `root_note` (0–11), `root_note_name` (`"C"`…`"B"`),
  `scale_name`, `scale_mode` — each read via `_safe`, `null` on Live < 12.
- `set_song_scale(root_note=None, scale_name=None, scale_mode=None)` — main thread,
  sets whichever are given, returns all three read back. Raises a clear error on
  Live < 12 (attribute absent).
- `get_clip_notes` adds clip-level scale fields **only if** the clip object exposes
  them; unverified on Live 12's LOM, so discovered at runtime, not assumed.

**MCP server** — `set_song_scale(root_note: str | int | None, scale_name, scale_mode)`;
`root_note` accepts `"F#"`, `"Gb"`, or 0–11.

## Error handling

Server tools keep the existing pattern: catch, log, return `"Error …: <message>"`.
Argument conflicts (zero or several of `color` / `color_index` / `key`) are rejected
in the server before any TCP round trip.

## Testing

`tests/` with stdlib `unittest`, run by `python3 -m unittest discover tests`:

- `test_camelot.py` — all 24 keys map to 24 distinct codes; relative keys share a
  hue; enharmonics agree; the input spellings above parse; garbage raises.
- `test_notation.py` — CSV round-trip preserves notes; number formatting; header /
  comment / blank-line tolerance; malformed row reports its line.
- `test_remote_script.py` — imports `__init__.py` with `_Framework` stubbed and
  exercises `validate_notes`, `_get_selected_context`, `_set_clip_color`,
  `_set_track_color` and the scale handlers against small fake Live objects.

Then a live check over TCP 9877 once the script is installed in Live, which also
settles whether clip-level scale fields exist.

## Out of scope

GUI, embedded LLM, prompt history, temperature, auto-retry, music-theory system
prompt, clip auto-resize — see the triage in the originating conversation.
