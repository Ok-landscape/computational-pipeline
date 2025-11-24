# Computational Pipeline - Published Notebooks

This repository contains validated, executable Jupyter notebooks covering computational physics, mathematics, finance, and machine learning topics.

## Repository Structure

This is a **split repository** setup. Content is divided between two repositories:

### Public Repository (This Repo)
- **Location**: https://github.com/Ok-landscape/computational-pipeline
- **Content**: Published, validated Jupyter notebooks
- **Directory**: `notebooks/published/`
- **Visibility**: PUBLIC

### Private Repository
- **Location**: https://github.com/Ok-landscape/computational-pipeline-outputs
- **Content**:
  - Social media posts (`output/`)
  - Orchestration files (`orchestration/`)
  - Templates (`templates/`)
  - Workflow automation (`workflow.py`, `system_prompts.md`)
- **Visibility**: PRIVATE

## Why Split Repositories?

This approach allows us to:
1. Share educational notebooks publicly for maximum impact
2. Keep internal workflow automation and drafts private
3. Maintain clean separation between published content and tooling

## Published Notebooks

All notebooks in `notebooks/published/` have been:
- Executed successfully via papermill validation
- Verified for correctness
- Formatted with proper LaTeX mathematics
- Tested with reproducible results

## Topics Covered

The notebooks span multiple domains including:
- **Physics**: Quantum mechanics, relativity, electromagnetism, chaos theory
- **Mathematics**: Differential equations, complex analysis, topology, group theory
- **Finance**: Options pricing, portfolio optimization, risk models, stochastic calculus
- **Machine Learning**: Neural networks, reinforcement learning, deep learning architectures
- **Numerical Methods**: ODE/PDE solvers, optimization algorithms, linear algebra

## Usage

Each notebook is self-contained and can be executed independently:

```bash
# Clone the repository
git clone https://github.com/Ok-landscape/computational-pipeline.git

# Navigate to published notebooks
cd computational-pipeline/notebooks/published

# Open with Jupyter
jupyter notebook
```

## Requirements

Notebooks use standard scientific Python stack:
- numpy
- scipy
- matplotlib
- pandas

## Contributing

This repository is managed by an autonomous computational pipeline. For questions or issues, please open a GitHub issue.

## License

All published notebooks are available for educational and research purposes.

## Automation

This repository is part of an autonomous research pipeline that:
1. Generates computational notebooks on scientific topics
2. Validates code execution via papermill
3. Publishes verified notebooks to this repository
4. Creates social media content (stored in private repo)

For details on the pipeline architecture, see the private repository (for authorized users).
