# tools/

Helper scripts that compose with the Ableton MCP server but run as their own
processes. Kept here (rather than inside `MCP_Server/`) so they're driven via
shell from the agent (or by you) without touching the MCP server.

## midigenai_bridge.py — AI MIDI continuation

CLI that turns a list of MIDI notes into an AI-generated continuation. Wraps
[openmusenet2](https://github.com/nicholasbien/openmusenet2) (v2 model). The
filename is intentionally backend-agnostic so we can swap models later without
churning callers.

### What it does

```
JSON notes (stdin)
    ↓
build a temporary .mid file
    ↓
encode with the v2 MidiTok tokenizer
    ↓
sample N tokens from the v2 transformer (Lambda-trained 25M checkpoint)
    ↓
decode back to MIDI, read notes, drop everything ≤ prompt_end_beat
    ↓
JSON notes (stdout)
```

### Dependencies

This bridge runs in **openmusenet2's venv**, not the MCP server's. That keeps
the MCP server lean (no torch/miditok/symusic in its env).

You need:

1. The **openmusenet2 repo** cloned next to this one (or anywhere — the path
   is hard-coded in the bridge; edit if yours differs):
   - default: `/Users/nicholasbien/openmusenet2/`
2. **openmusenet2's venv** with `torch`, `miditok`, `symusic` installed:
   - default: `/Users/nicholasbien/openmusenet2/.venv/`
3. **A v2 checkpoint + tokenizer** at:
   - `runs/pilot_lambda/ckpt_final.pt`
   - `runs/pilot_lambda/tokenizer.json`

   These are produced by openmusenet2's training pipeline (see `v2/train_v2.py`
   and `setup_lambda.sh`). The pilot Lambda checkpoint (~97 MB, 25M params)
   loads in <2s on CPU and generates ~70 notes/s.

   Override the paths via the `checkpoint` / `tokenizer` keys in the JSON
   payload if you have a different model.

### Usage

Build a JSON config, pipe it to the bridge using openmusenet2's venv:

```bash
echo '{
  "notes": [
    {"pitch": 62, "start_time": 0.0, "duration": 0.5, "velocity": 100},
    {"pitch": 66, "start_time": 0.5, "duration": 0.5, "velocity": 100},
    {"pitch": 69, "start_time": 1.0, "duration": 0.5, "velocity": 100}
  ],
  "tempo_bpm": 80,
  "max_new_tokens": 256,
  "temperature": 1.0,
  "top_k": 50,
  "prompt_end_beat": 4.0,
  "pitch_range": [60, 92]
}' | /Users/nicholasbien/openmusenet2/.venv/bin/python tools/midigenai_bridge.py
```

Returns:

```json
{
  "prompt_tokens": 33,
  "generated_tokens": 256,
  "tempo_bpm": 80,
  "notes": [{"pitch": 78, "start_time": 0.0, "duration": 0.5, "velocity": 95, "mute": false}, ...]
}
```

Note start times are returned **relative to `prompt_end_beat`**, so they're
ready to drop into a fresh clip starting at beat 0.

### Knobs

| key | meaning |
|---|---|
| `notes` | seed notes — Ableton MCP format (`pitch`/`start_time`/`duration`/`velocity`) |
| `tempo_bpm` | tempo of seed *and* output (the model is tempo-agnostic; this is just decoding) |
| `max_new_tokens` | how much continuation to sample. ~4 tokens/note → 256 ≈ 60 notes |
| `temperature` | 0.5–1.5. Lower sticks closer to the prompt; higher diverges more |
| `top_k` | nucleus sampling K |
| `prompt_end_beat` | drop output notes that start before this beat (= filter out the prompt itself) |
| `pitch_range` | optional `[min, max]` MIDI pitch filter — useful when you only want, say, the lead range |
| `checkpoint`, `tokenizer` | optional model overrides |

### Wiring it into the Ableton workflow

The agent typically:

1. `mcp__AbletonMCP__get_clip_notes` → pull a clip's notes as the seed
2. Build a JSON payload with those notes + tempo + knobs
3. Run `tools/midigenai_bridge.py` via `Bash`, capture stdout
4. (optional) post-filter: snap to scale, clip durations, drop anything outside the song length
5. `mcp__AbletonMCP__create_clip` + `mcp__AbletonMCP__add_notes_to_clip` on a target track to drop the result

We deliberately did **not** add MCP tool wrappers around this. The bridge is a
plain CLI; the agent drives it via shell. Reasons:

- No MCP server restart needed when the bridge changes
- The bridge can be used standalone outside the agent (`echo … | python …`)
- The dependency on openmusenet2's venv stays out of the MCP server's env

### Performance

Cold call ≈ 2s (model load + ~250 tokens). If you start hammering it, the
~2s/call gets old fast. Cleanest fix is a small local Flask server in the
openmusenet2 venv that loads the model once and exposes `/generate` —
mirroring what `web_server_modal.py` does for Modal. Defer until needed.
