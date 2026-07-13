#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ABC 发音乐园 - 构建脚本

流程：
1. 从 data.py 收集所有需要的音频（字母名/单音示范/单词常速+慢速/中文语音）
2. 用 say 生成 aiff -> afconvert 压成 mono 32kbps AAC(m4a)，带缓存
3. 全部 base64 内嵌进 template.html，输出 dist/index.html（单文件、可离线）
4. 打印单音示范的时长体检表（时长异常 = 可能被逐字母拼读，需要换拟声词）
"""
import base64
import hashlib
import json
import os
import re
import subprocess
import sys

from data import LETTERS, COMBOS, CONFUSION_PAIRS, ZH_CLIPS, STICKERS

ROOT = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(ROOT, "audio_cache")
DIST = os.path.join(ROOT, "dist")
VOICE_EN = "Samantha"
VOICE_ZH = "Tingting"
SLOW_RATE = 105


def synth(voice, text, rate=None):
    """生成一段语音，返回缓存的 m4a 路径（按 voice|rate|text 哈希缓存）。"""
    key = hashlib.md5(f"{voice}|{rate}|{text}".encode()).hexdigest()
    m4a = os.path.join(CACHE, key + ".m4a")
    if os.path.exists(m4a):
        return m4a
    aiff = m4a + ".tmp.aiff"
    cmd = ["say", "-v", voice, "-o", aiff]
    if rate:
        cmd += ["-r", str(rate)]
    cmd.append(text)
    subprocess.run(cmd, check=True, capture_output=True)
    subprocess.run(
        ["afconvert", aiff, m4a, "-f", "m4af", "-d", "aac", "-b", "32000", "-c", "1"],
        check=True, capture_output=True)
    os.remove(aiff)
    return m4a


def duration_of(path):
    out = subprocess.run(["afinfo", path], capture_output=True, text=True).stdout
    m = re.search(r"estimated duration:\s*([\d.]+)", out)
    return float(m.group(1)) if m else -1.0


def collect_tasks():
    """key -> (voice, text, rate)。key 约定: L:字母名 d:单音示范 w:常速词 s:慢速词 z:中文"""
    tasks = {}
    units = LETTERS + COMBOS
    for u in LETTERS:
        # 机器试听发现：大写单字母会被念成 "Capital A"，小写才是干净的字母名
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
    for i, (key, (voice, text, rate)) in enumerate(sorted(tasks.items())):
        m4a = synth(voice, text, rate)
        raw = open(m4a, "rb").read()
        total += len(raw)
        audio_map[key] = "data:audio/mp4;base64," + base64.b64encode(raw).decode()
        if key.startswith("d:"):
            demo_report.append((text, duration_of(m4a)))
        if (i + 1) % 80 == 0:
            print(f"  …{i + 1}/{len(tasks)}")

    print(f"\n== 单音示范体检（>1.2s 视为可疑，可能在拼读字母）==")
    bad = 0
    for text, dur in sorted(demo_report, key=lambda x: -x[1]):
        flag = "  ⚠️可疑" if dur > 1.2 else ""
        if flag:
            bad += 1
        print(f"  {text:<8} {dur:5.2f}s{flag}")
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
