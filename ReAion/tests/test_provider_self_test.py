import unittest
from provider_self_test import check_provider

class ProviderSelfTestTests(unittest.TestCase):
    def test_builtin_ready(self):
        self.assertEqual(check_provider("built_in", ({}))[0], True)
    def test_missing_api_key_is_not_ready(self):
        self.assertFalse(check_provider("anthropic", {"api_key_env":"__MISSING_INTERVIEWCOPILOT_KEY__"})[0])

if __name__ == "__main__": unittest.main()
