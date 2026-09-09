import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import app_paths

class AppPathsTests(unittest.TestCase):
    def test_data_dir_can_be_isolated_per_user(self):
        with tempfile.TemporaryDirectory() as d, patch.dict(os.environ, {"INTERVIEWCOPILOT_DATA_DIR": d}):
            self.assertEqual(app_paths.user_data_dir(), Path(d))
            self.assertEqual(app_paths.private_path("candidate_profile.md"), Path(d) / "candidate_profile.md")

if __name__ == "__main__": unittest.main()
