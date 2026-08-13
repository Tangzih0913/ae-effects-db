#!/usr/bin/env node
"use strict";

const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");
const DATA_DIR = path.join(ROOT, "data");
const OUTPUT = path.join(ROOT, "curation", "localization.json");
const VERIFY_DATE = new Date().toISOString().slice(0, 10);
const USER_AGENT = "ae-effects-db localization verifier/1.0 (+https://github.com/xup61069/ae-effects-db)";

const OFFICIAL_CATEGORY_RULES = [
  {id:"3d-channel",patterns:["/3d-channel-effects.html"],labels:{en:"3D Channel",ja:"3D チャンネル"}},
  {id:"audio",patterns:["/audio-effects.html"],labels:{en:"Audio",ja:"オーディオ"}},
  {id:"blur-sharpen",patterns:["/blur-sharpen-effects.html","/blur-and-sharpen-effects.html"],labels:{en:"Blur and Sharpen",ja:"ブラー＆シャープ"}},
  {id:"channel",patterns:["/channel-effects.html"],labels:{en:"Channel",ja:"チャンネル"}},
  {id:"color-correction",patterns:["/color-correction-effects.html"],labels:{en:"Color Correction",ja:"カラー補正"}},
  {id:"distort",patterns:["/distort-effects.html","/detail-preserving-upscale-effect.html"],labels:{en:"Distort",ja:"ディストーション"}},
  {id:"expression-controls",patterns:["/expression-controls-effects.html"],labels:{en:"Expression Controls",ja:"エクスプレッション制御"}},
  {id:"generate",patterns:["/generate-effects.html"],labels:{en:"Generate",ja:"描画"}},
  {id:"immersive-video",patterns:["/immersive-video-effects.html","/vr-effects.html"],labels:{en:"Immersive Video",ja:"イマーシブビデオ"}},
  {id:"keying",patterns:["/keying-effects.html"],labels:{en:"Keying",ja:"キーイング"}},
  {id:"matte",patterns:["/matte-effects.html"],labels:{en:"Matte",ja:"マット"}},
  {id:"noise-grain",patterns:["/noise-grain-effects.html","/noise-and-grain-effects.html"],labels:{en:"Noise and Grain",ja:"ノイズ＆グレイン"}},
  {id:"perspective",patterns:["/perspective-effects.html"],labels:{en:"Perspective",ja:"遠近"}},
  {id:"simulation",patterns:["/simulation-effects.html"],labels:{en:"Simulation",ja:"シミュレーション"}},
  {id:"stylize",patterns:["/stylize-effects.html"],labels:{en:"Stylize",ja:"スタイライズ"}},
  {id:"text",patterns:["/text-effects.html"],labels:{en:"Text",ja:"テキスト"}},
  {id:"time",patterns:["/time-effects.html"],labels:{en:"Time",ja:"時間"}},
  {id:"transition",patterns:["/transition-effects.html"],labels:{en:"Transition",ja:"トランジション"}},
  {id:"utility",patterns:["/utility-effects.html"],labels:{en:"Utility",ja:"ユーティリティ"}}
];

function readRows() {
  const rows = [];
  for (const file of fs.readdirSync(DATA_DIR).filter(name => name.endsWith(".jsonl"))) {
    const lines = fs.readFileSync(path.join(DATA_DIR, file), "utf8").split(/\r?\n/).filter(Boolean);
    for (const line of lines) rows.push(JSON.parse(line));
  }
  return rows;
}

function localizedCandidate(value) {
  let url;
  try { url = new URL(value); } catch (_) { return null; }
  if (url.hostname === "helpx.adobe.com" && !/^\/(?:jp|tw|cn)\//.test(url.pathname)) {
    url.pathname = `/jp${url.pathname}`;
    return url.href;
  }
  if (url.hostname === "www.maxon.net" && url.pathname.startsWith("/en/")) {
    url.pathname = `/ja/${url.pathname.slice(4)}`;
    return url.href;
  }
  return null;
}

function normalizedPath(value) {
  const url = new URL(value);
  return url.pathname.replace(/\/$/, "");
}

function documentName(value) {
  const pathname = new URL(value).pathname.replace(/\/$/, "");
  return pathname.slice(pathname.lastIndexOf("/") + 1);
}

