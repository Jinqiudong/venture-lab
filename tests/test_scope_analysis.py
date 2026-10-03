import unittest

from scripts.analyze_scope import analyze


class ScopeAnalysisTests(unittest.TestCase):
    def test_bounded_issue_stays_bounded(self):
        body = """## Goal
Add one configuration file.

## Acceptance criteria
- Read one public value.
- Show a recoverable error.
"""
        result = analyze("Add public configuration", body)
        self.assertEqual(result["verdict"], "bounded")

    def test_cross_layer_issue_is_oversized(self):
        body = """## Goal
Implement full authentication.

## Acceptance criteria
- Add SDK configuration.
- Persist session in Keychain.
- Restore and refresh session state.
- Inject bearer authorization into API calls.
- Add a SwiftUI login screen.
- Verify /me.
- Run CI with xcodebuild.
- Document a live device acceptance checklist.
"""
        result = analyze("Implement iOS auth end to end", body)
        self.assertEqual(result["verdict"], "oversized")
        self.assertGreaterEqual(len(result["domains"]), 4)

    def test_ci_plus_live_validation_adds_scope_signal(self):
        body = """## Acceptance criteria
- Run tests in CI.
- Run xcodebuild on a simulator.
- Validate with real credentials on a live device.
- Document human acceptance.
"""
        result = analyze("Finish release validation", body)
        self.assertIn("ci", result["domains"])
        self.assertIn("live", result["domains"])


if __name__ == "__main__":
    unittest.main()
