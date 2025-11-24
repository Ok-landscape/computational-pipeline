#!/bin/bash
# ============================================================================
# File: generate_share_links.sh
# Purpose: Generate CoCalc ShareServer links for all templates and PDFs
# Usage: ./scripts/generate_share_links.sh [project-id]
# ============================================================================

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

BASE_DIR="/home/user/latex-templates"
OUTPUT_FILE="$BASE_DIR/SHARE_LINKS.md"

# Get project ID from argument or prompt
if [ $# -eq 1 ]; then
    PROJECT_ID="$1"
else
    echo -e "${YELLOW}Enter your CoCalc Project ID:${NC}"
    echo "(Find it in your browser URL: https://cocalc.com/projects/PROJECT-ID/...)"
    read -p "Project ID: " PROJECT_ID
fi

if [ -z "$PROJECT_ID" ]; then
    echo "Error: Project ID required"
    exit 1
fi

cd "$BASE_DIR"

echo -e "${BLUE}Generating CoCalc Share Links...${NC}"
echo ""

# Start output file
cat > "$OUTPUT_FILE" << EOF
# LaTeX Template Share Links

**Generated**: $(date '+%Y-%m-%d %H:%M:%S')
**Project ID**: \`$PROJECT_ID\`

This document provides direct links to view and download all LaTeX templates and compiled PDFs via CoCalc ShareServer.

## Quick Access

EOF

# Count totals
TOTAL_TEMPLATES=0
TOTAL_PDFS=0

# Generate links by category
for category_dir in templates/*/; do
    if [ ! -d "$category_dir" ]; then
        continue
    fi

    category_name=$(basename "$category_dir")

    # Check if category has any .tex files
    tex_count=$(find "$category_dir" -name "*.tex" -type f | wc -l)
    if [ "$tex_count" -eq 0 ]; then
        continue
    fi

    # Category header
    cat >> "$OUTPUT_FILE" << EOF

## ${category_name^}

| Template | Source | PDF |
|----------|--------|-----|
EOF

    # Find all .tex files in category
    find "$category_dir" -name "*.tex" -type f | sort | while read tex_file; do
        basename_file=$(basename "$tex_file" .tex)
        rel_tex="${tex_file#./}"

        # Template URL
        template_url="https://cocalc.com/projects/${PROJECT_ID}/files/${rel_tex}"

        # Check for corresponding PDF
        pdf_file="output/${basename_file}.pdf"

        if [ -f "$pdf_file" ]; then
            pdf_url="https://cocalc.com/projects/${PROJECT_ID}/files/${pdf_file}"
            echo "| \`${basename_file}\` | [View Source](${template_url}) | [View PDF](${pdf_url}) |" >> "$OUTPUT_FILE"
            TOTAL_PDFS=$((TOTAL_PDFS + 1))
        else
            echo "| \`${basename_file}\` | [View Source](${template_url}) | — |" >> "$OUTPUT_FILE"
        fi

        TOTAL_TEMPLATES=$((TOTAL_TEMPLATES + 1))
    done

    echo "" >> "$OUTPUT_FILE"
done

# Add footer
cat >> "$OUTPUT_FILE" << EOF

---

## Statistics

- **Total Templates**: $TOTAL_TEMPLATES
- **Compiled PDFs**: $TOTAL_PDFS
- **Categories**: $(find templates -mindepth 1 -maxdepth 1 -type d | wc -l)

## Access Methods

### Method 1: Direct Links (Above)

Click any link above to view files directly in CoCalc.

### Method 2: Project URL

Access the entire project:
\`\`\`
https://cocalc.com/projects/${PROJECT_ID}
\`\`\`

### Method 3: Download via Git

Clone the GitHub repository:
\`\`\`bash
git clone https://github.com/YOUR_USERNAME/latex-templates.git
\`\`\`

## Making Files Public

To make these links accessible without CoCalc login:

1. Open Project Settings in CoCalc
2. Navigate to "Public files" section
3. Enable public access for:
   - \`templates/\` directory
   - \`output/\` directory

Or create individual share links via the Share button in CoCalc's file browser.

## Notes

- Links point to files in your CoCalc project
- Public access must be enabled in project settings
- PDFs are compiled versions of the templates
- Source \`.tex\` files are also available on GitHub

---

**Last Updated**: $(date '+%Y-%m-%d %H:%M:%S')
EOF

echo ""
echo -e "${GREEN}✓ Share links generated: $OUTPUT_FILE${NC}"
echo ""
echo "Summary:"
echo "  Templates: $TOTAL_TEMPLATES"
echo "  PDFs: $TOTAL_PDFS"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Review the generated file: cat SHARE_LINKS.md"
echo "2. Enable public access in CoCalc Project Settings"
echo "3. Commit to git: git add SHARE_LINKS.md && git commit -m 'Add share links'"
echo ""
