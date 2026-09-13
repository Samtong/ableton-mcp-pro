"""MCP tool wrappers in server.py, with Ableton replaced at the TCP boundary."""
import json
import logging
import unittest
from unittest import mock

import MCP_Server.server as server
from MCP_Server.camelot import color_for_key


class FakeAbleton(object):
    """Stands in for AbletonConnection: records commands, answers with a canned result."""

    def __init__(self, result):
        self.result = result
        self.sent = []

    def send_command(self, command_type, params=None):
        self.sent.append((command_type, params))
        return self.result


class ToolTestCase(unittest.TestCase):
    result = {}

    def setUp(self):
        logging.disable(logging.CRITICAL)
        self.ableton = FakeAbleton(json.loads(json.dumps(self.result)))
        patcher = mock.patch.object(server, "get_ableton_connection", lambda: self.ableton)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.addCleanup(logging.disable, logging.NOTSET)

    def assertNothingSent(self, output, error_prefix):
        self.assertTrue(output.startswith(error_prefix), output)
        self.assertEqual(self.ableton.sent, [])


class SetClipColorTest(ToolTestCase):
    result = {"clip_name": "Bass", "color": 1, "color_index": 2}

    def test_key_sends_its_camelot_color_and_names_the_code(self):
        output = json.loads(server.set_clip_color(None, 1, 2, key="F minor"))
        self.assertEqual(self.ableton.sent,
                         [("set_clip_color", {"track_index": 1, "clip_index": 2, "rgb": color_for_key("4A")})])
        self.assertEqual(output["camelot"], "4A")
        self.assertEqual(output["color_index"], 2)

    def test_hex_color(self):
        output = json.loads(server.set_clip_color(None, 0, 3, color="#FF8800"))
        self.assertEqual(self.ableton.sent, [("set_clip_color", {"track_index": 0, "clip_index": 3, "rgb": 0xFF8800})])
        self.assertNotIn("camelot", output)

    def test_palette_index(self):
        server.set_clip_color(None, 0, 3, color_index=69)
        self.assertEqual(self.ableton.sent, [("set_clip_color", {"track_index": 0, "clip_index": 3, "color_index": 69})])

    def test_argument_errors_never_reach_ableton(self):
        self.assertNothingSent(server.set_clip_color(None, 0, 0), "Error setting clip color")
        self.assertNothingSent(server.set_clip_color(None, 0, 0, color="#000000", key="Am"), "Error setting clip color")
        self.assertNothingSent(server.set_clip_color(None, 0, 0, key="H minor"), "Error setting clip color")


class SetTrackColorTest(ToolTestCase):
    result = {"track_name": "Main", "color": 1, "color_index": 5}

    def test_sends_palette_index_for_master(self):
        output = json.loads(server.set_track_color(None, -1, color_index=5))
        self.assertEqual(self.ableton.sent, [("set_track_color", {"track_index": -1, "color_index": 5})])
        self.assertEqual(output["track_name"], "Main")

    def test_hex_color(self):
        server.set_track_color(None, 2, color="00ff00")
        self.assertEqual(self.ableton.sent, [("set_track_color", {"track_index": 2, "rgb": 0x00FF00})])

    def test_needs_exactly_one_color(self):
        self.assertNothingSent(server.set_track_color(None, 0), "Error setting track color")
        self.assertNothingSent(server.set_track_color(None, 0, color="#000000", color_index=1),
                               "Error setting track color")


class GetSelectedContextTest(ToolTestCase):
    result = {"selected_track": {"index": 2, "name": "BASS"}, "detail_clip": None}

    def test_returns_the_context_as_json(self):
        output = json.loads(server.get_selected_context(None))
        self.assertEqual([command for command, _ in self.ableton.sent], ["get_selected_context"])
        self.assertEqual(output, self.result)


class SetSongScaleTest(ToolTestCase):
    result = {"root_note": 6, "root_note_name": "F#", "scale_name": "Minor", "scale_mode": False}

    def test_note_name_root_is_converted(self):
        output = json.loads(server.set_song_scale(None, root_note="Gb", scale_name="Minor"))
        self.assertEqual(self.ableton.sent, [("set_song_scale", {"root_note": 6, "scale_name": "Minor"})])
        self.assertEqual(output, self.result)

    def test_integer_root_and_turning_scale_mode_off(self):
        server.set_song_scale(None, root_note=0, scale_mode=False)
        self.assertEqual(self.ableton.sent, [("set_song_scale", {"root_note": 0, "scale_mode": False})])

    def test_bad_or_missing_arguments_never_reach_ableton(self):
        self.assertNothingSent(server.set_song_scale(None), "Error setting song scale")
        self.assertNothingSent(server.set_song_scale(None, root_note="H"), "Error setting song scale")
        self.assertNothingSent(server.set_song_scale(None, root_note=12), "Error setting song scale")


