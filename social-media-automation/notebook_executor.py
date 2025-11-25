#!/usr/bin/env python3
"""
Notebook Executor - Execute notebooks to generate outputs and images

Executes Jupyter notebooks and saves them with outputs for social media posting.
"""

import sys
import os
import logging
from pathlib import Path
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor, CellExecutionError
import tempfile
import shutil

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class NotebookExecutor:
    """Execute Jupyter notebooks and save with outputs"""

    def __init__(self, timeout=300, kernel_name='python3'):
        """
        Initialize executor

        Args:
            timeout: Maximum execution time per cell in seconds (default: 300)
            kernel_name: Jupyter kernel to use (default: 'python3')
        """
        self.timeout = timeout
        self.kernel_name = kernel_name

        # Create executor
        self.ep = ExecutePreprocessor(
            timeout=self.timeout,
            kernel_name=self.kernel_name,
            allow_errors=False  # Stop on first error
        )

        logger.info(f"Notebook executor initialized (timeout={timeout}s, kernel={kernel_name})")

    def execute_notebook(self, notebook_path: str, output_path: str = None, backup=True) -> dict:
        """
        Execute a notebook and save with outputs

        Args:
            notebook_path: Path to input notebook
            output_path: Path for output notebook (default: overwrite input)
            backup: Create backup of original notebook before overwriting (default: True)

        Returns:
            Dictionary with execution results:
                - success: bool
                - notebook_path: Path to output notebook
                - output_count: Number of outputs generated
                - image_count: Number of images generated
                - error: Error message if failed
        """
        notebook_path = Path(notebook_path)

        if not notebook_path.exists():
            logger.error(f"Notebook not found: {notebook_path}")
            return {
                'success': False,
                'error': 'File not found',
                'notebook_path': str(notebook_path)
            }

        if output_path is None:
            output_path = notebook_path
        else:
            output_path = Path(output_path)

        logger.info(f"Executing notebook: {notebook_path.name}")

        try:
            # Read notebook
            with open(notebook_path, 'r') as f:
                nb = nbformat.read(f, as_version=4)

            # Create backup if overwriting
            if backup and output_path == notebook_path:
                backup_path = notebook_path.with_suffix('.ipynb.bak')
                shutil.copy2(notebook_path, backup_path)
                logger.info(f"  Backup created: {backup_path.name}")

            # Execute notebook
            logger.info(f"  Executing cells...")
            self.ep.preprocess(nb, {'metadata': {'path': str(notebook_path.parent)}})

            # Count outputs
            output_count = 0
            image_count = 0

            for cell in nb.cells:
                if cell.cell_type == 'code':
                    if cell.get('outputs'):
                        output_count += len(cell.outputs)

                        for output in cell.outputs:
                            if output.get('output_type') in ['display_data', 'execute_result']:
                                data = output.get('data', {})
                                if 'image/png' in data or 'image/jpeg' in data:
                                    image_count += 1

            logger.info(f"  Generated {output_count} outputs, {image_count} images")

            # Save executed notebook
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                nbformat.write(nb, f)

            logger.info(f"  Saved to: {output_path}")

            return {
                'success': True,
                'notebook_path': str(output_path),
                'output_count': output_count,
                'image_count': image_count
            }

        except CellExecutionError as e:
            logger.error(f"  Execution error in cell: {e}")
            return {
                'success': False,
                'error': f'Cell execution error: {str(e)}',
                'notebook_path': str(notebook_path)
            }

        except Exception as e:
            logger.error(f"  Error: {e}")
            return {
                'success': False,
                'error': str(e),
                'notebook_path': str(notebook_path)
            }

    def execute_batch(self, notebook_paths: list, output_dir: str = None) -> dict:
        """
        Execute multiple notebooks

        Args:
            notebook_paths: List of notebook paths
            output_dir: Optional output directory (default: overwrite originals)

        Returns:
            Dictionary with batch results:
                - total: Total notebooks processed
                - success: Number of successful executions
                - failed: Number of failed executions
                - results: List of individual results
        """
        results = []
        success_count = 0
        failed_count = 0

        for nb_path in notebook_paths:
            if output_dir:
                output_path = Path(output_dir) / Path(nb_path).name
            else:
                output_path = None

            result = self.execute_notebook(nb_path, output_path)
            results.append(result)

            if result['success']:
                success_count += 1
            else:
                failed_count += 1

        return {
            'total': len(notebook_paths),
            'success': success_count,
            'failed': failed_count,
            'results': results
        }


def main():
    """Test executor on a single notebook"""
    import argparse

    parser = argparse.ArgumentParser(description='Execute Jupyter notebooks')
    parser.add_argument('notebook', help='Path to notebook file')
    parser.add_argument('-o', '--output', help='Output path (default: overwrite input)')
    parser.add_argument('-t', '--timeout', type=int, default=300, help='Execution timeout in seconds')
    parser.add_argument('--no-backup', action='store_true', help='Skip backup creation')

    args = parser.parse_args()

    executor = NotebookExecutor(timeout=args.timeout)
    result = executor.execute_notebook(
        args.notebook,
        output_path=args.output,
        backup=not args.no_backup
    )

    if result['success']:
        print("\n" + "=" * 80)
        print("SUCCESS")
        print("=" * 80)
        print(f"Notebook executed successfully")
        print(f"Outputs: {result['output_count']}")
        print(f"Images: {result['image_count']}")
        print(f"Saved to: {result['notebook_path']}")
        print("=" * 80)
        sys.exit(0)
    else:
        print("\n" + "=" * 80)
        print("FAILED")
        print("=" * 80)
        print(f"Error: {result['error']}")
        print("=" * 80)
        sys.exit(1)


if __name__ == '__main__':
    main()
