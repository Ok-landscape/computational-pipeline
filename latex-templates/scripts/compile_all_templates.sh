#!/bin/bash

# Comprehensive LaTeX Template Compilation Script
# Compiles all 201 PythonTeX templates in the repository

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
TEMPLATES_DIR="$REPO_ROOT/templates"
OUTPUT_DIR="$REPO_ROOT/output"
LOG_DIR="$REPO_ROOT/logs"

# Create necessary directories
mkdir -p "$OUTPUT_DIR"
mkdir -p "$LOG_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
TOTAL=0
SUCCESS=0
FAILED=0

# Array to track failures
declare -a FAILED_FILES

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}LaTeX Template Compilation${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""

# Function to compile a single template
compile_template() {
    local tex_file="$1"
    local relative_path="${tex_file#$TEMPLATES_DIR/}"
    local category=$(dirname "$relative_path")
    local basename=$(basename "$tex_file" .tex)
    local dir=$(dirname "$tex_file")

    ((TOTAL++))

    echo -ne "${YELLOW}[$TOTAL]${NC} Compiling: $relative_path ... "

    # Change to template directory
    cd "$dir"

    # Clean previous artifacts
    rm -f "$basename.aux" "$basename.log" "$basename.out" "$basename.toc" \
          "$basename.pytxcode" "$basename.pdf" 2>/dev/null || true
    rm -rf "pythontex-files-$basename" 2>/dev/null || true

    # Log file for this compilation
    local log_file="$LOG_DIR/${category//\//_}_${basename}.log"

    # Three-pass compilation for PythonTeX
    if pdflatex -interaction=nonstopmode "$basename.tex" > "$log_file" 2>&1; then
        if pythontex "$basename.tex" >> "$log_file" 2>&1; then
            if pdflatex -interaction=nonstopmode "$basename.tex" >> "$log_file" 2>&1; then
                # Check if PDF was created
                if [ -f "$basename.pdf" ]; then
                    # Move PDF to output directory
                    cp "$basename.pdf" "$OUTPUT_DIR/${category//\//_}_${basename}.pdf"
                    echo -e "${GREEN}SUCCESS${NC}"
                    ((SUCCESS++))
                    return 0
                else
                    echo -e "${RED}FAILED (no PDF)${NC}"
                    FAILED_FILES+=("$relative_path (no PDF generated)")
                    ((FAILED++))
                    return 1
                fi
            else
                echo -e "${RED}FAILED (3rd pass)${NC}"
                FAILED_FILES+=("$relative_path (3rd pdflatex pass failed)")
                ((FAILED++))
                return 1
            fi
        else
            echo -e "${RED}FAILED (pythontex)${NC}"
            FAILED_FILES+=("$relative_path (pythontex failed)")
            ((FAILED++))
            return 1
        fi
    else
        echo -e "${RED}FAILED (1st pass)${NC}"
        FAILED_FILES+=("$relative_path (1st pdflatex pass failed)")
        ((FAILED++))
        return 1
    fi
}

# Find all .tex files and compile them
echo "Scanning for templates..."
echo ""

while IFS= read -r -d '' tex_file; do
    compile_template "$tex_file"
done < <(find "$TEMPLATES_DIR" -name "*.tex" -type f -print0 | sort -z)

# Print summary
echo ""
echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}Compilation Summary${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""
echo -e "Total templates:    ${YELLOW}$TOTAL${NC}"
echo -e "Successful:         ${GREEN}$SUCCESS${NC}"
echo -e "Failed:             ${RED}$FAILED${NC}"
echo ""

if [ $FAILED -gt 0 ]; then
    echo -e "${RED}Failed templates:${NC}"
    for failed_file in "${FAILED_FILES[@]}"; do
        echo -e "  - $failed_file"
    done
    echo ""
    echo -e "${YELLOW}Check logs in: $LOG_DIR${NC}"
    exit 1
else
    echo -e "${GREEN}All templates compiled successfully!${NC}"
    echo ""
    echo -e "${GREEN}PDFs saved to: $OUTPUT_DIR${NC}"
    exit 0
fi
