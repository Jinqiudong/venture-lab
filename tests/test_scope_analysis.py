from scripts.analyze_scope import analyze


def test_bounded_issue_stays_bounded():
    body = """## Goal\nAdd one configuration file.\n\n## Acceptance criteria\n- Read one public value.\n- Show a recoverable error.\n"""
    result = analyze("Add public configuration", body)
    assert result["verdict"] == "bounded"


def test_cross_layer_issue_is_oversized():
    body = """## Goal\nImplement full authentication.\n\n## Acceptance criteria\n- Add SDK configuration.\n- Persist session in Keychain.\n- Restore and refresh session state.\n- Inject bearer authorization into API calls.\n- Add a SwiftUI login screen.\n- Verify /me.\n- Run CI with xcodebuild.\n- Document a live device acceptance checklist.\n"""
    result = analyze("Implement iOS auth end to end", body)
    assert result["verdict"] == "oversized"
    assert len(result["domains"]) >= 4


def test_ci_plus_live_validation_adds_scope_signal():
    body = """## Acceptance criteria\n- Run tests in CI.\n- Run xcodebuild on a simulator.\n- Validate with real credentials on a live device.\n- Document human acceptance.\n"""
    result = analyze("Finish release validation", body)
    assert "ci" in result["domains"]
    assert "live" in result["domains"]
