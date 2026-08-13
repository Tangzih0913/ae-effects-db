import unittest

import search
from tools.audit import popular_keys


class DatabaseConsistencyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = search.load()
        cls.by_name = {row["name"]: row for row in cls.rows}

    def test_every_popular_key_points_to_a_real_row(self):
        keys = popular_keys()
        available = {f"{row['_src']}:{row['name']}" for row in self.rows}
        self.assertGreater(len(keys), 30, "熱門清單不應為空或意外縮水")
        self.assertEqual(len(keys), len(set(keys)), "POPULAR_KEYS 不應重複")
        self.assertEqual([], [key for key in keys if key not in available])

    def test_multi_term_search_prefers_exact_product(self):
        results = search.ranked(self.rows, ["fx", "console"], require_all=True)
        self.assertTrue(results)
        self.assertEqual("FX Console", results[0][1]["name"])

    def test_chinese_fallback_segmentation(self):
        self.assertEqual(["煙霧", "霧模", "模擬"], search.segment(["煙霧模擬"]))

    def test_prominent_scripts_and_plugins_are_classified_correctly(self):
        expected = {
            "Plexus 3": "plugin",
            "Beauty Box Video": "plugin",
            "Jlitch": "plugin",
            "LayerRender": "plugin",
            "Modulation 2": "plugin",
            "Blob it!": "script",
            "KBar3": "script",
            "Motion Studio": "script",
            "Voukoder Pro 2026": "plugin",
        }
        self.assertEqual(expected, {name: self.by_name[name]["kind"] for name in expected})


if __name__ == "__main__":
    unittest.main()
