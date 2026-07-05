#!/usr/bin/env python3
"""make_profile.py — Génère un profil spectral personnalisé à partir de tracks de référence.

Le profil devient la Definition of Done spectrale de mix_tests.py :
"ça sonne comme mes références" = test automatique.

Usage:
    python make_profile.py ref1.wav ref2.wav ref3.wav --name mes_refs -o my_profile.json
    python mix_tests.py <render.wav> --profile-file my_profile.json --premaster

Méthode:
  1. Pour chaque référence, isole la fenêtre de 30 s la plus forte (≈ climax).
  2. Calcule l'énergie par octave (63→8000 Hz) relative à la moyenne
     (bruit rose parfait = 0 dB partout) — même métrique que mix_tests.py.
  3. Moyenne les courbes et fixe les tolérances par bande :
     [moyenne - marge, moyenne + marge], marge = max(1.5 × écart-type, min-margin).
     Plus tes références se ressemblent, plus le test est exigeant.

NB : les références sont des tracks MASTERISÉES — leur spectre est une cible
valable pour ton mix, leurs LUFS ne le sont pas (garde --premaster côté tests).

Dépendances: numpy, soundfile, scipy, pyloudnorm
"""
import sys, json, argparse
import numpy as np
import soundfile as sf

OCTAVES = [63, 125, 250, 500, 1000, 2000, 4000, 8000]

def loudest_window(mono, sr, win_s=30):
    """Indices (start, end) de la fenêtre de win_s secondes la plus forte (RMS)."""
    w = int(win_s * sr)
    if len(mono) <= w:
        return 0, len(mono)
    csum = np.concatenate([[0.0], np.cumsum(mono ** 2)])
    hop = sr
    starts = np.arange(0, len(mono) - w, hop)
    energies = csum[starts + w] - csum[starts]
    i = int(starts[np.argmax(energies)])
    return i, i + w

def octave_deviation(mono, sr):
    spec = np.abs(np.fft.rfft(mono * np.hanning(len(mono)))) ** 2
    freqs = np.fft.rfftfreq(len(mono), 1 / sr)
    out = {}
    for c in OCTAVES:
        lo, hi = c / np.sqrt(2), c * np.sqrt(2)
        out[c] = 10 * np.log10(max(spec[(freqs >= lo) & (freqs < hi)].sum(), 1e-18))
    mean = np.mean(list(out.values()))
    return {c: v - mean for c, v in out.items()}

def analyze_ref(path):
    data, sr = sf.read(path, always_2d=True)
    mono = data.mean(axis=1)
    a, b = loudest_window(mono, sr)
    dev = octave_deviation(mono[a:b], sr)
    lufs = None
    try:
        import pyloudnorm as pyln
        v = pyln.Meter(sr).integrated_loudness(data[a:b])
        lufs = round(float(v), 2) if np.isfinite(v) else None
    except ImportError:
        pass
    return dev, lufs, round(a / sr, 1)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("files", nargs="+", help="2 à 6 tracks de référence (WAV/AIFF/FLAC)")
    p.add_argument("--name", default="custom")
    p.add_argument("--min-margin", type=float, default=2.5,
                   help="marge minimale ± en dB par bande (défaut 2.5)")
    p.add_argument("-o", "--output", default="custom_profile.json")
    a = p.parse_args()

    if len(a.files) < 2:
        print("⚠ Une seule référence = profil peu robuste ; 3+ recommandé.", file=sys.stderr)

    all_dev, per_file = [], {}
    for f in a.files:
        dev, lufs, climax_at = analyze_ref(f)
        all_dev.append(dev)
        per_file[f] = {"climax_at_s": climax_at, "lufs_climax": lufs,
                       "octaves_db": {f"{c}": round(dev[c], 2) for c in OCTAVES}}
        print(f"✓ {f} (climax à {climax_at}s"
              + (f", {lufs} LUFS" if lufs is not None else "") + ")", file=sys.stderr)

    octaves = {}
    for c in OCTAVES:
        vals = np.array([d[c] for d in all_dev])
        margin = max(1.5 * float(vals.std()), a.min_margin)
        octaves[str(c)] = [round(float(vals.mean()) - margin, 1),
                           round(float(vals.mean()) + margin, 1)]

    profile = {"name": a.name, "octaves": octaves, "built_from": per_file}
    with open(a.output, "w") as fh:
        json.dump(profile, fh, indent=2, ensure_ascii=False)
    print(json.dumps({"name": a.name, "octaves": octaves}, indent=2))
    print(f"\n🟢 Profil écrit : {a.output}\n   Utilisation : "
          f"python mix_tests.py <render.wav> --profile-file {a.output} --premaster",
          file=sys.stderr)

if __name__ == "__main__":
    main()
