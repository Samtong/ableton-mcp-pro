# MIDIjourney Ports Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add clip/track colors (with Camelot key coloring), selection reading, note validation, compact CSV notation and Live 12 song scale to ableton-mcp-pro.

**Architecture:** Pure logic lives in two small server modules (`MCP_Server/camelot.py`, `MCP_Server/notation.py`) and one module-level function in the Remote Script (`validate_notes`). LOM-touching handlers follow the existing Remote Script pattern (read-only on the socket thread, mutations on the main thread) and each gets a thin `@mcp.tool()` wrapper.

**Tech Stack:** Python 3 (Live 12's embedded interpreter for the Remote Script, ≥3.10 for the server), FastMCP, stdlib `unittest`.

## Global Constraints

- The Remote Script is installed by copying only `AbletonMCP_Remote_Script/__init__.py`; it must stay a single file.
- Server modules import with a fallback: `from MCP_Server import x` then `import x` (script launch).
- Tests use stdlib `unittest` only. Run with the main checkout's venv, from the worktree root:
  `/Users/sami-inc/Code/ableton-mcp-pro/.venv/bin/python -m unittest discover -s tests -v`
  (`MCP_Server/__init__.py` imports `server.py`, which needs `mcp`; system `python3` lacks it.)
- Track indexing: `-1` master, `-2 - i` for return track `i`.
- Palette `color_index` range 0–69; `rgb` range `0x000000`–`0xFFFFFF`.
- `pitch` and `start_time` become required on notes; `duration` defaults 0.25, `velocity` 100, `mute` false.
- Every new state-modifying command name goes in **three** places: the Remote Script's main-thread command list, its `main_thread_task` routing, and the server's `is_modifying_command` list.

---

## File Structure

| File | Responsibility |
|---|---|
| `MCP_Server/notation.py` (new) | Notes ↔ CSV, clip rendering as `json`/`csv` |
| `MCP_Server/camelot.py` (new) | Note/key parsing, Camelot codes, key colors, color-argument resolution |
| `MCP_Server/server.py` | New tools + `format` / CSV input on existing note tools |
| `AbletonMCP_Remote_Script/__init__.py` | `validate_notes`, color / selection / scale handlers, color & scale fields on reads |
| `tests/remote_script_harness.py` (new) | Loads `__init__.py` with `_Framework` stubbed; builds a handler-only instance |
| `tests/test_notation.py`, `tests/test_camelot.py`, `tests/test_remote_script.py` (new) | Unit tests |

---

### Task 1: CSV notation

**Files:**
- Create: `MCP_Server/notation.py`
- Create: `tests/test_notation.py`
- Modify: `MCP_Server/server.py` (imports; `get_clip_notes`, `get_arrangement_clip_notes`, `add_notes_to_clip`)

**Interfaces:**
- Produces: `notes_to_csv(notes: list[dict]) -> str`, `csv_to_notes(text: str) -> list[dict]`, `clip_to_csv(clip: dict) -> str`, `render_clip(clip: dict, fmt: str) -> str`. Note dicts use keys `pitch, start_time, duration, velocity, mute`.

- [ ] **Step 1: Write the failing tests** — `tests/test_notation.py`

```python
import unittest

from MCP_Server.notation import clip_to_csv, csv_to_notes, notes_to_csv, render_clip

NOTES = [
    {"pitch": 64, "start_time": 1.0, "duration": 0.5, "velocity": 90.0, "mute": False},
    {"pitch": 60, "start_time": 0.0, "duration": 0.25, "velocity": 100.0, "mute": True},
    {"pitch": 67, "start_time": 1.0, "duration": 1.125, "velocity": 72.5, "mute": False},
]


class NotesToCsvTest(unittest.TestCase):
    def test_header_sorted_rows_and_trimmed_numbers(self):
        self.assertEqual(
            notes_to_csv(NOTES),
            "pitch,start,dur,vel,mute\n"
            "60,0,0.25,100,1\n"
            "64,1,0.5,90,0\n"
            "67,1,1.125,72.5,0",
        )

    def test_empty(self):
        self.assertEqual(notes_to_csv([]), "pitch,start,dur,vel,mute")


class CsvToNotesTest(unittest.TestCase):
    def test_round_trip(self):
        back = csv_to_notes(notes_to_csv(NOTES))
        key = lambda n: (n["start_time"], n["pitch"])
        self.assertEqual(sorted(back, key=key), sorted(NOTES, key=key))

    def test_headerless_comments_blanks_and_optional_mute(self):
        text = "# a comment\n\n60, 0, 0.5, 100\n62,0.5,0.5,80,1\n"
        self.assertEqual(csv_to_notes(text), [
            {"pitch": 60, "start_time": 0.0, "duration": 0.5, "velocity": 100.0, "mute": False},
            {"pitch": 62, "start_time": 0.5, "duration": 0.5, "velocity": 80.0, "mute": True},
        ])

    def test_wrong_column_count_names_the_line(self):
        with self.assertRaisesRegex(ValueError, "Line 2"):
            csv_to_notes("pitch,start,dur,vel\n60,0,0.5\n")

    def test_non_numeric_names_the_line(self):
        with self.assertRaisesRegex(ValueError, "Line 1"):
            csv_to_notes("C3,0,0.5,100")


class ClipRenderTest(unittest.TestCase):
    CLIP = {"clip_name": "Bass A", "length": 8.0, "note_count": 3, "notes": NOTES}

    def test_clip_to_csv_has_comment_line(self):
        first, rest = clip_to_csv(self.CLIP).split("\n", 1)
        self.assertEqual(first, '# clip "Bass A" length=8 notes=3')
        self.assertTrue(rest.startswith("pitch,start,dur,vel,mute\n60,0"))

    def test_comment_includes_start_and_scale_when_present(self):
        clip = dict(self.CLIP, start_time=32.0, root_note_name="F", scale_name="Minor")
        first = clip_to_csv(clip).split("\n", 1)[0]
        self.assertEqual(first, '# clip "Bass A" length=8 start=32 scale="F Minor" notes=3')

    def test_render_clip_formats(self):
        self.assertIn('"clip_name": "Bass A"', render_clip(self.CLIP, "json"))
        self.assertTrue(render_clip(self.CLIP, "csv").startswith("# clip"))
        with self.assertRaisesRegex(ValueError, "format"):
            render_clip(self.CLIP, "xml")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run to verify it fails**

Run: `/Users/sami-inc/Code/ableton-mcp-pro/.venv/bin/python -m unittest discover -s tests -v`
Expected: ERROR — `ModuleNotFoundError: No module named 'MCP_Server.notation'`

- [ ] **Step 3: Implement** — `MCP_Server/notation.py`

```python
"""Compact CSV form of MIDI notes.

A dense clip as JSON costs several times the tokens of the same notes as CSV,
in both directions: reading a clip and writing one.
"""
import json

HEADER = "pitch,start,dur,vel,mute"


def _num(value):
    """Shortest faithful text for a beat/velocity value: 1.0 -> '1', 0.250 -> '0.25'."""
    text = "{:.4f}".format(float(value)).rstrip("0").rstrip(".")
    return "0" if text in ("", "-0") else text


def notes_to_csv(notes):
    rows = [HEADER]
    for note in sorted(notes, key=lambda n: (n["start_time"], n["pitch"])):
        rows.append(",".join([
            str(int(note["pitch"])),
            _num(note["start_time"]),
            _num(note["duration"]),
            _num(note["velocity"]),
            "1" if note.get("mute") else "0",
        ]))
    return "\n".join(rows)


def csv_to_notes(text):
    """Parse `pitch,start,dur,vel[,mute]` rows. Header, blank and `#` lines are skipped."""
    notes = []
    for line_no, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        cells = [cell.strip() for cell in line.split(",")]
        if cells[0].lower() == "pitch":
            continue
        if len(cells) not in (4, 5):
            raise ValueError("Line {}: expected pitch,start,dur,vel[,mute], got {!r}".format(line_no, raw))
        try:
            notes.append({
                "pitch": int(cells[0]),
                "start_time": float(cells[1]),
                "duration": float(cells[2]),
                "velocity": float(cells[3]),
                "mute": len(cells) == 5 and cells[4].lower() in ("1", "true"),
            })
        except ValueError:
            raise ValueError("Line {}: non-numeric value in {!r}".format(line_no, raw))
    return notes


def clip_to_csv(clip):
    """A `# clip ...` comment line with the clip's metadata, then its notes as CSV."""
    notes = clip.get("notes", [])
    meta = ['clip "{}"'.format(clip.get("clip_name", "")), "length={}".format(_num(clip.get("length", 0)))]
    if "start_time" in clip:
        meta.append("start={}".format(_num(clip["start_time"])))
    if clip.get("scale_name"):
        scale = "{} {}".format(clip.get("root_note_name") or "", clip["scale_name"]).strip()
        meta.append('scale="{}"'.format(scale))
    meta.append("notes={}".format(len(notes)))
    return "# " + " ".join(meta) + "\n" + notes_to_csv(notes)


def render_clip(clip, fmt):
    if fmt == "json":
        return json.dumps(clip, indent=2)
    if fmt == "csv":
        return clip_to_csv(clip)
    raise ValueError("format must be 'json' or 'csv', got {!r}".format(fmt))
```

- [ ] **Step 4: Run to verify it passes**

Run: `/Users/sami-inc/Code/ableton-mcp-pro/.venv/bin/python -m unittest discover -s tests -v`
Expected: 9 tests, OK

- [ ] **Step 5: Wire into the server** — `MCP_Server/server.py`

After the `from typing import ...` line:

```python
try:
    from MCP_Server import notation
except ImportError:  # launched as `python MCP_Server/server.py`
    import notation
```

Replace `get_arrangement_clip_notes`:

```python
@mcp.tool()
def get_arrangement_clip_notes(ctx: Context, track_index: int, arrangement_clip_index: int,
                               format: str = "json") -> str:
    """
    Read MIDI notes from a clip in the arrangement view (not session view).

    Parameters:
    - track_index: Index of the track
    - arrangement_clip_index: Index into track.arrangement_clips (0 = first arrangement clip on the track).
                              Get the index from `get_arrangement_clips`.
    - format: "json" (default) or "csv" — CSV is a `# clip ...` comment line then
              `pitch,start,dur,vel,mute` rows, a fraction of the tokens for dense clips
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("get_arrangement_clip_notes", {
            "track_index": track_index,
            "arrangement_clip_index": arrangement_clip_index,
        })
        return notation.render_clip(result, format)
    except Exception as e:
        logger.error(f"Error getting arrangement clip notes: {str(e)}")
        return f"Error getting arrangement clip notes: {str(e)}"
```

Replace `get_clip_notes`:

```python
@mcp.tool()
def get_clip_notes(ctx: Context, track_index: int, clip_index: int, format: str = "json") -> str:
    """
    Get all MIDI notes from a clip.

    Parameters:
    - track_index: The index of the track
    - clip_index: The index of the clip slot
    - format: "json" (default) or "csv" — CSV is a `# clip ...` comment line then
              `pitch,start,dur,vel,mute` rows, a fraction of the tokens for dense clips
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("get_clip_notes", {
            "track_index": track_index,
            "clip_index": clip_index
        })
        return notation.render_clip(result, format)
    except Exception as e:
        logger.error(f"Error getting clip notes: {str(e)}")
        return f"Error getting clip notes: {str(e)}"
```

Replace `add_notes_to_clip`:

```python
@mcp.tool()
def add_notes_to_clip(
    ctx: Context,
    track_index: int,
    clip_index: int,
    notes: Union[List[Dict[str, Union[int, float, bool]]], str]
) -> str:
    """
    Add MIDI notes to a clip.

    Parameters:
    - track_index: The index of the track containing the clip
    - clip_index: The index of the clip slot containing the clip
    - notes: Either a list of note dicts (pitch, start_time required; duration,
             velocity, mute optional), or the same notes as CSV text:
             `pitch,start,dur,vel[,mute]` one note per line, header optional.
             Invalid notes are rejected before anything is written.
    """
    try:
        if isinstance(notes, str):
            notes = notation.csv_to_notes(notes)
        ableton = get_ableton_connection()
        result = ableton.send_command("add_notes_to_clip", {
            "track_index": track_index,
            "clip_index": clip_index,
            "notes": notes
        })
        return f"Added {len(notes)} notes to clip at track {track_index}, slot {clip_index}"
    except Exception as e:
        logger.error(f"Error adding notes to clip: {str(e)}")
        return f"Error adding notes to clip: {str(e)}"
```

- [ ] **Step 6: Smoke-check the server still imports**

Run: `/Users/sami-inc/Code/ableton-mcp-pro/.venv/bin/python -c "import MCP_Server.server as s; print('ok')"`
Expected: `ok`

- [ ] **Step 7: Commit**

```bash
git add MCP_Server/notation.py MCP_Server/server.py tests/test_notation.py
git commit -m "feat: compact CSV notation for reading and writing clip notes"
```

---

### Task 2: Note validation in the Remote Script

**Files:**
- Create: `tests/remote_script_harness.py`
- Create: `tests/test_remote_script.py`
- Modify: `AbletonMCP_Remote_Script/__init__.py` (imports; new module-level `validate_notes`; `_add_notes_to_clip`; `_create_arrangement_midi_clip`)

**Interfaces:**
- Produces: module-level `validate_notes(notes: list) -> list[tuple]` raising `ValueError`; test helpers `Obj(**fields)`, `load_remote_script()` and `make_script(song)`.

- [ ] **Step 1: Write the harness** — `tests/remote_script_harness.py`

```python
"""Load the Remote Script outside Live, with `_Framework` stubbed out."""
import importlib.util
import pathlib
import sys
import types

ROOT = pathlib.Path(__file__).resolve().parents[1]
_module = None


class Obj(object):
    """Fake Live object. Equality is identity, like LOM wrappers compared with ==;
    SimpleNamespace compares contents, which would let two fake tracks match."""

    def __init__(self, **fields):
        self.__dict__.update(fields)


def load_remote_script():
    global _module
    if _module is None:
        control_surface = types.ModuleType("_Framework.ControlSurface")

        class ControlSurface(object):
            def __init__(self, c_instance):
                pass

            def log_message(self, *args):
                pass

        control_surface.ControlSurface = ControlSurface
        sys.modules.setdefault("_Framework", types.ModuleType("_Framework"))
        sys.modules.setdefault("_Framework.ControlSurface", control_surface)
        spec = importlib.util.spec_from_file_location(
            "abletonmcp_remote_script", ROOT / "AbletonMCP_Remote_Script" / "__init__.py")
        _module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_module)
    return _module


