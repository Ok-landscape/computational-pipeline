#!/bin/bash

# Parallel LaTeX Template Compilation Script
# Compiles all 200 PythonTeX templates using GNU parallel

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
TEMPLATES_DIR="$REPO_ROOT/templates"
OUTPUT_DIR="$REPO_ROOT/output"
LOG_DIR="$REPO_ROOT/logs"

# Create directories
mkdir -p "$OUTPUT_DIR" "$LOG_DIR"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}Parallel LaTeX Template Compilation${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""

# Function to compile a single template
compile_one() {
    local tex_file="$1"
    local relative_path="${tex_file#$TEMPLATES_DIR/}"
    local category=$(dirname "$relative_path")
    local basename=$(basename "$tex_file" .tex)
    local dir=$(dirname "$tex_file")

    cd "$dir"

    # Clean
    rm -f "$basename.aux" "$basename.log" "$basename.out" "$basename.toc" \
          "$basename.pytxcode" "$basename.pdf" 2>/dev/null
    rm -rf "pythontex-files-$basename" 2>/dev/null

    local log_file="$LOG_DIR/${category//\//_}_${basename}.log"

    # Compile with timeout
    if timeout 120 bash -c "pdflatex -interaction=nonstopmode '$basename.tex' > '$log_file' 2>&1 && \
                            pythontex '$basename.tex' >> '$log_file' 2>&1 && \
                            pdflatex -interaction=nonstopmode '$basename.tex' >> '$log_file' 2>&1"; then
        if [ -f "$basename.pdf" ]; then
            cp "$basename.pdf" "$OUTPUT_DIR/${category//\//_}_${basename}.pdf"
            echo "$relative_path:SUCCESS"
            return 0
        fi
    fi

    echo "$relative_path:FAILED"
    return 1
}

export -f compile_one
export TEMPLATES_DIR OUTPUT_DIR LOG_DIR

# Find all templates and compile in parallel (8 jobs at a time)
find "$TEMPLATES_DIR" -name "*.tex" -type f | sort | \
    parallel -j 8 --progress compile_one {} | \
    tee /tmp/compile_results.txt

# Count results
TOTAL=$(cat /tmp/compile_results.txt | wc -l)
SUCCESS=$(grep -c ":SUCCESS$" /tmp/compile_results.txt)
FAILED=$(grep -c ":FAILED$" /tmp/compile_results.txt)

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
    grep ":FAILED$" /tmp/compile_results.txt | sed 's/:FAILED$//' | while read file; do
        echo -e "  - $file"
    done
    echo ""
fi

echo -e "${GREEN}PDFs saved to: $OUTPUT_DIR${NC}"
echo -e "${YELLOW}Logs saved to: $LOG_DIR${NC}"
