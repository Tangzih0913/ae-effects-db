# 一起維護這個特效庫 🙌

歡迎補特效、修描述、加同義詞。**不用會寫程式**——你甚至可以叫 AI 幫你生一行資料，貼上來就好。

> AI 助手請先讀 [AGENTS.md](AGENTS.md)（機器可讀規格在 [schema/effect.schema.json](schema/effect.schema.json)）。

## 最快：用 AI 幫你生一行（推薦）

把下面這段**提示詞**整段貼進 ChatGPT / Claude / 任何 AI，最後填上你要加的外掛名稱，它會吐一行可直接貼進資料庫的 JSON：

<details><summary>👉 點開複製提示詞</summary>

```
你是「AE 特效資料庫」的資料貢獻助手。我會給你一個 After Effects 外掛/特效名稱（可能附官網或說明），
請輸出「一行」可直接貼進資料庫的壓縮 JSON（JSONL 格式），並在下一行註明該放哪個資料檔。

規則：
- 只輸出一行 JSON，不要美化、不要多餘標點。
- 必填：name, cat, tags, desc。
- name：效果原名（Sapphire 前綴 S_、Continuum 前綴 BCC/BCC+）。
- cat：從這清單挑一個最貼切（小寫）：glow blur-glow light flare particles stylize film color blur warp
  keying tracking restore time transition text generate 3d draw paint art texture audio physics rigging
  workflow render expression animation preset utility distort mograph beauty edge emboss composite matte
  perspective kaleido vr recipe
- tags：中英混合、至少 5 個，放英文名/中文名/俗名/用途/外觀等同義詞——這是搜尋關鍵，越多越好。
- desc：一句「繁體中文」，說它做什麼＋典型用途（用繁中，勿用簡中詞）。
- url：**必填**，官方產品頁連結（aescripts 為 https://aescripts.com/<slug>/）。
- 選填：look（畫面外觀一句）、vendor（廠商/作者，不確定就寫 aescripts 或 未知/免費）、suite、aex（.aex 檔名）。
- 若查不到可靠說明：desc 註明「（推測，未查證）」並加 "unverified":true。
- 要事實準確，不要編造作者或功能。

該放哪個檔：Trapcode/MagicBullet/VFX→red-giant.jsonl；Universe→universe.jsonl；Sapphire→sapphire.jsonl；
Continuum→continuum.jsonl；AE內建→builtin-ae.jsonl；aescripts市集→aescripts.jsonl；
其他有官網的廠商→third-party.jsonl；畫面感配方→recipes.jsonl。

輸出範例：
{"name":"Deep Glow 2","cat":"glow","tags":["glow","bloom","physical","發光","輝光","柔光","光暈","溢光"],"desc":"物理精確的高品質輝光，一鍵讓亮部自然溢光，公認最漂亮的 AE 發光外掛。","look":"亮部柔和外擴、衰減真實","vendor":"Plugin Everything","url":"https://aescripts.com/deep-glow/"}
→ 放進 aescripts.jsonl

現在請處理這個外掛：<填外掛名稱或官網連結>
```

</details>

## 進階：讓 AI 巡 aescripts.com 一個一個補（需要能上網的 AI）

若你的 AI 能瀏覽網頁（Claude Code、ChatGPT 瀏覽、Perplexity 等），用下面這段讓它自動巡 aescripts.com、判斷實用性、去重、附官方連結，成批產出。

<details><summary>👉 點開複製「aescripts 批次補齊」提示詞</summary>

