import unittest
from claude_desktop import is_claude_title

class ClaudeDesktopTests(unittest.TestCase):
    def test_title_detection(self):
        self.assertTrue(is_claude_title("Claude"))
        self.assertTrue(is_claude_title("Claude Desktop — Free"))
        self.assertFalse(is_claude_title("ChatGPT"))

if __name__ == "__main__": unittest.main()
