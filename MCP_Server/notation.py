"""Compact CSV form of MIDI notes.

A dense clip as JSON costs several times the tokens of the same notes as CSV,
in both directions: reading a clip and writing one.
"""
import json

HEADER = "pitch,start,dur,vel,mute"


def _num(value):
    """Shortest faithful text for a beat/velocity value: 1.0 -> '1', 0.250 -> '0.25'."""
    text = "{:.4f}".format(float(value)).rstrip("0").rstrip(".")
    return "0" if text == "-0" else text


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
