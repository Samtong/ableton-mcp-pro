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

    def test_negative_zero_prints_as_zero(self):
        self.assertEqual(notes_to_csv([dict(NOTES[0], start_time=-0.0)]).split("\n")[1], "64,0,0.5,90,0")


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

    def test_mute_accepts_true(self):
        self.assertTrue(csv_to_notes("60,0,0.5,100,true")[0]["mute"])
        self.assertTrue(csv_to_notes("60,0,0.5,100,TRUE")[0]["mute"])

    def test_too_many_columns_is_an_error(self):
        with self.assertRaisesRegex(ValueError, "Line 1"):
            csv_to_notes("60,0,0.5,100,0,extra")

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
