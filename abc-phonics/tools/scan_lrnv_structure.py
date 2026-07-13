#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""L/R/N/V 真人录音结构扫描：逐 50ms 报告能量与音色，估算元音头长度。

判读：元音段=高能量+高一阶共振（响亮开口音色）；纯辅音段=稳定低开口音色。
用 频谱质心(centroid) 区分：元音(a/ə)质心明显高于鼻音/边音稳态。
"""
import os
import subprocess
import wave

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REC = os.path.join(ROOT, "recordings")
SR = 16000
FILES = ["alphasounds-l", "alphasounds-r", "alphasounds-n", "alphasounds-v"]


def load(path):
    wav = path + ".scan.wav"
    subprocess.run(["afconvert", path, wav, "-f", "WAVE", "-d", f"LEI16@{SR}", "-c", "1"],
                   check=True, capture_output=True)
    with wave.open(wav, "rb") as w:
        x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float64)
    os.remove(wav)
    return x


def main():
    for name in FILES:
        x = load(os.path.join(REC, name + ".mp3"))
        hop = int(0.050 * SR)
        n = len(x) // hop
        rows = []
        for i in range(n):
            f = x[i * hop:(i + 1) * hop]
            rms = np.sqrt(np.mean(f * f))
            spec = np.abs(np.fft.rfft(f * np.hanning(len(f))))
            freqs = np.fft.rfftfreq(len(f), 1 / SR)
            centroid = (spec * freqs).sum() / (spec.sum() or 1)
            rows.append((i * 50, rms, centroid))
        peak = max(r[1] for r in rows) or 1
        active = [r for r in rows if r[1] > 0.08 * peak]
        if not active:
            continue
        t0, t1 = active[0][0], active[-1][0] + 50
        # 有效段内，前段质心 vs 后段质心
        seg = [r for r in rows if t0 <= r[0] < t1]
        third = max(1, len(seg) // 3)
        head_c = np.mean([r[2] for r in seg[:third]])
        tail_c = np.mean([r[2] for r in seg[-third:]])
        band = " ".join(f"{r[2]:>4.0f}" for r in seg)
        print(f"{name}: 有效音 {t0}-{t1}ms ({t1-t0}ms)")
        print(f"  逐50ms频谱质心(Hz): {band}")
        print(f"  前1/3平均 {head_c:.0f}Hz vs 后1/3平均 {tail_c:.0f}Hz -> "
              f"{'前高后低=有元音头,边界可切' if head_c > tail_c * 1.25 else '结构均匀或需人耳判断'}")
        print()


if __name__ == "__main__":
    main()
