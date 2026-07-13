#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""鉴定 IPA archive 里的 R/L 备选录音是否为纯持续单音。"""
import os
import subprocess
import wave

import numpy as np

IPA = "/private/tmp/claude-502/-Users-xuxin-Desktop-Claude-Code/181d6b6e-e0b5-4a24-bb4d-afa79cde22bf/scratchpad/ipa-audio/ipa_audio/consonants/archive"
CANDS = [
    ("R候选-卷舌近音2", "Retroflex_Approximant2.oga.mp3"),
    ("R候选-龈后近音",  "Postalveolar_approximant.ogg.mp3"),
    ("L候选-软颚化边音", "Velarized_alveolar_lateral_approximant.ogg.mp3"),
]
SR = 16000


def segments(x):
    hop = int(0.010 * SR)
    n = len(x) // hop
    rms = np.array([np.sqrt(np.mean(x[i*hop:(i+1)*hop] ** 2)) for i in range(n)])
    peak = rms.max() or 1
    act = rms > 0.06 * peak
    segs, i = [], 0
    while i < n:
        if act[i]:
            j, gap = i, 0
            while j < n and gap < 15:
                gap = gap + 1 if not act[j] else 0
                j += 1
            segs.append((i * 10, (j - gap) * 10))
            i = j
        else:
            i += 1
    return segs


def main():
    from faster_whisper import WhisperModel
    from allosaurus.app import read_recognizer
    wh = WhisperModel("large-v3", device="cpu", compute_type="int8")
    al = read_recognizer()
    print(f"{'候选':<12} {'段数':>3} {'各段ms':<16} whisper | allosaurus")
    print("-" * 68)
    for label, fname in CANDS:
        path = os.path.join(IPA, fname)
        if not os.path.exists(path):
            print(f"{label:<12} 文件缺失")
            continue
        wav = f"/tmp/qa_ar_{label}.wav"
        subprocess.run(["afconvert", path, wav, "-f", "WAVE", "-d", f"LEI16@{SR}", "-c", "1"],
                       check=True, capture_output=True)
        with wave.open(wav, "rb") as w:
            x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float64)
        segs = segments(x)
        seginfo = " ".join(str(b - a) for a, b in segs[:6])
        s, _ = wh.transcribe(wav, language="en", beam_size=5, temperature=0.0,
                             condition_on_previous_text=False, without_timestamps=True)
        heard = " ".join(t.text.strip() for t in s).strip() or "(空)"
        try:
            phones = al.recognize(wav, "eng") or "(空)"
        except Exception as e:
            phones = f"失败:{e}"
        os.remove(wav)
        print(f"{label:<12} {len(segs):>3} {seginfo:<16} {heard} | {phones}")


if __name__ == "__main__":
    main()
