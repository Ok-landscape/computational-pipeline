#!/usr/bin/env python3
"""
Image Quality Validator

Validates that extracted images have actual content and aren't blank/empty.
Prevents posting images with empty subplots or other quality issues.
"""

import numpy as np
from PIL import Image
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ImageQualityResult:
    """Result of image quality validation"""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metrics: Dict[str, float] = field(default_factory=dict)

    def add_error(self, message: str):
        """Add error message"""
        self.errors.append(message)
        self.is_valid = False

    def add_warning(self, message: str):
        """Add warning message"""
        self.warnings.append(message)

    def __str__(self) -> str:
        """String representation"""
        lines = []
        lines.append(f"Valid: {self.is_valid}")
        if self.errors:
            lines.append("Errors:")
            for error in self.errors:
                lines.append(f"  - {error}")
        if self.warnings:
            lines.append("Warnings:")
            for warning in self.warnings:
                lines.append(f"  - {warning}")
        if self.metrics:
            lines.append("Metrics:")
            for key, value in self.metrics.items():
                lines.append(f"  {key}: {value:.4f}")
        return "\n".join(lines)


class ImageQualityValidator:
    """Validates image quality to detect empty plots and other issues"""

    def __init__(self,
                 min_content_ratio: float = 0.05,
                 max_white_ratio: float = 0.85,
                 min_color_variance: float = 10.0):
        """
        Initialize validator

        Args:
            min_content_ratio: Minimum ratio of non-background pixels (default 5%)
            max_white_ratio: Maximum ratio of white/near-white pixels (default 85%)
            min_color_variance: Minimum color variance to indicate actual content
        """
        self.min_content_ratio = min_content_ratio
        self.max_white_ratio = max_white_ratio
        self.min_color_variance = min_color_variance

    def validate_image(self, image_path: str) -> ImageQualityResult:
        """
        Validate image quality

        Args:
            image_path: Path to image file

        Returns:
            ImageQualityResult with validation details
        """
        result = ImageQualityResult(is_valid=True)

        try:
            # Open image
            img = Image.open(image_path)
            img_array = np.array(img)

            # Store basic info
            result.metrics['width'] = img.width
            result.metrics['height'] = img.height
            result.metrics['total_pixels'] = img.width * img.height

            # Check 1: Image dimensions
            if img.width < 100 or img.height < 100:
                result.add_error(f"Image too small: {img.width}x{img.height}")
                return result

            # Check 2: Detect if image is mostly blank/white
            white_ratio = self._calculate_white_ratio(img_array)
            result.metrics['white_ratio'] = white_ratio

            if white_ratio > self.max_white_ratio:
                result.add_error(
                    f"Image is {white_ratio*100:.1f}% white/blank (max {self.max_white_ratio*100:.0f}%)"
                )

            # Check 3: Color variance (indicates actual content)
            color_variance = self._calculate_color_variance(img_array)
            result.metrics['color_variance'] = color_variance

            if color_variance < self.min_color_variance:
                result.add_error(
                    f"Low color variance ({color_variance:.2f}) - image appears blank"
                )

            # Check 4: Detect empty subplot regions (matplotlib-specific)
            if self._is_matplotlib_figure(img_array):
                empty_regions = self._detect_empty_subplots(img_array)
                result.metrics['empty_subplot_count'] = len(empty_regions)

                if empty_regions:
                    result.add_error(
                        f"Found {len(empty_regions)} empty subplot(s): {empty_regions}"
                    )

            # Check 5: Detect error text in image
            if self._contains_error_text(img_array):
                result.add_warning("Image may contain error messages")

            # Check 6: Content density
            content_ratio = self._calculate_content_ratio(img_array)
            result.metrics['content_ratio'] = content_ratio

            if content_ratio < self.min_content_ratio:
                result.add_warning(
                    f"Low content ratio ({content_ratio*100:.1f}%) - image may be mostly empty"
                )

        except Exception as e:
            logger.error(f"Error validating image {image_path}: {e}")
            result.add_error(f"Failed to validate image: {str(e)}")

        return result

    def _calculate_white_ratio(self, img_array: np.ndarray) -> float:
        """Calculate ratio of white/near-white pixels"""
        # Handle both RGB and RGBA
        if img_array.ndim == 3:
            if img_array.shape[2] == 4:  # RGBA
                rgb = img_array[:, :, :3]
                alpha = img_array[:, :, 3]
                # Consider pixels with low alpha as white background
                white_mask = (np.all(rgb > 240, axis=2)) | (alpha < 10)
            else:  # RGB
                white_mask = np.all(img_array > 240, axis=2)
        else:  # Grayscale
            white_mask = img_array > 240

        return np.sum(white_mask) / white_mask.size

    def _calculate_color_variance(self, img_array: np.ndarray) -> float:
        """Calculate color variance across image"""
        if img_array.ndim == 3:
            # Convert to grayscale for variance calculation
            if img_array.shape[2] == 4:  # RGBA
                gray = np.mean(img_array[:, :, :3], axis=2)
            else:  # RGB
                gray = np.mean(img_array, axis=2)
        else:
            gray = img_array

        return float(np.var(gray))

    def _calculate_content_ratio(self, img_array: np.ndarray) -> float:
        """Calculate ratio of pixels that appear to be content (not background)"""
        if img_array.ndim == 3:
            if img_array.shape[2] == 4:  # RGBA
                rgb = img_array[:, :, :3]
                # Content is non-white pixels
                content_mask = np.any(rgb < 240, axis=2)
            else:  # RGB
                content_mask = np.any(img_array < 240, axis=2)
        else:  # Grayscale
            content_mask = img_array < 240

        return np.sum(content_mask) / content_mask.size

    def _is_matplotlib_figure(self, img_array: np.ndarray) -> bool:
        """Check if image appears to be a matplotlib figure"""
        # Matplotlib figures typically have:
        # 1. White/light background
        # 2. Grid lines or axes
        # 3. Multiple distinct regions (subplots)

        # Simple heuristic: check if there are horizontal/vertical lines
        # that could be subplot boundaries
        if img_array.ndim != 3:
            return False

        # Look for consistent horizontal lines (subplot separators)
        gray = np.mean(img_array[:, :, :3], axis=2) if img_array.shape[2] >= 3 else img_array

        # Check for rows that are mostly white (potential subplot dividers)
        row_whiteness = np.mean(gray > 240, axis=1)
        has_subplot_dividers = np.any(row_whiteness > 0.95)

        return has_subplot_dividers

    def _detect_empty_subplots(self, img_array: np.ndarray) -> List[str]:
        """
        Detect empty subplot regions in matplotlib figures

        Returns list of detected empty regions like ["bottom-left", "bottom-right"]
        """
        empty_regions = []

        # Divide image into quadrants and check each
        height, width = img_array.shape[:2]
        mid_h, mid_w = height // 2, width // 2

        # Define quadrants
        quadrants = {
            'top-left': (0, mid_h, 0, mid_w),
            'top-right': (0, mid_h, mid_w, width),
            'bottom-left': (mid_h, height, 0, mid_w),
            'bottom-right': (mid_h, height, mid_w, width),
        }

        for name, (y1, y2, x1, x2) in quadrants.items():
            region = img_array[y1:y2, x1:x2]

            # Check if region is mostly white/empty
            if region.ndim == 3:
                if region.shape[2] == 4:  # RGBA
                    rgb = region[:, :, :3]
                    white_mask = np.all(rgb > 240, axis=2)
                else:  # RGB
                    white_mask = np.all(region > 240, axis=2)
            else:  # Grayscale
                white_mask = region > 240

            white_ratio = np.sum(white_mask) / white_mask.size

            # If more than 90% white, consider it empty
            if white_ratio > 0.90:
                # But check if there are axes/labels (usually at edges)
                # If edges are non-white, it's a subplot with axes but no content
                edges = np.concatenate([
                    region[0, :].flatten(),    # top edge
                    region[-1, :].flatten(),   # bottom edge
                    region[:, 0].flatten(),    # left edge
                    region[:, -1].flatten()    # right edge
                ])

                # If edges have some non-white content (axes), but center is empty
                edge_white_ratio = np.sum(edges > 240) / len(edges)

                if edge_white_ratio < 0.95:  # Has axes/frames
                    empty_regions.append(name)

        return empty_regions

    def _contains_error_text(self, img_array: np.ndarray) -> bool:
        """
        Check if image contains error messages (very basic heuristic)

        This is a simple check - proper implementation would use OCR
        """
        # Look for red pixels (common in error messages)
        if img_array.ndim == 3 and img_array.shape[2] >= 3:
            red_channel = img_array[:, :, 0]
            green_channel = img_array[:, :, 1]
            blue_channel = img_array[:, :, 2]

            # Red text: high red, low green/blue
            red_mask = (red_channel > 200) & (green_channel < 100) & (blue_channel < 100)
            red_ratio = np.sum(red_mask) / red_mask.size

            # If more than 1% is red, might be error text
            return red_ratio > 0.01

        return False

    def validate_batch(self, image_paths: List[str]) -> Dict[str, ImageQualityResult]:
        """
        Validate multiple images

        Args:
            image_paths: List of image file paths

        Returns:
            Dictionary mapping file paths to validation results
        """
        results = {}

        for image_path in image_paths:
            logger.info(f"Validating: {Path(image_path).name}")
            result = self.validate_image(image_path)
            results[image_path] = result

        return results

    def generate_report(self, results: Dict[str, ImageQualityResult]) -> str:
        """Generate validation report"""
        lines = []
        lines.append("=" * 80)
        lines.append("IMAGE QUALITY VALIDATION REPORT")
        lines.append("=" * 80)
        lines.append(f"Total images: {len(results)}")
        lines.append("")

        passed = sum(1 for r in results.values() if r.is_valid)
        failed = len(results) - passed

        lines.append(f"Passed: {passed}")
        lines.append(f"Failed: {failed}")
        lines.append("")

        if failed > 0:
            lines.append("FAILED IMAGES:")
            lines.append("-" * 80)
            for path, result in results.items():
                if not result.is_valid:
                    lines.append(f"\n{Path(path).name}:")
                    for error in result.errors:
                        lines.append(f"  ✗ {error}")

        lines.append("=" * 80)
        return "\n".join(lines)


def main():
    """Test the validator"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python image_quality_validator.py <image_path>")
        sys.exit(1)

    image_path = sys.argv[1]

    validator = ImageQualityValidator()
    result = validator.validate_image(image_path)

    print(result)
    print()

    if result.is_valid:
        print("✓ Image passed quality checks")
    else:
        print("✗ Image failed quality checks")

    sys.exit(0 if result.is_valid else 1)


if __name__ == "__main__":
    main()
