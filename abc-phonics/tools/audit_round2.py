#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第二轮定向试听：只测第一轮暴露问题的音 + 字母名读法方案。"""
import os
import subprocess
import tempfile

from faster_whisper import WhisperModel

VOICE = "Samantha"

CANDIDATES = {
    "字母名A":  ["a", "A.", "a."],
    "字母名B":  ["b", "B.", "b."],
    "字母名C":  ["c", "C.", "c."],
    "字母名W":  ["w", "W.", "w."],
    "字母名S":  ["s.", "S."],
    "/eɪ/":    ["a", "hey"],
    "/aɪ/":    ["aye", "i"],
    "/ʌ/":     ["up", "uh."],
    "/uː/":    ["oooh", "ooo", "oo."],
    "/s/":     ["sah", "sa", "ss."],
    "/z/":     ["zah", "za", "zz."],
    "/f/":     ["fah", "fa", "ff."],
    "/ər/":    ["err", "er."],
    "/aʊ/":    ["oww", "ouch", "ow."],
    "/h/":     ["hah."],
    "/b/":     ["bah."],
    "/g/":     ["gah."],
    "/p/":     ["pah."],
    "/tʃ/":    ["cha."],
    "/dʒ/":    ["jah."],
    "/kw/":    ["kwah."],
    "/ɑr/":    ["ar."],
    "/k/":     ["kah."],
    "/l/":     ["la."],
    "/w-耳/":  ["wah."],
    "/j-耳/":  ["yah."],
}

def synth_wav(text, outdir):
    aiff = os.path.join(outdir, "t.aiff")
    wav = os.path.join(outdir, "t.wav")
    subprocess.run(["say", "-v", VOICE, "-o", aiff, text], check=True, capture_output=True)
    subprocess.run(["afconvert", aiff, wav, "-f", "WAVE", "-d", "LEI16@16000", "-c", "1"],
                   check=True, capture_output=True)
    return wav

def main():
    model = WhisperModel("base.en", device="cpu", compute_type="int8")
    tmpdir = tempfile.mkdtemp(prefix="demo_audit2_")
    print(f"{'音':<10} {'候选':<8} {'机器听到':<26}")
    print("-" * 48)
    for ipa, cands in CANDIDATES.items():
        for c in cands:
            wav = synth_wav(c, tmpdir)
            segments, _info = model.transcribe(
                wav, language="en", beam_size=5, temperature=0.0,
                condition_on_previous_text=False, without_timestamps=True)
            heard = " ".join(s.text.strip() for s in segments).strip() or "(空)"
            print(f"{ipa:<10} {c:<8} {heard:<26}")
        print("-" * 48)

if __name__ == "__main__":
    main()
