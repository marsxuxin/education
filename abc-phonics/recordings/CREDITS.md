# 录音来源与授权（recordings/）

## Sound City Reading（alphasounds-*.mp3 / btalpha-*.mp3）

- 来源：Sound City Reading（soundcityreading.net），作者 Kathryn J. Davis，
  美国自然拼读教学项目，由美国教师录制的标准字母/组合音发音。
- 授权条款（摘自官网）：材料可免费下载，供教师、家长、辅导者用于教学；
  **不得从材料的分发中获利**（非商业教育用途）。
- 本项目为免费教育用途，符合上述授权；如未来涉及任何商业化，
  须先联系作者取得书面许可。

## 其他来源

- `custom-l.wav` / `custom-r.wav`：定制示范发音（项目维护者亲自示范并终审），
  经 OpenVoice V2（MIT 许可）音色转换与本库教师声线统一。
- `kokoro-l.wav` / `kokoro-r.wav`：Kokoro-82M 开源神经语音模型（Apache-2.0）
  以音标直接合成的历史版本（已被 custom 版替代，留档）。
- `scrtrim-n.wav` / `scrtrim-v.wav`：由上述 Sound City Reading 的 n / v 录音
  经测量级修剪（去除起始元音段，见 tools/trim_scr_n.py）得到的纯持续音，
  授权同 Sound City Reading 条款。

## 结构与质量校验

- `tools/analyze_recordings.py`：信号分析证明每条录音为单段纯音（不含示例单词）；
- `tools/qa_gate.py`：faster-whisper large-v3 + allosaurus 双引擎机器听审。
