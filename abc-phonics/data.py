# -*- coding: utf-8 -*-
"""ABC 发音乐园 - 内容库（唯一事实来源）

结构说明：
- LETTERS: 26 个字母，每个含 1~3 种常见发音(sounds)。
- COMBOS:  17 组常见字母组合音。
- 每种发音: ipa(展示用音标) / label(给孩子看的中文标签) / demo(TTS 拟声词，
  用来生成"单音示范"音频) / words(该发音的高频词, [单词, emoji]) /
  advanced(进阶音, 只展示不进游戏)。

demo 拟声词字典（2026-07-13 经 faster-whisper 机器试听两轮校准）：
- 字母音(长元音)直接用能发出字母名的串: a / ee / eye / oh / you
- 辅音用 -ah 系: bah kah dah fa gah hah jah kah la pah kwah sa tuh wah yah za
  cha jah kwah；可持续音用 mmm nnn rrr vvv shh thh
- 无法用拟声词表达的用真实小词锚定: at it Ed look ox the moo oww ar or er ing
- 若家长反馈某音不准: 只改对应 demo 字段, 重跑 build.py 即可(有缓存,秒级)

emoji 均限制在 Unicode 12 及以下，保证华为平板正常显示。
"""

LETTERS = [
    {"letter": "A", "sounds": [
        {"ipa": "/æ/", "label": "短音", "demo": "at",
         "words": [["apple", "🍎"], ["cat", "🐱"], ["hat", "🎩"], ["bag", "🎒"]]},
        {"ipa": "/eɪ/", "label": "字母音·长音", "demo": "a",
         "words": [["cake", "🎂"], ["snake", "🐍"], ["grape", "🍇"], ["face", "😊"]]},
    ]},
    {"letter": "B", "sounds": [
        {"ipa": "/b/", "label": "它的声音", "demo": "bah",
         "words": [["ball", "⚽"], ["banana", "🍌"], ["bear", "🐻"], ["bed", "🛏️"]]},
    ]},
    {"letter": "C", "sounds": [
        {"ipa": "/k/", "label": "常用发音", "demo": "kah",
         "words": [["cat", "🐱"], ["car", "🚗"], ["cup", "☕"], ["cow", "🐮"]]},
        {"ipa": "/s/", "label": "遇到 e·i·y 时", "demo": "sa", "advanced": True,
         "words": [["ice", "🧊"], ["rice", "🍚"], ["city", "🏙️"]]},
    ]},
    {"letter": "D", "sounds": [
        {"ipa": "/d/", "label": "它的声音", "demo": "duh",
         "words": [["dog", "🐶"], ["duck", "🦆"], ["dad", "👨"], ["door", "🚪"]]},
    ]},
    {"letter": "E", "sounds": [
        {"ipa": "/e/", "label": "短音", "demo": "Ed",
         "words": [["egg", "🥚"], ["bed", "🛏️"], ["red", "🔴"], ["pen", "🖊️"]]},
        {"ipa": "/iː/", "label": "字母音·长音", "demo": "ee",
         "words": [["he", "👦"], ["she", "👧"], ["we", "👨‍👩‍👧"], ["me", "🙋"]]},
    ]},
    {"letter": "F", "sounds": [
        {"ipa": "/f/", "label": "它的声音", "demo": "fa",
         "words": [["fish", "🐟"], ["five", "5️⃣"], ["fox", "🦊"], ["foot", "🦶"]]},
    ]},
    {"letter": "G", "sounds": [
        {"ipa": "/g/", "label": "常用发音", "demo": "gah",
         "words": [["goat", "🐐"], ["girl", "👧"], ["gift", "🎁"], ["green", "💚"]]},
        {"ipa": "/dʒ/", "label": "少数单词里", "demo": "jah", "advanced": True,
         "words": [["orange", "🍊"], ["giraffe", "🦒"]]},
    ]},
    {"letter": "H", "sounds": [
        {"ipa": "/h/", "label": "它的声音", "demo": "hah",
         "words": [["hat", "🎩"], ["hand", "✋"], ["horse", "🐴"], ["house", "🏠"]]},
    ]},
    {"letter": "I", "sounds": [
        {"ipa": "/ɪ/", "label": "短音", "demo": "it",
         "words": [["pig", "🐷"], ["six", "6️⃣"], ["milk", "🥛"], ["fish", "🐟"]]},
        {"ipa": "/aɪ/", "label": "字母音·长音", "demo": "eye",
         "words": [["five", "5️⃣"], ["kite", "🪁"], ["bike", "🚲"], ["ice", "🧊"]]},
    ]},
    {"letter": "J", "sounds": [
        {"ipa": "/dʒ/", "label": "它的声音", "demo": "jah",
         "words": [["juice", "🧃"], ["jam", "🍓"], ["jump", "🤸"], ["jacket", "🧥"]]},
    ]},
    {"letter": "K", "sounds": [
        {"ipa": "/k/", "label": "它的声音", "demo": "kah",
         "words": [["key", "🔑"], ["king", "👑"], ["kite", "🪁"], ["kid", "🧒"]]},
    ]},
    {"letter": "L", "sounds": [
        {"ipa": "/l/", "label": "它的声音", "demo": "la",
         "words": [["lion", "🦁"], ["leg", "🦵"], ["lamp", "💡"], ["lemon", "🍋"]]},
    ]},
    {"letter": "M", "sounds": [
        {"ipa": "/m/", "label": "闭上嘴巴哼", "demo": "mmm",
         "words": [["mom", "👩"], ["milk", "🥛"], ["mouse", "🐭"], ["map", "🗺️"]]},
    ]},
    {"letter": "N", "sounds": [
        {"ipa": "/n/", "label": "舌头顶上颚", "demo": "nnn",
         "words": [["nose", "👃"], ["nut", "🥜"], ["nine", "9️⃣"], ["night", "🌙"]]},
    ]},
    {"letter": "O", "sounds": [
        {"ipa": "/ɑ/", "label": "短音", "demo": "ah",
         "words": [["dog", "🐶"], ["box", "📦"], ["fox", "🦊"], ["hot", "🔥"]]},
        {"ipa": "/oʊ/", "label": "字母音·长音", "demo": "oh",
         "words": [["nose", "👃"], ["rose", "🌹"], ["home", "🏠"], ["no", "🙅"]]},
        {"ipa": "/ʌ/", "label": "少数词里像短u", "demo": "uh", "advanced": True,
         "words": [["mother", "👩"], ["love", "❤️"], ["come", "👋"]]},
    ]},
    {"letter": "P", "sounds": [
        {"ipa": "/p/", "label": "它的声音", "demo": "pah",
         "words": [["pig", "🐷"], ["pen", "🖊️"], ["panda", "🐼"], ["pink", "🌸"]]},
    ]},
    {"letter": "Q", "sounds": [
        {"ipa": "/kw/", "label": "qu 在一起", "demo": "kwah",
         "words": [["queen", "👸"], ["question", "❓"], ["quiet", "🤫"], ["quick", "🏃"]]},
    ]},
    {"letter": "R", "sounds": [
        {"ipa": "/r/", "label": "它的声音", "demo": "rrr",
         "words": [["rabbit", "🐰"], ["red", "🔴"], ["run", "🏃"], ["rice", "🍚"]]},
    ]},
    {"letter": "S", "sounds": [
        {"ipa": "/s/", "label": "常用发音", "demo": "sa",
         "words": [["sun", "☀️"], ["six", "6️⃣"], ["star", "⭐"], ["sit", "🪑"]]},
        {"ipa": "/z/", "label": "有时读 z", "demo": "za", "advanced": True,
         "words": [["is", "☑️"], ["his", "👦"], ["nose", "👃"]]},
    ]},
    {"letter": "T", "sounds": [
        {"ipa": "/t/", "label": "它的声音", "demo": "tuh",
         "words": [["ten", "🔟"], ["tiger", "🐯"], ["turtle", "🐢"], ["top", "🔝"]]},
    ]},
    {"letter": "U", "sounds": [
        {"ipa": "/ʌ/", "label": "短音", "demo": "uh",
         "words": [["cup", "☕"], ["bus", "🚌"], ["duck", "🦆"], ["sun", "☀️"]]},
        {"ipa": "/juː/", "label": "字母音·长音", "demo": "you",
         "words": [["cute", "🥰"], ["music", "🎵"], ["unicorn", "🦄"], ["cube", "🧊"]]},
    ]},
    {"letter": "V", "sounds": [
        {"ipa": "/v/", "label": "咬住下嘴唇", "demo": "vvv",
         "words": [["van", "🚐"], ["vest", "🦺"], ["violin", "🎻"], ["vegetable", "🥦"]]},
    ]},
    {"letter": "W", "sounds": [
        {"ipa": "/w/", "label": "它的声音", "demo": "wah",
         "words": [["water", "💧"], ["watch", "⌚"], ["watermelon", "🍉"], ["wolf", "🐺"]]},
    ]},
    {"letter": "X", "sounds": [
        {"ipa": "/ks/", "label": "在单词结尾", "demo": "ox",
         "words": [["box", "📦"], ["fox", "🦊"], ["six", "6️⃣"], ["ox", "🐂"]]},
    ]},
    {"letter": "Y", "sounds": [
        {"ipa": "/j/", "label": "在单词开头", "demo": "yah",
         "words": [["yellow", "💛"], ["yes", "✅"], ["yo-yo", "🪀"]]},
        {"ipa": "/aɪ/", "label": "在词尾·像字母I", "demo": "eye",
         "words": [["my", "🙋"], ["sky", "🌌"], ["cry", "😢"]]},
        {"ipa": "/iː/", "label": "在词尾·轻快的衣", "demo": "ee",
         "words": [["baby", "👶"], ["happy", "😄"], ["candy", "🍬"], ["family", "👪"]]},
    ]},
    {"letter": "Z", "sounds": [
        {"ipa": "/z/", "label": "它的声音", "demo": "za",
         "words": [["zoo", "🦁"], ["zebra", "🦓"], ["zip", "🤐"], ["zero", "0️⃣"]]},
    ]},
]

