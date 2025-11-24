#!/bin/bash
# ============================================================================
# File: publish_new.sh
# Purpose: Publish only new or modified templates and PDFs to GitHub
# Usage: ./scripts/publish_new.sh
# ============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

BASE_DIR="/home/user/latex-templates"
PUBLISHER="$BASE_DIR/scripts/latex_publisher.py"

cd "$BASE_DIR"

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}Publish New/Modified Templates${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

# Verify publisher script exists
if [ ! -f "$PUBLISHER" ]; then
    echo -e "${RED}Error: Publisher script not found: $PUBLISHER${NC}"
    exit 1
fi

# Check git status
echo -e "${GREEN}Checking for changes...${NC}"
echo ""

# Show status summary
git status --short | grep -E '\.(tex|pdf)$' || true

MODIFIED_COUNT=$(git status --porcelain | grep -E '\.(tex|pdf)$' | wc -l)

if [ "$MODIFIED_COUNT" -eq 0 ]; then
    echo -e "${GREEN}✓ No modified templates or PDFs${NC}"
    echo "All files are up to date!"
    exit 0
fi

echo ""
echo -e "${YELLOW}Found $MODIFIED_COUNT modified file(s)${NC}"
echo ""

# Confirm action
read -p "$(echo -e ${YELLOW}Publish these changes to GitHub? \(y/n\) ${NC})" -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 0
fi

echo ""
echo -e "${GREEN}Publishing changes...${NC}"
echo ""

# Run publisher for new/modified files
if python3 "$PUBLISHER" new; then
    echo ""
    echo -e "${GREEN}============================================${NC}"
    echo -e "${GREEN}✓ Changes published successfully!${NC}"
    echo -e "${GREEN}============================================${NC}"
    echo ""

    # Show remote URL
    REMOTE_URL=$(git remote get-url origin 2>/dev/null || echo "Not configured")
    echo "Repository: $REMOTE_URL"

    # Show last commit
    echo ""
    echo "Last commit:"
    git log -1 --oneline
else
    echo ""
    echo -e "${RED}============================================${NC}"
    echo -e "${RED}✗ Publishing failed${NC}"
    echo -e "${RED}============================================${NC}"
    echo ""
    echo "Check logs for details:"
    echo "  cat logs/publishing.log"
    exit 1
fi
