#!/usr/bin/env python3
"""Smoke tests for the audio layer. Run from repo root:  python tests/test_audio.py

Checks: modules import, sine/osc frequency is correct, every sound effect and every
music mood renders to finite, non-silent, non-clipped audio of the expected length.
"""
import sys, tempfile
from pathlib import Path

import numpy as np

KIT_AUDIO = Path(__file__).resolve().parents[1] / "skills" / "make-2d-video" / "kit" / "audio"
sys.path.insert(0, str(KIT_AUDIO))
import dsp  # noqa: E402
import sfx  # noqa: E402
import music  # noqa: E402

failures = []


def check(cond, msg):
    if not cond:
        failures.append(msg)
        print("FAIL:", msg)


def dominant_freq(x):
    spec = np.abs(np.fft.rfft(x))
    return np.fft.rfftfreq(len(x), 1 / dsp.SR)[spec.argmax()]


# 1. oscillator correctness
check(abs(dominant_freq(dsp.sine(440, dsp.SR)) - 440) < 1, "sine(440) dominant frequency is not 440 Hz")
check(abs(dominant_freq(dsp.osc("saw", 220, dsp.SR)) - 220) < 2, "osc('saw', 220) dominant frequency is not ~220 Hz")
check(abs(dsp.midi_hz(69) - 440) < 1e-6 and abs(dsp.midi_hz(81) - 880) < 1e-6, "midi_hz mapping wrong")
glide = dsp.sine(np.linspace(200, 400, dsp.SR), dsp.SR)
check(np.isfinite(glide).all() and np.abs(glide).max() <= 1.0001, "gliding sine is not finite or out of range")

# 2. every sound effect
with tempfile.TemporaryDirectory() as tmp:
    names = [name for name in sfx.LIB] if isinstance(getattr(sfx, "LIB", None), dict) and sfx.LIB else None
    if names is None:
        import subprocess
        out = subprocess.run([sys.executable, str(KIT_AUDIO / "sfx.py"), "--list"], capture_output=True, text=True).stdout
        names = [line.split()[0] for line in out.splitlines() if line.strip()]
    check(len(names) > 0, "no sound effects listed")
    for name in names:
        out = Path(tmp) / f"{name}.wav"
        r = __import__("subprocess").run([sys.executable, str(KIT_AUDIO / "sfx.py"), "--make", name, "--out", str(out)],
                                         capture_output=True, text=True)
        if r.returncode != 0 or not out.exists():
            check(False, f"sfx {name} failed: {r.stderr.strip().splitlines()[-1] if r.stderr.strip() else 'no output'}")
            continue
        from scipy.io import wavfile
        _, x = wavfile.read(out)
        x = x.astype(np.float32) / 32767
        check(np.isfinite(x).all(), f"sfx {name} has non-finite samples")
        check(np.sqrt(np.mean(x ** 2)) > 1e-4, f"sfx {name} is silent")
        check(np.abs(x).max() < 0.999, f"sfx {name} clips")

# 3. every music mood (short render)
import subprocess
out = subprocess.run([sys.executable, str(KIT_AUDIO / "music.py"), "--list"], capture_output=True, text=True).stdout
moods = [line.split()[0] for line in out.splitlines() if line.strip()]
check(len(moods) > 0, "no music moods listed")
with tempfile.TemporaryDirectory() as tmp:
    for mood in moods:
        out_path = Path(tmp) / f"{mood}.wav"
        r = subprocess.run([sys.executable, str(KIT_AUDIO / "music.py"), "--mood", mood, "--dur", "8", "--out", str(out_path)],
                           capture_output=True, text=True)
        if r.returncode != 0 or not out_path.exists():
            check(False, f"music {mood} failed: {r.stderr.strip().splitlines()[-1] if r.stderr.strip() else 'no output'}")
            continue
        from scipy.io import wavfile
        _, x = wavfile.read(out_path)
        x = x.astype(np.float32) / 32767
        check(np.isfinite(x).all(), f"music {mood} has non-finite samples")
        check(np.sqrt(np.mean(x ** 2)) > 1e-4, f"music {mood} is silent")
        check(np.abs(x).max() < 0.999, f"music {mood} clips")

print(f"audio tests: {'PASS' if not failures else f'{len(failures)} FAILURE(S)'}")
sys.exit(1 if failures else 0)
