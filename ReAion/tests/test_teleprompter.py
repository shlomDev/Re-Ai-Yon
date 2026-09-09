import unittest
from teleprompter import Teleprompter, chunk_answer

class TeleprompterTests(unittest.TestCase):
    def test_chunks_are_short(self):
        chunks = chunk_answer("One short sentence. Another short sentence. A third sentence.", 5)
        self.assertGreater(len(chunks), 1)
    def test_advances_when_spoken(self):
        t = Teleprompter("Check the link state and cable. Then verify the switch port and NIC.", 8)
        self.assertTrue(t.observe("Check the link state and cable then verify the switch port and NIC"))
        self.assertNotEqual(t.index, 0)

if __name__ == "__main__": unittest.main()
