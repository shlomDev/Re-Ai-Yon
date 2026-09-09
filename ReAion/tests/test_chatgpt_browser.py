import unittest
from chatgpt_browser import ChatGPTBrowserClient

class BrowserTests(unittest.TestCase):
    def test_defaults_are_visible_and_safe(self):
        c = ChatGPTBrowserClient()
        self.assertFalse(c.headless)
        self.assertTrue(c.url.startswith("https://"))

if __name__ == "__main__": unittest.main()
