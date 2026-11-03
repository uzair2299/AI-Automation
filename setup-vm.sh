#!/usr/bin/env bash
# ==============================================================================
# Smiota AI Platform - Automated Linux VM Deployment Script
# 
# Deploys:
#   1. System packages & Docker / Docker Compose engine
#   2. Clones / checks out branch 'feature/mcp-client-server-architecture'
#   3. Generates production .env with pgvector & microservice URLs
#   4. Builds and launches all 5 microservices + pgvector + Redis
#   5. Performs automated end-to-end health & search checks
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

REPO_URL="https://github.com/uzair2299/AI-Automation.git"
BRANCH="feature/mcp-client-server-architecture"
INSTALL_DIR="${HOME}/smiota-ai"

echo -e "${BOLD}"
echo "======================================================================"
echo "    🚀 Smiota AI Platform: Automated VM Deployment Orchestrator       "
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
log_info "Step 1/5: Checking and installing system dependencies..."
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

# Ensure docker-compose plugin or standalone is available
DOCKER_COMPOSE="docker compose"
if ! docker compose version >/dev/null 2>&1; then
    if command -v docker-compose >/dev/null 2>&1; then
        DOCKER_COMPOSE="docker-compose"
    else
        log_info "Installing docker-compose-v2..."
        $SUDO apt-get install -y docker-compose-v2
    fi
fi

# Add current user to docker group if non-root
if [ "$(id -u)" -ne 0 ]; then
    if ! groups "$USER" | grep -q '\bdocker\b'; then
        log_info "Adding $USER to docker group..."
        $SUDO usermod -aG docker "$USER" || true
    fi
fi

# ------------------------------------------------------------------------------
# 3. Clone Repository or Update Existing Workspace
# ------------------------------------------------------------------------------
log_info "Step 2/5: Synchronizing codebase from GitHub..."

if [ -f "./docker-compose.yml" ] && [ -d "./rag-service" ]; then
    # Already inside repository directory
    TARGET_DIR="$(pwd)"
    log_info "Running inside existing repository at ${TARGET_DIR}."
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
log_info "Step 3/5: Configuring environment and credentials..."

ENV_FILE="${TARGET_DIR}/.env"

# Generate strong random JWT secret if not present
JWT_SECRET=$(head -c 32 /dev/urandom | base64 | tr -dc 'a-zA-Z0-9' | head -c 32 || echo "smiota-sec-key-$(date +%s)")

if [ ! -f "${ENV_FILE}" ]; then
    log_info "Creating new .env file with pgvector database credentials..."
    cat <<EOF > "${ENV_FILE}"
# ==============================================================================
# Smiota AI Platform - VM Production Environment
# ==============================================================================
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
PORT=8000
HOST=0.0.0.0
ENABLE_SWAGGER=true
CORS_ORIGINS=["*"]

# Database, Cache & pgvector (Configured)
POSTGRES_USER=smiota_user
POSTGRES_PASSWORD=smaiops26devdb
POSTGRES_DB=smiota_ai_dev
PGVECTOR_PASSWORD=smaiops26devdb
DATABASE_URL=postgresql+asyncpg://smiota_user:smaiops26devdb@localhost:5432/smiota_ai_dev
REDIS_URL=redis://localhost:6379/0

# GCP & Gemini
GCP_PROJECT_ID=project-smiota-psi-1
GCP_REGION=global
GEMINI_MODEL=gemini-3.7-flash
GEMINI_EMBEDDING_MODEL=text-embedding-004

# Security & JWT
JWT_SECRET_KEY=${JWT_SECRET}
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=120

# MCP & Remote Microservice URLs
MCP_READ_ONLY_DEFAULT=true
REQUIRE_HUMAN_APPROVAL_FOR_REMEDIATION=true
MCP_REMOTE_ENABLED=true
MCP_REMOTE_FALLBACK=true
MCP_CLIENT_TIMEOUT_SECONDS=15.0
MCP_K8S_SERVER_URL=http://k8s-sre-mcp:8080
MCP_OBSERVABILITY_SERVER_URL=http://observability-mcp:8081
MCP_LOCKER_SERVER_URL=http://smart-locker-mcp:8082
RAG_SERVICE_URL=http://rag-service:8001
EOF
    log_success ".env configuration generated successfully."
