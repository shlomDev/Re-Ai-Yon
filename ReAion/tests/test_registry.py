import unittest
from discovery.registry import extract_meeting_url, validate_interview

class RegistryTests(unittest.TestCase):
    def test_extracts_provider_url(self):
        out = extract_meeting_url("Join: https://meet.google.com/abc-defg-hij.")
        self.assertEqual(out, ("google_meet", "https://meet.google.com/abc-defg-hij"))
    def test_validates_required_fields(self):
        self.assertEqual(validate_interview({"id":"x", "title":"t", "start":"s", "end":"e", "meeting_code":"abc"}), [])

if __name__ == "__main__": unittest.main()
