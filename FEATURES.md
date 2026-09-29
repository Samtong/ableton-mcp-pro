# Tout ce que ce repo sait faire

Inventaire complet, du plus basique au plus obscur. Écrit pour être lu par un humain
qui veut savoir quoi demander à l'assistant. Les 69 outils MCP sont tous listés.

- **Remote Script** (`AbletonMCP_Remote_Script/__init__.py`) — tourne dans Live, écoute en TCP sur le port 9877.
- **Serveur MCP** (`MCP_Server/server.py`) — expose les 69 outils à l'assistant.

Tu peux aussi parler au Remote Script sans passer par MCP : envoie
`{"type": "<commande>", "params": {...}}` en JSON sur `localhost:9877`.

## Les conventions à connaître

| Sujet | Règle |
|---|---|
| Index de piste | `0`+ pistes normales, `-1` master, `-2` / `-3` return A / B |
| Valeurs de paramètres | Toujours normalisées `0.0`–`1.0`, quelle que soit l'échelle réelle |
| Volume ↔ dB | `dB = (position − 0.85) × 40` (0.85 = 0 dB, 1.0 = +6 dB). Pour un send : `dB = (position − 1.0) × 40`. Relis toujours `volume_db` après écriture |
| Positions | En temps (beats) : `4.0` = 1 mesure en 4/4 |
| Notes MIDI | pitch 0–127, vélocité 0–127. Live appelle le pitch 60 **C3** (donc C1=36, C2=48, C4=72) |
| Couleurs | Palette Live de 70 cases : `#RRGGBB` (Live prend la plus proche) ou `color_index` 0–69 |

---

## 1. Lire l'état du set

| Outil | Ce que ça donne |
|---|---|
| `get_session_info()` | Tempo, signature, nombre de pistes et de returns, master, tonalité/gamme du morceau |
| `get_track_info(track_index)` | Nom, volume, pan, mute/solo/arm, devices, tous les clip slots de la piste |
| `get_selected_context()` | **Ce que tu as sélectionné dans Live à l'instant** : piste, scène, clip slot surligné, clip ouvert dans le détail, device sélectionné, position de lecture. C'est ça qui permet de dire « cette piste », « ce clip », « ici » au lieu de donner des index |
| `get_track_routing(track_index)` | Routage entrée/sortie de la piste + toutes les options disponibles, par nom |
| `get_device_parameters(track_index, device_index)` | Tous les paramètres d'un device avec valeur courante, plage et nom affiché |
| `get_track_output_meter(track_index, duration_ms, interval_ms)` | Fait tourner le transport et renvoie le **pic** observé sur une fenêtre (défaut 2 s). Live expose du RMS post-fader, donc c'est bon pour **comparer des pistes entre elles**, pas comme référence dBFS absolue. Lance la lecture et soloe la piste avant |
| `get_browser_tree(category_type)` | Arborescence du navigateur Live : `all`, `instruments`, `sounds`, `drums`, `audio_effects`, `midi_effects` |
| `get_browser_items_at_path(path)` | Contenu d'un dossier du navigateur, avec les URI à charger |

## 2. Pistes

| Outil | Ce que ça fait |
|---|---|
| `create_midi_track(index=-1)` | Crée une piste MIDI (`-1` = à la fin) |
| `create_audio_track(index=-1)` | Crée une piste audio |
| `duplicate_track(track_index)` | Duplique la piste avec ses clips et ses devices |
| `delete_track(track_index)` | Supprime la piste |
| `set_track_name(track_index, name)` | Renomme |
| `set_track_color(track_index, color \| color_index)` | Colore la piste |
| `set_track_volume` / `set_track_panning` | Volume et pan, en 0.0–1.0 (marche aussi sur le master avec `-1`) |
| `set_track_mute` / `set_track_solo` / `set_track_arm` | Mute, solo, armement |
| `set_send_level(track_index, send_index, value)` | Niveau d'un send vers un return |
| `set_track_input_routing(track_index, routing_type, routing_channel)` | Choisit l'entrée de la piste **par nom affiché**. Sert surtout à enregistrer ce que joue vraiment un effet MIDI (séquenceur, arpégiateur) : on route la sortie de cette piste vers une autre et on capture le Post FX |

## 3. Clips en vue Session

