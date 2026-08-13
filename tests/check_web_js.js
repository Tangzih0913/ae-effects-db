const fs = require("fs");
const path = require("path");

const root = path.resolve(__dirname, "..");
const html = fs.readFileSync(path.join(root, "index.html"), "utf8");
const inline = [...html.matchAll(/<script(?: [^>]*)?>([\s\S]*?)<\/script>/g)]
  .map(match => match[1])
  .filter(Boolean)
  .join("\n");
new Function(inline);

require(path.join(root, "i18n.js"));
const {locales, searchAliases} = globalThis.AE_I18N;
const expected = Object.keys(locales.zh.messages).sort();
for (const language of ["en", "ja"]) {
  const actual = Object.keys(locales[language].messages).sort();
  if (JSON.stringify(actual) !== JSON.stringify(expected)) {
    throw new Error(`${language} message keys do not match zh`);
  }
  if (Object.keys(locales[language].categories).length !== 42) {
    throw new Error(`${language} must translate all 42 categories`);
  }
}

const usedKeys = [...inline.matchAll(/\bt\("([^"]+)"/g)].map(match => match[1]);
for (const language of ["zh", "en", "ja"]) {
  const missing = [...new Set(usedKeys)].filter(key => !(key in locales[language].messages));
  if (missing.length) throw new Error(`${language} is missing messages: ${missing.join(", ")}`);
}
if (!searchAliases["グリッチ"]?.includes("glitch")) {
  throw new Error("Japanese search aliases are unavailable");
}

const localization = JSON.parse(fs.readFileSync(path.join(root, "curation", "localization.json"), "utf8"));
const dataUrls = new Set();
const dataRows = [];
for (const file of fs.readdirSync(path.join(root, "data")).filter(name => name.endsWith(".jsonl"))) {
  for (const line of fs.readFileSync(path.join(root, "data", file), "utf8").split(/\r?\n/).filter(Boolean)) {
    const row = JSON.parse(line);
    dataRows.push(row);
    if (row.url) dataUrls.add(row.url);
    if (row.date_url) dataUrls.add(row.date_url);
  }
}
const localizedEntries = Object.entries(localization.localized_urls || {});
if (localizedEntries.length < 100) throw new Error("Expected at least 100 verified localized official URLs");
for (const [original, variants] of localizedEntries) {
  if (!dataUrls.has(original)) throw new Error(`Localized URL is not used by the database: ${original}`);
  if (Object.keys(variants).join(",") !== "ja") throw new Error(`Only verified Japanese URL variants are currently allowed: ${original}`);
  const source = new URL(original), target = new URL(variants.ja);
  if (source.hostname !== target.hostname || source.href === target.href) throw new Error(`Invalid localized mapping: ${original}`);
  if (target.hostname === "helpx.adobe.com" && !target.pathname.startsWith("/jp/")) throw new Error(`Adobe Japanese path is invalid: ${target.href}`);
  if (target.hostname === "www.maxon.net" && !target.pathname.startsWith("/ja/")) throw new Error(`Maxon Japanese path is invalid: ${target.href}`);
  if (!["helpx.adobe.com", "www.maxon.net"].includes(target.hostname)) throw new Error(`Unapproved localized host: ${target.hostname}`);
}
const ruleIds = new Set();
for (const rule of localization.official_category_rules || []) {
  if (ruleIds.has(rule.id)) throw new Error(`Duplicate official category rule: ${rule.id}`);
  ruleIds.add(rule.id);
  if (!rule.labels?.en || !rule.labels?.ja || !rule.patterns?.length) throw new Error(`Incomplete official category rule: ${rule.id}`);
}
for (const required of ["blur-sharpen", "color-correction", "distort", "generate", "immersive-video"]) {
  if (!ruleIds.has(required)) throw new Error(`Missing Adobe official category rule: ${required}`);
}
const officialEffectCategories = localization.official_effect_categories || {};
if (Object.keys(officialEffectCategories).length !== 278) throw new Error("Expected 278 effect-name-level Adobe category mappings");
for (const [name, categoryId] of Object.entries(officialEffectCategories)) {
  if (!dataRows.some(row => row.kind === "builtin" && row.name === name)) throw new Error(`Adobe category points to a missing built-in: ${name}`);
  if (!localization.official_categories?.[categoryId]) throw new Error(`Unknown Adobe category ${categoryId} for ${name}`);
}
for (const [name, expectedCategory] of Object.entries({Keylight:"keying","CC Burn Film":"stylize","CC Rain":"simulation","Warp Stabilizer VFX":"distort","Mocha AE":"boris-fx-mocha",CINEWARE:"cinema-4d"})) {
  if (officialEffectCategories[name] !== expectedCategory) throw new Error(`${name} must map to Adobe category ${expectedCategory}`);
}

const japaneseVocabulary = JSON.parse(fs.readFileSync(path.join(root, "curation", "search-aliases.ja.json"), "utf8"));
const japaneseAliases = japaneseVocabulary.aliases || {};
if (Object.keys(japaneseAliases).length < 80) throw new Error("Japanese discovery vocabulary is unexpectedly small");
const normalizeSearch = value => String(value || "").normalize("NFKC").toLowerCase().replace(/\s+/g, " ").trim();
for (const [query, aliases] of Object.entries(japaneseAliases)) {
  if (!/[\u3040-\u30ff\u4e00-\u9fff]/.test(query) || !Array.isArray(aliases) || aliases.length < 2) throw new Error(`Invalid Japanese alias: ${query}`);
}
for (const check of japaneseVocabulary.checks || []) {
  const terms = [check.query,...(japaneseAliases[check.query] || [])].map(normalizeSearch);
  const matches = dataRows.filter(row => {
    const haystack = normalizeSearch([row.name,row.desc,row.look,row.vendor,row.suite,...(row.tags || [])].join(" "));
    return terms.some(term => haystack.includes(term));
  }).map(row => row.name);
  if (!check.expected_any.some(name => matches.includes(name))) throw new Error(`Japanese query has no expected result: ${check.query}`);
}
for (const contract of ["localizedOfficialUrl", "officialCategory", "official_effect_categories", "siteCategoryTitle", "curation/localization.json", "curation/search-aliases.ja.json"]) {
  if (!html.includes(contract)) throw new Error(`Web localization integration is missing: ${contract}`);
}

console.log(`Web JavaScript, zh/en/ja locales, ${localizedEntries.length} verified localized URLs, 278 Adobe categories, and ${Object.keys(japaneseAliases).length} Japanese aliases are valid.`);
