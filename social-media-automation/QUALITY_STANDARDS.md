# Content Quality Standards for Social Media Posting

## Overview

This document defines quality standards for computational notebook content before it can be posted to social media platforms. These standards ensure that all posted content maintains high quality and provides value to followers.

## Critical Quality Issue: Empty Plot Prevention

### The Problem

On 2025-11-25, we posted a notebook (`finite_element_method_heat_transfer`) with an image containing **two empty subplots**. The validation system at the time only checked "does image exist?" but not "is image quality good?". This resulted in posting broken content.

### Root Cause

The notebook created a 2x2 subplot grid in cell 5, but only populated the top 2 subplots. Matplotlib automatically output the figure after cell execution, capturing an incomplete figure with empty bottom subplots. Later cells (7 and 9) continued to populate the same figure object, but their outputs were text-only (not images), so only the incomplete image from cell 5 was available in the notebook outputs.

## Quality Standards

### 1. Image Quality Requirements

All images posted must meet these requirements:

#### A. Content Density
- **Maximum white/blank ratio**: 85% of pixels
- **Minimum content ratio**: 5% of pixels must be non-background
- **Minimum color variance**: 10.0 (indicates actual content vs blank image)

#### B. No Empty Subplots
- All subplots in a multi-panel figure must contain data
- Quadrant analysis checks top-left, top-right, bottom-left, bottom-right regions
- Any subplot more than 90% blank is flagged as empty

#### C. No Error Messages
- Images should not contain visible error text
- Red text (common in error messages) is detected heuristically

#### D. Appropriate Dimensions
- Minimum dimensions: 100x100 pixels
- Recommended: 1200x800 or larger for social media

### 2. Notebook Execution Standards

To ensure quality outputs:

#### A. Complete Figures
- If creating multi-panel figures across multiple cells:
  - Use `plt.ioff()` to prevent automatic figure display
  - Only display/save the figure after ALL subplots are populated
  - Or create separate complete figures in each cell

#### B. Proper Output Control
```python
# GOOD: Complete figure in one cell
fig, axes = plt.subplots(2, 2)
# ... populate all 4 subplots ...
plt.tight_layout()
plt.show()  # Now display complete figure

# BAD: Partial figure output
fig, axes = plt.subplots(2, 2)
# ... only populate 2 subplots ...
# Cell ends here - matplotlib outputs incomplete figure!
```

#### C. File Naming
- Avoid generic names like `plot.png` that get overwritten
- Use descriptive names: `finite_element_convergence.png`
- Include notebook name in saved file name

### 3. Validation Workflow

Before posting, ALL content must pass:

#### Phase 1: Basic Validation
1. Local file exists
2. File exists on GitHub
3. Notebook has saved outputs
4. Notebook has images in outputs
5. CoCalc link is valid and accessible
6. Post text quality checks

#### Phase 2: Image Quality Validation (NEW)
7. Extract all images from notebook outputs
8. Check each image for:
   - Acceptable white/blank ratio
   - Sufficient color variance
   - No empty subplot regions
   - No error text
9. **FAIL if ANY image fails quality checks**

### 4. Post-Validation Actions

#### If Validation Fails
- **DO NOT POST** - even if other checks pass
- Log detailed error information
- Add notebook to "needs_manual_review" list
- Generate issue report with:
  - Which cell(s) have problematic images
  - Specific quality issues detected
  - Suggested fixes

#### If Validation Passes
- Content is safe to post
- Proceed with scheduling or immediate posting
- Log successful validation for audit trail

## Tools and Implementation

### Image Quality Validator
Location: `/home/user/computational-pipeline/social-media-automation/image_quality_validator.py`

Usage:
```bash
# Validate single image
python image_quality_validator.py path/to/image.png

# Batch validate all notebooks
python batch_quality_check.py
```

### Enhanced Pre-Publish Validator
Location: `/home/user/computational-pipeline/social-media-automation/pre_publish_validator.py`

The validator now includes:
- `_check_notebook_image_quality()` method
- Automatic extraction of images from notebook outputs to temporary files
- Quality validation using `ImageQualityValidator`
- Detailed error reporting with cell and output indices

