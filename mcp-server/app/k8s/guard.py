"""Input validation and namespace security guards."""
from __future__ import annotations

import re
from typing import Optional
from app.config import settings

# RFC 1123 DNS Subdomain & Label patterns
_DNS_1123_LABEL_RE = re.compile(r"^[a-z0-9]([-a-z0-9]*[a-z0-9])?$")
_DNS_1123_SUBDOMAIN_RE = re.compile(r"^[a-z0-9]([-a-z0-9]*[a-z0-9])?(\.[a-z0-9]([-a-z0-9]*[a-z0-9])?)*$")


class SecurityValidationError(ValueError):
    """Raised when input fails security constraints or DNS validation."""
    pass


def validate_dns_subdomain(name: str, field_name: str = "name") -> str:
    """Validate that name adheres to Kubernetes DNS-1123 subdomain specification (max 253 chars)."""
    if not name or len(name) > 253:
        raise SecurityValidationError(f"Invalid {field_name}: length must be between 1 and 253 characters.")
    if not _DNS_1123_SUBDOMAIN_RE.match(name):
        raise SecurityValidationError(
            f"Invalid {field_name} '{name}': must consist of lower case alphanumeric characters, '-' or '.', "
            "and start and end with an alphanumeric character."
        )
    return name


def validate_dns_label(name: str, field_name: str = "label") -> str:
    """Validate that name adheres to Kubernetes DNS-1123 label specification (max 63 chars)."""
    if not name or len(name) > 63:
        raise SecurityValidationError(f"Invalid {field_name}: length must be between 1 and 63 characters.")
    if not _DNS_1123_LABEL_RE.match(name):
        raise SecurityValidationError(
            f"Invalid {field_name} '{name}': must consist of lower case alphanumeric characters or '-', "
            "and start and end with an alphanumeric character."
        )
    return name


def validate_namespace_access(namespace: Optional[str]) -> Optional[str]:
    """Validate namespace against configured allowlist and denylist.

    If namespace is None or empty (cluster-wide query), allow if allowed_namespaces is empty.
    """
    if not namespace:
        if settings.K8S_ALLOWED_NAMESPACES:
            raise SecurityValidationError(
                f"Cluster-wide operations not permitted when K8S_ALLOWED_NAMESPACES is configured: "
                f"{settings.K8S_ALLOWED_NAMESPACES}"
            )
        return None

    validate_dns_label(namespace, field_name="namespace")

    # 1. Denylist check
    if namespace in settings.K8S_DENIED_NAMESPACES:
        raise SecurityValidationError(f"Access to namespace '{namespace}' is forbidden by denylist policy.")

    # 2. Allowlist check
    if settings.K8S_ALLOWED_NAMESPACES and namespace not in settings.K8S_ALLOWED_NAMESPACES:
        raise SecurityValidationError(
            f"Access to namespace '{namespace}' is forbidden. Allowed namespaces: {settings.K8S_ALLOWED_NAMESPACES}"
        )

    return namespace


def validate_bounded_int(
    val: Optional[int],
    default: int,
    min_val: int = 1,
    max_val: int = 5000,
    field_name: str = "value",
) -> int:
    """Validate integer within inclusive bounds."""
    if val is None:
        return default
    if not isinstance(val, int):
        raise SecurityValidationError(f"{field_name} must be an integer, got {type(val).__name__}")
    if val < min_val or val > max_val:
        raise SecurityValidationError(f"{field_name} must be between {min_val} and {max_val}, got {val}")
    return val

