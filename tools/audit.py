#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""產生 AE 特效資料庫的唯讀品質盤點報告。"""

from __future__ import annotations

import collections
import glob
import json
import os
import re
import sys
from urllib.parse import urlparse

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
DISCONTINUED = re.compile(
    r"(?:已停售|已下架|停止販售|discontinued|no longer available)", re.I
)


def main() -> None:
    rows: list[tuple[str, dict]] = []
    for path in sorted(glob.glob(os.path.join(DATA, "*.jsonl"))):
        filename = os.path.basename(path)
        with open(path, encoding="utf-8") as handle:
            for raw in handle:
                if raw.strip():
                    rows.append((filename, json.loads(raw)))

    by_file = collections.Counter(filename for filename, _ in rows)
    by_kind = collections.Counter(item.get("kind", "(missing)") for _, item in rows)
    by_cat = collections.Counter(item.get("cat", "(missing)") for _, item in rows)
    by_host = collections.Counter(urlparse(item.get("url", "")).netloc for _, item in rows)
    names: dict[str, list[str]] = collections.defaultdict(list)
    for filename, item in rows:
        names[item.get("name", "").strip().casefold()].append(filename)

    checks = {
        "缺少 URL": [item["name"] for _, item in rows if not item.get("url")],
        "tags 少於 5 個": [item["name"] for _, item in rows if len(item.get("tags", [])) < 5],
        "仍標示 unverified": [item["name"] for _, item in rows if item.get("unverified")],
        "停售／下架文字": [item["name"] for _, item in rows if DISCONTINUED.search(item.get("desc", ""))],
        "排列組合式配方": [
            item["name"] for _, item in rows
            if item.get("kind") == "recipe" and "・" in item.get("name", "")
        ],
        "同檔重複名稱": [
            name for name, files in names.items()
            if any(count > 1 for count in collections.Counter(files).values())
        ],
    }

    print(f"總筆數：{len(rows):,}（{len(by_file)} 個資料檔）")
    print("型態：" + " / ".join(f"{key} {value:,}" for key, value in by_kind.most_common()))
    print("\n資料檔：")
    for key, value in by_file.most_common():
        print(f"  {key:<22} {value:>5,}")
    print("\n前 12 大分類：")
    print("  " + " / ".join(f"{key} {value:,}" for key, value in by_cat.most_common(12)))
    print("\n前 10 大官方網域：")
    for key, value in by_host.most_common(10):
        print(f"  {key:<34} {value:>5,}")
    print("\n品質檢查：")
    for label, items in checks.items():
        suffix = "" if not items else " — " + "、".join(items[:5]) + ("…" if len(items) > 5 else "")
        print(f"  {label}: {len(items)}{suffix}")


if __name__ == "__main__":
    main()
