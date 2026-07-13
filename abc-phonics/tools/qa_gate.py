#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""出厂质检门禁：对 data.py 引用的每一条单音示范做双引擎机器听审。

引擎：
1. faster-whisper large-v3 —— 顶配听写（听成什么词/什么音）
2. allosaurus —— 音素级识别（听出 IPA 音素序列）
3. 浊音占比 —— 区分清/浊（th 清浊对、s/z 这类靠这个铁证）

结论仅供人工定夺；真人录音的第一保证是来源（美国教师教学录音），
机器听审用于抓"文件装错/映射错/内容异常"这类系统性错误。
"""
import os
import subprocess
import sys
import wave

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REC = os.path.join(ROOT, "recordings")
sys.path.insert(0, ROOT)
from data import LETTERS, COMBOS  # noqa: E402

SR = 16000


def to_wav(src, dst):
    subprocess.run(["afconvert", src, dst, "-f", "WAVE", "-d", f"LEI16@{SR}", "-c", "1"],
                   check=True, capture_output=True)


def voiced_fraction(wav_path):
    """活动帧中「高能量+低过零率(周期性浊声)」的占比。"""
    with wave.open(wav_path, "rb") as w:
        x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float64)
    hop = int(0.010 * SR)
    n = len(x) // hop
    if n == 0:
        return 0.0
    rms = np.array([np.sqrt(np.mean(x[i*hop:(i+1)*hop] ** 2)) for i in range(n)])
    zcr = np.array([np.mean(np.abs(np.diff(np.sign(x[i*hop:(i+1)*hop])))) / 2 for i in range(n)])
    peak = rms.max() or 1
    act = rms > 0.15 * peak
    if act.sum() == 0:
        return 0.0
    voiced = act & (zcr < 0.12)
    return float(voiced.sum()) / float(act.sum())


def main():
    from faster_whisper import WhisperModel
    from allosaurus.app import read_recognizer
    print("加载引擎…")
    wh = WhisperModel("large-v3", device="cpu", compute_type="int8")
    al = read_recognizer()

    # 收集 demo -> 所属(单元/音标) 映射
    demos = {}
    for u in LETTERS + COMBOS:
        for s in u["sounds"]:
            demos.setdefault(s["demo"], []).append(f"{u['letter']}{s['ipa']}")

    print(f"{'目标':<26} {'示范':<26} {'浊比':>4}  whisper大模型听到 | allosaurus音素")
    print("-" * 100)
    for demo, owners in sorted(demos.items()):
        if demo.startswith("rec:"):
            src = os.path.join(REC, demo[4:] + ".mp3")
        else:
            # 合成条目：现场生成
            src = f"/tmp/qa_{demo}.aiff"
            subprocess.run(["say", "-v", "Samantha", "-o", src, demo],
                           check=True, capture_output=True)
        wav = src + ".qa.wav"
        to_wav(src, wav)
        segs, _ = wh.transcribe(wav, language="en", beam_size=5, temperature=0.0,
                                condition_on_previous_text=False, without_timestamps=True)
        heard = " ".join(s.text.strip() for s in segs).strip() or "(空)"
        try:
            phones = al.recognize(wav, "eng") or "(空)"
        except Exception as e:
            phones = f"失败:{e}"
        vf = voiced_fraction(wav)
        os.remove(wav)
        own = ",".join(owners[:3])
        print(f"{own:<26} {demo:<26} {vf:>4.0%}  {heard} | {phones}")


if __name__ == "__main__":
    main()
