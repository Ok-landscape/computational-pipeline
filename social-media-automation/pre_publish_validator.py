#!/usr/bin/env python3
"""
Pre-Publish Validation Module

Validates content before posting to social media to prevent 404s and missing images.
Performs comprehensive checks on GitHub existence, image availability, and link validity.
"""

import os
import sys
import json
import requests
import logging
import base64
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import nbformat
from image_quality_validator import ImageQualityValidator, ImageQualityResult

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of validation checks"""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    checks_passed: Dict[str, bool] = field(default_factory=dict)
    metadata: Dict[str, any] = field(default_factory=dict)

    def add_error(self, message: str):
        """Add error message"""
        self.errors.append(message)
        self.is_valid = False

    def add_warning(self, message: str):
        """Add warning message"""
        self.warnings.append(message)

    def add_check(self, name: str, passed: bool):
        """Record check result"""
        self.checks_passed[name] = passed
        if not passed:
            self.is_valid = False

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'is_valid': self.is_valid,
            'errors': self.errors,
            'warnings': self.warnings,
            'checks_passed': self.checks_passed,
            'metadata': self.metadata,
            'timestamp': datetime.now().isoformat()
        }

    def __str__(self) -> str:
        """Readable string representation"""
        lines = []
        lines.append("=" * 80)
        lines.append("VALIDATION RESULT")
        lines.append("=" * 80)
        lines.append(f"Status: {'PASS' if self.is_valid else 'FAIL'}")
        lines.append("")

        if self.checks_passed:
            lines.append("Checks:")
            for check, passed in self.checks_passed.items():
                status = "✓" if passed else "✗"
                lines.append(f"  {status} {check}")
            lines.append("")

        if self.errors:
            lines.append("ERRORS:")
            for error in self.errors:
                lines.append(f"  ✗ {error}")
            lines.append("")

        if self.warnings:
            lines.append("WARNINGS:")
            for warning in self.warnings:
                lines.append(f"  ⚠ {warning}")
            lines.append("")

        if self.metadata:
            lines.append("Metadata:")
            for key, value in self.metadata.items():
                lines.append(f"  {key}: {value}")

        lines.append("=" * 80)
        return "\n".join(lines)


class PrePublishValidator:
    """Validates content before publishing to social media"""

    GITHUB_API_BASE = "https://api.github.com"
    GITHUB_RAW_BASE = "https://raw.githubusercontent.com"

    def __init__(self,
                 github_owner: str = "Ok-landscape",
                 github_repo: str = "computational-pipeline",
                 github_token: Optional[str] = None):
        """
        Initialize validator

        Args:
            github_owner: GitHub repository owner
            github_repo: GitHub repository name
            github_token: Optional GitHub API token for higher rate limits
        """
        self.github_owner = github_owner
        self.github_repo = github_repo
        self.github_token = github_token

        # Cache for GitHub file checks
        self._github_cache = {}

        # Image quality validator
        self.image_validator = ImageQualityValidator(
            min_content_ratio=0.05,
            max_white_ratio=0.85,
            min_color_variance=10.0
        )

        logger.info(f"Validator initialized for {github_owner}/{github_repo}")

    def validate_notebook_post(self,
                               notebook_path: str,
                               cocalc_url: str,
                               post_text: Optional[str] = None) -> ValidationResult:
        """
        Validate a notebook post before publishing

        Args:
            notebook_path: Local path to notebook file
            cocalc_url: CoCalc URL for the notebook
            post_text: Optional post text to validate

        Returns:
            ValidationResult object
        """
        result = ValidationResult(is_valid=True)
        result.metadata['notebook_path'] = notebook_path
        result.metadata['cocalc_url'] = cocalc_url

        logger.info(f"Validating notebook: {Path(notebook_path).name}")

        # Check 1: Local file exists
        if not self._check_local_file_exists(notebook_path, result):
            return result

        # Check 2: GitHub file existence
        github_path = self._extract_github_path(notebook_path)
        self._check_github_file_exists(github_path, result)

        # Check 3: Notebook has saved outputs with images
        self._check_notebook_outputs(notebook_path, result)

        # Check 3b: Image quality validation (NEW)
        self._check_notebook_image_quality(notebook_path, result)

        # Check 4: CoCalc link validation
        self._check_cocalc_link(cocalc_url, result)

        # Check 5: Post text quality
        if post_text:
            self._check_post_text_quality(post_text, result)

        # Check 6: Repository sync status
        self._check_repo_sync_status(notebook_path, result)

        return result

    def validate_template_post(self,
                               template_path: str,
                               cocalc_url: str,
                               post_text: Optional[str] = None) -> ValidationResult:
        """
        Validate a LaTeX template post before publishing

        Args:
            template_path: Local path to template file
            cocalc_url: CoCalc URL for the template
            post_text: Optional post text to validate

        Returns:
            ValidationResult object
        """
        result = ValidationResult(is_valid=True)
        result.metadata['template_path'] = template_path
        result.metadata['cocalc_url'] = cocalc_url

        logger.info(f"Validating template: {Path(template_path).name}")

        # Check 1: Local file exists
        if not self._check_local_file_exists(template_path, result):
            return result

        # Check 2: GitHub file existence
        github_path = self._extract_github_path(template_path)
        self._check_github_file_exists(github_path, result)

        # Check 3: PDF exists (for templates)
        self._check_template_pdf_exists(template_path, result)

        # Check 4: CoCalc link validation
        self._check_cocalc_link(cocalc_url, result)

        # Check 5: Post text quality
        if post_text:
            self._check_post_text_quality(post_text, result)

        # Check 6: Repository sync status
        self._check_repo_sync_status(template_path, result)

        return result

    def _check_local_file_exists(self, file_path: str, result: ValidationResult) -> bool:
        """Check if file exists locally"""
        file_exists = Path(file_path).exists()
        result.add_check("Local file exists", file_exists)

        if not file_exists:
            result.add_error(f"File not found locally: {file_path}")
            return False

        result.metadata['file_size'] = Path(file_path).stat().st_size
        return True

    def _extract_github_path(self, local_path: str) -> str:
        """
        Extract GitHub repository path from local path

        Example:
        /home/user/computational-pipeline/social-media-automation/repo-data/notebooks/published/file.ipynb
        -> notebooks/published/file.ipynb
        """
        local_path = str(local_path)

        # Handle notebooks
        if 'repo-data/notebooks/published/' in local_path:
            idx = local_path.index('repo-data/notebooks/published/')
            relative = local_path[idx:]
            return relative.replace('repo-data/', '')

        # Handle templates
        if 'repo-data/latex-templates/templates/' in local_path:
            idx = local_path.index('repo-data/latex-templates/templates/')
            relative = local_path[idx:]
            return relative.replace('repo-data/latex-templates/', '')

        # Fallback: try to extract from 'repo-data/'
        if 'repo-data/' in local_path:
            idx = local_path.index('repo-data/')
            return local_path[idx + len('repo-data/'):]

        # Unable to determine
        logger.warning(f"Unable to extract GitHub path from: {local_path}")
        return Path(local_path).name

    def _check_github_file_exists(self, github_path: str, result: ValidationResult) -> bool:
        """Check if file exists on GitHub"""
        # Check cache first
        if github_path in self._github_cache:
            exists = self._github_cache[github_path]
            result.add_check("GitHub file exists", exists)
            if not exists:
                result.add_error(f"File not found on GitHub: {github_path}")
            return exists

        # Check via GitHub API
        url = f"{self.GITHUB_API_BASE}/repos/{self.github_owner}/{self.github_repo}/contents/{github_path}"

        headers = {}
        if self.github_token:
            headers['Authorization'] = f'token {self.github_token}'

        try:
            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                self._github_cache[github_path] = True
                result.add_check("GitHub file exists", True)
                result.metadata['github_url'] = f"https://github.com/{self.github_owner}/{self.github_repo}/blob/main/{github_path}"
                return True
            elif response.status_code == 404:
                self._github_cache[github_path] = False
                result.add_check("GitHub file exists", False)
                result.add_error(f"File not found on GitHub: {github_path}")
                result.add_error("Suggestion: Push this file to GitHub before posting")
                return False
            else:
                result.add_warning(f"Unable to verify GitHub file (status {response.status_code})")
                result.add_check("GitHub file exists", True)  # Assume exists
                return True

        except requests.exceptions.RequestException as e:
            logger.error(f"Error checking GitHub: {e}")
            result.add_warning(f"GitHub check failed: {str(e)}")
            result.add_check("GitHub file exists", True)  # Assume exists
            return True

    def _check_notebook_outputs(self, notebook_path: str, result: ValidationResult) -> bool:
        """Check if notebook has saved outputs with images"""
        try:
            with open(notebook_path, 'r') as f:
                nb = nbformat.read(f, as_version=4)

            has_outputs = False
            has_images = False
            output_count = 0
            image_count = 0

            for cell in nb.cells:
                if cell.cell_type == 'code':
                    if cell.get('outputs'):
                        output_count += len(cell.outputs)
                        has_outputs = True

                        for output in cell.outputs:
                            if output.get('output_type') == 'display_data' or output.get('output_type') == 'execute_result':
                                data = output.get('data', {})
                                if 'image/png' in data or 'image/jpeg' in data:
                                    image_count += 1
                                    has_images = True

            result.metadata['notebook_outputs'] = output_count
            result.metadata['notebook_images'] = image_count

            # Check if has outputs
            result.add_check("Notebook has outputs", has_outputs)
            if not has_outputs:
                result.add_error("Notebook has no saved outputs - needs execution")
                result.add_error("Suggestion: Execute notebook to generate outputs before posting")

            # Check if has images
            result.add_check("Notebook has images", has_images)
            if not has_images:
                result.add_warning("Notebook has no images - post will be text-only")

            return has_outputs and has_images

        except Exception as e:
            logger.error(f"Error reading notebook: {e}")
            result.add_warning(f"Unable to check notebook outputs: {str(e)}")
            result.add_check("Notebook has outputs", False)
            result.add_check("Notebook has images", False)
            return False

    def _check_notebook_image_quality(self, notebook_path: str, result: ValidationResult) -> bool:
        """
        Check quality of images in notebook outputs
        Detects empty plots, blank images, and other quality issues
        """
        try:
            with open(notebook_path, 'r') as f:
                nb = nbformat.read(f, as_version=4)

            images_checked = 0
            images_passed = 0
            images_failed = 0
            quality_issues = []

            for cell_idx, cell in enumerate(nb.cells):
                if cell.cell_type == 'code' and cell.get('outputs'):
                    for output_idx, output in enumerate(cell.outputs):
                        if output.get('output_type') in ['display_data', 'execute_result']:
                            data = output.get('data', {})

                            # Check PNG images
                            if 'image/png' in data:
                                images_checked += 1

                                # Extract image to temporary file
                                png_data = data['image/png']
                                png_bytes = base64.b64decode(png_data)

                                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                                    tmp.write(png_bytes)
                                    tmp_path = tmp.name

                                try:
                                    # Validate image quality
                                    quality_result = self.image_validator.validate_image(tmp_path)

                                    if quality_result.is_valid:
                                        images_passed += 1
                                    else:
                                        images_failed += 1
                                        issue_desc = f"Cell {cell_idx} Output {output_idx}: "
                                        issue_desc += ", ".join(quality_result.errors)
                                        quality_issues.append(issue_desc)

                                        logger.warning(f"Image quality issue in {Path(notebook_path).name}: {issue_desc}")

                                finally:
                                    # Clean up temp file
                                    try:
                                        os.unlink(tmp_path)
                                    except:
                                        pass

            # Record results
            result.metadata['images_quality_checked'] = images_checked
            result.metadata['images_quality_passed'] = images_passed
            result.metadata['images_quality_failed'] = images_failed

            if images_checked > 0:
                if images_failed > 0:
                    result.add_check("Image quality validation", False)
                    result.add_error(f"{images_failed} of {images_checked} images failed quality checks")
                    for issue in quality_issues[:3]:  # Show first 3 issues
                        result.add_error(f"  - {issue}")
                    if len(quality_issues) > 3:
                        result.add_error(f"  ... and {len(quality_issues) - 3} more issues")
                    result.add_error("Suggestion: Review notebook execution for empty plots or incomplete figures")
                    return False
                else:
                    result.add_check("Image quality validation", True)
                    return True
            else:
                # No images to check
                result.add_check("Image quality validation", True)
                return True

        except Exception as e:
            logger.error(f"Error checking image quality: {e}")
            result.add_warning(f"Unable to check image quality: {str(e)}")
            result.add_check("Image quality validation", False)
            return False

    def _check_template_pdf_exists(self, template_path: str, result: ValidationResult) -> bool:
        """Check if PDF exists for template"""
        # Look for PDF in same directory
        template_dir = Path(template_path).parent
        template_name = Path(template_path).stem

        # Common PDF patterns
        pdf_patterns = [
            f"{template_name}.pdf",
            f"{template_name}_example.pdf",
            f"{template_name}_output.pdf",
        ]

        pdf_found = False
        for pattern in pdf_patterns:
            pdf_path = template_dir / pattern
            if pdf_path.exists():
                pdf_found = True
                result.metadata['pdf_path'] = str(pdf_path)
                result.metadata['pdf_size'] = pdf_path.stat().st_size
                break

        result.add_check("Template PDF exists", pdf_found)
        if not pdf_found:
            result.add_warning("No PDF found for template")
            result.add_warning("Suggestion: Compile template to generate PDF before posting")

        return pdf_found

    def _check_cocalc_link(self, cocalc_url: str, result: ValidationResult) -> bool:
        """Check if CoCalc link is valid and returns 200"""
        if not cocalc_url:
            result.add_check("CoCalc link valid", False)
            result.add_error("No CoCalc URL provided")
            return False

        # Basic format check
        if not cocalc_url.startswith('https://cocalc.com/'):
            result.add_check("CoCalc link format", False)
            result.add_error(f"Invalid CoCalc URL format: {cocalc_url}")
            return False
        else:
            result.add_check("CoCalc link format", True)

        # Check if link returns 200
        try:
            # Use HEAD request to avoid downloading content
            response = requests.head(cocalc_url, timeout=10, allow_redirects=True)

            if response.status_code == 200:
                result.add_check("CoCalc link accessible", True)
                return True
            elif response.status_code == 404:
                result.add_check("CoCalc link accessible", False)
                result.add_error(f"CoCalc link returns 404: {cocalc_url}")
                result.add_error("Suggestion: Wait for GitHub->CoCalc sync (5-15 minutes)")
                return False
            else:
                result.add_warning(f"CoCalc link returned status {response.status_code}")
                result.add_check("CoCalc link accessible", True)  # Assume OK
                return True

        except requests.exceptions.RequestException as e:
            logger.error(f"Error checking CoCalc link: {e}")
            result.add_warning(f"Unable to verify CoCalc link: {str(e)}")
            result.add_check("CoCalc link accessible", True)  # Assume OK
            return True

    def _check_post_text_quality(self, post_text: str, result: ValidationResult) -> bool:
        """Check post text quality"""
        if not post_text or not post_text.strip():
            result.add_check("Post text exists", False)
            result.add_error("Post text is empty")
            return False

        result.add_check("Post text exists", True)
        result.metadata['post_length'] = len(post_text)

        # Check length constraints
        # Facebook: 63,206 characters
        # Threads: 500 characters
        # Instagram: 2,200 characters

        if len(post_text) > 63206:
            result.add_error(f"Post text too long for Facebook: {len(post_text)} chars (max 63,206)")

        if len(post_text) < 10:
            result.add_warning("Post text very short (less than 10 characters)")

        # Check for common issues
        if '\\' in post_text and ('frac' in post_text or 'sum' in post_text):
            result.add_warning("Post contains LaTeX syntax - may not render correctly")

        return True

    def _check_repo_sync_status(self, file_path: str, result: ValidationResult) -> bool:
        """Check if local file is in sync with repository"""
        # This is a basic check - in production, could use git to check diff
        github_path = self._extract_github_path(file_path)

        # Check if file exists locally
        if not Path(file_path).exists():
            result.add_check("Repository sync", False)
            result.add_warning("File not found locally")
            return False

        # Basic check: file exists both locally and on GitHub
        # For a more thorough check, would need to compare file hashes
        result.add_check("Repository sync", True)
        result.add_warning("Repository sync check is basic - consider manual verification")

        return True

    def validate_batch(self, items: List[Dict]) -> Dict[str, ValidationResult]:
        """
        Validate multiple items

        Args:
            items: List of items to validate, each with 'type', 'path', 'url', 'text'

        Returns:
            Dictionary mapping item identifiers to validation results
        """
        results = {}

        for item in items:
            item_type = item.get('type', 'notebook')
            item_path = item.get('path')
            item_url = item.get('url')
            item_text = item.get('text')
            item_id = item.get('id', Path(item_path).stem if item_path else 'unknown')

            logger.info(f"Validating {item_id}...")

            if item_type == 'notebook':
                result = self.validate_notebook_post(item_path, item_url, item_text)
            elif item_type == 'template':
                result = self.validate_template_post(item_path, item_url, item_text)
            else:
                result = ValidationResult(is_valid=False)
                result.add_error(f"Unknown item type: {item_type}")

            results[item_id] = result

        return results

    def generate_validation_report(self, results: Dict[str, ValidationResult]) -> str:
        """
        Generate a summary report of validation results

        Args:
            results: Dictionary of validation results

        Returns:
            Formatted report string
        """
        lines = []
        lines.append("=" * 80)
        lines.append("VALIDATION REPORT")
        lines.append("=" * 80)
        lines.append(f"Total items validated: {len(results)}")
        lines.append("")

        passed = sum(1 for r in results.values() if r.is_valid)
        failed = len(results) - passed

        lines.append(f"Passed: {passed}")
        lines.append(f"Failed: {failed}")
        lines.append("")

        if failed > 0:
            lines.append("FAILED ITEMS:")
            lines.append("-" * 80)
            for item_id, result in results.items():
                if not result.is_valid:
                    lines.append(f"\n{item_id}:")
                    for error in result.errors:
                        lines.append(f"  ✗ {error}")
            lines.append("")

        if any(r.warnings for r in results.values()):
            lines.append("ITEMS WITH WARNINGS:")
            lines.append("-" * 80)
            for item_id, result in results.items():
                if result.warnings:
                    lines.append(f"\n{item_id}:")
                    for warning in result.warnings:
                        lines.append(f"  ⚠ {warning}")
            lines.append("")

        lines.append("=" * 80)
        return "\n".join(lines)


def main():
    """Test validator"""
    validator = PrePublishValidator()

    # Test notebook validation
    notebook_path = "/home/user/computational-pipeline/social-media-automation/repo-data/notebooks/published/finite_element_method_heat_transfer.ipynb"
    cocalc_url = "https://cocalc.com/github/Ok-landscape/computational-pipeline/blob/main/notebooks/published/finite_element_method_heat_transfer.ipynb"

    print("Testing notebook validation...")
    result = validator.validate_notebook_post(notebook_path, cocalc_url)
    print(result)


if __name__ == "__main__":
    main()
