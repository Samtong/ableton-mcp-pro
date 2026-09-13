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
