#!/usr/bin/env bash
# ==============================================================================
# Smiota Platform - Automated Linux VM Monorepo Deployment Orchestrator
#
# Deploys:
#   1. System packages & Docker engine
#   2. Validates/creates root .env from .env.example
#   3. Builds and launches all monorepo containers (Java API + Python AI + MCP)
#   4. Performs automated end-to-end health checks on both stacks
# ==============================================================================

set -euo pipefail

# Text formatting
BOLD="\033[1m"
GREEN="\033[0;32m"
BLUE="\033[0;34m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
RESET="\033[0m"

log_info() { echo -e "${BLUE}${BOLD}[INFO]${RESET} $1"; }
log_success() { echo -e "${GREEN}${BOLD}[SUCCESS]${RESET} $1"; }
log_warn() { echo -e "${YELLOW}${BOLD}[WARNING]${RESET} $1"; }
log_error() { echo -e "${RED}${BOLD}[ERROR]${RESET} $1"; }

REPO_URL="${REPO_URL:-https://dev.azure.com/smiota/smiotaplatform/_git/smiota-aiops}"
BRANCH="${BRANCH:-feature/mcp-client-server-architecture}"
INSTALL_DIR="${HOME}/smiota"

echo -e "${BOLD}"
echo "======================================================================"
echo "    🚀 Smiota Platform: Unified Monorepo VM Deployment Orchestrator   "
echo "======================================================================"
echo -e "${RESET}"

# ------------------------------------------------------------------------------
# 1. Root & Sudo Privilege Check
# ------------------------------------------------------------------------------
SUDO=""
if [ "$(id -u)" -ne 0 ]; then
    if command -v sudo >/dev/null 2>&1; then
        SUDO="sudo"
    else
        log_error "This script requires sudo privileges to install Docker. Please run as root or install sudo."
        exit 1
    fi
fi

# ------------------------------------------------------------------------------
# 2. Package Updates & Docker Engine Installation
# ------------------------------------------------------------------------------
log_info "Step 1/5: Checking system dependencies and host services..."
$SUDO apt-get update -y
$SUDO apt-get install -y --no-install-recommends \
    git \
    curl \
    jq \
    ca-certificates \
    gnupg \
    lsb-release

if ! command -v docker >/dev/null 2>&1; then
    log_info "Docker not found. Installing Docker engine..."
    $SUDO apt-get install -y docker.io docker-compose-v2
    $SUDO systemctl enable --now docker
else
    log_info "Docker is already installed ($(docker --version))."
fi

DOCKER_COMPOSE="docker compose"
if ! docker compose version >/dev/null 2>&1; then
    if command -v docker-compose >/dev/null 2>&1; then
        DOCKER_COMPOSE="docker-compose"
    else
        log_info "Installing docker-compose-v2..."
        $SUDO apt-get install -y docker-compose-v2
    fi
fi

# ------------------------------------------------------------------------------
# 3. Synchronize Codebase
# ------------------------------------------------------------------------------
log_info "Step 2/5: Synchronizing codebase from repository..."

if [ -f "./docker-compose.yml" ] && [ -d "./smiota-core" ] && [ -d "./smiota-ai" ]; then
    TARGET_DIR="$(pwd)"
    log_info "Running inside existing monorepo repository at ${TARGET_DIR}."
else
    if [ -d "${INSTALL_DIR}/.git" ]; then
        log_info "Updating repository in ${INSTALL_DIR}..."
        cd "${INSTALL_DIR}"
        git fetch origin "${BRANCH}"
        git checkout "${BRANCH}"
        git pull origin "${BRANCH}"
    else
        log_info "Cloning repository into ${INSTALL_DIR}..."
        git clone -b "${BRANCH}" "${REPO_URL}" "${INSTALL_DIR}"
        cd "${INSTALL_DIR}"
    fi
    TARGET_DIR="${INSTALL_DIR}"
fi

# ------------------------------------------------------------------------------
# 4. Generate Production .env Configuration
# ------------------------------------------------------------------------------
log_info "Step 3/5: Configuring environment..."

ENV_FILE="${TARGET_DIR}/.env"
if [ ! -f "$ENV_FILE" ]; then
    if [ -f "${TARGET_DIR}/.env.example" ]; then
        cp "${TARGET_DIR}/.env.example" "$ENV_FILE"
        log_success "Created .env from .env.example."
    fi
fi

# ------------------------------------------------------------------------------
# 5. Build and Launch Containers
# ------------------------------------------------------------------------------
log_info "Step 4/5: Building and starting Smiota microservices..."
cd "$TARGET_DIR"

$DOCKER_COMPOSE down --remove-orphans || true
$DOCKER_COMPOSE build --parallel
$DOCKER_COMPOSE up -d

log_success "All containers launched."

# ------------------------------------------------------------------------------
# 6. Automated Health Verification
# ------------------------------------------------------------------------------
log_info "Step 5/5: Running health checks..."
sleep 10

# Check Python AI Gateway
if curl -sf http://localhost:8000/health >/dev/null 2>&1 || curl -sf http://localhost:8000/api/v1/health >/dev/null 2>&1; then
    log_success "Smiota AI Gateway (Port 8000) is HEALTHY."
else
    log_warn "Smiota AI Gateway is still initializing or returned non-200. Check: docker logs smiota-agent-gateway"
fi

# Check Java Core API
if curl -sf http://localhost:8080/actuator/health >/dev/null 2>&1 || curl -sf http://localhost:8080/api/v1/health >/dev/null 2>&1; then
    log_success "Smiota Core API (Port 8080) is HEALTHY."
else
    log_info "Smiota Core API is spinning up (check: docker logs smiota-core-api)."
fi

echo -e "\n${GREEN}${BOLD}======================================================================${RESET}"
echo -e "${GREEN}${BOLD}   🎉 Smiota Platform Monorepo Deployment Complete!                   ${RESET}"
echo -e "${GREEN}${BOLD}======================================================================${RESET}"
echo -e "   - Java Core API:       http://localhost:8080"
echo -e "   - AI Agent Gateway:    http://localhost:8000"
echo -e "   - Smart Locker MCP:    http://localhost:8082"
echo -e "   - RAG Knowledge Base:  http://localhost:8001"
echo ""
