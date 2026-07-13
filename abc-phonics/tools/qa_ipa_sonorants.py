#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""鉴定 Wikimedia IPA 库的 L/R/N/V/M 单音：必须是单段纯持续音（无 [aCa] 框架、无元音头）。"""
import os
import subprocess
import wave

import numpy as np

IPA = os.environ.get(
    "IPA_SRC",
    "/private/tmp/claude-502/-Users-xuxin-Desktop-Claude-Code/181d6b6e-e0b5-4a24-bb4d-afa79cde22bf/scratchpad/ipa-audio/ipa_audio")
CANDS = [
    ("L", os.path.join(IPA, "consonants/Voiced_alveolar_lateral_approximant_l.ogg.mp3")),
    ("R", os.path.join(IPA, "consonants/archive/Alveolar_approximant_ɹ.ogg.mp3")),
    ("N", os.path.join(IPA, "consonants/Alveolar_nasal_n.ogg.mp3")),
    ("M", os.path.join(IPA, "consonants/Bilabial_nasal_m.ogg.mp3")),
    ("V", os.path.join(IPA, "consonants/Voiced_labio-dental_fricative_v.ogg.mp3")),
]
SR = 16000


def to_wav(src, dst):
    subprocess.run(["afconvert", src, dst, "-f", "WAVE", "-d", f"LEI16@{SR}", "-c", "1"],
                   check=True, capture_output=True)


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
    print(f"{'音':<3} {'段数':>3} {'各段ms':<14} whisper | allosaurus")
    print("-" * 60)
    for label, path in CANDS:
        wav = f"/tmp/qa_ipa_{label}.wav"
        to_wav(path, wav)
        with wave.open(wav, "rb") as w:
            x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float64)
        segs = segments(x)
        seginfo = " ".join(str(b - a) for a, b in segs)
        s, _ = wh.transcribe(wav, language="en", beam_size=5, temperature=0.0,
                             condition_on_previous_text=False, without_timestamps=True)
        heard = " ".join(t.text.strip() for t in s).strip() or "(空)"
        try:
            phones = al.recognize(wav, "eng") or "(空)"
        except Exception as e:
            phones = f"失败:{e}"
        os.remove(wav)
        print(f"{label:<3} {len(segs):>3} {seginfo:<14} {heard} | {phones}")


if __name__ == "__main__":
    main()
