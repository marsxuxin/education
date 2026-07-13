#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""按老板语音样本（ɻ o）微调 R：补合成候选，与既有候选一起备比对。"""
import os

import numpy as np
import soundfile as sf
import torch
from huggingface_hub import hf_hub_download

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "candidates")
VOICE = "af_heart"
CANDS = [("R-ro", "ɹɔ", 1.0), ("R-roh", "ɹɔʊ", 1.0), ("R-rwo9", "ɹwɔ", 0.9)]


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
        sf.write(os.path.join(OUT, f"kk-{name}.wav"), audio, 24000)
        print(f"{name} <{ph}> ok")


if __name__ == "__main__":
    main()
