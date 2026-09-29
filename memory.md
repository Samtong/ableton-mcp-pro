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

## ⚠️ NEVER drive arrangement RECORDING (Resampling → MIX_TEST) over MCP for the mixing render loop — it froze the transport AND destructively truncated the arrangement

Learned the very hard way in a `mixing-guide-mindpath` session (2026-07-06). The
skill's Red/Green step ("record the master to a MIX_TEST track set to input
Resampling") driven over MCP went catastrophic:

- After a few `set_record_mode` / `play_arrangement` / `stop_playback` /
  `delete_arrangement_clip` cycles, **Live's transport froze** (playhead stopped
  advancing; `get_arrangement_info` said `is_playing: true` but no audio
  rendered) and the recorded clips came out **silent (−240 dBFS)** or truncated
  to <1 s despite 45 s of wall-clock playback. An engine restart / long idle did
  NOT recover it.
- Far worse: the record/delete cycles **destructively cut the ENTIRE arrangement
  at a fixed beat (~260) across ALL tracks** — the whole techno drop
  (beats 304→432) was deleted on kick, sub, clap, hats and synth. So
  `delete_arrangement_clip` (and/or arrangement-record punch-in) behaves like a
  global *delete-time*, not a local clip delete. Only recovered because the user
  had a pre-session `.als` backup.

**Rules — do not repeat:**
1. For the Red/Green loop, **use manual export from the start** (ask the user:
   File → Export Audio, Rendered Track = Master, **Normalize OFF**, give you the
   WAV path). Do **not** automate Resampling recording over MCP. This is the
   skill's "Plan B" — treat it as Plan A.
2. **Never** run rapid `record_mode`/`play`/`stop`/`delete_arrangement_clip`
   cycles on a real project. There is no safe MCP "move arrangement clip" tool
   either — clip timing nudges are the user's job (by ear).
3. Restarting Ableton **clears undo history** → you cannot undo the truncation
   afterwards. Recovery = the user's `.als` backups (project root + `Backup/`).
   Find an intact one by `gzip`-decompressing the `.als` and regexing
   `CurrentStart`/`CurrentEnd` values to see how far the arrangement extends.

## Tempo automation makes transport position + metering unreadable over MCP

