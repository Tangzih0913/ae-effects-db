#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""驗證 data/*.jsonl 的格式與策展品質。

用法：
    python validate.py
    python validate.py --strict

一般模式把品質問題列為警告；strict 模式會把警告視為錯誤，供 CI 使用。
"""

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

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT, "data")

KNOWN_CATS = {
    "glow", "blur-glow", "light", "flare", "particles", "stylize", "film",
    "color", "blur", "warp", "keying", "tracking", "restore", "time",
    "transition", "text", "generate", "3d", "draw", "paint", "art",
    "texture", "audio", "physics", "rigging", "workflow", "render",
    "expression", "animation", "preset", "utility", "distort", "mograph",
    "beauty", "edge", "emboss", "composite", "matte", "perspective",
    "kaleido", "vr", "recipe",
}
KNOWN_KINDS = {"plugin", "script", "builtin", "recipe"}
REQUIRED = ("name", "kind", "cat", "tags", "desc", "url")
OPTIONAL = {
    "look", "variants", "stack", "builtin", "suite", "vendor",
    "unverified", "aex",
}
ALLOWED = set(REQUIRED) | OPTIONAL

CJK = re.compile(r"[\u3400-\u9fff]")
DISCONTINUED = re.compile(
    r"(?:已停售|已下架|停止販售|discontinued|no longer available)", re.I
)


def valid_url(value: object) -> bool:
    if not isinstance(value, str):
        return False
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def quality_checks(rows: list[tuple[str, str, dict]]) -> list[str]:
    warnings: list[str] = []

    no_cjk = [loc for _, loc, item in rows if not any(CJK.search(str(t)) for t in item["tags"])]
    if no_cjk:
        sample = "、".join(no_cjk[:5])
        more = "…" if len(no_cjk) > 5 else ""
        warnings.append(f"{len(no_cjk)} 筆 tags 沒有中文搜尋詞：{sample}{more}")

    unverified = [loc for _, loc, item in rows if item.get("unverified")]
    if unverified:
        sample = "、".join(unverified[:5])
        more = "…" if len(unverified) > 5 else ""
        warnings.append(f"{len(unverified)} 筆仍標為 unverified：{sample}{more}")

    # 防止以「風格 × 動畫」笛卡兒積灌水；變體應收在單一條目的 variants。
    generated = [loc for _, loc, item in rows if item.get("kind") == "recipe" and "・" in item["name"]]
    if generated:
        warnings.append(
            f"{len(generated)} 筆配方名稱疑似排列組合產物，請改用 variants："
            + "、".join(generated[:5])
        )

    return warnings


def main() -> None:
    strict = "--strict" in sys.argv
    errors: list[str] = []
    warnings: list[str] = []
    rows: list[tuple[str, str, dict]] = []
    names: dict[str, list[str]] = collections.defaultdict(list)
    total = 0
    stats = collections.Counter()

    files = sorted(glob.glob(os.path.join(DATA_DIR, "*.jsonl")))
    if not files:
        print("找不到 data/*.jsonl")
        raise SystemExit(1)

    for path in files:
        filename = os.path.basename(path)
        with open(path, encoding="utf-8") as handle:
            for line_no, raw in enumerate(handle, 1):
                if not raw.strip():
                    continue
                total += 1
                loc = f"{filename}:{line_no}"
                try:
                    item = json.loads(raw)
                except json.JSONDecodeError as exc:
                    errors.append(f"{loc} JSON 格式錯誤：{exc}")
                    continue
                if not isinstance(item, dict):
                    errors.append(f"{loc} 必須是 JSON 物件")
                    continue

                missing = [key for key in REQUIRED if key not in item]
                if missing:
                    errors.append(f"{loc} 缺少欄位：{', '.join(missing)}")
                unknown = sorted(set(item) - ALLOWED)
                if unknown:
                    errors.append(f"{loc} 未知欄位：{', '.join(unknown)}")

                name = item.get("name")
                if not isinstance(name, str) or not name.strip():
                    errors.append(f"{loc} name 必須是非空字串")
                else:
                    names[name.strip().casefold()].append(loc)

                kind = item.get("kind")
                if kind not in KNOWN_KINDS:
                    errors.append(f"{loc} kind 必須是 plugin/script/builtin/recipe")

                cat = item.get("cat")
                if not isinstance(cat, str) or cat not in KNOWN_CATS:
                    errors.append(f"{loc} 未知分類：{cat!r}")

                tags = item.get("tags")
                if not isinstance(tags, list) or not all(isinstance(tag, str) and tag.strip() for tag in tags):
                    errors.append(f"{loc} tags 必須是非空字串陣列")
                elif len(tags) < 5:
                    errors.append(f"{loc} tags 至少需要 5 個，目前 {len(tags)} 個")

                desc = item.get("desc")
                if not isinstance(desc, str) or not desc.strip():
                    errors.append(f"{loc} desc 必須是非空字串")
                elif DISCONTINUED.search(desc):
                    errors.append(f"{loc} desc 顯示產品已停售／下架，不應收錄")

                if not valid_url(item.get("url")):
                    errors.append(f"{loc} url 必須是完整的 http(s) 官方連結")
                if "variants" in item and not isinstance(item["variants"], dict):
                    errors.append(f"{loc} variants 必須是物件")
                if "stack" in item and not isinstance(item["stack"], list):
                    errors.append(f"{loc} stack 必須是陣列")
                if "unverified" in item and not isinstance(item["unverified"], bool):
                    errors.append(f"{loc} unverified 必須是 true/false")

                # 檔案即是資料分區，避免前端來源與型態互相矛盾。
                if kind == "builtin" and filename != "builtin-ae.jsonl":
                    errors.append(f"{loc} builtin 條目必須放在 builtin-ae.jsonl")
                if kind == "recipe" and filename != "recipes.jsonl":
                    errors.append(f"{loc} recipe 條目必須放在 recipes.jsonl")
                if filename == "builtin-ae.jsonl" and kind != "builtin":
                    errors.append(f"{loc} builtin-ae.jsonl 只能包含 builtin")
                if filename == "recipes.jsonl" and kind != "recipe":
                    errors.append(f"{loc} recipes.jsonl 只能包含 recipe")

                rows.append((filename, loc, item))
                stats[kind] += 1
                stats["url"] += bool(item.get("url"))

    for normalized, locs in names.items():
        if len(locs) > 1:
            per_file = collections.Counter(loc.split(":", 1)[0] for loc in locs)
            if any(count > 1 for count in per_file.values()):
                errors.append(f"同一資料檔重複名稱 {normalized!r}：{', '.join(locs)}")

    warnings.extend(quality_checks(rows))
    if strict and warnings:
        errors.extend(warnings)
        warnings = []

    print(f"檢查 {total} 筆 / {len(files)} 個資料檔")
    for warning in warnings:
        print("  ⚠ " + warning)
    for error in errors:
        print("  ✗ " + error)

    if errors:
        print(f"\n失敗：{len(errors)} 個錯誤、{len(warnings)} 個警告")
        raise SystemExit(1)

    print(f"\n通過：{len(warnings)} 個警告")
    print(
        "   型態："
        f"外掛 {stats['plugin']} / 腳本 {stats['script']} / "
        f"內建 {stats['builtin']} / 配方 {stats['recipe']}；"
        f"官方連結 {stats['url']}/{total}"
    )


if __name__ == "__main__":
    main()
