#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 L/R 试听台：老板原声段 + 女声变调版 + 线上现行版，一页试听。

在 kvenv(py3.12, 含 librosa) 运行。输出路径由环境变量 AUDITION_OUT 指定，
缺省输出到 candidates/试听台.html。
"""
import base64
import io
import os

import librosa
import numpy as np
import soundfile as sf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAND = os.path.join(ROOT, "candidates")
REC = os.path.join(ROOT, "recordings")
OUT_HTML = os.environ.get("AUDITION_OUT", os.path.join(CAND, "试听台.html"))
FEM_STEPS = 4   # 变声：升 4 个半音（男->女声区）

# (编号, 标签, 源文件, 是否变女声[旧版变调,已弃用])
CLIPS = [
    ("L1", "L·你的原声·候选一", os.path.join(CAND, "boss-L-3.wav"), False),
    ("L2", "L·你的原声·候选三", os.path.join(CAND, "boss-L-5.wav"), False),
    ("L3", "L·女声转换版(AI换声带,由候选一)", os.path.join(CAND, "vc-L-a.wav"), False),
    ("L4", "L·女声转换版(AI换声带,由候选三)", os.path.join(CAND, "vc-L-b.wav"), False),
    ("R1", "R·你的原声·候选一", os.path.join(CAND, "boss-R-3.wav"), False),
    ("R2", "R·你的原声·候选二", os.path.join(CAND, "boss-R-2.wav"), False),
    ("R3", "R·女声转换版(AI换声带,由候选一)", os.path.join(CAND, "vc-R-a.wav"), False),
    ("R4", "R·女声转换版(AI换声带,由候选二)", os.path.join(CAND, "vc-R-b.wav"), False),
]


def to_b64_wav(path, femalize):
    y, sr = librosa.load(path, sr=22050, mono=True)
    if femalize:
        y = librosa.effects.pitch_shift(y=y, sr=sr, n_steps=FEM_STEPS)
        peak = np.abs(y).max() or 1
        y = y / peak * 0.7
    buf = io.BytesIO()
    sf.write(buf, y, sr, format="WAV", subtype="PCM_16")
    return base64.b64encode(buf.getvalue()).decode()


def main():
    rows = []
    for cid, label, path, fem in CLIPS:
        if not os.path.exists(path):
            print(f"缺文件跳过: {path}")
            continue
        b64 = to_b64_wav(path, fem)
        rows.append((cid, label, b64))
        print(f"{cid} {label} ok")
    btns = "\n".join(
        f'<button class="c" onclick="p(\'{cid}\')"><b>{cid}</b><span>{label}</span></button>'
        f'<audio id="{cid}" src="data:audio/wav;base64,{b64}"></audio>'
        for cid, label, b64 in rows)
    html = f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>L / R 发音试听台</title><style>
body{{font-family:"PingFang SC",sans-serif;background:#f0f6fc;padding:24px;max-width:560px;margin:0 auto}}
h1{{font-size:22px;color:#33557a}} p{{color:#5b789a;font-weight:bold}}
.c{{display:flex;align-items:center;gap:14px;width:100%;padding:14px 18px;margin:10px 0;
font-size:17px;font-weight:bold;color:#2f3a4f;background:#fff;border:2px solid #cfe3f5;
border-radius:14px;cursor:pointer;text-align:left}}
.c:active{{background:#e3f1ff}} .c b{{font-size:20px;color:#3c6fb2;min-width:36px}}
</style></head><body>
<h1>🔤 L / R 发音试听台</h1>
<p>逐个点击试听，选出 L 和 R 各一个最满意的，把编号告诉小太阳（例如 "L 用 L4，R 用 R3"），确认后才会上线。</p>
{btns}
<script>function p(id){{document.querySelectorAll('audio').forEach(a=>{{a.pause();a.currentTime=0}});document.getElementById(id).play()}}</script>
</body></html>"""
    with open(OUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"\n试听台已生成: {OUT_HTML}")


if __name__ == "__main__":
    main()