On a set with tempo automation (e.g. 128→135 BPM), during playback:
- `get_arrangement_info.current_song_time` returns **garbage/near-frozen** beat
  values (jumps around, doesn't advance linearly).
- `set_song_time` / `play_arrangement` **return-strings are wrong** (e.g. asked
  305, echoed "403.4") — the actual set may still be correct; **confirm with a
  separate `get_arrangement_info`** (same async gotcha as `current_song_time`
  above).
- `get_track_output_meter` returns **−120 dB constantly** — NOT a reliable
  "is audio playing" indicator.

Ground truth for "did audio actually render" = **the exported/recorded WAV on
disk** (analyze with soundfile), nothing else.

## MCP parameter mappings for mixing (verified this session)

- **Group / Return / Main tracks**: `get_track_info` and `get_arrangement_clips`
  **error** ("... have no Arm state / arrangement clips"). That's how you detect
  a group. You can still read/write their **devices** via
  `get_device_parameters(track, device_index)` (e.g. Utility+Bass Mono on a LOW
  group works fine).
- **`set_track_panning` expects 0.0–1.0** (0.5 = centre), NOT −1..1 — but
  `get_track_info.panning` **reads back −1..1** (0 = centre). Set `0.575` → reads
  `+0.15`. (Sending `-0.15` errors "Panning must be between 0.0 and 1.0".)
- **EQ Eight** per band: `N Filter On A` / `N Filter Type A` / `N Frequency A` /
  `N Gain A` / `N Resonance A`. Filter Type is quantised 0–7:
  **0=48dB low-cut, 1=12dB low-cut, 2=low-shelf, 3=bell, 4=notch, 5=high-shelf,
  6=12dB high-cut, 7=48dB high-cut.** Normalised `k/7` tends to **floor**
  (0.1428→value 0); use `(k+0.5)/7` to land value `k` reliably.
- **EQ Eight Frequency** is a raw 0–1 param (no Hz readback). Log map:
  `normalised ≈ ln(Hz/10) / ln(2205)` (~10 Hz–22 kHz). 100 Hz≈0.30, 300 Hz≈0.44,
  500 Hz≈0.51, 2 kHz≈0.69, 7 kHz≈0.85, 27 Hz≈0.13.
- **Glue Compressor**: Ratio stepped (0=2:1, 1=4:1, 2=10:1). Attack/Release
  stepped 0–6 (Attack value 6 = 30 ms; Release value 6 = Auto).
- **Limiter**: Ceiling is a *sample* ceiling — inter-sample **true-peak
  overshoots it by ~0.2–0.3 dB**, so set ceiling **−1.5** to keep true-peak
  ≤ −1.0 dBTP. Integrated LUFS tracks the Limiter input **Gain ~1:1** (peaks
  barely move LUFS) → `new_gain = gain + (target_LUFS − measured_LUFS)`.
- **Loading a device appends to the end** of the chain. Master often already has
  `Project Timer` (0) + `Monitoring Rack` (1); a LOW/BASS group often has a
  `Monitoring Rack` (0). So your loaded device lands at index 2+ / 1+. Re-read
  the chain; the `set_device_parameter` return echoes the resolved param name —
  use it to confirm you hit the intended device/band.

## Mixing lessons (mixing-guide-mindpath)

- **Macro-dynamic test** needs the export window to include a **loudness
  transition** (the entry into the drop), or a steady loop fails (<1.5 dB). But
  don't drag in too much sparse intro — it dilutes the octave spectrum. Pick the
  smallest window that has both full density AND one transition.
- **Shared-track EQ conflicts are unsolvable by EQ.** If two sounds on the same
  track need opposite treatment in the same band (here: a house lead too full at
  500 Hz vs a techno acid too scooped at 500 Hz), no master/track EQ satisfies
  both. Fix = **routing**: split them onto separate tracks (user does the
  arrangement split; then EQ each independently). This was the whole unlock of
  the mix.
- **Simulate the Limiter offline** (numpy: apply gain, clip to ceiling, re-measure
  LUFS/true-peak with pyloudnorm) on the last export before asking for a
  re-export — predictions are close enough to save a manual-export round-trip.
- True-peak ≤ −1 dBTP wants ceiling −1.5 (see Limiter note). LUFS premaster
  target −14..−10; leave it conservative (~−13) for a real mastering pass.

## Ne jamais croire un message d'erreur de version sans l'avoir vérifié sur ce build

`create_arrangement_midi_clip` échouait avec « Live version does not support
Track.create_midi_clip; need Live 11+ ». Le message était faux sur les deux points :
la méthode n'existe **pas** avant Live **12.1.10** (notes de version Live 12), et ce
build est **12.0.15**. La page LOM de Cycling '74 liste les méthodes du Live le plus
récent sans dire depuis quand elles existent — elle ne prouve donc rien sur ce build.

Trois réflexes, dans cet ordre :

1. **La version du build** :
   `defaults read "/Applications/Ableton Live 12 Suite.app/Contents/Info.plist" CFBundleShortVersionString`
2. **Ce que ce binaire expose vraiment**, sans redémarrer Live ni écrire de device M4L :
   `strings -n 6 "/Applications/Ableton Live 12 Suite.app/Contents/MacOS/Live"` puis
   chercher le nom de la méthode — les docstrings Python sont dans le binaire, groupées
   par classe (les méthodes de `Track` sont à côté de `delete_clip`, `duplicate_clip_slot`).
   C'est comme ça qu'on a établi que `create_audio_clip`, `delete_clip` et
   `duplicate_clip_to_arrangement` sont là en 12.0.15, mais pas `create_midi_clip`.
3. **Depuis quelle version** : les notes de version d'Ableton
   (ableton.com/en/release-notes/live-12/ et live-12-beta), pas la doc LOM.
   Attention aux fausses pistes : l'entrée « create_audio_clip / create_midi_clip » de
   12.2 concerne `TakeLane`, pas `Track`, et un fil de forum qui parle de « 12.0.5 »
   parlait de `ClipSlot.create_audio_clip` (Session), pas de la version Arrangement.

Corollaire : un `hasattr(...)` suivi d'un `raise` est un **constat**, jamais une preuve
de la version requise. Quand une méthode manque, chercher le chemin de repli qui existe
sur ce build (ici : clip Session temporaire + `duplicate_clip_to_arrangement`) plutôt que
de renvoyer « mets à jour Live ».

## Avant Live 12.2, `Track.create_midi_clip` / `create_audio_clip` ne renvoient rien

Le retour du clip créé n'est arrivé qu'en 12.2b13. Sur les versions antérieures l'appel
renvoie `None` : les notes n'étaient donc jamais écrites, en silence, même sur les builds
où la méthode existe (12.1.10 → 12.1.x). Ne pas se fier à la valeur de retour — retrouver
le clip dans `track.arrangement_clips` par sa position de départ (`_arrangement_clip_at`).

## La doc du repo dérive et finit par mentir

CLAUDE.md, README.md et NEXT_STEPS.md affirmaient « Arrangement is read-only » alors que
trois outils d'écriture d'arrangement existaient et étaient documentés ailleurs dans le
même README. Quand une capacité change, corriger **tous** les fichiers d'un coup :
`CLAUDE.md`, `README.md` (features + Known Limitations + prérequis), `NEXT_STEPS.md`,
`DEVELOPMENT.md`, les docstrings de `MCP_Server/server.py` et `FEATURES.md`.
Un `grep -rn` sur la formule périmée avant de clore, ça évite d'en oublier.
