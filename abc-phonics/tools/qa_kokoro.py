#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""鉴定 Kokoro 合成的 L/R/N/V 候选：三重听审 + 结构 + 无元音头核验。
在系统 python3 运行（whisper/allosaurus 在系统环境里）。"""
import os
import subprocess
import wave

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAND = os.path.join(ROOT, "candidates")
SR = 16000


def to_wav16(src, dst):
    subprocess.run(["afconvert", src, dst, "-f", "WAVE", "-d", f"LEI16@{SR}", "-c", "1"],
                   check=True, capture_output=True)


def stats(x):
    hop = int(0.010 * SR)
    n = len(x) // hop
    rms = np.array([np.sqrt(np.mean(x[i*hop:(i+1)*hop] ** 2)) for i in range(n)])
    zcr = np.array([np.mean(np.abs(np.diff(np.sign(x[i*hop:(i+1)*hop])))) / 2 for i in range(n)])
    peak = rms.max() or 1
    act = rms > 0.15 * peak
    voiced = float((act & (zcr < 0.12)).sum()) / (act.sum() or 1)
    dur_ms = int(act.sum()) * 10
    return voiced, dur_ms


def main():
    from faster_whisper import WhisperModel
    from allosaurus.app import read_recognizer
    wh = WhisperModel("large-v3", device="cpu", compute_type="int8")
    al = read_recognizer()
    print(f"{'候选':<14} {'有效ms':>6} {'浊比':>4}  whisper | allosaurus")
    print("-" * 64)
    for f in sorted(os.listdir(CAND)):
        if not f.endswith(".wav"):
            continue
        src = os.path.join(CAND, f)
        wav = src + ".16k.wav"
        to_wav16(src, wav)
        with wave.open(wav, "rb") as w:
            x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float64)
        voiced, dur = stats(x)
        s, _ = wh.transcribe(wav, language="en", beam_size=5, temperature=0.0,
                             condition_on_previous_text=False, without_timestamps=True)
        heard = " ".join(t.text.strip() for t in s).strip() or "(空)"
        try:
            phones = al.recognize(wav, "eng") or "(空)"
        except Exception as e:
            phones = f"失败:{e}"
        os.remove(wav)
        print(f"{f:<14} {dur:>6} {voiced:>4.0%}  {heard} | {phones}")


if __name__ == "__main__":
    main()
