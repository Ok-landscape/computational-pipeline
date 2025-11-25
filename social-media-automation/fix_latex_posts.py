#!/usr/bin/env python3
"""
Identify and fix posts that have actual LaTeX problems.

Only converts posts that truly need help - ignoring posts that already
use proper Unicode throughout.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple
from convert_latex_to_unicode import convert_latex_to_unicode, LATEX_TO_UNICODE


def has_unicode_math(text: str) -> bool:
    """Check if text already uses Unicode math symbols"""
    # Common Unicode math ranges
    unicode_math_chars = set()

    # Greek letters
    unicode_math_chars.update(range(0x0370, 0x03FF))
    # Mathematical operators
    unicode_math_chars.update(range(0x2200, 0x22FF))
    # Subscripts and superscripts
    unicode_math_chars.update(range(0x2070, 0x209F))
    # Number forms
    unicode_math_chars.update(range(0x2150, 0x218F))

    for char in text:
        if ord(char) in unicode_math_chars:
            return True
    return False


def has_problematic_latex(text: str) -> Tuple[bool, List[str]]:
    """
    Check if text has LaTeX that should be converted.

    Returns:
        (has_problems, list_of_issues)
    """
    issues = []

    # Check for actual LaTeX commands (not just ^ and _)
    for latex_cmd in LATEX_TO_UNICODE.keys():
        if latex_cmd in text:
            issues.append(f"LaTeX command: {latex_cmd}")

    # Check for $ delimiters (inline math mode)
    if '$' in text:
        # Count occurrences
        count = text.count('$')
        if count >= 2:  # Paired delimiters
            issues.append(f"Math delimiters: {count//2} pairs of $...$")

    # Check for problematic patterns like ^{text} (multi-char superscript)
    multi_super = re.findall(r'\^\{[a-zA-Z0-9+\-*/()]+\}', text)
    if multi_super:
        issues.append(f"Multi-char superscripts: {len(multi_super)} found")

    # Check for problematic patterns like _{text} (multi-char subscript)
    multi_sub = re.findall(r'_\{[a-zA-Z0-9+\-*/()]+\}', text)
    if multi_sub:
        issues.append(f"Multi-char subscripts: {len(multi_sub)} found")

    return len(issues) > 0, issues


def analyze_post(file_path: str) -> Dict:
    """Analyze a single post file"""

    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()

    has_unicode = has_unicode_math(text)
    has_latex, latex_issues = has_problematic_latex(text)

    status = "clean"
    if has_latex and not has_unicode:
        status = "needs_conversion"
    elif has_latex and has_unicode:
        status = "mixed"  # Has both - might still need cleanup
    elif not has_latex and has_unicode:
        status = "unicode_only"  # Perfect!

    return {
        'file': os.path.basename(file_path),
        'path': file_path,
        'status': status,
        'has_unicode': has_unicode,
        'has_latex': has_latex,
        'issues': latex_issues
    }


def main():
    posts_dir = "/home/user/computational-pipeline/social-media-automation/repo-data/output/social_posts"

    print("=" * 80)
    print("SMART LATEX FIXER - Only Convert Posts That Need It")
    print("=" * 80)
    print()

    # Get all post files
    post_files = list(Path(posts_dir).glob('*_posts.txt'))
    print(f"Analyzing {len(post_files)} post files...")
    print()

    # Analyze all
    results = []
    for post_file in sorted(post_files):
        result = analyze_post(str(post_file))
        results.append(result)

    # Categorize
    unicode_only = [r for r in results if r['status'] == 'unicode_only']
    needs_conversion = [r for r in results if r['status'] == 'needs_conversion']
    mixed = [r for r in results if r['status'] == 'mixed']
    clean = [r for r in results if r['status'] == 'clean']

    # Report
    print("Analysis Results:")
    print(f"  Unicode-only (perfect):      {len(unicode_only):3d}")
    print(f"  Needs conversion (LaTeX):    {len(needs_conversion):3d}")
    print(f"  Mixed (has both):            {len(mixed):3d}")
    print(f"  Clean (no math symbols):     {len(clean):3d}")
    print()

    # Show what needs conversion
    targets = needs_conversion + mixed
    if targets:
        print(f"Files to convert ({len(targets)}):")
        print()
        for r in targets[:20]:  # Show first 20
            print(f"  {r['file']}")
            for issue in r['issues'][:2]:  # Show first 2 issues
                print(f"    - {issue}")
        if len(targets) > 20:
            print(f"  ... and {len(targets) - 20} more")
        print()

        # Ask for confirmation
        print("=" * 80)
        response = input(f"Convert {len(targets)} files? (yes/no): ")

        if response.lower() in ['yes', 'y']:
            print()
            print("Converting files...")

            converted_count = 0
            for r in targets:
                # Read original
                with open(r['path'], 'r', encoding='utf-8') as f:
                    original = f.read()

                # Convert
                converted = convert_latex_to_unicode(original, aggressive=False)

                # Only save if actually changed
                if converted != original:
                    # Backup
                    backup_path = r['path'] + '.backup'
                    with open(backup_path, 'w', encoding='utf-8') as f:
                        f.write(original)

                    # Save converted
                    with open(r['path'], 'w', encoding='utf-8') as f:
                        f.write(converted)

                    converted_count += 1
                    print(f"  ✓ {r['file']}")

            print()
            print(f"✓ Converted {converted_count} files")
            print(f"  Backups saved with .backup extension")
        else:
            print("Conversion cancelled")
    else:
        print("✓ No files need conversion - all posts use proper Unicode!")


if __name__ == '__main__':
    main()
