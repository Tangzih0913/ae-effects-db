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

console.log("Web JavaScript and zh/en/ja locale contracts are valid.");
