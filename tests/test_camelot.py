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
