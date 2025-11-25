#!/usr/bin/env python3
"""
LaTeX Template Discovery and Indexing Module

Scans the latex-templates directory, extracts metadata from .tex files,
catalogs visualizations, and maintains a searchable template index.
"""

import os
import re
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class TemplateMetadata:
    """Metadata for a LaTeX template"""
    category: str
    template_name: str
    tex_file: str
    pdf_file: Optional[str]
    plot_files: List[str]
    title: str
    author: str
    abstract: str
    packages: List[str]
    github_url: str
    cocalc_url: str
    has_pythontex: bool
    has_sagetex: bool
    has_knitr: bool
    file_size: int
    last_modified: str
    complexity_score: int  # 1-5 based on content analysis

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)


class TemplateScanner:
    """Scans and indexes LaTeX templates"""

    def __init__(self,
                 templates_dir: str = "/home/user/latex-templates/templates",
                 github_base: str = "https://github.com/Ok-landscape/computational-pipeline",
                 cocalc_base: str = "https://cocalc.com/github/Ok-landscape/computational-pipeline"):
        """
        Initialize the template scanner

        Args:
            templates_dir: Root directory containing template categories
            github_base: Base GitHub repository URL
            cocalc_base: Base CoCalc viewer URL
        """
        self.templates_dir = Path(templates_dir)
        self.github_base = github_base
        self.cocalc_base = cocalc_base
        self.index_file = Path("/home/user/computational-pipeline/social-media-automation/data/template_index.json")
        self.templates: Dict[str, List[TemplateMetadata]] = {}

        # Ensure data directory exists
        self.index_file.parent.mkdir(parents=True, exist_ok=True)

    def scan_all_templates(self) -> Dict[str, List[TemplateMetadata]]:
        """
        Scan all template categories and build complete index

        Returns:
            Dictionary mapping category names to lists of template metadata
        """
        logger.info(f"Scanning templates in {self.templates_dir}")

        if not self.templates_dir.exists():
            logger.error(f"Templates directory not found: {self.templates_dir}")
            return {}

        categories = [d for d in self.templates_dir.iterdir() if d.is_dir()]
        logger.info(f"Found {len(categories)} categories")

        for category_dir in sorted(categories):
            category_name = category_dir.name
            logger.info(f"Scanning category: {category_name}")

            templates = self.scan_category(category_dir)
            if templates:
                self.templates[category_name] = templates
                logger.info(f"  Found {len(templates)} templates in {category_name}")

        total_templates = sum(len(t) for t in self.templates.values())
        logger.info(f"Total templates indexed: {total_templates}")

        return self.templates

    def scan_category(self, category_dir: Path) -> List[TemplateMetadata]:
        """
        Scan a single category directory

        Args:
            category_dir: Path to category directory

        Returns:
            List of template metadata objects
        """
        templates = []
        tex_files = list(category_dir.glob("*.tex"))

        for tex_file in tex_files:
            try:
                metadata = self.extract_metadata(tex_file, category_dir)
                if metadata:
                    templates.append(metadata)
            except Exception as e:
                logger.error(f"Error processing {tex_file}: {e}")

        return templates

    def extract_metadata(self, tex_file: Path, category_dir: Path) -> Optional[TemplateMetadata]:
        """
        Extract metadata from a .tex file

        Args:
            tex_file: Path to .tex file
            category_dir: Parent category directory

        Returns:
            TemplateMetadata object or None if extraction fails
        """
        try:
            content = tex_file.read_text(encoding='utf-8', errors='ignore')
        except Exception as e:
            logger.error(f"Could not read {tex_file}: {e}")
            return None

        category = category_dir.name
        template_name = tex_file.stem

        # Extract title
        title_match = re.search(r'\\title\{([^}]+)\}', content)
        title = title_match.group(1) if title_match else self._generate_title(template_name)

        # Clean up title (remove LaTeX commands)
        title = re.sub(r'\\\\', ' ', title)
        title = re.sub(r'\\[a-zA-Z]+\{([^}]*)\}', r'\1', title)

        # Extract author
        author_match = re.search(r'\\author\{([^}]+)\}', content)
        author = author_match.group(1) if author_match else "Computational Science Department"

        # Extract abstract
        abstract_match = re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}', content, re.DOTALL)
        abstract = abstract_match.group(1).strip() if abstract_match else self._generate_abstract(title, category)

        # Clean abstract
        abstract = re.sub(r'\n+', ' ', abstract)
        abstract = re.sub(r'\s+', ' ', abstract)
        abstract = abstract[:500]  # Limit length

        # Extract packages
        packages = re.findall(r'\\usepackage(?:\[.*?\])?\{([^}]+)\}', content)

        # Check for computational packages
        has_pythontex = 'pythontex' in packages
        has_sagetex = 'sagetex' in packages
        has_knitr = tex_file.suffix == '.Rnw'

        # Find associated files
        pdf_file = category_dir / f"{template_name}.pdf"
        pdf_path = str(pdf_file) if pdf_file.exists() else None

        # Find plot files
        plot_files = []
        for ext in ['*.pdf', '*.png']:
            plots = list(category_dir.glob(f"{template_name}_*{ext[1:]}"))
            plot_files.extend([str(p) for p in plots])

        # Generate URLs
        github_url = f"{self.github_base}/tree/main/latex-templates/templates/{category}/{tex_file.name}"
        cocalc_url = f"{self.cocalc_base}/tree/main/latex-templates/templates/{category}/{tex_file.name}"

        # File metadata
        file_size = tex_file.stat().st_size
        last_modified = datetime.fromtimestamp(tex_file.stat().st_mtime).isoformat()

        # Calculate complexity score
        complexity_score = self._calculate_complexity(content, packages)

        return TemplateMetadata(
            category=category,
            template_name=template_name,
            tex_file=str(tex_file),
            pdf_file=pdf_path,
            plot_files=plot_files,
            title=title,
            author=author,
            abstract=abstract,
            packages=packages,
            github_url=github_url,
            cocalc_url=cocalc_url,
            has_pythontex=has_pythontex,
            has_sagetex=has_sagetex,
            has_knitr=has_knitr,
            file_size=file_size,
            last_modified=last_modified,
            complexity_score=complexity_score
        )

    def _generate_title(self, template_name: str) -> str:
        """Generate a human-readable title from filename"""
        # Convert underscores to spaces and title case
        title = template_name.replace('_', ' ').replace('-', ' ')
        title = ' '.join(word.capitalize() for word in title.split())
        return title

    def _generate_abstract(self, title: str, category: str) -> str:
        """Generate a generic abstract if none exists"""
        return f"Computational analysis of {title.lower()} using advanced numerical methods and visualization techniques in {category.replace('-', ' ')}."

    def _calculate_complexity(self, content: str, packages: List[str]) -> int:
        """
        Calculate template complexity score (1-5)

        Factors:
        - Number of equations
        - Computational packages
        - Code blocks
        - Length
        """
        score = 1

        # Check for equations
        equation_count = len(re.findall(r'\\begin\{equation\}|\\begin\{align\}|\$\$', content))
        if equation_count > 5:
            score += 1
        if equation_count > 10:
            score += 1

        # Check for computational packages
        computational_packages = ['pythontex', 'sagetex', 'listings', 'minted']
        if any(pkg in packages for pkg in computational_packages):
            score += 1

        # Check for code blocks
        code_blocks = len(re.findall(r'\\begin\{(pycode|sageblock|lstlisting)', content))
        if code_blocks > 3:
            score += 1

        return min(score, 5)

    def save_index(self, filepath: Optional[Path] = None):
        """
        Save the template index to JSON file

        Args:
            filepath: Optional custom filepath for index
        """
        if filepath is None:
            filepath = self.index_file

        # Convert to serializable format
        index_data = {
            'generated_at': datetime.now().isoformat(),
            'total_categories': len(self.templates),
            'total_templates': sum(len(t) for t in self.templates.values()),
            'categories': {}
        }

        for category, templates in self.templates.items():
            index_data['categories'][category] = [t.to_dict() for t in templates]

        with open(filepath, 'w') as f:
            json.dump(index_data, f, indent=2)

        logger.info(f"Index saved to {filepath}")

    def load_index(self, filepath: Optional[Path] = None) -> bool:
        """
        Load template index from JSON file

        Args:
            filepath: Optional custom filepath for index

        Returns:
            True if successful, False otherwise
        """
        if filepath is None:
            filepath = self.index_file

        if not filepath.exists():
            logger.warning(f"Index file not found: {filepath}")
            return False

        try:
            with open(filepath, 'r') as f:
                index_data = json.load(f)

            self.templates = {}
            for category, templates_data in index_data['categories'].items():
                templates = []
                for t_data in templates_data:
                    templates.append(TemplateMetadata(**t_data))
                self.templates[category] = templates

            logger.info(f"Loaded {index_data['total_templates']} templates from index")
            return True

        except Exception as e:
            logger.error(f"Error loading index: {e}")
            return False

    def get_template_by_name(self, category: str, template_name: str) -> Optional[TemplateMetadata]:
        """Get a specific template by category and name"""
        if category not in self.templates:
            return None

        for template in self.templates[category]:
            if template.template_name == template_name:
                return template

        return None

    def get_random_template(self, exclude_recent: Optional[List[str]] = None) -> Optional[TemplateMetadata]:
        """
        Get a random template, optionally excluding recently used ones

        Args:
            exclude_recent: List of template names to exclude

        Returns:
            Random TemplateMetadata object
        """
        import random

        all_templates = []
        for templates in self.templates.values():
            all_templates.extend(templates)

        if exclude_recent:
            all_templates = [t for t in all_templates if t.template_name not in exclude_recent]

        if not all_templates:
            return None

        return random.choice(all_templates)

    def get_templates_by_category(self, category: str) -> List[TemplateMetadata]:
        """Get all templates in a category"""
        return self.templates.get(category, [])

    def search_templates(self, query: str) -> List[TemplateMetadata]:
        """
        Search templates by title, abstract, or category

        Args:
            query: Search string

        Returns:
            List of matching templates
        """
        query_lower = query.lower()
        results = []

        for templates in self.templates.values():
            for template in templates:
                if (query_lower in template.title.lower() or
                    query_lower in template.abstract.lower() or
                    query_lower in template.category.lower()):
                    results.append(template)

        return results

    def get_statistics(self) -> Dict:
        """Get statistics about the template collection"""
        stats = {
            'total_categories': len(self.templates),
            'total_templates': sum(len(t) for t in self.templates.values()),
            'templates_with_plots': 0,
            'templates_with_pythontex': 0,
            'templates_with_sagetex': 0,
            'templates_with_knitr': 0,
            'category_distribution': {},
            'complexity_distribution': {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        }

        for category, templates in self.templates.items():
            stats['category_distribution'][category] = len(templates)

            for template in templates:
                if template.plot_files:
                    stats['templates_with_plots'] += 1
                if template.has_pythontex:
                    stats['templates_with_pythontex'] += 1
                if template.has_sagetex:
                    stats['templates_with_sagetex'] += 1
                if template.has_knitr:
                    stats['templates_with_knitr'] += 1

                stats['complexity_distribution'][template.complexity_score] += 1

        return stats


def main():
    """Main function for testing"""
    scanner = TemplateScanner()

    # Scan all templates
    print("Scanning templates...")
    templates = scanner.scan_all_templates()

    # Save index
    scanner.save_index()

    # Display statistics
    stats = scanner.get_statistics()
    print("\n" + "="*60)
    print("Template Collection Statistics")
    print("="*60)
    print(f"Total Categories: {stats['total_categories']}")
    print(f"Total Templates: {stats['total_templates']}")
    print(f"Templates with Plots: {stats['templates_with_plots']}")
    print(f"Templates with PythonTeX: {stats['templates_with_pythontex']}")
    print(f"Templates with SageTeX: {stats['templates_with_sagetex']}")
    print(f"Templates with Knitr: {stats['templates_with_knitr']}")

    print("\nComplexity Distribution:")
    for level, count in sorted(stats['complexity_distribution'].items()):
        print(f"  Level {level}: {count} templates")

    print("\nTop 10 Categories by Template Count:")
    sorted_cats = sorted(stats['category_distribution'].items(), key=lambda x: x[1], reverse=True)
    for cat, count in sorted_cats[:10]:
        print(f"  {cat}: {count} templates")

    # Show sample template
    print("\n" + "="*60)
    print("Sample Template:")
    print("="*60)
    random_template = scanner.get_random_template()
    if random_template:
        print(f"Category: {random_template.category}")
        print(f"Name: {random_template.template_name}")
        print(f"Title: {random_template.title}")
        print(f"Abstract: {random_template.abstract[:200]}...")
        print(f"CoCalc URL: {random_template.cocalc_url}")
        print(f"Has Plots: {len(random_template.plot_files) > 0}")
        print(f"Complexity: {random_template.complexity_score}/5")


if __name__ == "__main__":
    main()
