# Ableton MCP Pro — gotchas learned the hard way

## Reloading `AbletonMCP_Remote_Script/__init__.py` requires a FULL Ableton Live restart

Deselecting/reselecting "AbletonMCP" as the Control Surface in
**Preferences → Link/Tempo/MIDI** does **not** re-read the file from disk.
Ableton keeps the Python module already imported in memory and just
re-instantiates the control surface class from it. Any edit to
`AbletonMCP_Remote_Script/__init__.py` (new commands, bug fixes, etc.) only
takes effect after you **Quit Ableton Live completely (Cmd+Q) and reopen it**.
Toggling the preference is not enough and will silently keep running the old
code (leading to confusing "Unknown command" errors even though the source
file is correct and even though there's a real `Server thread started` /
`AbletonMCP initialized` log line in `Live x/Log.txt` — that log line just
confirms re-instantiation, not a fresh import).

The MCP server side (`MCP_Server/server.py`) is a normal persistent stdio
process managed by the MCP host (Claude Code) — editing it requires
restarting the Claude Code session (or the MCP connection) for changes to
take effect, same idea, different process.

## `Song.current_song_time` is applied asynchronously by Live's engine

Setting `self._song.current_song_time = x` and reading it back
**immediately in the same command** can return a stale/optimistic value —
sometimes even the value from the *previous* command, one call behind. A
tight retry loop with `time.sleep()` inside a single command does **not**
help, because that loop runs on Live's own main thread (via
`schedule_message`), which blocks the very thread that needs to process the
transport update.

The fix that actually works: split "move the playhead" and "act on the
current position" (e.g. `set_or_delete_cue()` to add/remove an arrangement
locator) into **two separate round-trip commands**, and confirm the position
really landed via a **separate** command (e.g. `get_arrangement_info`) rather
than trusting the return value of the command that set it. See
`_ensure_cue_at_current_time` / `_remove_cue_at_current_time` in the Remote
Script and `_goto_song_time` in `MCP_Server/server.py` for the pattern.

Also: if `get_arrangement_info` shows `"back_to_arranger": true`, the
transport can be extra flaky (likely because a session clip is still
queued/active). Call `set_back_to_arranger` + `stop_playback` first if
`set_song_time` isn't landing.

## `CuePoint.name` is READ-ONLY in the Remote Script API (this Live 12.0.15 build) — do not attempt to rename cue points via the API

Generic web research (Cycling '74 LOM docs, AbletonOSC source) suggested
`cue_point.name = "foo"` should work in Live 12. It does not, in this
Remote Script binding. Confirmed by direct introspection:

```
type(cp)  -> <class 'Song.CuePoint'>
dir(cp)   -> [..., 'add_name_listener', 'canonical_parent', 'jump', 'name',
              'name_has_listener', 'remove_name_listener', 'time',
              'time_has_listener', ...]
```

`name` exists (readable, observable via `add_name_listener`) but assigning
to it always raises `AttributeError: can't set attribute` — reproducible
100% of the time, on freshly-created cue points, regardless of timing/lag
workarounds. There is no `set_name()` or other setter method either — this
particular Python binding (`Song.CuePoint`, as exposed to Remote Scripts)
just doesn't expose a name setter, unlike whatever binding AbletonOSC or
Max for Live use.

**Practical consequence:** `add_locator`/`ensure_cue_at_current_time` can
still create a cue point at the right beat position (that part works
fine), but the `name` parameter is a no-op — the cue keeps Live's default
auto-incrementing name ("1", "2", "3", ...). If you need descriptive
locator names, the position is scriptable but the label is not: tell the
user which name goes with which beat position and have them rename each
one by hand (double-click the locator name in the Arrangement ruler — a
few seconds per locator, much faster than fighting this further).

Don't re-attempt `cp.name = x` fixes without new evidence — this was
checked directly via `dir()` on a live object, not inferred from behavior.
