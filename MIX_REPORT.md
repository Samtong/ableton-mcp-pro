# Mix Report — liminal_state_arrangement (to_mix_2) — 2026-07-06

Mixage via AbletonMCP + skill **mixing-guide-mindpath**. Devices natifs, chaque param relu. **Résultat : 🟢 GREEN 15/15 sur les DEUX sections (techno ET house).**

> Parcours : 1ʳᵉ session `to_mix` abandonnée (capture MCP par ré-enregistrement → transport figé + arrangement tronqué). Repartis du backup intact `final_sub`, mix ré-appliqué en **ajouts de devices only**, **test par export manuel**. Puis séparation du lead house et de l'acid techno sur 2 pistes (SYNTH H / SYNTH T) pour lever le conflit 500 Hz.

## Auto-découverte
- BPM 128 (house) → 135 (techno). Kick 44 Hz (F1). Sub 40.5 Hz mono, sidechainé au kick.
- Profil réf `mes_refs_profile.json` (Crime Partners / Robert Hood / Save the Children) = club bass-heavy.
- Climax techno = bars 77–97 (beats 304–384). Section house testée = bars 25–45.

## Indices de piste (après séparation)
0 HIGH(grp) · 1 CHH · 2 RIDE · 3 OHH · 4 MID(grp) · 5 CLAP · 6 SNARE AD H · **7 SYNTH H (house)** · **8 SYNTH T (techno)** · 9 LOW(grp=kick+sub) · 10 KICK · 11 SUB · 12 MIX_TEST · −1 Master

## Chaîne de traitement

| Piste | Device | Réglage | Pourquoi |
|---|---|---|---|
| **LOW** (grp, 9) | Utility | Bass Mono ON ~100 Hz | mono <100 Hz → corrélation 1.00 |
| **SYNTH H** (7, lead house) | EQ Eight | HPF ~90 Hz · **bell −4 dB @ 450 (large)** · **bell −3 dB @ 620** · **+2.5 dB @ 2 kHz** | dégonfle le bas-médium house (mid-forward) + présence |
| **SYNTH T** (8, acid techno) | EQ Eight | HPF ~90 Hz · **bell +4 dB @ 500** | corr <100 Hz de l'acid + comble le scoop 500 du techno |
| **SNARE** (6, house only) | EQ Eight | bell −3 dB @ 400 Hz | aide le 500 house (aucun impact techno) |
| **CHH** (1) | EQ Eight | HPF ~300 Hz, centré | hygiène |
| **OHH** (3) | EQ Eight | HPF ~250 Hz · pan +15 % | hygiène + largeur |
| **RIDE** (2) | EQ Eight | HPF ~400 Hz · pan −15 % | hygiène + largeur |
| **CLAP** (5) | EQ Eight | HPF ~180 Hz | hygiène |
| **Master** (−1) | EQ Eight | HPF 48 dB/oct ~27 Hz · high-shelf −1.5 dB @ 7 kHz | anti-infra <30 Hz · dompte le 8 kHz |
| **Master** | Glue Comp | 2:1, attack 30 ms, release Auto, thr −6 dB | glue léger |
| **Master** | Limiter | ceiling −1.5 dB, gain +7.68 dB, auto release | true peak ≤ −1 + loudness premaster |

**Principe clé** : le lead house et l'acid techno partageaient une piste et demandaient l'inverse à 500 Hz (house trop plein / techno trop scoopé). Impossible à résoudre au master ou sur une piste partagée → **séparation en 2 pistes** = chacun EQ librement. C'est LA leçon de ce mix.

## Résultat Red/Green — 🟢 GREEN × 2

**TECHNO** (bars 73–99, premaster) : LUFS −13.3 · TP −1.29 · PLR 12.0 · corr<100Hz 1.00 · macro 8.3 · octaves 8/8 (500 = −6.81, marge 1.2 dB via bell +5.5 dB @ 500 sur SYNTH T).
**HOUSE** (bars 25–45, premaster) : 15/15.

## 🎛 Pour ajuster
- Loudness globale : gain d'entrée du Limiter master (couple les 2 sections).
- House trop/pas assez creusé : bell −4 @ 450 de **SYNTH H**.
- Techno 500 : bell +4 @ 500 de **SYNTH T**.
- Brillance : high-shelf master band 8.

## ⚠ À vérifier à l'oreille
- Caractère du limiteur (kick ~4 dB de réduction au climax ; PLR 12 = ça respire).
- Le boost +4 @ 500 sur l'acid ne le rend pas trop nasal.
- Timing du rumble house (recalé manuellement) : continuité kick→rumble.

## À faire quand tu veux
- **Master d'écoute final** : retirer `--premaster` et pousser vers −8/−9 LUFS (garder cette version premaster pour un ingé mastering).
- Supprimer les clips de session en double sur SYNTH H/T (cosmétique).
