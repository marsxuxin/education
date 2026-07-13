#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测量级修剪：把 SCR 真人 n / v 录音开头的元音段精确剪掉，留纯哼鸣/纯浊擦。

方法：10ms 帧频谱质心+能量扫描，元音段(高质心)→稳态段(低质心)的边界处
切割（边界后再让 20ms 缓冲），5ms 淡入。输出到 candidates/ 供三重鉴定。
"""
import os
import subprocess
import wave

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REC = os.path.join(ROOT, "recordings")
OUT = os.path.join(ROOT, "candidates")
SR = 22050

TARGETS = [("alphasounds-n", "scrtrim-n"), ("alphasounds-v", "scrtrim-v")]


def main():
    os.makedirs(OUT, exist_ok=True)
    for src_name, out_name in TARGETS:
        src = os.path.join(REC, src_name + ".mp3")
        raw = os.path.join(OUT, out_name + ".raw.wav")
        subprocess.run(["afconvert", src, raw, "-f", "WAVE", "-d", f"LEI16@{SR}", "-c", "1"],
                       check=True, capture_output=True)
        with wave.open(raw, "rb") as w:
            x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float64)
        os.remove(raw)
        hop = int(0.010 * SR)
        n = len(x) // hop
        rms = np.zeros(n)
        cen = np.zeros(n)
        for i in range(n):
            f = x[i * hop:(i + 1) * hop]
            rms[i] = np.sqrt(np.mean(f * f))
            spec = np.abs(np.fft.rfft(f * np.hanning(len(f))))
            freqs = np.fft.rfftfreq(len(f), 1 / SR)
            cen[i] = (spec * freqs).sum() / (spec.sum() or 1)
        peak = rms.max() or 1
        act = np.where(rms > 0.08 * peak)[0]
        a0, a1 = act[0], act[-1]
        # 稳态基准 = 有效段后半的质心中位数；从前向后找第一个进入稳态±25%的帧
        steady = np.median(cen[(a0 + a1) // 2: a1])
        cut = a0
        for i in range(a0, (a0 + a1) // 2):
            if abs(cen[i] - steady) < 0.25 * steady:
                cut = i
                break
        cut_sample = cut * hop + int(0.020 * SR)
        seg = x[cut_sample: (a1 + 1) * hop].copy()
        fi = int(0.005 * SR)
        seg[:fi] *= np.linspace(0, 1, fi)
        fo = int(0.030 * SR)
        seg[-fo:] *= np.linspace(1, 0, fo)
        seg *= (0.6 * 32767) / (np.abs(seg).max() or 1)
        pad = np.zeros(int(0.05 * SR))
        outwav = os.path.join(OUT, out_name + ".wav")
        with wave.open(outwav, "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(SR)
            data = np.concatenate([pad, seg, pad])
            w.writeframes(np.clip(data, -32767, 32767).astype(np.int16).tobytes())
        print(f"{src_name}: 有效段 {a0*10}-{a1*10}ms, 元音头切点 {cut*10}ms(+20ms缓冲), "
              f"剪后纯音 {len(seg)/SR*1000:.0f}ms -> {out_name}.wav")


if __name__ == "__main__":
    main()
