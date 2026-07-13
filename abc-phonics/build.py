#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ABC 发音乐园 - 构建脚本

流程：
1. 从 data.py 收集所有需要的音频（字母名/单音示范/单词常速+慢速/中文语音）
2. 普通条目：say 合成 -> afconvert 压成 mono 32kbps AAC(m4a)，带缓存
   剪辑条目（demo 形如 "cut:ustop:cat"）：合成整个单词后做"音头手术"——
   用能量+过零率找到元音起点，把起点之前的辅音音头剪出来，
   得到不带元音的纯辅音示范（k! s~ d! …），解决 TTS 念拟声词必带元音的问题
3. 全部 base64 内嵌进 template.html，输出 dist/index.html（单文件、可离线）
4. 打印体检表：拟声词看时长；剪辑音看剪出长度是否落在该类辅音的合理区间
"""
import base64
import hashlib
import json
import os
import re
import subprocess
import wave

import numpy as np

from data import LETTERS, COMBOS, CONFUSION_PAIRS, ZH_CLIPS, STICKERS

ROOT = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(ROOT, "audio_cache")
DIST = os.path.join(ROOT, "dist")
VOICE_EN = "Samantha"
VOICE_ZH = "Tingting"
SLOW_RATE = 105
SR = 22050

# 剪辑类别 -> (剪出长度合理区间 ms, 结束点相对元音起点的偏移 ms, 尾部淡出 ms)
CUT_KINDS = {
    "ustop": ((30, 200),  -2, 12),   # 清塞音 k p t：留爆破+送气，元音前 2ms 截断
    "vstop": ((25, 140),  25, 15),   # 浊塞音 b d g：爆破很短，带 25ms 元音起振才听得见
    "fric":  ((80, 480),  -5, 30),   # 擦音 s f z：留住整段嘶声
    "aff":   ((60, 400),  -5, 25),   # 塞擦音 ch j：爆破+摩擦整段保留
}


def run(cmd):
    subprocess.run(cmd, check=True, capture_output=True)


def synth_wav(voice, text, wav_path, rate=None):
    aiff = wav_path + ".tmp.aiff"
    cmd = ["say", "-v", voice, "-o", aiff]
    if rate:
        cmd += ["-r", str(rate)]
    cmd.append(text)
    run(cmd)
    run(["afconvert", aiff, wav_path, "-f", "WAVE", "-d", f"LEI16@{SR}", "-c", "1"])
    os.remove(aiff)


def wav_to_m4a(wav_path, m4a_path):
    run(["afconvert", wav_path, m4a_path, "-f", "m4af", "-d", "aac", "-b", "32000", "-c", "1"])


def read_wav(path):
    with wave.open(path, "rb") as w:
        data = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)
    return data.astype(np.float64)


def write_wav(path, samples):
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(np.clip(samples, -32767, 32767).astype(np.int16).tobytes())


def cut_onset(word_wav, out_wav, kind):
    """从单词录音里剪出起始辅音。返回剪出长度(ms)。"""
    (_lo, _hi), end_off_ms, fade_out_ms = CUT_KINDS[kind]
    x = read_wav(word_wav)
    hop, win = int(0.005 * SR), int(0.010 * SR)
    n = max(0, (len(x) - win) // hop)
    rms = np.zeros(n)
    zcr = np.zeros(n)
    for i in range(n):
        f = x[i * hop: i * hop + win]
        rms[i] = np.sqrt(np.mean(f * f))
        zcr[i] = np.mean(np.abs(np.diff(np.sign(f)))) / 2
    peak = rms.max()
    # 声音起点：连续 3 帧能量高于噪底（f 这类弱擦音能量低，阈值放低）
    above = rms > 0.02 * peak
    burst = next((i for i in range(n - 3) if above[i] and above[i + 1] and above[i + 2]), 0)
    # 元音起点：burst 之后第一处 高能量+低过零率（周期性浊声）
    vo = next((i for i in range(burst + 1, n) if rms[i] > 0.35 * peak and zcr[i] < 0.12), None)
    if vo is None:
        raise RuntimeError(f"{word_wav}: 找不到元音起点")
    start = max(0, burst * hop - int(0.005 * SR))
    end = min(len(x), vo * hop + int(end_off_ms / 1000 * SR))
    if end <= start:
        raise RuntimeError(f"{word_wav}: 剪辑区间为空")
    seg = x[start:end].copy()
    fi = min(len(seg), int(0.005 * SR))
    seg[:fi] *= np.linspace(0, 1, fi)
    fo = min(len(seg), int(fade_out_ms / 1000 * SR))
    seg[-fo:] *= np.linspace(1, 0, fo)
    seg *= (0.6 * 32767) / (np.abs(seg).max() or 1)
    pad_h = np.zeros(int(0.05 * SR))
    pad_t = np.zeros(int(0.10 * SR))
    write_wav(out_wav, np.concatenate([pad_h, seg, pad_t]))
    return (end - start) / SR * 1000


def make_clip(spec):
    """生成一个条目，返回 (m4a路径, 剪辑长度ms或None)。spec=(voice,text,rate)"""
    voice, text, rate = spec
    h = hashlib.md5(f"v3|{voice}|{rate}|{text}".encode()).hexdigest()
    m4a = os.path.join(CACHE, h + ".m4a")
    meta = m4a + ".cutms"
    if os.path.exists(m4a):
        cut_ms = float(open(meta).read()) if os.path.exists(meta) else None
        return m4a, cut_ms
    if text.startswith("cut:"):
        _tag, kind, word = text.split(":", 2)
        word_wav = m4a + ".word.wav"
        cut_wav = m4a + ".cut.wav"
        synth_wav(voice, word, word_wav)
        cut_ms = cut_onset(word_wav, cut_wav, kind)
        wav_to_m4a(cut_wav, m4a)
        os.remove(word_wav)
        os.remove(cut_wav)
        open(meta, "w").write(str(cut_ms))
        return m4a, cut_ms
    aiff = m4a + ".tmp.aiff"
    cmd = ["say", "-v", voice, "-o", aiff]
    if rate:
        cmd += ["-r", str(rate)]
    cmd.append(text)
    run(cmd)
    run(["afconvert", aiff, m4a, "-f", "m4af", "-d", "aac", "-b", "32000", "-c", "1"])
    os.remove(aiff)
    return m4a, None


def duration_of(path):
    out = subprocess.run(["afinfo", path], capture_output=True, text=True).stdout
    m = re.search(r"estimated duration:\s*([\d.]+)", out)
    return float(m.group(1)) if m else -1.0


def collect_tasks():
    """key -> (voice, text, rate)。key: L:字母名 d:示范 w:常速词 s:慢速词 z:中文"""
    tasks = {}
    units = LETTERS + COMBOS
    for u in LETTERS:
        # 大写单字母会被念成 "Capital A"，小写才是干净的字母名
        tasks[f"L:{u['letter']}"] = (VOICE_EN, u["letter"].lower(), None)
    for u in units:
        for s in u["sounds"]:
            tasks[f"d:{s['demo']}"] = (VOICE_EN, s["demo"], None)
            for w, _emoji in s["words"]:
                tasks[f"w:{w}"] = (VOICE_EN, w, None)
                tasks[f"s:{w}"] = (VOICE_EN, w, SLOW_RATE)
    for k, text in ZH_CLIPS.items():
        tasks[f"z:{k}"] = (VOICE_ZH, text, None)
    return tasks


def main():
    os.makedirs(CACHE, exist_ok=True)
    os.makedirs(DIST, exist_ok=True)

    tasks = collect_tasks()
    print(f"音频任务共 {len(tasks)} 条，生成中…")
    audio_map, total = {}, 0
    demo_report = []
    for i, (key, spec) in enumerate(sorted(tasks.items())):
        m4a, cut_ms = make_clip(spec)
        raw = open(m4a, "rb").read()
        total += len(raw)
        audio_map[key] = "data:audio/mp4;base64," + base64.b64encode(raw).decode()
        if key.startswith("d:"):
            demo_report.append((spec[1], cut_ms, duration_of(m4a)))
        if (i + 1) % 80 == 0:
            print(f"  …{i + 1}/{len(tasks)}")

    print("\n== 单音示范体检 ==")
    bad = 0
    for text, cut_ms, dur in sorted(demo_report, key=lambda x: x[0]):
        if text.startswith("cut:"):
            kind = text.split(":")[1]
            lo, hi = CUT_KINDS[kind][0]
            ok = lo <= cut_ms <= hi
            flag = "" if ok else "  ⚠️区间外"
            bad += 0 if ok else 1
            print(f"  [剪辑] {text:<18} 剪出 {cut_ms:5.0f}ms (合理 {lo}-{hi}ms){flag}")
        else:
            flag = "  ⚠️可疑" if dur > 1.2 else ""
            bad += 1 if dur > 1.2 else 0
            print(f"  [拟声] {text:<18} {dur:5.2f}s{flag}")
    print(f"体检结论: {len(demo_report)} 个示范音, {bad} 个可疑")

    content = {
        "letters": LETTERS,
        "combos": COMBOS,
        "pairs": CONFUSION_PAIRS,
        "stickers": STICKERS,
    }
    tpl = open(os.path.join(ROOT, "template.html"), encoding="utf-8").read()
    html = tpl.replace("__CONTENT_JSON__", json.dumps(content, ensure_ascii=False, separators=(",", ":")))
    html = html.replace("__AUDIO_JSON__", json.dumps(audio_map, separators=(",", ":")))
    out = os.path.join(DIST, "index.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\n音频原始体积 {total / 1024:.0f} KB, 成品 {os.path.getsize(out) / 1024 / 1024:.2f} MB")
    print(f"输出: {out}")


if __name__ == "__main__":
    main()
