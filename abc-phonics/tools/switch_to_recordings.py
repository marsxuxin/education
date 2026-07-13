#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 data.py 的 demo 字段批量切换到 SCR 真人录音（rec:文件名）。"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "data.py")

REPL = [
    ('"demo": "at"',              '"demo": "rec:alphasounds-a"'),
    ('"demo": "a"',               '"demo": "rec:btalpha-7-a-long"'),      # A长音/ai/ay
    ('"demo": "cut:vstop:ball"',  '"demo": "rec:alphasounds-b"'),
    ('"demo": "cut:ustop:cat"',   '"demo": "rec:alphasounds-k"'),         # C/K/ck
    ('"demo": "cut:fric:sun"',    '"demo": "rec:alphasounds-s"'),         # S/C进阶
    ('"demo": "cut:vstop:dog"',   '"demo": "rec:alphasounds-d"'),
    ('"demo": "Ed"',              '"demo": "rec:alphasounds-e"'),
    ('"demo": "ee"',              '"demo": "rec:btalpha-2-e-long"'),      # E长音/Y词尾/ee/ea
    ('"demo": "cut:fric:fish"',   '"demo": "rec:alphasounds-f"'),
    ('"demo": "cut:vstop:goat"',  '"demo": "rec:alphasounds-g"'),
    ('"demo": "hah"',             '"demo": "rec:alphasounds-h"'),
    ('"demo": "it"',              '"demo": "rec:alphasounds-i"'),
    ('"demo": "eye"',             '"demo": "rec:btalpha-i-long"'),        # I长音/Y词尾/igh
    ('"demo": "cut:aff:juice"',   '"demo": "rec:alphasounds-j"'),         # J/G进阶
    ('"demo": "la"',              '"demo": "rec:alphasounds-l"'),
    ('"demo": "mmm"',             '"demo": "rec:alphasounds-m"'),
    ('"demo": "nnn"',             '"demo": "rec:alphasounds-n"'),
    ('"demo": "ah"',              '"demo": "rec:alphasounds-o-sh"'),
    ('"demo": "oh"',              '"demo": "rec:btalpha-3-o-long"'),      # O长音/oa/ow第二音
    ('"demo": "uh"',              '"demo": "rec:alphasounds-u-sh"'),      # U短音/O进阶
    ('"demo": "cut:ustop:pig"',   '"demo": "rec:alphasounds-p-2"'),
    ('"demo": "kwah"',            '"demo": "rec:alphasounds-q"'),
    ('"demo": "rrr"',             '"demo": "rec:alphasounds-r"'),
    ('"demo": "cut:ustop:ten"',   '"demo": "rec:alphasounds-t"'),
    ('"demo": "you"',             '"demo": "rec:btalpha-10-u-long"'),
    ('"demo": "vvv"',             '"demo": "rec:alphasounds-v"'),
    ('"demo": "wah"',             '"demo": "rec:alphasounds-w"'),         # W/wh
    ('"demo": "ox"',              '"demo": "rec:alphasounds-x"'),
    ('"demo": "yah"',             '"demo": "rec:alphasounds-y"'),
    ('"demo": "cut:fric:zoo"',    '"demo": "rec:alphasounds-z"'),         # Z/S进阶
    ('"demo": "shh"',             '"demo": "rec:btalpha-1-sh"'),
    ('"demo": "cut:aff:chair"',   '"demo": "rec:btalpha-8-ch"'),
    ('"demo": "thh"',             '"demo": "rec:btalpha-4-th-soft"'),
    ('"demo": "the"',             '"demo": "rec:btalpha-5-th-hard"'),
    ('"demo": "ing"',             '"demo": "rec:btalpha-9-ng"'),
    ('"demo": "moo"',             '"demo": "rec:btalpha-6-o-dotted"'),
    ('"demo": "look"',            '"demo": "rec:btalpha-13-u-dotted"'),
    ('"demo": "oww"',             '"demo": "rec:btalpha-12-ow"'),
    # 保留合成：ar / or / er（SCR 无单独卷舌音文件）
]

s = open(P, encoding="utf-8").read()
for old, new in REPL:
    n = s.count(old)
    if n == 0:
        print(f"⚠️ 没找到: {old}")
        continue
    s = s.replace(old, new)
    print(f"{old:<34} -> {new}  ({n} 处)")
open(P, "w", encoding="utf-8").write(s)
print("完成")
