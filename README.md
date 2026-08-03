# AE 特效資料庫 (ae-effects-db)

## 🔍 線上搜尋（點這裡，手機/電腦都能用）

# → https://xup61069.github.io/ae-effects-db/

打開就能用文字搜特效，免安裝、免登入。用「文字描述」或「參考圖」找 After Effects 特效的知識庫。

**想用「貼參考圖」找效果？** 在搜尋頁按一下 **🤖 用 AI 找 / 貼圖找**，複製那段提示詞貼進
ChatGPT / Claude / Gemini 就能用——不用安裝任何東西。提示詞也放在 **[PROMPT.md](PROMPT.md)**。

> 740 筆條目，涵蓋約 1090+ 個特效（同族變體收合），資料於 2026-07 整理自各廠商官方最新清單，並比對本機 AE 2026 實裝外掛補齊。

## 四種用法

### 1. 網頁（最萬用）
**線上直接用（推薦）：https://xup61069.github.io/ae-effects-db/**
即時搜尋、中英皆可、分類/來源篩選、關鍵字高亮，手機也能開。

想在本機跑：因瀏覽器安全限制不能直接雙擊 `file://`，要經 HTTP 開啟：
> ```bash
> python -m http.server 8000
> ```
> 然後開 http://localhost:8000 。

### 2. 命令列
```bash
python search.py 發光              # 中文
python search.py neon glow         # 英文多關鍵字(OR)
python search.py --cat transition 甩鏡
python search.py --suite sapphire glow
python search.py --list-cats       # 看所有分類
```

### 3. 任何 AI（一鍵提示詞，新手最推薦）
複製 [PROMPT.md](PROMPT.md) 的第一段貼進任何 AI，它會自己去讀資料庫，
之後你就能**直接貼參考圖**問「這是什麼效果」，或描述一整個畫面感讓它拆解。
搜尋頁上的 🤖 按鈕可以一鍵複製那段提示詞。

### 4. Claude Code `/find-effect`
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
| `data/aescripts.jsonl` | **aescripts.com 熱門工具**（Deep Glow / Overlord / RubberHose / Motion / Plexus / Stardust / Beauty Box…） | aescripts+aeplugins 各作者 |
| `data/third-party.jsonl` | 其他第三方（Video Copilot / RE:Vision / Neat Video / Mocha…） | 各家 |
| `data/installed.jsonl` | **未驗證**：掃描本機 AE 實裝、官方清單沒收錄的（Topaz / VC Orb / Gaussian Splatting / Physarum / Soft Body / VR 沉浸式…）。其中查無官方說明、純用檔名推測的會標 ⚠ | 各家 |
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

## 一起維護（歡迎協作）

補特效、修描述、加同義詞都歡迎，**不用會寫程式**——甚至可以叫 AI 幫你生一行貼上來。

- 👥 貢獻者看 **[CONTRIBUTING.md](CONTRIBUTING.md)**（內含「複製貼進你 AI 的提示詞」，一鍵生資料）
- 🤖 AI 助手看 **[AGENTS.md](AGENTS.md)**；機器可讀規格在 **[schema/effect.schema.json](schema/effect.schema.json)**
- 📈 專門做「持續擴充」的作業流程看 **[EXPANSION.md](EXPANSION.md)**
- 🐛 不會用 git 也可以：直接[開 Issue 回報缺少的特效](https://github.com/xup61069/ae-effects-db/issues/new?template=add-effect.yml)

### 工具

```bash
python validate.py              # 校驗全部資料（送 PR 時 CI 也會跑）
python tools/find_new.py --desc # 列出 aescripts 上還沒收錄的候選＋官方說明
python tools/add.py new.jsonl   # 安全匯入：自動判重、檢查欄位、選對資料檔
```

新增一行 JSON 到對應 `data/*.jsonl` 即可；新套件就開新 `.jsonl`。
刻意不收的東西請記進 `curation/skipped.tsv`（附原因），避免日後重複評估。

## 資料來源
- Universe 工具總覽 · https://www.maxon.net/en/product-detail/red-giant/universe/tools
- Sapphire 完整圖鑑 · https://borisfx.com/documentation/sapphire/ae/picture-index/
- Continuum 完整清單 · https://borisfx.com/documentation/continuum/bcc-effects-list/
- aescripts 熱門/新品 · https://aescripts.com/?tab=viewed

## 關於
本資料庫由 **Kadid**（[@xup61069](https://github.com/xup61069)）與 **Claude**（Anthropic）共同整理維護。
資料來自各廠商官方頁面逐筆查證，繁體中文說明與中英搜尋標籤為人工＋AI 協作編寫。

歡迎一起補充 → [CONTRIBUTING.md](CONTRIBUTING.md)

## 授權
資料整理與程式碼採 MIT（見 `LICENSE`）。各特效名稱與商標歸原廠商所有；本庫僅為索引/教學用途，不含任何官方素材或程式。
