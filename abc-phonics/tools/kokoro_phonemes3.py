#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kokoro 第三轮：长辅音+轻尾音结构（老板验收通过的 buh/kah 同款结构）。"""
import os

import numpy as np
import soundfile as sf
import torch
from huggingface_hub import hf_hub_download

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "candidates")
VOICE = "af_heart"

CANDS = [
    ("l3-a", "lə"), ("l3-b", "lːə"), ("l3-c", "lːːə"),
    ("r3-a", "ɹə"), ("r3-b", "ɹːə"), ("r3-c", "ɹːːə"),
    ("v3-a", "və"), ("v3-b", "vːə"), ("v3-c", "vːːə"),
    ("n3-a", "nə"), ("n3-b", "nːə"),
]


def main():
    os.makedirs(OUT, exist_ok=True)
    from kokoro import KModel
    model = KModel().eval()
    pack = torch.load(hf_hub_download("hexgrad/Kokoro-82M", f"voices/{VOICE}.pt"),
                      weights_only=True)
    for name, ph in CANDS:
        try:
            ref_s = pack[len(ph) - 1]
            with torch.no_grad():
                audio = model(ph, ref_s, speed=0.75)
            audio = audio.numpy() if torch.is_tensor(audio) else np.asarray(audio)
        except Exception as e:
            print(f"{name} <{ph}> 失败: {type(e).__name__}: {e}")
            continue
        path = os.path.join(OUT, f"kk-{name}.wav")
        sf.write(path, audio, 24000)
        print(f"{name} <{ph}> -> kk-{name}.wav ({len(audio)/24000:.2f}s)")


if __name__ == "__main__":
    main()
