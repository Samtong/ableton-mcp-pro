import colorsys
import json
import pathlib
import unittest

from MCP_Server.camelot import (NOTE_NAMES, camelot_code, palette_index_for_key, parse_hex_color,
                                parse_root_note, pitch_class, resolve_color)

LIVE12_PALETTE = json.loads((pathlib.Path(__file__).parent / "live12_palette.json").read_text())["colors"]


def hsv(palette_index):
    rgb = int(LIVE12_PALETTE[palette_index][1:], 16)
    return colorsys.rgb_to_hsv((rgb >> 16) / 255.0, (rgb >> 8 & 255) / 255.0, (rgb & 255) / 255.0)

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


class PaletteIndexForKeyTest(unittest.TestCase):
    """Keys map straight to Live palette slots: RGB would be snapped by Live, and on
    Live 12 Camelot 8 and 9 snapped to the same slot."""

    def indices(self):
        return [palette_index_for_key("{0}A".format(n)) for n in range(1, 13)]

    def test_relative_keys_share_a_slot(self):
        self.assertEqual(palette_index_for_key("A minor"), palette_index_for_key("C major"))
        for n in range(1, 13):
            self.assertEqual(palette_index_for_key("{0}A".format(n)), palette_index_for_key("{0}B".format(n)))

    def test_twelve_distinct_slots_of_the_palette(self):
        self.assertEqual(len(set(self.indices())), 12)
        for index in self.indices():
            self.assertTrue(0 <= index <= 69, index)

    def test_slots_walk_round_the_hue_circle_in_wheel_order(self):
        hues = [hsv(i)[0] * 360 for i in self.indices()]
        self.assertEqual(hues, sorted(hues), "wheel neighbours must be hue neighbours")
        gaps = [b - a for a, b in zip(hues, hues[1:])] + [360 - hues[-1] + hues[0]]
        self.assertGreaterEqual(min(gaps), 15, gaps)

    def test_slots_are_vivid(self):
        # 0.5, not higher: Live 12's palette has no violet or purple above 0.53 that is
        # also bright. The pastel row sits at 0.40-0.45, so this still excludes it.
        for index in self.indices():
            _, saturation, value = hsv(index)
            self.assertGreaterEqual(saturation, 0.5, index)
            self.assertGreaterEqual(value, 0.75, index)


class ResolveColorTest(unittest.TestCase):
    def test_each_form(self):
        self.assertEqual(resolve_color(color="#ff8800"), ({"rgb": 0xFF8800}, None))
        self.assertEqual(resolve_color(color_index=12), ({"color_index": 12}, None))
        self.assertEqual(resolve_color(key="F minor"), ({"color_index": palette_index_for_key("4A")}, "4A"))

    def test_exactly_one(self):
        with self.assertRaisesRegex(ValueError, "none"):
            resolve_color()
        with self.assertRaisesRegex(ValueError, "color, key"):
            resolve_color(color="#000000", key="Am")

    def test_bad_values(self):
        for kwargs in ({"color": "orange"}, {"color_index": 70}, {"color_index": True}):
            with self.assertRaises(ValueError):
                resolve_color(**kwargs)
        self.assertEqual(resolve_color(color_index=0), ({"color_index": 0}, None))
        self.assertEqual(resolve_color(color_index=69), ({"color_index": 69}, None))
        self.assertEqual(parse_hex_color("00ff00"), 0x00FF00)


if __name__ == "__main__":
    unittest.main()
