#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""用 Kokoro 神经语音引擎直接从音标合成 L/R/N/V 的持续单音候选。

绕开一切文本前端（不给它会被念成字母名/单词的文本），直连声学模型 KModel，
音素串直接进模型，输出 24kHz wav 到 candidates/。需在 uv 的 py3.12 环境运行。
"""
import os

import numpy as np
import soundfile as sf
import torch
from huggingface_hub import hf_hub_download

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "candidates")
VOICE = "af_heart"   # 美音女声(最高质量评级)

CANDS = {
    "l":  ["l", "ll", "lll", "llll"],
    "r":  ["ɹ", "ɹɹ", "ɹɹɹ", "ɹɹɹɹ"],
    "n":  ["n", "nn", "nnn", "nnnn"],
    "v":  ["v", "vv", "vvv", "vvvv"],
    "m":  ["mmm"],   # 对照组（真人版已合格，用来校准判读标准）
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
                    audio = model(ph, ref_s, speed=0.8)
                audio = audio.numpy() if torch.is_tensor(audio) else np.asarray(audio)
            except Exception as e:
                print(f"{sound} <{ph}> 失败: {type(e).__name__}: {e}")
                continue
            path = os.path.join(OUT, f"kk-{sound}-{len(ph)}.wav")
            sf.write(path, audio, 24000)
            print(f"{sound} <{ph}> -> kk-{sound}-{len(ph)}.wav ({len(audio)/24000:.2f}s)")


if __name__ == "__main__":
    main()
