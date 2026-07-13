#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""示范音机器试听：每个音生成多个候选拟声词，用 faster-whisper 听写，
根据"机器听到了什么"来判断哪个候选真的发出了目标音。

判读逻辑（人工最终定夺，脚本只提供证据）：
- /eɪ/ 候选 "ay" 若被听成 "I/eye/aye" => 它实际发的是 /aɪ/，淘汰；
- 候选 "A" 被听成 "a/A/hey" => 发的是字母名 /eɪ/，正确；
- 嘶音类("sss")若被听成 "S"(字母名 es) => 带了元音头，可疑。
"""
import os
import subprocess
import tempfile

from faster_whisper import WhisperModel

VOICE = "Samantha"

# ipa -> 候选拟声词列表（第一个是当前线上版本）
CANDIDATES = {
    "/eɪ/ 字母音A": ["ay", "A", "hey"],
    "/iː/ 字母音E": ["ee", "E"],
    "/aɪ/ 字母音I": ["eye", "I"],
    "/oʊ/ 字母音O": ["oh", "O"],
    "/juː/字母音U": ["you", "U"],
    "/æ/ 短a":      ["at"],
    "/e/ 短e":      ["Ed", "egg"],
    "/ɪ/ 短i":      ["it"],
    "/ɑ/ 短o":      ["ah", "aw"],
    "/ʌ/ 短u":      ["uh"],
    "/ʊ/ 短oo":     ["look"],
    "/uː/ 长oo":    ["ooh", "oo"],
    "/k/":  ["kuh", "cuh", "kah", "keh", "ka"],
    "/s/":  ["sss", "ss", "ssss", "s"],
    "/z/":  ["zzz", "zz"],
    "/f/":  ["fff", "ff", "fuh"],
    "/v/":  ["vvv", "vuh"],
    "/m/":  ["mmm", "mm"],
    "/n/":  ["nnn", "nn"],
    "/l/":  ["lll", "luh", "la"],
    "/r/":  ["rrr", "ruh", "rah"],
    "/h/":  ["huh", "hah", "ha"],
    "/w/":  ["wuh", "wah", "wa"],
    "/j/":  ["yuh", "yah", "ya"],
    "/b/":  ["buh", "bah", "ba"],
    "/d/":  ["duh", "dah", "da"],
    "/g/":  ["guh", "gah", "ga"],
    "/p/":  ["puh", "pah", "pa"],
    "/t/":  ["tuh", "tah", "ta"],
    "/tʃ/": ["chuh", "cha", "chah"],
    "/dʒ/": ["juh", "jah", "ja"],
    "/ʃ/":  ["shh", "sh", "shhh"],
    "/θ/":  ["thh"],
    "/ð/":  ["the", "thuh"],
    "/ŋ/":  ["ing"],
    "/kw/": ["kwuh", "qua", "kwah"],
    "/ks/": ["ox", "ks"],
    "/ɑr/": ["arr", "ar"],
    "/ɔr/": ["or"],
    "/ər/": ["er"],
    "/aʊ/": ["ow"],
}

def synth_wav(text, outdir):
    aiff = os.path.join(outdir, "t.aiff")
    wav = os.path.join(outdir, "t.wav")
    subprocess.run(["say", "-v", VOICE, "-o", aiff, text], check=True, capture_output=True)
    subprocess.run(["afconvert", aiff, wav, "-f", "WAVE", "-d", "LEI16@16000", "-c", "1"],
                   check=True, capture_output=True)
    return wav

def main():
    print("加载 whisper base.en 模型…")
    model = WhisperModel("base.en", device="cpu", compute_type="int8")
    tmpdir = tempfile.mkdtemp(prefix="demo_audit_")
    print(f"{'音':<12} {'候选':<8} {'机器听到':<24}")
    print("-" * 50)
    for ipa, cands in CANDIDATES.items():
        for c in cands:
            wav = synth_wav(c, tmpdir)
            segments, _info = model.transcribe(
                wav, language="en", beam_size=5, temperature=0.0,
                condition_on_previous_text=False, without_timestamps=True)
            heard = " ".join(s.text.strip() for s in segments).strip() or "(空)"
            print(f"{ipa:<12} {c:<8} {heard:<24}")
        print("-" * 50)

if __name__ == "__main__":
    main()
