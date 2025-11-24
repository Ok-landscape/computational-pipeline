#!/bin/bash
# ============================================================================
# File: publish_all.sh
# Purpose: Batch publish all LaTeX templates and PDFs to GitHub
# Usage: ./scripts/publish_all.sh [--dry-run]
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
echo -e "${BLUE}Batch Publish All Templates${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

# Check for dry-run flag
DRY_RUN=""
if [ "$1" == "--dry-run" ]; then
    DRY_RUN="--dry-run"
    echo -e "${YELLOW}DRY RUN MODE: Changes will be committed locally but not pushed${NC}"
    echo ""
fi

# Verify publisher script exists
if [ ! -f "$PUBLISHER" ]; then
    echo -e "${RED}Error: Publisher script not found: $PUBLISHER${NC}"
    exit 1
fi

# Count templates and PDFs
TEMPLATE_COUNT=$(find templates -name "*.tex" -type f | wc -l)
PDF_COUNT=$(find output -name "*.pdf" -type f 2>/dev/null | wc -l || echo "0")

echo -e "${GREEN}Found:${NC}"
echo "  Templates: $TEMPLATE_COUNT .tex files"
echo "  PDFs: $PDF_COUNT compiled files"
echo ""

# Confirm action
if [ -z "$DRY_RUN" ]; then
    read -p "$(echo -e ${YELLOW}Publish all files to GitHub? \(y/n\) ${NC})" -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 0
    fi
fi

echo ""
echo -e "${GREEN}Publishing...${NC}"
echo ""

# Run publisher in batch mode
if python3 "$PUBLISHER" batch $DRY_RUN; then
    echo ""
    echo -e "${GREEN}============================================${NC}"
    echo -e "${GREEN}✓ Batch publish complete!${NC}"
    echo -e "${GREEN}============================================${NC}"

    if [ -n "$DRY_RUN" ]; then
        echo ""
        echo -e "${YELLOW}To push to GitHub, run:${NC}"
        echo "  git push origin main"
    else
        echo ""
        echo -e "${GREEN}All templates and PDFs have been published to GitHub${NC}"

        # Show remote URL
        REMOTE_URL=$(git remote get-url origin 2>/dev/null || echo "Not configured")
        echo "Repository: $REMOTE_URL"
    fi
else
    echo ""
    echo -e "${RED}============================================${NC}"
    echo -e "${RED}✗ Batch publish failed${NC}"
    echo -e "${RED}============================================${NC}"
    echo ""
    echo "Check logs for details:"
    echo "  cat logs/publishing.log"
    exit 1
fi
