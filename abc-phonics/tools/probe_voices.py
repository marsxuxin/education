#!/usr/bin/env python3
"""探测各语音对音标输入/拟声词的支持情况。

原理：用 afinfo 读取生成音频的时长。
- 若语音支持 [[inpt PHON]] 音标输入，单个音标的音频应当很短(<1s)；
  若不支持，语音会把标记文本整句念出来，时长会明显偏长(>1.5s)。
- 拟声词(如 sss/mmm)若被当作字母逐个拼读，时长也会偏长。
"""
import subprocess
import re
import os
import tempfile

TESTS = [
    # (voice, label, text)
    ("Fred",     "PHON:AE(短a)",      "[[inpt PHON]]1AE[[inpt TEXT]]"),
    ("Fred",     "PHON:man",          "[[inpt PHON]]m1AEn[[inpt TEXT]]"),
    ("Fred",     "PHON:AE,AE",        "[[inpt PHON]]1AE, 1AE.[[inpt TEXT]]"),
    ("Fred",     "PHON:n持续",        "[[inpt PHON]]nnn[[inpt TEXT]]"),
    ("Fred",     "PHON:IH(短i)",      "[[inpt PHON]]1IH[[inpt TEXT]]"),
    ("Samantha", "PHON:AE(短a)",      "[[inpt PHON]]1AE[[inpt TEXT]]"),
    ("Samantha", "PHON:man",          "[[inpt PHON]]m1AEn[[inpt TEXT]]"),
    ("Samantha", "词:cake",           "cake"),
    ("Samantha", "词:apple",          "apple"),
    ("Samantha", "拟:shh",            "shh"),
    ("Samantha", "拟:mmm",            "mmm"),
    ("Samantha", "拟:sss",            "sss"),
    ("Samantha", "拟:zzz",            "zzz"),
    ("Samantha", "拟:nnn",            "nnn"),
    ("Samantha", "拟:ay",             "ay"),
    ("Samantha", "拟:ee",             "ee"),
    ("Samantha", "拟:ooh",            "ooh"),
    ("Samantha", "拟:ah",             "ah"),
    ("Samantha", "拟:uh",             "uh"),
    ("Samantha", "拟:oh",             "oh"),
    ("Samantha", "拟:eye",            "eye"),
    ("Samantha", "拟:er",             "er"),
    ("Samantha", "拟:arr",            "arr"),
    ("Samantha", "拟:ow",             "ow"),
    ("Samantha", "拟:buh",            "buh"),
    ("Samantha", "拟:kuh",            "kuh"),
    ("Tingting", "中:真棒",           "真棒！"),
]

def duration_of(path: str) -> float:
    out = subprocess.run(["afinfo", path], capture_output=True, text=True).stdout
    m = re.search(r"estimated duration:\s*([\d.]+)", out)
    return float(m.group(1)) if m else -1.0

def main():
    tmpdir = tempfile.mkdtemp(prefix="voiceprobe_")
    print(f"{'voice':<10} {'label':<16} {'dur(s)':>7}  verdict")
    for voice, label, text in TESTS:
        aiff = os.path.join(tmpdir, "t.aiff")
        r = subprocess.run(["say", "-v", voice, "-o", aiff, text],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print(f"{voice:<10} {label:<16} {'FAIL':>7}  {r.stderr.strip()[:60]}")
            continue
        dur = duration_of(aiff)
        verdict = "短音✓" if dur < 1.0 else ("可疑(偏长,可能在拼读)" if dur < 2.0 else "不支持(整句念标记)")
        print(f"{voice:<10} {label:<16} {dur:>7.2f}  {verdict}")
        os.remove(aiff)

    # 顺带验证 aiff -> m4a (AAC) 转码管线
    aiff = os.path.join(tmpdir, "conv.aiff")
    m4a = os.path.join(tmpdir, "conv.m4a")
    subprocess.run(["say", "-v", "Samantha", "-o", aiff, "cake"], check=True)
    r = subprocess.run(["afconvert", aiff, m4a, "-f", "m4af", "-d", "aac", "-b", "32000", "-c", "1"],
                       capture_output=True, text=True)
    if r.returncode == 0:
        size = os.path.getsize(m4a)
        print(f"\nafconvert m4a 转码 OK, cake.m4a = {size} bytes")
    else:
        print(f"\nafconvert 失败: {r.stderr[:200]}")

if __name__ == "__main__":
    main()
