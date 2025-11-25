#!/bin/bash
# Sync changes to BOTH public and private repositories
# Usage: ./sync_both.sh "commit message for public" "commit message for private"

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check arguments
if [ -z "$1" ]; then
    echo -e "${RED}Error: Commit messages required${NC}"
    echo "Usage: ./sync_both.sh \"Public commit message\" \"Private commit message\""
    echo ""
    echo "Example:"
    echo "  ./sync_both.sh \"Add new feature X\" \"Update outputs from feature X\""
    exit 1
fi

PUBLIC_MSG="$1"
PRIVATE_MSG="${2:-$1}"  # Use same message for both if only one provided

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║           DUAL REPOSITORY SYNC UTILITY                     ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Sync to public repo
echo -e "${YELLOW}[1/2] Syncing to PUBLIC repository...${NC}"
echo "Commit message: $PUBLIC_MSG"
echo ""

bash /home/user/computational-pipeline/social-media-automation/sync_to_public.sh "$PUBLIC_MSG"

echo ""
echo -e "${GREEN}✓ Public sync complete${NC}"
echo ""

# Separator
echo -e "${BLUE}────────────────────────────────────────────────────────────${NC}"
echo ""

# Sync to private repo
echo -e "${YELLOW}[2/2] Syncing to PRIVATE repository...${NC}"
echo "Commit message: $PRIVATE_MSG"
echo ""

bash /home/user/computational-pipeline/social-media-automation/sync_to_private.sh "$PRIVATE_MSG"

echo ""
echo -e "${GREEN}✓ Private sync complete${NC}"
echo ""

# Final summary
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║               SYNC OPERATION COMPLETE                      ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}Both repositories have been updated successfully!${NC}"
echo ""
echo "Public repo:  https://github.com/Ok-landscape/computational-pipeline"
echo "Private repo: https://github.com/Ok-landscape/computational-pipeline-outputs"
