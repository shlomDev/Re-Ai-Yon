import unittest
from meetings.base import MeetingContext, detect_provider

class MeetingTests(unittest.TestCase):
    def test_supported_providers(self):
        self.assertEqual(detect_provider(MeetingContext(url="https://teams.microsoft.com/l/meetup")), "teams")
        self.assertEqual(detect_provider(MeetingContext(process_name="Zoom.exe")), "zoom")
        self.assertEqual(detect_provider(MeetingContext(url="https://unknown.invalid")), "generic")

if __name__ == "__main__": unittest.main()
