#!/usr/bin/env python3
"""
Page Router Module

Routes templates and notebooks to appropriate Facebook pages based on content type.
Implements dual-page strategy:
- CoCalc page (698630966948910): All content
- SageMath page (26593144945): SageMath-specific content only
"""

import logging
from typing import List, Dict, Optional
from pathlib import Path
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class PageRoute:
    """Represents a routing decision for content"""
    page_id: str
    page_name: str
    reason: str
    priority: int = 5


class PageRouter:
    """Routes content to appropriate Facebook pages"""

    # Page configurations
    PAGES = {
        'cocalc': {
            'id': '698630966948910',
            'name': 'CoCalc',
            'accepts': ['all']  # Accepts all content types
        },
        'sagemath': {
            'id': '26593144945',
            'name': 'SageMath',
            'accepts': ['sagemath', 'sagetex', 'mathematics']  # Only math content
        }
    }

    # Keywords that indicate SageMath relevance
    SAGEMATH_KEYWORDS = [
        'sage', 'sagetex', 'sagemath', 'symbolic', 'algebra',
        'number theory', 'combinatorics', 'topology', 'pure math',
        'abstract algebra', 'group theory', 'ring theory'
    ]

    # Categories that map to SageMath
    SAGEMATH_CATEGORIES = [
        'mathematics', 'pure-mathematics', 'algebra', 'number-theory',
        'topology', 'combinatorics', 'graph-theory', 'symbolic-computation'
    ]

    def __init__(self):
        """Initialize page router"""
        logger.info("Page Router initialized")

    def route_template(self, template_metadata: Dict) -> List[PageRoute]:
        """
        Route a LaTeX template to appropriate pages

        Args:
            template_metadata: Template metadata dict with keys:
                - template_name: str
                - category: str
                - has_sagetex: bool
                - has_pythontex: bool
                - description: str (optional)

        Returns:
            List of PageRoute objects (pages to post to)
        """
        routes = []

        # CoCalc page always gets the content
        routes.append(PageRoute(
            page_id=self.PAGES['cocalc']['id'],
            page_name=self.PAGES['cocalc']['name'],
            reason="CoCalc page receives all template content",
            priority=10
        ))

        # Check if SageMath page should also get it
        if self._is_sagemath_relevant(template_metadata):
            routes.append(PageRoute(
                page_id=self.PAGES['sagemath']['id'],
                page_name=self.PAGES['sagemath']['name'],
                reason="Template uses SageTeX or is math-focused",
                priority=8
            ))

        logger.info(f"Template '{template_metadata.get('template_name')}' routes to {len(routes)} page(s)")
        return routes

    def route_notebook(self, notebook_metadata: Dict) -> List[PageRoute]:
        """
        Route a computational notebook to appropriate pages

        Args:
            notebook_metadata: Notebook metadata dict with keys:
                - basename: str
                - description: str (optional)
                - tags: List[str] (optional)

        Returns:
            List of PageRoute objects (pages to post to)
        """
        routes = []

        # CoCalc page always gets the content
        routes.append(PageRoute(
            page_id=self.PAGES['cocalc']['id'],
            page_name=self.PAGES['cocalc']['name'],
            reason="CoCalc page receives all notebook content",
            priority=10
        ))

        # Check if SageMath page should also get it
        if self._is_notebook_sagemath_relevant(notebook_metadata):
            routes.append(PageRoute(
                page_id=self.PAGES['sagemath']['id'],
                page_name=self.PAGES['sagemath']['name'],
                reason="Notebook contains SageMath/mathematical content",
                priority=8
            ))

        logger.info(f"Notebook '{notebook_metadata.get('basename')}' routes to {len(routes)} page(s)")
        return routes

    def _is_sagemath_relevant(self, template_metadata: Dict) -> bool:
        """
        Determine if a template is relevant to SageMath page

        Args:
            template_metadata: Template metadata

        Returns:
            True if relevant to SageMath
        """
        # Check if uses SageTeX
        if template_metadata.get('has_sagetex', False):
            logger.debug(f"Template uses SageTeX - relevant to SageMath page")
            return True

        # Check category
        category = template_metadata.get('category', '').lower()
        if any(cat in category for cat in self.SAGEMATH_CATEGORIES):
            logger.debug(f"Template category '{category}' matches SageMath")
            return True

        # Check template name and description
        searchable_text = ' '.join([
            template_metadata.get('template_name', ''),
            template_metadata.get('description', ''),
            category
        ]).lower()

        if any(keyword in searchable_text for keyword in self.SAGEMATH_KEYWORDS):
            logger.debug(f"Template contains SageMath keywords")
            return True

        return False

    def _is_notebook_sagemath_relevant(self, notebook_metadata: Dict) -> bool:
        """
        Determine if a notebook is relevant to SageMath page

        Args:
            notebook_metadata: Notebook metadata

        Returns:
            True if relevant to SageMath
        """
        # Check filename for SageMath indicators
        basename = notebook_metadata.get('basename', '').lower()

        if any(keyword in basename for keyword in ['sage', 'symbolic', 'algebra', 'math']):
            logger.debug(f"Notebook name contains SageMath keywords")
            return True

        # Check tags if available
        tags = notebook_metadata.get('tags', [])
        if tags:
            tag_text = ' '.join(tags).lower()
            if any(keyword in tag_text for keyword in self.SAGEMATH_KEYWORDS):
                logger.debug(f"Notebook tags match SageMath")
                return True

        # Check description
        description = notebook_metadata.get('description', '').lower()
        if any(keyword in description for keyword in self.SAGEMATH_KEYWORDS):
            logger.debug(f"Notebook description contains SageMath keywords")
            return True

        return False

    def get_page_info(self, page_id: str) -> Optional[Dict]:
        """
        Get information about a page by ID

        Args:
            page_id: Facebook page ID

        Returns:
            Page info dict or None
        """
        for page_key, page_data in self.PAGES.items():
            if page_data['id'] == page_id:
                return page_data
        return None

    def get_all_pages(self) -> Dict[str, Dict]:
        """
        Get all configured pages

        Returns:
            Dictionary of page configurations
        """
        return self.PAGES

    def should_spread_across_days(self, routes: List[PageRoute]) -> bool:
        """
        Determine if content routed to multiple pages should be spread across days

        Args:
            routes: List of page routes

        Returns:
            True if content should be spread across different days
        """
        # If content goes to multiple pages, spread it out
        return len(routes) > 1


