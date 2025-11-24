#!/bin/bash
# auto_publish.sh - Automated Git Publishing Script
# Watches for changes in latex-templates/ and automatically commits and pushes to GitHub

set -euo pipefail

# Configuration
REPO_DIR="/home/user/computational-pipeline"
WATCH_DIR="${REPO_DIR}/latex-templates"
BRANCH="main"
REMOTE="origin"
CHECK_INTERVAL=60  # seconds between checks

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Check if we're in the right directory
cd "${REPO_DIR}" || {
    log_error "Failed to change to repository directory: ${REPO_DIR}"
    exit 1
}

# Verify git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    log_error "Not a git repository: ${REPO_DIR}"
    exit 1
fi

log_info "Starting auto-publish service for ${WATCH_DIR}"
log_info "Check interval: ${CHECK_INTERVAL} seconds"
log_info "Branch: ${BRANCH}"
log_info "Remote: ${REMOTE}"

# Function to check for changes and publish
check_and_publish() {
    cd "${REPO_DIR}" || return 1

    # Check for uncommitted changes
    if [[ -z $(git status --porcelain) ]]; then
        return 0  # No changes, nothing to do
    fi

    log_info "Changes detected in repository"

    # Show status
    git status --short

    # Analyze what changed
    local new_files=$(git ls-files --others --exclude-standard latex-templates/templates/*.tex 2>/dev/null | wc -l)
    local modified_files=$(git diff --name-only latex-templates/ | wc -l)
    local new_pdfs=$(git ls-files --others --exclude-standard latex-templates/output/*.pdf 2>/dev/null | wc -l)

    # Create intelligent commit message
    local commit_msg="Auto-update: "
    local details=""

    if [[ $new_files -gt 0 ]]; then
        commit_msg+="added ${new_files} new template(s)"
        details+="New templates added\n"
    fi

    if [[ $modified_files -gt 0 ]]; then
        if [[ $new_files -gt 0 ]]; then
            commit_msg+=", "
        fi
        commit_msg+="modified ${modified_files} file(s)"
        details+="Files modified\n"
    fi

    if [[ $new_pdfs -gt 0 ]]; then
        if [[ $new_files -gt 0 ]] || [[ $modified_files -gt 0 ]]; then
            commit_msg+=", "
        fi
        commit_msg+="compiled ${new_pdfs} new PDF(s)"
        details+="PDFs compiled\n"
    fi

    # Add all changes in latex-templates and notebooks
    log_info "Staging changes..."
    git add latex-templates/ notebooks/published/ .gitignore 2>/dev/null || true

    # Check if there's anything to commit after staging
    if git diff --cached --quiet; then
        log_warning "No changes to commit after staging"
        return 0
    fi

    # Commit with detailed message
    log_info "Creating commit: ${commit_msg}"
    git commit -m "$(cat <<EOF
${commit_msg}

${details}
🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)" || {
        log_error "Failed to create commit"
        return 1
    }

    log_success "Commit created successfully"

    # Push to remote
    log_info "Pushing to ${REMOTE}/${BRANCH}..."
    if git push ${REMOTE} ${BRANCH}; then
        log_success "Successfully pushed to GitHub"
        return 0
    else
        log_error "Failed to push to GitHub"
        log_warning "You may need to run: git pull --rebase ${REMOTE} ${BRANCH}"
        return 1
    fi
}

# Main monitoring loop
main() {
    log_info "Monitoring started. Press Ctrl+C to stop."

    while true; do
        if check_and_publish; then
            log_info "Check complete. Waiting ${CHECK_INTERVAL} seconds..."
        else
            log_warning "Check failed. Waiting ${CHECK_INTERVAL} seconds before retry..."
        fi

        sleep "${CHECK_INTERVAL}"
    done
}

# Handle Ctrl+C gracefully
trap 'log_info "Received interrupt signal. Shutting down..."; exit 0' INT TERM

# Run with argument handling
case "${1:-monitor}" in
    monitor)
        main
        ;;
    once)
        log_info "Running single check..."
        if check_and_publish; then
            log_success "Single check completed successfully"
            exit 0
        else
            log_error "Single check failed"
            exit 1
        fi
        ;;
    status)
        cd "${REPO_DIR}"
        log_info "Repository status:"
        git status
        ;;
    *)
        echo "Usage: $0 {monitor|once|status}"
        echo ""
        echo "  monitor  - Continuously monitor for changes (default)"
        echo "  once     - Run a single check and publish if needed"
        echo "  status   - Show current git status"
        exit 1
        ;;
esac
