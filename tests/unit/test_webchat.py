"""Unit tests for webchat channel endpoints, branding, and welcome message configuration."""
import os


def test_webchat_file_branding_and_welcome():
    """Verify that the embed widget iframe HTML contains Smiota SI branding, chat icon, and welcome message."""
    webchat_path = "smiota-agent-gateway/api/v1/channels/webchat.py" if os.path.exists("smiota-agent-gateway/api/v1/channels/webchat.py") else "src/smiota/api/v1/channels/webchat.py"
    with open(webchat_path, "r", encoding="utf-8") as f:
        html = f.read()

    assert "Hi there! Welcome to Smiota. How can I help you today?" in html
    assert "Smiota SI" in html
    assert 'aria-label="Smiota SI"' in html


def test_webchat_initial_suggested_action_pills():
    """Verify that the embed widget iframe HTML contains the six initial suggested action pills."""
    webchat_path = "smiota-agent-gateway/api/v1/channels/webchat.py" if os.path.exists("smiota-agent-gateway/api/v1/channels/webchat.py") else "src/smiota/api/v1/channels/webchat.py"
    with open(webchat_path, "r", encoding="utf-8") as f:
        html = f.read()

    # 6 Pill IDs
    assert 'data-pill-id="has_package"' in html
    assert 'data-pill-id="lost_code"' in html
    assert 'data-pill-id="locker_issue"' in html
    assert 'data-pill-id="courier_delivery"' in html
    assert 'data-pill-id="package_collected"' in html
    assert 'data-pill-id="human_support"' in html

    # Pill labels and presets
    assert "Do I have a package?" in html
    assert "I lost my code" in html
    assert "Locker won't open" in html
    assert "Courier says delivered" in html
    assert "Package already collected" in html
    assert "Talk to support" in html
    assert "INITIAL_ACTION_PILLS" in html
    assert "sendPresetPill" in html
