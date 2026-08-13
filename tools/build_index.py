#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
產生給 AI 讀的合併檔（每次資料變動後執行；CI 也會自動跑）：

  dist/all.jsonl   全部條目合併成一檔，欄位完整（給有大上下文的 AI / 工具用）
  dist/index.txt   精簡索引：名稱｜來源｜分類｜說明｜官方連結（省 token，適合一般 AI）

放在 dist/ 而不是 data/，是為了避免 search.py / validate.py 等工具重複讀到同一批資料。

用法：python tools/build_index.py
"""
import json, os, glob, sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
DIST = os.path.join(ROOT, "dist")
SRC_LABEL = {
    "red-giant": "Red Giant", "universe": "Universe", "sapphire": "Sapphire",
    "continuum": "Continuum", "builtin-ae": "AE內建", "aescripts": "aescripts",
    "third-party": "第三方", "installed": "未驗證", "recipes": "配方",
}

def main():
    rows = []
    for path in sorted(glob.glob(os.path.join(DATA, "*.jsonl"))):
        src = os.path.splitext(os.path.basename(path))[0]
        for line in open(path, encoding="utf-8"):
            line = line.strip()
            if line:
                o = json.loads(line)
                o["src"] = SRC_LABEL.get(src, src)
                rows.append(o)

    os.makedirs(DIST, exist_ok=True)
    with open(os.path.join(DIST, "all.jsonl"), "w", encoding="utf-8", newline="\n") as f:
        for o in rows:
            f.write(json.dumps(o, ensure_ascii=False) + "\n")

    head = (
        "# After Effects 特效／外掛索引（繁體中文）\n"
        f"# 共 {len(rows)} 筆　格式：名稱｜來源｜型態｜分類｜說明｜官方連結\n"
        "# 完整資料（含中英搜尋標籤、外觀描述）：dist/all.jsonl\n"
        "# 線上搜尋：https://xup61069.github.io/ae-effects-db/\n"
    )
    with open(os.path.join(DIST, "index.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write(head)
        for o in rows:
            f.write(f"{o['name']}｜{o['src']}｜{o.get('kind','')}｜{o.get('cat','')}｜{o.get('desc','')}｜{o.get('url','')}\n")

    a = os.path.getsize(os.path.join(DIST, "all.jsonl")) / 1024
    b = os.path.getsize(os.path.join(DIST, "index.txt")) / 1024
    print(f"✅ dist/all.jsonl（{len(rows)} 筆，{a:.0f} KB）")
    print(f"✅ dist/index.txt（精簡索引，{b:.0f} KB）")

if __name__ == "__main__":
    main()
