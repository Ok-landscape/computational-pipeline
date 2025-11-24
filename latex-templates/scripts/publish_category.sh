#!/bin/bash
# ============================================================================
# File: publish_category.sh
# Purpose: Publish templates from a specific category
# Usage: ./scripts/publish_category.sh <category-name>
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

# Parse arguments
if [ $# -eq 0 ]; then
    echo -e "${RED}Error: Category name required${NC}"
    echo "Usage: $0 <category-name>"
    echo ""
    echo "Available categories:"
    cd "$BASE_DIR/templates"
    ls -d */ | sed 's|/||' | sort | head -20
    echo "... (use 'ls templates/' to see all)"
    exit 1
fi

CATEGORY="$1"
CATEGORY_PATH="$BASE_DIR/templates/$CATEGORY"

cd "$BASE_DIR"

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}Publish Category: ${CATEGORY}${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

# Verify category exists
if [ ! -d "$CATEGORY_PATH" ]; then
    echo -e "${RED}Error: Category not found: $CATEGORY${NC}"
    echo ""
    echo "Available categories:"
    cd "$BASE_DIR/templates"
    ls -d */ | sed 's|/||' | sort
    exit 1
fi

# Count templates in category
TEMPLATE_COUNT=$(find "$CATEGORY_PATH" -name "*.tex" -type f | wc -l)

if [ "$TEMPLATE_COUNT" -eq 0 ]; then
    echo -e "${YELLOW}No templates found in category: $CATEGORY${NC}"
    exit 0
fi

echo -e "${GREEN}Found $TEMPLATE_COUNT template(s) in $CATEGORY${NC}"
echo ""

# List templates
echo "Templates:"
find "$CATEGORY_PATH" -name "*.tex" -type f -exec basename {} \; | sort

echo ""

# Confirm action
read -p "$(echo -e ${YELLOW}Publish these templates? \(y/n\) ${NC})" -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 0
fi

echo ""
echo -e "${GREEN}Publishing ${CATEGORY} templates...${NC}"
echo ""

# Run publisher with category pattern
if python3 "$PUBLISHER" batch --pattern "${CATEGORY}/*.tex"; then
    echo ""
    echo -e "${GREEN}============================================${NC}"
    echo -e "${GREEN}✓ Category published successfully!${NC}"
    echo -e "${GREEN}============================================${NC}"
    echo ""

    # Show remote URL
    REMOTE_URL=$(git remote get-url origin 2>/dev/null || echo "Not configured")
    echo "Repository: $REMOTE_URL"
else
    echo ""
    echo -e "${RED}============================================${NC}"
    echo -e "${RED}✗ Publishing failed${NC}"
    echo -e "${RED}============================================${NC}"
    exit 1
fi