def make_script(song):
    """An AbletonMCP instance with only `_song` set: no socket server, no Live."""
    module = load_remote_script()
    script = object.__new__(module.AbletonMCP)
    script._song = song
    return script
```

- [ ] **Step 2: Write the failing tests** — `tests/test_remote_script.py`

```python
import unittest

from remote_script_harness import Obj, load_remote_script, make_script

rs = load_remote_script()


class ValidateNotesTest(unittest.TestCase):
    def test_converts_to_live_tuples_with_defaults(self):
        self.assertEqual(
            rs.validate_notes([{"pitch": 60, "start_time": 0}, {"pitch": 62.0, "start_time": 1.5, "duration": 1,
                                                                 "velocity": 80, "mute": True}]),
            [(60, 0.0, 0.25, 100, False), (62, 1.5, 1.0, 80, True)],
        )

    def test_missing_pitch_and_start_are_errors(self):
        with self.assertRaises(ValueError) as caught:
            rs.validate_notes([{"duration": 1}])
        self.assertIn("note 0: pitch", str(caught.exception))
        self.assertIn("start_time", str(caught.exception))

    def test_ranges(self):
        bad = [
            {"pitch": 128, "start_time": 0},
            {"pitch": 60.5, "start_time": 0},
            {"pitch": 60, "start_time": -1},
            {"pitch": 60, "start_time": 0, "duration": 0},
            {"pitch": 60, "start_time": 0, "velocity": 128},
        ]
        with self.assertRaises(ValueError) as caught:
            rs.validate_notes(bad)
        message = str(caught.exception)
        for i in range(5):
            self.assertIn("note {0}:".format(i), message)

    def test_bools_and_strings_are_not_numbers(self):
        with self.assertRaisesRegex(ValueError, "pitch"):
            rs.validate_notes([{"pitch": True, "start_time": 0}])
        with self.assertRaisesRegex(ValueError, "velocity"):
            rs.validate_notes([{"pitch": 60, "start_time": 0, "velocity": "loud"}])
        with self.assertRaisesRegex(ValueError, "mute"):
            rs.validate_notes([{"pitch": 60, "start_time": 0, "mute": 1}])

    def test_reports_first_five_then_a_count(self):
        with self.assertRaises(ValueError) as caught:
            rs.validate_notes([{"pitch": -1, "start_time": 0}] * 8)
        message = str(caught.exception)
        self.assertIn("note 4:", message)
        self.assertNotIn("note 5:", message)
        self.assertIn("and 3 more", message)


