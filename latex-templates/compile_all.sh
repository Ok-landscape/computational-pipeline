#!/bin/bash
# Script to compile all PythonTeX templates
# This builds each template with the pdflatex -> pythontex -> pdflatex pipeline

BASE_DIR="/home/user/latex-templates/templates"
OUTPUT_DIR="/home/user/latex-templates/output"

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Counters
total=0
success=0
failed=0
failed_list=""

# Find all .tex files
while IFS= read -r tex_file; do
    total=$((total + 1))

    # Get directory and filename
    dir=$(dirname "$tex_file")
    filename=$(basename "$tex_file" .tex)
    category=$(basename "$dir")

    echo "[$total] Compiling: $category/$filename"

    # Change to the template directory
    cd "$dir"

    # First pdflatex pass
    pdflatex -interaction=nonstopmode "$filename.tex" > /dev/null 2>&1

    # Run pythontex
    pythontex "$filename.tex" > /dev/null 2>&1

    # Second pdflatex pass
    pdflatex -interaction=nonstopmode "$filename.tex" > /dev/null 2>&1

    # Check if PDF was created
    if [ -f "$filename.pdf" ]; then
        # Copy to output directory with organized naming
        cp "$filename.pdf" "$OUTPUT_DIR/${category}_${filename}.pdf"
        success=$((success + 1))
        echo "  -> Success"
    else
        failed=$((failed + 1))
        failed_list="$failed_list\n  - $category/$filename"
        echo "  -> FAILED"
    fi

    # Clean up auxiliary files
    rm -f *.aux *.log *.out *.pytxcode *.synctex.gz 2>/dev/null

done < <(find "$BASE_DIR" -name "*.tex" -type f | sort)

echo ""
echo "=========================================="
echo "Compilation Complete"
echo "=========================================="
echo "Total templates: $total"
echo "Successful: $success"
echo "Failed: $failed"

if [ $failed -gt 0 ]; then
    echo ""
    echo "Failed templates:"
    echo -e "$failed_list"
fi

echo ""
echo "PDFs saved to: $OUTPUT_DIR"
echo "=========================================="
