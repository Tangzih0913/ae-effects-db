#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""批次加入候選條目，自動判重並選擇資料檔。

用法：
    python tools/add.py batch.jsonl
    python tools/add.py batch.jsonl --dry
    python tools/add.py batch.jsonl --file aescripts
    Get-Content batch.jsonl | python tools/add.py -
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import sys
from urllib.parse import urlparse

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
REQUIRED = ("name", "kind", "cat", "tags", "desc", "url")
ORDER = [
    "name", "suite", "vendor", "kind", "cat", "tags", "desc", "look",
    "variants", "stack", "builtin", "url", "unverified", "aex",
]


def valid_url(value: object) -> bool:
    if not isinstance(value, str):
        return False
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def guess_file(item: dict) -> str:
    url = item.get("url", "")
    suite = item.get("suite", "")
    if item.get("kind") == "recipe" or item.get("stack") or item.get("cat") == "recipe":
        return "recipes"
    if item.get("kind") == "builtin":
        return "builtin-ae"
    if "borisfx.com/documentation/sapphire" in url:
        return "sapphire"
    if "borisfx.com/documentation/continuum" in url:
        return "continuum"
    if "helpx.adobe.com" in url:
        return "builtin-ae"
    if "maxon.net" in url and "/universe/" in url:
        return "universe"
    if "maxon.net" in url or any(name in suite for name in ("Trapcode", "Magic Bullet", "VFX Suite")):
        return "red-giant"
    if "aescripts.com" in url:
        return "aescripts"
    if item.get("unverified") or item.get("aex"):
        return "installed"
    return "third-party"


def load_existing() -> dict[str, str]:
    names: dict[str, str] = {}
    for path in glob.glob(os.path.join(DATA, "*.jsonl")):
        with open(path, encoding="utf-8") as handle:
            for line_no, raw in enumerate(handle, 1):
                if raw.strip():
                    item = json.loads(raw)
                    names[item["name"].strip().casefold()] = f"{os.path.basename(path)}:{line_no}"
    return names


def reorder(item: dict) -> dict:
    ordered = {key: item[key] for key in ORDER if key in item}
    ordered.update({key: value for key, value in item.items() if key not in ordered})
    return ordered


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("src", help="JSONL 檔案，或用 - 讀取 stdin")
    parser.add_argument("--file", help="強制寫入指定的 data/<name>.jsonl")
    parser.add_argument("--dry", action="store_true", help="只預覽，不寫入")
    args = parser.parse_args()

    raw = (
        sys.stdin.buffer.read().decode("utf-8-sig")
        if args.src == "-"
        else open(args.src, encoding="utf-8-sig").read()
    )
    existing = load_existing()
    buckets: dict[str, list[dict]] = {}
    added: list[str] = []
    skipped: list[str] = []
    errors: list[str] = []

    for line_no, raw_line in enumerate(raw.splitlines(), 1):
        line = raw_line.strip()
        if not line:
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"第 {line_no} 行 JSON 格式錯誤：{exc}")
            continue
        if not isinstance(item, dict):
            errors.append(f"第 {line_no} 行必須是 JSON 物件")
            continue

        missing = [key for key in REQUIRED if key not in item]
        if missing:
            errors.append(f"第 {line_no} 行缺少欄位：{', '.join(missing)}")
            continue
        if not isinstance(item.get("tags"), list) or len(item["tags"]) < 5:
            errors.append(f"第 {line_no} 行「{item.get('name', '?')}」至少需要 5 個 tags")
            continue
        if not valid_url(item.get("url")):
            errors.append(f"第 {line_no} 行「{item.get('name', '?')}」缺少有效官方 URL")
            continue

        key = str(item["name"]).strip().casefold()
        if key in existing:
            skipped.append(f"{item['name']}（已存在：{existing[key]}）")
            continue

        target = args.file or guess_file(item)
        buckets.setdefault(target, []).append(reorder(item))
        existing[key] = f"{target}.jsonl:new"
        added.append(f"{item['name']} → {target}.jsonl")

    for message in errors:
        print("  ✗ " + message)
    for message in skipped:
        print("  ↷ 略過 " + message)
    for message in added:
        print("  ✓ " + message)

    if errors:
        print(f"\n失敗：{len(errors)} 個錯誤，未寫入任何資料")
        raise SystemExit(1)
    if args.dry:
        print(f"\n（dry-run）可加入 {len(added)} 筆")
        return

    for target, items in buckets.items():
        path = os.path.join(DATA, target + ".jsonl")
        with open(path, "a", encoding="utf-8", newline="\n") as handle:
            for item in items:
                handle.write(json.dumps(item, ensure_ascii=False) + "\n")
    print(f"\n完成：加入 {len(added)} 筆，略過 {len(skipped)} 筆；請執行 python validate.py --strict")


if __name__ == "__main__":
    main()
