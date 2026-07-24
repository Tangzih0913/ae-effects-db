# AGENTS.md — 給 AI 協作者的說明

> 這份檔案給任何 AI 助手（Claude / ChatGPT / Copilot 等）看，讓它了解本專案並正確地幫忙新增/修改資料。人類貢獻者請看 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 這是什麼

一個 After Effects 特效／外掛的**可搜尋資料庫**。核心是 `data/*.jsonl`：一個特效一行 JSON。使用者用文字描述（或貼參考圖交給 AI）就能找到對應特效。線上搜尋頁：https://xup61069.github.io/ae-effects-db/

**設計原則：搜尋主要靠 `tags` 欄位做子字串比對，不用向量資料庫。** 所以你的首要任務永遠是「讓條目更好被搜到」——把中英文同義詞、俗名、常見講法都塞進 tags。

## 檔案結構

```
data/*.jsonl        每行一筆特效（唯一的資料來源，你主要動這裡）
schema/effect.schema.json   單筆條目的 JSON Schema（機器可讀規格）
validate.py         校驗腳本（改完一定要跑）
search.py           命令列搜尋
index.html          靜態搜尋網頁（GitHub Pages）
skill/find-effect/  Claude Code skill
```

### 各資料檔的分工（新增時放對檔案）
| 檔案 | 放什麼 |
|---|---|
| `red-giant.jsonl` | Maxon/Red Giant：Trapcode、Magic Bullet、VFX Suite |
| `universe.jsonl` | Red Giant Universe |
| `sapphire.jsonl` | Boris FX Sapphire（前綴 `S_`） |
| `continuum.jsonl` | Boris FX Continuum（前綴 `BCC`/`BCC+`） |
| `builtin-ae.jsonl` | Adobe AE 內建效果（含 CC/Cycore） |
| `aescripts.jsonl` | aescripts.com 市集的外掛/腳本 |
| `third-party.jsonl` | 其他有獨立官網的廠商（Video Copilot、RE:Vision、Neat Video…） |
| `installed.jsonl` | 掃描本機安裝、上面都沒收錄的雜項；查無官方說明的標 `unverified` |
| `recipes.jsonl` | 「畫面感 → 要疊哪些效果」的配方（用 `stack`/`builtin`） |

## 資料格式

JSONL：**一行一個 JSON 物件，不是陣列、沒有逗號結尾、UTF-8、不要美化換行**。

必填 `name` `cat` `tags` `desc`；其餘選填。完整規格見 [`schema/effect.schema.json`](schema/effect.schema.json)。

```json
{"name":"S_Glow","cat":"glow","tags":["glow","bloom","發光","輝光","柔光","光暈"],"desc":"經典柔和輝光，讓亮部往外柔順發光。","look":"亮部往外柔和溢光","suite":"Sapphire"}
```

| 欄位 | 說明 |
|---|---|
| `name` | 效果名（Sapphire=`S_`、Continuum=`BCC`/`BCC+`；群組用「XX系列/工具組」） |
| `cat` | 分類，小寫，見下方清單 |
| `tags` | **中英混合關鍵字，至少 3 個，越多越好**。放英文名、中文名、俗名、用途、外觀 |
| `desc` | 一句繁中：做什麼＋典型用途 |
| `look` | (選) 畫面外觀一句 |
| `variants` | (選) 同族變體 `{"S_KaleidoOct":"八角", ...}`，幾十個相似效果收一行 |
| `stack`/`builtin` | (選，僅 recipes) 要疊的效果清單／內建替代做法 |
| `suite`/`vendor` | (選) 套件／廠商作者 |
| `unverified` | (選) `true`=查無官方說明、描述是推測，網頁顯示 ⚠。查證後移除 |
| `aex` | (選) 對應的 `.aex` 檔名 |

### 分類 cat（沿用既有，勿亂造新的）
`glow` `blur-glow` `light` `flare` `particles` `stylize` `film` `color` `blur` `warp` `keying` `tracking` `restore` `time` `transition` `text` `generate` `3d` `draw` `paint` `art` `texture` `audio` `physics` `rigging` `workflow` `render` `expression` `animation` `preset` `utility` `distort` `mograph` `beauty` `edge` `emboss` `composite` `matte` `perspective` `kaleido` `vr` `recipe`

真的需要新分類時，同時加進 `validate.py` 的 `KNOWN_CATS`。

## 你該遵守的規則

1. **繁體中文**寫 `desc`（這是台灣使用者的庫）。用語別用中國詞（如「渲染→算圖」看情境，但技術詞可保留）。
2. **tags 一定要中英雙語＋同義詞**。想像使用者會怎麼搜：發光的人可能打 glow / 發光 / 輝光 / 光暈 / bloom，全放。
3. **不要重寫整個檔案**去改一行——用精準的行編輯，避免動到別人條目。
4. **改完必跑** `python validate.py`，要全綠（warning 可接受，error 不行）。
5. **事實準確**：不確定作者就寫 `aescripts` 或 `未知/免費`，不要亂掰。查不到官方說明就標 `unverified:true` 並在 desc 註明「（推測，未查證）」。
6. **不要放盜版/下載連結**，不要抓取受版權的整段文案。特效名稱與商標屬原廠。
7. 一次 PR 專注一件事（例：新增某套件、或修某檔描述）。

## 新增一筆的流程

1. 判斷屬於哪個資料檔（見上表）。
2. 查官方頁或可靠來源，寫準確的 desc。
3. 組出符合 schema 的一行 JSON，tags 塞好中英同義詞。
4. append 到該檔最後（或群組附近）。
5. `python validate.py`，通過後送 PR。

## 快速驗證指令
```bash
python validate.py                 # 校驗全部
python search.py 發光               # 測搜尋
python search.py --suite sapphire glow
```
