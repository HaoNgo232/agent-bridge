#!/bin/bash
# Quick setup and lint check script for agent-bridge

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}🚀 Agent Bridge - Quick Setup & Lint Check${NC}\n"

# Step 1: Check Python
echo -e "${YELLOW}📋 Step 1: Checking environment...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found. Please install Python 3.9+${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✓ Python ${PYTHON_VERSION} found${NC}"

# Step 2: Check/Create venv
echo -e "\n${YELLOW}📦 Step 2: Setting up virtual environment...${NC}"
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment exists${NC}"
fi

# Step 3: Activate venv and install dependencies
echo -e "\n${YELLOW}📥 Step 3: Installing dependencies...${NC}"
source .venv/bin/activate

# Check if ruff is installed
if ! python -c "import ruff" 2>/dev/null; then
    echo "Installing dev dependencies..."
    pip install -q -e ".[dev]"
    echo -e "${GREEN}✓ Dependencies installed${NC}"
else
    echo -e "${GREEN}✓ Dependencies already installed${NC}"
fi

# Step 4: Run lint check
echo -e "\n${YELLOW}🔍 Step 4: Running lint check...${NC}"
if ruff check src/; then
    echo -e "\n${GREEN}✅ All lint checks passed!${NC}"
else
    echo -e "\n${RED}❌ Lint check failed!${NC}"
    echo -e "${CYAN}💡 Tip: Run 'make format' to auto-fix issues${NC}"
    exit 1
fi

# Step 5: Check formatting
echo -e "\n${YELLOW}✨ Step 5: Checking code formatting...${NC}"
if ruff format --check src/; then
    echo -e "${GREEN}✓ Code is properly formatted${NC}"
else
    echo -e "${YELLOW}⚠️  Code needs formatting${NC}"
    echo -e "${CYAN}💡 Tip: Run 'make format' to auto-format${NC}"
fi

# Summary
echo -e "\n${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🎉 Setup complete! You're ready to develop.${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "\n${YELLOW}Quick commands:${NC}"
echo -e "  ${CYAN}make lint${NC}      - Run lint check"
echo -e "  ${CYAN}make format${NC}    - Auto-fix and format code"
echo -e "  ${CYAN}make check${NC}     - Run all checks"
echo -e "  ${CYAN}make clean${NC}     - Remove cache files"
echo ""
