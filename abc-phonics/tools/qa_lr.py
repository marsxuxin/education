#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""L/R 示范音候选对比鉴定：SCR 真人版 vs 合成持续音版。"""
import os
import subprocess
import wave

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REC = os.path.join(ROOT, "recordings")
SR = 16000

CANDIDATES = [
    ("L 现版(SCR真人)", os.path.join(REC, "alphasounds-l.mp3"), None),
    ("L 候选 lll",      None, "lll"),
    ("L 候选 ll",       None, "ll"),
    ("L 候选 la",       None, "la"),
    ("R 现版(SCR真人)", os.path.join(REC, "alphasounds-r.mp3"), None),
    ("R 候选 rrr",      None, "rrr"),
    ("R 候选 rr",       None, "rr"),
]


def to_wav(src, dst):
    subprocess.run(["afconvert", src, dst, "-f", "WAVE", "-d", f"LEI16@{SR}", "-c", "1"],
                   check=True, capture_output=True)


def voiced_fraction(wav_path):
    with wave.open(wav_path, "rb") as w:
        x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float64)
    hop = int(0.010 * SR)
    n = len(x) // hop
    rms = np.array([np.sqrt(np.mean(x[i*hop:(i+1)*hop] ** 2)) for i in range(n)])
    zcr = np.array([np.mean(np.abs(np.diff(np.sign(x[i*hop:(i+1)*hop])))) / 2 for i in range(n)])
    peak = rms.max() or 1
    act = rms > 0.15 * peak
    if act.sum() == 0:
        return 0.0
    return float((act & (zcr < 0.12)).sum()) / float(act.sum())


def main():
    from faster_whisper import WhisperModel
    from allosaurus.app import read_recognizer
    wh = WhisperModel("large-v3", device="cpu", compute_type="int8")
    al = read_recognizer()
    print(f"{'候选':<16} {'浊比':>4}  whisper听到 | allosaurus音素")
    print("-" * 60)
    for label, path, synth_text in CANDIDATES:
        if path is None:
            path = f"/tmp/qa_lr_{synth_text}.aiff"
            subprocess.run(["say", "-v", "Samantha", "-o", path, synth_text],
                           check=True, capture_output=True)
        wav = path + ".qa.wav"
        to_wav(path, wav)
        segs, _ = wh.transcribe(wav, language="en", beam_size=5, temperature=0.0,
                                condition_on_previous_text=False, without_timestamps=True)
        heard = " ".join(s.text.strip() for s in segs).strip() or "(空)"
        try:
            phones = al.recognize(wav, "eng") or "(空)"
        except Exception as e:
            phones = f"失败:{e}"
        vf = voiced_fraction(wav)
        os.remove(wav)
        print(f"{label:<16} {vf:>4.0%}  {heard} | {phones}")


if __name__ == "__main__":
    main()
