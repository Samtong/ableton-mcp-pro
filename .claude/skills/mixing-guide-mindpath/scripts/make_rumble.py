#!/usr/bin/env python3
"""make_rumble.py — Extrait proprement la tail (sub) d'un kick pour créer un clip rumble/sub.

Coupe aux passages à zéro, applique fade in/out, et peut caler la longueur sur
l'intervalle entre deux kicks (BPM) pour que la tail ne bave pas sur le kick suivant.

Usage:
    python make_rumble.py kick.wav -o rumble.wav --bpm 128 --gap-start 0.25 --gap-end 0.95
    # --gap-start/--gap-end : position de début/fin du rumble dans le beat (0=kick, 1=kick suivant)

Sortie: rumble.wav (mono) + JSON d'info (fondamentale, durées, positions de placement en beats).
Le clip est à placer via create_arrangement_audio_clip à chaque beat + gap_start.

Dépendances: numpy, soundfile
"""
import sys, json, argparse
import numpy as np
import soundfile as sf

def zero_cross_after(x, i):
    """Premier passage à zéro (montant) à partir de l'indice i."""
    s = np.sign(x[i:])
    z = np.where((s[:-1] <= 0) & (s[1:] > 0))[0]
    return i + int(z[0]) + 1 if len(z) else i

def zero_cross_before(x, i):
    s = np.sign(x[:i])
    z = np.where((s[:-1] <= 0) & (s[1:] > 0))[0]
    return int(z[-1]) + 1 if len(z) else i

def fundamental(x, sr):
    n = max(len(x), 16384)
    spec = np.abs(np.fft.rfft(x * np.hanning(len(x)), n=n))
    f = np.fft.rfftfreq(n, 1 / sr)
    m = (f >= 30) & (f <= 100)
    return float(f[m][np.argmax(spec[m])])

def stable_grain_start(x, sr, start_i, win, fmin=30.0, fmax=100.0, span_s=0.25):
    """Cherche, dans les ~span_s après start, la fenêtre de `win` samples dont le
    pitch (via passages à zéro) varie le MOINS, avec une amplitude suffisante.
    Un grain pris pendant la descente de pitch du kick, bouclé, wobble = le
    'fiou' ; celui-ci choisit le grain le plus stable, quel que soit le kick."""
    end = min(start_i + int(span_s * sr), len(x) - win)
    ref_amp = np.abs(x[start_i:start_i + int(span_s * sr)]).max() or 1e-9
    best_i, best_var, step = start_i, 1e18, max(win // 4, 1)
    i = start_i
    while i < end:
        seg = x[i:i + win]
        zc = np.where((np.sign(seg[:-1]) <= 0) & (np.sign(seg[1:]) > 0))[0]
        fr = [sr / (zc[j + 1] - zc[j]) for j in range(len(zc) - 1)]
        fr = [f for f in fr if fmin <= f <= fmax]
        if len(fr) >= 2 and np.abs(seg).max() > 0.4 * ref_amp:
            v = float(np.std(fr))
            if v < best_var:
                best_var, best_i = v, i
        i += step
    return best_i

def detect_onsets(x, sr, thr_ratio=0.28, min_gap_s=0.07, hp_hz=150.0):
    """Positions (s) des transients de kick. On PASSE-HAUT d'abord (>150 Hz) :
    sinon les cycles de sub (~44 Hz) créent des fausses montées et on duckerait
    à chaque oscillation. Le transient du kick, lui, a de l'énergie large bande."""
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / sr)
    X[f < hp_hz] = 0
    xf = np.fft.irfft(X, len(x))
    w = max(int(0.003 * sr), 1)
    env = np.convolve(np.abs(xf), np.ones(w) / w, "same")
    d = np.diff(env, prepend=env[0]); d[d < 0] = 0
    pk = d.max() or 1e-9
    onsets, i, step = [], 0, int(min_gap_s * sr)
    while i < len(d):
        if d[i] > pk * thr_ratio:
            onsets.append(i / sr); i += step
        else:
            i += 1
    return onsets

