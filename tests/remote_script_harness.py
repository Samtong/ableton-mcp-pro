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
    """An AbletonMCP instance around a fake song: no socket server, no Live."""
    module = load_remote_script()
    script = object.__new__(module.AbletonMCP)
    script._song = song
    script.song = lambda: song
    # Live runs scheduled tasks on its main thread later; running them inline keeps
    # _process_command's queue hand-off synchronous. Delays are recorded for tests.
    script.scheduled_delays = []
    script.schedule_message = lambda delay, task: (script.scheduled_delays.append(delay), task())
    return script
