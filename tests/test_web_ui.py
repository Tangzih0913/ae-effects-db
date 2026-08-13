import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "index.html").read_text(encoding="utf-8")
I18N = (ROOT / "i18n.js").read_text(encoding="utf-8")


class WebUiContractTests(unittest.TestCase):
    def test_sort_modes_are_distinct_and_shareable(self):
        options = re.findall(r'<option value="([^"]+)"', HTML)
        self.assertEqual(
            ["popular", "relevance", "name", "category", "source", "latest"], options
        )
        self.assertIn('if(mode==="category") return categoryCmp', HTML)
        self.assertIn('if(mode==="relevance" && hasTerms)', HTML)
        self.assertIn('return popularCmp(a[1],b[1]);', HTML)
        self.assertIn('setParam("sort"', HTML)
        self.assertIn("curation/popularity.json", HTML)
        self.assertIn('function popularityBreakdown', HTML)
        self.assertIn('if(mode==="latest")', HTML)

    def test_favorites_are_local_persistent_and_filterable(self):
        self.assertIn('id="favBtn"', HTML)
        self.assertIn('const FAVORITES_KEY = "ae-effects-db:favorites:v1"', HTML)
        self.assertIn("localStorage.setItem(FAVORITES_KEY", HTML)
        self.assertIn("if(favoritesOnly)pool=pool.filter", HTML)
        self.assertIn('setParam("fav"', HTML)
        self.assertIn('data-favorite="${esc(itemKey(d))}"', HTML)
        self.assertIn('id="favExport"', HTML)
        self.assertIn('id="favImport"', HTML)

    def test_compare_detail_and_shareable_state_exist(self):
        self.assertIn('id="compareTray"', HTML)
        self.assertIn('id="compareDialog"', HTML)
        self.assertIn('id="detailDialog"', HTML)
        self.assertIn('data-detail="${esc(itemKey(d))}"', HTML)
        self.assertIn('setParam("compare"', HTML)
        self.assertIn('url.searchParams.set("item"', HTML)

    def test_prebuilt_index_and_mobile_performance_contract(self):
        self.assertIn("dist/web-index.json", HTML)
        self.assertIn('content-visibility:auto', HTML)
        self.assertIn('IntersectionObserver', HTML)
        self.assertIn('id="mq"', HTML)
        self.assertIn('id="backTop"', HTML)

    def test_search_normalizes_simplified_text_and_corrects_typos(self):
        self.assertIn('function normalizeText', HTML)
        self.assertIn('const SEARCH_ALIASES', HTML)
        self.assertIn('function levenshtein', HTML)
        self.assertIn('function correctTerms', HTML)

    def test_cards_keep_distinct_kind_colors(self):
        for kind in ("plugin", "script", "builtin", "recipe"):
            self.assertIn(f".card.kind-{kind}", HTML)
            self.assertIn(f".kindbadge.kind-{kind}", HTML)

    def test_english_and_japanese_are_shareable_complete_locales(self):
        self.assertIn('src="i18n.js?', HTML)
        self.assertIn('data-lang="en"', HTML)
        self.assertIn('data-lang="ja"', HTML)
        self.assertIn('setParam("lang"', HTML)
        self.assertIn('htmlLang:"en"', I18N)
        self.assertIn('htmlLang:"ja"', I18N)
        self.assertIn('AE エフェクトデータベース', I18N)
        self.assertIn('AE Effects Database', I18N)
        self.assertIn('"グリッチ":["glitch"', I18N)

    def test_non_chinese_locales_label_curated_description_fallback(self):
        self.assertIn('id="languageNote"', HTML)
        self.assertIn('descriptionOriginal', HTML)
        self.assertIn('Traditional Chinese original', I18N)
        self.assertIn('繁体字中国語の原文', I18N)


if __name__ == "__main__":
    unittest.main()
