#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从老板的 L/R 语音样本里精准抠出示范段，清理后导出。

前半段(0-6s)=L 报幕+示范×3；后半段(6s-末尾)=R 报幕+示范×3。
高门限切分抗咖啡馆底噪；每段导出为独立 wav（修边+淡入淡出+音量归一），
交由 QA 判定哪段最干净。用法：python3 extract_boss_demos.py <样本> <输出目录>
"""
import os
import subprocess
import sys

import numpy as np

SR = 16000


def read_wav_raw(path):
    raw = open(path, "rb").read()
    di = raw.find(b"data")
    size = int.from_bytes(raw[di+4:di+8], "little")
    return np.frombuffer(raw[di+8:di+8+size], dtype=np.int16).astype(np.float64)


def write_wav(path, x):
    import wave
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(np.clip(x, -32767, 32767).astype(np.int16).tobytes())


def segments(x, thr=0.22, gap_frames=18, min_ms=120):
    hop = int(0.010 * SR)
    n = len(x) // hop
    rms = np.array([np.sqrt(np.mean(x[i*hop:(i+1)*hop] ** 2)) for i in range(n)])
    peak = rms.max() or 1
    act = rms > thr * peak
    out, i = [], 0
    while i < n:
        if act[i]:
            j, g = i, 0
            while j < n and g < gap_frames:
                g = g + 1 if not act[j] else 0
                j += 1
            if (j - g - i) * 10 >= min_ms:
                out.append((i * hop, (j - g) * hop))
            i = j
        else:
            i += 1
    return out


def main():
    src, outdir = sys.argv[1], sys.argv[2]
    os.makedirs(outdir, exist_ok=True)
    wav = src + ".x.wav"
    subprocess.run(["afconvert", src, wav, "-f", "WAVE", "-d", f"LEI16@{SR}", "-c", "1"],
                   check=True, capture_output=True)
    x = read_wav_raw(wav)
    os.remove(wav)
    halves = {"L": x[: int(6.0 * SR)], "R": x[int(6.0 * SR):]}
    for label, h in halves.items():
        for k, (a, b) in enumerate(segments(h)):
            seg = h[max(0, a - int(0.03 * SR)): min(len(h), b + int(0.05 * SR))].copy()
            fi = min(len(seg), int(0.008 * SR))
            seg[:fi] *= np.linspace(0, 1, fi)
            fo = min(len(seg), int(0.030 * SR))
            seg[-fo:] *= np.linspace(1, 0, fo)
            seg *= (0.6 * 32767) / (np.abs(seg).max() or 1)
            p = os.path.join(outdir, f"boss-{label}-{k}.wav")
            write_wav(p, seg)
            print(f"{label} 段{k}: {(b-a)/SR*1000:4.0f}ms -> {os.path.basename(p)}")


if __name__ == "__main__":
    main()
