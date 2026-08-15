#!/usr/bin/env python3
"""檢查工具型態；預設只報告，加入 ``--apply`` 才會寫回資料。"""
import argparse
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
PLUGIN_FILES = {"red-giant.jsonl", "universe.jsonl", "sapphire.jsonl", "continuum.jsonl"}
SCRIPT_CATS = {"workflow", "rigging", "expression", "render", "utility"}
SCRIPT_WORDS = ("腳本", "script", "panel", "面板", "workflow", "工作流程", "automation", "自動化", "批次", "batch", "project", "專案", "layer manager", "圖層管理", "keyframe tool", "關鍵影格工具", "extension", "擴充功能", "dockable", "jsx", "cep panel")
PLUGIN_WORDS = ("外掛", "plugin", "plug-in", "effect", "濾鏡", "filter", ".aex", "gpu accelerated", "shader", "生成器", "generator", "transition plugin", "轉場外掛")

# 這些廠商在資料庫中的收錄項目都是原生外掛。aescripts 上「效果」也常被
# 文案稱為 animation/tool，不能只靠關鍵字把它們降成腳本。
PLUGIN_ONLY_VENDORS = {"Digital Anarchy", "FxFactory", "RE:Vision Effects", "Rowbyte", "Superluminal"}

# 官方頁、安裝說明或檔案格式已逐筆確認的例外。混合式工具以主要介面判定：
# CEP／ScriptUI 面板仍歸 script；可從 Effect 選單套用的原生模組歸 plugin。
KIND_OVERRIDES = {
    "AfterCodecs": "plugin",
    "Auto Crop 3": "plugin",
    "AE Fusion 3D Bridge": "script",
    "AutoTargetUI": "script",
    "UI Mockup Builder": "script",
    "BAO Boa": "plugin",
    "BAO Bones": "plugin",
    "BAO Joint": "plugin",
    "BAO Layer Sculptor": "plugin",
    "BAO Mask 3D Warper": "plugin",
    "BAO Mask Avenger 2": "plugin",
    "Blob it!": "script",
    "Bowl Wobble": "script",
    "Change Default Easing for After Effects": "script",
    "ColorVSN": "plugin",
    "Depth Scanner 2": "plugin",
    "EZ3D": "script",
    "Face Swapper": "plugin",
    "Fixel DeLightIT 2": "plugin",
    "Fixel EdgeHancer 3": "plugin",
    "Fixel LightIT 2": "plugin",
    "Fluid": "plugin",
    "FoldLayers": "plugin",
    "Fluxion Warp": "plugin",
    "Fractal Noise 3D v2": "plugin",
    "Glaze": "plugin",
    "GPUResize": "plugin",
    "GlyphForge": "script",
    "Hacksaw": "plugin",
    "Holora": "plugin",
    "Influx": "plugin",
    "Interlaced Glitch": "plugin",
    "Island Chatter": "plugin",
    "Jlitch": "plugin",
    "LayerRender": "plugin",
    "loopFlow": "plugin",
    "MeltFlow Blur": "plugin",
    "NatuRamp": "plugin",
    "Newton 4": "plugin",
    "Paint & Stick 2": "plugin",
    "PathSmear": "plugin",
    "Pixel Melt": "plugin",
    "Pixelocybe": "plugin",
    "Pixion": "plugin",
    "Pixy Halftone": "plugin",
    "Plumebus": "plugin",
    "Power Cylinder": "plugin",
    "Power Hyperboloid": "plugin",
    "Ray Projector": "plugin",
    "Reflow": "plugin",
    "ReScanX": "plugin",
    "Risograph": "plugin",
    "SRT Importer for AE": "script",
    "NGS_EaseCraft": "script",
    "BPMc": "script",
    "MojiFlow": "script",
    "Cyberpunk One-Click Filter": "script",
    "Color Shifter": "script",
    "ぶんつむ": "script",
    "アニメの撮影用ツール": "script",
    "Transition Master 2 Basic / Pro": "plugin",
    "XDoG Studio": "plugin",
}

def classify(filename, row):
    if filename == "recipes.jsonl" or row.get("cat") == "recipe" or row.get("stack"):
        return "recipe"
    if filename == "builtin-ae.jsonl" or "helpx.adobe.com" in row.get("url", ""):
        return "builtin"
    if filename in PLUGIN_FILES or row.get("aex"):
        return "plugin"
    if row.get("name") in KIND_OVERRIDES:
        return KIND_OVERRIDES[row["name"]]
    if row.get("vendor") in PLUGIN_ONLY_VENDORS:
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
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--apply",
        action="store_true",
        help="套用建議型態；未指定時只列出差異，不修改檔案",
    )
    args = parser.parse_args()
    counts = Counter()
    changed = 0
    suggestions = []
    for path in sorted(DATA.glob("*.jsonl")):
        rows = []
        file_changed = False
        for line in path.read_text(encoding="utf-8").splitlines():
            row = json.loads(line)
            kind = classify(path.name, row)
            if row.get("kind") != kind:
                changed += 1
                suggestions.append((path.name, row.get("name", ""), row.get("kind"), kind))
                if args.apply:
                    row["kind"] = kind
                    file_changed = True
            ordered = {}
            for key in ("name", "suite", "vendor", "kind", "cat", "tags", "desc", "look", "variants", "stack", "builtin", "url", "unverified", "aex"):
                if key in row:
                    ordered[key] = row[key]
            ordered.update({k: v for k, v in row.items() if k not in ordered})
            rows.append(ordered)
            counts[kind] += 1
        if args.apply and file_changed:
            path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8", newline="\n")
    action = "updated" if args.apply else "suggested"
    print(f"{action} {changed} entries")
    for filename, name, old, new in suggestions:
        print(f"{filename}: {name}: {old} -> {new}")
    for kind in ("plugin", "script", "builtin", "recipe"):
        print(f"{kind}: {counts[kind]}")

if __name__ == "__main__":
    main()
