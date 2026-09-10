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

    def test_side_panel_uses_reaion_dark_grey_violet_palette(self):
        root=Path(__file__).resolve().parents[1]/"chrome_extension"
        css=(root/"sidepanel.css").read_text()
        html=(root/"sidepanel.html").read_text()
        self.assertIn("--violet: #7442cf", css)
        self.assertIn("--bg: #212121", css)
        self.assertNotIn("#ffc400", css.lower())
        self.assertNotIn("yellow", css.lower())
        self.assertIn('class="logo" aria-hidden="true">↑</div>', html)

    def test_desktop_view_matches_browser_palette(self):
        root=Path(__file__).resolve().parents[1]
        source=(root/"interview_assistant_gui.py").read_text()
        for color in ("#212121", "#7442cf", "#f8f7fb"):
            self.assertIn(color, source)
        self.assertNotIn("#ffc400", source.lower())

if __name__ == "__main__": unittest.main()
