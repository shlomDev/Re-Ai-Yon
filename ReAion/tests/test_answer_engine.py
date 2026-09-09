import unittest
from unittest.mock import patch

import answer_engine


class AnswerEngineTests(unittest.TestCase):
    def test_non_windows_chatgpt_failure_falls_back_safely(self):
        with patch.dict(answer_engine.SETTINGS["answer_engine"], provider="chatgpt_windows"), patch("chatgpt_windows.ChatGPTWindowsClient.submit_question", side_effect=RuntimeError("unavailable")), patch.object(answer_engine, "BANK", {}):
            answer, source = answer_engine.generate_answer(
                "How would you troubleshoot a server with no network connectivity?"
            )
        self.assertIn("fallback", source)
        self.assertIn("verify", answer.lower())
        self.assertGreater(len(answer), 40)


if __name__ == "__main__":
    unittest.main()
