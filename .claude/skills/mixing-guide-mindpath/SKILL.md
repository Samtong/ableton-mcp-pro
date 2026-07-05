---
name: mixing-guide-mindpath
description: Fully autonomous 3-band mixing workflow for electronic music (house, techno, bass music) in Ableton Live via AbletonMCP, with a measurable Red/Green Definition of Done. Use this skill whenever the user asks to mix a track, balance levels, clean the low end, set up a master chain, do gain staging, or says anything like "mixe mon son", "fais le mixage", "équilibre les pistes", "prépare pour le master" — even without any brief or details. The skill discovers everything itself (BPM, kick key, track roles, genre) by reading the session AND analyzing the audio with scripts/analyze_audio.py, then validates the master render against scripts/mix_tests.py until GREEN. Never ask the user for a brief, references, or aesthetic opinions.
---

# Mixing Guide Mindpath — Mixage 3 bandes autonome + TDD Red/Green (Ableton + MCP)

## Principe

Tu mixes **seul, de bout en bout, sans brief**, et le mix n'est **fini que quand la suite de tests passe au vert**. Tout est découvrable :
- **Session** via MCP : BPM, pistes, devices, volumes, pans, clips.
- **Audio par piste** via `scripts/analyze_audio.py` : chaque clip a un `file_path` (via `get_arrangement_clips`). Tu l'analyses pour obtenir fondamentale, niveaux, spectre, corrélation stéréo. C'est ainsi que tu "entends" chaque élément.
- **Rendu du master** via `scripts/mix_tests.py` : les métriques que les ingés lisent sur leurs meters (LUFS ITU-R BS.1770, true peak, PLR, corrélation, spectre vs bruit rose), calculées par script sur un enregistrement réel du climax. C'est ta **Definition of Done**.
- **Décisions** : ce fichier contient tous les défauts. Aucune question esthétique, jamais. Interactions autorisées : (a) le GO après le diagnostic Phase 0, (b) le setup manuel unique de la piste MIX_TEST (Phase 5.5), (c) signaler un blocage factuel.

## Contraintes absolues

1. **Devices Ableton natifs uniquement** : EQ Eight, Utility, Saturator, Glue Compressor, Compressor, Limiter, Drum Buss. Jamais de VST tiers (paramètres illisibles via le LOM).
2. **Sous-corriger** : moves EQ ≤ 3 dB, GR master ≤ 2 dB (glue) / ≤ 3 dB (limiter). En cas de doute, le move le plus doux.
3. **Réversible et documenté** : sauvegarde/duplication du projet demandée avant de commencer ; chaque modification va dans `MIX_REPORT.md` ; `undo` disponible.
4. **Ne jamais** : modifier les clips, toucher aux devices existants sans le documenter, panner pour résoudre un conflit fréquentiel, pousser un EQ pour "rentrer dans une courbe".
5. **Vérifier par la mesure** : chaque écriture de paramètre est relue (`get_device_parameters`, qui renvoie la valeur réelle) ; le rendu global est validé par la boucle Red/Green (Phase 5.5). `mix_tests.py` renvoie **exit 0 = GREEN**, **1 = RED (vrais défauts de mix)**, **2 = rendu invalide (corriger la CAPTURE, pas le mix)**. Les moves restent conservateurs : le vert s'atteint par petites touches.

## Ordre général (ne jamais dévier)

```
Phase 0 — Auto-découverte & diagnostic (lecture + analyse audio, zéro modif) → GO utilisateur
Phase 1 — Gain staging "From Scratch"
Phase 2 — LOW END (la fondation)
Phase 3 — HIGH END (l'énergie)
Phase 4 — MIDS (l'identité)
Phase 5 — Master léger (glue + limiteur)
Phase 5.5 — Boucle Red/Green (tests mesurés sur le rendu du master)
Phase 6 — MIX_REPORT.md
```

La **Couche MCP** en fin de fichier donne la traduction dB/Hz/ratio → normalisé 0.0–1.0 (obligatoire pour piloter les devices) — s'y référer à chaque écriture de paramètre.

