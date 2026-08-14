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
- Gumroad 第一批已掃 `After Effects` 搭配 script／plugin／panel／extension／ScriptUI／JSX／AEX 的搜尋結果與 8 個官方商品頁；已決策 Island Chatter、Shy Filters、Script Launcher、Zoom、Easy Connect、EZ3D、PathPrep、FX TextFrame，但尚未窮盡平台；
- BOOTH 第一批已掃 `After Effects スクリプト`、`AE スクリプト`、`After Effects パネル`、`ScriptUI パネル` 的搜尋結果與 6 個官方商品頁；已決策 items 7769569、7695646、2307736、2728552、6815576、5899013，但尚未窮盡平台。
- Gumroad 第二批已掃 `After Effects ScriptUI panel`、`After Effects jsxbin workflow` 的搜尋結果與 7 個官方商品頁；已決策 ImpactFX、Grid Layers、Apex Control Pro、Keyframe Buddy、Quick Tools Pro、Visual States PRO、Dither FX PRO，但尚未窮盡平台；
- BOOTH 第二批已掃 `After Effects`／`AfterEffects` 熱門列表首批軟體候選與 8 個官方商品頁；已決策 Texton、SHIG Project Starter、CleanLayer、All Font Changer、BaraMoji、RZNC Geometry Generator、SyncFX、BeatPad，但尚未窮盡平台。
- Gumroad 第三批已掃 `After Effects ScriptUI animation tool`、`After Effects JSXBIN panel`、`After Effects script panel`、`After Effects workflow script jsx` 等搜尋結果與 6 個官方商品頁；已決策 CoreKit Pro 3、WordFlow、SubTitle Animator、MessCtrl、TimeOffset、Quick Wiggle，但尚未窮盡平台；
- BOOTH 第三批已掃 `After Effects スクリプト アニメーション`、`AfterEffects ScriptUI パネル`、`After Effects用スクリプト ScriptUI` 等搜尋結果與 9 個官方商品頁；已決策 BlinkPanel、Shy Folder、RplEffect、CenterOrigin、AutoTargetUI、Japanese_manuscript_paper、baraji、Set Adjustment、Bowl Wobble，但尚未窮盡平台。
- Payhip／獨立站第四批已檢查 After Toolkit、Pulse X、One Click Liquid Glass、SaaS Panel Kit 的官方商店或產品頁；原始 HTTP 檢查會遭 Payhip 防機器人回應 403，但已用可渲染的官方頁面核對內容，本批均因資訊不足或功能重疊略過，平台尚未窮盡。
- Gumroad 第四批已檢查 Motion UI 官方商品頁，因通用工具組功能與既有條目高度重疊而略過，平台尚未窮盡。
- BOOTH 第四批已掃 7 個官方商品頁；已決策 Siawase_FontShuffle、BPM同期モーションスクリプト、ColorPalette、Aulymo、moti、ShapeFit Panel、TSK_Input Expression，但尚未窮盡平台。
- Ko-fi 第四批以 After Effects script／panel／tool 關鍵字搜尋；結果主要為素材與預設包，未找到兼具官方商品頁、明確 AE 腳本功能與差異化價值的候選，平台尚未窮盡。
- BOOTH 第五批以自動化、ScriptUI、代理、相機、粒子、文字與旁白等關鍵字掃描 13 個官方商品頁；已決策 Particle launcher、Script Launcher、Auto Camera、AE Project Folder Organizer、Auto Crop Comp、Nanten ExAI、QuickComp、NeonBlink、Aurgan、TXT-NA Importer、自動ループ化スクリプト、MojiFlex、Ascify，其中 Aurgan 頁面已回 HTTP 404，其餘頁面均回 HTTP 200，平台尚未窮盡。
- Itch.io／Ko-fi 第五批搜尋仍以 AE 素材、模板及預設包為主，未找到比本批 BOOTH 候選更可信且具獨立工具功能的官方商品頁，平台尚未窮盡。
- BOOTH 第六批以 Marker、Keyframe、Layer、Path、Audio、Lip Sync 與 Morph 等關鍵字掃描 16 個官方商品頁；已決策 MatchLayerDuration、Arrange Layers、Random Placement、SelectiveAdjustment、レイヤー移動スクリプト、Label & Finder Bar、SyncFX、グリッドレイアウト、Marker Tools、DropFrameEXP v2、Path to Position、SyncAudio_To_Precomp、AudioGlide、Lab_LS、Deckard、MorphMesh，其中グリッドレイアウト頁面回 HTTP 404，其餘頁面均回 HTTP 200，平台尚未窮盡。
- Payhip 第六批已檢查 TIDY LAYERS、Project Organizer、Binzii_FastEase、AM Reverse Path 四個官方商品頁；頁面可正常渲染，但原始 HTTP 驗證仍會遭平台防機器人阻擋，本批均因與既有工具重疊而略過，平台尚未窮盡。
- BOOTH 第七批以顏色偵測、HUD、圓形文字、斬擊、像素、字形 3D 佈局等關鍵字掃描並驗證 8 個官方商品頁（全部 HTTP 200）；收錄 NodeField、TextOrbit、Katana Slash Pro、Words Scatter Pro、Palf PixelPaint、Syndromee Text Distribute、UltraBarabara、FacePartSelector，另以功能重疊或描述不足略過 40 個候選並記錄於 skipped.tsv，平台尚未窮盡。
- BOOTH 第八批以工具型候選清單（461 個，經素材／BGM／VRchat／Photoshop 等過濾後）逐筆抓取 meta 驗證並判重；收錄 Palf FontMixer、AlignLab、SaveAnimation、3D Grid Panel、HourFlow 五個（功能獨立，不與既有工具重疊），並以素材、非 AE、重疊或過窄為由略過 424 個候選且記錄於 skipped.tsv（另修復 skipped.tsv 中 39 筆以字面換行黏在同行的紀錄）。BOOTH 累計已涵蓋約 536 個商品 id（收錄 34 ＋ 略過 502），平台尚未窮盡。
- 收錄規則調整（2026-08-14）：功能重疊不再作為略過理由，改以熱門度（BOOTH wish_lists_count 等）、品質與實作差異判斷；知名作者的招牌工具一律收錄。據此以 BOOTH wish 數重審先前略過名單，第九批共收錄 43 筆（Nisai 17 筆：Nisai Stroke、MultiEase、RandomMotionNS、ひらがなだけ小さくする、テキスト状態保持文字分解、DelayAnimator、BPMコマ落ちウィグラー、BPM同期モーション、NotepadNS、ゴリ押しリピーター、自動ループ化、レイヤー追加ツールバー、アウトポイント階段状、位置間隔調整、プレビュー拡大率、マーカーコピー、親ヌル作成；重審收錄 26 筆：Everything、Auto Motion、Texflow、baraji、Blobin、Grungefy、Texton、Palf MotionTextBox、Compote、HL_LyricMotioner、ALStroke 2、Auto Camera、SimuDrop、Overbleed、NGS_ShapeLibrary、yama ultimate path、Effect Dash、MojiDropper、mojula、Filament 3D、LayoutKit+、Ascify、Figma to After Effects Exporter、Spookie、Renamus、Shape to mask）；因撞名略過 BOOTH ColorFlow（與 aescripts ColorFlow 同名）與 moti（與 aescripts MoTi 同名），另以「與 Nisai テキスト状態保持文字分解幾乎相同」略過 361do 的 BaraMoji；30 個已收錄 id 已自 skipped.tsv 移除（BOOTH 累計收錄 77、略過 472）。

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
python tools/add.py batch.jsonl --dry
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
