#!/bin/bash

# Sample Compilation Test Script
# Tests a representative sample of templates including the 7 previously failed ones

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
TEMPLATES_DIR="$REPO_ROOT/templates"
OUTPUT_DIR="$REPO_ROOT/output"
LOG_DIR="$REPO_ROOT/logs"

mkdir -p "$OUTPUT_DIR" "$LOG_DIR"

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Testing Sample of Templates${NC}"
echo ""

# Test the 7 previously failed templates
FAILED_TEMPLATES=(
    "data-science/time_series.tex"
    "machine-learning/decision_tree.tex"
    "machine-learning/kmeans.tex"
    "machine-learning/linear_regression.tex"
    "machine-learning/svm.tex"
    "neuroscience/action_potential.tex"
    "signal-processing/fft_analysis.tex"
)

# Add some additional templates from new categories
SAMPLE_TEMPLATES=(
    "acoustics/room_acoustics.tex"
    "astrophysics/neutron_stars.tex"
    "biomedical/ecg_analysis.tex"
    "cryptography/aes.tex"
    "quantum-mechanics/schrodinger.tex"
)

SUCCESS=0
FAILED=0
declare -a FAILED_FILES

compile_template() {
    local rel_path="$1"
    local tex_file="$TEMPLATES_DIR/$rel_path"
    local category=$(dirname "$rel_path")
    local basename=$(basename "$tex_file" .tex)
    local dir="$TEMPLATES_DIR/$category"

    echo -ne "Compiling: ${rel_path} ... "

    if [ ! -f "$tex_file" ]; then
        echo -e "${YELLOW}SKIPPED - not found${NC}"
        return
    fi

    cd "$dir"
    rm -f "$basename".{aux,log,out,toc,pytxcode,pdf} 2>/dev/null
    rm -rf "pythontex-files-$basename" 2>/dev/null

    local log="$LOG_DIR/${category//\//_}_${basename}.log"

    if timeout 120 bash -c "pdflatex -interaction=nonstopmode '$basename.tex' > '$log' 2>&1 && \
                            pythontex '$basename.tex' >> '$log' 2>&1 && \
                            pdflatex -interaction=nonstopmode '$basename.tex' >> '$log' 2>&1"; then
        if [ -f "$basename.pdf" ]; then
            cp "$basename.pdf" "$OUTPUT_DIR/${category//\//_}_${basename}.pdf"
            echo -e "${GREEN}SUCCESS${NC}"
            ((SUCCESS++))
            return 0
        fi
    fi

    echo -e "${RED}FAILED${NC}"
    FAILED_FILES+=("$rel_path")
    ((FAILED++))
    return 1
}

echo -e "${YELLOW}Testing Previously Failed Templates:${NC}"
for template in "${FAILED_TEMPLATES[@]}"; do
    compile_template "$template"
done

echo ""
echo -e "${YELLOW}Testing Sample from New Categories:${NC}"
for template in "${SAMPLE_TEMPLATES[@]}"; do
    compile_template "$template"
done

echo ""
echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}Test Results${NC}"
echo -e "${BLUE}======================================${NC}"
echo -e "Successful:    ${GREEN}$SUCCESS${NC}"
echo -e "Failed:        ${RED}$FAILED${NC}"

if [ $FAILED -gt 0 ]; then
    echo ""
    echo -e "${RED}Failed templates:${NC}"
    for failed in "${FAILED_FILES[@]}"; do
        echo -e "  - $failed"
    done
fi

[ $FAILED -eq 0 ] && exit 0 || exit 1
