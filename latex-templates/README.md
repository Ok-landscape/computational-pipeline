# LaTeX Template Collection

A comprehensive collection of 201 reproducible scientific document templates using computational typesetting across 67 scientific disciplines.

## Repository Access

- **GitHub**: [https://github.com/YOUR_USERNAME/latex-templates](https://github.com/YOUR_USERNAME/latex-templates) (Update after setup)
- **CoCalc ShareServer**: See [SHARE_LINKS.md](SHARE_LINKS.md) for direct access to templates and PDFs
- **Documentation**: [COCALC_SHARESERVER.md](COCALC_SHARESERVER.md) for ShareServer integration details

## Collection Overview

This repository contains **201 LaTeX templates** organized into **67 scientific categories**, including:

- Aerospace, Astronomy, Astrophysics
- Biology, Bioinformatics, Biomedical Engineering
- Chemistry, Chemical Engineering
- Computer Science, Data Science
- Engineering (Electrical, Mechanical, Civil, etc.)
- Mathematics, Statistics
- Physics, Quantum Mechanics
- And 50+ more specialized fields

See [COMPLETE_TEMPLATE_LIST.txt](/home/user/latex-templates/COMPLETE_TEMPLATE_LIST.txt) for the full inventory.

## Directory Structure

```
latex-templates/
├── templates/          # 201 .tex files across 67 categories
│   ├── aerospace/
│   ├── astronomy/
│   ├── bioinformatics/
│   ├── biology/
│   ├── chemistry/
│   ├── computer-science/
│   ├── data-science/
│   ├── engineering/
│   ├── mathematics/
│   ├── physics/
│   └── ... (57 more categories)
├── output/            # ~103 compiled PDFs (more being generated)
├── scripts/           # Compilation and publishing scripts
├── config/            # Build configuration
├── logs/              # Build and publishing logs
└── docs/              # Additional documentation
```

## Templates

### Template A: PythonTeX (Engineering Report)
- **File**: `templates/pythontex/engineering_report.tex`
- **Use case**: Signal processing, control systems, numerical analysis
- **Libraries**: NumPy, SciPy, Matplotlib

### Template B: SageTeX (Math Thesis)
- **File**: `templates/sagetex/math_thesis.tex`
- **Use case**: Symbolic algebra, number theory, 3D surfaces
- **Engine**: SageMath

### Template C: Knitr (Clinical Report)
- **File**: `templates/knitr/clinical_report.Rnw`
- **Use case**: Statistical analysis, clinical trials, data visualization
- **Libraries**: ggplot2, xtable

## Building

### Using Make (Recommended)

```bash
# Build individual templates
make pythontex
make sagetex
make knitr

# Build all templates
make all-docs

# Verify generated PDFs
make verify

# Clean generated files
make clean
```

### Using Build Scripts

```bash
# Make scripts executable
chmod +x scripts/*.sh

# Build PythonTeX document
./scripts/build_pythontex.sh templates/pythontex/engineering_report.tex

# Build SageTeX document
./scripts/build_sagetex.sh templates/sagetex/math_thesis.tex

# Build Knitr document
./scripts/build_knitr.sh templates/knitr/clinical_report.Rnw

# Verify a PDF
./scripts/verify_pdf.sh output/engineering_report.pdf
```

### Using latexmk

For SageTeX documents with automated dependency resolution:

```bash
cp config/latexmkrc ~/.latexmkrc
latexmk -pdf templates/sagetex/math_thesis.tex
```

## Build Chains

| Template   | Build Process                              |
|------------|-------------------------------------------|
| PythonTeX  | pdflatex -> pythontex -> pdflatex         |
| SageTeX    | pdflatex -> sage -> pdflatex              |
| Knitr      | Rscript (knit) -> pdflatex                |

## Requirements

- LaTeX: pdflatex, latexmk
- Python: python3, numpy, scipy, matplotlib, pythontex
- R: R, knitr, ggplot2, xtable
- SageMath: sage
- PDF tools: pdfinfo, pdftotext (poppler-utils)

## Verification

The `verify_pdf.sh` script checks:
- Structural integrity (qpdf)
- PDF metadata (pdfinfo)
- Text extraction (pdftotext)
- File size sanity

## Building in CoCalc (Recommended)

CoCalc automatically handles multi-pass compilation for all templates.

### Quick Build

1. Open the template file in CoCalc's LaTeX editor
2. Press **Shift+Enter** or use **Go > Build**
3. View PDF in the right pane

CoCalc automatically:
- Detects PythonTeX and SageTeX packages
- Recognizes .Rnw files as Knitr documents
- Runs all intermediate compilation passes
- Manages auxiliary files

### Tips for CoCalc

- **Disable Build on Save**: For computational documents, go to **Go > Build on Save** and disable it
- **Use TimeTravel**: Automatic version history at 2-second resolution
- **Check Build Tab**: View full compilation log and click on errors

### When to Use Terminal Commands

Use the Makefile and scripts for:
- Debugging compilation issues (run passes individually)
- Batch processing multiple documents
- PDF verification checks (`make verify`)

## Publishing to GitHub

### Initial Setup

1. **Configure GitHub repository**:
```bash
./scripts/setup_github.sh YOUR_GITHUB_USERNAME
```

2. **Create repository on GitHub**:
   - Visit: https://github.com/new
   - Repository name: `latex-templates`
   - Make it public or private
   - Do NOT initialize with README

3. **Publish all templates**:
```bash
# Review what will be published
git status

# Publish everything
./scripts/publish_all.sh

# Or just new/modified files
./scripts/publish_new.sh
```

### Publishing Workflow

```bash
# Publish specific category
./scripts/publish_category.sh aerospace

# Publish single template
python3 scripts/latex_publisher.py single templates/physics/quantum_mechanics.tex

# Check publishing status
python3 scripts/latex_publisher.py status

# Publish only modified files
python3 scripts/latex_publisher.py new
```

## CoCalc ShareServer Integration

### Generate Share Links

```bash
# Generate links for all templates
./scripts/generate_share_links.sh YOUR_COCALC_PROJECT_ID

# View generated links
cat SHARE_LINKS.md
```

### Enable Public Access

1. Open your CoCalc project
2. Go to Project Settings (gear icon)
3. Under "Public files", enable access for:
   - `templates/` directory
   - `output/` directory

See [COCALC_SHARESERVER.md](COCALC_SHARESERVER.md) for complete integration guide.

## Template Categories

The collection includes templates for:

**Physical Sciences**: Aerospace, Astronomy, Astrophysics, Atomic Physics, Chemistry, Climate Science, Cosmology, Earth Science, Fluid Dynamics, Geophysics, Materials Science, Optics, Particle Physics, Plasma Physics, Quantum Mechanics, Statistical Mechanics, Thermodynamics

**Life Sciences**: Bioinformatics, Biology, Biomedical Engineering, Computational Biology, Ecology, Epidemiology, Genetics, Immunology, Marine Biology, Microbiology, Neuroscience, Pharmacology, Systems Biology

**Engineering**: Acoustics, Aerospace, Biomedical, Chemical, Civil, Control Theory, Electrical, Industrial, Materials, Mechanical, Nuclear, Robotics, Signal Processing, Structural Engineering

**Mathematics & Computer Science**: Algorithms, Applied Mathematics, Category Theory, Combinatorics, Complex Analysis, Computational Geometry, Cryptography, Data Science, Differential Equations, Graph Theory, Linear Algebra, Logic, Machine Learning, Network Science, Number Theory, Numerical Analysis, Optimization, Probability, Stochastic Processes, Topology

**Social Sciences**: Economics, Econometrics, Environmental Science, Financial Mathematics, Game Theory, Operations Research, Political Science

## Template Features

Each template includes:

- **Computational Integration**: PythonTeX, SageTeX, or Knitr support where applicable
- **Professional Formatting**: Publication-ready layouts
- **Domain-Specific Packages**: Pre-configured for each scientific field
- **Example Content**: Demonstrating key features and equations
- **Build Scripts**: Automated compilation with proper pass sequences

## Bug Fixes Applied

This implementation includes fixes for issues in the original templates:
- **PythonTeX**: Fixed `\pySI` command (now takes 2 arguments), added T1 fontenc, removed deprecated pyfuture option
- **SageTeX**: Fixed `\sagevisible` command (now takes 2 arguments)

## Contributing

To contribute new templates:

1. Fork the repository
2. Add templates to appropriate category in `templates/`
3. Compile and test the template
4. Submit pull request with:
   - Template `.tex` file
   - Compiled PDF in `output/`
   - Brief description of the template

## License

[Specify your license here - e.g., MIT, CC BY 4.0, etc.]

## Support

- **Issues**: Report bugs or request features via GitHub Issues
- **Discussions**: Ask questions via GitHub Discussions
- **CoCalc**: For CoCalc-specific help, see [CoCalc Documentation](https://doc.cocalc.com/)
