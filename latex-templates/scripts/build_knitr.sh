#!/bin/bash
# Build script for Knitr documents
# Usage: ./build_knitr.sh <filename.Rnw>

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <filename.Rnw>"
    echo "Example: $0 clinical_report.Rnw"
    exit 1
fi

FILENAME="$1"
BASENAME="${FILENAME%.Rnw}"

echo "=== Building Knitr document: $FILENAME ==="

# Get the directory of the Rnw file
RNWDIR=$(dirname "$FILENAME")
if [ "$RNWDIR" = "." ]; then
    RNWDIR=$(pwd)
fi

cd "$RNWDIR"
RNWFILE=$(basename "$FILENAME")
TEXBASENAME="${RNWFILE%.Rnw}"

echo ""
echo "Pass 1: Knitting R code to LaTeX..."
Rscript -e "library(knitr); knit('$RNWFILE')"

echo ""
echo "Pass 2: Compiling LaTeX..."
pdflatex -interaction=nonstopmode "${TEXBASENAME}.tex"

echo ""
echo "=== Build complete! Output: ${TEXBASENAME}.pdf ==="
