"""
MIDI Gen AI Bridge: Ableton MCP clip notes -> AI MIDI generation -> notes back.

Wraps openmusenet2 (v2 model) but named generically so the backend can be
swapped later without churning callers.

Reads JSON config from stdin:
  {
    "notes": [{"pitch": 62, "start_time": 0.0, "duration": 0.5, "velocity": 100}, ...],
    "tempo_bpm": 80.0,
    "max_new_tokens": 256, "temperature": 1.0, "top_k": 50,
    "prompt_end_beat": 32.0,           # filter output to notes after this beat
    "pitch_range": [60, 96],           # optional pitch filter
    "checkpoint": "...", "tokenizer": "..."  # optional model overrides
  }

Writes JSON to stdout:
  {"prompt_tokens": int, "generated_tokens": int, "tempo_bpm": float,
   "notes": [{"pitch", "start_time", "duration", "velocity"}, ...]}

Run with the openmusenet2 venv:
  /Users/nicholasbien/openmusenet2/.venv/bin/python tools/midi_gen_ai_bridge.py < cfg.json
"""

import json
import sys
import tempfile
from pathlib import Path

OMN2_ROOT = Path("/Users/nicholasbien/openmusenet2")
DEFAULT_CKPT = OMN2_ROOT / "runs/pilot_lambda/ckpt_final.pt"
DEFAULT_TOKENIZER = OMN2_ROOT / "runs/pilot_lambda/tokenizer.json"
TPQ = 480

sys.path.insert(0, str(OMN2_ROOT))


def notes_to_score(notes, tempo_bpm):
    from symusic import Score, Track, Note, Tempo
    score = Score(TPQ)
    score.tempos = [Tempo(time=0, qpm=tempo_bpm)]

    by_program = {}
    for n in notes:
        prog = int(n.get("program", 0))
        by_program.setdefault(prog, []).append(n)

    for prog, ns in by_program.items():
        track = Track(program=prog, is_drum=False, name=f"prog{prog}")
        for n in ns:
            track.notes.append(Note(
                time=int(round(float(n["start_time"]) * TPQ)),
                duration=max(1, int(round(float(n["duration"]) * TPQ))),
                pitch=int(n["pitch"]),
                velocity=int(n["velocity"]),
            ))
        score.tracks.append(track)
    return score


def score_to_notes(score, prompt_end_beat=None, pitch_range=None):
    notes = []
    tpq = score.ticks_per_quarter
    for track in score.tracks:
        for n in track.notes:
            start_beat = float(n.start) / tpq
            dur_beat = float(n.duration) / tpq
            pitch = int(n.pitch)
            if prompt_end_beat is not None and start_beat < prompt_end_beat - 1e-6:
                continue
            if pitch_range is not None and not (pitch_range[0] <= pitch <= pitch_range[1]):
                continue
            notes.append({
                "pitch": pitch,
                "start_time": round(start_beat - (prompt_end_beat or 0), 4),
                "duration": round(dur_beat, 4),
                "velocity": int(n.velocity),
                "mute": False,
            })
    notes.sort(key=lambda x: (x["start_time"], x["pitch"]))
    return notes


def main():
    cfg = json.loads(sys.stdin.read())

    notes = cfg["notes"]
    tempo = float(cfg.get("tempo_bpm", 120.0))
    max_new_tokens = int(cfg.get("max_new_tokens", 256))
    temperature = float(cfg.get("temperature", 1.0))
    top_k = int(cfg.get("top_k", 50))
    prompt_end_beat = cfg.get("prompt_end_beat")
    if prompt_end_beat is not None:
        prompt_end_beat = float(prompt_end_beat)
    pitch_range = cfg.get("pitch_range")
    ckpt = cfg.get("checkpoint", str(DEFAULT_CKPT))
    tokenizer = cfg.get("tokenizer", str(DEFAULT_TOKENIZER))

    score = notes_to_score(notes, tempo)
    with tempfile.NamedTemporaryFile(suffix=".mid", delete=False) as f:
        in_path = f.name
    score.dump_midi(in_path)

    from v2.generate_v2 import V2Generator
    gen = V2Generator(checkpoint_path=ckpt, tokenizer_path=tokenizer)
    prompt_ids = gen.encode_midi_file(in_path)

    out_path = in_path.replace(".mid", "_out.mid")
    new_ids = gen.generate_to_midi(
        prompt_ids, out_path,
        tempo_bpm=tempo,
        max_new_tokens=max_new_tokens,
        temperature=temperature,
        top_k=top_k,
    )

    from symusic import Score
    out_score = Score(out_path)
    out_notes = score_to_notes(out_score, prompt_end_beat=prompt_end_beat, pitch_range=pitch_range)

    Path(in_path).unlink(missing_ok=True)
    Path(out_path).unlink(missing_ok=True)

    json.dump({
        "prompt_tokens": len(prompt_ids),
        "generated_tokens": len(new_ids),
        "tempo_bpm": tempo,
        "notes": out_notes,
    }, sys.stdout)


if __name__ == "__main__":
    main()