| Outil | Ce que ça fait |
|---|---|
| `create_clip(track_index, clip_index, length=4.0)` | Clip MIDI vide dans un slot |
| `create_audio_clip(track_index, clip_index, file_path)` | Clip audio depuis un fichier dans un slot |
| `add_notes_to_clip(track_index, clip_index, notes)` | Ajoute des notes. Accepte une liste de dicts **ou du CSV** : `pitch,start,dur,vel[,mute]`, une note par ligne. Tout est validé avant écriture — un lot invalide n'écrit rien du tout |
| `get_clip_notes(track_index, clip_index, format)` | Relit les notes. `format="csv"` = beaucoup moins de tokens sur un clip dense |
| `set_clip_name` / `set_clip_color` | Renomme / colore un clip |
| `set_clip_loop(..., loop_start, loop_end, looping)` | Réglages de boucle, chaque paramètre est optionnel |
| `duplicate_clip(track_index, clip_index, target_index=-1)` | Duplique dans un autre slot de la même piste |
| `delete_clip(track_index, clip_index)` | Supprime le clip |

**Le truc à connaître : `set_clip_color(key=...)`.** Passe une tonalité — `"F minor"`,
`"F#m"`, `"Bb"`, `"Ebmaj"` ou un code Camelot comme `"8A"` — et le clip prend une des 12
couleurs vives de la palette, choisie par numéro Camelot : relatif majeur/mineur partagent
la couleur et les tonalités à la quinte sont voisines en teinte. Les clips compatibles se
ressemblent à l'œil. Le résultat renvoie aussi le code Camelot.

## 4. Scènes

`create_scene(index=-1)`, `delete_scene(scene_index)`, `set_scene_name(scene_index, name)`,
`fire_scene(scene_index)` — lance tous les clips d'une scène d'un coup.

## 5. Vue Arrangement

**Édition directe** (nécessite Live 12, voir la section Limites) :

| Outil | Ce que ça fait |
|---|---|
| `create_arrangement_midi_clip(track_index, time, length, notes?)` | Pose un clip MIDI à une position en beats, avec ses notes en un seul appel |
| `create_arrangement_audio_clip(track_index, file_path, time, length?)` | Pose un échantillon à une position, par chemin de fichier |
| `get_arrangement_clips(track_index)` | Liste les clips d'une piste : `start_time`, `length`, et le `file_path` de la source pour l'audio — pratique pour recopier un sample déjà présent |
| `get_arrangement_clip_notes(track_index, arrangement_clip_index, format)` | Relit les notes d'un clip d'arrangement (json ou csv) |
| `delete_arrangement_clip(track_index, arrangement_clip_index)` | Supprime un clip par index |
| `get_full_arrangement()` | Vue complète : toutes les pistes avec leurs clips, tempo, signature, longueur, liste des scènes |

Un nouveau clip **remplace** ce qui se trouve dessous, comme un collage dans Live.

**Transport et repères** :

| Outil | Ce que ça fait |
|---|---|
| `get_arrangement_info()` | Position, mode enregistrement, boucle, état du transport, longueur du morceau |
| `play_arrangement(time=0.0)` | Bascule en vue Arrangement, arrête les clips Session, lit depuis une position |
| `start_playback()` / `stop_playback()` | Play / stop |
| `set_song_time(time)` | Déplace la tête de lecture. **Vérifie ensuite avec `get_arrangement_info`** : Live applique ça en asynchrone |
| `set_record_mode(on)` | Arme l'enregistrement d'arrangement |
| `set_arrangement_overdub(on)` | Superpose au lieu de remplacer |
| `set_back_to_arranger()` | Rend la main à l'arrangement après un passage en Session |
| `set_arrangement_loop(on, start, length)` | Boucle d'arrangement |
| `get_locators()` | Tous les repères (cue points), triés par position |
| `add_locator(time, name)` | Pose un repère — « Intro », « Drop », « Break » |
| `delete_locator(time)` | Supprime le repère le plus proche d'une position |

