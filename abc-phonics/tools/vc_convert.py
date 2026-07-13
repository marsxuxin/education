#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""声音转换：老板的 L/R 示范 -> 游戏老师的女声音色（发音不动，只换声带）。

OpenVoice V2 ToneColorConverter，CPU 推理。在 kvenv(py3.12) 运行。
"""
import os

import torch

# torch>=2.6 默认 weights_only=True 会拒载旧式 checkpoint，这里放开（模型来自官方 HF 仓库）
_orig_load = torch.load
def _load(*a, **k):
    k.setdefault("weights_only", False)
    return _orig_load(*a, **k)
torch.load = _load

from huggingface_hub import hf_hub_download

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAND = os.path.join(ROOT, "candidates")
SAMPLE = os.environ["VC_SAMPLE"]   # 源说话人的整段录音路径（用于提取源音色特征）

SOURCES = [
    ("boss-L-3.wav", "vc-L-a.wav"),
    ("boss-L-5.wav", "vc-L-b.wav"),
    ("boss-R-3.wav", "vc-R-a.wav"),
    ("boss-R-2.wav", "vc-R-b.wav"),
]


def main():
    import subprocess
    cfg = hf_hub_download("myshell-ai/OpenVoiceV2", "converter/config.json")
    ckpt = hf_hub_download("myshell-ai/OpenVoiceV2", "converter/checkpoint.pth")
    from openvoice.api import ToneColorConverter
    tcc = ToneColorConverter(cfg, device="cpu")
    tcc.load_ckpt(ckpt)

    # 源音色特征：用老板整段 12s 录音（比 0.3s 小段稳）；目标音色：老师参考
    full_wav = os.path.join(CAND, "boss-full.wav")
    subprocess.run(["afconvert", SAMPLE, full_wav, "-f", "WAVE", "-d", "LEI16@22050", "-c", "1"],
                   check=True, capture_output=True)
    src_se = tcc.extract_se(full_wav)
    tgt_se = tcc.extract_se(os.path.join(CAND, "teacher-ref.wav"))

    for src_name, out_name in SOURCES:
        src = os.path.join(CAND, src_name)
        out = os.path.join(CAND, out_name)
        if not os.path.exists(src):
            print(f"缺 {src_name}，跳过")
            continue
        tcc.convert(audio_src_path=src, src_se=src_se, tgt_se=tgt_se, output_path=out)
        print(f"{src_name} -> {out_name} ok")


if __name__ == "__main__":
    main()
