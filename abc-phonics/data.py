# -*- coding: utf-8 -*-
"""ABC 发音乐园 - 内容库（唯一事实来源）

结构说明：
- LETTERS: 26 个字母，每个含 1~3 种常见发音(sounds)。
- COMBOS:  17 组常见字母组合音。
- 每种发音: ipa(展示用音标) / label(给孩子看的中文标签) / demo(TTS 拟声词，
  用来生成"单音示范"音频) / words(该发音的高频词, [单词, emoji]) /
  advanced(进阶音, 只展示不进游戏)。

demo 示范音字典（2026-07-13 v4 定稿：真人录音为主）：
- "rec:文件名" = abc-phonics/recordings/ 下的真人发音录音（美国教师录制，
  来源 Sound City Reading，免费教育用途授权，见 recordings/CREDITS.md）。
  build.py 只做去首尾静音 + 音量归一，不动声音内容本身。
- 疑难四音终案（2026-07-13 v5，判读标准=辅音在前+接近该字母在单词里的发音）：
  L="la"(Samantha, 听写"law") / R="rec:kokoro-r"(神经语音音标直出 ɹːə, 听写"Ruh")
  N="rec:scrtrim-n"(SCR真人精修, 听写"Hmm"纯哼鸣, 与 M 同声源)
  V="rec:scrtrim-v"(SCR真人精修, 与 F 同声源)
- 其余合成：kwah + 卷舌 ar or er；辨音配对(m/n、f/v、b/d、b/p)保持同声源
- 教训存档：TTS 念重复字母串=字母名；神经TTS发不了孤立辅音(会脑补元音)；
  espeak 只能出几十毫秒嘀嗒——持续辅音要么真人、要么"辅音+轻尾音"结构
- 结构校验：tools/analyze_recordings.py 证明每条录音都是单段纯音、不夹单词；
  机器听写复核：tools/qa_gate.py（faster-whisper large + allosaurus 双引擎）
- 若家长反馈某音不准: 换 recordings/ 里的文件或改 demo 字段, 重跑 build.py

emoji 均限制在 Unicode 12 及以下，保证华为平板正常显示。
"""

