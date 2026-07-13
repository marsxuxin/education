#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""下载真人发音录音（SCR 老师 + Wikimedia 语音学家）并用 allosaurus 逐条鉴定。

输出：每个文件的 音素识别结果 + 时长，供人工定夺最终映射。
下载到 abc-phonics/recordings/（入库文件后续由 build.py 消费）。
"""
import os
import subprocess
import sys

SCR_BASE = "https://www.soundcityreading.net/uploads/3/7/6/1/37611941/"
SCR_FILES = [
    # 26 字母
    "alphasounds-a.mp3", "btalpha-7-a-long.mp3", "btalpha-14-a-dotted.mp3",
    "alphasounds-b.mp3", "alphasounds-c.mp3", "alphasounds-d.mp3",
    "alphasounds-e.mp3", "btalpha-2-e-long.mp3", "alphasounds-f.mp3",
    "alphasounds-g.mp3", "alphasounds-h.mp3", "alphasounds-i.mp3",
    "btalpha-i-long.mp3", "alphasounds-j.mp3", "alphasounds-k.mp3",
    "alphasounds-l.mp3", "alphasounds-m.mp3", "alphasounds-n.mp3",
    "alphasounds-o-sh.mp3", "btalpha-3-o-long.mp3", "btalpha-6-o-dotted.mp3",
    "alphasounds-p-2.mp3", "alphasounds-q.mp3", "alphasounds-r.mp3",
    "alphasounds-s.mp3", "alphasounds-t.mp3", "alphasounds-u-sh.mp3",
    "btalpha-10-u-long.mp3", "btalpha-13-u-dotted.mp3", "alphasounds-v.mp3",
    "alphasounds-w.mp3", "alphasounds-x.mp3", "alphasounds-y.mp3",
    "alphasounds-z.mp3",
    # 组合音
    "btalpha-1-sh.mp3", "btalpha-4-th-soft.mp3", "btalpha-5-th-hard.mp3",
    "btalpha-8-ch.mp3", "btalpha-9-ng.mp3", "btalpha-12-ow.mp3",
]

# 可选：Wikimedia IPA 音频目录（clone github.com/joshstephenson/PhoneticFlashCards 后
# 指向其 ipa_audio/）。评估结论：IPA 辅音是 [ka-aka] 三连示范格式，不适合做孤立音，
# 本项目最终未采用，仅保留对比能力。
IPA_DIR = os.environ.get("IPA_DIR", "")
IPA_FILES = [
    ("vowels/Near-open_front_unrounded_vowel_æ.ogg.mp3", "ipa-ae.mp3"),
    ("vowels/Open-mid_front_unrounded_vowel_ɛ.ogg.mp3", "ipa-eh.mp3"),
    ("vowels/Near-close_near-front_unrounded_vowel_ɪ.ogg.mp3", "ipa-ih.mp3"),
    ("vowels/Open_back_unrounded_vowel_ɑ.ogg.mp3", "ipa-aa.mp3"),
    ("vowels/Close_back_rounded_vowel_u.ogg.mp3", "ipa-uu.mp3"),
    ("vowels/Near-close_near-back_rounded_vowel_ʊ.ogg.mp3", "ipa-uh-short.mp3"),
    ("consonants/Voiceless_dental_fricative_θ.ogg.mp3", "ipa-th-soft.mp3"),
    ("consonants/Voiced_dental_fricative_ð.ogg.mp3", "ipa-th-hard.mp3"),
    ("consonants/Velar_nasal_ŋ.ogg.mp3", "ipa-ng.mp3"),
    ("consonants/Voiceless_velar_plosive_k.ogg.mp3", "ipa-k.mp3"),
    ("consonants/Voiceless_alveolar_sibilant_s.ogg.mp3", "ipa-s.mp3"),
    ("consonants/Voiced_alveolar_plosive_d.ogg.mp3", "ipa-d.mp3"),
]

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REC = os.path.join(ROOT, "recordings")


def sh(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def duration_of(path):
    out = sh(["afinfo", path]).stdout
    for line in out.splitlines():
        if "estimated duration" in line:
            return float(line.split(":")[1].strip().split()[0])
    return -1.0


def main():
    os.makedirs(REC, exist_ok=True)
    # 1. 下载 SCR
    for f in SCR_FILES:
        dst = os.path.join(REC, f)
        if not os.path.exists(dst):
            r = sh(["curl", "-s", "-m", "60", "-o", dst, SCR_BASE + f])
            if r.returncode != 0 or os.path.getsize(dst) < 1000:
                print(f"下载失败: {f}", file=sys.stderr)
                if os.path.exists(dst):
                    os.remove(dst)
    # 2. 拷贝 Wikimedia IPA 精选（可选，仅当设置了 IPA_DIR）
    if IPA_DIR:
        for src, dst_name in IPA_FILES:
            dst = os.path.join(REC, dst_name)
            if not os.path.exists(dst):
                full = os.path.join(IPA_DIR, src)
                if os.path.exists(full):
                    sh(["cp", full, dst])
                else:
                    print(f"缺少 IPA 文件: {src}", file=sys.stderr)

    # 3. allosaurus 逐条鉴定（mp3 -> 16k wav -> 识别）
    from allosaurus.app import read_recognizer
    model = read_recognizer()
    print(f"{'文件':<28} {'时长':>5}  识别出的音素(eng)")
    print("-" * 70)
    for f in sorted(os.listdir(REC)):
        if not f.endswith(".mp3"):
            continue
        path = os.path.join(REC, f)
        wav = path + ".wav"
        sh(["afconvert", path, wav, "-f", "WAVE", "-d", "LEI16@16000", "-c", "1"])
        try:
            phones = model.recognize(wav, "eng")
        except Exception as e:
            phones = f"识别失败: {e}"
        os.remove(wav)
        print(f"{f:<28} {duration_of(path):>4.1f}s  {phones}")


if __name__ == "__main__":
    main()
