import json
import unittest
from pathlib import Path

class ExtensionAssetTests(unittest.TestCase):
    def test_chrome_side_panel_is_declared(self):
        root=Path(__file__).resolve().parents[1]/"chrome_extension"
        manifest=json.loads((root/"manifest.json").read_text())
        self.assertIn("sidePanel", manifest["permissions"])
        self.assertEqual(manifest["side_panel"]["default_path"], "sidepanel.html")
        self.assertTrue((root/"sidepanel.js").exists())

if __name__ == "__main__": unittest.main()
