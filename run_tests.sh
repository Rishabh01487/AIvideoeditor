#!/bin/bash
# Comprehensive Test Suite for AI Video Editor Platform
# This script runs all tests and generates a report

echo "======================================"
echo "AI VIDEO EDITOR PLATFORM - TEST SUITE"
echo "======================================"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test results
PASSED=0
FAILED=0
SKIPPED=0

# Helper functions
pass() {
    echo -e "${GREEN}✓ PASS${NC}: $1"
    ((PASSED++))
}

fail() {
    echo -e "${RED}✗ FAIL${NC}: $1"
    ((FAILED++))
}

skip() {
    echo -e "${YELLOW}⊘ SKIP${NC}: $1"
    ((SKIPPED++))
}

info() {
    echo -e "${BLUE}ℹ INFO${NC}: $1"
}

# Start testing
echo ""
echo "====== PHASE 1: DOCKER & ENVIRONMENT CHECKS ======"

# Check Docker
if command -v docker &> /dev/null; then
    pass "Docker installed"
else
    fail "Docker not installed"
    exit 1
fi

# Check Docker Compose
if command -v docker-compose &> /dev/null; then
    pass "Docker Compose installed"
else
    fail "Docker Compose not installed"
    exit 1
fi

# Check project structure
if [ -f "docker-compose.yml" ]; then
    pass "docker-compose.yml exists"
else
    fail "docker-compose.yml not found"
    exit 1
fi

if [ -f "backend/app/main.py" ]; then
    pass "Backend app exists"
else
    fail "Backend app not found"
fi

if [ -f "frontend/src/App.js" ]; then
    pass "Frontend app exists"
else
    fail "Frontend app not found"
fi

echo ""
echo "====== PHASE 2: DOCKER SERVICES STATUS ======"

info "Checking Docker service status..."
docker-compose ps 2>/dev/null | grep -q "postgres" && pass "PostgreSQL container exists" || fail "PostgreSQL container missing"
docker-compose ps 2>/dev/null | grep -q "redis" && pass "Redis container exists" || fail "Redis container missing"
docker-compose ps 2>/dev/null | grep -q "minio" && pass "MinIO container exists" || fail "MinIO container missing"
docker-compose ps 2>/dev/null | grep -q "backend" && pass "Backend container exists" || fail "Backend container missing"
docker-compose ps 2>/dev/null | grep -q "frontend" && pass "Frontend container exists" || fail "Frontend container missing"

echo ""
echo "====== PHASE 3: CODE VALIDATION ======"

# Check Python syntax
if python3 -m py_compile backend/app/main.py 2>/dev/null; then
    pass "Backend Python syntax valid"
else
    fail "Backend Python syntax invalid"
fi

# Check requirements.txt
if [ -f "backend/requirements.txt" ]; then
    pass "requirements.txt exists"
    REQUIRED_PACKAGES=("fastapi" "sqlalchemy" "pydantic" "celery" "redis" "boto3")
    for pkg in "${REQUIRED_PACKAGES[@]}"; do
        if grep -q "$pkg" backend/requirements.txt; then
            pass "  - $pkg in requirements"
        else
            fail "  - $pkg missing from requirements"
        fi
    done
else
    fail "requirements.txt not found"
fi

echo ""
echo "====== PHASE 4: CONFIGURATION VALIDATION ======"

# Check .env file
if [ -f "backend/.env" ]; then
    pass "backend/.env exists"
    # Check for required keys
    if grep -q "SECRET_KEY" backend/.env; then
        pass "  - SECRET_KEY configured"
    else
        fail "  - SECRET_KEY not configured"
    fi
    if grep -q "DATABASE_URL" backend/.env; then
        pass "  - DATABASE_URL configured"
    else
        fail "  - DATABASE_URL not configured"
    fi
else
    info "backend/.env not found (will create from .env.example)"
fi

# Check docker-compose.yml validity
if docker-compose config > /dev/null 2>&1; then
    pass "docker-compose.yml is valid"
else
    fail "docker-compose.yml is invalid"
fi

echo ""
echo "====== PHASE 5: DIRECTORY STRUCTURE ======"

DIRS=(
    "backend/app"
    "backend/app/auth"
    "backend/app/projects"
    "backend/app/assets"
    "backend/app/jobs"
    "backend/ai_engine"
    "backend/workers"
    "frontend/src"
    "frontend/src/components"
    "frontend/src/services"
    "nginx"
)

for dir in "${DIRS[@]}"; do
    if [ -d "$dir" ]; then
        pass "Directory exists: $dir"
    else
        fail "Directory missing: $dir"
    fi
done

echo ""
echo "====== PHASE 6: CRITICAL FILES CHECK ======"

CRITICAL_FILES=(
    "docker-compose.yml"
    "backend/Dockerfile"
    "frontend/Dockerfile"
    "backend/requirements.txt"
    "frontend/package.json"
    "backend/app/main.py"
    "backend/app/models.py"
    "backend/app/database.py"
    "frontend/src/App.js"
    "README.md"
    "TESTING.md"
)

for file in "${CRITICAL_FILES[@]}"; do
    if [ -f "$file" ]; then
        pass "File exists: $file"
    else
        fail "Critical file missing: $file"
    fi
done

echo ""
echo "====== PHASE 7: CODE METRICS ======"

# Count Python files
PY_FILES=$(find backend -name "*.py" | wc -l)
info "Python files in backend: $PY_FILES"

# Count JavaScript files
JS_FILES=$(find frontend/src -name "*.js" -o -name "*.jsx" | wc -l)
info "JavaScript/JSX files in frontend: $JS_FILES"

# Count lines of code
PY_LINES=$(find backend -name "*.py" -exec wc -l {} + | tail -1 | awk '{print $1}')
info "Total Python lines: $PY_LINES"

# Count API endpoints
ENDPOINTS=$(grep -r "@router" backend/app --include="*.py" | wc -l)
info "API endpoints: $ENDPOINTS"

echo ""
echo "====== PHASE 8: DEPENDENCY CHECK ======"

# Check if key Python packages are installable
python3 -c "import fastapi" 2>/dev/null && pass "FastAPI available" || info "FastAPI not installed (will be in container)"
python3 -c "import sqlalchemy" 2>/dev/null && pass "SQLAlchemy available" || info "SQLAlchemy not installed (will be in container)"
python3 -c "import pydantic" 2>/dev/null && pass "Pydantic available" || info "Pydantic not installed (will be in container)"

echo ""
echo "====== TEST SUMMARY ======"
echo ""
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo -e "${YELLOW}Skipped: $SKIPPED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ ALL TESTS PASSED!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Start Docker Desktop (if on Windows/Mac)"
    echo "  2. Run: docker-compose up -d"
    echo "  3. Run: docker-compose exec backend python -c \"from app.database import init_db; init_db()\""
    echo "  4. Visit: http://localhost:3000"
    echo ""
    exit 0
else
    echo -e "${RED}✗ SOME TESTS FAILED${NC}"
    echo "Please check the output above and fix issues before deploying."
    exit 1
fi
