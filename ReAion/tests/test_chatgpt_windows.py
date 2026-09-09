import unittest

from chatgpt_windows import build_interview_prompt, is_chatgpt_title


class ChatGPTWindowsTests(unittest.TestCase):
    def test_title_detection_is_specific(self):
        self.assertTrue(is_chatgpt_title("ChatGPT"))
        self.assertTrue(is_chatgpt_title("My interview — ChatGPT"))
        self.assertFalse(is_chatgpt_title("Google Meet"))

    def test_prompt_is_compact_and_grounded(self):
        prompt = build_interview_prompt("  How   do I debug DHCP? ")
        self.assertIn("How do I debug DHCP?", prompt)
        self.assertIn("never invent", prompt)
        self.assertLess(len(prompt), 600)

    def test_empty_question_rejected(self):
        with self.assertRaises(ValueError):
            build_interview_prompt("  ")


if __name__ == "__main__":
    unittest.main()