class FakeClip(object):
    def __init__(self):
        self.name = "clip"
        self.written = None

    def set_notes(self, notes):
        self.written = notes


def song_with_clip(clip):
    slot = Obj(has_clip=True, clip=clip)
    track = Obj(clip_slots=[slot])
    return Obj(tracks=[track])


class AddNotesTest(unittest.TestCase):
    def test_invalid_notes_never_reach_the_clip(self):
        clip = FakeClip()
        script = make_script(song_with_clip(clip))
        with self.assertRaises(ValueError):
            script._add_notes_to_clip(0, 0, [{"pitch": 60, "start_time": 0}, {"pitch": 200, "start_time": 0}])
        self.assertIsNone(clip.written)

    def test_valid_notes_are_written(self):
        clip = FakeClip()
        script = make_script(song_with_clip(clip))
        self.assertEqual(script._add_notes_to_clip(0, 0, [{"pitch": 60, "start_time": 0}]), {"note_count": 1})
        self.assertEqual(clip.written, ((60, 0.0, 0.25, 100, False),))


class CreateArrangementMidiClipTest(unittest.TestCase):
    def test_invalid_notes_create_no_clip(self):
        created = []
        track = Obj(has_midi_input=True, arrangement_clips=[],
                                      create_midi_clip=lambda start, length: created.append(start))
        script = make_script(Obj(tracks=[track]))
        with self.assertRaises(ValueError):
            script._create_arrangement_midi_clip(0, 0.0, 4.0, [{"pitch": 60}])
        self.assertEqual(created, [])


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 3: Run to verify it fails**

Run: `/Users/sami-inc/Code/ableton-mcp-pro/.venv/bin/python -m unittest discover -s tests -v`
Expected: `AttributeError: module 'abletonmcp_remote_script' has no attribute 'validate_notes'` (and the clip tests fail: invalid pitch 200 is written)

- [ ] **Step 4: Implement** — `AbletonMCP_Remote_Script/__init__.py`

Add `import math` after `import json`. After `HOST = "localhost"`, add:

```python
def _is_number(value):
    """A finite int/float. bool is excluded: True would otherwise pass as pitch 1."""
    return (isinstance(value, (int, float)) and not isinstance(value, bool)
            and math.isfinite(value))


def validate_notes(notes):
    """Check note dicts and convert them to the tuples Clip.set_notes expects.

    Raises ValueError naming the offending notes, so nothing half-written ever
    reaches a clip. pitch and start_time are required: silently landing a
    note with no pitch on C3 hides the caller's bug.
    """
    live_notes = []
    problems = []
    for i, note in enumerate(notes):
        if not isinstance(note, dict):
            problems.append("note {0}: expected an object, got {1!r}".format(i, note))
            continue
        pitch = note.get("pitch")
        start_time = note.get("start_time")
        duration = note.get("duration", 0.25)
        velocity = note.get("velocity", 100)
        mute = note.get("mute", False)
        reasons = []
        if not _is_number(pitch) or pitch != int(pitch) or not 0 <= pitch <= 127:
            reasons.append("pitch must be an integer 0-127, got {0!r}".format(pitch))
        if not _is_number(start_time) or start_time < 0:
            reasons.append("start_time must be a number >= 0, got {0!r}".format(start_time))
        if not _is_number(duration) or duration <= 0:
            reasons.append("duration must be a number > 0, got {0!r}".format(duration))
        if not _is_number(velocity) or not 0 <= velocity <= 127:
            reasons.append("velocity must be a number 0-127, got {0!r}".format(velocity))
        if not isinstance(mute, bool):
            reasons.append("mute must be true or false, got {0!r}".format(mute))
        if reasons:
            problems.append("note {0}: {1}".format(i, ", ".join(reasons)))
        else:
            live_notes.append((int(pitch), float(start_time), float(duration), velocity, mute))
    if problems:
        shown = problems[:5]
        if len(problems) > 5:
            shown.append("and {0} more".format(len(problems) - 5))
        raise ValueError("Invalid notes: " + "; ".join(shown))
    return live_notes
```

In `_add_notes_to_clip`, delete the `# Convert note data to Live's format` block (the `live_notes = []` loop) and make the first line inside `try:` be:

```python
            live_notes = validate_notes(notes)
```

In `_create_arrangement_midi_clip`, add as the first line inside `try:`:

```python
            live_notes = validate_notes(notes) if notes else []
```

and replace the block from `note_count = 0` through `note_count = len(live_notes)` with:

```python
            note_count = 0
            if live_notes and clip is not None:
                clip.set_notes(tuple(live_notes))
                note_count = len(live_notes)
```

- [ ] **Step 5: Run to verify it passes**

Run: `/Users/sami-inc/Code/ableton-mcp-pro/.venv/bin/python -m unittest discover -s tests -v`
Expected: all tests OK

- [ ] **Step 6: Commit**

```bash
git add AbletonMCP_Remote_Script/__init__.py tests/remote_script_harness.py tests/test_remote_script.py
git commit -m "feat: validate MIDI notes before writing them to a clip"
```

---

### Task 3: Camelot keys and colors

**Files:**
- Create: `MCP_Server/camelot.py`
- Create: `tests/test_camelot.py`

**Interfaces:**
- Produces: `NOTE_NAMES: list[str]`, `pitch_class(note: str) -> int`, `parse_root_note(value: str | int) -> int`, `camelot_code(key: str) -> str`, `color_for_key(key: str) -> int`, `parse_hex_color(text: str) -> int`, `resolve_color(color=None, color_index=None, key=None) -> tuple[dict, str | None]` where the dict is `{"rgb": int}` or `{"color_index": int}`.

- [ ] **Step 1: Write the failing tests** — `tests/test_camelot.py`

