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

    def test_boundaries_are_accepted(self):
        notes = rs.validate_notes([
            {"pitch": 0, "start_time": 0, "velocity": 0},
            {"pitch": 127, "start_time": 0, "velocity": 127},
        ])
        self.assertEqual([(n[0], n[3]) for n in notes], [(0, 0), (127, 127)])

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

    def test_six_problems_show_five_and_one_more(self):
        with self.assertRaisesRegex(ValueError, "and 1 more$"):
            rs.validate_notes([{"pitch": -1, "start_time": 0}] * 6)


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

    def test_palette_and_rgb_bounds_are_accepted(self):
        for kwargs, field, value in (({"color_index": 0}, "color_index", 0), ({"color_index": 69}, "color_index", 69),
                                     ({"rgb": 0}, "color", 0), ({"rgb": 0xFFFFFF}, "color", 0xFFFFFF)):
            self.script._set_clip_color(0, 0, **kwargs)
            self.assertEqual(getattr(self.clip, field), value, kwargs)

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

    def test_highlighted_empty_slot(self):
        self.view.highlighted_clip_slot = self.empty_slot
        self.assertEqual(self.script._get_selected_context()["highlighted_clip_slot"],
                         {"track_index": 1, "clip_index": 0, "has_clip": False, "clip_name": None})

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

    def test_top_root_note_and_turning_scale_mode_off(self):
        song = live12_song(root_note=0, scale_name="Major", scale_mode=True)
        result = make_script(song)._set_song_scale(root_note=11, scale_mode=False)
        self.assertEqual((song.root_note, song.scale_mode), (11, False))
        self.assertEqual(result["root_note_name"], "B")

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


def routing(name):
    return Obj(display_name=name)


class RoutingTest(unittest.TestCase):
    """Input routing is set by display name, since Live wants its own RoutingType objects."""

    def setUp(self):
        self.ext, self.twisted = routing("Ext: All Ins"), routing("TWISTED MIND")
        self.all_ch, self.post_fx = routing("All Channels"), routing("Post FX")
        self.channels = {self.ext: [self.all_ch], self.twisted: [routing("Pre FX"), self.post_fx]}
        owner = self

        class Track(Obj):
            @property
            def available_input_routing_channels(self):
                return owner.channels[self.input_routing_type]

        self.track = Track(name="SNIFF", available_input_routing_types=[self.ext, self.twisted],
                           input_routing_type=self.ext, input_routing_channel=self.all_ch,
                           output_routing_type=routing("Main"), output_routing_channel=routing(""),
                           available_output_routing_types=[routing("Main")],
                           available_output_routing_channels=[routing("")])
        self.script = make_script(Obj(tracks=[self.track], return_tracks=[], master_track=None))

    def test_get_track_routing_lists_current_and_available_names(self):
        result = self.script._get_track_routing(0)
        self.assertEqual(result["input_routing_type"], "Ext: All Ins")
        self.assertEqual(result["input_routing_channel"], "All Channels")
        self.assertEqual(result["available_input_routing_types"], ["Ext: All Ins", "TWISTED MIND"])
        self.assertEqual(result["available_input_routing_channels"], ["All Channels"])
        self.assertEqual(result["output_routing_type"], "Main")

    def test_sets_type_then_channel_from_the_new_type_list(self):
        result = self.script._set_track_input_routing(0, "twisted mind", "Post FX")
        self.assertIs(self.track.input_routing_type, self.twisted)
        self.assertIs(self.track.input_routing_channel, self.post_fx)
        self.assertEqual((result["input_routing_type"], result["input_routing_channel"]),
                         ("TWISTED MIND", "Post FX"))

    def test_type_only_keeps_live_default_channel(self):
        self.script._set_track_input_routing(0, "TWISTED MIND")
        self.assertIs(self.track.input_routing_type, self.twisted)
        self.assertIs(self.track.input_routing_channel, self.all_ch)

    def test_unknown_names_list_the_options(self):
        with self.assertRaisesRegex(ValueError, "TWISTED MIND"):
            self.script._set_track_input_routing(0, "Nope")
        with self.assertRaisesRegex(ValueError, "Pre FX"):
            self.script._set_track_input_routing(0, "TWISTED MIND", "Mid FX")


class DispatchTest(unittest.TestCase):
    """Commands reach their handlers through _process_command, mutations via the main thread."""

    def setUp(self):
        self.clip = Obj(name="Bass", color=0, color_index=0)
        self.track = Obj(name="BASS", clip_slots=[Obj(has_clip=True, clip=self.clip)], color=0, color_index=0)
        view = Obj(selected_track=None, selected_scene=None, highlighted_clip_slot=None, detail_clip=None)
        self.song = live12_song(tracks=[self.track], root_note=0, scale_name="Major", scale_mode=False,
                                view=view, current_song_time=8.0, is_playing=True)
        self.script = make_script(self.song)

    def send(self, command_type, **params):
        return self.script._process_command({"type": command_type, "params": params})

    def test_set_clip_color_runs_on_the_main_thread(self):
        response = self.send("set_clip_color", track_index=0, clip_index=0, color_index=7)
        self.assertEqual(response["status"], "success", response)
        self.assertEqual(response["result"]["color_index"], 7)
        self.assertEqual(self.script.scheduled_delays, [0])

    def test_set_track_color_runs_on_the_main_thread(self):
        response = self.send("set_track_color", track_index=0, rgb=0x123456)
        self.assertEqual(response["status"], "success", response)
        self.assertEqual(self.track.color, 0x123456)
        self.assertEqual(self.script.scheduled_delays, [0])

    def test_set_song_scale_runs_on_the_main_thread(self):
        response = self.send("set_song_scale", root_note=9, scale_name="Dorian", scale_mode=True)
        self.assertEqual(response["status"], "success", response)
        self.assertEqual(response["result"], {"root_note": 9, "root_note_name": "A", "scale_name": "Dorian",
                                              "scale_mode": True})
        self.assertEqual(self.script.scheduled_delays, [0])

    def test_get_selected_context_is_read_without_scheduling(self):
        response = self.send("get_selected_context")
        self.assertEqual(response["status"], "success", response)
        self.assertEqual((response["result"]["current_song_time"], response["result"]["is_playing"]), (8.0, True))
        self.assertEqual(self.script.scheduled_delays, [])

    def route_track(self):
        for side in ("input", "output"):
            setattr(self.track, side + "_routing_type", routing("Main"))
            setattr(self.track, side + "_routing_channel", routing(""))
            setattr(self.track, "available_" + side + "_routing_types", [routing("Ext: All Ins")])
            setattr(self.track, "available_" + side + "_routing_channels", [])

    def test_set_track_input_routing_runs_on_the_main_thread(self):
        self.route_track()
        response = self.send("set_track_input_routing", track_index=0, routing_type="Ext: All Ins")
        self.assertEqual(response["status"], "success", response)
        self.assertEqual(self.script.scheduled_delays, [0])

    def test_get_track_routing_is_read_without_scheduling(self):
        self.route_track()
        response = self.send("get_track_routing", track_index=0)
        self.assertEqual(response["status"], "success", response)
        self.assertEqual(self.script.scheduled_delays, [])

    def test_handler_errors_come_back_as_error_status(self):
        response = self.send("set_clip_color", track_index=0, clip_index=0)
        self.assertEqual(response["status"], "error")
        self.assertIn("exactly one", response["message"])


if __name__ == "__main__":
    unittest.main()
