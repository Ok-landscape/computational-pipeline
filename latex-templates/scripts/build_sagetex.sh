#!/bin/bash
# Build script for SageTeX documents
# Usage: ./build_sagetex.sh <filename.tex>

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <filename.tex>"
    echo "Example: $0 math_thesis.tex"
    exit 1
fi

FILENAME="$1"
BASENAME="${FILENAME%.tex}"

echo "=== Building SageTeX document: $FILENAME ==="

# Get the directory of the tex file
TEXDIR=$(dirname "$FILENAME")
if [ "$TEXDIR" = "." ]; then
    TEXDIR=$(pwd)
fi

cd "$TEXDIR"
TEXFILE=$(basename "$FILENAME")
SAGEBASENAME="${TEXFILE%.tex}"

echo ""
echo "Pass 1: Initial LaTeX compilation..."
pdflatex -interaction=nonstopmode "$TEXFILE"

echo ""
echo "Pass 2: Executing Sage code..."
sage "${SAGEBASENAME}.sagetex.sage"

echo ""
echo "Pass 3: Final LaTeX compilation..."
pdflatex -interaction=nonstopmode "$TEXFILE"

echo ""
echo "=== Build complete! Output: ${SAGEBASENAME}.pdf ==="