```python
import unittest

from MCP_Server.camelot import (NOTE_NAMES, camelot_code, color_for_key, parse_hex_color,
                                parse_root_note, pitch_class, resolve_color)

# The wheel, straight from its definition.
WHEEL = {
    "1A": "G# minor", "2A": "D# minor", "3A": "A# minor", "4A": "F minor", "5A": "C minor", "6A": "G minor",
    "7A": "D minor", "8A": "A minor", "9A": "E minor", "10A": "B minor", "11A": "F# minor", "12A": "C# minor",
    "1B": "B major", "2B": "F# major", "3B": "C# major", "4B": "G# major", "5B": "D# major", "6B": "A# major",
    "7B": "F major", "8B": "C major", "9B": "G major", "10B": "D major", "11B": "A major", "12B": "E major",
}


class PitchClassTest(unittest.TestCase):
    def test_names_and_enharmonics(self):
        self.assertEqual([pitch_class(n) for n in NOTE_NAMES], list(range(12)))
        self.assertEqual(pitch_class("Gb"), pitch_class("F#"))
        self.assertEqual(pitch_class("bb"), 10)
        self.assertEqual(pitch_class("Cb"), 11)
        self.assertEqual(pitch_class("E#"), 5)

    def test_parse_root_note(self):
        self.assertEqual(parse_root_note("F#"), 6)
        self.assertEqual(parse_root_note(11), 11)
        for bad in (12, -1, True, "H"):
            with self.assertRaises(ValueError):
                parse_root_note(bad)


class CamelotCodeTest(unittest.TestCase):
    def test_whole_wheel(self):
        for code, key in WHEEL.items():
            self.assertEqual(camelot_code(key), code, key)

    def test_spellings(self):
        for key in ("F minor", "f min", "Fm", "F MINOR", " f  minor "):
            self.assertEqual(camelot_code(key), "4A", key)
        self.assertEqual(camelot_code("Gb major"), "2B")
        self.assertEqual(camelot_code("Bb"), "6B")
        self.assertEqual(camelot_code("Bbmaj"), "6B")
        self.assertEqual(camelot_code("bbm"), "3A")
        self.assertEqual(camelot_code("Ebm"), "2A")
        self.assertEqual(camelot_code("8a"), "8A")
        self.assertEqual(camelot_code("12B"), "12B")

    def test_garbage(self):
        for bad in ("", "H minor", "13A", "F lydian", None):
            with self.assertRaises(ValueError):
                camelot_code(bad)


class ColorForKeyTest(unittest.TestCase):
    def test_relative_keys_share_a_color_and_numbers_differ(self):
        self.assertEqual(color_for_key("A minor"), color_for_key("C major"))
        colors = {color_for_key("{0}A".format(n)) for n in range(1, 13)}
        self.assertEqual(len(colors), 12)
        for color in colors:
            self.assertTrue(0 <= color <= 0xFFFFFF)


class ResolveColorTest(unittest.TestCase):
    def test_each_form(self):
        self.assertEqual(resolve_color(color="#ff8800"), ({"rgb": 0xFF8800}, None))
        self.assertEqual(resolve_color(color_index=12), ({"color_index": 12}, None))
        self.assertEqual(resolve_color(key="F minor"), ({"rgb": color_for_key("4A")}, "4A"))

    def test_exactly_one(self):
        with self.assertRaisesRegex(ValueError, "none"):
            resolve_color()
        with self.assertRaisesRegex(ValueError, "color, key"):
            resolve_color(color="#000000", key="Am")

    def test_bad_values(self):
        for kwargs in ({"color": "orange"}, {"color_index": 70}, {"color_index": True}):
            with self.assertRaises(ValueError):
                resolve_color(**kwargs)
        self.assertEqual(parse_hex_color("00ff00"), 0x00FF00)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run to verify it fails**

Run: `/Users/sami-inc/Code/ableton-mcp-pro/.venv/bin/python -m unittest discover -s tests -v`
Expected: ERROR — `No module named 'MCP_Server.camelot'`

- [ ] **Step 3: Implement** — `MCP_Server/camelot.py`

```python
"""Key names, Camelot codes, and the colors that go with them.

The Camelot wheel numbers the 24 keys so that harmonic neighbours are adjacent:
the same number is a relative major/minor pair, and one step either way is a
fifth. Coloring clips by number makes compatible material look alike in Live.
"""
import colorsys
import re

NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

_LETTERS = {"c": 0, "d": 2, "e": 4, "f": 5, "g": 7, "a": 9, "b": 11}
_CAMELOT_RE = re.compile(r"^(1[0-2]|[1-9])([ab])$")
_NOTE_RE = re.compile(r"^([a-g])([#b♯♭]*)$")
_KEY_RE = re.compile(r"^([a-g])([#b♯♭]*)(m|min|minor|maj|major)?$")
# Tonic pitch class at position 1 of each side: 1A = G# minor, 1B = B major.
# Each step round the wheel adds a fifth (7 semitones).
_WHEEL_START = {"A": 8, "B": 11}


def _compact(text):
    if not isinstance(text, str):
        raise ValueError("Expected text, got {!r}".format(text))
    return re.sub(r"\s+", "", text.lower())


def _pitch_class(letter, accidentals):
    shift = sum(1 if a in "#♯" else -1 for a in accidentals)
    return (_LETTERS[letter] + shift) % 12


def pitch_class(note):
    """'F#', 'Gb', 'bb' -> 0-11."""
    match = _NOTE_RE.match(_compact(note))
    if not match:
        raise ValueError("Unrecognised note name: {!r}".format(note))
    return _pitch_class(match.group(1), match.group(2))


def parse_root_note(value):
    """A note name or a 0-11 integer -> 0-11."""
    if isinstance(value, int) and not isinstance(value, bool):
        if 0 <= value <= 11:
            return value
        raise ValueError("root_note must be 0-11, got {}".format(value))
    return pitch_class(value)


def camelot_code(key):
    """'F minor', 'F#m', 'Bb' (major), 'Bbmaj' or a code like '8a' -> e.g. '4A'."""
    text = _compact(key)
    match = _CAMELOT_RE.match(text)
    if match:
        return match.group(1) + match.group(2).upper()
    match = _KEY_RE.match(text)
    if not match:
        raise ValueError("Unrecognised key: {!r} (try 'F minor', 'F#m', 'Bb' or '8A')".format(key))
    side = "A" if match.group(3) in ("m", "min", "minor") else "B"
    tonic = _pitch_class(match.group(1), match.group(2))
    # 7 is its own inverse mod 12, so undoing "add a fifth per step" is another *7.
    number = ((tonic - _WHEEL_START[side]) * 7) % 12 + 1
    return "{}{}".format(number, side)


def color_for_key(key):
    """0xRRGGBB for a key: one of 12 hues, shared by both sides of a Camelot number."""
    number = int(camelot_code(key)[:-1])
    r, g, b = colorsys.hsv_to_rgb((number - 1) / 12.0, 0.75, 0.95)
    return (round(r * 255) << 16) | (round(g * 255) << 8) | round(b * 255)


def parse_hex_color(text):
    match = re.match(r"^#?([0-9a-fA-F]{6})$", text.strip()) if isinstance(text, str) else None
    if not match:
        raise ValueError("color must be '#RRGGBB', got {!r}".format(text))
    return int(match.group(1), 16)


def resolve_color(color=None, color_index=None, key=None):
    """Turn exactly one of color / color_index / key into Remote Script params.

    Returns (params, camelot) — params is {"rgb": int} or {"color_index": int};
    camelot is the key's code when a key was given, else None.
    """
    given = [name for name, value in (("color", color), ("color_index", color_index), ("key", key))
             if value is not None]
    if len(given) != 1:
        raise ValueError("Pass exactly one of color, color_index, key (got {})".format(", ".join(given) or "none"))
    if color is not None:
        return {"rgb": parse_hex_color(color)}, None
    if color_index is not None:
        if isinstance(color_index, bool) or not isinstance(color_index, int) or not 0 <= color_index <= 69:
            raise ValueError("color_index must be an integer 0-69, got {!r}".format(color_index))
        return {"color_index": color_index}, None
    return {"rgb": color_for_key(key)}, camelot_code(key)
