"""Unit tests for webchat channel endpoints and welcome message configuration."""
from fastapi.testclient import TestClient
from smiota.main import app
from smiota.core.config import get_settings

client = TestClient(app)


def test_webchat_config_default_welcome_message():
    """Verify that webchat config returns the expected default welcome message."""
    response = client.get("/api/v1/channels/webchat/config")
    assert response.status_code == 200
    data = response.json()
    assert data["welcome_message"] == "Hi there! Welcome to Smiota. How can I help you today?"
    assert data["welcome_title"] == "Welcome to Smiota!"


def test_webchat_embed_html_default_welcome_message():
    """Verify that the embed widget iframe HTML contains the default welcome message."""
    response = client.get("/api/v1/channels/webchat/embed")
    assert response.status_code == 200
    html = response.text
    assert "Hi there! Welcome to Smiota. How can I help you today?" in html


def test_webchat_embed_html_custom_welcome_override():
    """Verify that query parameters can override the default welcome message."""
    custom_msg = "Hello resident! Welcome to your parcel lockers."
    response = client.get(f"/api/v1/channels/webchat/embed?welcome_msg={custom_msg}")
    assert response.status_code == 200
    assert custom_msg in response.text
