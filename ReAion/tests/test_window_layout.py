import unittest

from window_layout import split_work_area


class WindowLayoutTests(unittest.TestCase):
    def test_split_is_contiguous_and_complete(self):
        meeting, answer = split_work_area(0, 0, 1920, 1040, 0.63)
        self.assertEqual(meeting.left + meeting.width, answer.left)
        self.assertEqual(meeting.width + answer.width, 1920)
        self.assertEqual((meeting.top, answer.top), (0, 0))
        self.assertEqual((meeting.height, answer.height), (1040, 1040))

    def test_invalid_ratio_rejected(self):
        with self.assertRaises(ValueError):
            split_work_area(0, 0, 1920, 1080, 0.9)


if __name__ == "__main__":
    unittest.main()
