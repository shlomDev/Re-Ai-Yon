import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class OneClickTests(unittest.TestCase):
    def test_launchers_exist_and_bootstrap(self):
        bat = (ROOT / "Launch_ReAion.bat").read_text(encoding="utf-8")
        ps = (ROOT / "Launch_ReAion.ps1").read_text(encoding="utf-8")
        for text in (bat, ps):
            self.assertIn("playwright install chromium", text)
            self.assertIn("auto_meet_watch.py", text)
            self.assertIn("setup_private_profile.py", text)

if __name__ == "__main__": unittest.main()
