# Makefile for LaTeX Template Pipeline
# Usage: make <target>

.PHONY: all pythontex sagetex knitr clean help verify

# Default target
all: help

# Help target
help:
	@echo "LaTeX Template Pipeline - Available targets:"
	@echo ""
	@echo "  make pythontex  - Build the PythonTeX engineering report"
	@echo "  make sagetex    - Build the SageTeX math thesis"
	@echo "  make knitr      - Build the Knitr clinical report"
	@echo "  make all-docs   - Build all templates"
	@echo "  make verify     - Verify all generated PDFs"
	@echo "  make clean      - Remove all generated files"
	@echo ""
	@echo "Output PDFs will be placed in the output/ directory."

# Build all documents
all-docs: pythontex sagetex knitr
	@echo ""
	@echo "=== All documents built successfully ==="

# PythonTeX template
pythontex:
	@echo "Building PythonTeX template..."
	cd templates/pythontex && \
	pdflatex -interaction=nonstopmode engineering_report.tex && \
	pythontex engineering_report.tex && \
	pdflatex -interaction=nonstopmode engineering_report.tex
	cp templates/pythontex/engineering_report.pdf output/
	@echo "Output: output/engineering_report.pdf"

# SageTeX template
sagetex:
	@echo "Building SageTeX template..."
	cd templates/sagetex && \
	pdflatex -interaction=nonstopmode math_thesis.tex && \
	sage math_thesis.sagetex.sage && \
	pdflatex -interaction=nonstopmode math_thesis.tex
	cp templates/sagetex/math_thesis.pdf output/
	@echo "Output: output/math_thesis.pdf"

# Knitr template
knitr:
	@echo "Building Knitr template..."
	cd templates/knitr && \
	Rscript -e "library(knitr); knit('clinical_report.Rnw')" && \
	pdflatex -interaction=nonstopmode clinical_report.tex
	cp templates/knitr/clinical_report.pdf output/
	@echo "Output: output/clinical_report.pdf"

# Verify all PDFs
verify:
	@echo "Verifying generated PDFs..."
	@for pdf in output/*.pdf; do \
		if [ -f "$$pdf" ]; then \
			./scripts/verify_pdf.sh "$$pdf"; \
			echo ""; \
		fi \
	done

# Clean generated files
clean:
	@echo "Cleaning generated files..."
	# PythonTeX cleanup
	cd templates/pythontex && rm -rf *.pdf *.aux *.log *.pytxcode *.pytxmcr \
		pythontex-files-* step_response.pdf 2>/dev/null || true
	# SageTeX cleanup
	cd templates/sagetex && rm -rf *.pdf *.aux *.log *.sagetex.sage *.sout \
		*.sagetex.scmd sage-plots-for-* 2>/dev/null || true
	# Knitr cleanup
	cd templates/knitr && rm -rf *.pdf *.aux *.log *.tex figure/ 2>/dev/null || true
	# Output cleanup
	rm -f output/*.pdf 2>/dev/null || true
	@echo "Clean complete."
