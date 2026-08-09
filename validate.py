#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
校驗 data/*.jsonl：每行是否為合法 JSON、必填欄位、型別、分類、重複名稱，
以及「樣板化」品質檢查（同一批條目共用同一句 desc 句型或同一組 tags）。

用法：
    python validate.py            # 品質問題只出警告，不擋合併
    python validate.py --strict   # 品質問題也視為錯誤（適合自己送 PR 前跑）

CI 與送 PR 前都會跑這支。有 error 會 exit 1。
"""
import json, sys, os, glob, re, collections

try:
    sys.stdout.reconfigure(encoding="utf-8")  # Windows 主控台預設非 UTF-8 時避免亂碼
except Exception:
    pass

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# 已知分類（新增分類請一併加到這裡與 AGENTS.md）
KNOWN_CATS = {
    "glow","blur-glow","light","flare","particles","stylize","film","color",
    "blur","warp","keying","tracking","restore","time","transition","text",
    "generate","3d","draw","paint","art","texture","audio","physics","rigging",
    "workflow","render","expression","animation","preset","utility","distort",
    "mograph","beauty","edge","emboss","composite","matte","perspective",
    "kaleido","vr","recipe",
}
REQUIRED = ("name","cat","tags","desc")
OPTIONAL = {"look","variants","stack","builtin","suite","vendor","unverified","aex","url"}
ALLOWED = set(REQUIRED) | OPTIONAL

CJK = re.compile(r"[一-鿿]")

def without_name(text, name):
    """把條目名（含拆開的字詞）從字串裡拿掉，用來偵測『只有名字不同』的樣板。"""
    t = text or ""
    parts = sorted([name] + re.split(r"[\s_+]+", name), key=len, reverse=True)
    for p in parts:
        if len(p) >= 2:
            t = t.replace(p, "")
    return re.sub(r"[\s「」\"'()（）·、]+", "", t)

def quality_checks(rows):
    """回傳品質問題清單。rows = [(檔名, 位置, 條目 dict), ...]"""
    out = []

    # 1) tags 全英文：中文使用者搜不到
    no_cjk = [loc for _, loc, o in rows
              if isinstance(o.get("tags"), list) and o["tags"]
              and not any(CJK.search(str(t)) for t in o["tags"])]
    if no_cjk:
        out.append("有 %d 筆的 tags 完全沒有中文（中文使用者搜不到）："
                   "%s%s" % (len(no_cjk), "、".join(no_cjk[:5]),
                             " …" if len(no_cjk) > 5 else ""))

    # 2) desc 樣板：同檔內把名字遮掉後句子一模一樣
    by_file = collections.defaultdict(lambda: collections.defaultdict(list))
    for fn, loc, o in rows:
        if isinstance(o.get("desc"), str) and isinstance(o.get("name"), str):
            key = without_name(o["desc"], o["name"])
            if len(key) >= 8:
                by_file[fn][key].append((loc, o["name"]))
    hits = [(fn, m) for fn, groups in by_file.items()
            for m in groups.values() if len(m) >= 3]
    hits.sort(key=lambda x: -len(x[1]))
    for fn, members in hits[:5]:
        names_ = "、".join(n for _, n in members[:4])
        out.append("%s 有 %d 筆共用同一句 desc 句型（只有名字不同）：%s…"
                   "／把名字遮掉後應該還能分辨是哪個效果" % (fn, len(members), names_))
    if len(hits) > 5:
        out.append("…另有 %d 組 desc 樣板（共 %d 筆），詳見同樣的檢查邏輯"
                   % (len(hits) - 5, sum(len(m) for _, m in hits[5:])))

    # 3) tags 樣板：同檔內把名字相關的 tag 拿掉後，整組 tags 一模一樣
    by_file2 = collections.defaultdict(lambda: collections.defaultdict(list))
    for fn, loc, o in rows:
        if isinstance(o.get("tags"), list) and isinstance(o.get("name"), str):
            nm = o["name"].lower()
            rest = tuple(sorted(str(t) for t in o["tags"] if str(t).lower() not in nm))
            if rest:
                by_file2[fn][rest].append((loc, o["name"]))
    hits2 = [(fn, rest, m) for fn, groups in by_file2.items()
             for rest, m in groups.items() if len(m) >= 4]
    hits2.sort(key=lambda x: -len(x[2]))
    for fn, rest, members in hits2[:5]:
        out.append("%s 有 %d 筆的 tags 去掉名字後完全相同：%s"
                   "／搜這組字會一次噴出一堆長得一樣的結果，請補俗名與外觀同義詞"
                   % (fn, len(members), "、".join(rest[:6])))
    if len(hits2) > 5:
        out.append("…另有 %d 組 tags 樣板（共 %d 筆）"
                   % (len(hits2) - 5, sum(len(m) for _, _, m in hits2[5:])))
    return out

def main():
    strict = "--strict" in sys.argv
    errors, warnings, total = [], [], 0
    names, rows = {}, []
    stats = {"url": 0, "look": 0, "unv": 0}
    files = sorted(glob.glob(os.path.join(DATA_DIR, "*.jsonl")))
    if not files:
        print("找不到 data/*.jsonl"); sys.exit(1)
    for path in files:
        fn = os.path.basename(path)
        with open(path, encoding="utf-8") as f:
            for i, line in enumerate(f, 1):
                line = line.rstrip("\n")
                if not line.strip():
                    continue
                total += 1
                loc = f"{fn}:{i}"
                try:
                    o = json.loads(line)
                except json.JSONDecodeError as e:
                    errors.append(f"{loc}  JSON 解析失敗：{e}")
                    continue
                if not isinstance(o, dict):
                    errors.append(f"{loc}  不是 JSON 物件"); continue
                for k in REQUIRED:
                    if k not in o:
                        errors.append(f"{loc}  缺必填欄位 '{k}'")
                for k in o:
                    if k not in ALLOWED:
                        errors.append(f"{loc}  未知欄位 '{k}'（拼錯或需先在 schema 註冊）")
                if "tags" in o:
                    if not isinstance(o["tags"], list) or not o["tags"]:
                        errors.append(f"{loc}  tags 必須是非空陣列")
                    elif len(o["tags"]) < 3:
                        warnings.append(f"{loc}  tags 少於 3 個，可搜性差（建議中英同義詞都放）")
                if "variants" in o and not isinstance(o["variants"], dict):
                    errors.append(f"{loc}  variants 必須是物件 {{名稱:註}}")
                if "stack" in o and not isinstance(o["stack"], list):
                    errors.append(f"{loc}  stack 必須是陣列")
                if "unverified" in o and not isinstance(o["unverified"], bool):
                    errors.append(f"{loc}  unverified 必須是 true/false")
                if "url" in o and not (isinstance(o["url"], str) and o["url"].startswith("http")):
                    errors.append(f"{loc}  url 必須是 http(s) 開頭的連結")
                c = o.get("cat")
                if isinstance(c, str) and c not in KNOWN_CATS:
                    warnings.append(f"{loc}  分類 '{c}' 不在已知清單（拼錯？或請加進 KNOWN_CATS）")
                nm = o.get("name")
                if isinstance(nm, str):
                    names.setdefault(nm.lower(), []).append(loc)
                rows.append((fn, loc, o))
                if o.get("url"):        stats["url"] += 1
                if o.get("look"):       stats["look"] += 1
                if o.get("unverified"): stats["unv"] += 1

    # 同一檔案內名稱重複才是問題；跨檔同名（如 AE 內建 Glow vs Universe Glow）是正常的
    for nm, locs in names.items():
        if len(locs) > 1:
            in_files = {l.split(":")[0] for l in locs}
            if len(in_files) < len(locs):
                errors.append(f"同檔內名稱重複 '{nm}'：{', '.join(locs)}")

    quality = quality_checks(rows)
    (errors if strict else warnings).extend(quality)

    print(f"檢查 {total} 筆 / {len(files)} 檔")
    for w in warnings: print("  ⚠ " + w)
    for e in errors:   print("  ✗ " + e)
    if errors:
        print(f"\n❌ {len(errors)} 個錯誤，{len(warnings)} 個警告"); sys.exit(1)
    print(f"\n✅ 全部通過（{len(warnings)} 個警告，不擋合併）")
    if stats:
        print(f"   涵蓋率：官方連結 {stats['url']}/{total}"
              f"｜外觀描述 {stats['look']}/{total}｜未驗證 {stats['unv']} 筆")

if __name__ == "__main__":
    main()
