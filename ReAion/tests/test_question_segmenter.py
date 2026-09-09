import unittest
from question_segmenter import QuestionSegmenter

class QuestionSegmenterTests(unittest.TestCase):
    def test_emits_complete_question(self):
        s = QuestionSegmenter()
        self.assertIsNone(s.add("How would you troubleshoot", 1))
        out = s.add("a server with no network connectivity?", 2)
        self.assertEqual(out.text, "How would you troubleshoot a server with no network connectivity?")
    def test_silence_flush(self):
        s = QuestionSegmenter(silence_seconds=1)
        s.add("Why do you use Redfish", 1)
        out = s.flush_if_silent(2.1)
        self.assertIsNotNone(out)
    def test_indirect_question_without_starter(self):
        s = QuestionSegmenter(silence_seconds=1)
        s.add("A server in the lab suddenly loses connectivity", 1)
        out = s.flush_if_silent(2.1)
        self.assertIsNotNone(out)
    def test_duplicate_suppressed(self):
        s = QuestionSegmenter()
        self.assertIsNotNone(s.add("What is DHCP?", 1))
        self.assertIsNone(s.add("What is DHCP?", 2))

if __name__ == "__main__": unittest.main()
