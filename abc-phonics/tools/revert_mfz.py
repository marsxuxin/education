#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""恢复被误换的示范音：M/F/Z 回真人版；L/R/N/V 临时回真人版（待老板定最终方案）。"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "data.py")

REPL = [
    ('"demo": "mmm"',  '"demo": "rec:alphasounds-m"'),
    ('"demo": "fff"',  '"demo": "rec:alphasounds-f"'),
    ('"demo": "zzzz"', '"demo": "rec:alphasounds-z"'),   # Z + S/z进阶 共2处
    ('"demo": "lll"',  '"demo": "rec:alphasounds-l"'),
    ('"demo": "rrr"',  '"demo": "rec:alphasounds-r"'),
    ('"demo": "nnn"',  '"demo": "rec:alphasounds-n"'),
    ('"demo": "vvv"',  '"demo": "rec:alphasounds-v"'),
]

s = open(P, encoding="utf-8").read()
for old, new in REPL:
    n = s.count(old)
    s = s.replace(old, new)
    print(f"{old:<18} -> {new}  ({n} 处)")
open(P, "w", encoding="utf-8").write(s)
print("完成")
