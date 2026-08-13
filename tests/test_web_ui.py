import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "index.html").read_text(encoding="utf-8")


class WebUiContractTests(unittest.TestCase):
    def test_sort_modes_are_distinct_and_shareable(self):
        options = re.findall(r'<option value="([^"]+)"', HTML)
        self.assertEqual(
            ["popular", "relevance", "name", "category", "source"], options
        )
        self.assertIn('if(mode==="category") return categoryCmp', HTML)
        self.assertIn('if(mode==="relevance" && hasTerms)', HTML)
        self.assertIn('return popularCmp(a[1],b[1]);', HTML)
        self.assertIn('setParam("sort"', HTML)

    def test_favorites_are_local_persistent_and_filterable(self):
        self.assertIn('id="favBtn"', HTML)
        self.assertIn('const FAVORITES_KEY = "ae-effects-db:favorites:v1"', HTML)
        self.assertIn("localStorage.setItem(FAVORITES_KEY", HTML)
        self.assertIn("if(favoritesOnly)pool=pool.filter", HTML)
        self.assertIn('setParam("fav"', HTML)
        self.assertIn('data-favorite="${esc(itemKey(d))}"', HTML)

    def test_cards_keep_distinct_kind_colors(self):
        for kind in ("plugin", "script", "builtin", "recipe"):
            self.assertIn(f".card.kind-{kind}", HTML)
            self.assertIn(f".kindbadge.kind-{kind}", HTML)


if __name__ == "__main__":
    unittest.main()
