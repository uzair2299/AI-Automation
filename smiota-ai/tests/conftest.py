"""Global pytest fixtures and test configuration."""
import os
os.environ["ENVIRONMENT"] = "test"

import pytest
from fastapi.testclient import TestClient

from core.config import get_settings
get_settings.cache_clear()

from agents import register_default_agents
from agents.registry import AgentRegistry
from main import app


@pytest.fixture(scope="session", autouse=True)
def init_test_environment():
    """Bootstrap agent registry and settings for testing."""
    register_default_agents()
    settings = get_settings()
    settings.ENVIRONMENT = "test"
    settings.DEBUG = True
    settings.CHAT_STORAGE_BACKEND = "memory"
    settings.VECTOR_STORE_BACKEND = "memory"
    settings.SMIOTA_AUTH_DUMMY_MODE = True
    settings.REQUIRE_HUMAN_APPROVAL_FOR_REMEDIATION = True
    settings.MCP_REMOTE_ENABLED = False


@pytest.fixture
def client():
    """Synchronous test client for FastAPI endpoints."""
    with TestClient(app) as test_client:
        yield test_client
