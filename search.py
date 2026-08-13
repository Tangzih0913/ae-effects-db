#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AE 特效資料庫 - 命令列搜尋
用法:
    python search.py 發光
    python search.py glow bloom          # 多關鍵字(OR)
    python search.py --cat transition 甩鏡
    python search.py --suite sapphire glow
    python search.py --kind script 關鍵影格
    python search.py --list-cats
無外部相依，純標準庫。搜尋 name / tags / desc / variants，中英皆可。
"""
import json, sys, os, glob, argparse

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

def load():
    rows = []
    for path in sorted(glob.glob(os.path.join(DATA_DIR, "*.jsonl"))):
        src = os.path.splitext(os.path.basename(path))[0]
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                obj["_src"] = src
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
    return " ".join(parts).lower()

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
    name = row.get("name", "").lower()
    tags = " ".join(row.get("tags", [])).lower()
    s = 0
    for t in terms:
        t = t.lower()
        if not t:
            continue
        if t in name:
            s += 5
        if t in tags:
            s += 3
        if t in text:
            s += 1
    return s

def main():
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("terms", nargs="*", help="關鍵字(中英皆可，多個為 OR)")
    ap.add_argument("--cat", help="限定分類 (glow/transition/particles/...)")
    ap.add_argument("--kind", choices=("plugin", "script", "builtin", "recipe"), help="限定工具型態")
    ap.add_argument("--suite", help="限定來源檔 (sapphire/continuum/universe/red-giant/builtin-ae/recipes/third-party)")
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

    scored = [(score(r, args.terms), r) for r in pool]
    scored = [x for x in scored if x[0] > 0]
    scored.sort(key=lambda x: -x[0])

    if not scored:
        segs = segment(args.terms)
        if segs:
            scored = [(score(r, segs), r) for r in pool]
            scored = [x for x in scored if x[0] > 0]
            scored.sort(key=lambda x: -x[0])
            if scored:
                print(f"找不到「{' '.join(args.terms)}」，已自動拆詞：{'、'.join(segs)}\n")

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
