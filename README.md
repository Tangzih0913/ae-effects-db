# AE 特效資料庫

[![資料驗證](https://github.com/xup61069/ae-effects-db/actions/workflows/validate.yml/badge.svg)](https://github.com/xup61069/ae-effects-db/actions/workflows/validate.yml)
[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

用文字描述、用途或畫面特徵，搜尋 After Effects 外掛、腳本、內建效果與效果配方。資料逐筆策展，收錄繁體中文說明、中英搜尋詞與已查證的官方連結。

## 直接使用

### [開啟線上搜尋](https://xup61069.github.io/ae-effects-db/)

免安裝、免登入，支援繁體中文、英文與日文介面。預設依「精選熱門」排序，也可切換搜尋相關度、名稱、分類、來源與官方日期。

熱門分數由人工精選、來源權重、資料完整度、官方更新日期與策展順序構成，計算規則集中在 [`curation/popularity.json`](curation/popularity.json)；它是方便探索的策展排序，不代表下載量、銷量或客觀市場排名。

網頁另提供：

- 外掛、腳本、AE 內建與配方的獨立底色及型態篩選；
- 42 種功能分類、來源篩選、錯字修正與繁簡中文搜尋；
- 收藏匯出／匯入、2～4 筆並排比較與可分享網址；
- 經驗證的日文官方頁，以及 Adobe 內建效果的英文／日文官方分類。

## 選一個入口

| 需求 | 入口 |
|---|---|
| 直接找效果 | [線上搜尋](https://xup61069.github.io/ae-effects-db/) |
| 在終端機搜尋 | [`search.py`](search.py) |
| 把資料庫交給一般 AI | [`PROMPT.md`](PROMPT.md) |
| 讓 AI／coding agent 維護 repo | [`AGENTS.md`](AGENTS.md) |
| 持續擴充資料 | [`EXPANSION.md`](EXPANSION.md) |
| 給可讀網址的 AI 一個精簡入口 | [`llms.txt`](llms.txt) |
| 貢獻資料或修正 | [`CONTRIBUTING.md`](CONTRIBUTING.md) |
| 多語系與官方翻譯政策 | [`LOCALIZATION.md`](LOCALIZATION.md) |

## 命令列搜尋

```bash
python search.py 發光
python search.py neon glow          # 多詞預設 AND；無結果才明確退回 OR
python search.py --any glow bloom   # 強制 OR
python search.py --kind script 字幕
python search.py --cat transition 甩鏡
python search.py --suite sapphire glow
python search.py --list-cats
```

本機預覽網頁不能直接使用 `file://`，請在 repo 根目錄啟動 HTTP server：

```bash
python -m http.server 8000
```

再開啟 <http://localhost:8000>。

## AI 可讀資料

- [`dist/index.txt`](dist/index.txt)：精簡索引，包含名稱、來源、型態、分類、說明與官方連結；檔頭會顯示即時總筆數。
- [`dist/all.jsonl`](dist/all.jsonl)：完整合併資料，保留 tags、look、variants、日期等欄位。
- [`dist/web-index.json`](dist/web-index.json)：已預建搜尋字串與熱門順位的網頁索引。
- [`schema/effect.schema.json`](schema/effect.schema.json)：單筆 JSON 的機器可讀規格。

`dist/` 由 `python tools/build_index.py` 產生，不是第二份資料來源；真正的來源是 `data/*.jsonl`。

## 資料分區

| 檔案 | 內容 |
|---|---|
| `data/red-giant.jsonl` | Trapcode、Magic Bullet、VFX Suite |
| `data/universe.jsonl` | Maxon Universe |
| `data/sapphire.jsonl` | Boris FX Sapphire |
| `data/continuum.jsonl` | Boris FX Continuum |
| `data/builtin-ae.jsonl` | Adobe After Effects 內建效果與工具 |
| `data/aescripts.jsonl` | aescripts 上的外掛與腳本 |
| `data/third-party.jsonl` | 其他原廠產品 |
| `data/installed.jsonl` | 從實際安裝環境辨識後、無法歸入前述產品線的工具 |
| `data/recipes.jsonl` | 畫面感與效果堆疊配方 |

目前精確筆數與品質狀態請以這兩個指令為準：

```bash
python validate.py --strict
python tools/audit.py --strict
```

## 單筆格式

JSONL 一行一筆；必填欄位為 `name`、`kind`、`cat`、`tags`、`desc`、`url`。

```json
{"name":"S_Glow","suite":"Sapphire","kind":"plugin","cat":"glow","tags":["glow","bloom","發光","輝光","光暈"],"desc":"讓亮部自然向外溢光，適合霓虹、標題與高光強化。","url":"https://borisfx.com/documentation/sapphire/ae/glow/"}
```

新增資料請使用安全匯入器，讓它先做 schema 檢查、判重與選檔：

```bash
python tools/add.py batch.jsonl
python validate.py --strict
python tools/audit.py --strict
python tools/build_index.py
```

完整的收錄與略過標準見 [`AGENTS.md`](AGENTS.md) 與 [`EXPANSION.md`](EXPANSION.md)。刻意不收的候選會連同具體原因記在 [`curation/skipped.tsv`](curation/skipped.tsv)，避免後續 AI 重複評估。

## 主要官方來源

- [Adobe After Effects effects list](https://helpx.adobe.com/after-effects/desktop/apply-effects-and-animation-presets/effects-and-animation-presets/effect-list.html)
- [Boris FX Sapphire picture index](https://borisfx.com/documentation/sapphire/ae/picture-index/)
- [Boris FX Continuum effects list](https://borisfx.com/documentation/continuum/bcc-effects-list/)
- [Maxon Universe tools](https://www.maxon.net/en/product-detail/red-giant/universe/tools)
- [aescripts](https://aescripts.com/)

## 維護者與授權

本資料庫由 **Kadid**（[@xup61069](https://github.com/xup61069)）、**Codex**（OpenAI）與 **Claude**（Anthropic）共同整理。程式碼與資料整理採 [MIT License](LICENSE)；產品名稱與商標歸各原廠所有。本 repo 只提供索引與教學資訊，不包含外掛程式、素材或任何非官方下載。