async function verifyJapanesePage(candidate) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 30000);
  try {
    const response = await fetch(candidate, {
      headers:{"User-Agent":USER_AGENT,"Accept-Language":"ja,en;q=0.5"},
      redirect:"follow",
      signal:controller.signal
    });
    const finalUrl = new URL(response.url);
    const requested = new URL(candidate);
    if (!response.ok) return {ok:false,reason:`HTTP ${response.status}`};
    if (finalUrl.hostname !== requested.hostname) return {ok:false,reason:`redirected to ${finalUrl.hostname}`};
    if (normalizedPath(finalUrl.href) !== normalizedPath(candidate) && documentName(finalUrl.href) !== documentName(candidate)) {
      return {ok:false,reason:`redirected to different document ${finalUrl.pathname}`};
    }
    const html = await response.text();
    const lang = html.match(/<html[^>]*\blang=["']([^"']+)/i)?.[1]?.toLowerCase() || "";
    const japaneseCharacters = (html.match(/[\u3040-\u30ff]/g) || []).length;
    const title = html.match(/<title[^>]*>([\s\S]*?)<\/title>/i)?.[1] || "";
    if (!lang.startsWith("ja")) return {ok:false,reason:`html lang is ${lang || "missing"}`};
    if (japaneseCharacters < 20) return {ok:false,reason:"page has too little Japanese text"};
    if (/\b(?:404|page not found)\b/i.test(title)) return {ok:false,reason:"not-found page"};
    if (requested.hash && !finalUrl.hash) finalUrl.hash = requested.hash;
    return {ok:true,url:finalUrl.href};
  } catch (error) {
    return {ok:false,reason:error.name === "AbortError" ? "timeout" : error.message};
  } finally {
    clearTimeout(timer);
  }
}

function baseManifest(localizedUrls) {
  return {
    version:1,
    verified_at:VERIFY_DATE,
    policy:{
      taxonomy:"The 42 categories are site-defined functional discovery categories, not vendor menu labels.",
      product_names:"Official product spelling is preserved in every language.",
      descriptions:"Curated Traditional Chinese originals are shown in every language until a reviewed translation exists.",
      localized_urls:"Only locale-specific official pages that pass an HTTP and language check are listed; all other links keep the original official URL."
    },
    sources:{
      adobe_effect_categories_en:"https://helpx.adobe.com/after-effects/desktop/apply-effects-and-animation-presets/effects-and-animation-presets/effect-list.html",
      adobe_effect_categories_ja:"https://helpx.adobe.com/jp/after-effects/desktop/apply-effects-and-animation-presets/effects-and-animation-presets/effect-list.html",
      adobe_after_effects_languages:"https://helpx.adobe.com/jp/after-effects/system-requirements/2024.html",
      maxon_red_giant_ja:"https://www.maxon.net/ja/red-giant"
    },
    official_category_rules:OFFICIAL_CATEGORY_RULES,
    localized_urls:localizedUrls
  };
}

async function mapWithConcurrency(values, limit, operation) {
  const results = new Array(values.length);
  let next = 0;
  async function worker() {
    while (next < values.length) {
      const index = next++;
      results[index] = await operation(values[index], index);
    }
  }
  await Promise.all(Array.from({length:Math.min(limit, values.length)}, worker));
  return results;
}

async function build() {
  let previous = {verified_at:"",localized_urls:{}};
  try { previous = JSON.parse(fs.readFileSync(OUTPUT, "utf8")); } catch (_) {}
  const originals = [...new Set(readRows().flatMap(row => [row.url, row.date_url]).filter(Boolean))]
    .map(original => ({original,candidate:localizedCandidate(original)}))
    .filter(item => item.candidate)
    .sort((a,b) => a.original.localeCompare(b.original));
  console.log(`Checking ${originals.length} candidate official URLs...`);
  const checked = await mapWithConcurrency(originals, 6, async (item, index) => {
    const cached = previous.verified_at === VERIFY_DATE && previous.localized_urls?.[item.original]?.ja;
    if (cached) {
      const cachedUrl = new URL(cached), originalHash = new URL(item.original).hash;
      if (originalHash && !cachedUrl.hash) cachedUrl.hash = originalHash;
      console.log(`[${index + 1}/${originals.length}] CACHED ${cachedUrl.href}`);
      return {...item,ok:true,url:cachedUrl.href};
    }
    const result = await verifyJapanesePage(item.candidate);
    console.log(`[${index + 1}/${originals.length}] ${result.ok ? "OK" : "SKIP"} ${item.candidate}${result.ok ? "" : ` (${result.reason})`}`);
    return {...item,...result};
  });
  const localizedUrls = {};
  for (const item of checked.filter(item => item.ok)) localizedUrls[item.original] = {ja:item.url};
  fs.writeFileSync(OUTPUT, `${JSON.stringify(baseManifest(localizedUrls), null, 2)}\n`, "utf8");
  console.log(`Wrote ${path.relative(ROOT, OUTPUT)} with ${Object.keys(localizedUrls).length} verified mappings.`);
}

async function check() {
  const manifest = JSON.parse(fs.readFileSync(OUTPUT, "utf8"));
  const entries = Object.entries(manifest.localized_urls || {}).map(([original,locales]) => ({original,candidate:locales.ja}));
  const checked = await mapWithConcurrency(entries, 6, async item => ({...item,...await verifyJapanesePage(item.candidate)}));
  const failures = checked.filter(item => !item.ok);
  for (const failure of failures) console.error(`FAIL ${failure.candidate}: ${failure.reason}`);
  if (failures.length) process.exitCode = 1;
  else console.log(`${entries.length} localized official URLs still pass live verification.`);
}

const mode = process.argv[2];
if (mode === "--write") build().catch(error => { console.error(error); process.exitCode = 1; });
else if (mode === "--check") check().catch(error => { console.error(error); process.exitCode = 1; });
else {
  console.log("Usage: node tools/build_localization.js --write|--check");
  process.exitCode = 2;
}
