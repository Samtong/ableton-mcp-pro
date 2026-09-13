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

    def test_integral_float_velocity_becomes_int(self):
        # CSV input yields floats; Live's legacy set_notes tuple wants an int velocity.
        [note] = rs.validate_notes([{"pitch": 60, "start_time": 0, "velocity": 100.0}])
        self.assertIs(type(note[3]), int)
        [note] = rs.validate_notes([{"pitch": 60, "start_time": 0, "velocity": 72.5}])
        self.assertEqual(note[3], 72.5)

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


if __name__ == "__main__":
    unittest.main()
