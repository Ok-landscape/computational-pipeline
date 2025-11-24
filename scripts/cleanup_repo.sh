#!/bin/bash
# cleanup_repo.sh - Repository Cleanup Script
# Removes build artifacts and unnecessary files from the repository

set -euo pipefail

REPO_DIR="/home/user/computational-pipeline"
LATEX_DIR="${REPO_DIR}/latex-templates"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

cd "${REPO_DIR}" || {
    log_error "Failed to change to repository directory"
    exit 1
}

log_info "Starting repository cleanup..."

# Function to safely remove files
safe_remove() {
    local pattern=$1
    local description=$2
    local count=0

    if [[ -n $(find "${LATEX_DIR}" -name "${pattern}" 2>/dev/null) ]]; then
        count=$(find "${LATEX_DIR}" -name "${pattern}" 2>/dev/null | wc -l)
        log_info "Removing ${count} ${description}..."
        find "${LATEX_DIR}" -name "${pattern}" -type f -delete 2>/dev/null || true
        log_success "Removed ${count} ${description}"
    fi
}

# Remove LaTeX auxiliary files
log_info "Cleaning LaTeX build artifacts..."
safe_remove "*.aux" "auxiliary files"
safe_remove "*.log" "log files"
safe_remove "*.out" "output files"
safe_remove "*.toc" "table of contents files"
safe_remove "*.bbl" "bibliography files"
safe_remove "*.blg" "bibliography log files"
safe_remove "*.bcf" "biblatex control files"
safe_remove "*.run.xml" "biblatex run files"
safe_remove "*.fls" "file list files"
safe_remove "*.fdb_latexmk" "latexmk database files"
safe_remove "*.synctex.gz" "synctex files"
safe_remove "*.nav" "navigation files"
safe_remove "*.snm" "navigation slide files"
safe_remove "*.vrb" "verbatim files"

# Remove PythonTeX files
log_info "Cleaning PythonTeX artifacts..."
safe_remove "*.pytxcode" "PythonTeX code files"
safe_remove "*.pytxmcr" "PythonTeX macro files"
safe_remove "*.pytxpyg" "PythonTeX Pygments files"

# Remove PythonTeX directories
if [[ -n $(find "${LATEX_DIR}" -type d -name "pythontex-files-*" 2>/dev/null) ]]; then
    local pytex_dirs=$(find "${LATEX_DIR}" -type d -name "pythontex-files-*" 2>/dev/null | wc -l)
    log_info "Removing ${pytex_dirs} PythonTeX directories..."
    find "${LATEX_DIR}" -type d -name "pythontex-files-*" -exec rm -rf {} + 2>/dev/null || true
    log_success "Removed ${pytex_dirs} PythonTeX directories"
fi

# Remove SageTeX files
log_info "Cleaning SageTeX artifacts..."
safe_remove "*.sagetex.sage" "SageTeX sage files"
safe_remove "*.sagetex.py" "SageTeX Python files"
safe_remove "*.sagetex.scmd" "SageTeX command files"
safe_remove "*.sout" "SageTeX output files"

# Remove Knitr files
log_info "Cleaning Knitr artifacts..."
safe_remove "*.Rout" "R output files"
safe_remove ".Rhistory" "R history files"
safe_remove ".RData" "R data files"
safe_remove "*-concordance.tex" "Knitr concordance files"

# Remove Knitr figure directories
if [[ -n $(find "${LATEX_DIR}" -type d -name "figure" 2>/dev/null) ]]; then
    local fig_dirs=$(find "${LATEX_DIR}" -type d -name "figure" 2>/dev/null | wc -l)
    log_info "Removing ${fig_dirs} Knitr figure directories..."
    find "${LATEX_DIR}" -type d -name "figure" -exec rm -rf {} + 2>/dev/null || true
    log_success "Removed ${fig_dirs} Knitr figure directories"
fi

# Remove temporary files
log_info "Cleaning temporary files..."
safe_remove "*~" "backup files"
safe_remove "*.swp" "vim swap files"
safe_remove "*.swo" "vim swap files"
safe_remove "*.tmp" "temporary files"
safe_remove "*.bak" "backup files"

# Clean Python cache
if [[ -n $(find "${LATEX_DIR}" -type d -name "__pycache__" 2>/dev/null) ]]; then
    local pycache_dirs=$(find "${LATEX_DIR}" -type d -name "__pycache__" 2>/dev/null | wc -l)
    log_info "Removing ${pycache_dirs} Python cache directories..."
    find "${LATEX_DIR}" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    log_success "Removed ${pycache_dirs} Python cache directories"
fi

safe_remove "*.pyc" "Python compiled files"
safe_remove "*.pyo" "Python optimized files"

# Clean logs directory but keep the directory
if [[ -d "${LATEX_DIR}/logs" ]]; then
    log_info "Cleaning logs directory..."
    rm -f "${LATEX_DIR}/logs"/*.log "${LATEX_DIR}/logs"/*.txt 2>/dev/null || true
    log_success "Cleaned logs directory"
fi

# Check git status for accidentally tracked artifacts
log_info "Checking for tracked build artifacts in git..."
cd "${REPO_DIR}"
tracked_artifacts=$(git ls-files | grep -E "\.(aux|log|pytxcode|out|toc|fls|synctex\.gz)$" 2>/dev/null || true)

if [[ -n "${tracked_artifacts}" ]]; then
    log_warning "Found tracked build artifacts:"
    echo "${tracked_artifacts}"
    log_info "Run 'git rm --cached <file>' to untrack these files"
else
    log_success "No tracked build artifacts found in git"
fi

# Summary
log_success "Repository cleanup completed!"
log_info "Summary:"
log_info "  - Removed LaTeX auxiliary files"
log_info "  - Removed PythonTeX artifacts"
log_info "  - Removed SageTeX artifacts"
log_info "  - Removed Knitr artifacts"
log_info "  - Removed temporary files"
log_info "  - Cleaned Python cache"

# Show disk space saved
log_info "Checking disk space..."
du -sh "${LATEX_DIR}"
