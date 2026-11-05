# ==============================================================================
# Smiota Platform - Local Development Setup Script (Windows PowerShell)
# ==============================================================================

Write-Host "`n=======================================================" -ForegroundColor Cyan
Write-Host "   🚀 Smiota Monorepo: Developer Environment Setup" -ForegroundColor Cyan
Write-Host "=======================================================`n" -ForegroundColor Cyan

$ROOT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Definition

# ------------------------------------------------------------------------------
# 1. Prerequisite Checks
# ------------------------------------------------------------------------------
Write-Host "[1/4] Checking Prerequisites..." -ForegroundColor Yellow

# Check Java
try {
    $javaVersion = java -version 2>&1 | Select-String "version" | Select-Object -First 1
    Write-Host "  ✅ Java detected: $javaVersion" -ForegroundColor Green
} catch {
    Write-Host "  ❌ Java not found! Please install OpenJDK 17 or Eclipse Temurin 17." -ForegroundColor Red
}

# Check Maven
try {
    $mvnVersion = mvn -v 2>&1 | Select-String "Apache Maven" | Select-Object -First 1
    Write-Host "  ✅ Maven detected: $mvnVersion" -ForegroundColor Green
} catch {
    Write-Host "  ❌ Maven not found! Please install Apache Maven and add to PATH." -ForegroundColor Red
}

# Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  ✅ Python detected: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  ❌ Python not found! Please install Python 3.10+." -ForegroundColor Red
}

# Check Docker
try {
    $dockerVersion = docker --version 2>&1
    Write-Host "  ✅ Docker detected: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "  ⚠️  Docker not found. Docker is optional for local development but required for containers." -ForegroundColor Yellow
}

# ------------------------------------------------------------------------------
# 2. Setup Environment Variables (.env)
# ------------------------------------------------------------------------------
Write-Host "`n[2/4] Checking Environment Configuration (.env)..." -ForegroundColor Yellow
$envFile = Join-Path $ROOT_DIR ".env"
$envExample = Join-Path $ROOT_DIR ".env.example"

if (-not (Test-Path $envFile)) {
    if (Test-Path $envExample) {
        Copy-Item $envExample $envFile
        Write-Host "  ✅ Created .env from .env.example" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️ .env.example not found." -ForegroundColor Yellow
    }
} else {
    Write-Host "  ✅ .env file already exists." -ForegroundColor Green
}

# ------------------------------------------------------------------------------
# 3. Build Java Services (smiota-core)
# ------------------------------------------------------------------------------
Write-Host "`n[3/4] Building Java Services (smiota-core)..." -ForegroundColor Yellow
$coreDir = Join-Path $ROOT_DIR "smiota-core"

if (Test-Path $coreDir) {
    Push-Location $coreDir
    Write-Host "  Running: mvn clean install -DskipTests..." -ForegroundColor Gray
    mvn clean install -DskipTests
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✅ Java backend (smiota-common-model & smiota-core-api) built successfully!" -ForegroundColor Green
    } else {
        Write-Host "  ❌ Java build failed. Check the error output above." -ForegroundColor Red
    }
    Pop-Location
}

# ------------------------------------------------------------------------------
# 4. Setup Python AI Services (smiota-ai)
# ------------------------------------------------------------------------------
Write-Host "`n[4/4] Setting up Python AI Services (smiota-ai)..." -ForegroundColor Yellow
$aiDir = Join-Path $ROOT_DIR "smiota-ai"

if (Test-Path $aiDir) {
    Push-Location $aiDir
    $venvDir = Join-Path $aiDir ".venv"
    if (-not (Test-Path $venvDir)) {
        Write-Host "  Creating virtual environment in smiota-ai\.venv..." -ForegroundColor Gray
        python -m venv .venv
        Write-Host "  ✅ Created .venv" -ForegroundColor Green
    } else {
        Write-Host "  ✅ .venv already exists." -ForegroundColor Green
    }
    Pop-Location
}

Write-Host "`n=======================================================" -ForegroundColor Cyan
Write-Host "   🎉 Setup Completed!" -ForegroundColor Green
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host "To run the full stack with Docker:" -ForegroundColor White
Write-Host "  docker compose up -d`n" -ForegroundColor Yellow

Write-Host "To run Java API locally:" -ForegroundColor White
Write-Host "  cd smiota-core\smiota-core-api; mvn spring-boot:run`n" -ForegroundColor Yellow

Write-Host "To run Python AI Gateway locally:" -ForegroundColor White
Write-Host "  cd smiota-ai; .\.venv\Scripts\Activate.ps1; uvicorn smiota-agent-gateway.main:app --reload`n" -ForegroundColor Yellow
