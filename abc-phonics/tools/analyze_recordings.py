#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""录音结构分析：每条录音里有几段声音、各段多长。

用途：判断 SCR 录音是"纯音重复几遍"（合格）还是"音+示例单词"（不合格，
单词段会明显更长且能量结构复杂）。
"""
import os
import subprocess
import wave

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REC = os.path.join(ROOT, "recordings")
SR = 16000


def segments_of(path):
    wav = path + ".seg.wav"
    subprocess.run(["afconvert", path, wav, "-f", "WAVE", "-d", f"LEI16@{SR}", "-c", "1"],
                   check=True, capture_output=True)
    with wave.open(wav, "rb") as w:
        x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float64)
    os.remove(wav)
    hop = int(0.010 * SR)
    n = len(x) // hop
    rms = np.array([np.sqrt(np.mean(x[i*hop:(i+1)*hop] ** 2)) for i in range(n)])
    peak = rms.max() or 1
    active = rms > 0.06 * peak
    # 合并成段（间隔 <150ms 视为同一段）
    segs = []
    i = 0
    while i < n:
        if active[i]:
            j = i
            gap = 0
            while j < n and gap < 15:
                gap = gap + 1 if not active[j] else 0
                j += 1
            segs.append(((i * 10), ((j - gap) * 10)))  # ms
            i = j
        else:
            i += 1
    return segs


def main():
    print(f"{'文件':<28} 段数  各段时长(ms)")
    print("-" * 64)
    for f in sorted(os.listdir(REC)):
        if not f.endswith(".mp3"):
            continue
        segs = segments_of(os.path.join(REC, f))
        durs = " ".join(str(b - a) for a, b in segs)
        print(f"{f:<28} {len(segs):>3}   {durs}")


if __name__ == "__main__":
    main()