```

- [ ] **Step 4: Run to verify it passes**

Run: `/Users/sami-inc/Code/ableton-mcp-pro/.venv/bin/python -m unittest discover -s tests -v`
Expected: all tests OK

- [ ] **Step 5: Commit**

```bash
git add MCP_Server/camelot.py tests/test_camelot.py
git commit -m "feat: Camelot key parsing and key-to-color mapping"
```

---

### Task 4: Clip and track colors

**Files:**
- Modify: `AbletonMCP_Remote_Script/__init__.py` (command list + routing; `_get_track_info`; `_get_arrangement_clips`; `_get_full_arrangement`; new `_color_fields`, `_apply_color`, `_set_clip_color`, `_set_track_color`)
- Modify: `MCP_Server/server.py` (import `camelot`; `is_modifying_command`; new tools `set_clip_color`, `set_track_color`)
- Test: `tests/test_remote_script.py`

**Interfaces:**
- Consumes: `camelot.resolve_color` (Task 3).
- Produces: Remote commands `set_clip_color {track_index, clip_index, color_index | rgb}` and `set_track_color {track_index, color_index | rgb}`, each returning `{..., "color": int, "color_index": int}`.

- [ ] **Step 1: Write the failing tests** — append to `tests/test_remote_script.py`, before the `if __name__` block

```python
class ColorTest(unittest.TestCase):
    def setUp(self):
        self.clip = Obj(name="Bass", length=4.0, is_playing=False, is_recording=False,
                                          color=0, color_index=0)
        slot = Obj(has_clip=True, clip=self.clip)
        mixer = Obj(volume=Obj(value=0.85), sends=[],
                                      panning=Obj(value=0.5))
        self.track = Obj(name="BASS", clip_slots=[slot], devices=[], mixer_device=mixer,
                                           color=0, color_index=0, arrangement_clips=[self.clip])
        self.master = Obj(name="Main", color=0, color_index=0)
        self.script = make_script(Obj(tracks=[self.track], return_tracks=[],
                                                        master_track=self.master, scenes=[],
                                                        tempo=120.0, signature_numerator=4,
                                                        signature_denominator=4, song_length=16.0))

    def test_set_clip_color_by_index_reads_back(self):
        result = self.script._set_clip_color(0, 0, color_index=12)
        self.assertEqual(self.clip.color_index, 12)
        self.assertEqual(result["color_index"], 12)
        self.assertEqual(result["clip_name"], "Bass")

    def test_set_clip_color_by_rgb(self):
        self.script._set_clip_color(0, 0, rgb=0xFF8800)
        self.assertEqual(self.clip.color, 0xFF8800)

    def test_exactly_one_and_ranges(self):
        for kwargs in ({}, {"color_index": 1, "rgb": 1}, {"color_index": 70}, {"rgb": 0x1000000},
                       {"color_index": True}):
            with self.assertRaises(ValueError):
                self.script._set_clip_color(0, 0, **kwargs)

    def test_set_track_color_supports_master(self):
        self.assertEqual(self.script._set_track_color(-1, color_index=3)["color_index"], 3)
        self.assertEqual(self.master.color_index, 3)

    def test_reads_include_colors(self):
        self.clip.color, self.clip.color_index = 0x00FF00, 5
        self.track.color, self.track.color_index = 0xFF0000, 9
        info = self.script._get_track_info(0)
        self.assertEqual((info["color"], info["color_index"]), (0xFF0000, 9))
        self.assertEqual(info["clip_slots"][0]["clip"]["color_index"], 5)
        clip_row = dict(start_time=0.0, end_time=4.0, is_midi_clip=True, is_audio_clip=False)
        vars(self.clip).update(clip_row)
        self.assertEqual(self.script._get_arrangement_clips(0)["clips"][0]["color_index"], 5)
        full = self.script._get_full_arrangement()
        self.assertEqual(full["tracks_with_clips"][0]["clips"][0]["color"], 0x00FF00)
```

- [ ] **Step 2: Run to verify it fails**

Run: `/Users/sami-inc/Code/ableton-mcp-pro/.venv/bin/python -m unittest discover -s tests -v`
Expected: `AttributeError: 'AbletonMCP' object has no attribute '_set_clip_color'`, and `KeyError: 'color'` in `test_reads_include_colors`

- [ ] **Step 3: Implement the Remote Script handlers** — `AbletonMCP_Remote_Script/__init__.py`

In the main-thread command list, change `"add_notes_to_clip", "set_clip_name",` to:

```python
                                 "add_notes_to_clip", "set_clip_name", "set_clip_color", "set_track_color",
```

In `main_thread_task`, right after the `set_clip_name` branch:

```python
                        elif command_type == "set_clip_color":
                            result = self._set_clip_color(params.get("track_index", 0), params.get("clip_index", 0),
                                                          params.get("color_index"), params.get("rgb"))
                        elif command_type == "set_track_color":
                            result = self._set_track_color(params.get("track_index", 0),
                                                           params.get("color_index"), params.get("rgb"))
```

After the `_param_str` static method, add:

```python
    @classmethod
    def _color_fields(cls, obj):
        """color (0xRRGGBB) and color_index (0-69) as Live reports them, None if refused."""
        return {"color": cls._safe(obj, "color"), "color_index": cls._safe(obj, "color_index")}

    def _apply_color(self, obj, color_index, rgb):
        """Set exactly one of color_index / rgb, then read both back: Live snaps
        arbitrary RGB to its nearest palette entry, so the read-back is the truth."""
        if (color_index is None) == (rgb is None):
            raise ValueError("Pass exactly one of color_index or rgb")
        if color_index is not None:
            if isinstance(color_index, bool) or not isinstance(color_index, int) or not 0 <= color_index <= 69:
                raise ValueError("color_index must be an integer 0-69, got {0!r}".format(color_index))
            obj.color_index = color_index
        else:
            if isinstance(rgb, bool) or not isinstance(rgb, int) or not 0 <= rgb <= 0xFFFFFF:
                raise ValueError("rgb must be an integer 0x000000-0xFFFFFF, got {0!r}".format(rgb))
            obj.color = rgb
        return self._color_fields(obj)

    def _set_clip_color(self, track_index, clip_index, color_index=None, rgb=None):
        """Color a session clip by palette index or RGB."""
        try:
            track = self._get_track(track_index)
            clip_slots = self._safe(track, "clip_slots", []) or []
            if clip_index < 0 or clip_index >= len(clip_slots):
                raise IndexError("Clip index out of range")
            if not clip_slots[clip_index].has_clip:
                raise Exception("No clip in slot")
            clip = clip_slots[clip_index].clip
            result = {"track_index": track_index, "clip_index": clip_index, "clip_name": clip.name}
            result.update(self._apply_color(clip, color_index, rgb))
            return result
        except Exception as e:
            self.log_message("Error setting clip color: " + str(e))
            raise

    def _set_track_color(self, track_index, color_index=None, rgb=None):
        """Color a track (-1 master, -2/-3 returns) by palette index or RGB."""
        try:
            track = self._get_track(track_index)
            result = {"track_index": track_index, "track_name": track.name}
            result.update(self._apply_color(track, color_index, rgb))
            return result
        except Exception as e:
            self.log_message("Error setting track color: " + str(e))
            raise
```

- [ ] **Step 4: Add colors to the reads** — same file

In `_get_track_info`, after the `clip_info = {...}` dict literal inside `if slot.has_clip:`:

```python
                    clip_info.update(self._color_fields(clip))
```

and after the `result = {...}` literal (before `return result`):

```python
            result.update(self._color_fields(track))
```

In `_get_arrangement_clips` **and** in `_get_full_arrangement`, after each `clip_info = {...}` literal:

```python
                    clip_info.update(self._color_fields(clip))