**`record_arrangement(sections, start_time=0.0)`** — enregistre des scènes Session dans
l'arrangement en les déclenchant à la mesure près. `sections` = `[{"scene_index": 0,
"bars": 8}, {"scene_index": 1, "bars": 16}]`. Tout tourne dans Live pour la précision :
placement, armement, transitions quantifiées à la mesure, désarmement des pistes,
restauration de la quantification d'origine. `start_time` sert à rallonger un morceau
existant sans écraser le début.

## 6. Devices et sons

| Outil | Ce que ça fait |
|---|---|
| `load_instrument_or_effect(track_index, uri, clip_index=-1)` | Charge un instrument ou un effet par URI du navigateur (`-1` = master) |
| `load_drum_kit(track_index, rack_uri, kit_path)` | Charge un Drum Rack puis y charge un kit |
| `set_device_parameter(track_index, device_index, parameter_index, value)` | Un paramètre, en 0.0–1.0 |
| `batch_set_device_parameters(..., parameter_indices, values)` | Plusieurs paramètres en un seul aller-retour — c'est ça qu'il faut utiliser pour construire un patch |
| `delete_device(track_index, device_index)` | Retire un device |

## 7. Automation dans les clips

`set_clip_envelope(track, clip, device, parameter, points)` avec `points` =
`[{"time": 0.0, "value": 0.2}, ...]` (valeurs normalisées),
`get_clip_envelope(...)` pour relire, `clear_clip_envelope(...)` pour effacer.
L'automation vit dans les clips Session ; elle est gravée dans l'arrangement au moment
de `record_arrangement`.

## 8. Morceau et transport global

`set_tempo(tempo)`, `set_time_signature(num, denom)`, `set_metronome(on)`,
`set_song_scale(root_note?, scale_name?, scale_mode?)` — tonalité et gamme du morceau
(Live 12). Attention : Live accepte n'importe quelle chaîne comme nom de gamme sans la
vérifier, une faute de frappe passe sans erreur.

`undo()` / `redo()` — l'historique d'annulation de Live.

---

## Les skills de production (21)

Elles se déclenchent toutes seules selon ta demande, en français comme en anglais.

**Batterie / groove** : `techno-drums`, `hardgroove-drums`, `house-drums`, `ukg-drums`,
`drum-swing` (swing MPC, humanisation, feel hip-hop).

**Basses** : `acid-bass` (303), `techno-bass`, `hardgroove-bass`, `trance-bass`,
`reese-bass` (D&B, saws désaccordés), `growl-bass` (FM/dubstep), `speed-garage`.

**Accords, nappes, mélodies** : `house-chords`, `supersaw-chords`, `ethereal-pads`,
`trance-melodies`, `ambient`, `synthwave`.

**Production** : `track-arrangement` (boucle de 8 mesures → morceau complet),
`mixing-guide` (mixage et mastering, chaîne master), `mixing-guide-mindpath` (mixage
3 bandes autonome avec critères mesurables rouge/vert, ne pose aucune question).

Pour en écrire une : [SKILL_AUTHORING_GUIDE.md](SKILL_AUTHORING_GUIDE.md).

## Les scripts annexes

- `.claude/skills/mixing-guide-mindpath/scripts/analyze_audio.py` — analyse un rendu audio (bandes, crête, dynamique).
- `.claude/skills/mixing-guide-mindpath/scripts/mix_tests.py` — valide un rendu master contre des seuils, en rouge/vert.
- `.claude/skills/mixing-guide-mindpath/scripts/make_profile.py`, `make_rumble.py` — profils de référence et rumble de kick.
- `tools/midigenai_bridge.py` — passe un clip dans le modèle MidiGenAI pour générer une suite de mélodie, puis réécrit le résultat avec `add_notes_to_clip`. Pas besoin de toucher au serveur MCP. Voir [tools/README.md](tools/README.md).

## Les tests

```bash
.venv/bin/python -m unittest discover -s tests -v
```

95 tests, sans Live : `tests/remote_script_harness.py` charge le Remote Script avec de
faux objets Live. Toute nouvelle commande doit être testée **à travers
`_process_command`**, sinon une commande absente des listes de dispatch passe quand même.

---

## Ce que ça ne sait PAS faire

- **Éditer l'arrangement sous Live 11** — `create_arrangement_*` et `delete_arrangement_clip` ont besoin de Live 12. Sous Live 11, il reste `record_arrangement`.
- **Sur Live 12.0.x** — pas de `Track.create_midi_clip` (arrivé en 12.1.10). Le clip passe par un slot Session temporaire puis `duplicate_clip_to_arrangement` : le résultat est identique, mais un appel laisse plusieurs étapes d'annulation.
- **Automation dans l'arrangement** — on ne peut automatiser que dans les clips Session ; ça se grave dans l'arrangement à l'enregistrement.
- **Créer des Racks multi-chaînes** — pas d'Instrument Rack / Audio Effect Rack avec chaînes parallèles Dry/Wet. C'est la limite qui bloque le plus de skills (growl-bass, reese-bass, supersaw-chords, synthwave).
- **Renommer un repère** — `CuePoint.name` est en lecture seule dans cette version.
- **Routage de sortie** — seule l'entrée se règle par l'API.
- **Clips .alc du navigateur** — `load_item()` ne charge que la chaîne de devices, pas l'audio ; glisse-les à la main.
- **Capture MIDI, groove pool, crossfader** — pas encore exposés.

Détails et contournements : [NEXT_STEPS.md](NEXT_STEPS.md) et [memory.md](memory.md)
(les pièges appris à la dure — à lire avant de débugger quoi que ce soit).