def apply_duck(loop, sr, onsets, loop_len_s, duck_db, atk_ms=4, rel_ms=110):
    """Grave un sidechain : à chaque onset, gain -> duck (attack rapide) puis
    retour à 1 (release). Reproduit le ducking d'un compresseur sidechain, mais
    dans le fichier — pas besoin de router quoi que ce soit."""
    gain = np.ones(len(loop))
    duck = 10 ** (duck_db / 20)
    atk, rel = max(int(atk_ms / 1000 * sr), 1), max(int(rel_ms / 1000 * sr), 1)
    for on in onsets:
        s = int((on % loop_len_s) * sr)
        e1 = min(s + atk, len(gain))
        if e1 > s:
            gain[s:e1] = np.minimum(gain[s:e1], np.linspace(1, duck, e1 - s))
        e2 = min(e1 + rel, len(gain))
        if e2 > e1:
            gain[e1:e2] = np.minimum(gain[e1:e2], np.linspace(duck, 1, e2 - e1))
    return loop * gain

def main():
    p = argparse.ArgumentParser()
    p.add_argument("kick")
    p.add_argument("-o", "--output", default="rumble.wav")
    p.add_argument("--bpm", type=float, default=None,
                   help="si fourni, la tail est calée sur l'intervalle entre kicks")
    p.add_argument("--gap-start", type=float, default=None,
                   help="début du rumble dans le beat (0..1). Par défaut AUTO-détecté "
                        "= là où le sub du kick a décroché (remplit le silence, pas de superposition)")
    p.add_argument("--gap-end", type=float, default=0.95,
                   help="fin du rumble dans le beat (défaut 0.95 = éteint avant le kick suivant)")
    p.add_argument("--skip-ms", type=float, default=60,
                   help="ms à sauter au début du kick (click + descente de pitch, défaut 60)")
    p.add_argument("--gain-db", type=float, default=0.0)
    p.add_argument("--loop-beats", type=int, default=None,
                   help="si fourni (avec --bpm), sort UN fichier loop de N beats "
                        "avec la tail tuilée à chaque beat (à poser en 1 clip au lieu de N)")
    p.add_argument("--sustain", action="store_true",
                   help="rumble CONTINU : boucle un grain de sub pour tenir tout le gap "
                        "(low end sans plat, cible 'continu' du cours) au lieu d'une tail qui meurt")
    p.add_argument("--duck", action="store_true",
                   help="grave un sidechain dans le fichier : ducke le sub à chaque kick "
                        "détecté (principaux + ghosts) pour qu'ils percent (pas de routing MCP requis)")
    p.add_argument("--duck-db", type=float, default=-12.0,
                   help="profondeur du duck en dB (défaut -12 ; -18 pour plus agressif)")
    a = p.parse_args()

    data, sr = sf.read(a.kick, always_2d=True)
    x = data.mean(axis=1)  # le sub doit être mono

    # 1) début de tail : après le transient/la descente, sur un passage à zéro
    start = zero_cross_after(x, int(a.skip_ms / 1000 * sr))

    # 2) AUTO-GAP : où le sub du KICK décroît (= début du trou à remplir).
    #    On regarde l'enveloppe lissée dans le 1er beat ; le rumble doit remplir
    #    le SILENCE après la décroissance du kick, PAS se superposer au sub du
    #    kick encore présent (sinon annulation de phase). Si --gap-start est
    #    fourni explicitement, il l'emporte.
    beat_s = (60.0 / a.bpm) if a.bpm else 0.5
    w = max(int(0.01 * sr), 1)
    smooth = np.convolve(np.abs(x), np.ones(w) / w, "same")
    look = smooth[:int(beat_s * sr)]
    pk = look.max() if len(look) else 1e-9
    peak_i = int(np.argmax(look))
    thr = pk * 10 ** (-18 / 20)  # -18 dB sous le pic = kick considéré "décroché"
    dec = np.where(look[peak_i:] < thr)[0]
    decay_s = (peak_i + int(dec[0])) / sr if len(dec) else 0.25 * beat_s
    gap_start = a.gap_start if a.gap_start is not None else round(decay_s / beat_s, 3)

    # 3) tail = sub décroissant du 1er kick, de `start` jusqu'à la décroissance,
    #    borné pour tenir dans le gap (gap_start..gap_end), coupé aux passages à zéro
    gap_len_s = max((a.gap_end - gap_start) * beat_s, 0.06)
    raw_end = min(start + int(gap_len_s * sr), len(x))
    end = zero_cross_before(x, raw_end)
    tail = x[start:end].copy()
    if len(tail) < int(0.04 * sr):
        sys.exit("⚠ Tail trop courte après découpe — kick trop court pour cette technique, "
                 "préférer un sub synthétisé (sine sur la fondamentale).")

    f0 = fundamental(tail, sr)

    # 3b) SUSTAIN : la copie de tail décroît et laisse un plat avant le kick suivant.
    #     Pour un low end CONTINU (cible "pink/continu" du cours), on soutient : on
    #     boucle un grain verrouillé sur des cycles entiers (donc phase-continu, pas
    #     de click) du sub établi, pour tenir toute la longueur du gap. La décroissance
    #     musicale est donnée par le fade-out ci-dessous, pas par la mort du sample.
    if a.sustain and a.bpm:
        period = sr / max(f0, 20.0)
        ncyc = max(3, int(round(0.05 * sr / period)))      # grain ≈ 50 ms
        gwin = int(round(ncyc * period))
        # grain choisi = fenêtre au pitch le plus stable (auto) → pas de 'fiou'/wobble
        g0 = zero_cross_after(x, stable_grain_start(x, sr, start, gwin))
        grain = x[g0:g0 + gwin]
        gz = zero_cross_before(grain, len(grain))
        grain = grain[:gz] if gz > period else grain
        if len(grain) >= period:
            tgt = max(int((a.gap_end - gap_start) * beat_s * sr), len(grain))
            reps = int(np.ceil(tgt / len(grain)))
            tail = np.tile(grain, reps)[:tgt].astype(float)   # concat = phase-continu
            mx = np.abs(tail).max()
            if mx > 0:
                tail /= mx                                    # niveau constant, pré-fade

    place_info = {"place_at_beat_offset": gap_start,
                  "gap_filled_beats": [gap_start, a.gap_end],
                  "kick_decays_at_beat": round(decay_s / beat_s, 3),
                  "sustain": bool(a.sustain),
                  "clip_length_beats": round(len(tail) / sr / beat_s, 3) if a.bpm else None,
                  "note": "create_arrangement_audio_clip(track_SUB, rumble.wav, "
                          "time=beat_N + offset) pour chaque beat"} if a.bpm else None

    # 4) fades anti-click : in 5 ms, out 20% de la longueur (dynamique décroissante)
    fi, fo = int(0.005 * sr), max(int(0.2 * len(tail)), int(0.01 * sr))
    tail[:fi] *= np.linspace(0, 1, fi)
    tail[-fo:] *= np.linspace(1, 0, fo) ** 1.5

    tail *= 10 ** (a.gain_db / 20)
    peak = np.abs(tail).max()
    if peak > 0.999:
        tail /= peak / 0.999

    # 5) option loop : tuiler la tail à chaque beat sur N beats → 1 seul fichier à poser
    #    (évite de créer des centaines de clips ; le rumble suit le 4-on-floor).
    out = tail
    loop_info = None
    if a.loop_beats and a.bpm:
        beat_n = int(round(60.0 / a.bpm * sr))
        total = beat_n * a.loop_beats
        loop = np.zeros(total, dtype=np.float32)
        off = int(gap_start * 60.0 / a.bpm * sr)
        for k in range(a.loop_beats):
            s = k * beat_n + off
            e = min(s + len(tail), total)
            loop[s:e] += tail[:e - s]
        out = loop
        n_onsets = 0
        if a.duck:
            onsets = detect_onsets(x, sr)
            n_onsets = len(onsets)
            out = apply_duck(out, sr, onsets, total / sr, a.duck_db)
        loop_info = {"loop_beats": a.loop_beats,
                     "loop_length_beats": a.loop_beats,
                     "ducked_at_kick_onsets": n_onsets if a.duck else None,
                     "duck_db": a.duck_db if a.duck else None,
                     "note": f"1 clip de {a.loop_beats} beats à poser/dupliquer sur la section "
                             "kick ; le rumble est déjà tuilé + duck sidechain gravé à chaque kick."}

    sf.write(a.output, out, sr, subtype="PCM_24")
    info = {"output": a.output, "sr": sr,
            "duration_s": round(len(out) / sr, 3),
            "fundamental_hz": round(f0, 1),
            "in_range_41_59": bool(41 <= f0 <= 59),
            "tail_extracted_from_s": round(start / sr, 3),
            "single_tail_s": round(len(tail) / sr, 3),
            "placement": loop_info or place_info}
    print(json.dumps(info, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
