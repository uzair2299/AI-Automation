"""Application-wide constants, enums, and system defaults."""
from enum import Enum


class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TEST = "test"


class ChannelType(str, Enum):
    TEAMS = "teams"
    IDE = "ide"
    WEBCHAT = "webchat"
    API = "api"


class AgentDomain(str, Enum):
    AIOPS = "aiops"
    SECURITY = "security"
    DEVELOPER = "developer"
    QA = "qa"
    CUSTOMER = "customer"


class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    EXECUTED = "executed"


class ToolAccessLevel(str, Enum):
    READ_ONLY = "read_only"
    REMEDIATION = "remediation"


# System Limits & Defaults
DEFAULT_MAX_TOKENS = 4096
DEFAULT_TEMPERATURE = 0.2
DEFAULT_TIMEOUT_SECONDS = 30.0
MAX_AGENT_ITERATIONS = 5
DEFAULT_RAG_TOP_K = 5