LETTERS = [
    {"letter": "A", "sounds": [
        {"ipa": "/æ/", "label": "短音", "demo": "rec:alphasounds-a",
         "words": [["apple", "🍎"], ["cat", "🐱"], ["hat", "🎩"], ["bag", "🎒"]]},
        {"ipa": "/eɪ/", "label": "字母音·长音", "demo": "rec:btalpha-7-a-long",
         "words": [["cake", "🎂"], ["snake", "🐍"], ["grape", "🍇"], ["face", "😊"]]},
    ]},
    {"letter": "B", "sounds": [
        {"ipa": "/b/", "label": "它的声音", "demo": "rec:alphasounds-b",
         "words": [["ball", "⚽"], ["banana", "🍌"], ["bear", "🐻"], ["bed", "🛏️"]]},
    ]},
    {"letter": "C", "sounds": [
        {"ipa": "/k/", "label": "常用发音", "demo": "rec:alphasounds-k",
         "words": [["cat", "🐱"], ["car", "🚗"], ["cup", "☕"], ["cow", "🐮"]]},
        {"ipa": "/s/", "label": "遇到 e·i·y 时", "demo": "rec:alphasounds-s", "advanced": True,
         "words": [["ice", "🧊"], ["rice", "🍚"], ["city", "🏙️"]]},
    ]},
    {"letter": "D", "sounds": [
        {"ipa": "/d/", "label": "它的声音", "demo": "rec:alphasounds-d",
         "words": [["dog", "🐶"], ["duck", "🦆"], ["dad", "👨"], ["door", "🚪"]]},
    ]},
    {"letter": "E", "sounds": [
        {"ipa": "/e/", "label": "短音", "demo": "rec:alphasounds-e",
         "words": [["egg", "🥚"], ["bed", "🛏️"], ["red", "🔴"], ["pen", "🖊️"]]},
        {"ipa": "/iː/", "label": "字母音·长音", "demo": "rec:btalpha-2-e-long",
         "words": [["he", "👦"], ["she", "👧"], ["we", "👨‍👩‍👧"], ["me", "🙋"]]},
    ]},
    {"letter": "F", "sounds": [
        {"ipa": "/f/", "label": "上齿咬下唇吹气", "demo": "rec:alphasounds-f",
         "words": [["fish", "🐟"], ["five", "5️⃣"], ["fox", "🦊"], ["foot", "🦶"]]},
    ]},
    {"letter": "G", "sounds": [
        {"ipa": "/g/", "label": "常用发音", "demo": "rec:alphasounds-g",
         "words": [["goat", "🐐"], ["girl", "👧"], ["gift", "🎁"], ["green", "💚"]]},
        {"ipa": "/dʒ/", "label": "少数单词里", "demo": "rec:alphasounds-j", "advanced": True,
         "words": [["orange", "🍊"], ["giraffe", "🦒"]]},
    ]},
    {"letter": "H", "sounds": [
        {"ipa": "/h/", "label": "它的声音", "demo": "rec:alphasounds-h",
         "words": [["hat", "🎩"], ["hand", "✋"], ["horse", "🐴"], ["house", "🏠"]]},
    ]},
    {"letter": "I", "sounds": [
        {"ipa": "/ɪ/", "label": "短音", "demo": "rec:alphasounds-i",
         "words": [["pig", "🐷"], ["six", "6️⃣"], ["milk", "🥛"], ["fish", "🐟"]]},
        {"ipa": "/aɪ/", "label": "字母音·长音", "demo": "rec:btalpha-i-long",
         "words": [["five", "5️⃣"], ["kite", "🪁"], ["bike", "🚲"], ["ice", "🧊"]]},
    ]},
    {"letter": "J", "sounds": [
        {"ipa": "/dʒ/", "label": "它的声音", "demo": "rec:alphasounds-j",
         "words": [["juice", "🧃"], ["jam", "🍓"], ["jump", "🤸"], ["jacket", "🧥"]]},
    ]},
    {"letter": "K", "sounds": [
        {"ipa": "/k/", "label": "它的声音", "demo": "rec:alphasounds-k",
         "words": [["key", "🔑"], ["king", "👑"], ["kite", "🪁"], ["kid", "🧒"]]},
    ]},
    {"letter": "L", "sounds": [
        {"ipa": "/l/", "label": "舌尖顶上颚拉长", "demo": "rec:custom-l",
         "words": [["lion", "🦁"], ["leg", "🦵"], ["lamp", "💡"], ["lemon", "🍋"]]},
    ]},
    {"letter": "M", "sounds": [
        {"ipa": "/m/", "label": "闭上嘴巴哼", "demo": "rec:alphasounds-m",
         "words": [["mom", "👩"], ["milk", "🥛"], ["mouse", "🐭"], ["map", "🗺️"]]},
    ]},
    {"letter": "N", "sounds": [
        {"ipa": "/n/", "label": "舌头顶上颚", "demo": "rec:scrtrim-n",
         "words": [["nose", "👃"], ["nut", "🥜"], ["nine", "9️⃣"], ["night", "🌙"]]},
    ]},
    {"letter": "O", "sounds": [
        {"ipa": "/ɑ/", "label": "短音", "demo": "rec:alphasounds-o-sh",
         "words": [["dog", "🐶"], ["box", "📦"], ["fox", "🦊"], ["hot", "🔥"]]},
        {"ipa": "/oʊ/", "label": "字母音·长音", "demo": "rec:btalpha-3-o-long",
         "words": [["nose", "👃"], ["rose", "🌹"], ["home", "🏠"], ["no", "🙅"]]},
        {"ipa": "/ʌ/", "label": "少数词里像短u", "demo": "rec:alphasounds-u-sh", "advanced": True,
         "words": [["mother", "👩"], ["love", "❤️"], ["come", "👋"]]},
    ]},
    {"letter": "P", "sounds": [
        {"ipa": "/p/", "label": "它的声音", "demo": "rec:alphasounds-p-2",
         "words": [["pig", "🐷"], ["pen", "🖊️"], ["panda", "🐼"], ["pink", "🌸"]]},
    ]},
    {"letter": "Q", "sounds": [
        {"ipa": "/kw/", "label": "qu 在一起", "demo": "kwah",
         "words": [["queen", "👸"], ["question", "❓"], ["quiet", "🤫"], ["quick", "🏃"]]},
    ]},
    {"letter": "R", "sounds": [
        {"ipa": "/r/", "label": "卷起舌头轻轻吼", "demo": "rec:custom-r",
         "words": [["rabbit", "🐰"], ["red", "🔴"], ["run", "🏃"], ["rice", "🍚"]]},
    ]},
    {"letter": "S", "sounds": [
        {"ipa": "/s/", "label": "常用发音", "demo": "rec:alphasounds-s",
         "words": [["sun", "☀️"], ["six", "6️⃣"], ["star", "⭐"], ["sit", "🪑"]]},
        {"ipa": "/z/", "label": "有时读 z", "demo": "rec:alphasounds-z", "advanced": True,
         "words": [["is", "☑️"], ["his", "👦"], ["nose", "👃"]]},
    ]},
    {"letter": "T", "sounds": [
        {"ipa": "/t/", "label": "它的声音", "demo": "rec:alphasounds-t",
         "words": [["ten", "🔟"], ["tiger", "🐯"], ["turtle", "🐢"], ["top", "🔝"]]},
    ]},
    {"letter": "U", "sounds": [
        {"ipa": "/ʌ/", "label": "短音", "demo": "rec:alphasounds-u-sh",
         "words": [["cup", "☕"], ["bus", "🚌"], ["duck", "🦆"], ["sun", "☀️"]]},
        {"ipa": "/juː/", "label": "字母音·长音", "demo": "rec:btalpha-10-u-long",
         "words": [["cute", "🥰"], ["music", "🎵"], ["unicorn", "🦄"], ["cube", "🧊"]]},
    ]},
    {"letter": "V", "sounds": [
        {"ipa": "/v/", "label": "咬住下嘴唇", "demo": "rec:scrtrim-v",
         "words": [["van", "🚐"], ["vest", "🦺"], ["violin", "🎻"], ["vegetable", "🥦"]]},
    ]},
    {"letter": "W", "sounds": [
        {"ipa": "/w/", "label": "它的声音", "demo": "rec:alphasounds-w",
         "words": [["water", "💧"], ["watch", "⌚"], ["watermelon", "🍉"], ["wolf", "🐺"]]},
    ]},
    {"letter": "X", "sounds": [
        {"ipa": "/ks/", "label": "在单词结尾", "demo": "rec:alphasounds-x",
         "words": [["box", "📦"], ["fox", "🦊"], ["six", "6️⃣"], ["ox", "🐂"]]},
    ]},
    {"letter": "Y", "sounds": [
        {"ipa": "/j/", "label": "在单词开头", "demo": "rec:alphasounds-y",
         "words": [["yellow", "💛"], ["yes", "✅"], ["yo-yo", "🪀"]]},
        {"ipa": "/aɪ/", "label": "在词尾·像字母I", "demo": "rec:btalpha-i-long",
         "words": [["my", "🙋"], ["sky", "🌌"], ["cry", "😢"]]},
        {"ipa": "/iː/", "label": "在词尾·轻快的衣", "demo": "rec:btalpha-2-e-long",
         "words": [["baby", "👶"], ["happy", "😄"], ["candy", "🍬"], ["family", "👪"]]},
    ]},
    {"letter": "Z", "sounds": [
        {"ipa": "/z/", "label": "它的声音", "demo": "rec:alphasounds-z",
         "words": [["zoo", "🦁"], ["zebra", "🦓"], ["zip", "🤐"], ["zero", "0️⃣"]]},
    ]},
]

