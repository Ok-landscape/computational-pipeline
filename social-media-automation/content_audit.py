#!/usr/bin/env python3
"""
Comprehensive Content Audit

Analyzes all notebooks and templates to determine:
1. Which have social media posts
2. Which have images
3. Quality of existing posts (LaTeX symbols vs Unicode)
4. What needs to be generated
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple
import sys

sys.path.insert(0, '/home/user/computational-pipeline/social-media-automation')

from notebook_scanner import NotebookScanner
from template_scanner import TemplateScanner
from notebook_content_extractor import NotebookContentExtractor
from post_text_parser import PostTextParser


class ContentAuditor:
    """Audit all content sources for social media readiness"""

    def __init__(self):
        self.notebooks_dir = "/home/user/computational-pipeline/social-media-automation/repo-data/notebooks"
        self.templates_dir = "/home/user/latex-templates/templates"
        self.posts_dir = "/home/user/computational-pipeline/social-media-automation/repo-data/output/social_posts"
        self.results = {
            'notebooks': {
                'total': 0,
                'with_posts': 0,
                'with_images': 0,
                'with_unicode_math': 0,
                'with_latex_symbols': 0,
                'ready_to_post': 0,
                'needs_work': []
            },
            'templates': {
                'total': 0,
                'with_posts': 0,
                'ready_to_post': 0,
                'needs_generation': []
            }
        }

    def has_latex_symbols(self, text: str) -> bool:
        """Check if text contains LaTeX math symbols"""
        latex_patterns = [
            r'\\[a-zA-Z]+',  # LaTeX commands like \alpha, \beta
            r'\$.*?\$',       # Inline math $...$
            r'\^[{]?[a-zA-Z0-9]+[}]?',  # Superscripts ^2
            r'_[{]?[a-zA-Z0-9]+[}]?',   # Subscripts _i
        ]
        return any(re.search(pattern, text) for pattern in latex_patterns)

    def has_unicode_math(self, text: str) -> bool:
        """Check if text contains Unicode mathematical symbols"""
        # Common Unicode math ranges
        unicode_math_chars = [
            range(0x2200, 0x22FF),  # Mathematical Operators
            range(0x2100, 0x214F),  # Letterlike Symbols
            range(0x0370, 0x03FF),  # Greek
            range(0x2070, 0x209F),  # Superscripts and Subscripts
        ]

        for char in text:
            code = ord(char)
            for char_range in unicode_math_chars:
                if code in char_range:
                    return True
        return False

    def audit_notebooks(self) -> Dict:
        """Audit all notebooks"""
        print("\n" + "=" * 80)
        print("AUDITING NOTEBOOKS")
        print("=" * 80)

        scanner = NotebookScanner(self.notebooks_dir, self.posts_dir)

        # Get all notebooks
        all_notebooks = []
        for subdir in ['published', 'drafts']:
            notebook_path = Path(self.notebooks_dir) / subdir
            if notebook_path.exists():
                all_notebooks.extend(list(notebook_path.glob('*.ipynb')))

        self.results['notebooks']['total'] = len(all_notebooks)
        print(f"\nTotal notebooks found: {len(all_notebooks)}")

        # Get notebooks with posts
        notebooks_with_posts = scanner.get_notebooks_with_posts()
        self.results['notebooks']['with_posts'] = len(notebooks_with_posts)
        print(f"Notebooks with post files: {len(notebooks_with_posts)}")

        # Analyze each notebook with posts
        print("\nAnalyzing notebooks with posts...")
        for nb_info in notebooks_with_posts:
            notebook_path = nb_info['path']
            post_file = nb_info['post_file']
            basename = nb_info['basename']

            # Check for images
            try:
                extractor = NotebookContentExtractor(notebook_path)
                has_images = extractor.has_images()
                if has_images:
                    self.results['notebooks']['with_images'] += 1

                # Analyze post text
                if os.path.exists(post_file):
                    with open(post_file, 'r') as f:
                        post_content = f.read()

                    has_latex = self.has_latex_symbols(post_content)
                    has_unicode = self.has_unicode_math(post_content)

                    if has_latex:
                        self.results['notebooks']['with_latex_symbols'] += 1

                    if has_unicode:
                        self.results['notebooks']['with_unicode_math'] += 1

                    # Determine if ready to post
                    issues = []
                    if has_latex and not has_unicode:
                        issues.append("Contains LaTeX symbols, needs Unicode conversion")

                    if not issues:
                        self.results['notebooks']['ready_to_post'] += 1
                    else:
                        self.results['notebooks']['needs_work'].append({
                            'name': basename,
                            'path': notebook_path,
                            'post_file': post_file,
                            'has_images': has_images,
                            'issues': issues
                        })

            except Exception as e:
                print(f"  Error analyzing {basename}: {e}")
                continue

        # Notebooks without posts
        notebooks_without_posts = set(nb.stem for nb in all_notebooks) - set(nb['basename'].replace('.ipynb', '') for nb in notebooks_with_posts)
        self.results['notebooks']['without_posts'] = len(notebooks_without_posts)

        print(f"\n✓ Notebooks with images: {self.results['notebooks']['with_images']}")
        print(f"✓ Notebooks with Unicode math: {self.results['notebooks']['with_unicode_math']}")
        print(f"⚠ Notebooks with LaTeX symbols: {self.results['notebooks']['with_latex_symbols']}")
        print(f"✓ Ready to post: {self.results['notebooks']['ready_to_post']}")
        print(f"⚠ Need work: {len(self.results['notebooks']['needs_work'])}")
        print(f"✗ Without posts: {self.results['notebooks']['without_posts']}")

        return self.results['notebooks']

    def audit_templates(self) -> Dict:
        """Audit all LaTeX templates"""
        print("\n" + "=" * 80)
        print("AUDITING LATEX TEMPLATES")
        print("=" * 80)

        scanner = TemplateScanner(self.templates_dir)
        all_templates = scanner.scan_all_templates()

        self.results['templates']['total'] = len(all_templates)
        print(f"\nTotal templates found: {len(all_templates)}")

        # Templates don't have pre-generated posts - they're generated on-the-fly
        # So we just count them and note they need generation
        needs_gen = []
        for template in all_templates:
            if isinstance(template, dict):
                needs_gen.append({
                    'name': template.get('template_name', 'unknown'),
                    'category': template.get('category', 'unknown'),
                    'path': template.get('path', ''),
                    'title': template.get('title', '')
                })
            else:
                needs_gen.append({
                    'name': getattr(template, 'template_name', 'unknown'),
                    'category': getattr(template, 'category', 'unknown'),
                    'path': str(getattr(template, 'path', '')),
                    'title': getattr(template, 'title', '')
                })
        self.results['templates']['needs_generation'] = needs_gen

        print(f"✓ All templates can generate posts on-demand")

        # Show category breakdown
        from collections import Counter
        categories = []
        for t in all_templates:
            if isinstance(t, dict):
                categories.append(t.get('category', 'unknown'))
            else:
                categories.append(getattr(t, 'category', 'unknown'))

        category_counts = Counter(categories)
        print(f"  Categories: {len(set(categories))}")
        print("\n  Templates by category:")
        for category, count in sorted(category_counts.items(), key=lambda x: -x[1])[:10]:
            print(f"    {category:30s} {count:3d}")

        return self.results['templates']

    def generate_report(self) -> str:
        """Generate comprehensive audit report"""
        report = []
        report.append("=" * 80)
        report.append("CONTENT AUDIT REPORT")
        report.append("=" * 80)
        report.append("")

        # Notebooks summary
        nb = self.results['notebooks']
        report.append("NOTEBOOKS:")
        report.append(f"  Total:                     {nb['total']:4d}")
        report.append(f"  With post files:           {nb['with_posts']:4d}")
        report.append(f"  With images:               {nb['with_images']:4d}")
        report.append(f"  With Unicode math:         {nb['with_unicode_math']:4d}")
        report.append(f"  With LaTeX symbols:        {nb['with_latex_symbols']:4d}")
        report.append(f"  Ready to post:             {nb['ready_to_post']:4d}")
        report.append(f"  Need work:                 {len(nb['needs_work']):4d}")
        report.append(f"  Without posts:             {nb.get('without_posts', 0):4d}")
        report.append("")

        # Templates summary
        tmpl = self.results['templates']
        report.append("TEMPLATES:")
        report.append(f"  Total:                     {tmpl['total']:4d}")
        report.append(f"  Ready (generate on-fly):   {tmpl['total']:4d}")
        report.append("")

        # Overall summary
        total_content = nb['total'] + tmpl['total']
        ready_content = nb['ready_to_post'] + tmpl['total']
        needs_work = len(nb['needs_work']) + nb.get('without_posts', 0)

        report.append("OVERALL:")
        report.append(f"  Total content sources:     {total_content:4d}")
        report.append(f"  Ready to post:             {ready_content:4d} ({ready_content/total_content*100:.1f}%)")
        report.append(f"  Needs work/generation:     {needs_work:4d} ({needs_work/total_content*100:.1f}%)")
        report.append("")

        # Issues to fix
        if nb['needs_work']:
            report.append("NOTEBOOKS NEEDING WORK:")
            for item in nb['needs_work'][:10]:  # Show first 10
                report.append(f"  {item['name']}:")
                for issue in item['issues']:
                    report.append(f"    - {issue}")
            if len(nb['needs_work']) > 10:
                report.append(f"  ... and {len(nb['needs_work']) - 10} more")
            report.append("")

        # Recommendations
        report.append("RECOMMENDATIONS:")
        report.append("")

        if nb['with_latex_symbols'] > 0:
            report.append(f"  1. Convert {nb['with_latex_symbols']} notebook posts from LaTeX to Unicode")
            report.append("     Run: python convert_latex_to_unicode.py")
            report.append("")

        if nb.get('without_posts', 0) > 0:
            report.append(f"  2. Generate posts for {nb.get('without_posts', 0)} notebooks without posts")
            report.append("     Run: python generate_notebook_posts.py")
            report.append("")

        report.append(f"  3. Templates ({tmpl['total']}) use on-the-fly generation")
        report.append("     These are handled automatically by content_generator.py")
        report.append("")

        report.append("=" * 80)

        return "\n".join(report)

    def save_results(self, output_path: str = "/home/user/computational-pipeline/social-media-automation/data/audit_results.json"):
        """Save audit results to JSON"""
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n✓ Results saved to: {output_path}")


def main():
    auditor = ContentAuditor()

    # Run audits
    auditor.audit_notebooks()
    auditor.audit_templates()

    # Generate and display report
    report = auditor.generate_report()
    print("\n" + report)

    # Save results
    auditor.save_results()


if __name__ == '__main__':
    main()