def main():
    """Test the page router"""
    import logging
    logging.basicConfig(level=logging.INFO)

    router = PageRouter()

    # Test template routing
    print("\n" + "="*60)
    print("Testing Template Routing")
    print("="*60)

    test_templates = [
        {
            'template_name': 'physics_simulation.tex',
            'category': 'physics',
            'has_sagetex': False,
            'has_pythontex': True,
            'description': 'Physics simulation using PythonTeX'
        },
        {
            'template_name': 'algebra_proof.tex',
            'category': 'mathematics',
            'has_sagetex': True,
            'has_pythontex': False,
            'description': 'Abstract algebra proof using SageMath'
        },
        {
            'template_name': 'number_theory.tex',
            'category': 'pure-mathematics/number-theory',
            'has_sagetex': True,
            'has_pythontex': False,
            'description': 'Number theory computations'
        },
        {
            'template_name': 'engineering_report.tex',
            'category': 'engineering',
            'has_sagetex': False,
            'has_pythontex': True,
            'description': 'Engineering analysis report'
        }
    ]

    for template in test_templates:
        print(f"\nTemplate: {template['template_name']}")
        print(f"  Category: {template['category']}")
        print(f"  SageTeX: {template['has_sagetex']}")
        routes = router.route_template(template)
        print(f"  Routes to {len(routes)} page(s):")
        for route in routes:
            print(f"    - {route.page_name} ({route.page_id})")
            print(f"      Reason: {route.reason}")

    # Test notebook routing
    print("\n" + "="*60)
    print("Testing Notebook Routing")
    print("="*60)

    test_notebooks = [
        {
            'basename': 'sage_symbolic_algebra',
            'description': 'Symbolic algebra computations using SageMath',
            'tags': ['sagemath', 'algebra']
        },
        {
            'basename': 'python_data_analysis',
            'description': 'Data analysis with Python and pandas',
            'tags': ['python', 'data-science']
        },
        {
            'basename': 'topology_visualization',
            'description': 'Topology concepts and visualizations',
            'tags': ['mathematics', 'topology']
        }
    ]

    for notebook in test_notebooks:
        print(f"\nNotebook: {notebook['basename']}")
        print(f"  Description: {notebook['description']}")
        print(f"  Tags: {notebook.get('tags', [])}")
        routes = router.route_notebook(notebook)
        print(f"  Routes to {len(routes)} page(s):")
        for route in routes:
            print(f"    - {route.page_name} ({route.page_id})")
            print(f"      Reason: {route.reason}")

        if router.should_spread_across_days(routes):
            print("  ⚠ Should spread across different days")


if __name__ == "__main__":
    main()
