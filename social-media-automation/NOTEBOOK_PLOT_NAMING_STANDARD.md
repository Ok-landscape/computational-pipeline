# Notebook Plot Naming Standard

## Convention
All notebook plots must use descriptive suffixes following this format:
`{notebook_name}_{specific_plot_description}.png`

## Guidelines

### Single Plot Notebooks
If a notebook generates one comprehensive figure:
- Use descriptive name that captures the plot's purpose
- Example: `finite_element_method_heat_transfer_comprehensive_analysis.png`

### Multiple Plot Notebooks
If a notebook generates multiple separate figures:
- Each plot gets its own descriptive suffix
- Examples:
  - `damped_harmonic_oscillator_phase_portrait.png`
  - `damped_harmonic_oscillator_time_series.png`
  - `damped_harmonic_oscillator_energy_decay.png`

## Naming Best Practices

1. **Be Specific**: Name should indicate what the plot shows
2. **Be Consistent**: Use similar patterns across notebooks
3. **Be Professional**: Use underscores, lowercase, no spaces
4. **Be Descriptive**: Should understand plot content from filename

## Common Suffixes

- `_analysis` - Comprehensive analysis plots
- `_comparison` - Comparing multiple methods/cases
- `_convergence` - Convergence studies
- `_phase_portrait` - Phase space visualizations
- `_time_series` - Time evolution plots
- `_probability_density` - PDF visualizations
- `_energy_decay` - Energy dissipation
- `_distribution` - Spatial/statistical distributions
- `_validation` - Validation against analytical solutions
- `_comprehensive_analysis` - Multi-panel figures showing various aspects

## Examples by Notebook Type

**FEM/Numerical Methods:**
- `{notebook}_convergence_study.png`
- `{notebook}_mesh_comparison.png`
- `{notebook}_error_analysis.png`
- `{notebook}_comprehensive_analysis.png`

**Dynamical Systems:**
- `{notebook}_phase_portrait.png`
- `{notebook}_bifurcation_diagram.png`
- `{notebook}_attractor.png`
- `{notebook}_trajectory.png`

**Statistical/Probabilistic:**
- `{notebook}_probability_density.png`
- `{notebook}_sample_paths.png`
- `{notebook}_distribution_evolution.png`

## Implementation

When fixing notebooks:
1. Identify what each plot shows
2. Choose appropriate descriptive suffix
3. Update `plt.savefig()` calls
4. Test to ensure correct file creation
5. Commit with updated naming

## Benefits

- No file overwrites between notebooks
- Clear plot-to-notebook association
- Self-documenting file structure
- Easy plot collection management
- Professional organization

## Implementation Status

### Completed
1. `finite_element_method_heat_transfer.ipynb` - Uses `comprehensive_analysis` suffix for 2x2 multi-case figure

### Pending
2. `damped_harmonic_oscillator.ipynb`
3. `kuramoto_model_synchronization.ipynb`
4. `lorentz_attractor_fractal_dimension.ipynb`
5. `poisson_equation_multigrid_solver.ipynb`
6. `replicator_dynamics.ipynb`
7. `sir_epidemic_model.ipynb`
8. `spectral_methods_chebyshev_polynomials.ipynb`
9. `stratonovich_calculus.ipynb`
