#!/bin/bash
# ============================================================================
# File: setup_github.sh
# Purpose: Configure GitHub repository for latex-templates
# Usage: ./scripts/setup_github.sh <github-username>
# ============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BASE_DIR="/home/user/latex-templates"
REPO_NAME="latex-templates"

# Parse arguments
if [ $# -eq 0 ]; then
    echo -e "${RED}Error: GitHub username required${NC}"
    echo "Usage: $0 <github-username>"
    exit 1
fi

GITHUB_USERNAME="$1"
REPO_URL="https://github.com/${GITHUB_USERNAME}/${REPO_NAME}.git"

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}GitHub Repository Setup${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

# Step 1: Verify we're in the right directory
cd "$BASE_DIR"
echo -e "${GREEN}[1/7] Verifying directory structure...${NC}"

if [ ! -d "templates" ] || [ ! -d "output" ]; then
    echo -e "${RED}Error: Invalid directory structure${NC}"
    echo "Expected: templates/ and output/ directories"
    exit 1
fi

echo "  ✓ Directory structure verified"
echo ""

# Step 2: Check git initialization
echo -e "${GREEN}[2/7] Checking git initialization...${NC}"

if [ ! -d ".git" ]; then
    echo -e "${RED}Error: Git not initialized${NC}"
    echo "Run: git init"
    exit 1
fi

echo "  ✓ Git initialized"
echo ""

# Step 3: Configure git remote
echo -e "${GREEN}[3/7] Configuring remote repository...${NC}"

# Check if remote already exists
if git remote | grep -q "origin"; then
    echo "  Remote 'origin' already exists:"
    CURRENT_URL=$(git remote get-url origin)
    echo "    Current: $CURRENT_URL"
    echo "    New: $REPO_URL"

    read -p "  Replace remote URL? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git remote set-url origin "$REPO_URL"
        echo "  ✓ Remote URL updated"
    else
        echo "  Keeping existing remote"
    fi
else
    git remote add origin "$REPO_URL"
    echo "  ✓ Remote added: $REPO_URL"
fi

echo ""

# Step 4: Update publisher script with correct URL
echo -e "${GREEN}[4/7] Updating publisher script...${NC}"

if [ -f "scripts/latex_publisher.py" ]; then
    sed -i "s|REPO_URL = \"https://github.com/YOUR_USERNAME/latex-templates.git\"|REPO_URL = \"${REPO_URL}\"|" scripts/latex_publisher.py
    echo "  ✓ Publisher script updated"
else
    echo -e "${YELLOW}  Warning: Publisher script not found${NC}"
fi

echo ""

# Step 5: Check authentication
echo -e "${GREEN}[5/7] Checking GitHub authentication...${NC}"

# Try SSH first
if ssh -T git@github.com 2>&1 | grep -q "successfully authenticated"; then
    echo "  ✓ SSH authentication configured"
    # Convert URL to SSH
    SSH_URL="git@github.com:${GITHUB_USERNAME}/${REPO_NAME}.git"
    git remote set-url origin "$SSH_URL"
    echo "  ✓ Using SSH: $SSH_URL"
elif git ls-remote "$REPO_URL" &> /dev/null; then
    echo "  ✓ HTTPS authentication working"
else
    echo -e "${YELLOW}  ⚠ Authentication not configured${NC}"
    echo ""
    echo -e "${YELLOW}You need to configure authentication to push to GitHub.${NC}"
    echo ""
    echo -e "${BLUE}Option 1: SSH Keys (Recommended)${NC}"
    echo "  1. Generate key: ssh-keygen -t ed25519 -C 'your_email@example.com'"
    echo "  2. Copy key: cat ~/.ssh/id_ed25519.pub"
    echo "  3. Add to GitHub: https://github.com/settings/keys"
    echo "  4. Run this script again"
    echo ""
    echo -e "${BLUE}Option 2: Personal Access Token${NC}"
    echo "  1. Generate at: https://github.com/settings/tokens"
    echo "  2. Use as password when pushing"
    echo ""
fi

echo ""

# Step 6: Create initial commit
echo -e "${GREEN}[6/7] Creating initial commit...${NC}"

# Check if there are any commits
if git rev-parse HEAD &> /dev/null; then
    echo "  Repository already has commits"
    COMMIT_COUNT=$(git rev-list --count HEAD)
    echo "  Total commits: $COMMIT_COUNT"
else
    echo "  Creating initial commit..."

    # Add .gitignore first
    git add .gitignore
    git commit -m "Initial commit: Add .gitignore" || echo "  .gitignore already committed"

    # Add documentation
    git add README.md CLAUDE.md Makefile
    git commit -m "Add documentation and build configuration" || echo "  Docs already committed"

    # Add scripts
    git add scripts/
    git commit -m "Add build and publishing scripts" || echo "  Scripts already committed"

    echo "  ✓ Initial commits created"
fi

echo ""

# Step 7: Instructions for next steps
echo -e "${GREEN}[7/7] Setup complete!${NC}"
echo ""
echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}Next Steps${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

echo -e "${YELLOW}1. Create GitHub repository:${NC}"
echo "   Visit: https://github.com/new"
echo "   Repository name: ${REPO_NAME}"
echo "   Make it public or private"
echo "   Do NOT initialize with README"
echo ""

echo -e "${YELLOW}2. Add templates and PDFs to git:${NC}"
echo "   cd $BASE_DIR"
echo "   git add templates/"
echo "   git add output/"
echo "   git status  # Review what will be committed"
echo ""

echo -e "${YELLOW}3. Commit and push:${NC}"
echo "   git commit -m 'Add LaTeX templates and compiled PDFs'"
echo "   git push -u origin main"
echo ""

echo -e "${YELLOW}4. Use publishing scripts:${NC}"
echo "   # Publish new/modified files:"
echo "   python3 scripts/latex_publisher.py new"
echo ""
echo "   # Publish all templates:"
echo "   ./scripts/publish_all.sh"
echo ""
echo "   # Publish specific category:"
echo "   python3 scripts/latex_publisher.py batch --pattern 'aerospace/*.tex'"
echo ""

echo -e "${GREEN}Repository URL: ${REPO_URL}${NC}"
echo ""
