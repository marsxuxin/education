#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""老板语音样本分析：全文带时间戳听写（中英混合）+ 分段音素识别。

用途：老板口述发音标准（"这是L的发音…示范…"），本脚本解析出
每个声音段的位置、时长、音素内容，为后续按谱合成提供依据。
用法：python3 analyze_boss_sample.py <音频文件>
"""
import os
import subprocess
import sys
import wave

import numpy as np

SR = 16000


def main():
    src = sys.argv[1]
    wav = src + ".analysis.wav"
    subprocess.run(["afconvert", src, wav, "-f", "WAVE", "-d", f"LEI16@{SR}", "-c", "1"],
                   check=True, capture_output=True)

    from faster_whisper import WhisperModel
    from allosaurus.app import read_recognizer
    wh = WhisperModel("large-v3", device="cpu", compute_type="int8")
    al = read_recognizer()

    print("== 全文听写（带时间戳，自动识别中英）==")
    segs, info = wh.transcribe(wav, beam_size=5, temperature=0.0,
                               condition_on_previous_text=False, word_timestamps=False)
    for s in segs:
        print(f"  [{s.start:6.2f}-{s.end:6.2f}] {s.text.strip()}")
    print(f"  (整体语言判定: {info.language}, 置信 {info.language_probability:.2f})")

    print("\n== 声音段切分 + 逐段音素识别 ==")
    # 容错读取：afconvert 可能输出 WAVE_FORMAT_EXTENSIBLE(65534)，标准 wave 模块不认，
    # 直接定位 data 块按 int16 解析（转换参数固定为 LEI16 mono，安全）
    raw = open(wav, "rb").read()
    di = raw.find(b"data")
    size = int.from_bytes(raw[di+4:di+8], "little")
    x = np.frombuffer(raw[di+8:di+8+size], dtype=np.int16).astype(np.float64)
    hop = int(0.010 * SR)
    n = len(x) // hop
    rms = np.array([np.sqrt(np.mean(x[i*hop:(i+1)*hop] ** 2)) for i in range(n)])
    peak = rms.max() or 1
    act = rms > 0.08 * peak
    bounds, i = [], 0
    while i < n:
        if act[i]:
            j, gap = i, 0
            while j < n and gap < 35:      # 350ms 静默为段界
                gap = gap + 1 if not act[j] else 0
                j += 1
            bounds.append((i, j - gap))
            i = j
        else:
            i += 1
    for k, (a, b) in enumerate(bounds):
        s0 = max(0, a * hop - int(0.05 * SR))
        s1 = min(len(x), b * hop + int(0.05 * SR))
        seg = x[s0:s1]
        segwav = f"{wav}.seg{k}.wav"
        with wave.open(segwav, "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(SR)
            w.writeframes(np.clip(seg, -32767, 32767).astype(np.int16).tobytes())
        try:
            phones = al.recognize(segwav, "eng") or "(空)"
        except Exception as e:
            phones = f"失败:{e}"
        os.remove(segwav)
        print(f"  段{k}: {a*10/1000:6.2f}-{b*10/1000:6.2f}s ({(b-a)*10:4d}ms)  音素: {phones}")

    os.remove(wav)


if __name__ == "__main__":
    main()
