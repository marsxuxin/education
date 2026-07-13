#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kokoro 第二轮：用长音符 ː 表达持续辅音（音标体系的正规写法）。"""
import os

import numpy as np
import soundfile as sf
import torch
from huggingface_hub import hf_hub_download

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "candidates")
VOICE = "af_heart"

CANDS = {
    "l2": ["lː", "lːː", "lːːː"],
    "r2": ["ɹː", "ɹːː", "ɹːːː"],
    "n2": ["nː", "nːː", "nːːː"],
    "v2": ["vː", "vːː", "vːːː"],
}


def main():
    os.makedirs(OUT, exist_ok=True)
    from kokoro import KModel
    model = KModel().eval()
    pack = torch.load(hf_hub_download("hexgrad/Kokoro-82M", f"voices/{VOICE}.pt"),
                      weights_only=True)
    for sound, plist in CANDS.items():
        for ph in plist:
            try:
                ref_s = pack[len(ph) - 1]
                with torch.no_grad():
                    audio = model(ph, ref_s, speed=0.7)
                audio = audio.numpy() if torch.is_tensor(audio) else np.asarray(audio)
            except Exception as e:
                print(f"{sound} <{ph}> 失败: {type(e).__name__}: {e}")
                continue
            path = os.path.join(OUT, f"kk-{sound}-{len(ph)}.wav")
            sf.write(path, audio, 24000)
            print(f"{sound} <{ph}> -> kk-{sound}-{len(ph)}.wav ({len(audio)/24000:.2f}s)")


if __name__ == "__main__":
    main()
