#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""风格统一批量鉴定：SCR 真人版 vs 合成纯音版（清亮无元音头标准）。"""
import os
import subprocess
import wave

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REC = os.path.join(ROOT, "recordings")
SR = 16000

CANDIDATES = [
    ("M 现版(真人)", os.path.join(REC, "alphasounds-m.mp3"), None),
    ("M 候选 mmm",   None, "mmm"),
    ("N 现版(真人)", os.path.join(REC, "alphasounds-n.mp3"), None),
    ("N 候选 nnn",   None, "nnn"),
    ("V 现版(真人)", os.path.join(REC, "alphasounds-v.mp3"), None),
    ("V 候选 vvv",   None, "vvv"),
    ("F 现版(真人)", os.path.join(REC, "alphasounds-f.mp3"), None),
    ("F 候选 fff",   None, "fff"),
    ("Q 现版(真人)", os.path.join(REC, "alphasounds-q.mp3"), None),
    ("Q 候选 kwuh",  None, "kwuh"),
    ("Q 候选 kwah",  None, "kwah"),
    ("Z 现版(真人)", os.path.join(REC, "alphasounds-z.mp3"), None),
    ("Z 候选 zzz",   None, "zzz"),
    ("Z 候选 zzzz",  None, "zzzz"),
    ("ng 现版(真人)", os.path.join(REC, "btalpha-9-ng.mp3"), None),
    ("ng 候选 nng",  None, "nng"),
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
    print(f"{'候选':<14} {'浊比':>4}  whisper听到 | allosaurus音素")
    print("-" * 64)
    for label, path, synth_text in CANDIDATES:
        if path is None:
            path = f"/tmp/qa_su_{synth_text}.aiff"
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
        print(f"{label:<14} {vf:>4.0%}  {heard} | {phones}")


if __name__ == "__main__":
    main()
