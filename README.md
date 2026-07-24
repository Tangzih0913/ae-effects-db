# AE 特效資料庫 (ae-effects-db)

用「文字描述」或「參考圖」找 After Effects 特效的本地知識庫。
三種用法：**網頁搜尋**（手機/瀏覽器）、**命令列**（終端機/腳本）、**Claude Code `/find-effect` skill**（可貼圖搜尋）。

> 522 筆條目，涵蓋約 900+ 個特效（同族變體收合），資料於 2026-07 整理自各廠商官方最新清單。

## 三種搜尋方式

### 1. 網頁（最萬用，可放 GitHub Pages）
打開 `index.html` 即可即時搜尋（中英皆可、分類/來源篩選、關鍵字高亮）。
> 因瀏覽器安全限制，需經 HTTP 開啟，不能直接雙擊 `file://`。本機測試：
> ```bash
> python -m http.server 8000
> ```
> 然後開 http://localhost:8000 。推上 GitHub 後開啟 Pages 即有公開網址。

### 2. 命令列
```bash
python search.py 發光              # 中文
python search.py neon glow         # 英文多關鍵字(OR)
python search.py --cat transition 甩鏡
python search.py --suite sapphire glow
python search.py --list-cats       # 看所有分類
```

### 3. Claude Code `/find-effect`
在本專案裡直接說「找 XX 效果」或**貼一張參考圖**，skill 會分析畫面特徵→比對資料庫→給推薦與參數方向，還能透過 AE MCP 直接套用。
skill 檔：[`skill/find-effect/SKILL.md`](skill/find-effect/SKILL.md)（要用的話複製到你的 `.claude/skills/`，並把裡面的資料路徑改成你放 `data/` 的位置）。

## 資料涵蓋

| 檔案 | 內容 | 來源 |
|---|---|---|
| `data/red-giant.jsonl` | Trapcode / Magic Bullet / VFX Suite | Maxon (Red Giant) |
| `data/universe.jsonl` | Universe 全部工具 | Maxon (Red Giant) |
| `data/sapphire.jsonl` | Sapphire 約 270 效果 | Boris FX |
| `data/continuum.jsonl` | Continuum (BCC/BCC+) 約 330 效果 | Boris FX |
| `data/builtin-ae.jsonl` | **AE 內建效果**（沒買外掛也搜得到） | Adobe |
| `data/third-party.jsonl` | 熱門第三方（Video Copilot / aescripts / RE:Vision…） | 各家 |
| `data/recipes.jsonl` | **配方庫**：一個「畫面感」對應要疊哪些效果 | 整理 |

## 資料格式（JSONL，一行一筆）

```json
{"name":"S_Glow","cat":"glow","tags":["glow","bloom","發光","輝光"],"desc":"經典柔和輝光"}
```

| 欄位 | 說明 |
|---|---|
| `name` | 效果名（Sapphire 前綴 `S_`、Continuum 前綴 `BCC`/`BCC+`） |
| `cat` | 分類（glow/light/flare/particles/stylize/film/color/blur/warp/keying/tracking/restore/time/transition/text/generate/3d/recipe…） |
| `tags` | **中英混合關鍵字——搜尋主要靠這欄** |
| `desc` | 一句話中文說明 |
| `variants` | (可選) 同族變體 `{名稱:簡註}`，例如 30 種 `S_Dissolve` 收在一行 |
| `stack` / `builtin` | (配方專用) 要疊的效果清單，及純內建替代做法 |
| `suite` / `vendor` | (可選) 套件 / 廠商 |

## 搜尋為什麼有效（不需要向量資料庫）

在這個規模，`tags` 中英關鍵字 + 子字串比對就足夠：
- **文字**：需求 → 中英關鍵字 → 掃 `tags`/`desc` → 排序
- **圖片**（透過 Claude）：先拆畫面視覺特徵（發光？故障？老膠片？粒子？）→ 轉關鍵字 → 同上。一張參考圖常是多效果疊加，會拆開找。

未來若條目破萬或要做大型 app，再升級 embeddings（文字 bge-m3 / voyage，圖片 CLIP/SigLIP），資料格式不用改。

## 擴充

新增一行 JSON 到對應檔即可；新套件就開新 `.jsonl`。
在 Claude Code 裡說「把 XX 外掛加進特效資料庫」也會自動補。

## 資料來源
- Universe 工具總覽 · https://www.maxon.net/en/product-detail/red-giant/universe/tools
- Sapphire 完整圖鑑 · https://borisfx.com/documentation/sapphire/ae/picture-index/
- Continuum 完整清單 · https://borisfx.com/documentation/continuum/bcc-effects-list/

## 授權
資料整理與程式碼採 MIT（見 `LICENSE`）。各特效名稱與商標歸原廠商所有；本庫僅為索引/教學用途，不含任何官方素材或程式。
