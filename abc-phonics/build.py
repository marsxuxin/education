#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ABC 发音乐园 - 构建脚本

流程：
1. 从 data.py 收集所有需要的音频（字母名/单音示范/单词常速+慢速/中文语音）
2. 普通条目：say 合成 -> afconvert 压成 mono 32kbps AAC(m4a)，带缓存
   真人录音条目（demo 形如 "rec:文件名"）：取 recordings/文件名.mp3，
   只做「去首尾静音 + 峰值音量归一」，不对声音内容本身做任何加工
3. 全部 base64 内嵌进 template.html，输出 dist/index.html（单文件、可离线）
4. 打印体检表：真人录音显示有效音长度；合成音显示时长（过长=可疑拼读）
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
REC = os.path.join(ROOT, "recordings")
VOICE_EN = "Samantha"
VOICE_ZH = "Tingting"
SLOW_RATE = 105
SR = 22050


def run(cmd):
    subprocess.run(cmd, check=True, capture_output=True)


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


def trim_and_normalize(src_any, out_wav):
    """去首尾静音（只删无声的空气，不碰声音内容）+ 峰值归一。返回有效音长度 ms。"""
    tmp = out_wav + ".raw.wav"
    run(["afconvert", src_any, tmp, "-f", "WAVE", "-d", f"LEI16@{SR}", "-c", "1"])
    x = read_wav(tmp)
    os.remove(tmp)
    hop = int(0.010 * SR)
    n = len(x) // hop
    rms = np.array([np.sqrt(np.mean(x[i*hop:(i+1)*hop] ** 2)) for i in range(n)])
    peak = rms.max() or 1
    active = rms > 0.04 * peak
    # 合并活动帧为段（间隔<150ms 算同段），取最长段——排除孤立的杂音点
    segs, i = [], 0
    while i < n:
        if active[i]:
            j, gap = i, 0
            while j < n and gap < 15:
                gap = gap + 1 if not active[j] else 0
                j += 1
            segs.append((i, j - gap))
            i = j
        else:
            i += 1
    if not segs:
        raise RuntimeError(f"{src_any}: 整条无声")
    a0, a1 = max(segs, key=lambda s: s[1] - s[0])
    start = max(0, a0 * hop - int(0.06 * SR))
    end = min(len(x), a1 * hop + int(0.12 * SR))
    seg = x[start:end].copy()
    seg *= (0.6 * 32767) / (np.abs(seg).max() or 1)
    write_wav(out_wav, seg)
    return (a1 - a0) * 10


def make_clip(spec):
    """生成一个条目，返回 (m4a路径, 有效音长度ms或None)。spec=(voice,text,rate)"""
    voice, text, rate = spec
    if text.startswith("rec:"):
        src = os.path.join(REC, text[4:] + ".mp3")
        if not os.path.exists(src):
            src = os.path.join(REC, text[4:] + ".wav")
        if not os.path.exists(src):
            raise RuntimeError(f"缺少录音文件: {src}")
        sig = hashlib.md5(open(src, "rb").read()).hexdigest()[:12]
        h = hashlib.md5(f"v4b|rec|{sig}".encode()).hexdigest()
        m4a = os.path.join(CACHE, h + ".m4a")
        meta = m4a + ".ms"
        if not os.path.exists(m4a):
            wav = m4a + ".trim.wav"
            ms = trim_and_normalize(src, wav)
            run(["afconvert", wav, m4a, "-f", "m4af", "-d", "aac", "-b", "32000", "-c", "1"])
            os.remove(wav)
            open(meta, "w").write(str(ms))
        ms = float(open(meta).read()) if os.path.exists(meta) else None
        return m4a, ms
    h = hashlib.md5(f"v4|{voice}|{rate}|{text}".encode()).hexdigest()
    m4a = os.path.join(CACHE, h + ".m4a")
    if not os.path.exists(m4a):
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
        m4a, ms = make_clip(spec)
        raw = open(m4a, "rb").read()
        total += len(raw)
        audio_map[key] = "data:audio/mp4;base64," + base64.b64encode(raw).decode()
        if key.startswith("d:"):
            demo_report.append((spec[1], ms, duration_of(m4a)))
        if (i + 1) % 80 == 0:
            print(f"  …{i + 1}/{len(tasks)}")

    print("\n== 单音示范体检 ==")
    bad = 0
    n_rec = 0
    for text, ms, dur in sorted(demo_report, key=lambda x: x[0]):
        if text.startswith("rec:"):
            n_rec += 1
            print(f"  [真人] {text:<26} 有效音 {ms:5.0f}ms")
        else:
            flag = "  ⚠️可疑" if dur > 1.2 else ""
            bad += 1 if dur > 1.2 else 0
            print(f"  [合成] {text:<26} {dur:5.2f}s{flag}")
    print(f"体检结论: {len(demo_report)} 个示范音（真人 {n_rec} / 合成 {len(demo_report)-n_rec}），{bad} 个可疑")

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
