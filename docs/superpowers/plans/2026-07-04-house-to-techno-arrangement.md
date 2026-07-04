# House → Techno Arrangement Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a full Arrangement View (176 bars, House → Transition → Techno) in the currently-open Ableton Live set, using the `ableton` MCP tools, by re-sequencing existing Session View audio stems into new scenes and recording them into the Arrangement.

**Architecture:** (1) Clear existing Arrangement content. (2) Create 10 new Session scenes (indices 11–20), each populated by duplicating the right existing per-track stem into place and setting it to loop. (3) Fire `record_arrangement` once with all 10 sections in order to bake them into the Arrangement. (4) Place 7 named locators at the section-start beats. (5) Verify the result.

**Tech Stack:** `mcp__ableton__*` MCP tools only (Ableton Live 12 Remote Script, this repo's `MCP_Server/server.py`). No code changes in this plan — this is a content/DAW-state task, not a software change, so "tests" below are MCP verification calls, not a test suite.

## Global Constraints

- Tempo stays at 128 for the whole build (tempo ramp to 135 is drawn by hand by the user afterward — do not attempt to script it).
- Track indices used below are current as of 2026-07-04 (see spec `docs/superpowers/specs/2026-07-04-house-to-techno-arrangement-design.md`): KICK=11, CHH=1, RIDE=2, OHH=3, CLAP=5, SNARE AD H=6, SYNTH=8. Track 9 (SYNTH + SQUARE) is excluded per user decision.
- All positions are in beats (4 beats = 1 bar, 4/4 time).
- Every `duplicate_clip` call must use an explicit numeric `target_index` (never `-1`) so scenes land at the planned index.
- Every newly duplicated clip must be set to loop (`looping=true`, `loop_start=0`, `loop_end=<source clip length>`) so it fills the full section even when the section is longer than the source clip.

---

### Task 1: Clean slate — clear existing Arrangement content

**Files:** None (Ableton project state only).

**Interfaces:**
- Produces: an empty Arrangement (no clips on any track, no locators) that Task 3+ builds on.

- [ ] **Step 1: List current locators**

Call `mcp__ableton__get_locators`. Note every `time` returned.

- [ ] **Step 2: Delete every existing locator**

For each `time` from Step 1, call `mcp__ableton__delete_locator` with that `time`. Call `mcp__ableton__get_locators` again afterward — expect `{"locators": []}`.

- [ ] **Step 3: Delete existing arrangement clips per track**

For every track index 0–11, call `mcp__ableton__get_arrangement_clips` with that `track_index`. Group/return tracks (0, 4, 7, 10) will return an error (`"Main, Group and Return Tracks have no arrangement clips"`) — that's expected, skip them. For any track that returns `arrangement_clip_count > 0`, call `mcp__ableton__delete_arrangement_clip` with that `track_index` and `arrangement_clip_index: 0` repeatedly (indices shift down after each delete, so always delete index 0) until `arrangement_clip_count` is 0 again.

- [ ] **Step 4: Verify clean slate**

Call `mcp__ableton__get_full_arrangement`. Expect every non-group track's `clips` array to be empty and `get_locators` to return `[]`.

---

### Task 2: Create the 10 new scenes

**Files:** None.

**Interfaces:**
- Produces: scenes at indices 11–20, named, ready to receive duplicated clips in Task 3.

- [ ] **Step 1: Create 10 scenes**

Call `mcp__ableton__create_scene` with `index: -1` ten times in a row (sequentially, not in parallel — scene indices must land predictably). After all 10 calls, `get_session_info` should report scene creation succeeded (no direct scene-count field is guaranteed; proceed if no errors were returned).

- [ ] **Step 2: Name each new scene**

Call `mcp__ableton__set_scene_name` for indices 11–20 with these exact names, in order:

| scene_index | name |
|---|---|
| 11 | ARR Intro Kick |
| 12 | ARR Intro Full |
| 13 | ARR House Groove |
| 14 | ARR Transition Build |
| 15 | ARR Transition Full |
| 16 | ARR Techno Groove |
| 17 | ARR Techno Build |
| 18 | ARR Techno Drop |
| 19 | ARR Outro Full |
| 20 | ARR Outro Strip |

---

### Task 3: Populate the new scenes by duplicating existing stems

**Files:** None.

**Interfaces:**
- Consumes: scenes 11–20 from Task 2.
- Produces: each scene fully populated and looped, ready for `record_arrangement` in Task 4.

Perform every row below as: `mcp__ableton__duplicate_clip(track_index, clip_index, target_index)` **then immediately** `mcp__ableton__set_clip_loop(track_index, clip_index=target_index, loop_start=0, loop_end=<length>, looping=true)`. `<length>` is the source clip's native length (given in the table). Do these two calls back-to-back for every row before moving to the next row — do not batch all duplicates first and loop-settings after, since it's easy to lose track of which target index belongs to which length.

| Track (index) | Source clip_index | Source clip name | Length (beats) | Target scenes (clip_index) |
|---|---|---|---|---|
| KICK (11) | 5 | 3-Audio 4 | 16.008 | 11, 12, 13, 14, 15, 16, 17, 18, 19, 20 |
| CHH (1) | 3 | 02_H2T_intro_kick_hh (Freeze) | 32 | 12, 13 |
| CHH (1) | 9 | 08_H2T_outro (Freeze) | 56 | 19 |
| SYNTH (8) | 0 | MIDI Giorgio Lopez ... (Freeze) | 16 | 12 |
| SYNTH (8) | 4 | V3 Stabs Cm 132 (Freeze) | 32 | 13 |
| SYNTH (8) | 5 | 05 Acid pedal C (Freeze) | 4 | 16, 17, 18 |
| OHH (3) | 6 | MIDI Open hat 01 (Freeze) | 4 | 13 |
| SNARE AD H (6) | 2 | SNARE AD H 3 | 16 | 14, 17 |
| RIDE (2) | 5 | 04_H2T_transition (Freeze) | 64 | 15 |
| RIDE (2) | 6 | 05_H2T_techno_groove (Freeze) | 64 | 16, 18 |
| RIDE (2) | 7 | 06_H2T_techno_build (Freeze) | 64 | 17 |
| RIDE (2) | 9 | 08_H2T_outro (Freeze) | 56 | 19, 20 |
| CLAP (5) | 5 | 04_H2T_transition (Freeze) | 64 | 15 |
| CLAP (5) | 6 | 05_H2T_techno_groove (Freeze) | 64 | 16 |
| CLAP (5) | 8 | 07_H2T_techno_drop (Freeze) | 64 | 18 |
| CLAP (5) | 9 | 08_H2T_outro (Freeze) | 56 | 19 |

Note: KICK is duplicated into every target scene from the SAME source clip_index (5) each time — `duplicate_clip` does not consume the source, so repeating `duplicate_clip(11, 5, <target>)` for each of the 10 targets is correct and expected.

- [ ] **Step 1: Duplicate + loop every row in the table above, in the order listed**

- [ ] **Step 2: Spot-check one scene per section**

Call `mcp__ableton__get_track_info` for `track_index: 11` (KICK) and confirm `clip_slots[11]` through `clip_slots[20]` all show `has_clip: true`. Spot check `get_track_info` for `track_index: 8` (SYNTH) and confirm slots 12, 13, 16, 17, 18 show `has_clip: true`.

---

### Task 4: Record the sequence into the Arrangement

**Files:** None.

**Interfaces:**
- Consumes: scenes 11–20 populated by Task 3.
- Produces: a fully populated Arrangement, 176 bars / 704 beats long.

- [ ] **Step 1: Call `record_arrangement`**

```json
{
  "sections": [
    {"scene_index": 11, "bars": 8},
    {"scene_index": 12, "bars": 8},
    {"scene_index": 13, "bars": 16},
    {"scene_index": 14, "bars": 8},
    {"scene_index": 15, "bars": 8},
    {"scene_index": 16, "bars": 32},
    {"scene_index": 17, "bars": 16},
    {"scene_index": 18, "bars": 40},
    {"scene_index": 19, "bars": 20},
    {"scene_index": 20, "bars": 20}
  ],
  "start_time": 0
}
```

This call can take a while (it plays through all 176 bars in real time inside Live) — use the tool's own timeout handling, don't cancel early.

- [ ] **Step 2: Verify length**

Call `mcp__ableton__get_arrangement_info`. Expect `song_length` to be `704.0` (176 bars × 4 beats).

---

### Task 5: Place section locators

**Files:** None.

**Interfaces:**
- Consumes: the recorded Arrangement from Task 4 (beat positions below are fixed regardless of recording order).

- [ ] **Step 1: Add each locator, one call at a time (not in parallel — see `memory.md` for why)**

| time (beats) | name |
|---|---|
| 0 | House - Intro |
| 64 | House - Groove |
| 128 | Transition |
| 192 | Techno - Groove |
| 320 | Techno - Build |
| 384 | Techno - Drop |
| 544 | Outro |

Call `mcp__ableton__add_locator` once per row, waiting for each call to return before the next.

- [ ] **Step 2: Verify locators**

Call `mcp__ableton__get_locators`. Expect exactly the 7 entries above, sorted by time, with the names as given (not Live's default numeric names — if any name is wrong, re-check `memory.md`'s note about `current_song_time` lag before retrying).

---

### Task 6: Final verification

**Files:** None.

**Interfaces:** None (terminal task).

- [ ] **Step 1: Full arrangement check**

Call `mcp__ableton__get_full_arrangement`. For each non-group track, confirm there is at least one clip and that clip start/end times are consistent with the section table in the spec (e.g. KICK should have clips spanning continuously from 0 to 704).

- [ ] **Step 2: Report to user**

Summarize: total length (176 bars / 704 beats), the 7 locators placed, and a reminder that the user still needs to hand-draw the 128→135 tempo ramp on the Master track's "Song Tempo" automation lane starting around beat 128 (the Transition locator).
