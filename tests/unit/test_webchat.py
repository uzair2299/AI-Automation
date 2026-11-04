"""Unit tests for webchat channel endpoints, branding, and welcome message configuration."""
from fastapi.testclient import TestClient
from smiota.main import app

client = TestClient(app)


def test_webchat_config_default_welcome_message():
    """Verify that webchat config returns the expected default welcome message and assistant name."""
    response = client.get("/api/v1/channels/webchat/config")
    assert response.status_code == 200
    data = response.json()
    assert data["welcome_message"] == "Hi there! Welcome to Smiota. How can I help you today?"
    assert data["welcome_title"] == "Welcome to Smiota!"
    assert data["assistant_name"] == "Smiota SI"


def test_webchat_embed_html_default_welcome_message():
    """Verify that the embed widget iframe HTML contains Smiota SI branding, chat icon, and welcome message."""
    response = client.get("/api/v1/channels/webchat/embed")
    assert response.status_code == 200
    html = response.text
    assert "Hi there! Welcome to Smiota. How can I help you today?" in html
    assert "Smiota SI" in html
    assert "aria-label=\"Smiota SI\"" in html


def test_webchat_embed_html_custom_welcome_override():
    """Verify that query parameters can override the default welcome message and assistant name."""
    custom_msg = "Hello resident! Welcome to your parcel lockers."
    custom_name = "Locker Concierge"
    response = client.get(f"/api/v1/channels/webchat/embed?welcome_msg={custom_msg}&assistant_name={custom_name}")
    assert response.status_code == 200
    assert custom_msg in response.text
    assert custom_name in response.text
