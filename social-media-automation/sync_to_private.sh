#!/bin/bash
# Sync outputs, executed notebooks, and generated content to private repository
# Usage: ./sync_to_private.sh "commit message"

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Directories
PRIVATE_REPO="/home/user/computational-pipeline/social-media-automation/repo-data"

# Check if commit message provided
if [ -z "$1" ]; then
    echo -e "${RED}Error: Commit message required${NC}"
    echo "Usage: ./sync_to_private.sh \"Your commit message\""
    exit 1
fi

COMMIT_MSG="$1"

echo -e "${YELLOW}=== Private Repository Sync ===${NC}"
echo "Target: https://github.com/Ok-landscape/computational-pipeline-outputs"
echo "Message: $COMMIT_MSG"
echo ""

# Navigate to private repo
cd "$PRIVATE_REPO"

# Check current status
echo -e "${YELLOW}Current status:${NC}"
git status --short

echo ""
echo -e "${YELLOW}Adding changes:${NC}"

# Add executed notebooks with outputs
echo "- Adding notebooks with outputs..."
git add notebooks/published/*.ipynb 2>/dev/null || true

# Add generated plots
echo "- Adding generated plots..."
git add notebooks/published/*.png 2>/dev/null || true

# Add social media posts
echo "- Adding social media posts..."
git add output/social_posts/*.txt 2>/dev/null || true

# Add orchestration state
echo "- Adding orchestration state..."
git add orchestration/ 2>/dev/null || true

# Show what will be committed
echo ""
echo -e "${YELLOW}Staged changes:${NC}"
git status --short

# Check if there are changes to commit
if git diff --staged --quiet; then
    echo -e "${YELLOW}No changes to commit.${NC}"
    exit 0
fi

# Ask for confirmation
echo ""
read -p "Proceed with commit and push? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${RED}Aborted.${NC}"
    exit 1
fi

# Commit
echo ""
echo -e "${GREEN}Committing...${NC}"
git commit -m "$COMMIT_MSG

Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"

# Push
echo ""
echo -e "${GREEN}Pushing to origin/main...${NC}"
git push origin main

echo ""
echo -e "${GREEN}=== Sync Complete ===${NC}"
echo "Private repo updated successfully!"
