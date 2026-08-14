#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AE 特效資料庫 - 命令列搜尋
用法:
    python search.py 發光
    python search.py glow bloom          # 多關鍵字預設 AND，無結果才清楚標示並退回 OR
    python search.py --cat transition 甩鏡
    python search.py --suite sapphire glow
    python search.py --kind script 關鍵影格
    python search.py --list-cats
無外部相依，純標準庫。搜尋 name / tags / desc / variants，中英皆可。
"""
import json, sys, os, glob, argparse, unicodedata
from urllib.parse import urlparse

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

SIMPLIFIED_TO_TRADITIONAL = str.maketrans({
    "发": "發", "辉": "輝", "颜": "顏", "调": "調", "颗": "顆",
    "过": "過", "转": "轉", "关": "關", "键": "鍵", "层": "層",
    "罩": "罩", "踪": "蹤", "稳": "穩", "绿": "綠", "脚": "腳",
    "插": "插", "内": "內", "动": "動", "边": "邊", "镜": "鏡",
    "雾": "霧", "锐": "銳", "变": "變", "还": "還", "显": "顯",
    "图": "圖", "线": "線", "选": "選", "场": "場", "复": "復",
    "术": "術", "体": "體", "数": "數", "据": "據", "画": "畫",
    "质": "質", "频": "頻", "拟": "擬", "应": "應", "滤": "濾",
    "渐": "漸", "虚": "虛", "实": "實", "声": "聲", "缩": "縮",
    "扩": "擴", "张": "張", "摆": "擺", "烧": "燒", "损": "損",
})

ALIASES = {
    "slowmo": ("slow motion", "慢動作", "補幀", "升格"),
    "slow-mo": ("slow motion", "慢動作", "補幀", "升格"),
    "retiming": ("retime", "變速", "補幀"),
    "key": ("keying", "去背", "摳像"),
    "greenscreen": ("green screen", "綠幕", "去背"),
    "glitch": ("故障", "數位故障", "破圖"),
    "denoise": ("noise reduction", "降噪", "去雜訊"),
    "beautify": ("beauty", "美膚", "磨皮"),
    "語音": ("voice", "speech", "講話", "說話", "旁白", "配音", "口白", "朗讀"),
    "voice": ("speech", "語音", "講話", "說話", "旁白", "配音", "口白", "朗讀"),
    "speech": ("voice", "語音", "講話", "說話", "旁白", "配音", "口白", "朗讀"),
    "講話": ("voice", "speech", "語音", "說話", "旁白", "配音", "口白", "朗讀"),
    "說話": ("voice", "speech", "語音", "講話", "旁白", "配音", "口白", "朗讀"),
    "旁白": ("voice", "speech", "語音", "講話", "說話", "配音", "口白", "朗讀"),
    "配音": ("voice", "speech", "語音", "講話", "說話", "旁白", "口白", "朗讀"),
    "字幕": ("subtitle", "caption", "cc", "歌詞", "lyrics", "字幕機", "sub"),
    "subtitle": ("caption", "cc", "字幕", "歌詞", "lyrics", "sub"),
    "caption": ("subtitle", "cc", "字幕", "歌詞", "lyrics", "sub"),
    "歌詞": ("lyrics", "字幕", "subtitle", "caption", "lyric"),
    "lyrics": ("歌詞", "字幕", "subtitle", "caption", "lyric"),
    "發光": ("glow", "光暈", "輝光", "bloom", "發光字"),
    "glow": ("發光", "光暈", "輝光", "bloom"),
    "光暈": ("glow", "發光", "輝光", "bloom"),
    "震動": ("shake", "晃動", "抖動", "震動模糊", "camera shake"),
    "shake": ("震動", "晃動", "抖動", "震動模糊", "camera shake"),
    "碎裂": ("shatter", "破裂", "爆裂", "碎片", "碎掉"),
    "shatter": ("碎裂", "破裂", "爆裂", "碎片"),
    "液體": ("liquid", "fluid", "流體", "水滴", "水"),
    "liquid": ("液體", "fluid", "流體", "水滴", "水"),
    "打字": ("typewriter", "打字機", "typing", "逐字敲出"),
    "typewriter": ("打字", "打字機", "typing", "逐字敲出"),
    "老電影": ("film", "底片", "膠片", "電影質感", "old film"),
    "film": ("底片", "膠片", "老電影", "電影質感", "old film"),
    "波形": ("waveform", "聲波", "音波", "audio waveform"),
    "waveform": ("波形", "聲波", "音波", "audio waveform"),
    "追蹤": ("tracking", "跟蹤", "跟拍", "track"),
    "tracking": ("追蹤", "跟蹤", "跟拍", "track"),
    "轉場": ("transition", "過場", "切場", "切換"),
    "transition": ("轉場", "過場", "切場", "切換"),
    "淡出": ("fade", "淡入", "淡入淡出", "fade in"),
    "fade": ("淡入", "淡出", "淡入淡出", "fade in"),
    "描邊": ("stroke", "輪廓", "描線", "outline", "線框"),
    "stroke": ("描邊", "輪廓", "描線", "outline", "線框"),
    "輪廓": ("stroke", "描邊", "描線", "outline", "線框"),
    "馬賽克": ("mosaic", "像素化", "pixelate", "點陣化"),
    "mosaic": ("馬賽克", "像素化", "pixelate", "點陣化"),
    "雜訊": ("noise", "噪點", "顆粒", "grain", "躁點"),
    "noise": ("雜訊", "噪點", "顆粒", "grain", "躁點"),
    "眨眼": ("blink", "閉眼", "wink"),
    "blink": ("眨眼", "閉眼", "wink"),
    "粒子": ("particle", "particles", "微粒", "粒子系統"),
    "particle": ("粒子", "particles", "微粒", "粒子系統"),
    "緩動": ("easing", "ease", "緩衝", "緩動曲線"),
    "easing": ("緩動", "ease", "緩衝", "緩動曲線"),
    "調色": ("color", "colour", "顏色", "色彩", "色調", "調色"),
    "color": ("調色", "colour", "顏色", "色彩", "色調"),
    "暈影": ("vignette", "暗角", "周邊暗角"),
    "vignette": ("暈影", "暗角", "周邊暗角"),
    "模糊": ("blur", "柔焦", "模糊化"),
    "blur": ("模糊", "柔焦", "模糊化"),
    "銳化": ("sharpen", "銳利", "sharpening"),
    "sharpen": ("銳化", "銳利", "sharpening"),
    "倒影": ("reflection", "反射", "鏡像", "mirror"),
    "reflection": ("倒影", "反射", "鏡像", "mirror"),
    "對齊": ("align", "alignment", "排列", "對齊工具"),
    "align": ("對齊", "alignment", "排列", "對齊工具"),
    "重新命名": ("rename", "改名", "命名", "重命名"),
    "rename": ("重新命名", "改名", "命名", "重命名"),
    "標記": ("marker", "時間標記", "標記點"),
    "marker": ("標記", "時間標記", "標記點"),
    "快捷鍵": ("shortcut", "快捷", "熱鍵", "熱鍵設定"),
    "shortcut": ("快捷鍵", "快捷", "熱鍵", "熱鍵設定"),
    "匯出": ("export", "輸出", "導出"),
    "export": ("匯出", "輸出", "導出"),
    "匯入": ("import", "導入", "輸入"),
    "import": ("匯入", "導入", "輸入"),
    "音樂": ("audio", "music", "音訊", "音效", "節拍", "bpm", "節奏"),
    "audio": ("音樂", "music", "音訊", "音效", "節拍", "bpm", "節奏"),
    "節拍": ("bpm", "節奏", "拍點", "beat"),
    "bpm": ("節拍", "節奏", "拍點", "beat"),
    "復古": ("vintage", "懷舊", "舊化", "retro", "老舊"),
    "vintage": ("復古", "懷舊", "舊化", "retro", "老舊"),
    "倒數": ("countdown", "計時", "timer", "倒數計時"),
    "countdown": ("倒數", "計時", "timer", "倒數計時"),
    "自動化": ("automation", "批次", "batch", "一鍵"),
    "automation": ("自動化", "批次", "batch", "一鍵"),
    "掉幀": ("抽幀", "frame step", "posterize", "定格"),
    "書法": ("毛筆", "calligraphy", "手寫字", "墨筆"),
    "calligraphy": ("書法", "毛筆", "手寫字", "墨筆"),
    "光線": ("light", "光束", "光", "打光", "燈光"),
    "light": ("光線", "光束", "打光", "燈光"),
    "陰影": ("shadow", "投影", "影子"),
    "shadow": ("陰影", "投影", "影子"),
    "火焰": ("fire", "火", "燃燒", "火燄"),
    "fire": ("火焰", "火", "燃燒", "火燄"),
    "煙霧": ("smoke", "煙", "煙塵"),
    "smoke": ("煙霧", "煙", "煙塵"),
    "閃電": ("lightning", "雷電", "電光", "雷"),
    "lightning": ("閃電", "雷電", "電光", "雷"),
    "爆炸": ("explosion", "爆裂", "爆炸效果", "炸"),
    "explosion": ("爆炸", "爆裂", "爆炸效果", "炸"),
    "星星": ("star", "星光", "sparkle", "閃爍", "星芒"),
    "star": ("星星", "星光", "sparkle", "閃爍", "星芒"),
    "愛心": ("heart", "心形", "愛心形狀"),
    "heart": ("愛心", "心形", "愛心形狀"),
    "箭頭": ("arrow", "箭頭指示", "指標"),
    "arrow": ("箭頭", "箭頭指示", "指標"),
    "對話框": ("speech bubble", "對話泡泡", "氣泡", "聊天框"),
    "emoji": ("表情", "貼圖", "笑臉", "表情符號"),
    "眼睛": ("eye", "眼球", "眼神", "瞳孔"),
    "eye": ("眼睛", "眼球", "眼神", "瞳孔"),
    "頭髮": ("hair", "髮絲", "毛髮"),
    "hair": ("頭髮", "髮絲", "毛髮"),
    "游標": ("cursor", "滑鼠", "鼠標", "指標"),
    "cursor": ("游標", "滑鼠", "鼠標", "指標"),
    "逐字": ("per character", "逐字元", "per-char", "逐字動畫"),
    "印章": ("stamp", "蓋章", "印鑑"),
    "stamp": ("印章", "蓋章", "印鑑"),
    "備忘": ("notes", "筆記", "記事", "便條"),
    "notes": ("備忘", "筆記", "記事", "便條"),
    "代理": ("proxy", "代理檔", "proxy file"),
    "proxy": ("代理", "代理檔", "proxy file"),
    "縮放": ("scale", "放大", "縮小", "縮放大小"),
    "scale": ("縮放", "放大", "縮小", "縮放大小"),
    "旋轉": ("rotate", "rotation", "轉動", "迴轉"),
    "rotate": ("旋轉", "rotation", "轉動", "迴轉"),
    "照片": ("photo", "相片", "相框", "圖片"),
    "photo": ("照片", "相片", "相框", "圖片"),
}


def derive_src(src, url):
    """依官方 URL 主機把商店來源（BOOTH、Gumroad）從資料檔來源拆出來。"""
    try:
        host = (urlparse(url).netloc or "").casefold()
    except Exception:
        host = ""
    if host == "booth.pm" or host.endswith(".booth.pm"):
        return "booth"
    if host == "gumroad.com" or host.endswith(".gumroad.com"):
        return "gumroad"
    return src


def normalize_text(value: object) -> str:
    """統一寬度、大小寫與常見簡體字，讓 CLI 與網頁搜尋行為一致。"""
    text = unicodedata.normalize("NFKC", str(value or ""))
    return " ".join(text.translate(SIMPLIFIED_TO_TRADITIONAL).casefold().split())


def term_groups(terms):
    groups = []
    for raw in terms:
        term = normalize_text(raw)
        if not term:
            continue
        values = {term}
        values.update(normalize_text(alias) for alias in ALIASES.get(term, ()))
        groups.append(values)
    return groups

def load():
    rows = []
    for path in sorted(glob.glob(os.path.join(DATA_DIR, "*.jsonl"))):
        file_src = os.path.splitext(os.path.basename(path))[0]
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                obj["_src"] = derive_src(file_src, obj.get("url", ""))
                rows.append(obj)
    return rows

def haystack(row):
    parts = [row.get("name", ""), row.get("kind", ""), row.get("cat", ""), row.get("desc", ""),
             row.get("look", ""), row.get("suite", ""), row.get("vendor", ""),
             " ".join(row.get("tags", []))]
    v = row.get("variants")
    if isinstance(v, dict):
        parts.append(" ".join(v.keys()))
        parts.append(" ".join(str(x) for x in v.values()))
    return normalize_text(" ".join(parts))

def _cjk_char(ch):
    return "一" <= ch <= "鿿" or "㐀" <= ch <= "䶿"

def is_cjk(s):
    return any(_cjk_char(ch) for ch in s)

def segment(terms):
    """中文長詞拆成 2 字詞組（「煙霧模擬」→ 煙霧/霧模/模擬），搜不到時當備援。"""
    out = []
    for t in terms:
        if len(t) >= 3 and is_cjk(t):
            for i in range(len(t) - 1):
                g = t[i:i+2]
                if all(_cjk_char(c) for c in g) and g not in out:
                    out.append(g)
    return out

def score(row, terms):
    text = haystack(row)
    name = normalize_text(row.get("name", ""))
    tags = normalize_text(" ".join(row.get("tags", [])))
    s = 0
    for group in term_groups(terms):
        group_score = 0
        for term in group:
            value = (5 if term in name else 0) + (3 if term in tags else 0) + (1 if term in text else 0)
            group_score = max(group_score, value)
        s += group_score
    phrase = " ".join(normalize_text(term) for term in terms if normalize_text(term))
    if phrase:
        if name == phrase:
            s += 40
        elif phrase in name:
            s += 20
        if phrase in tags:
            s += 10
    return s

def ranked(rows, terms, require_all=True):
    """依相關度排序；預設每個查詢詞都要命中同一筆資料。"""
    groups = term_groups(terms)
    found = []
    for row in rows:
        text = haystack(row)
        matches = [any(term in text for term in group) for group in groups]
        if require_all and not all(matches):
            continue
        value = score(row, terms)
        if value > 0:
            found.append((value, row))
    return sorted(found, key=lambda item: (-item[0], item[1].get("name", "").casefold()))


def levenshtein(a, b):
    previous = list(range(len(b) + 1))
    for i, char_a in enumerate(a, 1):
        current = [i]
        for j, char_b in enumerate(b, 1):
            current.append(min(current[-1] + 1, previous[j] + 1, previous[j - 1] + (char_a != char_b)))
        previous = current
    return previous[-1]


def vocabulary(rows):
    words = set()
    for row in rows:
        values = [row.get("name", ""), *row.get("tags", [])]
        for value in values:
            words.update(part for part in re_split(normalize_text(value)) if len(part) >= 3)
    return words


def re_split(value):
    current = []
    for char in value:
        if char.isalnum() or _cjk_char(char):
            current.append(char)
        elif current:
            yield "".join(current)
            current = []
    if current:
        yield "".join(current)


def correct_terms(rows, terms):
    words = vocabulary(rows)
    corrected = []
    changed = False
    for raw in terms:
        term = normalize_text(raw)
        if len(term) < 4 or term in words or is_cjk(term):
            corrected.append(term)
            continue
        limit = 2 if len(term) >= 7 else 1
        candidates = sorted((levenshtein(term, word), word) for word in words if abs(len(word) - len(term)) <= limit)
        if candidates and candidates[0][0] <= limit:
            corrected.append(candidates[0][1])
            changed = changed or candidates[0][1] != term
        else:
            corrected.append(term)
    return corrected if changed else []

def main():
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("terms", nargs="*", help="關鍵字（中英皆可，多個預設為 AND）")
    ap.add_argument("--any", action="store_true", help="多個關鍵字改用 OR，符合任一個就顯示")
    ap.add_argument("--cat", help="限定分類 (glow/transition/particles/...)")
    ap.add_argument("--kind", choices=("plugin", "script", "builtin", "recipe"), help="限定工具型態")
    ap.add_argument("--suite", help="限定來源 (sapphire/continuum/universe/red-giant/builtin-ae/recipes/third-party/booth/gumroad)")
    ap.add_argument("--top", type=int, default=15, help="顯示前 N 筆 (預設15)")
    ap.add_argument("--list-cats", action="store_true", help="列出所有分類與筆數")
    args = ap.parse_args()

    rows = load()

    if args.list_cats:
        from collections import Counter
        c = Counter(r.get("cat", "?") for r in rows)
        for cat, n in sorted(c.items(), key=lambda x: -x[1]):
            print(f"{n:4d}  {cat}")
        print(f"\n總計 {len(rows)} 筆 / {len(set(r['_src'] for r in rows))} 個來源檔")
        return

    if not args.terms:
        ap.print_help()
        return

    pool = rows
    if args.suite:
        pool = [r for r in pool if args.suite.lower() in r["_src"].lower()]
    if args.cat:
        pool = [r for r in pool if r.get("cat", "").lower() == args.cat.lower()]
    if args.kind:
        pool = [r for r in pool if r.get("kind") == args.kind]

    scored = ranked(pool, args.terms, require_all=not args.any)

    if not scored and len(args.terms) > 1 and not args.any:
        scored = ranked(pool, args.terms, require_all=False)
        if scored:
            print("沒有同時符合全部關鍵字，改顯示符合任一關鍵字。\n")

    if not scored:
        segs = segment(args.terms)
        if segs:
            scored = ranked(pool, segs, require_all=False)
            if scored:
                print(f"找不到「{' '.join(args.terms)}」，已自動拆詞：{'、'.join(segs)}\n")

    if not scored:
        corrected = correct_terms(pool, args.terms)
        if corrected:
            scored = ranked(pool, corrected, require_all=not args.any)
            if scored:
                print(f"找不到「{' '.join(args.terms)}」，已修正為：{'、'.join(corrected)}\n")

    if not scored:
        print("找不到相符效果，換個關鍵字或用 --list-cats 看分類。")
        return

    for s, r in scored[:args.top]:
        origin = r.get("suite") or r.get("vendor") or r["_src"]
        print(f"[{r.get('kind','?'):7}/{r.get('cat','?'):10}] {r['name']}  ({origin})")
        print(f"            {r.get('desc','')}")
        v = r.get("variants")
        if isinstance(v, dict):
            sample = list(v.items())[:6]
            print("            變體: " + " | ".join(f"{k}={val}" for k, val in sample)
                  + (" …" if len(v) > 6 else ""))
    if len(scored) > args.top:
        print(f"\n… 另有 {len(scored) - args.top} 筆，用 --top 調整或加關鍵字縮小。")

if __name__ == "__main__":
    main()
