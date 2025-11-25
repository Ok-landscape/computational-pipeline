"""
Notebook Content Extractor Module

Extracts images and content from Jupyter notebooks.
"""

import json
import base64
from pathlib import Path
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class NotebookContentExtractor:
    """Extracts images and content from Jupyter notebooks."""

    def __init__(self, notebook_path: str):
        """
        Initialize the NotebookContentExtractor.

        Args:
            notebook_path: Path to the Jupyter notebook (.ipynb file)
        """
        self.notebook_path = Path(notebook_path)

        if not self.notebook_path.exists():
            raise FileNotFoundError(f"Notebook not found: {notebook_path}")

        self.notebook_data = self._load_notebook()
        self.notebook_name = self.notebook_path.stem

    def _load_notebook(self) -> dict:
        """Load and parse the notebook JSON."""
        try:
            with open(self.notebook_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse notebook JSON: {e}")
            raise

    def extract_images(self, output_dir: Optional[str] = None) -> List[Dict[str, str]]:
        """
        Extract all images from notebook output cells.

        Args:
            output_dir: Directory to save images (optional)

        Returns:
            List of dictionaries containing image metadata
        """
        images = []

        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
        else:
            output_path = None

        # Iterate through cells
        for cell_idx, cell in enumerate(self.notebook_data.get('cells', [])):
            # Check if cell has outputs
            if cell.get('cell_type') == 'code' and 'outputs' in cell:
                for output_idx, output in enumerate(cell['outputs']):
                    # Check for image data in output
                    if 'data' in output:
                        data = output['data']

                        # Check for various image formats
                        for mime_type in ['image/png', 'image/jpeg', 'image/jpg', 'image/svg+xml']:
                            if mime_type in data:
                                image_data = data[mime_type]

                                # Determine file extension
                                if mime_type == 'image/svg+xml':
                                    ext = 'svg'
                                    is_base64 = False
                                elif mime_type == 'image/jpeg' or mime_type == 'image/jpg':
                                    ext = 'jpg'
                                    is_base64 = True
                                else:  # image/png
                                    ext = 'png'
                                    is_base64 = True

                                # Generate filename
                                filename = f"{self.notebook_name}_cell{cell_idx}_output{output_idx}.{ext}"

                                image_info = {
                                    'filename': filename,
                                    'cell_index': cell_idx,
                                    'output_index': output_idx,
                                    'mime_type': mime_type,
                                    'extension': ext,
                                }

                                # Save image if output directory specified
                                if output_path:
                                    filepath = output_path / filename

                                    try:
                                        if is_base64:
                                            # Decode base64 and save
                                            img_bytes = base64.b64decode(image_data)
                                            with open(filepath, 'wb') as img_file:
                                                img_file.write(img_bytes)
                                        else:
                                            # Save SVG as text
                                            with open(filepath, 'w', encoding='utf-8') as img_file:
                                                img_file.write(image_data)

                                        image_info['saved_path'] = str(filepath)
                                        logger.info(f"Saved image: {filename}")

                                    except Exception as e:
                                        logger.error(f"Failed to save image {filename}: {e}")
                                        image_info['error'] = str(e)

                                images.append(image_info)

        logger.info(f"Extracted {len(images)} images from {self.notebook_name}")
        return images

    def extract_markdown_text(self) -> List[str]:
        """
        Extract all markdown cell content.

        Returns:
            List of markdown cell contents
        """
        markdown_cells = []

        for cell in self.notebook_data.get('cells', []):
            if cell.get('cell_type') == 'markdown':
                source = cell.get('source', [])

                # Source can be a string or list of strings
                if isinstance(source, list):
                    content = ''.join(source)
                else:
                    content = source

                markdown_cells.append(content)

        logger.info(f"Extracted {len(markdown_cells)} markdown cells")
        return markdown_cells

    def get_notebook_title(self) -> Optional[str]:
        """
        Extract the notebook title from the first markdown cell or metadata.

        Returns:
            Notebook title or None
        """
        # Check metadata first
        metadata = self.notebook_data.get('metadata', {})
        if 'title' in metadata:
            return metadata['title']

        # Look for first H1 heading in markdown cells
        markdown_cells = self.extract_markdown_text()
        if markdown_cells:
            first_cell = markdown_cells[0]
            lines = first_cell.split('\n')
            for line in lines:
                # Check for H1 heading
                if line.strip().startswith('# '):
                    return line.strip()[2:].strip()

        # Fallback to notebook filename
        return self.notebook_name.replace('_', ' ').title()

    def get_image_count(self) -> int:
        """Get the total number of images in the notebook."""
        return len(self.extract_images())

    def has_images(self) -> bool:
        """Check if the notebook contains any images."""
        return self.get_image_count() > 0


def main():
    """Test the NotebookContentExtractor."""
    import sys

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Test with a sample notebook
    test_notebook = "/home/user/computational-pipeline/social-media-automation/repo-data/notebooks/published/finite_element_method_heat_transfer.ipynb"
    output_dir = "/home/user/computational-pipeline/social-media-automation/test_images"

    try:
        extractor = NotebookContentExtractor(test_notebook)

        print(f"\n=== Analyzing: {extractor.notebook_name} ===")
        print(f"Title: {extractor.get_notebook_title()}")
        print(f"Has images: {extractor.has_images()}")

        print("\n=== Extracting Images ===")
        images = extractor.extract_images(output_dir=output_dir)
        print(f"Total images: {len(images)}")

        if images:
            print("\nImage details:")
            for img in images:
                print(f"  - {img['filename']} ({img['mime_type']})")
                if 'saved_path' in img:
                    print(f"    Saved to: {img['saved_path']}")

        print("\n=== Markdown Cells ===")
        markdown = extractor.extract_markdown_text()
        print(f"Total markdown cells: {len(markdown)}")

        if markdown:
            print(f"\nFirst markdown cell preview:")
            print(markdown[0][:200] + "..." if len(markdown[0]) > 200 else markdown[0])

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