COMBOS = [
    {"letter": "sh", "sounds": [
        {"ipa": "/ʃ/", "label": "嘘~安静", "demo": "rec:btalpha-1-sh",
         "words": [["sheep", "🐑"], ["ship", "🚢"], ["shoe", "👟"], ["fish", "🐟"]]},
    ]},
    {"letter": "ch", "sounds": [
        {"ipa": "/tʃ/", "label": "像小火车", "demo": "rec:btalpha-8-ch",
         "words": [["chair", "🪑"], ["cheese", "🧀"], ["chicken", "🐔"], ["peach", "🍑"]]},
    ]},
    {"letter": "th", "sounds": [
        {"ipa": "/θ/", "label": "舌尖轻咬·吹气", "demo": "rec:btalpha-4-th-soft",
         "words": [["three", "3️⃣"], ["mouth", "👄"], ["teeth", "🦷"], ["bath", "🛁"]]},
        {"ipa": "/ð/", "label": "舌尖轻咬·出声", "demo": "rec:btalpha-5-th-hard",
         "words": [["this", "👇"], ["that", "👉"], ["they", "👬"], ["mother", "👩"]]},
    ]},
    {"letter": "wh", "sounds": [
        {"ipa": "/w/", "label": "和 w 一样", "demo": "rec:alphasounds-w",
         "words": [["whale", "🐳"], ["white", "🤍"], ["what", "❓"], ["when", "⏰"]]},
    ]},
    {"letter": "ck", "sounds": [
        {"ipa": "/k/", "label": "和 k 一样", "demo": "rec:alphasounds-k",
         "words": [["duck", "🦆"], ["clock", "⏰"], ["sock", "🧦"], ["black", "⚫"]]},
    ]},
    {"letter": "ng", "sounds": [
        {"ipa": "/ŋ/", "label": "鼻音嗡嗡", "demo": "rec:btalpha-9-ng",
         "words": [["king", "👑"], ["ring", "💍"], ["sing", "🎤"], ["long", "📏"]]},
    ]},
    {"letter": "ee", "sounds": [
        {"ipa": "/iː/", "label": "长长的衣", "demo": "rec:btalpha-2-e-long",
         "words": [["bee", "🐝"], ["tree", "🌳"], ["sheep", "🐑"], ["see", "👀"]]},
    ]},
    {"letter": "ea", "sounds": [
        {"ipa": "/iː/", "label": "和 ee 一样", "demo": "rec:btalpha-2-e-long",
         "words": [["tea", "🍵"], ["sea", "🌊"], ["eat", "🍽️"], ["peach", "🍑"]]},
    ]},
    {"letter": "oo", "sounds": [
        {"ipa": "/uː/", "label": "长音·像火车呜", "demo": "rec:btalpha-6-o-dotted",
         "words": [["moon", "🌙"], ["food", "🍕"], ["school", "🏫"], ["cool", "😎"]]},
        {"ipa": "/ʊ/", "label": "短音", "demo": "rec:btalpha-13-u-dotted",
         "words": [["book", "📖"], ["look", "👀"], ["foot", "🦶"], ["good", "👍"]]},
    ]},
    {"letter": "ai", "sounds": [
        {"ipa": "/eɪ/", "label": "和字母 A 一样", "demo": "rec:btalpha-7-a-long",
         "words": [["rain", "🌧️"], ["train", "🚂"], ["snail", "🐌"], ["mail", "📬"]]},
    ]},
    {"letter": "ay", "sounds": [
        {"ipa": "/eɪ/", "label": "和字母 A 一样", "demo": "rec:btalpha-7-a-long",
         "words": [["day", "🌞"], ["play", "⚽"], ["say", "💬"], ["birthday", "🎂"]]},
    ]},
    {"letter": "igh", "sounds": [
        {"ipa": "/aɪ/", "label": "和字母 I 一样", "demo": "rec:btalpha-i-long",
         "words": [["night", "🌙"], ["light", "💡"], ["high", "🎈"], ["right", "✅"]]},
    ]},
    {"letter": "oa", "sounds": [
        {"ipa": "/oʊ/", "label": "和字母 O 一样", "demo": "rec:btalpha-3-o-long",
         "words": [["boat", "⛵"], ["goat", "🐐"], ["coat", "🧥"], ["road", "🛣️"]]},
    ]},
    {"letter": "ar", "sounds": [
        {"ipa": "/ɑr/", "label": "像海盗阿~", "demo": "ar",
         "words": [["car", "🚗"], ["star", "⭐"], ["park", "🎡"], ["arm", "💪"]]},
    ]},
    {"letter": "or", "sounds": [
        {"ipa": "/ɔr/", "label": "喔儿~", "demo": "or",
         "words": [["fork", "🍴"], ["horse", "🐴"], ["corn", "🌽"], ["morning", "🌅"]]},
    ]},
    {"letter": "er", "sounds": [
        {"ipa": "/ər/", "label": "轻轻的儿", "demo": "er",
         "words": [["tiger", "🐯"], ["teacher", "👩‍🏫"], ["water", "💧"], ["flower", "🌸"]]},
    ]},
    {"letter": "ow", "sounds": [
        {"ipa": "/aʊ/", "label": "哎呦~", "demo": "rec:btalpha-12-ow",
         "words": [["cow", "🐮"], ["owl", "🦉"], ["down", "⬇️"], ["brown", "🟤"]]},
        {"ipa": "/oʊ/", "label": "也常读字母O的音", "demo": "rec:btalpha-3-o-long",
         "words": [["snow", "❄️"], ["yellow", "💛"], ["slow", "🐢"], ["grow", "🌱"]]},
    ]},
]