```

(indent to match: `_get_full_arrangement`'s literal sits one level deeper).

- [ ] **Step 5: Run to verify it passes**

Run: `/Users/sami-inc/Code/ableton-mcp-pro/.venv/bin/python -m unittest discover -s tests -v`
Expected: all tests OK

- [ ] **Step 6: Add the server tools** — `MCP_Server/server.py`

Extend the import block from Task 1:

```python
try:
    from MCP_Server import camelot, notation
except ImportError:  # launched as `python MCP_Server/server.py`
    import camelot
    import notation
```

In `is_modifying_command`, change `"add_notes_to_clip", "set_clip_name",` to `"add_notes_to_clip", "set_clip_name", "set_clip_color", "set_track_color",`.

After the `set_clip_name` tool:

```python
@mcp.tool()
def set_clip_color(ctx: Context, track_index: int, clip_index: int, color: Optional[str] = None,
                   color_index: Optional[int] = None, key: Optional[str] = None) -> str:
    """
    Color a session clip. Pass exactly one of:
    - color: "#RRGGBB" — Live snaps it to the nearest entry in its 70-color palette
    - color_index: 0-69, Live's palette index
    - key: a musical key — "F minor", "F#m", "Bb" (major), "Ebmaj" — or a Camelot code like "8A".
      Colors by Camelot number: relative major/minor share a color, and keys a fifth
      apart get neighbouring hues, so harmonically compatible clips look alike.

    Returns the color Live actually applied (plus the Camelot code for a key).
    """
    try:
        color_params, code = camelot.resolve_color(color, color_index, key)
        ableton = get_ableton_connection()
        result = ableton.send_command("set_clip_color", dict(
            {"track_index": track_index, "clip_index": clip_index}, **color_params))
        if code:
            result["camelot"] = code
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error setting clip color: {str(e)}")
        return f"Error setting clip color: {str(e)}"

@mcp.tool()
def set_track_color(ctx: Context, track_index: int, color: Optional[str] = None,
                    color_index: Optional[int] = None) -> str:
    """
    Color a track. Pass exactly one of color ("#RRGGBB", snapped to Live's palette)
    or color_index (0-69).

    Parameters:
    - track_index: 0+ for tracks, -1 for master, -2/-3 for return A/B
    """
    try:
        color_params, _ = camelot.resolve_color(color, color_index)
        ableton = get_ableton_connection()
        result = ableton.send_command("set_track_color", dict({"track_index": track_index}, **color_params))
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error setting track color: {str(e)}")
        return f"Error setting track color: {str(e)}"
```

- [ ] **Step 7: Smoke-check and commit**

Run: `/Users/sami-inc/Code/ableton-mcp-pro/.venv/bin/python -c "import MCP_Server.server as s; print('ok')"`
Expected: `ok`

```bash
git add AbletonMCP_Remote_Script/__init__.py MCP_Server/server.py tests/test_remote_script.py
git commit -m "feat: set and read clip and track colors, with key-based coloring"
```

---

### Task 5: Reading the user's selection

**Files:**
- Modify: `AbletonMCP_Remote_Script/__init__.py` (socket-thread dispatch; new `_index_in`, `_track_index_of`, `_describe_clip_slot`, `_describe_clip`, `_get_selected_context`)
- Modify: `MCP_Server/server.py` (new tool `get_selected_context`)
- Test: `tests/test_remote_script.py`

**Interfaces:**
- Produces: Remote command `get_selected_context {}` returning the shape in the spec, section B.

- [ ] **Step 1: Write the failing tests** — append to `tests/test_remote_script.py`, before the `if __name__` block

```python
class SelectedContextTest(unittest.TestCase):
    def setUp(self):
        self.clip = Obj(name="Bass A", is_arrangement_clip=False)
        self.empty_slot = Obj(has_clip=False, clip=None)
        self.slot = Obj(has_clip=True, clip=self.clip)
        self.device = Obj(name="Operator")
        self.track = Obj(name="BASS", clip_slots=[self.empty_slot, self.slot],
                                           devices=[Obj(name="EQ"), self.device],
                                           arrangement_clips=[],
                                           view=Obj(selected_device=self.device))
        self.slot.canonical_parent = self.track
        self.empty_slot.canonical_parent = self.track
        self.clip.canonical_parent = self.slot
        self.other = Obj(name="KICK", clip_slots=[], devices=[], arrangement_clips=[],
                                           view=Obj(selected_device=None))
        self.ret = Obj(name="A-Reverb", devices=[], view=Obj(selected_device=None))
        self.scene = Obj(name="Drop")
        self.view = Obj(selected_track=self.track, selected_scene=self.scene,
                                          highlighted_clip_slot=self.slot, detail_clip=self.clip)
        self.song = Obj(tracks=[self.other, self.track], return_tracks=[self.ret],
                                          master_track=Obj(name="Main"),
                                          scenes=[Obj(name="Intro"), self.scene],
                                          view=self.view, current_song_time=32.0, is_playing=False)
        self.script = make_script(self.song)

    def test_full_context(self):
        self.assertEqual(self.script._get_selected_context(), {
            "selected_track": {"index": 1, "name": "BASS"},
            "selected_scene": {"index": 1, "name": "Drop"},
            "highlighted_clip_slot": {"track_index": 1, "clip_index": 1, "has_clip": True, "clip_name": "Bass A"},
            "detail_clip": {"name": "Bass A", "view": "session", "track_index": 1, "clip_index": 1},
            "selected_device": {"index": 1, "name": "Operator"},
            "current_song_time": 32.0,
            "is_playing": False,
        })

    def test_return_and_master_indices(self):
        self.view.selected_track = self.ret
        self.assertEqual(self.script._get_selected_context()["selected_track"], {"index": -2, "name": "A-Reverb"})
        self.view.selected_track = self.song.master_track
        self.assertEqual(self.script._get_selected_context()["selected_track"]["index"], -1)

    def test_arrangement_detail_clip(self):
        arr_clip = Obj(name="Lead", is_arrangement_clip=True, start_time=64.0,
                                         canonical_parent=self.track)
        self.track.arrangement_clips = [Obj(name="x"), arr_clip]
        self.view.detail_clip = arr_clip
        self.assertEqual(self.script._get_selected_context()["detail_clip"], {
            "name": "Lead", "view": "arrangement", "track_index": 1, "arrangement_clip_index": 1,
            "start_time": 64.0})

    def test_nothing_selected_is_nulls_not_errors(self):
        self.view.selected_track = None
        self.view.selected_scene = None
        self.view.highlighted_clip_slot = None
        self.view.detail_clip = None
        context = self.script._get_selected_context()
        for section in ("selected_track", "selected_scene", "highlighted_clip_slot", "detail_clip",
                        "selected_device"):
            self.assertIsNone(context[section], section)

    def test_unlocatable_objects_degrade_to_partial_info(self):
        del self.clip.canonical_parent
        self.assertEqual(self.script._get_selected_context()["detail_clip"], {"name": "Bass A"})
```

- [ ] **Step 2: Run to verify it fails**

Run: `/Users/sami-inc/Code/ableton-mcp-pro/.venv/bin/python -m unittest discover -s tests -v`
Expected: `AttributeError: 'AbletonMCP' object has no attribute '_get_selected_context'`

- [ ] **Step 3: Implement** — `AbletonMCP_Remote_Script/__init__.py`

In the socket-thread dispatch, right after the `get_locators` branch:

```python
            elif command_type == "get_selected_context":
                response["result"] = self._get_selected_context()