CLIP = {"clip_name": "Bass", "length": 4.0, "note_count": 1,
        "notes": [{"pitch": 60, "start_time": 0.0, "duration": 0.5, "velocity": 100.0, "mute": False}]}


class GetClipNotesTest(ToolTestCase):
    result = CLIP

    def test_json_by_default(self):
        self.assertEqual(json.loads(server.get_clip_notes(None, 0, 1)), CLIP)
        self.assertEqual(self.ableton.sent, [("get_clip_notes", {"track_index": 0, "clip_index": 1})])

    def test_csv(self):
        self.assertEqual(server.get_clip_notes(None, 0, 1, format="csv"),
                         '# clip "Bass" length=4 notes=1\npitch,start,dur,vel,mute\n60,0,0.5,100,0')

    def test_unknown_format_is_rejected_before_asking_ableton(self):
        self.assertNothingSent(server.get_clip_notes(None, 0, 1, format="xml"), "Error getting clip notes")


class GetArrangementClipNotesTest(ToolTestCase):
    result = dict(CLIP, start_time=32.0, arrangement_clip_index=0)

    def test_csv_includes_the_clip_position(self):
        output = server.get_arrangement_clip_notes(None, 3, 0, format="csv")
        self.assertTrue(output.startswith('# clip "Bass" length=4 start=32 notes=1\n'), output)
        self.assertEqual(self.ableton.sent,
                         [("get_arrangement_clip_notes", {"track_index": 3, "arrangement_clip_index": 0})])

    def test_unknown_format_is_rejected_before_asking_ableton(self):
        self.assertNothingSent(server.get_arrangement_clip_notes(None, 3, 0, format="midi"),
                               "Error getting arrangement clip notes")


class AddNotesToClipTest(ToolTestCase):
    result = {"note_count": 2}

    def test_csv_text_is_sent_as_notes(self):
        output = server.add_notes_to_clip(None, 0, 1, "pitch,start,dur,vel\n60,0,0.5,100\n64,0.5,0.5,90,1")
        self.assertEqual(output, "Added 2 notes to clip at track 0, slot 1")
        self.assertEqual(self.ableton.sent, [("add_notes_to_clip", {"track_index": 0, "clip_index": 1, "notes": [
            {"pitch": 60, "start_time": 0.0, "duration": 0.5, "velocity": 100.0, "mute": False},
            {"pitch": 64, "start_time": 0.5, "duration": 0.5, "velocity": 90.0, "mute": True},
        ]})])

    def test_note_list_is_sent_unchanged(self):
        notes = [{"pitch": 60, "start_time": 0}]
        server.add_notes_to_clip(None, 0, 1, notes)
        self.assertEqual(self.ableton.sent, [("add_notes_to_clip", {"track_index": 0, "clip_index": 1, "notes": notes})])

    def test_malformed_csv_never_reaches_ableton(self):
        self.assertNothingSent(server.add_notes_to_clip(None, 0, 1, "60,0,0.5"), "Error adding notes to clip")


class FakeSocket(object):
    def __init__(self):
        self.timeouts = []

    def sendall(self, data):
        pass

    def settimeout(self, timeout):
        self.timeouts.append(timeout)

    def recv(self, size):
        return json.dumps({"status": "success", "result": {}}).encode("utf-8")


class ModifyingCommandTimeoutTest(unittest.TestCase):
    """State-modifying commands get the longer timeout and settle delays."""

    def timeout_for(self, command_type):
        sock = FakeSocket()
        with mock.patch("time.sleep"), mock.patch.object(server.logger, "info"):
            server.AbletonConnection(host="localhost", port=0, sock=sock).send_command(command_type, {})
        return sock.timeouts[-1]

    def test_new_mutations_are_modifying(self):
        for command_type in ("set_clip_color", "set_track_color", "set_song_scale"):
            self.assertEqual(self.timeout_for(command_type), 15.0, command_type)

    def test_selection_read_is_not(self):
        self.assertEqual(self.timeout_for("get_selected_context"), 10.0)


if __name__ == "__main__":
    unittest.main()
