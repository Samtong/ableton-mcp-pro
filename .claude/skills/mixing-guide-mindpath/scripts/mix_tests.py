#!/usr/bin/env python3
"""mix_tests.py — Suite de tests Red/Green sur un rendu du master (climax).

Usage:
    python mix_tests.py <master_render.wav> [--profile techno_bass_heavy] [--premaster]

Sortie: table PASS/FAIL + JSON. Exit code 0 = GREEN (tout passe), 1 = RED.

Dépendances: numpy, soundfile, scipy, pyloudnorm
    pip install numpy soundfile scipy pyloudnorm
"""
import sys, json, argparse
import numpy as np
import soundfile as sf

try:
    import pyloudnorm as pyln
except ImportError:
    sys.exit("pip install pyloudnorm scipy")

# ---------------------------------------------------------------- profiles
# Tolérances de déviation spectrale par octave, en dB, vs bruit rose
# (bruit rose = énergie égale par octave => cible plate). (min, max) par bande.
PROFILES = {
    "techno_bass_heavy": {
        "octaves": {63: (-2, 6), 125: (-3, 4), 250: (-4, 3), 500: (-4, 3),
                    1000: (-4, 3), 2000: (-4, 3), 4000: (-5, 3), 8000: (-7, 2)},
    },
    "house": {
        "octaves": {63: (-3, 5), 125: (-3, 4), 250: (-4, 3), 500: (-4, 3),
                    1000: (-3, 3), 2000: (-3, 3), 4000: (-4, 3), 8000: (-6, 3)},
    },
}

def db(x):
    return 20 * np.log10(max(x, 1e-12))

def true_peak_dbtp(data, sr):
    """True peak via suréchantillonnage x4 (zero-padding FFT)."""
    tp = 0.0
    for ch in range(data.shape[1]):
        x = data[:, ch]
        n = len(x)
        X = np.fft.rfft(x)
        X4 = np.zeros(n * 2 + 1, dtype=complex)
        X4[: len(X)] = X
        y = np.fft.irfft(X4, n * 4) * 4
        tp = max(tp, float(np.abs(y).max()))
    return round(db(tp), 2)

def octave_deviation(mono, sr):
    """Énergie par octave (centres 63..8000), en dB relatif à la moyenne.
    Bruit rose parfait => 0 dB partout."""
    spec = np.abs(np.fft.rfft(mono * np.hanning(len(mono)))) ** 2
    freqs = np.fft.rfftfreq(len(mono), 1 / sr)
    out = {}
    for c in [63, 125, 250, 500, 1000, 2000, 4000, 8000]:
        lo, hi = c / np.sqrt(2), c * np.sqrt(2)
        e = spec[(freqs >= lo) & (freqs < hi)].sum()
        out[c] = 10 * np.log10(max(e, 1e-18))
    mean = np.mean(list(out.values()))
    return {c: round(v - mean, 2) for c, v in out.items()}

def lowpass(x, sr, fmax):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / sr)
    X[f > fmax] = 0
    return np.fft.irfft(X, len(x))

def correlation(l, r):
    d = np.sqrt((l ** 2).sum() * (r ** 2).sum())
    return 1.0 if d < 1e-12 else round(float((l * r).sum() / d), 3)

# ---------------------------------------------------------------- render sanity
def render_sanity(data, sr, meter):
    """Garde-fou : un rendu vide / trop court / à peine audible produit sinon
    des tests trompeurs (LUFS -inf marqué RED, true peak -240 dB marqué PASS)
    et l'agent corrige des fantômes. On échoue LOUD et CLAIR à la place —
    le problème est la CAPTURE, pas le mix.

    Renvoie (ok, problems). Si not ok : ne pas lancer les 15 tests, exit 2."""
    problems = []
    dur = len(data) / sr
    if dur < 20:
        problems.append(f"Rendu trop court ({dur:.1f}s) : il faut >= 20 s de "
                        "climax pour un LUFS integre et une macro-dynamique "
                        "fiables. Re-enregistre plus longtemps.")
    peak = db(float(np.abs(data).max()) if data.size else 0.0)
    if peak < -50:
        problems.append(f"Rendu quasi silencieux (peak {peak:.1f} dBFS). "
                        "Capture cassee : verifie que MIX_TEST a bien input "
                        "Resampling, qu'elle est armee, et que le master joue.")
    ivalue = meter.integrated_loudness(data)
    if not np.isfinite(ivalue) or ivalue < -40:
        problems.append(f"Loudness integre non exploitable ({ivalue}). "
                        "Rendu vide ou signal sous le gate LUFS : re-render.")
    return (len(problems) == 0), problems


