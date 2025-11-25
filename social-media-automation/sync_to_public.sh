#!/bin/bash
# Sync social-media-automation code and docs to public repository
# Usage: ./sync_to_public.sh "commit message"

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Directories
PUBLIC_REPO="/home/user/computational-pipeline"
PRIVATE_REPO="/home/user/computational-pipeline/social-media-automation/repo-data"

# Check if commit message provided
if [ -z "$1" ]; then
    echo -e "${RED}Error: Commit message required${NC}"
    echo "Usage: ./sync_to_public.sh \"Your commit message\""
    exit 1
fi

COMMIT_MSG="$1"

echo -e "${YELLOW}=== Public Repository Sync ===${NC}"
echo "Target: https://github.com/Ok-landscape/computational-pipeline"
echo "Message: $COMMIT_MSG"
echo ""

# Navigate to public repo
cd "$PUBLIC_REPO"

# Check current status
echo -e "${YELLOW}Current status:${NC}"
git status --short

echo ""
echo -e "${YELLOW}Files to be committed:${NC}"

# Add Python files (but exclude repo-data, test outputs, etc.)
echo "- Adding Python source files..."
find social-media-automation -name "*.py" -not -path "*/repo-data/*" -not -path "*/__pycache__/*" -exec git add {} \;

# Add documentation
echo "- Adding documentation files..."
find social-media-automation -name "*.md" -not -path "*/repo-data/*" -exec git add {} \;

# Add configuration examples (but not actual .env)
echo "- Adding configuration templates..."
git add social-media-automation/.env.example 2>/dev/null || true
git add social-media-automation/requirements.txt 2>/dev/null || true
git add social-media-automation/setup.sh 2>/dev/null || true

# Show what will be committed
echo ""
echo -e "${YELLOW}Staged changes:${NC}"
git status --short

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
echo "Public repo updated successfully!"
