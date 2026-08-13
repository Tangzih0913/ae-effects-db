# EXPANSION.md — 持續擴充作業手冊

做資料擴充前，必須先完整讀 [`AGENTS.md`](AGENTS.md)。本檔只描述批次研究、決策、匯入與發佈流程；資料格式與硬性品質規則以 `AGENTS.md`、schema 與驗證器為準。

## 每輪流程

一般一批以 10～15 個「已作出收／不收決策的候選」為單位；使用者另有批量要求時從其指示。

1. 從官方產品線、官方效果清單或高訊號榜單取得候選。
2. 搜尋全部 `data/*.jsonl` 的 `name`、`variants`、官方 URL 與功能同義詞。
3. 回原廠頁確認 AE host、實際功能、是否仍販售，以及 URL 是否存在。
4. 收錄者寫入暫存 `batch.jsonl`，執行 `python tools/add.py batch.jsonl`。
5. 不收者把穩定 slug／識別字與具體理由追加到 `curation/skipped.tsv`。
6. 重建索引、完整驗證、提交並推送。
7. 等 GitHub Actions 與 Pages 完成，再驗證正式站。

`curation/skipped.tsv` 是長期決策記憶。不要只寫「不適合」；應寫明是 bundle、非 AE host、停售、無功能說明、太小眾，或與哪一筆高度重複。

## 候選來源優先順序

1. Adobe、Boris FX、Maxon 與既有主要廠商的最新版官方清單差異。
2. Rowbyte、Superluminal、Digital Anarchy、RE:Vision Effects、Video Copilot 等原廠產品線缺口。
3. LookAE 等列表只能用來發現名稱；所有事實一律回原廠確認。
4. aescripts 先看 viewed／bestselling 或明確分類中的高訊號產品；sitemap 尚有大量低命中候選，不優先掃。

來源進度（最後整理：2026-08-13）：

- LookAE After Effects 列表已掃到第 64 頁；
- c4dsky 的 After Effect、AE 插件、AE 腳本、AE 預設、Element 3D 分類已掃完；
- aescripts sitemap 尚有大量未評估頁面，只作低優先候選池；
- Adobe 目前效果清單、RE:Vision、Video Copilot 與 Frischluft 已做過一次差異檢查，但新版仍應依官方清單重跑差異。

## 官方來源技巧

| 來源 | 可靠做法 |
|---|---|
| aescripts | 先用 `python tools/find_new.py --limit 30 --desc`；slug 以 `tools/.sitemap_cache.xml`／官方 sitemap 為準。產品頁可用 Python `urllib` 帶 User-Agent 讀 meta description；若仍無實際說明就略過 |
| Sapphire | 比對官方 picture index 與 `data/sapphire.jsonl`；個別效果以官方 documentation 頁確認 |
| Continuum | 比對官方 BCC effects list 與 `data/continuum.jsonl`；不要自行推測新 ML 效果 slug |
| Maxon／Red Giant | 頁面由前端渲染時用瀏覽器檢查 DOM；路徑例外很多，不能依名稱拼網址 |
| Adobe 內建 | 以最新版官方 effect list 與分類頁為準；obsolete／legacy 不收，面板工具與效果選單項目要分開判斷 |
| 其他原廠 | 只接受原廠產品、文件或支援頁；轉售頁與第三方 host 宣稱不算證據 |

一次抓列表時控制在 3～4 頁，避免逾時。候選站若不適合出現在 repo，絕對不要把站名、連結或文案寫進資料與 curation 檔。

## 暫存批次格式

每行一個壓縮 JSON 物件；至少具備 `name`、`kind`、`cat`、`tags`、`desc`、`url`。完成匯入後刪除暫存批次檔，不要提交。

```bash
python tools/add.py batch.jsonl --dry-run
python tools/add.py batch.jsonl
```

匯入器會判重與選檔，但不能代替人工功能判斷。同名跨來源可能合法；功能相同但名稱不同也可能是重複。

## 完整驗證

```bash
python validate.py --strict
python tools/audit.py --strict
python tools/classify_kind.py
python -m unittest discover -s tests -v
node tests/check_web_js.js
python tools/build_index.py
git diff --check
```

若修改多語資料、官方分類或在地化網址，再執行：

```bash
node tools/build_localization.js --write
node tools/build_localization.js --check
```

若資料、熱門度、在地化或搜尋別名有更新，檢查 `index.html` 的 `ASSET_VERSION` 是否需要遞增，避免正式站使用舊快取。

## 發佈與正式站確認

先依使用者要求設定提交作者與 trailers，再提交並推送。不要假設一定走 main 或 PR；以當次維護流程為準。

```bash
git status -sb
git diff --cached --check
git commit
git push
```

推送後用 commit SHA 監看：

```bash
gh run list --commit <sha>
gh run watch <run-id> --exit-status
```

必須確認 validate、build-index 與 Pages 成功。最後直接抓正式站的 `dist/web-index.json`（附新的 cache-busting query）確認：

- 總筆數與本機一致；
- 本批所有新名稱存在；
- 同名跨來源條目仍可區分；
- 熱門清單與多語映射沒有失效；
- repo 工作樹乾淨，`HEAD` 與遠端分支一致。

## 每批回報格式

回報應包含：

- 收錄名稱；
- 略過 slug／名稱與逐筆具體理由；
- 最新總筆數與型態統計；
- 驗證、GitHub Actions、Pages 與正式站結果；
- commit 連結。
