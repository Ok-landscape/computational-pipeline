#!/usr/bin/env python3
"""
Media Extraction Module for Social Media Posts

Extracts images from PDFs, optimizes for different platforms,
and generates accessibility alt-text.
"""

import os
import logging
from pathlib import Path
from typing import List, Optional, Tuple, Dict
from dataclasses import dataclass
from PIL import Image
import io

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ExtractedMedia:
    """Container for extracted media with metadata"""
    image_path: str
    platform: str  # 'facebook', 'instagram', 'threads'
    width: int
    height: int
    file_size: int
    alt_text: str
    source_pdf: str
    page_number: int = 1


class MediaExtractor:
    """Extract and optimize images from LaTeX PDFs for social media"""

    # Platform-specific image requirements
    PLATFORM_SPECS = {
        'facebook': {
            'max_width': 2048,
            'max_height': 2048,
            'aspect_ratio': None,  # Flexible
            'format': 'PNG',
            'max_size_mb': 4
        },
        'instagram': {
            'max_width': 1080,
            'max_height': 1350,
            'aspect_ratio': (4, 5),  # Vertical posts work best
            'format': 'JPEG',
            'max_size_mb': 8
        },
        'threads': {
            'max_width': 1080,
            'max_height': 1080,
            'aspect_ratio': (1, 1),  # Square
            'format': 'JPEG',
            'max_size_mb': 4
        }
    }

    def __init__(self, output_dir: str = "/home/user/computational-pipeline/social-media-automation/media"):
        """
        Initialize media extractor

        Args:
            output_dir: Directory for processed images
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Try to import PyMuPDF
        try:
            import fitz
            self.fitz = fitz
            self.has_fitz = True
            logger.info("PyMuPDF (fitz) available for PDF processing")
        except ImportError:
            self.fitz = None
            self.has_fitz = False
            logger.warning("PyMuPDF not available. PDF extraction will be limited.")

    def extract_from_pdf(self,
                        pdf_path: str,
                        template_name: str,
                        category: str,
                        platforms: List[str] = None) -> Dict[str, ExtractedMedia]:
        """
        Extract and optimize images from PDF for specified platforms

        Args:
            pdf_path: Path to PDF file
            template_name: Template identifier
            category: Template category
            platforms: List of platforms to generate images for

        Returns:
            Dictionary mapping platform names to ExtractedMedia objects
        """
        if platforms is None:
            platforms = ['facebook', 'instagram', 'threads']

        if not Path(pdf_path).exists():
            logger.error(f"PDF not found: {pdf_path}")
            return {}

        if not self.has_fitz:
            logger.error("PyMuPDF not available. Cannot extract from PDF.")
            return self._extract_with_imagemagick(pdf_path, template_name, category, platforms)

        results = {}

        try:
            # Open PDF
            doc = self.fitz.open(pdf_path)
            logger.info(f"Processing PDF: {pdf_path} ({len(doc)} pages)")

            # Extract first page as base image
            page = doc[0]
            pix = page.get_pixmap(matrix=self.fitz.Matrix(2, 2))  # 2x resolution

            # Convert to PIL Image
            img_data = pix.tobytes("png")
            base_image = Image.open(io.BytesIO(img_data))

            # Generate platform-specific versions
            for platform in platforms:
                try:
                    optimized = self._optimize_for_platform(
                        base_image,
                        platform,
                        template_name,
                        category
                    )

                    if optimized:
                        # Generate alt text
                        alt_text = self._generate_alt_text(template_name, category, platform)

                        media = ExtractedMedia(
                            image_path=optimized['path'],
                            platform=platform,
                            width=optimized['width'],
                            height=optimized['height'],
                            file_size=optimized['size'],
                            alt_text=alt_text,
                            source_pdf=pdf_path,
                            page_number=1
                        )

                        results[platform] = media
                        logger.info(f"Generated {platform} image: {optimized['path']}")

                except Exception as e:
                    logger.error(f"Error optimizing for {platform}: {e}")

            doc.close()

        except Exception as e:
            logger.error(f"Error extracting from PDF: {e}")

        return results

    def extract_plot_image(self,
                          plot_path: str,
                          template_name: str,
                          category: str,
                          platforms: List[str] = None) -> Dict[str, ExtractedMedia]:
        """
        Extract and optimize standalone plot images (matplotlib outputs)

        Args:
            plot_path: Path to plot PDF or PNG
            template_name: Template identifier
            category: Template category
            platforms: List of platforms to generate images for

        Returns:
            Dictionary mapping platform names to ExtractedMedia objects
        """
        if platforms is None:
            platforms = ['facebook', 'instagram', 'threads']

        plot_path = Path(plot_path)
        if not plot_path.exists():
            logger.error(f"Plot not found: {plot_path}")
            return {}

        results = {}

        try:
            # Load image
            if plot_path.suffix.lower() == '.pdf':
                if not self.has_fitz:
                    return self._extract_with_imagemagick(str(plot_path), template_name, category, platforms)

                # Extract from PDF
                doc = self.fitz.open(str(plot_path))
                page = doc[0]
                pix = page.get_pixmap(matrix=self.fitz.Matrix(3, 3))  # High resolution for plots
                img_data = pix.tobytes("png")
                base_image = Image.open(io.BytesIO(img_data))
                doc.close()
            else:
                # Direct image load
                base_image = Image.open(plot_path)

            # Generate platform versions
            for platform in platforms:
                try:
                    optimized = self._optimize_for_platform(
                        base_image,
                        platform,
                        f"{template_name}_plot",
                        category
                    )

                    if optimized:
                        alt_text = self._generate_alt_text(template_name, category, platform, is_plot=True)

                        media = ExtractedMedia(
                            image_path=optimized['path'],
                            platform=platform,
                            width=optimized['width'],
                            height=optimized['height'],
                            file_size=optimized['size'],
                            alt_text=alt_text,
                            source_pdf=str(plot_path),
                            page_number=1
                        )

                        results[platform] = media
                        logger.info(f"Generated {platform} plot: {optimized['path']}")

                except Exception as e:
                    logger.error(f"Error optimizing plot for {platform}: {e}")

        except Exception as e:
            logger.error(f"Error processing plot: {e}")

        return results

    def _optimize_for_platform(self,
                               image: Image.Image,
                               platform: str,
                               template_name: str,
                               category: str) -> Optional[Dict]:
        """
        Optimize image for specific platform requirements

        Args:
            image: PIL Image object
            platform: Target platform
            template_name: Template identifier
            category: Template category

        Returns:
            Dictionary with path, dimensions, and size
        """
        if platform not in self.PLATFORM_SPECS:
            logger.error(f"Unknown platform: {platform}")
            return None

        specs = self.PLATFORM_SPECS[platform]

        # Convert to RGB if needed
        if image.mode in ('RGBA', 'LA', 'P'):
            # Create white background
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[-1] if 'A' in image.mode else None)
            image = background

        # Calculate target dimensions
        width, height = image.size

        if specs['aspect_ratio']:
            target_ratio = specs['aspect_ratio'][0] / specs['aspect_ratio'][1]
            current_ratio = width / height

            if current_ratio > target_ratio:
                # Image is wider, crop width
                new_width = int(height * target_ratio)
                left = (width - new_width) // 2
                image = image.crop((left, 0, left + new_width, height))
            elif current_ratio < target_ratio:
                # Image is taller, crop height
                new_height = int(width / target_ratio)
                top = (height - new_height) // 2
                image = image.crop((0, top, width, top + new_height))

        # Resize if exceeds max dimensions
        width, height = image.size
        max_width = specs['max_width']
        max_height = specs['max_height']

        if width > max_width or height > max_height:
            image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)

        # Save with platform-specific format
        output_filename = f"{category}_{template_name}_{platform}.{specs['format'].lower()}"
        output_path = self.output_dir / output_filename

        # Save with quality optimization
        if specs['format'] == 'JPEG':
            image.save(output_path, 'JPEG', quality=85, optimize=True)
        else:
            image.save(output_path, 'PNG', optimize=True)

        # Check file size
        file_size = output_path.stat().st_size
        max_size = specs['max_size_mb'] * 1024 * 1024

        # If too large, reduce quality/size
        if file_size > max_size and specs['format'] == 'JPEG':
            logger.warning(f"Image too large ({file_size/1024/1024:.2f}MB), reducing quality")
            quality = 75
            while file_size > max_size and quality > 40:
                image.save(output_path, 'JPEG', quality=quality, optimize=True)
                file_size = output_path.stat().st_size
                quality -= 10

        width, height = image.size

        return {
            'path': str(output_path),
            'width': width,
            'height': height,
            'size': file_size
        }

    def _generate_alt_text(self,
                          template_name: str,
                          category: str,
                          platform: str,
                          is_plot: bool = False) -> str:
        """
        Generate accessibility alt text for images

        Args:
            template_name: Template identifier
            category: Template category
            platform: Target platform
            is_plot: Whether this is a plot or full document

        Returns:
            Alt text string
        """
        # Convert names to readable format
        readable_name = template_name.replace('_', ' ').replace('-', ' ').title()
        readable_category = category.replace('_', ' ').replace('-', ' ').title()

        if is_plot:
            alt_text = f"Computational visualization from {readable_name} in {readable_category}. "
            alt_text += "Scientific plot showing numerical results and data analysis."
        else:
            alt_text = f"LaTeX document preview for {readable_name} in {readable_category}. "
            alt_text += "Computational template with mathematical equations and code."

        # Platform-specific additions
        if platform == 'instagram':
            alt_text += " #ScienceVisualization #ComputationalScience"

        return alt_text

    def _extract_with_imagemagick(self,
                                  pdf_path: str,
                                  template_name: str,
                                  category: str,
                                  platforms: List[str]) -> Dict[str, ExtractedMedia]:
        """
        Fallback extraction using ImageMagick command-line tools

        Args:
            pdf_path: Path to PDF
            template_name: Template identifier
            category: Template category
            platforms: List of platforms

        Returns:
            Dictionary of extracted media
        """
        import subprocess

        results = {}

        try:
            # Convert first page to PNG at high resolution
            temp_png = self.output_dir / f"temp_{template_name}.png"

            cmd = [
                'convert',
                '-density', '300',
                f'{pdf_path}[0]',  # First page only
                '-quality', '90',
                str(temp_png)
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0 and temp_png.exists():
                # Load and process with PIL
                base_image = Image.open(temp_png)

                for platform in platforms:
                    optimized = self._optimize_for_platform(
                        base_image,
                        platform,
                        template_name,
                        category
                    )

                    if optimized:
                        alt_text = self._generate_alt_text(template_name, category, platform)

                        media = ExtractedMedia(
                            image_path=optimized['path'],
                            platform=platform,
                            width=optimized['width'],
                            height=optimized['height'],
                            file_size=optimized['size'],
                            alt_text=alt_text,
                            source_pdf=pdf_path,
                            page_number=1
                        )

                        results[platform] = media

                # Clean up temp file
                temp_png.unlink()

            else:
                logger.error(f"ImageMagick conversion failed: {result.stderr}")

        except FileNotFoundError:
            logger.error("ImageMagick (convert) not found. Cannot extract images.")
        except Exception as e:
            logger.error(f"Error with ImageMagick extraction: {e}")

        return results

    def create_composite_image(self,
                              template_name: str,
                              category: str,
                              pdf_path: str,
                              plot_paths: List[str],
                              platform: str = 'instagram') -> Optional[ExtractedMedia]:
        """
        Create a composite image combining document preview and plots

        Args:
            template_name: Template identifier
            category: Template category
            pdf_path: Path to main PDF
            plot_paths: List of plot image paths
            platform: Target platform

        Returns:
            ExtractedMedia object or None
        """
        if not self.has_fitz and not Path('convert').exists():
            logger.error("No image processing tools available")
            return None

        # Extract main document
        doc_images = self.extract_from_pdf(pdf_path, template_name, category, [platform])
        if platform not in doc_images:
            return None

        # If no plots, return document image
        if not plot_paths or len(plot_paths) == 0:
            return doc_images[platform]

        try:
            # Load document image
            doc_img = Image.open(doc_images[platform].image_path)

            # Load first plot
            plot_path = plot_paths[0]
            if Path(plot_path).suffix.lower() == '.pdf':
                plot_images = self.extract_plot_image(plot_path, template_name, category, [platform])
                if platform not in plot_images:
                    return doc_images[platform]
                plot_img = Image.open(plot_images[platform].image_path)
            else:
                plot_img = Image.open(plot_path)

            # Create composite (side-by-side or top-bottom based on platform)
            if platform == 'instagram':
                # Vertical layout for Instagram
                total_width = max(doc_img.width, plot_img.width)
                total_height = doc_img.height + plot_img.height

                composite = Image.new('RGB', (total_width, total_height), (255, 255, 255))

                # Center images
                doc_x = (total_width - doc_img.width) // 2
                plot_x = (total_width - plot_img.width) // 2

                composite.paste(doc_img, (doc_x, 0))
                composite.paste(plot_img, (plot_x, doc_img.height))

            else:
                # Side-by-side for other platforms
                total_width = doc_img.width + plot_img.width
                total_height = max(doc_img.height, plot_img.height)

                composite = Image.new('RGB', (total_width, total_height), (255, 255, 255))

                composite.paste(doc_img, (0, 0))
                composite.paste(plot_img, (doc_img.width, 0))

            # Optimize composite
            optimized = self._optimize_for_platform(
                composite,
                platform,
                f"{template_name}_composite",
                category
            )

            if optimized:
                alt_text = self._generate_alt_text(template_name, category, platform) + " Includes visualization."

                return ExtractedMedia(
                    image_path=optimized['path'],
                    platform=platform,
                    width=optimized['width'],
                    height=optimized['height'],
                    file_size=optimized['size'],
                    alt_text=alt_text,
                    source_pdf=pdf_path,
                    page_number=1
                )

        except Exception as e:
            logger.error(f"Error creating composite: {e}")
            return doc_images[platform]

        return None


def main():
    """Test media extraction"""
    extractor = MediaExtractor()

    # Test with a sample PDF
    test_pdf = "/home/user/latex-templates/templates/acoustics/sound_propagation.pdf"

    if Path(test_pdf).exists():
        print(f"Testing extraction from: {test_pdf}")

        results = extractor.extract_from_pdf(
            test_pdf,
            "sound_propagation",
            "acoustics",
            platforms=['facebook', 'instagram', 'threads']
        )

        print(f"\nExtracted {len(results)} images:")
        for platform, media in results.items():
            print(f"\n{platform.upper()}:")
            print(f"  Path: {media.image_path}")
            print(f"  Dimensions: {media.width}x{media.height}")
            print(f"  Size: {media.file_size / 1024:.2f} KB")
            print(f"  Alt text: {media.alt_text}")

    else:
        print(f"Test PDF not found: {test_pdf}")


if __name__ == "__main__":
    main()
