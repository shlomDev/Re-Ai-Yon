import unittest
from answer_engine import looks_like_question, fallback_answer
from teleprompter import Teleprompter

class MultilingualTests(unittest.TestCase):
    def test_hebrew_question_detection(self):
        self.assertTrue(looks_like_question("איך מתמודדים עם תקלה בשרת?"))
    def test_hebrew_fallback(self):
        self.assertIn("הייתי", fallback_answer("איך פותרים בעיית רשת בשרת?"))
    def test_hebrew_teleprompter_words(self):
        self.assertTrue(Teleprompter("בדיקת הכבל והמתג. אימות כתובת ה IP.", 10).current())

if __name__ == "__main__": unittest.main()
