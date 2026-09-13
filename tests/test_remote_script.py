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
