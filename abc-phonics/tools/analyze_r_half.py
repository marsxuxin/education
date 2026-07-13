#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""聚焦精析样本的 R 半段（6s 之后）：高噪声门限 + 细粒度切分 + 逐段音素。"""
import os
import subprocess
import sys

import numpy as np

SR = 16000
SRC = sys.argv[1]   # 样本音频路径由命令行传入


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


def main():
    wav = SRC + ".r.wav"
    subprocess.run(["afconvert", SRC, wav, "-f", "WAVE", "-d", f"LEI16@{SR}", "-c", "1"],
                   check=True, capture_output=True)
    x = read_wav_raw(wav)
    os.remove(wav)
    x = x[int(6.0 * SR):]          # 只看 R 半段
    hop = int(0.010 * SR)
    n = len(x) // hop
    rms = np.array([np.sqrt(np.mean(x[i*hop:(i+1)*hop] ** 2)) for i in range(n)])
    peak = rms.max() or 1
    act = rms > 0.22 * peak        # 高门限压噪声
    bounds, i = [], 0
    while i < n:
        if act[i]:
            j, gap = i, 0
            while j < n and gap < 18:   # 180ms 段界
                gap = gap + 1 if not act[j] else 0
                j += 1
            if (j - gap - i) * 10 >= 120:   # 忽略 <120ms 的噪声点
                bounds.append((i, j - gap))
            i = j
        else:
            i += 1
    from allosaurus.app import read_recognizer
    al = read_recognizer()
    print(f"R 半段共 {len(bounds)} 个声音段：")
    for k, (a, b) in enumerate(bounds):
        s0 = max(0, a * hop - int(0.03 * SR))
        s1 = min(len(x), b * hop + int(0.03 * SR))
        segwav = f"/tmp/rseg{k}.wav"
        write_wav(segwav, x[s0:s1])
        try:
            phones = al.recognize(segwav, "eng") or "(空)"
        except Exception as e:
            phones = f"失败:{e}"
        os.remove(segwav)
        print(f"  段{k}: +{a*10/1000:5.2f}-{b*10/1000:5.2f}s ({(b-a)*10:4d}ms)  音素: {phones}")


if __name__ == "__main__":
    main()
