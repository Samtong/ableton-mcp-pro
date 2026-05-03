# Ableton MCP Pro

Full control of Ableton Live through AI assistants via the Model Context Protocol (MCP). Create tracks, program MIDI, load instruments, mix, automate, and record arrangements — all from natural language.

### Demo Tracks

- [claude_hardgroove](https://soundcloud.com/nicholasbien/claude_hardgroove)
- [claude_song1](https://soundcloud.com/nicholasbien/claude_song1)

Forked from [uisato/ableton-mcp-extended](https://github.com/uisato/ableton-mcp-extended), inspired by [ahujasid/ableton-mcp](https://github.com/ahujasid/ableton-mcp).

## What's New

This fork adds significant capabilities beyond the original:

- **Arrangement recording** — Record session clips into the arrangement with bar-accurate scene transitions
- **Arrangement view** — Read arrangement info, clips per track, full arrangement state; control loop, overdub, song position, and back-to-arranger
- **Arrangement playback** — Dedicated `play_arrangement` command that switches to arrangement view
- **Smooth automation envelopes** — Interpolated ramps between points (not just flat steps)
- **Full mixing** — Volume, panning, sends, mute, solo, arm for all tracks including master and returns
- **Master/return track support** — Use `track_index: -1` for master, `-2`/`-3` for return tracks across all mixing commands
- **Scene management** — Create, delete, rename, and fire scenes for arrangement workflows
- **Track management** — Create/delete/duplicate MIDI and audio tracks
- **Clip operations** — Duplicate, delete, rename, loop control, get/set notes
- **Device control** — Get/set any device parameter, batch updates, delete devices
- **Browser integration** — Browse and load instruments, effects, and presets by URI
- **Transport controls** — Tempo, time signature, metronome, record mode
- **Undo/redo** support

See [NEXT_STEPS.md](NEXT_STEPS.md) for the full feature list and roadmap.

## Music Production Skills

When used with [Claude Code](https://claude.com/claude-code), this project includes 20 production skills that guide Claude through genre-specific workflows — from sound design to pattern programming to mixing. Each skill provides specific, actionable parameter values.

### Available Skills

| Category | Skills |
|----------|--------|
| **Techno** | [techno-drums](.claude/skills/techno-drums/SKILL.md) — minimal/dark techno percussion with Operator synthesis<br>[techno-bass](.claude/skills/techno-bass/SKILL.md) — 3 Operator patches (sub, distorted, acid-influenced)<br>[hardgroove-drums](.claude/skills/hardgroove-drums/SKILL.md) — driving tom-heavy patterns with layered percussion<br>[hardgroove-bass](.claude/skills/hardgroove-bass/SKILL.md) — simple driving basslines with FM and acid variations |
| **House & Garage** | [house-drums](.claude/skills/house-drums/SKILL.md) — classic 4/4 patterns with open hats and congas<br>[house-chords](.claude/skills/house-chords/SKILL.md) — stabs, deep pads, disco filtered chords<br>[ukg-drums](.claude/skills/ukg-drums/SKILL.md) — 2-step patterns with gain staging and 5 pattern templates<br>[speed-garage](.claude/skills/speed-garage/SKILL.md) — walking FM bass, rave loops, vocal chops |
| **Trance** | [trance-bass](.claude/skills/trance-bass/SKILL.md) — 3 essential types (offbeat, filled 16ths, octave jump)<br>[trance-melodies](.claude/skills/trance-melodies/SKILL.md) — melody writing with call-and-response and tension/resolution |
| **Bass Music** | [acid-bass](.claude/skills/acid-bass/SKILL.md) — 303-style squelch with accent, slide, and distortion<br>[growl-bass](.claude/skills/growl-bass/SKILL.md) — FM synthesis growl with macro control and formant filters<br>[reese-bass](.claude/skills/reese-bass/SKILL.md) — detuned saw phasing with notch filter movement |
| **Synth & Ambient** | [supersaw-chords](.claude/skills/supersaw-chords/SKILL.md) — Wavetable unison patches with mono/stereo layering<br>[ethereal-pads](.claude/skills/ethereal-pads/SKILL.md) — split-voice chord layers with drone notes and noise<br>[ambient](.claude/skills/ambient/SKILL.md) — reverb-as-sound-design with granular textures<br>[synthwave](.claude/skills/synthwave/SKILL.md) — gated reverb, arps, retro bass and leads |
| **Production** | [mixing-guide](.claude/skills/mixing-guide/SKILL.md) — systematic mixing workflow with master chain<br>[track-arrangement](.claude/skills/track-arrangement/SKILL.md) — loop-to-full-track with genre-specific notes<br>[drum-swing](.claude/skills/drum-swing/SKILL.md) — MPC swing percentages, humanization, groove theory |

### Using Skills

Skills activate automatically based on what you ask. Examples:

- *"Make me a techno beat"* → triggers techno-drums
- *"Add an acid bassline"* → triggers acid-bass
- *"Let's mix this track"* → triggers mixing-guide
- *"Make some dreamy pads"* → triggers ethereal-pads

Skills can also be combined — ask for "techno drums and bass" and Claude will use both techno-drums and techno-bass skills together.

### Creating Your Own Skills

See the [Skill Authoring Guide](SKILL_AUTHORING_GUIDE.md) for best practices on creating new skills.

## Setup

### Prerequisites

- Ableton Live 11+ (any edition)
- Python 3.10+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

### 1. Clone the repo

```bash
git clone https://github.com/nicholasbien/ableton-mcp-pro.git
cd ableton-mcp-pro
```

### 2. Install the Remote Script in Ableton

Copy the Remote Script into Ableton's MIDI Remote Scripts folder:

**Mac:**
```bash
mkdir -p "/Applications/Ableton Live 12 Suite.app/Contents/App-Resources/MIDI Remote Scripts/AbletonMCP"
cp AbletonMCP_Remote_Script/__init__.py "/Applications/Ableton Live 12 Suite.app/Contents/App-Resources/MIDI Remote Scripts/AbletonMCP/__init__.py"
```

**Windows:**
```
Copy AbletonMCP_Remote_Script\__init__.py to:
C:\ProgramData\Ableton\Live 12 Suite\Resources\MIDI Remote Scripts\AbletonMCP\__init__.py
```

> Adjust the path for your Ableton version (Live 11, Live 12, Suite vs Standard, etc).

### 3. Enable in Ableton

1. Open Ableton Live
2. Go to **Preferences** > **Link, Tempo & MIDI**
3. Set a **Control Surface** slot to **AbletonMCP**
4. Leave Input and Output set to **None**

You should see "AbletonMCP: Listening for commands on port 9877" in the status bar.

### 4. Connect your AI assistant

#### Claude Code (CLI)

Add to your `.mcp.json` in the project root:

```json
{
  "mcpServers": {
    "AbletonMCP": {
      "command": "uv",
      "args": [
        "run",
        "--project", "/path/to/ableton-mcp-pro",
        "python",
        "/path/to/ableton-mcp-pro/MCP_Server/server.py"
      ]
    }
  }
}
```

#### Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "AbletonMCP": {
      "command": "/opt/homebrew/bin/uv",
      "args": [
        "run",
        "--project", "/path/to/ableton-mcp-pro",
        "python",
        "/path/to/ableton-mcp-pro/MCP_Server/server.py"
      ]
    }
  }
}
```

> Replace `/path/to/ableton-mcp-pro` with the actual path where you cloned the repo. If you don't have `uv`, you can use `pip install -e .` and replace the command with `python` and args with just the server path.

#### Cursor

Add an MCP server in **Settings > MCP** with the same command and args as above.

### 5. Try it

Open your AI assistant and try:
- "What tracks do I have?"
- "Create a MIDI track, load Analog on it, and program a bass line"
- "Set the tempo to 128 and add a compressor to the master"

## How It Works

```
AI Assistant --> MCP Server (Python) --> TCP socket (port 9877) --> Remote Script (inside Ableton)
```

1. You give a natural language instruction to your AI assistant
2. The assistant calls MCP tools like `create_clip`, `add_notes_to_clip`, `set_device_parameter`
3. The MCP server sends JSON commands over TCP to the Remote Script running inside Ableton
4. The Remote Script executes commands using Ableton's Live Object Model (LOM)

## Available Tools

### Read
`get_session_info`, `get_track_info`, `get_device_parameters`, `get_arrangement_info`, `get_arrangement_clips`, `get_full_arrangement`, `get_clip_notes`, `get_clip_envelope`, `get_browser_tree`, `get_browser_items_at_path`

### Modify
`create_midi_track`, `create_audio_track`, `create_clip`, `add_notes_to_clip`, `set_clip_name`, `set_clip_loop`, `delete_clip`, `duplicate_clip`, `delete_track`, `duplicate_track`, `set_track_name`, `set_track_volume`, `set_track_panning`, `set_track_mute`, `set_track_solo`, `set_track_arm`, `set_send_level`, `set_tempo`, `set_time_signature`, `set_metronome`, `fire_clip`, `stop_clip`, `fire_scene`, `create_scene`, `delete_scene`, `set_scene_name`, `start_playback`, `stop_playback`, `play_arrangement`, `load_instrument_or_effect`, `set_device_parameter`, `batch_set_device_parameters`, `delete_device`, `set_song_time`, `set_record_mode`, `set_arrangement_overdub`, `set_back_to_arranger`, `set_arrangement_loop`, `set_clip_envelope`, `clear_clip_envelope`, `undo`, `redo`

### Special
`record_arrangement` — Records session clips into the arrangement by firing scenes at timed intervals with bar-accurate transitions.

## Updating the Remote Script

When you modify `AbletonMCP_Remote_Script/__init__.py`:

```bash
cp AbletonMCP_Remote_Script/__init__.py "/Applications/Ableton Live 12 Suite.app/Contents/App-Resources/MIDI Remote Scripts/AbletonMCP/__init__.py"
rm -rf "/Applications/Ableton Live 12 Suite.app/Contents/App-Resources/MIDI Remote Scripts/AbletonMCP/__pycache__"
```

Then **fully restart Ableton** (toggling the Control Surface in preferences doesn't reliably reload the script).

## AI Melody Generation

`tools/midigenai_bridge.py` is a CLI that pipes Ableton clip notes through
[openmusenet2](https://github.com/nicholasbien/openmusenet2) (v2 model) to
generate melody continuations. The agent reads a clip with `get_clip_notes`,
shells out to the bridge, and writes the result back with
`add_notes_to_clip` — no MCP server changes needed. See
[tools/README.md](tools/README.md) for setup, dependencies, and usage.

## Known Limitations

- **Arrangement clips are read-only** — The LOM can't create/delete arrangement clips directly. Use `record_arrangement` to record from session, or record an empty scene to erase.
- **Audio clip loading** — `ClipSlot.create_clip()` only accepts a length (for MIDI clips), not file paths. Audio clips must be dragged manually from Ableton's browser.
- **Stale song reference** — First command after an Ableton restart may fail (retry works). The script auto-refreshes its internal reference.

## Development

See [DEVELOPMENT.md](DEVELOPMENT.md) for the full development guide — threading model, adding new commands, device parameters, automation, and recording architecture.

## License

MIT — see [LICENSE](LICENSE).

**Built with** [Model Context Protocol](https://github.com/modelcontextprotocol) and [Ableton Live](https://www.ableton.com).