COMBOS = [
    {"letter": "sh", "sounds": [
        {"ipa": "/ʃ/", "label": "嘘~安静", "demo": "shh",
         "words": [["sheep", "🐑"], ["ship", "🚢"], ["shoe", "👟"], ["fish", "🐟"]]},
    ]},
    {"letter": "ch", "sounds": [
        {"ipa": "/tʃ/", "label": "像小火车", "demo": "cha",
         "words": [["chair", "🪑"], ["cheese", "🧀"], ["chicken", "🐔"], ["peach", "🍑"]]},
    ]},
    {"letter": "th", "sounds": [
        {"ipa": "/θ/", "label": "舌尖轻咬·吹气", "demo": "thh",
         "words": [["three", "3️⃣"], ["mouth", "👄"], ["teeth", "🦷"], ["bath", "🛁"]]},
        {"ipa": "/ð/", "label": "舌尖轻咬·出声", "demo": "the",
         "words": [["this", "👇"], ["that", "👉"], ["they", "👬"], ["mother", "👩"]]},
    ]},
    {"letter": "wh", "sounds": [
        {"ipa": "/w/", "label": "和 w 一样", "demo": "wah",
         "words": [["whale", "🐳"], ["white", "🤍"], ["what", "❓"], ["when", "⏰"]]},
    ]},
    {"letter": "ck", "sounds": [
        {"ipa": "/k/", "label": "和 k 一样", "demo": "kah",
         "words": [["duck", "🦆"], ["clock", "⏰"], ["sock", "🧦"], ["black", "⚫"]]},
    ]},
    {"letter": "ng", "sounds": [
        {"ipa": "/ŋ/", "label": "鼻音嗡嗡", "demo": "ing",
         "words": [["king", "👑"], ["ring", "💍"], ["sing", "🎤"], ["long", "📏"]]},
    ]},
    {"letter": "ee", "sounds": [
        {"ipa": "/iː/", "label": "长长的衣", "demo": "ee",
         "words": [["bee", "🐝"], ["tree", "🌳"], ["sheep", "🐑"], ["see", "👀"]]},
    ]},
    {"letter": "ea", "sounds": [
        {"ipa": "/iː/", "label": "和 ee 一样", "demo": "ee",
         "words": [["tea", "🍵"], ["sea", "🌊"], ["eat", "🍽️"], ["peach", "🍑"]]},
    ]},
    {"letter": "oo", "sounds": [
        {"ipa": "/uː/", "label": "长音·像火车呜", "demo": "moo",
         "words": [["moon", "🌙"], ["food", "🍕"], ["school", "🏫"], ["cool", "😎"]]},
        {"ipa": "/ʊ/", "label": "短音", "demo": "look",
         "words": [["book", "📖"], ["look", "👀"], ["foot", "🦶"], ["good", "👍"]]},
    ]},
    {"letter": "ai", "sounds": [
        {"ipa": "/eɪ/", "label": "和字母 A 一样", "demo": "a",
         "words": [["rain", "🌧️"], ["train", "🚂"], ["snail", "🐌"], ["mail", "📬"]]},
    ]},
    {"letter": "ay", "sounds": [
        {"ipa": "/eɪ/", "label": "和字母 A 一样", "demo": "a",
         "words": [["day", "🌞"], ["play", "⚽"], ["say", "💬"], ["birthday", "🎂"]]},
    ]},
    {"letter": "igh", "sounds": [
        {"ipa": "/aɪ/", "label": "和字母 I 一样", "demo": "eye",
         "words": [["night", "🌙"], ["light", "💡"], ["high", "🎈"], ["right", "✅"]]},
    ]},
    {"letter": "oa", "sounds": [
        {"ipa": "/oʊ/", "label": "和字母 O 一样", "demo": "oh",
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
        {"ipa": "/aʊ/", "label": "哎呦~", "demo": "oww",
         "words": [["cow", "🐮"], ["owl", "🦉"], ["down", "⬇️"], ["brown", "🟤"]]},
        {"ipa": "/oʊ/", "label": "也常读字母O的音", "demo": "oh",
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