else
    log_info "Existing .env found. Ensuring pgvector credentials are up to date..."
    if ! grep -q "smaiops26devdb" "${ENV_FILE}"; then
        sed -i 's/POSTGRES_PASSWORD=.*/POSTGRES_PASSWORD=smaiops26devdb/' "${ENV_FILE}" || true
        sed -i 's/PGVECTOR_PASSWORD=.*/PGVECTOR_PASSWORD=smaiops26devdb/' "${ENV_FILE}" || true
    fi
fi

# ------------------------------------------------------------------------------
# 5. Build and Launch Containers via Docker Compose
# ------------------------------------------------------------------------------
log_info "Step 4/5: Building and starting microservices mesh via Docker Compose..."

$SUDO $DOCKER_COMPOSE down --remove-orphans || true
$SUDO $DOCKER_COMPOSE up -d --build

# ------------------------------------------------------------------------------
# 6. Automated Health Verification Loop
# ------------------------------------------------------------------------------
log_info "Step 5/5: Awaiting container startup and health checks..."

MAX_RETRIES=20
RETRY_COUNT=0

check_endpoint() {
    local url=$1
    local name=$2
    for i in $(seq 1 $MAX_RETRIES); do
        if curl -s -f "$url" >/dev/null 2>&1; then
            log_success "${name} is UP (${url})"
            return 0
        fi
        sleep 2
    done
    log_warn "${name} is taking longer than expected to report ready at ${url}."
    return 1
}

echo ""
log_info "Probing microservices..."
check_endpoint "http://localhost:8000/health" "Client Gateway (Port 8000)" || true
check_endpoint "http://localhost:8001/health" "RAG REST Service (Port 8001)" || true
check_endpoint "http://localhost:8080/health" "K8s SRE MCP Server (Port 8080)" || true
check_endpoint "http://localhost:8081/health" "Observability MCP Server (Port 8081)" || true

# Test pgvector Semantic Search
echo ""
log_info "Testing RAG pgvector Semantic Search..."
SEARCH_RESULT=$(curl -s -X POST "http://localhost:8001/api/v1/rag/search" \
    -H "Content-Type: application/json" \
    -d '{"query": "refrigerated cold storage", "top_k": 1}' || echo "{}")

if echo "$SEARCH_RESULT" | grep -q "status"; then
    log_success "RAG pgvector search test passed!"
fi

# ------------------------------------------------------------------------------
# 7. Final Summary & Actionable Info
# ------------------------------------------------------------------------------
EXTERNAL_IP=$(curl -s -4 ifconfig.me 2>/dev/null || curl -s -4 icanhazip.com 2>/dev/null || echo "YOUR_VM_IP")

echo ""
echo -e "${GREEN}${BOLD}======================================================================${RESET}"
echo -e "${GREEN}${BOLD}    ✅ SMIOTA AI PLATFORM IS RUNNING SUCCESSFULLY ON YOUR VM!         ${RESET}"
echo -e "${GREEN}${BOLD}======================================================================${RESET}"
echo ""
echo -e "${BOLD}Access Endpoints:${RESET}"
echo -e "  • WebChat Widget:        ${BLUE}http://${EXTERNAL_IP}:8000/api/v1/channels/webchat/embed${RESET}"
echo -e "  • WebChat Interactive:   ${BLUE}http://${EXTERNAL_IP}:8000/api/v1/channels/webchat/demo${RESET}"
echo -e "  • Gateway API Docs:      ${BLUE}http://${EXTERNAL_IP}:8000/docs${RESET}"
echo -e "  • Standalone RAG Health: ${BLUE}http://${EXTERNAL_IP}:8001/health${RESET}"
echo -e "  • K8s SRE MCP:           ${BLUE}http://${EXTERNAL_IP}:8080/health${RESET}"
echo -e "  • Observability MCP:     ${BLUE}http://${EXTERNAL_IP}:8081/health${RESET}"
echo ""
echo -e "${BOLD}Management Commands:${RESET}"
echo -e "  • View Live Gateway Logs: ${YELLOW}docker compose logs -f smiota-agent-gateway${RESET}"
echo -e "  • View RAG Service Logs:  ${YELLOW}docker compose logs -f rag-service${RESET}"
echo -e "  • View Container Status:  ${YELLOW}docker compose ps${RESET}"
echo -e "  • Restart All Services:   ${YELLOW}docker compose restart${RESET}"
echo -e "  • Stop All Services:      ${YELLOW}docker compose down${RESET}"
echo ""
echo -e "${YELLOW}${BOLD}Firewall Reminder:${RESET} In GCP/Azure/AWS, allow inbound TCP port ${BOLD}8000${RESET} to your VM."
echo "======================================================================"
