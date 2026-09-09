import unittest
from platform_support import capabilities, summary

class PlatformSupportTests(unittest.TestCase):
    def test_capability_shape(self):
        c = capabilities()
        for key in ("audio_capture", "gui", "whisper", "provider_detection", "chatgpt_desktop_uia"):
            self.assertIn(key, c)
    def test_summary_nonempty(self):
        self.assertTrue(summary())

if __name__ == "__main__": unittest.main()