```
你是「AE 特效資料庫」的策展貢獻助手，任務是巡 aescripts.com 找出「還沒收錄且值得收錄」的外掛，
逐一產出可貼進 data/aescripts.jsonl 的 JSONL。

步驟：
1) 先抓已收錄清單以避免重複：讀
   https://raw.githubusercontent.com/xup61069/ae-effects-db/main/data/aescripts.jsonl
   記住裡面所有 name（也留意 third-party.jsonl / red-giant.jsonl 可能已含同名）。
2) 逐頁瀏覽 aescripts.com（建議依 https://aescripts.com/?tab=viewed 最多瀏覽、
   或 ?tab=bestselling 暢銷、或各分類），一個一個看產品。
3) 對每個產品做「收/不收」判斷：
   收錄條件（要同時成立）：
     - 尚未在已收錄清單中（名稱或功能沒重複）。
     - 功能實用、有代表性（暢銷/常被討論/解決常見需求）。
   直接略過（不要收）：
     - 已收錄，或與現有條目功能高度重複（例如又一個普通 glow、又一個普通 blur）。
     - 冷門、極小眾、實驗性、幾乎沒人用的。
     - 純預設包/素材包/教學，而非真正的外掛或腳本工具。
4) 決定收錄的，輸出「一行」壓縮 JSON，欄位規則：
     必填 name, cat, tags, desc, url
     - cat 從此清單挑（小寫）：glow blur-glow light flare particles stylize film color blur warp keying
       tracking restore time transition text generate 3d draw paint art texture audio physics rigging
       workflow render expression animation preset utility distort mograph beauty edge emboss composite
       matte perspective kaleido vr recipe
     - tags：中英混合≥5個，放英文名/中文名/俗名/用途/外觀同義詞（搜尋關鍵，越多越好），最後放 "aescripts"。
     - desc：一句繁體中文，做什麼＋典型用途（用繁中，勿簡中詞）。
     - url：該產品在 aescripts 的官方頁 https://aescripts.com/<slug>/（務必是真實存在的頁面，不要杜撰）。
     - vendor：作者名（頁面上的 author），不確定就寫 "aescripts"。
     - 事實要準；查不到說明就別硬收。
5) 每產一批（例如 10 筆）就停下讓我確認，並附一句「這批略過了哪些、為什麼」。

輸出格式範例（每行一筆，後面不用箭頭，全部都放 aescripts.jsonl）：
{"name":"Foldspace","cat":"3d","tags":["fold","bend","warp","curve","book","彎折","翻書","摺疊","3D扭曲","aescripts"],"desc":"在3D空間彎折/翻摺平面，做翻書、摺紙、曲面扭曲，控制點可連結其他圖層。","vendor":"aescripts","url":"https://aescripts.com/foldspace/"}

先做第 1 步，把已收錄清單抓回來並回報數量，再開始第一批。
```

</details>

拿到那行 JSON 後，貼到對應的 `data/xxx.jsonl` 檔案最後一行即可（見下方送出方式）。

> 想「貼參考圖找效果」而不是加資料？直接把圖丟給 AI 問「這畫面是什麼 AE 效果」，或用線上搜尋頁 https://xup61069.github.io/ae-effects-db/

## 資料長怎樣

一個特效一行 JSON，搜尋主要靠 `tags`（所以中英同義詞塞好塞滿）：

```json
{"name":"S_Rays","cat":"light","tags":["god rays","light shafts","volumetric","丁達爾","體積光","上帝光","放射光線","雲隙光"],"desc":"從亮部放射的體積光/上帝光，做雲隙光、窗光、神聖光束。","look":"從亮處放射的可見光柱","suite":"Sapphire"}
```

欄位與分類完整說明見 [AGENTS.md](AGENTS.md)。

## 送出方式

**方法 A：GitHub 網頁直接改（免裝任何東西）**
1. 開對應的 `data/xxx.jsonl` → 按右上鉛筆 ✏️ Edit。
2. 到最後貼上你的一行 JSON。
3. 下方填一句說明 → **Propose changes** → 開 Pull Request。

**方法 B：本機**
```bash
git clone https://github.com/xup61069/ae-effects-db
# 編輯 data/xxx.jsonl，加上你的行
python validate.py          # 一定要全綠
git commit -am "add: XXX 外掛"
```
再開 PR。

## 規矩（PR 前自檢）
- [ ] `python validate.py` 通過（error 會被 CI 擋下）。
- [ ] `desc` 用繁體中文、一句話、講清楚用途。
- [ ] `tags` 有中英雙語與同義詞（≥5 個更好搜）。
- [ ] 放對資料檔、`cat` 用既有分類。
- [ ] 作者/功能屬實；查不到就標 `unverified`。
- [ ] 不放盜版下載連結、不整段複製官方文案。

有問題就開 Issue（有「新增特效」範本可用）。感謝你 ❤️
