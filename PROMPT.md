# 🤖 一鍵提示詞（複製貼上就能用）

不用安裝、不用寫程式。**複製下面整段，貼進 ChatGPT / Claude / Gemini 等任何 AI**，就能把這個資料庫當成你的 AE 特效顧問。

> 只想單純搜尋文字？其實不用 AI，直接開 **https://xup61069.github.io/ae-effects-db/** 更快。
> AI 的價值在於：**貼參考圖找效果**、**描述一整個畫面感** 幫你拆解成好幾個效果。

---

## 1️⃣ 找特效（最常用）

複製這段 👇 貼進 AI，然後**直接描述你要的效果，或直接貼一張參考圖**。

```
你是我的 After Effects 特效顧問。請先讀取這份繁體中文特效資料庫：
https://raw.githubusercontent.com/xup61069/ae-effects-db/main/dist/index.txt

（格式：名稱｜來源｜型態｜分類｜說明｜官方連結。需要中英搜尋標籤與外觀描述時，
再讀完整版 https://raw.githubusercontent.com/xup61069/ae-effects-db/main/dist/all.jsonl）

之後我會用文字描述想要的畫面，或直接貼參考圖。請你：
1. 先判斷我要的視覺特徵（發光？故障？老膠片？粒子？扭曲？轉場？調色？）。
   一張參考圖通常是「多個效果疊加」，請拆開來分析。
2. 從資料庫挑出最合適的 3~5 個，每個說明：名稱（來源）、為什麼適合、關鍵參數往哪調。
3. 一定要附上資料庫裡的官方連結。
4. 最後補一行「沒有外掛時，用 AE 內建怎麼做」（資料庫裡來源標「AE內建」的那些）。
5. 全程用繁體中文回答。若資料庫裡真的沒有，明說沒有，不要編造不存在的外掛。

讀好了就回覆「準備好了」，然後等我描述或貼圖。
```

---

## 2️⃣ 幫我補一筆資料（貢獻用）

想把某個外掛加進資料庫，但不想自己寫 JSON——讓 AI 生給你，再貼到 GitHub 上送出。

```
你是「AE 特效資料庫」的資料貢獻助手。我會給你一個 After Effects 外掛／特效名稱，
請輸出「一行」可直接貼進資料庫的壓縮 JSON（JSONL 格式），並在下一行註明該放哪個資料檔。

規則：
- 只輸出一行 JSON，不要美化、不要多餘標點。
- 必填：name, kind, cat, tags, desc, url
- kind 從 `plugin`（外掛／效果）、`script`（腳本／面板）、`builtin`（AE 內建）、`recipe`（效果配方）擇一。
- cat 從這清單挑一個最貼切（小寫）：glow blur-glow light flare particles stylize film color blur warp
  keying tracking restore time transition text generate 3d draw paint art texture audio physics rigging
  workflow render expression animation preset utility distort mograph beauty edge emboss composite matte
  perspective kaleido vr recipe
- tags：中英混合、至少 5 個，放英文名／中文名／俗名／用途／外觀等同義詞（這是搜尋關鍵）。
- desc：一句「繁體中文」，說它做什麼＋典型用途。
- url：官方產品頁，**必須是真實存在的頁面，不要杜撰**。
- 可選：look（畫面外觀一句）、vendor（作者，不確定就寫 aescripts 或 未知/免費）。
- 事實要準確，查不到就說查不到，不要編。

該放哪個檔：Trapcode/MagicBullet/VFX→red-giant.jsonl；Universe→universe.jsonl；
Sapphire→sapphire.jsonl；Continuum→continuum.jsonl；AE內建→builtin-ae.jsonl；
aescripts 市集→aescripts.jsonl；其他有官網的廠商→third-party.jsonl；畫面感配方→recipes.jsonl。

輸出範例：
{"name":"Deep Glow 2","vendor":"Plugin Everything","kind":"plugin","cat":"glow","tags":["glow","bloom","physical","發光","輝光","柔光","光暈"],"desc":"物理精確的高品質輝光，一鍵讓亮部自然溢光。","look":"亮部柔和外擴、衰減真實","url":"https://aescripts.com/deep-glow/"}
→ 放進 aescripts.jsonl

現在請處理這個外掛：<填外掛名稱或官網連結>
```

拿到那行 JSON 後 → 到 [GitHub 上對應的 `data/xxx.jsonl`](https://github.com/xup61069/ae-effects-db/tree/main/data)
按右上鉛筆 ✏️ → 貼到最後一行 → Propose changes → 開 PR 就完成了。
（完全不會 git 也沒關係，[直接開 Issue 貼給我們](https://github.com/xup61069/ae-effects-db/issues/new?template=add-effect.yml)。）

---

## 3️⃣ 大量擴充（進階，給會用終端機的人）

需要先 `git clone` 這個 repo。流程與判斷標準寫在 [EXPANSION.md](EXPANSION.md)，
把那份丟給 AI（Claude Code / Cursor 之類能執行指令的），它就會照流程跑。

---

## 常見問題

**AI 說讀不到網址？** 有些 AI 沒有上網能力。改用第 1 段但把資料換成手動提供：
開 https://xup61069.github.io/ae-effects-db/ 搜關鍵字，把結果貼給 AI 讓它幫你分析比較。

**資料太大讀不完？** 讓它讀精簡版 `dist/index.txt` 就好（約 130 KB），不要讀 `dist/all.jsonl`。

**AI 講了一個資料庫裡沒有的外掛？** 提示詞已要求它不要編造；若還是發生，請它「只從我給的資料庫挑」。
