#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""L/R 终极定制：按老板给的目标音（L≈拼音le轻声, R≈拼音ruo轻声）生成候选。

Kokoro 音标直出（本脚本，需 kvenv py3.12）+ Samantha 拟声词（qa 阶段一并生成）。
"""
import os

import numpy as np
import soundfile as sf
import torch
from huggingface_hub import hf_hub_download

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "candidates")
VOICE = "af_heart"

# L 目标 lə（勒轻声）；R 目标 ɹwɔ/ɹʊ（若/窝轻声）
CANDS = [
    ("L-la10", "lə", 1.0),
    ("L-la09", "lə", 0.9),
    ("L-lax",  "lʌ", 1.0),
    ("R-ru10", "ɹʊ", 1.0),
    ("R-rua",  "ɹuə", 1.0),
    ("R-rwo",  "ɹwɔ", 1.0),
    ("R-row",  "ɹoʊ", 1.0),
    ("R-re10", "ɹə", 1.0),
]


def main():
    os.makedirs(OUT, exist_ok=True)
    from kokoro import KModel
    model = KModel().eval()
    pack = torch.load(hf_hub_download("hexgrad/Kokoro-82M", f"voices/{VOICE}.pt"),
                      weights_only=True)
    for name, ph, speed in CANDS:
        try:
            ref_s = pack[len(ph) - 1]
            with torch.no_grad():
                audio = model(ph, ref_s, speed=speed)
            audio = audio.numpy() if torch.is_tensor(audio) else np.asarray(audio)
        except Exception as e:
            print(f"{name} <{ph}> 失败: {type(e).__name__}: {e}")
            continue
        path = os.path.join(OUT, f"kk-{name}.wav")
        sf.write(path, audio, 24000)
        print(f"{name} <{ph}> speed={speed} -> kk-{name}.wav ({len(audio)/24000:.2f}s)")


if __name__ == "__main__":
    main()
