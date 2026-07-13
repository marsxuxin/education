#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""拼接 SCR 老师的多段录音，生成声音转换用的目标音色参考（约5秒）。"""
import os
import subprocess
import wave

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REC = os.path.join(ROOT, "recordings")
OUT = os.path.join(ROOT, "candidates", "teacher-ref.wav")
SR = 22050
PICKS = ["btalpha-7-a-long", "btalpha-2-e-long", "btalpha-3-o-long",
         "btalpha-10-u-long", "alphasounds-m", "alphasounds-l",
         "alphasounds-r", "btalpha-9-ng", "alphasounds-e"]


def read_wav_raw(path):
    raw = open(path, "rb").read()
    di = raw.find(b"data")
    size = int.from_bytes(raw[di+4:di+8], "little")
    return np.frombuffer(raw[di+8:di+8+size], dtype=np.int16).astype(np.float64)


def main():
    parts = []
    gap = np.zeros(int(0.12 * SR))
    for name in PICKS:
        src = os.path.join(REC, name + ".mp3")
        w = src + ".t.wav"
        subprocess.run(["afconvert", src, w, "-f", "WAVE", "-d", f"LEI16@{SR}", "-c", "1"],
                       check=True, capture_output=True)
        x = read_wav_raw(w)
        os.remove(w)
        # 去首尾静音
        hop = int(0.010 * SR)
        n = len(x) // hop
        rms = np.array([np.sqrt(np.mean(x[i*hop:(i+1)*hop] ** 2)) for i in range(n)])
        act = np.where(rms > 0.06 * (rms.max() or 1))[0]
        x = x[act[0]*hop: (act[-1]+1)*hop]
        parts += [x, gap]
    y = np.concatenate(parts)
    y *= (0.6 * 32767) / (np.abs(y).max() or 1)
    with wave.open(OUT, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(np.clip(y, -32767, 32767).astype(np.int16).tobytes())
    print(f"老师音色参考已生成: {OUT} ({len(y)/SR:.1f}s)")


if __name__ == "__main__":
    main()