```

After `_set_track_color`, add:

```python
    @staticmethod
    def _index_in(items, obj):
        """Position of a Live object in a Live list, by equality (wrappers are not identical)."""
        for i, item in enumerate(items):
            if item == obj:
                return i
        return None

    def _track_index_of(self, track):
        """Project convention: 0+ tracks, -1 master, -2 - i for return track i."""
        index = self._index_in(self._song.tracks, track)
        if index is not None:
            return index
        index = self._index_in(self._song.return_tracks, track)
        if index is not None:
            return -2 - index
        if track == self._song.master_track:
            return -1
        return None

    def _describe_clip_slot(self, slot):
        track = slot.canonical_parent
        return {
            "track_index": self._track_index_of(track),
            "clip_index": self._index_in(track.clip_slots, slot),
            "has_clip": slot.has_clip,
            "clip_name": slot.clip.name if slot.has_clip else None,
        }

    def _describe_clip(self, clip):
        info = {"name": clip.name}
        try:
            parent = clip.canonical_parent
            if self._safe(clip, "is_arrangement_clip", False):
                info.update({
                    "view": "arrangement",
                    "track_index": self._track_index_of(parent),
                    "arrangement_clip_index": self._index_in(parent.arrangement_clips, clip),
                    "start_time": clip.start_time,
                })
            else:
                slot = self._describe_clip_slot(parent)
                info.update({"view": "session", "track_index": slot["track_index"],
                             "clip_index": slot["clip_index"]})
        except Exception as e:
            self.log_message("Could not locate detail clip: " + str(e))
        return info

    def _get_selected_context(self):
        """What the user has selected in Live. Each part is None when Live has
        nothing selected there or cannot resolve it, never an error."""
        view = self._song.view
        context = {
            "selected_track": None,
            "selected_scene": None,
            "highlighted_clip_slot": None,
            "detail_clip": None,
            "selected_device": None,
            "current_song_time": self._safe(self._song, "current_song_time"),
            "is_playing": self._safe(self._song, "is_playing"),
        }
        track = self._safe(view, "selected_track")
        if track is not None:
            context["selected_track"] = {"index": self._track_index_of(track), "name": track.name}
            device = self._safe(self._safe(track, "view"), "selected_device")
            if device is not None:
                context["selected_device"] = {"index": self._index_in(track.devices, device), "name": device.name}
        scene = self._safe(view, "selected_scene")
        if scene is not None:
            context["selected_scene"] = {"index": self._index_in(self._song.scenes, scene), "name": scene.name}
        slot = self._safe(view, "highlighted_clip_slot")
        if slot is not None:
            try:
                context["highlighted_clip_slot"] = self._describe_clip_slot(slot)
            except Exception as e:
                self.log_message("Could not locate highlighted clip slot: " + str(e))
        clip = self._safe(view, "detail_clip")
        if clip is not None:
            context["detail_clip"] = self._describe_clip(clip)
        return context
```

- [ ] **Step 4: Run to verify it passes**

Run: `/Users/sami-inc/Code/ableton-mcp-pro/.venv/bin/python -m unittest discover -s tests -v`
Expected: all tests OK

- [ ] **Step 5: Add the server tool** — `MCP_Server/server.py`, after `get_track_info`

```python
@mcp.tool()
def get_selected_context(ctx: Context) -> str:
    """
    What the user currently has selected in Live: track, scene, highlighted clip
    slot, the clip open in the detail view (session or arrangement), selected
    device, and the playhead. Call this when the user says "this track", "this
    clip", "here" instead of asking them for indices. Parts with nothing
    selected are null.
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("get_selected_context")
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error getting selected context: {str(e)}")
        return f"Error getting selected context: {str(e)}"
```

- [ ] **Step 6: Smoke-check and commit**

Run: `/Users/sami-inc/Code/ableton-mcp-pro/.venv/bin/python -c "import MCP_Server.server as s; print('ok')"`
Expected: `ok`

```bash
git add AbletonMCP_Remote_Script/__init__.py MCP_Server/server.py tests/test_remote_script.py
git commit -m "feat: read the user's current selection in Live"
```

---

### Task 6: Song scale (Live 12)

**Files:**
- Modify: `AbletonMCP_Remote_Script/__init__.py` (command list + routing; `_get_session_info`; `_get_clip_notes`; `_get_arrangement_clip_notes`; new `_scale_fields`, `_set_song_scale`)
- Modify: `MCP_Server/server.py` (`is_modifying_command`; new tool `set_song_scale`)
- Test: `tests/test_remote_script.py`

**Interfaces:**
- Consumes: `camelot.parse_root_note` (Task 3).
- Produces: Remote command `set_song_scale {root_note?, scale_name?, scale_mode?}` returning `{root_note, root_note_name, scale_name, scale_mode}`; the same four keys on `get_session_info`, and on `get_clip_notes` / `get_arrangement_clip_notes` only when the clip exposes `scale_name`.

- [ ] **Step 1: Write the failing tests** — append to `tests/test_remote_script.py`, before the `if __name__` block

```python
def live12_song(**extra):
    mixer = Obj(volume=Obj(value=0.85), panning=Obj(value=0.5))
    fields = dict(tempo=124.0, signature_numerator=4, signature_denominator=4, tracks=[], return_tracks=[],
                  master_track=Obj(mixer_device=mixer))
    fields.update(extra)
    return Obj(**fields)


class ScaleTest(unittest.TestCase):
    def test_session_info_reports_scale(self):
        script = make_script(live12_song(root_note=5, scale_name="Minor", scale_mode=True))
        info = script._get_session_info()
        self.assertEqual((info["root_note"], info["root_note_name"], info["scale_name"], info["scale_mode"]),
                         (5, "F", "Minor", True))

    def test_session_info_on_live_11_is_nulls(self):
        info = make_script(live12_song())._get_session_info()
        self.assertEqual((info["root_note"], info["root_note_name"], info["scale_name"]), (None, None, None))

    def test_set_song_scale_sets_only_what_is_given(self):
        song = live12_song(root_note=0, scale_name="Major", scale_mode=False)
        result = make_script(song)._set_song_scale(root_note=9, scale_name="Dorian")
        self.assertEqual((song.root_note, song.scale_name, song.scale_mode), (9, "Dorian", False))
        self.assertEqual(result, {"root_note": 9, "root_note_name": "A", "scale_name": "Dorian",
                                  "scale_mode": False})

    def test_set_song_scale_rejects_bad_root_and_old_live(self):
        with self.assertRaises(ValueError):
            make_script(live12_song(root_note=0, scale_name="Major", scale_mode=False))._set_song_scale(root_note=12)
        with self.assertRaisesRegex(Exception, "Live 12"):
            make_script(live12_song())._set_song_scale(scale_name="Minor")

    def test_clip_notes_include_clip_scale_only_when_exposed(self):
        clip = Obj(name="c", length=4.0, is_midi_clip=True,
                                     get_notes_extended=lambda **kwargs: [])
        song = live12_song(tracks=[Obj(clip_slots=[Obj(has_clip=True,
                                                                                          clip=clip)])])
        script = make_script(song)
        self.assertNotIn("scale_name", script._get_clip_notes(0, 0))
        clip.root_note, clip.scale_name = 2, "Minor"
        result = script._get_clip_notes(0, 0)
        self.assertEqual((result["root_note_name"], result["scale_name"]), ("D", "Minor"))
```

- [ ] **Step 2: Run to verify it fails**

Run: `/Users/sami-inc/Code/ableton-mcp-pro/.venv/bin/python -m unittest discover -s tests -v`
Expected: `KeyError: 'root_note'` and `AttributeError: ... '_set_song_scale'`

- [ ] **Step 3: Implement** — `AbletonMCP_Remote_Script/__init__.py`

After `HOST = "localhost"` (before `_is_number`):

```python
NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
```

In the main-thread command list, change `"set_tempo", "fire_clip", "stop_clip",` to `"set_tempo", "set_song_scale", "fire_clip", "stop_clip",`. In `main_thread_task`, right after the `set_tempo` branch:

```python
                        elif command_type == "set_song_scale":
                            result = self._set_song_scale(params.get("root_note"), params.get("scale_name"),
                                                          params.get("scale_mode"))
```

After `_color_fields`, add:

```python
    @classmethod
    def _scale_fields(cls, obj):
        """Live 12 scale of a Song (or Clip, where exposed). All None before Live 12."""
        root = cls._safe(obj, "root_note")
        return {
            "root_note": root,
            "root_note_name": NOTE_NAMES[root] if isinstance(root, int) and 0 <= root < 12 else None,
            "scale_name": cls._safe(obj, "scale_name"),
            "scale_mode": cls._safe(obj, "scale_mode"),
        }

    def _set_song_scale(self, root_note=None, scale_name=None, scale_mode=None):
        """Set the song's root note (0-11), scale name and/or scale mode (Live 12+)."""
        try:
            if self._safe(self._song, "scale_name") is None:
                raise Exception("Song scale needs Live 12 or later")
            if root_note is not None:
                if isinstance(root_note, bool) or not isinstance(root_note, int) or not 0 <= root_note <= 11:
                    raise ValueError("root_note must be an integer 0-11, got {0!r}".format(root_note))
                self._song.root_note = root_note
            if scale_name is not None:
                self._song.scale_name = str(scale_name)
            if scale_mode is not None:
                self._song.scale_mode = bool(scale_mode)
            return self._scale_fields(self._song)
        except Exception as e:
            self.log_message("Error setting song scale: " + str(e))
            raise
