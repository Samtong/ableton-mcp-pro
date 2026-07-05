#!/usr/bin/env python3
"""analyze_audio.py — analyse d'un fichier audio pour le mixage autonome.

Usage:
    python analyze_audio.py <file> [--kick] [--json]

Sortie (JSON): peak_dbfs, rms_dbfs, crest_db, duration_s, channels,
band_energy_pct {sub, low_mids, high_mids, highs}, dominant_peak_hz,
stereo {is_mono, correlation_full, correlation_sub_100hz},
et avec --kick : kick {fundamental_hz, note, in_range_41_59}.

Dépendances: numpy, soundfile  (pip install numpy soundfile)
"""
import sys, json, argparse
import numpy as np
import soundfile as sf

NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

def hz_to_note(f):
    if f <= 0:
        return "?"
    n = int(round(12 * np.log2(f / 440.0))) + 69
    return f"{NOTE_NAMES[n % 12]}{n // 12 - 1}"

def dbfs(x):
    return 20 * np.log10(max(x, 1e-12))

def band_energy(mono, sr):
    spec = np.abs(np.fft.rfft(mono * np.hanning(len(mono)))) ** 2
    freqs = np.fft.rfftfreq(len(mono), 1 / sr)
    bands = {"sub": (20, 100), "low_mids": (100, 300),
             "high_mids": (300, 6000), "highs": (6000, 20000)}
    tot = spec[(freqs >= 20) & (freqs <= 20000)].sum() or 1e-12
    out = {k: round(100 * spec[(freqs >= lo) & (freqs < hi)].sum() / tot, 1)
           for k, (lo, hi) in bands.items()}
    peak_idx = np.argmax(spec[(freqs >= 20) & (freqs <= 20000)])
    out_peak = float(freqs[(freqs >= 20) & (freqs <= 20000)][peak_idx])
    return out, round(out_peak, 1)

def correlation(l, r, sr, fmax=None):
    if fmax:
        # filtre passe-bas grossier via FFT pour isoler <fmax
        def lp(x):
            X = np.fft.rfft(x)
            f = np.fft.rfftfreq(len(x), 1 / sr)
            X[f > fmax] = 0
            return np.fft.irfft(X, len(x))
        l, r = lp(l), lp(r)
    denom = np.sqrt((l ** 2).sum() * (r ** 2).sum())
    if denom < 1e-12:
        return 1.0
    return round(float((l * r).sum() / denom), 3)

def kick_fundamental(mono, sr):
    """Fondamentale = pic spectral 30–100 Hz sur la partie soutenue
    (on saute les 30 premières ms : transient/click)."""
    start = int(0.03 * sr)
    seg = mono[start:start + int(0.25 * sr)]
    if len(seg) < 1024:
        seg = mono
    n = max(len(seg), 8192)
    spec = np.abs(np.fft.rfft(seg * np.hanning(len(seg)), n=n))
    freqs = np.fft.rfftfreq(n, 1 / sr)
    m = (freqs >= 30) & (freqs <= 100)
    f0 = float(freqs[m][np.argmax(spec[m])])
    # affinage parabolique
    return round(f0, 1)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("file")
    p.add_argument("--kick", action="store_true")
    p.add_argument("--json", action="store_true", default=True)
    a = p.parse_args()

    data, sr = sf.read(a.file, always_2d=True)
    l = data[:, 0]
    r = data[:, 1] if data.shape[1] > 1 else data[:, 0]
    mono = (l + r) / 2

    res = {
        "file": a.file,
        "duration_s": round(len(mono) / sr, 2),
        "channels": int(data.shape[1]),
        "peak_dbfs": round(dbfs(float(np.abs(data).max())), 2),
        "rms_dbfs": round(dbfs(float(np.sqrt((mono ** 2).mean()))), 2),
    }
    res["crest_db"] = round(res["peak_dbfs"] - res["rms_dbfs"], 2)
    res["band_energy_pct"], res["dominant_peak_hz"] = band_energy(mono, sr)
    res["stereo"] = {
        "is_mono": bool(np.allclose(l, r, atol=1e-6)),
        "correlation_full": correlation(l, r, sr),
        "correlation_sub_100hz": correlation(l, r, sr, fmax=100),
    }
    if a.kick:
        f0 = kick_fundamental(mono, sr)
        res["kick"] = {
            "fundamental_hz": f0,
            "note": hz_to_note(f0),
            "in_range_41_59": bool(41 <= f0 <= 59),
        }
    print(json.dumps(res, indent=2))

if __name__ == "__main__":
    main()
