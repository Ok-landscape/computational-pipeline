#!/usr/bin/env python3
"""
Convert LaTeX mathematical symbols to Unicode in social media posts

Ensures posts display correctly on all social media platforms without
special rendering.
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Tuple

# Comprehensive LaTeX to Unicode mapping
LATEX_TO_UNICODE = {
    # Greek letters (lowercase)
    r'\\alpha': 'α', r'\\beta': 'β', r'\\gamma': 'γ', r'\\delta': 'δ',
    r'\\epsilon': 'ε', r'\\zeta': 'ζ', r'\\eta': 'η', r'\\theta': 'θ',
    r'\\iota': 'ι', r'\\kappa': 'κ', r'\\lambda': 'λ', r'\\mu': 'μ',
    r'\\nu': 'ν', r'\\xi': 'ξ', r'\\pi': 'π', r'\\rho': 'ρ',
    r'\\sigma': 'σ', r'\\tau': 'τ', r'\\upsilon': 'υ', r'\\phi': 'φ',
    r'\\chi': 'χ', r'\\psi': 'ψ', r'\\omega': 'ω',

    # Greek letters (uppercase)
    r'\\Gamma': 'Γ', r'\\Delta': 'Δ', r'\\Theta': 'Θ', r'\\Lambda': 'Λ',
    r'\\Xi': 'Ξ', r'\\Pi': 'Π', r'\\Sigma': 'Σ', r'\\Upsilon': 'Υ',
    r'\\Phi': 'Φ', r'\\Psi': 'Ψ', r'\\Omega': 'Ω',

    # Mathematical operators
    r'\\times': '×', r'\\div': '÷', r'\\pm': '±', r'\\mp': '∓',
    r'\\cdot': '·', r'\\ast': '∗', r'\\star': '⋆',

    # Relations
    r'\\leq': '≤', r'\\geq': '≥', r'\\neq': '≠', r'\\approx': '≈',
    r'\\equiv': '≡', r'\\sim': '∼', r'\\simeq': '≃', r'\\cong': '≅',
    r'\\propto': '∝', r'\\ll': '≪', r'\\gg': '≫',

    # Set theory
    r'\\in': '∈', r'\\notin': '∉', r'\\subset': '⊂', r'\\subseteq': '⊆',
    r'\\supset': '⊃', r'\\supseteq': '⊇', r'\\cup': '∪', r'\\cap': '∩',
    r'\\emptyset': '∅', r'\\varnothing': '∅',

    # Logic
    r'\\forall': '∀', r'\\exists': '∃', r'\\neg': '¬', r'\\land': '∧',
    r'\\lor': '∨', r'\\implies': '⇒', r'\\iff': '⇔',

    # Calculus
    r'\\partial': '∂', r'\\nabla': '∇', r'\\int': '∫', r'\\oint': '∮',
    r'\\sum': '∑', r'\\prod': '∏', r'\\infty': '∞',

    # Arrows
    r'\\rightarrow': '→', r'\\leftarrow': '←', r'\\leftrightarrow': '↔',
    r'\\Rightarrow': '⇒', r'\\Leftarrow': '⇐', r'\\Leftrightarrow': '⇔',
    r'\\uparrow': '↑', r'\\downarrow': '↓',

    # Special symbols
    r'\\hbar': 'ℏ', r'\\ell': 'ℓ', r'\\Re': 'ℜ', r'\\Im': 'ℑ',
    r'\\wp': '℘', r'\\aleph': 'ℵ', r'\\beth': 'ℶ',

    # Miscellaneous
    r'\\dots': '…', r'\\cdots': '⋯', r'\\ldots': '…',
    r'\\degree': '°', r'\\prime': '′', r'\\dagger': '†',
    r'\\ddagger': '‡', r'\\S': '§', r'\\P': '¶',
}

# Superscripts and subscripts
SUPERSCRIPTS = {
    '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴',
    '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹',
    '+': '⁺', '-': '⁻', '=': '⁼', '(': '⁽', ')': '⁾',
    'n': 'ⁿ', 'i': 'ⁱ'
}

SUBSCRIPTS = {
    '0': '₀', '1': '₁', '2': '₂', '3': '₃', '4': '₄',
    '5': '₅', '6': '₆', '7': '₇', '8': '₈', '9': '₉',
    '+': '₊', '-': '₋', '=': '₌', '(': '₍', ')': '₎',
    'a': 'ₐ', 'e': 'ₑ', 'o': 'ₒ', 'x': 'ₓ', 'i': 'ᵢ', 'j': 'ⱼ'
}


def convert_superscript(text: str) -> str:
    """Convert ^{...} or ^x to Unicode superscripts"""

    # Handle ^{...} (multi-character)
    def replace_braced(match):
        content = match.group(1)
        result = ''
        for char in content:
            result += SUPERSCRIPTS.get(char, char)
        return result

    text = re.sub(r'\^\{([^}]+)\}', replace_braced, text)

    # Handle ^x (single character)
    def replace_single(match):
        char = match.group(1)
        return SUPERSCRIPTS.get(char, '^' + char)

    text = re.sub(r'\^([0-9a-zA-Z+\-=()])', replace_single, text)

    return text


def convert_subscript(text: str) -> str:
    """Convert _{...} or _x to Unicode subscripts"""

    # Handle _{...} (multi-character)
    def replace_braced(match):
        content = match.group(1)
        result = ''
        for char in content:
            result += SUBSCRIPTS.get(char, char)
        return result

    text = re.sub(r'_\{([^}]+)\}', replace_braced, text)

    # Handle _x (single character)
    def replace_single(match):
        char = match.group(1)
        return SUBSCRIPTS.get(char, '_' + char)

    text = re.sub(r'_([0-9a-zA-Z+\-=()])', replace_single, text)

    return text


def remove_math_delimiters(text: str) -> str:
    """Remove $ delimiters but keep content"""
    # Remove $...$ inline math delimiters
    text = re.sub(r'\$([^\$]+)\$', r'\1', text)
    return text


def convert_latex_to_unicode(text: str, aggressive: bool = False) -> str:
    """
    Convert LaTeX mathematical notation to Unicode

    Args:
        text: Text containing LaTeX symbols
        aggressive: If True, remove ALL LaTeX commands. If False, only convert known symbols.

    Returns:
        Text with Unicode symbols
    """

    # First remove math delimiters
    text = remove_math_delimiters(text)

    # Convert LaTeX commands to Unicode
    for latex, unicode_char in LATEX_TO_UNICODE.items():
        # Match with word boundary to avoid partial matches
        text = re.sub(latex + r'\b', unicode_char, text)
        text = re.sub(latex + r'(?=[^a-zA-Z])', unicode_char, text)

    # Convert superscripts and subscripts
    text = convert_superscript(text)
    text = convert_subscript(text)

    # If aggressive, remove remaining LaTeX commands
    if aggressive:
        # Remove any remaining \command patterns
        text = re.sub(r'\\[a-zA-Z]+\b', '', text)
        # Remove braces
        text = text.replace('{', '').replace('}', '')

    return text


def needs_conversion(text: str) -> Tuple[bool, List[str]]:
    """
    Check if text needs LaTeX to Unicode conversion

    Returns:
        (needs_conversion, list_of_found_latex_commands)
    """
    found_commands = []

    # Check for LaTeX commands
    for latex_cmd in LATEX_TO_UNICODE.keys():
        if latex_cmd in text:
            found_commands.append(latex_cmd)

    # Check for superscripts/subscripts
    if re.search(r'\^[{]?[a-zA-Z0-9+\-=()]+[}]?', text):
        found_commands.append('^{} or ^x')

    if re.search(r'_[{]?[a-zA-Z0-9+\-=()]+[}]?', text):
        found_commands.append('_{} or _x')

    # Check for $ delimiters
    if '$' in text:
        found_commands.append('$ delimiters')

    return len(found_commands) > 0, found_commands


def process_post_file(file_path: str, dry_run: bool = True, backup: bool = True) -> Dict:
    """
    Process a single social media post file

    Returns:
        Dictionary with conversion statistics
    """

    with open(file_path, 'r', encoding='utf-8') as f:
        original_text = f.read()

    needs_conv, latex_commands = needs_conversion(original_text)

    if not needs_conv:
        return {
            'file': os.path.basename(file_path),
            'status': 'clean',
            'changes': 0,
            'latex_found': []
        }

    # Convert
    converted_text = convert_latex_to_unicode(original_text, aggressive=False)

    # Count changes
    changes = len(latex_commands)

    if not dry_run:
        # Backup original
        if backup:
            backup_path = file_path + '.backup'
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(original_text)

        # Write converted
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(converted_text)

        status = 'converted'
    else:
        status = 'would_convert'

    return {
        'file': os.path.basename(file_path),
        'status': status,
        'changes': changes,
        'latex_found': latex_commands
    }


def main():
    posts_dir = "/home/user/computational-pipeline/social-media-automation/repo-data/output/social_posts"

    print("=" * 80)
    print("LATEX TO UNICODE CONVERTER")
    print("=" * 80)
    print()

    # Get all post files
    post_files = list(Path(posts_dir).glob('*_posts.txt'))

    print(f"Found {len(post_files)} post files")
    print()

    # Dry run first
    print("Running dry-run analysis...")
    print()

    results = []
    for post_file in sorted(post_files):
        result = process_post_file(str(post_file), dry_run=True)
        results.append(result)

    # Show statistics
    total = len(results)
    clean = sum(1 for r in results if r['status'] == 'clean')
    needs_work = sum(1 for r in results if r['status'] == 'would_convert')

    print(f"Results:")
    print(f"  Total files:        {total}")
    print(f"  Clean (no LaTeX):   {clean}")
    print(f"  Needs conversion:   {needs_work}")
    print()

    if needs_work > 0:
        print(f"Files needing conversion:")
        for r in results:
            if r['status'] == 'would_convert':
                print(f"  {r['file']}: {r['changes']} LaTeX patterns found")
                if r['latex_found'][:3]:  # Show first 3
                    print(f"    Examples: {', '.join(r['latex_found'][:3])}")
        print()

    # Ask for confirmation
    print("=" * 80)
    response = input(f"Convert {needs_work} files? (yes/no): ")

    if response.lower() in ['yes', 'y']:
        print()
        print("Converting files...")

        converted_count = 0
        for post_file in sorted(post_files):
            result = process_post_file(str(post_file), dry_run=False, backup=True)
            if result['status'] == 'converted':
                converted_count += 1
                print(f"  ✓ {result['file']}")

        print()
        print(f"✓ Converted {converted_count} files")
        print(f"  Backups saved with .backup extension")
    else:
        print("Conversion cancelled")


if __name__ == '__main__':
    main()