### Batch Quality Checker
Location: `/home/user/computational-pipeline/social-media-automation/batch_quality_check.py`

Scans all notebooks and generates report:
- Notebooks passed: Ready for posting
- Notebooks failed: Quality issues detected
- Notebooks with no images: Not executed or text-only
- Detailed JSON report saved to `data/quality_check_report.json`

## Common Issues and Fixes

### Issue 1: Empty Subplots

**Symptom**: Multi-panel figure with some panels blank

**Cause**: Figure output before all subplots populated

**Fix**:
```python
# Add at start of cell that creates figure
plt.ioff()  # Disable automatic display

# ... create and populate ALL subplots ...

# Only show when complete
plt.ion()   # Re-enable
plt.show()
```

### Issue 2: Mostly White/Blank Images

**Symptom**: Image validation fails with "X% white/blank (max 85%)"

**Cause**:
- Plot has insufficient data
- Plot created but data wasn't actually plotted
- Axes are drawn but no lines/points/bars

**Fix**:
- Check that data arrays are not empty
- Verify plot commands actually executed
- Add print statements to check data before plotting

### Issue 3: Overwritten Output Files

**Symptom**: Wrong notebook's plots appear in different notebook

**Cause**: Multiple notebooks save to same filename (e.g., `plot.png`)

**Fix**:
```python
# Use unique filename
notebook_name = "finite_element_heat_transfer"
plt.savefig(f'{notebook_name}_output.png')
```

## Quality Metrics (Batch Check Results)

As of 2025-11-25:

- **Total notebooks checked**: 261
- **Passed quality checks**: 6 (2.3%)
- **Failed quality checks**: 9 (3.4%)
  - finite_element_method_heat_transfer
  - damped_harmonic_oscillator
  - kuramoto_model_synchronization
  - lorentz_attractor_fractal_dimension
  - poisson_equation_multigrid_solver
  - replicator_dynamics
  - sir_epidemic_model
  - spectral_methods_chebyshev_polynomials
  - stratonovich_calculus
  - symmetric_polynomials_out
  - trapezoidal_rule
- **No images (not executed)**: 246 (94.3%)

## Action Items

### Immediate
1. ✅ **DONE**: Created image quality validator
2. ✅ **DONE**: Integrated into pre-publish validation
3. ✅ **DONE**: Ran batch quality check on all notebooks
4. ⚠️ **PENDING**: Delete bad Facebook posts (API permission issue - needs manual deletion)
5. ⚠️ **PENDING**: Fix 9 notebooks with quality issues

### Short-term
1. Re-execute fixed notebooks to generate quality outputs
2. Update automated posting workflow to use enhanced validator
3. Add quality checks to CI/CD pipeline (if exists)
4. Create visual dashboard showing validation stats

### Long-term
1. Develop notebook linting tool to catch these issues before execution
2. Add pre-execution checks (e.g., detect incomplete subplot creation patterns)
3. Implement automated notebook repair suggestions
4. Create notebook authoring guidelines with quality best practices

## Validation Command Reference

```bash
# Validate single notebook before posting
python -c "
from pre_publish_validator import PrePublishValidator
validator = PrePublishValidator()
result = validator.validate_notebook_post(
    'path/to/notebook.ipynb',
    'https://cocalc.com/...'
)
print(result)
exit(0 if result.is_valid else 1)
"

# Batch check all notebooks
python batch_quality_check.py

# Validate specific image
python image_quality_validator.py path/to/image.png

# Check publishing queue
python validate_queue.py
```

## Contact and Support

If you encounter quality issues:

1. Check this document for common issues
2. Run the image quality validator on problematic images
3. Review the batch quality check report
4. Examine the notebook's execution outputs cell by cell
5. Fix the notebook code or execution, then re-execute

Remember: **Never post content that fails validation.** The validation exists to maintain our content quality standards and protect our followers from broken or incomplete content.

---

**Last Updated**: 2025-11-25
**Author**: Social Media Automation System
**Version**: 1.0