---

## Phase 0 — Auto-découverte

### 0.1 Lecture session
`get_session_info`, puis `get_track_info` sur toutes les pistes (master `-1`, returns `-2`/`-3` inclus), puis `get_arrangement_clips` par piste pour récupérer les `file_path` audio.

### 0.2 Analyse audio
Dépendances (une fois) : `pip install numpy soundfile`. Puis pour chaque fichier audio unique :
```
python scripts/analyze_audio.py <file_path> [--kick]
```
Retour JSON : peak dBFS, RMS dBFS, crest, énergie par bande (sub <100 / low-mids 100–300 / high-mids 300–6k / highs >6k, %), corrélation stéréo <100 Hz, mono/stéréo, et avec `--kick` la fondamentale + note.

### 0.3 Classification automatique (aucune question)
- **Kick** : nom contient kick/bd OU sub dominant + transient fort + pattern 4/4.
- **Sub/Rumble** : énergie <100 Hz > 60 %, pas de transient de kick.
- **LOW END** = kick + sub/rumble + low toms. **HIGH END** = >50 % d'énergie >6 kHz. **MIDS** = le reste.
- **Lead** : la piste mid mélodique la plus présente (durée dans l'arrangement × RMS) ; égalité → la plus riche en 300 Hz–6 kHz. Décision justifiée dans le diagnostic.
- **Genre** : BPM 120–126 + swing/open hats → house ; 128–140 droit → techno ; entre les deux/évolutif → house→techno (défauts techno bass-heavy sur le low end, mids plus ouverts).

### 0.4 Défauts de direction (non négociables sans instruction contraire)
Kick in-between · high end resserré · courbe master bass-heavy · sidechain discret · lead mono-compatible et devant.

### 0.5 Diagnostic écrit → GO
Table des pistes (bande, rôle, peak/RMS, % spectral), fondamentale du kick (⚠ si hors 41–59 Hz), problèmes (MIDI kick/sub non bounced, absence de groupes, hors-phase <100 Hz, éléments <100 Hz hors low end), et le plan. Attendre le GO.

## Phase 1 — Gain staging "From Scratch"

Cibles (le kick est la référence absolue) :

| Élément | Niveau |
|---|---|
| Kick | **-6 dB** |
| Sub / Rumble | **-9 à -12 dB** (3–6 dB sous le kick ; house → 3–4, techno → 4–6) |
| Lead | **-12 dB** |
| Hat principal | **-12 dB** |
| Éléments secondaires | **-16 à -24 dB** (hiérarchisés par rôle) |

Ce sont des **niveaux résultants**, pas des positions de fader : pars du RMS mesuré en 0.2 et calcule le gain à appliquer. Pour un gain **exact** en dB, insère un **Utility** et règle son **Gain** (dB linéaire → formule exacte, voir Couche MCP) plutôt que de viser sur le fader mixer (courbe non-linéaire). Pans à 0 partout à ce stade.

## Phase 2 — LOW END

1. **Mono <100 Hz (obligatoire)** : Utility en fin de chaîne sur kick et sub (ou le groupe Low End), Bass Mono ON à 100 Hz. Croisé avec la corrélation de 0.2 — source déjà hors-phase <100 Hz → signalée au rapport.
2. **Cleaning global** : EQ Eight HPF sur toute piste hors low end — synths/leads 100–150, hats/cymbales 200–400, SFX/voix 120–200 Hz (coupe juste sous le contenu utile mesuré), pente 12 dB/oct (24 si beaucoup de parasites).
3. **Anti-boomy** : kick >35 % d'énergie en 100–400 Hz → EQ type Pultec : bell large +1.5 dB sur la fondamentale mesurée, bell moyen -2.5 dB sur le pic 100–400 détecté.
4. **Clé du kick** : fondamentale hors 41–59 Hz → ⚠ signalée, pas de repitch (production, pas mix).
5. **Glue optionnelle** Low End : Saturator Soft Sine, Drive ≤ 3 dB, output compensé pour RMS constant.
6. **Trou dans le low end (kick seul, pas de sub soutenu)** — problème de **production**, pas de mix, mais fréquent et bloquant pour l'octave 63 Hz de `mix_tests.py`. Remède zéro-synthèse : `scripts/make_rumble.py`.
   - Commande type (un rumble par tempo/kick de la track — house et techno ont souvent des kicks + tempos différents) :
     `python scripts/make_rumble.py <kick.wav> -o rumble.wav --bpm <bpm> --loop-beats 16 --sustain --gain-db -10`
   - Le script : extrait le sub du kick, **détecte auto le point de décroissance du kick** et remplit **le silence** entre les kicks (pas de superposition = pas d'annulation de phase) ; **`--sustain`** = sub continu (choisit auto le grain au pitch le plus stable → évite le wobble/"fiou" des kicks à longue descente de pitch) ; sortie mono, fondamentale = celle du kick (vérifiée dans le JSON), niveau posé par `--gain-db` (~-10 dBFS, la balance fine reste le fader).
   - `--loop-beats N` sort **un seul fichier loop** (tail tuilée à chaque beat) à poser back-to-back via `create_arrangement_audio_clip` sur la piste SUB, aligné au 4-on-floor (les positions kick = beats entiers ; sauter les breaks). Régler SUB **3–6 dB sous le kick**, vérifier à l'Occular Scope /LOW que la transition kick→rumble→kick est **continue et en phase** (cible du cours).
   - **Ghost kicks masqués par le sub** → sidechain. Le routing de la source sidechain (`Audio From → KICK`) **n'est pas réglable via MCP** (comme toute entrée). Deux options : (a) charger + configurer un **Compressor sur SUB** via MCP (S/C On, ratio ~0.9, attack rapide, release ~0.3, threshold à tuner au **mixage** = profondeur du pump) et laisser l'utilisateur faire le seul clic `Audio From → KICK` ; (b) **`--duck`** grave le ducking directement dans le fichier (détection des transients kick passe-hautée), sans routing — utile si zéro intervention voulue.
   - Si la tail du kick est trop courte (`single_tail_s` < ~0.1 s) et `--sustain` insuffisant → sub sine synthétisé sur la fondamentale.

## Phase 3 — HIGH END

1. Hiérarchie : hat principal, layers secondaires 4–6 dB en dessous (une couche = une fonction).
2. Anti-harsh : pic étroit dominant 6–10 kHz → bell -2 dB. Énergie >15 kHz excessive (>15 %) → shelf -1.5 dB.
3. Stéréo : layers secondaires pannés ±10 à ±20 ; hat principal centré.

## Phase 4 — MIDS

1. **Let the Lead lead** : lead à -12 dB, autres mids replacés sous lui par importance (2–4 dB d'écart entre niveaux).
2. **Conflits fréquentiels** : zones dominantes qui se chevauchent (mesurées en 0.2, affinées via `get_clip_notes` sur les MIDI) ET jouées ensemble → l'élément non prioritaire prend un bell -2/-3 dB sur la fondamentale de l'autre.
3. **Profondeur** : devant = +1.5 dB bell 2–5 kHz ; derrière = high-shelf -2/-3 dB + volume plus bas. Lead : Utility Width ≤ 100 %.
4. **Sidechain kick → pads/bass mid soutenus** (seulement si notes longues chevauchant le kick) : Compressor sidechain (input kick), 4:1, attack 1 ms, release 120 ms, GR 3 dB. Discret par défaut.

## Phase 5 — Master léger

Chaîne sur `-1`, dans l'ordre : **EQ Eight** (neutre, réserve ≤ 1.5 dB) → **Glue Compressor** (2:1, attack 30 ms, release Auto, GR 1–2 dB au climax) → **Limiter** (ceiling -1.0 dB, gain pour ≤ 3 dB de réduction au climax). Master d'écoute propre, pas de loudness war.

## Phase 5.5 — Boucle Red/Green (Definition of Done mesurable)

Le mix n'est **fini** que quand `scripts/mix_tests.py` retourne **exit 0 (🟢 GREEN)** sur un rendu du climax.
Dépendances (une fois) : `pip install numpy soundfile scipy pyloudnorm`.

### Setup (une seule fois, manuel — demander à l'utilisateur au début de la Phase 5.5)
Créer dans Ableton une piste audio **MIX_TEST**, input = **Resampling**, monitoring **Off**. Le MCP ne règle pas le routing d'entrée → cette étape est humaine. (Si MIX_TEST reste routée vers le master, la muter après l'enregistrement pour ne pas la re-capturer.) La mécanique d'enregistrement en aval (arm → record → play → stop → clip avec `file_path`) est **vérifiée** ; seul ce routing Resampling reste manuel.

### Profil spectral personnalisé (fortement recommandé)
Si l'utilisateur a un dossier `refs/` de tracks de référence (WAV/AIFF/FLAC/MP3, 3–5 masters du **même style** que la track mixée), construire le profil AVANT la boucle :
```
python scripts/make_profile.py refs/*.wav --name mes_refs -o mes_refs.json
```
Le script isole le climax (fenêtre de 30 s la plus forte) de chaque référence, moyenne les courbes spectrales par octave et fixe les tolérances (± max(1.5σ, 2.5 dB) : plus les refs se ressemblent, plus le test est serré). Utiliser ensuite `--profile-file mes_refs.json` à l'étape 2 : « sonner comme mes références » devient un test automatique.

⚠ **Les profils génériques (`techno_bass_heavy`, `house`) sont conservateurs dans le bas** — vérifié : de vrais masters club (Robert Hood, Crime Partners) sont à **+10 à +15 dB à 63 Hz** vs bruit rose, là où le profil générique n'autorise que +6. Un mix calé sur le générique sera **sous-basse** pour le club. Dès que des références existent, le profil `make_profile.py` est la cible fiable ; le générique n'est qu'un filet de sécurité sans refs. ⚠ Seul le **spectre** des références fait cible, **pas leurs LUFS** (ce sont des masters finis à -8/-6) : garder `--premaster`.

### La boucle (max 3 itérations)
1. **Render** (séquence MCP vérifiée en conditions réelles — produit bien un `.aif` avec `file_path` lisible) :
   armer MIX_TEST (`set_track_arm`, True) → `set_record_mode` ON → `play_arrangement(time=<début climax>)` → **attendre en wall-clock** (outil shell `sleep 45`, le MCP n'a pas de pause) → `stop_playback` → `set_record_mode` OFF → désarmer. Récupérer le clip via `get_arrangement_clips` sur MIX_TEST : son `file_path` est le rendu à tester.
   ⚠ Ne suppose pas la position de départ exacte : `play_arrangement(time=x)` ne se cale pas toujours pile sur `x`. Enregistre une **fenêtre généreuse (45–60 s)** et vérifie via le `start_time`/`length` du clip qu'elle couvre bien le climax ; peu importe le décalage tant que c'est du vrai master soutenu.
   Si l'enregistrement échoue (0 clip, ou fichier vide → `mix_tests.py` renvoie exit 2) : passer au **Plan B** ci-dessous.
2. **Test** : `python scripts/mix_tests.py <file_path> --profile-file mes_refs.json --premaster` si un profil de références a été construit ; sinon `--profile techno_bass_heavy` (ou `house`). `--premaster` = cibles avant mastering, le retirer seulement pour un master d'écoute final.
3. Lire l'**exit code** :
   - **2 (rendu invalide)** → ne touche PAS au mix. La capture est cassée (silence, <20 s, ou pas de signal) : corrige le setup MIX_TEST (Resampling, armement, master qui joue) et ré-enregistre. Le JSON liste les `problems`.
   - **1 (RED)** → appliquer UNIQUEMENT les `fix_if_red` des tests échoués, dans cet ordre : corrélation/phase → énergie <30 Hz → true peak → LUFS → PLR → spectre par octave. Un seul move par test, ≤ 2 dB. Supprimer le clip de test (`delete_arrangement_clip`), retour à l'étape 1.
   - **0 (GREEN)** → mix terminé, Phase 6, joindre le JSON final au rapport.
4. Toujours RED après 3 itérations → STOP (risque de sur-mixage). Consigner les tests rouges restants avec leur fix, et signaler si le problème relève de la **production** (macro-dynamique plate = arrangement statique ; creux spectral = instrument manquant) — dans ce cas **aucun EQ ne doit le masquer**.

### Plan B — export manuel (si l'enregistrement MCP est capricieux)
La séquence d'enregistrement a été validée, mais si sur une machine/config donnée elle ne produit pas de rendu exploitable (exit 2 répété, MIX_TEST introuvable, routing Resampling impossible), **ne bloque pas la boucle** : demander à l'utilisateur d'exporter le climax à la main — **File → Export Audio/Video**, sélectionner ~45 s autour du climax, Rendered Track = **Master**, laisser normalize OFF — puis donner le chemin du WAV à l'agent. Le reste de la boucle (test → fix → ré-export) est identique. C'est une action manuelle par itération (max 3), le prix de la robustesse quand l'auto-capture ne passe pas.

### Ce que les tests vérifient (la "Definition of Done")
LUFS intégré dans la cible · true peak ≤ -1 dBTP · PLR 6–13 dB (ni écrasé ni mou) · corrélation > 0 partout et ≥ 0.9 sous 100 Hz · pas d'infra <30 Hz (≤ 5 %) · macro-dynamique ≥ 1.5 dB · spectre par octave dans les tolérances du profil vs bruit rose. Les tolérances par octave vivent dans le dict `PROFILES` en tête de `mix_tests.py` — c'est ta courbe de référence, ajustable si trop stricte/laxiste sur ta track.

### Tests unitaires par phase (avant le render, vérifiables via MCP + analyze_audio.py)
À valider en fin de chaque phase comme des asserts :
- [P1] gain kick = -6 dB ; écart kick/sub 3–6 dB ; lead/hat -12 ; secondaires -16/-24
- [P2] Utility Bass Mono sur le low end ; HPF sur toute piste hors low end ; fondamentale kick 41–59 Hz (sinon ⚠ production)
- [P3] hat principal 4–6 dB au-dessus des layers ; aucun pan > ±20
- [P4] Width du lead ≤ 100 % ; sidechain GR ≤ 3 dB
- [P5] ordre chaîne master EQ→Glue→Limiter ; GR glue ≤ 2 dB ; ceiling -1.0
Relire les paramètres (`get_device_parameters`) après chaque écriture.

## Phase 6 — MIX_REPORT.md (obligatoire)

```markdown
# Mix Report — [projet] — [date]

## Auto-découverte
BPM, genre inféré, kick (fondamentale + note), lead identifié + justification, table des pistes (bande/rôle/peak/RMS/% spectral).

## Gain staging
| Piste | Avant | Après | Raison |

## Par piste / groupe
### [Nom]
- **Device ajouté** : [nom + position]
- **Réglages** : [param = valeur réelle (normalisé)]
- **Pourquoi** : [règle appliquée + mesure qui l'a déclenchée]
- **🎛 Pour ajuster toi-même** : [ex: "plus de punch → bell 2–4 kHz bande 3 EQ Eight ; pompage → allonge le release du Compressor"]

## Master
[chaîne + réglages]

## Résultat Red/Green
[JSON final de mix_tests.py + nombre d'itérations ; tests restés rouges avec fix, et si c'est un problème de production]

## ⚠ À vérifier à l'oreille (les seuls points où l'analyse numérique ne suffit pas)
[caractère de la saturation, tail du sub sur le kick suivant, agressivité résiduelle — avec pour chacun LE paramètre à bouger]

## Ce que cette track t'apprend
[2-3 principes du mix illustrés concrètement]
```

## Erreurs à ne jamais commettre

EQ raide qui déphase le kick · couper la tail du kick · sub qui bave sur le kick suivant (longueur du sub vs intervalle entre kicks au BPM mesuré) · sur-nettoyer les artefacts · panner pour réparer un masquage · loudness war sur le master · corriger un problème de production à l'EQ · modifier sans documenter.

---

# Couche MCP — traduire dB / Hz / ratio → normalisé 0.0–1.0

Les tools `set_device_parameter` et `set_track_volume` prennent **toujours un normalisé 0.0–1.0** (jamais des dB/Hz directement). Cette section est la traduction ; elle est **vérifiée sur le code du Remote Script et sur des devices réels**, pas devinée.

## La formule (exacte, pour tout paramètre de device)

Le Remote Script fait littéralement `valeur_réelle = min + normalisé × (max − min)`. Le mapping est donc **linéaire** pour **chaque** paramètre de device, dans son unité native :

```
normalisé = (cible − min) / (max − min)
```

Méthode fiable en 4 temps, pour chaque réglage :
1. `get_device_parameters(track, device_index)` → lire `min`, `max` du paramètre (il renvoie aussi `value` réel et `normalized_value` courants).
2. `normalisé = (cible − min) / (max − min)`, clampé à [0, 1].
3. `set_device_parameter(track, device_index, param_index, normalisé)` → le retour contient la **valeur réelle obtenue**.
4. **Vérifier** : valeur réelle ≈ cible ? Sinon (rare : param dont l'unité affichée ≠ unité interne), ajuster par dichotomie en relisant `value`.

Exemples réels mesurés (Saturator) : **Drive** min=-36/max=36 → +6 dB = `(6+36)/72 = 0.583`. **Output** min=-36/max=0 → -3 dB = `(-3+36)/36 = 0.917`.

## Gain staging exact (Phase 1) — Utility Gain, pas le fader

Le **fader mixer** (`set_track_volume`) prend un 0–1 mais suit la **courbe non-linéaire d'Ableton** (`0.85` = 0 dB) : pas de dB précis par formule. Deux options :

- **Précis** (recommandé) : insérer un **Utility**, régler son **Gain** (min=-35, max=35 dB, **linéaire** → formule exacte). Le RMS mesuré par `analyze_audio.py` donne la cible ; le Gain Utility t'y amène au dB près.
- **Approx** (balance grossière) : `set_track_volume` avec ces ancres de la courbe Ableton (approximatives) :

| normalisé | ≈ dB | normalisé | ≈ dB |
|---|---|---|---|
| 1.00 | +6 | 0.50 | -17 |
| 0.85 | 0 | 0.40 | -25 |
| 0.75 | -5 | 0.30 | -32 |
| 0.60 | -12 | 0.15 | -52 |

Les cibles de Phase 1 étant **relatives**, de petites erreurs de table affectent tout pareil : la hiérarchie reste juste. Pour un mix propre, préfère Utility Gain + RMS mesuré.

## URIs de chargement des devices natifs (vérifiés dans le browser)

`load_instrument_or_effect(track_index, uri)` — `track_index = -1` pour le master.

| Device | URI |
|---|---|
| EQ Eight | `query:AudioFx#EQ%20Eight` |
| Utility | `query:AudioFx#Utility` |
| Saturator | `query:AudioFx#Saturator` |
| Glue Compressor | `query:AudioFx#Glue%20Compressor` |
| Compressor | `query:AudioFx#Compressor` |
| Limiter | `query:AudioFx#Limiter` |
| Drum Buss | `query:AudioFx#Drum%20Buss` |

Chargement échoué (pack déplacé, version différente) → retrouver l'URI via `get_browser_items_at_path("audio_effects")`.

## Rappels d'index
- `track_index` : 0+ pistes normales, `-1` master, `-2`/`-3` returns A/B.
- `device_index` : ordre dans la chaîne (0 = premier). Après `load_instrument_or_effect`, le device est en fin de chaîne — relire `get_track_info` pour son index avant de le régler.
- Après chaque `set_device_parameter`, la valeur réelle renvoyée est ta vérification immédiate ; documenter `param = valeur_réelle (normalisé)` dans le rapport.
