import json
import unittest
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]


class LocalizationContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads((ROOT / "curation" / "localization.json").read_text(encoding="utf-8"))
        cls.rows = []
        for path in (ROOT / "data").glob("*.jsonl"):
            cls.rows.extend(json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip())
        cls.official_urls = {
            value
            for row in cls.rows
            for value in (row.get("url"), row.get("date_url"))
            if value
        }

    def test_localized_urls_are_explicit_official_mappings(self):
        mappings = self.manifest["localized_urls"]
        self.assertGreaterEqual(len(mappings), 100)
        for original, locales in mappings.items():
            self.assertIn(original, self.official_urls)
            self.assertEqual(set(locales), {"ja"})
            source, target = urlparse(original), urlparse(locales["ja"])
            self.assertEqual(source.hostname, target.hostname)
            self.assertNotEqual(original, locales["ja"])
            if target.hostname == "helpx.adobe.com":
                self.assertTrue(target.path.startswith("/jp/"))
            elif target.hostname == "www.maxon.net":
                self.assertTrue(target.path.startswith("/ja/"))
            else:
                self.fail(f"unapproved localized host: {target.hostname}")

    def test_adobe_categories_have_official_english_and_japanese_labels(self):
        rules = self.manifest["official_category_rules"]
        self.assertEqual(len({rule["id"] for rule in rules}), len(rules))
        self.assertTrue({"blur-sharpen", "color-correction", "distort", "generate", "immersive-video"}.issubset({rule["id"] for rule in rules}))
        for rule in rules:
            self.assertTrue(rule["patterns"])
            self.assertTrue(rule["labels"]["en"])
            self.assertTrue(rule["labels"]["ja"])

    def test_site_taxonomy_is_declared_separately_from_vendor_categories(self):
        policy = self.manifest["policy"]
        self.assertIn("site-defined", policy["taxonomy"])
        self.assertIn("Official product spelling", policy["product_names"])
        self.assertIn("Traditional Chinese", policy["descriptions"])


if __name__ == "__main__":
    unittest.main()
