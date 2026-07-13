#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""L/R/N/V 第三货源鉴定：SoundDino vs ShowAndTellLetter。
标准：单段(或纯音重复)、无元音头（allosaurus 音素不得以元音开头）、非字母名。"""
import os
import subprocess
import wave

import numpy as np

STAGE = "/private/tmp/claude-502/-Users-xuxin-Desktop-Claude-Code/181d6b6e-e0b5-4a24-bb4d-afa79cde22bf/scratchpad/lrnv"
SOURCES = [
    ("dino-l", "https://sounddino.com/mp3/81/l.mp3"),
    ("dino-r", "https://sounddino.com/mp3/81/r.mp3"),
    ("dino-n", "https://sounddino.com/mp3/81/n.mp3"),
    ("dino-v", "https://sounddino.com/mp3/81/v.mp3"),
    ("dino-m", "https://sounddino.com/mp3/81/m.mp3"),
    ("satl-l", "https://alphabet-sounds.showandtellletter.com/letter/12-1-letter-l-sound.mp3"),
    ("satl-r", "https://alphabet-sounds.showandtellletter.com/letter/18-1-letter-r-sound.mp3"),
    ("satl-n", "https://alphabet-sounds.showandtellletter.com/letter/14-1-letter-n-sound.mp3"),
    ("satl-v", "https://alphabet-sounds.showandtellletter.com/letter/22-1-letter-v-sound.mp3"),
    ("satl-m", "https://alphabet-sounds.showandtellletter.com/letter/13-1-letter-m-sound.mp3"),
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
    os.makedirs(STAGE, exist_ok=True)
    from faster_whisper import WhisperModel
    from allosaurus.app import read_recognizer
    wh = WhisperModel("large-v3", device="cpu", compute_type="int8")
    al = read_recognizer()
    print(f"{'候选':<8} {'段数':>3} {'各段ms':<16} whisper | allosaurus")
    print("-" * 70)
    for name, url in SOURCES:
        mp3 = os.path.join(STAGE, name + ".mp3")
        if not os.path.exists(mp3):
            r = subprocess.run(["curl", "-s", "-L", "-m", "60", "-A", "Mozilla/5.0", "-o", mp3, url],
                               capture_output=True)
            if r.returncode != 0 or not os.path.exists(mp3) or os.path.getsize(mp3) < 500:
                print(f"{name:<8} 下载失败")
                if os.path.exists(mp3):
                    os.remove(mp3)
                continue
        wav = mp3 + ".wav"
        try:
            to_wav(mp3, wav)
        except Exception:
            print(f"{name:<8} 转码失败(可能不是音频)")
            continue
        with wave.open(wav, "rb") as w:
            x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float64)
        segs = segments(x)
        seginfo = " ".join(str(b - a) for a, b in segs[:5])
        s, _ = wh.transcribe(wav, language="en", beam_size=5, temperature=0.0,
                             condition_on_previous_text=False, without_timestamps=True)
        heard = " ".join(t.text.strip() for t in s).strip() or "(空)"
        try:
            phones = al.recognize(wav, "eng") or "(空)"
        except Exception as e:
            phones = f"失败:{e}"
        os.remove(wav)
        print(f"{name:<8} {len(segs):>3} {seginfo:<16} {heard} | {phones}")


if __name__ == "__main__":
    main()
