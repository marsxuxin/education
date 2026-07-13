#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""espeak-ng 音标直出：合成 L/R/N/V 持续单音候选（Kirshenbaum 记法，[[x:]]=拉长）。"""
import os
import subprocess

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "candidates")
ESPEAK = "/opt/homebrew/bin/espeak-ng"

# (输出名, 音标串, 语速)
CANDS = [
    ("es-l-1", "[[l:]]", 80),
    ("es-l-2", "[[l:l:]]", 80),
    ("es-r-1", "[[r:]]", 80),
    ("es-r-2", "[[r:r:]]", 80),
    ("es-r-3", "[[3:]]", 80),      # en-us 的儿化元音 ɝ（美式卷舌感）
    ("es-n-1", "[[n:]]", 80),
    ("es-n-2", "[[n:n:]]", 80),
    ("es-v-1", "[[v:]]", 80),
    ("es-v-2", "[[v:v:]]", 80),
    ("es-m-1", "[[m:]]", 80),      # 对照组
]


def main():
    os.makedirs(OUT, exist_ok=True)
    for name, ph, speed in CANDS:
        wav = os.path.join(OUT, name + ".wav")
        r = subprocess.run([ESPEAK, "-v", "en-us", "-s", str(speed), "-w", wav, ph],
                           capture_output=True, text=True)
        if r.returncode != 0 or not os.path.exists(wav):
            print(f"{name} <{ph}> 失败: {r.stderr.strip()[:60]}")
            continue
        size = os.path.getsize(wav)
        print(f"{name} <{ph}> -> {size} bytes")


if __name__ == "__main__":
    main()
