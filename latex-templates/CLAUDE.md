# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build Commands

### CoCalc Quick Build (Recommended)

In CoCalc, simply open the file and press **Shift+Enter**. CoCalc handles multi-pass compilation automatically.

### Terminal Commands (for debugging/verification)

```bash
# Build individual templates
make pythontex          # PythonTeX engineering report
make sagetex            # SageTeX math thesis
make knitr              # Knitr clinical report

# Build all templates
make all-docs

# Verify generated PDFs
make verify

# Clean generated files
make clean
```

## Architecture

This is a computational typesetting project implementing three reproducible document pipelines:

### Template Build Chains

| Template | Build Process | Output |
|----------|---------------|--------|
| PythonTeX | `pdflatex -> pythontex -> pdflatex` | output/engineering_report.pdf |
| SageTeX | `pdflatex -> sage -> pdflatex` | output/math_thesis.pdf |
| Knitr | `Rscript (knit) -> pdflatex` | output/clinical_report.pdf |

### Directory Structure

- `templates/pythontex/` - Engineering/Physics (NumPy, SciPy, Matplotlib)
- `templates/sagetex/` - Pure Mathematics (SageMath symbolic algebra)
- `templates/knitr/` - Statistics/Biology (R, ggplot2, xtable)
- `scripts/` - Build and verification shell scripts
- `config/latexmkrc` - Custom latexmk rules for SageTeX
- `output/` - Generated PDF files

### Key Template Patterns

**PythonTeX**: Uses `\py{}` for inline Python, `\begin{pycode}` for silent execution, `\begin{pyblock}` for displayed code. Custom `\pySI{value}{unit}` command for siunitx integration.

**SageTeX**: Uses `\sage{}` for inline results, `\begin{sageblock}` for displayed code, `\begin{sagesilent}` for silent execution, `\sageplot{}` for automatic figure handling.

**Knitr**: Uses `\Sexpr{}` for inline R, `<<chunk_name, options>>=` for code chunks. Key options: `echo`, `results='asis'`, `fig.cap`.

## Dependencies

- LaTeX: pdflatex, latexmk, pythontex
- Python 3: numpy, scipy, matplotlib
- R: knitr, ggplot2, xtable
- SageMath: sage
- PDF tools: pdfinfo, pdftotext (poppler-utils)

## Troubleshooting

**"Undefined control sequence" errors**: Usually caused by stale auxiliary files when Python/Sage/R code fails. Fix the code error first, then run `make clean` before rebuilding.

**PythonTeX variables not updating**: Delete `.pytxcode` and `pythontex-files-*` directory in the template folder, then rebuild.

**SageTeX "unknown variable" errors**: Delete `.sagetex.sage` and `.sout` files, then rebuild all three passes.

**Knitr figure not appearing**: Ensure `results='asis'` is set for xtable output; check that `figure/` directory is being created.

## Manual Build Commands

When debugging, run passes individually:

```bash
# PythonTeX
cd templates/pythontex
pdflatex -interaction=nonstopmode engineering_report.tex
pythontex engineering_report.tex
pdflatex -interaction=nonstopmode engineering_report.tex

# SageTeX
cd templates/sagetex
pdflatex -interaction=nonstopmode math_thesis.tex
sage math_thesis.sagetex.sage
pdflatex -interaction=nonstopmode math_thesis.tex

# Knitr
cd templates/knitr
Rscript -e "library(knitr); knit('clinical_report.Rnw')"
pdflatex -interaction=nonstopmode clinical_report.tex
```

## Using latexmk for SageTeX

Copy the config for automated dependency resolution:

```bash
cp config/latexmkrc ~/.latexmkrc
latexmk -pdf templates/sagetex/math_thesis.tex
```