# 「耳朵尖尖」辨音游戏的易混字母对；weight 越大越常出题（m/n 是重点）
CONFUSION_PAIRS = [
    {"pair": ["m", "n"], "weight": 4},
    {"pair": ["b", "d"], "weight": 2},
    {"pair": ["b", "p"], "weight": 2},
    {"pair": ["f", "v"], "weight": 1},
]

# 中文语音（婷婷）
ZH_CLIPS = {
    "hint_explore": "点一点字母，听听它的发音吧！",
    "intro_g1": "仔细听，然后点一点你听到的单词！",
    "intro_g2": "听一听这个发音，它藏在哪个单词里？",
    "intro_g3": "听一听，这个单词的开头，是哪个字母的声音？",
    "praise_1": "真棒！",
    "praise_2": "太厉害啦！",
    "praise_3": "答对啦！",
    "praise_4": "你真聪明！",
    "retry": "再试一次哦",
    "win_round": "闯关成功！你真是发音小达人！",
    "new_sticker": "哇！解锁新贴纸啦！",
}

# 奖励贴纸（每集满 12 颗星解锁一张）
STICKERS = ["🦄", "🐬", "🦖", "🚀", "🌈", "🍦", "🎠", "🐳", "🦋", "🎈", "🍭", "🛸"]
