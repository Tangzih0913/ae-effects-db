# 擴充作業手冊（給專門擴充資料庫的工作階段）

> 這份是「持續擴大資料庫」的標準流程。新開一個對話要做擴充時，先讀這份 +
> [AGENTS.md](AGENTS.md)（格式規範），就能直接開工，不用重新摸索。

## 一輪標準流程

```bash
python tools/find_new.py --limit 30 --desc     # 1. 取出待評估清單＋官方說明
# 2. 逐一判斷收/不收（標準見下）
python tools/add.py batch.jsonl                # 3. 收的：寫成 JSONL 後匯入（自動判重+選檔）
#    不收的：把 slug 與原因寫進 curation/skipped.tsv
python validate.py                             # 4. 校驗
git add -A && git commit -m "Add N plugins: ..." && git push
```

推上去後 GitHub Pages 約 40–70 秒自動重建。驗證：開
https://xup61069.github.io/ae-effects-db/ 搜新加的關鍵字（若看到舊資料，網址加 `?v=2` 避開快取）。

## 收錄判斷標準

**收**（要同時成立）
- 尚未收錄，且與現有條目功能沒有高度重複
- 功能實用、有代表性（暢銷／常被討論／解決常見需求）
- 是真的能在 After Effects 用的外掛或腳本

**不收**（寫進 `curation/skipped.tsv` 並註明原因）
- 純預設包／素材包／模板／教學，而非工具本身
- 套裝包（bundle）——個別工具已收錄就好
- 其他軟體專用（Premiere / Photoshop / Resolve / Audition / Cavalry…）
- 官方頁查不到實際功能說明（不要用猜的硬收）
- 極小眾（例：特定語系排版工具）或功能與既有條目重複

> `curation/skipped.tsv` 是「決策記憶」——寫進去之後 `find_new.py` 就不會再問第二次。
> 改變主意就把那行刪掉，它會重新出現在待評估清單。

## 資料品質要求（每一筆）

| 欄位 | 要求 |
|---|---|
| `kind` | 必填：`plugin` 外掛／效果、`script` 腳本／面板、`builtin` AE 內建、`recipe` 效果配方 |
| `desc` | 繁體中文一句話：**做什麼 ＋ 典型用途**。不要只寫功能名詞 |
| `tags` | **中英混合 ≥5 個**：英文名、中文名、俗名、用途、外觀。這是搜尋命中的關鍵 |
| `url` | **必填**，官方產品頁，且必須真實存在（不要憑 slug 猜） |
| `look` | 建議填：畫面看起來像什麼 |
| `vendor` | 作者／廠商；不確定就寫 `aescripts` 或 `未知/免費` |

## 各來源怎麼取得正確資料（踩過的坑）

| 來源 | 方法 |
|---|---|
| **aescripts** | slug 清單用 `https://aescripts.com/media/sitemap/sitemap.xml`（主站 `/sitemap.xml` 被 Cloudflare 擋，這支 curl 可過）。產品說明抓該頁 `<meta name="description">` |
| **Boris Sapphire** | 官方 picture-index 頁抓 doc 連結；效果頁 = `/documentation/sapphire/ae/<去掉S_的小寫名>/` |
| **Boris Continuum** | 官方 bcc-effects-list 抓連結；新 ML 工具的 slug 常不同（如 `bcc-witnessprotection`），要個別實測 |
| **Maxon Universe / Red Giant** | 網站是前端渲染，**curl 抓不到連結，要用瀏覽器讀 DOM**。slug 有例外（`symbol-mapper-tool`）。Red Giant 現在的路徑是 `/product-detail/red-giant/<類別>/<工具>` |
| **Adobe 內建** | `helpx.adobe.com` 的 curl 會卡住，要用瀏覽器；分類頁在 `.../list-of-effects/<分類>-effects.html` |
| **其他廠商** | 一律連原廠官網，不要連轉售頁 |

**鐵則：URL 一律驗證過才寫入**（HTTP 200 或出現在官方索引），絕不憑名稱猜 slug。

## 還沒掃過的方向（下次可以往這裡挖）

- [ ] aescripts 依分類逐類掃（Text / Particles / Keying / Color…），比只看熱門榜更全面
- [ ] Rowbyte、Superluminal、Digital Anarchy、RE:Vision 的其他產品線
- [ ] Video Copilot 全產品線複查
- [ ] Boris FX Sapphire / Continuum 新版新增的效果（每年更新）
- [x] `data/installed.jsonl` 的 `unverified` 條目已完成查證或依規則移除（2026-08）
- [ ] `data/builtin-ae.jsonl` 若有 AE 新版新增效果，補進來

## 目前規模

執行 `python validate.py --strict` 會印出即時統計；`python tools/audit.py` 另列資料檔、型態、分類、官方網域與品質風險。
