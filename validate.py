#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
校驗 data/*.jsonl：每行是否為合法 JSON、必填欄位、型別、分類、重複名稱。
用法：  python validate.py
CI 與送 PR 前都會跑這支。有 error 會 exit 1。
"""
import json, sys, os, glob

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

def main():
    errors, warnings, total = [], [], 0
    names = {}
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

    for nm, locs in names.items():
        if len(locs) > 1:
            warnings.append(f"名稱重複 '{nm}'：{', '.join(locs)}")

    print(f"檢查 {total} 筆 / {len(files)} 檔")
    for w in warnings: print("  ⚠ " + w)
    for e in errors:   print("  ✗ " + e)
    if errors:
        print(f"\n❌ {len(errors)} 個錯誤，{len(warnings)} 個警告"); sys.exit(1)
    print(f"\n✅ 全部通過（{len(warnings)} 個警告，不擋合併）")

if __name__ == "__main__":
    main()
