#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安全新增條目：自動判重、檢查欄位、放進正確的資料檔。

用法：
    python tools/add.py new.jsonl                 # 從檔案讀入（每行一筆 JSON）
    echo '{"name":...}' | python tools/add.py -    # 從 stdin 讀入
    python tools/add.py new.jsonl --file aescripts # 強制指定目標檔
    python tools/add.py new.jsonl --dry            # 只檢查不寫入

會自動判斷該進哪個資料檔（依 url / vendor / suite），並拒絕重複名稱。
"""
import json, os, re, sys, glob, argparse

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
REQUIRED = ("name", "cat", "tags", "desc")
ORDER = ["name","suite","vendor","cat","tags","desc","look","variants","stack","builtin","url","unverified","aex"]

def guess_file(o):
    u, v, s = o.get("url",""), o.get("vendor",""), o.get("suite","")
    if "borisfx.com/documentation/sapphire" in u: return "sapphire"
    if "borisfx.com/documentation/continuum" in u: return "continuum"
    if "helpx.adobe.com" in u: return "builtin-ae"
    if "maxon.net" in u and "/universe/" in u: return "universe"
    if "maxon.net" in u: return "red-giant"
    if "Trapcode" in s or "Magic Bullet" in s or "VFX Suite" in s: return "red-giant"
    if o.get("stack") or o.get("cat") == "recipe": return "recipes"
    if "aescripts.com" in u: return "aescripts"
    if o.get("unverified") or o.get("aex"): return "installed"
    return "third-party"

def load_existing():
    names = {}
    for p in glob.glob(os.path.join(DATA, "*.jsonl")):
        for i, line in enumerate(open(p, encoding="utf-8"), 1):
            line = line.strip()
            if line:
                names[json.loads(line)["name"].strip().lower()] = f"{os.path.basename(p)}:{i}"
    return names

def reorder(o):
    new = {k: o[k] for k in ORDER if k in o}
    for k in o:
        if k not in new:
            new[k] = o[k]
    return new

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src", help="來源 .jsonl 檔，或 - 代表 stdin")
    ap.add_argument("--file", help="強制指定目標資料檔（不含副檔名）")
    ap.add_argument("--dry", action="store_true", help="只檢查不寫入")
    a = ap.parse_args()

    # Windows 主控台預設編碼會把中文變成 surrogate，一律以 UTF-8 讀取
    raw = sys.stdin.buffer.read().decode("utf-8") if a.src == "-" else open(a.src, encoding="utf-8").read()
    existing = load_existing()
    buckets, added, skipped, errors = {}, [], [], []

    for n, line in enumerate(raw.splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            o = json.loads(line)
        except json.JSONDecodeError as e:
            errors.append(f"第{n}行 JSON 解析失敗：{e}"); continue
        miss = [k for k in REQUIRED if k not in o]
        if miss:
            errors.append(f"第{n}行 缺欄位 {miss}"); continue
        if len(o.get("tags", [])) < 3:
            errors.append(f"第{n}行 '{o['name']}' tags 少於 3 個"); continue
        if o.get("url") and not o["url"].startswith("http"):
            errors.append(f"第{n}行 '{o['name']}' url 格式不對"); continue
        key = o["name"].strip().lower()
        if key in existing:
            skipped.append(f"{o['name']}（已存在於 {existing[key]}）"); continue
        target = a.file or guess_file(o)
        buckets.setdefault(target, []).append(reorder(o))
        existing[key] = f"{target}.jsonl:new"
        added.append(f"{o['name']} → {target}.jsonl")

    for line in errors: print("  ✗ " + line)
    for line in skipped: print("  ↷ 略過 " + line)
    for line in added:  print("  ✔ " + line)

    if errors:
        print(f"\n❌ 有 {len(errors)} 個錯誤，未寫入任何資料"); sys.exit(1)
    if a.dry:
        print(f"\n(--dry) 檢查通過，可新增 {len(added)} 筆"); return
    for target, rows in buckets.items():
        path = os.path.join(DATA, target + ".jsonl")
        with open(path, "a", encoding="utf-8", newline="\n") as f:
            for o in rows:
                f.write(json.dumps(o, ensure_ascii=False) + "\n")
    print(f"\n✅ 新增 {len(added)} 筆、略過重複 {len(skipped)} 筆。請接著執行：python validate.py")

if __name__ == "__main__":
    main()