# ---------------------------------------------------------------- tests
def run(path, profile_name, premaster):
    data, sr = sf.read(path, always_2d=True)
    if data.shape[1] == 1:
        data = np.column_stack([data[:, 0], data[:, 0]])
    l, r = data[:, 0], data[:, 1]
    mono = (l + r) / 2
    meter = pyln.Meter(sr)

    ok, problems = render_sanity(data, sr, meter)
    if not ok:
        report = {"file": path, "GREEN": False, "render_valid": False,
                  "problems": problems}
        print(json.dumps(report, indent=2, ensure_ascii=False))
        print("\n⚠️  RENDU INVALIDE — corrige la CAPTURE, pas le mix :",
              file=sys.stderr)
        for p in problems:
            print("   - " + p, file=sys.stderr)
        return 2

    integrated = round(meter.integrated_loudness(data), 2)
    # short-term (fenêtres 3 s, hop 1 s) pour la macro-dynamique
    st = []
    w, hop = 3 * sr, sr
    for i in range(0, len(mono) - w, hop):
        st.append(meter.integrated_loudness(data[i:i + w]))
    st = [v for v in st if np.isfinite(v)]
    macro_range = round(np.percentile(st, 95) - np.percentile(st, 10), 2) if len(st) >= 4 else None

    tp = true_peak_dbtp(data, sr)
    plr = round(tp - integrated, 2)
    dev = octave_deviation(mono, sr)
    corr_full = correlation(l, r)
    corr_sub = correlation(lowpass(l, sr, 100), lowpass(r, sr, 100))
    spec = np.abs(np.fft.rfft(mono)) ** 2
    freqs = np.fft.rfftfreq(len(mono), 1 / sr)
    infra_pct = round(100 * spec[freqs < 30].sum() / max(spec[(freqs >= 20) & (freqs <= 20000)].sum(), 1e-18), 2)

    lufs_target = (-14, -10) if premaster else (-10, -7.5)
    prof = PROFILES[profile_name]["octaves"]

    tests = []
    def t(name, ok, value, target, fix):
        tests.append({"test": name, "pass": bool(ok), "value": value,
                      "target": target, "fix_if_red": fix})

    t("LUFS intégré (climax)", lufs_target[0] <= integrated <= lufs_target[1],
      integrated, f"{lufs_target[0]} à {lufs_target[1]} LUFS",
      "trop bas → +gain limiteur master (max 3 dB GR) ; trop haut → -gain, on ne smash pas")
    t("True peak", tp <= -0.9, tp, "≤ -1.0 dBTP",
      "baisser le ceiling du Limiter à -1.0")
    t("PLR (dynamique)", 6.0 <= plr <= 13.0, plr, "6–13 dB",
      "<6 = écrasé → réduire GR limiter/glue ; >13 = mou → transients irréguliers, vérifier micro-dynamique")
    t("Corrélation full", corr_full > 0.0, corr_full, "> 0 (mono-compatible)",
      "réduire Width des éléments larges (Utility), vérifier effets temporels")
    t("Corrélation <100 Hz", corr_sub >= 0.9, corr_sub, "≥ 0.9 (~mono)",
      "Utility Bass Mono 100 Hz manquant ou source hors-phase dans le low end")
    t("Énergie <30 Hz", infra_pct <= 5.0, f"{infra_pct}%", "≤ 5% (infra inutile)",
      "HPF 24 dB/oct à 25–30 Hz sur le master ou sur le sub")
    if macro_range is not None:
        t("Macro-dynamique (p95-p10 short-term)", macro_range >= 1.5,
          macro_range, "≥ 1.5 dB de mouvement",
          "arrangement trop statique — hors périmètre mix, à noter au rapport")
    for c, (lo, hi) in prof.items():
        t(f"Spectre octave {c} Hz vs rose", lo <= dev[c] <= hi, dev[c],
          f"{lo} à {hi} dB",
          f"bell doux (≤2 dB) sur l'EQ master autour de {c} Hz, ou revoir le niveau des pistes dominantes de cette bande")

    green = all(x["pass"] for x in tests)
    report = {"file": path, "profile": profile_name,
              "premaster": premaster, "GREEN": green, "tests": tests}
    print(json.dumps(report, indent=2, ensure_ascii=False))
    print("\n" + ("🟢 GREEN — le mix passe tous les tests" if green
                  else "🔴 RED — corriger les tests en échec ci-dessus"), file=sys.stderr)
    return 0 if green else 1

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("file")
    p.add_argument("--profile", default="techno_bass_heavy", choices=list(PROFILES))
    p.add_argument("--profile-file", default=None,
                   help="profil JSON généré par make_profile.py (prioritaire sur --profile). "
                        "Calibré sur tes références = cible bien plus fiable que les profils génériques.")
    p.add_argument("--premaster", action="store_true",
                   help="cibles LUFS pour un mix avant mastering (défaut: master d'écoute)")
    a = p.parse_args()
    if a.profile_file:
        with open(a.profile_file) as fh:
            prof = json.load(fh)
        name = prof.get("name", "custom")
        PROFILES[name] = {"octaves": {int(k): tuple(v) for k, v in prof["octaves"].items()}}
        a.profile = name
    sys.exit(run(a.file, a.profile, a.premaster))
