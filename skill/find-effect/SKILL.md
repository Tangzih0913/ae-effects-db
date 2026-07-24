---
name: find-effect
description: 用文字描述或貼圖找 AE 特效（Trapcode/Magic Bullet/VFX Suite/Universe/Sapphire/Continuum/AE內建/配方/熱門第三方）。觸發時機：用戶問「找特效」「這個效果怎麼做」「有什麼外掛可以做XX」「這張圖/影片的效果是什麼」，或貼參考圖要仿效果。
---

# 找 AE 特效

資料庫位置：`C:\AEMCP\effects-db\data\*.jsonl`（一行一效果；`tags` 為中英關鍵字，`variants` 收合同族變體）。
其中 `builtin-ae.jsonl` 是 AE 內建效果（沒買外掛也有解），`recipes.jsonl` 是「畫面感→效果堆疊」配方。

## 流程

1. **解析需求 → 關鍵字**
   - 文字描述：抽取視覺概念，翻成英文關鍵字＋常見同義詞（見下方對照表）。
   - 若用戶描述的是**整體畫面風格/氛圍**（賽博龐克、電影感、老電影、科技HUD…）而非單一效果，**先搜 `recipes.jsonl`** 給出效果堆疊配方，再視需要展開各單項。
   - 圖片/影片截圖：先客觀描述畫面特徵——發光？色差？顆粒？掃描線？粒子？扭曲？文字動畫？轉場？調色風格？——再轉成關鍵字。通常一張參考圖是「多個效果疊加」，要拆開找（例：賽博龐克標題 = 霓虹描邊發光 + 故障位移 + 色差 + 掃描線）。
2. **Grep 搜尋**：對 `C:\AEMCP\effects-db\data\` 用 `-i` 搜多組同義詞（regex 用 `|` 併聯，例 `glow|bloom|halation`）。中文詞也可直接搜。命中太多就加詞縮小，命中為零就換同義詞或放寬。
3. **讀命中行，挑前 3–5 名**，按符合度排序。
4. **回答格式**：每個候選給「名稱（套件/廠商）— 為什麼像、關鍵參數往哪調」；最後補一行「AE 內建近似做法」（查 `builtin-ae.jsonl`），讓沒買外掛也有退路。若命中的是 `recipes` 配方，直接把 `stack` 的堆疊順序與 `builtin` 替代方案列給用戶。
5. **可選—直接套用**：若用戶已安裝該外掛且想試，可用 AfterEffectsMCP 的 run-script 以效果 matchName 套用到選中圖層；AE 內建效果用 apply-effect。第三方 matchName 不確定時，先用 ExtendScript 列舉 `app.effects` 查證再套。

## 中→英關鍵字對照（優先查這張表）

| 描述 | 關鍵字 |
|---|---|
| 發光/輝光/柔光 | glow, bloom, halation |
| 鏡頭光暈/光斑 | lens flare, flare |
| 體積光/光線/丁達爾 | rays, god rays, light shafts, volumetric |
| 星芒/閃耀 | glint, glare, star, sparkle |
| 漏光 | light leak |
| 霓虹/描邊發光 | neon, edge glow, saber, outline |
| 故障/毛刺 | glitch, digital damage, datamosh, pixel sort |
| 老電視/雪花 | tv damage, analog, static, scanline, crt |
| 錄影帶 | vhs, tape |
| 老膠片/復古底片 | film damage, retro, grain, vignette, 8mm, 16mm |
| 色差/色散 | chromatic aberration, prism, dispersion, rgb split |
| 熱浪/隱形扭曲 | heat haze, displacement, refraction |
| 粒子/星塵/魔法 | particle, dust, magic, emitter |
| 煙/火/爆炸 | smoke, fire, explosion |
| 拖尾/殘影 | trails, echo, feedback |
| 震動/手持 | camera shake, handheld |
| 甩鏡轉場 | swish, whip pan |
| 轉場 | transition, dissolve, wipe |
| 去背/摳像/綠幕 | key, chroma key, primatte, green screen |
| 追蹤/貼螢幕 | track, corner pin, planar, mocha, screen replace |
| 移除物件/修補 | remove, clone, inpaint, wire |
| 慢動作/補幀/變速 | retime, optical flow, slow motion, twixtor |
| 降噪 | denoise, noise reduction |
| 美膚/磨皮 | beauty, skin |
| 調色/電影感 | color grade, looks, film stock, cinematic |
| 卡通/漫畫 | cartoon, toon, halftone, posterize |
| 素描/油畫/水彩 | sketch, pencil, paint, watercolor |
| 馬賽克/像素化 | mosaic, pixelate, pixel art, 8-bit |
| 萬花筒/鏡像 | kaleidoscope, mirror, symmetry |
| 無限鏡像/回饋 | feedback, infinite |
| 水波/漣漪/焦散 | ripple, water, wave, caustics |
| 魚眼/移軸/微縮 | fisheye, tilt shift, miniature |
| 漩渦/極座標/小星球 | vortex, twirl, polar, tiny planet |
| 閃電/電流 | lightning, zap, electric |
| 雷射/光劍 | laser, saber, beam |
| 散景/景深/失焦 | bokeh, defocus, depth of field, rack focus |
| 打字機/文字動畫 | type on, typewriter, text, kinetic |
| 數字滾動 | numbers, counter |
| 科幻介面/全息 | hud, hologram, holomatrix, sci-fi |
| 音樂驅動/音頻可視化 | audio, beat, sound keys, visualizer, waveform |
| 3D文字/模型 | element 3d, extrude, title studio |
| 破碎 | shatter |
| 陰影/倒影 | shadow, reflection |
| 穩定/防抖 | stabilize |
| 打碼/隱私 | censor, blur, mosaic, witness protection |

## 注意

- 群組條目（名稱含「系列/工具組/轉場組」）：命中後從 `variants` 裡挑出最貼切的具體效果名回覆。
- 資料庫沒涵蓋的（AE 內建、冷門外掛），用自身知識回答，並提議把它補進資料庫。
- 用戶描述模糊時，先給最可能的 2–3 個方向各附代表效果，不要反問一長串。
