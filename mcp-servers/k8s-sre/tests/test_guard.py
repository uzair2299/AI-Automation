"""Unit tests for input validation and namespace security guards."""
import pytest
from app.config import settings
from app.k8s.guard import (
    SecurityValidationError,
    validate_bounded_int,
    validate_dns_label,
    validate_dns_subdomain,
    validate_namespace_access,
)


def test_validate_dns_subdomain_valid():
    assert validate_dns_subdomain("smiota-prod") == "smiota-prod"
    assert validate_dns_subdomain("service.default.svc.cluster.local") == "service.default.svc.cluster.local"


def test_validate_dns_subdomain_invalid():
    with pytest.raises(SecurityValidationError):
        validate_dns_subdomain("-invalid-start")
    with pytest.raises(SecurityValidationError):
        validate_dns_subdomain("INVALID_CAPS")
    with pytest.raises(SecurityValidationError):
        validate_dns_subdomain("has space")


def test_validate_dns_label():
    assert validate_dns_label("default") == "default"
    assert validate_dns_label("my-pod-123") == "my-pod-123"
    with pytest.raises(SecurityValidationError):
        validate_dns_label("label.with.dots")


def test_validate_namespace_access_denylist():
    settings.K8S_DENIED_NAMESPACES = ["kube-system-sensitive", "restricted-vault"]
    with pytest.raises(SecurityValidationError, match="forbidden by denylist"):
        validate_namespace_access("restricted-vault")


def test_validate_namespace_access_allowlist():
    settings.K8S_ALLOWED_NAMESPACES = ["smiota-prod", "smiota-staging"]
    assert validate_namespace_access("smiota-prod") == "smiota-prod"

    with pytest.raises(SecurityValidationError, match="Allowed namespaces"):
        validate_namespace_access("kube-system")

    # Reset allowlist
    settings.K8S_ALLOWED_NAMESPACES = []


def test_validate_bounded_int():
    assert validate_bounded_int(50, default=100, min_val=1, max_val=500) == 50
    assert validate_bounded_int(None, default=100) == 100

    with pytest.raises(SecurityValidationError):
        validate_bounded_int(10000, default=100, min_val=1, max_val=5000)

    with pytest.raises(SecurityValidationError):
        validate_bounded_int(-5, default=100, min_val=1, max_val=5000)

