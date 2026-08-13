#!/usr/bin/env python3
"""依資料來源與功能說明，回填 plugin/script/builtin/recipe 型態。"""
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
PLUGIN_FILES = {"red-giant.jsonl", "universe.jsonl", "sapphire.jsonl", "continuum.jsonl"}
SCRIPT_CATS = {"workflow", "rigging", "expression", "render", "utility"}
SCRIPT_WORDS = ("腳本", "script", "panel", "面板", "workflow", "工作流程", "automation", "自動化", "批次", "batch", "project", "專案", "layer manager", "圖層管理", "keyframe tool", "關鍵影格工具", "extension", "擴充功能", "dockable", "jsx", "cep panel")
PLUGIN_WORDS = ("外掛", "plugin", "plug-in", "effect", "濾鏡", "filter", ".aex", "gpu accelerated", "shader", "生成器", "generator", "transition plugin", "轉場外掛")

def classify(filename, row):
    if filename == "recipes.jsonl" or row.get("cat") == "recipe" or row.get("stack"):
        return "recipe"
    if filename == "builtin-ae.jsonl" or "helpx.adobe.com" in row.get("url", ""):
        return "builtin"
    if filename in PLUGIN_FILES or row.get("aex"):
        return "plugin"
    text = " ".join([row.get("name", ""), row.get("desc", ""), row.get("cat", ""), row.get("vendor", ""), row.get("suite", ""), " ".join(row.get("tags", []))]).lower()
    script_score = sum(word in text for word in SCRIPT_WORDS)
    plugin_score = sum(word in text for word in PLUGIN_WORDS)
    if row.get("cat") in SCRIPT_CATS:
        script_score += 2
    if row.get("unverified") and not row.get("aex"):
        script_score += 1
    return "script" if script_score > plugin_score else "plugin"

def main():
    counts = Counter()
    changed = 0
    for path in sorted(DATA.glob("*.jsonl")):
        rows = []
        for line in path.read_text(encoding="utf-8").splitlines():
            row = json.loads(line)
            kind = classify(path.name, row)
            if row.get("kind") != kind:
                changed += 1
            row["kind"] = kind
            ordered = {}
            for key in ("name", "suite", "vendor", "kind", "cat", "tags", "desc", "look", "variants", "stack", "builtin", "url", "unverified", "aex"):
                if key in row:
                    ordered[key] = row[key]
            ordered.update({k: v for k, v in row.items() if k not in ordered})
            rows.append(ordered)
            counts[kind] += 1
        path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8", newline="\n")
    print(f"updated {changed} entries")
    for kind in ("plugin", "script", "builtin", "recipe"):
        print(f"{kind}: {counts[kind]}")

if __name__ == "__main__":
    main()