```

In `_get_session_info`, before `return result`:

```python
            result.update(self._scale_fields(self._song))
```

In both `_get_clip_notes` and `_get_arrangement_clip_notes`, change `return {` to `result = {`, and after that dict literal's closing `}` add:

```python
            scale = self._scale_fields(clip)
            if scale["scale_name"] is not None:
                result.update(scale)
            return result
```

- [ ] **Step 4: Run to verify it passes**

Run: `/Users/sami-inc/Code/ableton-mcp-pro/.venv/bin/python -m unittest discover -s tests -v`
Expected: all tests OK

- [ ] **Step 5: Add the server tool** — `MCP_Server/server.py`

In `is_modifying_command`, change `"set_tempo", "fire_clip", "stop_clip",` to `"set_tempo", "set_song_scale", "fire_clip", "stop_clip",`. After the `set_tempo` tool:

```python
@mcp.tool()
def set_song_scale(ctx: Context, root_note: Optional[Union[str, int]] = None, scale_name: Optional[str] = None,
                   scale_mode: Optional[bool] = None) -> str:
    """
    Set the song's key (Live 12+). Pass any combination of:
    - root_note: note name ("F#", "Gb") or 0-11 (0 = C)
    - scale_name: as Live names it, e.g. "Major", "Minor", "Dorian"
    - scale_mode: true to turn on Scale Mode (highlights and folds to the scale in clips)

    Returns the scale Live reports back. The current scale is also in get_session_info.
    """
    try:
        params = {}
        if root_note is not None:
            params["root_note"] = camelot.parse_root_note(root_note)
        if scale_name is not None:
            params["scale_name"] = scale_name
        if scale_mode is not None:
            params["scale_mode"] = scale_mode
        if not params:
            raise ValueError("Pass at least one of root_note, scale_name, scale_mode")
        ableton = get_ableton_connection()
        result = ableton.send_command("set_song_scale", params)
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error setting song scale: {str(e)}")
        return f"Error setting song scale: {str(e)}"
```

- [ ] **Step 6: Smoke-check and commit**

Run: `/Users/sami-inc/Code/ableton-mcp-pro/.venv/bin/python -c "import MCP_Server.server as s; print('ok')"`
Expected: `ok`

```bash
git add AbletonMCP_Remote_Script/__init__.py MCP_Server/server.py tests/test_remote_script.py
git commit -m "feat: read and set the Live 12 song scale"
```

---

### Task 7: Docs and full verification

**Files:**
- Modify: `README.md` (Available Tools lists)
- Modify: `NEXT_STEPS.md` (Completed section)
- Modify: `DEVELOPMENT.md` (how to run tests; the three places a modifying command is registered)

- [ ] **Step 1: README** — in `## Available Tools`, append `, get_selected_context` to the `### Read` list, and append `, set_clip_color, set_track_color, set_song_scale` to the `### Modify` list. Under the Read list add:

```markdown
`get_clip_notes` / `get_arrangement_clip_notes` take `format="csv"` for a compact
`pitch,start,dur,vel,mute` listing, and `add_notes_to_clip` accepts the same CSV.
```

- [ ] **Step 2: NEXT_STEPS** — add under `## Completed`, before `### Advanced`:

```markdown
### Musical Context (ported from MIDIjourney)
- [x] **Clip / track colors** — `set_clip_color(track_index, clip_index, color | color_index | key)`, `set_track_color(...)`; a `key` colors by Camelot number
- [x] **Selection** — `get_selected_context()` — selected track, scene, highlighted slot, detail clip, device
- [x] **Note validation** — invalid notes are rejected with their index before anything is written
- [x] **CSV notation** — `format="csv"` on note reads, CSV accepted by `add_notes_to_clip`
- [x] **Song scale (Live 12)** — `set_song_scale(root_note, scale_name, scale_mode)`; scale in `get_session_info`
```

- [ ] **Step 3: DEVELOPMENT.md** — after the `#### 2. MCP Server` subsection of "Step-by-Step: Adding a New Command", add:

```markdown
#### 3. Register a state-modifying command in all three places

1. The Remote Script's main-thread command list (`elif command_type in [...]`)
2. Its `main_thread_task` routing
3. The server's `is_modifying_command` list in `AbletonConnection.send_command` (longer timeout, settle delays)

### Tests

Pure logic (`MCP_Server/notation.py`, `MCP_Server/camelot.py`, `validate_notes`) and
Remote Script handlers are unit-tested with fake Live objects — `tests/remote_script_harness.py`
loads `__init__.py` with `_Framework` stubbed. Run from the repo root with a Python
that has `mcp` installed:

    .venv/bin/python -m unittest discover -s tests -v
```

- [ ] **Step 4: Full run**

Run: `/Users/sami-inc/Code/ableton-mcp-pro/.venv/bin/python -m unittest discover -s tests -v`
Expected: all tests OK

Run: `/Users/sami-inc/Code/ableton-mcp-pro/.venv/bin/python -c "import MCP_Server.server as s, asyncio; print(sorted(t.name for t in asyncio.run(s.mcp.list_tools()) if t.name in {'get_selected_context','set_clip_color','set_track_color','set_song_scale'}))"`
Expected: `['get_selected_context', 'set_clip_color', 'set_song_scale', 'set_track_color']`

- [ ] **Step 5: Commit**

```bash
git add README.md NEXT_STEPS.md DEVELOPMENT.md
git commit -m "docs: document colors, selection, CSV notes and song scale"
```

---

### Live verification (needs the user)

Not automatable from here: Live must load the new Remote Script. After the user copies
`__init__.py` into Live and reloads the control surface, check over TCP 9877:

1. `get_session_info` shows `root_note` / `scale_name` (non-null on Live 12).
2. `set_song_scale` with `scale_name="Dorian"` reads back `"Dorian"` — confirms the property is writable.
3. `set_clip_color` with `key="A minor"` and `key="C major"` land on the same `color_index`; 12 Camelot numbers give 12 distinct indices (palette snapping must not merge hues).
4. `get_selected_context` matches what is visibly selected, for a session clip and an arrangement clip — confirms `canonical_parent` / `is_arrangement_clip`.
5. `get_clip_notes` on a clip: note whether clip-level `scale_name` appears.
6. `add_notes_to_clip` with a pitch-128 note returns the validation message and writes nothing.
