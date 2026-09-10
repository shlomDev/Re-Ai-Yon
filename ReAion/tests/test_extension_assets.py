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

    def test_side_panel_uses_reaion_violet_amber_palette(self):
        root=Path(__file__).resolve().parents[1]/"chrome_extension"
        css=(root/"sidepanel.css").read_text()
        html=(root/"sidepanel.html").read_text()
        self.assertIn("--violet: #7442cf", css)
        self.assertIn("--amber: #ffc400", css)
        self.assertIn("--bg: #171717", css)
        self.assertIn('class="logo" aria-hidden="true">↑</div>', html)

    def test_desktop_view_matches_browser_palette(self):
        root=Path(__file__).resolve().parents[1]
        source=(root/"interview_assistant_gui.py").read_text()
        for color in ("#171717", "#7442cf", "#ffc400", "#f8f7fb"):
            self.assertIn(color, source)

if __name__ == "__main__": unittest.main()
