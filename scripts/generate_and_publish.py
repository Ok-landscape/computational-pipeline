#!/usr/bin/env python3
"""
generate_and_publish.py - Automated Template Generation and Publishing
Creates new LaTeX templates, compiles them, and publishes to GitHub
"""

import os
import sys
import subprocess
import json
import time
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple

# Configuration
REPO_DIR = Path("/home/user/computational-pipeline")
LATEX_DIR = REPO_DIR / "latex-templates"
TEMPLATES_DIR = LATEX_DIR / "templates"
OUTPUT_DIR = LATEX_DIR / "output"
SCRIPTS_DIR = REPO_DIR / "scripts"

# Categories and their typical template counts
CATEGORIES = {
    "acoustics": {"current": 3, "target": 5},
    "aerospace": {"current": 5, "target": 8},
    "astronomy": {"current": 4, "target": 6},
    "astrophysics": {"current": 3, "target": 6},
    "atmospheric-science": {"current": 3, "target": 5},
    "bioinformatics": {"current": 4, "target": 7},
    "biology": {"current": 3, "target": 6},
    "biomedical": {"current": 3, "target": 6},
    "chemical-engineering": {"current": 4, "target": 7},
    "chemistry": {"current": 3, "target": 6},
    "civil-engineering": {"current": 3, "target": 6},
    "climate-science": {"current": 3, "target": 6},
    "cognitive-science": {"current": 3, "target": 5},
    "computational-biology": {"current": 4, "target": 7},
    "computer-science": {"current": 4, "target": 8},
    "control-theory": {"current": 3, "target": 6},
    "cosmology": {"current": 3, "target": 5},
    "cryptography": {"current": 3, "target": 6},
    "data-science": {"current": 4, "target": 8},
    "earth-science": {"current": 3, "target": 6},
    "ecology": {"current": 3, "target": 6},
    "economics": {"current": 4, "target": 7},
    "electrical-engineering": {"current": 4, "target": 7},
    "electromagnetics": {"current": 3, "target": 6},
    "epidemiology": {"current": 3, "target": 6},
    "financial-math": {"current": 4, "target": 7},
    "fluid-dynamics": {"current": 3, "target": 6},
    "game-development": {"current": 3, "target": 5},
    "geochemistry": {"current": 3, "target": 5},
    "geophysics": {"current": 3, "target": 6},
    "hydrology": {"current": 3, "target": 5},
    "image-processing": {"current": 3, "target": 6},
    "machine-learning": {"current": 4, "target": 10},
    "marine-biology": {"current": 4, "target": 6},
    "materials-science": {"current": 3, "target": 6},
    "mathematics": {"current": 5, "target": 10},
    "mechanical-engineering": {"current": 5, "target": 8},
    "medical-physics": {"current": 3, "target": 6},
    "neuroscience": {"current": 4, "target": 7},
    "nlp": {"current": 3, "target": 6},
    "nuclear-physics": {"current": 3, "target": 5},
    "numerical-methods": {"current": 4, "target": 8},
    "oceanography": {"current": 3, "target": 5},
    "operations-research": {"current": 3, "target": 6},
    "optics": {"current": 3, "target": 6},
    "particle-physics": {"current": 3, "target": 5},
    "photonics": {"current": 3, "target": 5},
    "plasma-physics": {"current": 3, "target": 5},
    "power-systems": {"current": 3, "target": 6},
    "probability": {"current": 3, "target": 6},
    "psychophysics": {"current": 3, "target": 5},
    "quantum-computing": {"current": 3, "target": 7},
    "quantum-mechanics": {"current": 4, "target": 7},
    "relativity": {"current": 3, "target": 5},
    "robotics": {"current": 4, "target": 7},
    "semiconductor": {"current": 3, "target": 5},
    "signal-processing": {"current": 4, "target": 7},
    "simulations": {"current": 3, "target": 6},
    "statistics": {"current": 4, "target": 8},
    "systems-biology": {"current": 3, "target": 6},
    "thermodynamics": {"current": 3, "target": 6},
    "topology": {"current": 3, "target": 5},
}


class Colors:
    """ANSI color codes for terminal output"""
    BLUE = '\033[0;34m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    RED = '\033[0;31m'
    NC = '\033[0m'  # No Color


def log_info(msg: str):
    print(f"{Colors.BLUE}[INFO]{Colors.NC} {msg}")


def log_success(msg: str):
    print(f"{Colors.GREEN}[SUCCESS]{Colors.NC} {msg}")


def log_warning(msg: str):
    print(f"{Colors.YELLOW}[WARNING]{Colors.NC} {msg}")


def log_error(msg: str):
    print(f"{Colors.RED}[ERROR]{Colors.NC} {msg}", file=sys.stderr)


def count_existing_templates() -> Dict[str, int]:
    """Count existing templates in each category"""
    counts = {}
    for category_dir in TEMPLATES_DIR.iterdir():
        if category_dir.is_dir() and category_dir.name not in ['knitr', 'pythontex', 'sagetex', 'other']:
            tex_files = list(category_dir.glob("*.tex"))
            counts[category_dir.name] = len(tex_files)
    return counts


def identify_gaps() -> List[Tuple[str, int]]:
    """Identify categories that need more templates"""
    existing = count_existing_templates()
    gaps = []

    for category, targets in CATEGORIES.items():
        current = existing.get(category, 0)
        target = targets["target"]
        if current < target:
            gap = target - current
            gaps.append((category, gap))

    # Sort by gap size (descending)
    gaps.sort(key=lambda x: x[1], reverse=True)
    return gaps


def compile_template(tex_file: Path) -> bool:
    """Compile a single LaTeX template"""
    log_info(f"Compiling {tex_file.name}...")

    # Change to the template directory
    os.chdir(tex_file.parent)

    try:
        # Run pdflatex twice (standard for LaTeX)
        for pass_num in [1, 2]:
            result = subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", tex_file.name],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode != 0:
                log_error(f"Compilation failed on pass {pass_num}")
                log_error(f"Error output: {result.stderr[:500]}")
                return False

        # Check for PythonTeX code
        pytxcode = tex_file.with_suffix('.pytxcode')
        if pytxcode.exists():
            log_info("Running PythonTeX...")
            result = subprocess.run(
                ["pythontex", tex_file.name],
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.returncode != 0:
                log_warning(f"PythonTeX execution had issues: {result.stderr[:200]}")

            # Final pdflatex pass
            subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", tex_file.name],
                capture_output=True,
                timeout=60
            )

        # Move PDF to output directory
        pdf_file = tex_file.with_suffix('.pdf')
        if pdf_file.exists():
            OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            output_pdf = OUTPUT_DIR / pdf_file.name
            pdf_file.rename(output_pdf)
            log_success(f"Compiled successfully: {output_pdf.name}")
            return True
        else:
            log_error("PDF was not generated")
            return False

    except subprocess.TimeoutExpired:
        log_error("Compilation timeout")
        return False
    except Exception as e:
        log_error(f"Compilation error: {str(e)}")
        return False
    finally:
        os.chdir(REPO_DIR)


def run_auto_publish(mode: str = "once") -> bool:
    """Run the auto_publish.sh script"""
    auto_publish_script = SCRIPTS_DIR / "auto_publish.sh"

    if not auto_publish_script.exists():
        log_error("auto_publish.sh not found")
        return False

    log_info(f"Running auto_publish.sh in {mode} mode...")

    try:
        result = subprocess.run(
            [str(auto_publish_script), mode],
            cwd=REPO_DIR,
            capture_output=True,
            text=True,
            timeout=300
        )

        if result.returncode == 0:
            log_success("Auto-publish completed successfully")
            print(result.stdout)
            return True
        else:
            log_error("Auto-publish failed")
            print(result.stderr)
            return False

    except Exception as e:
        log_error(f"Failed to run auto_publish: {str(e)}")
        return False


def generate_report() -> Dict:
    """Generate a status report"""
    existing = count_existing_templates()
    gaps = identify_gaps()

    total_templates = sum(existing.values())
    total_gaps = sum(gap for _, gap in gaps)

    report = {
        "timestamp": datetime.now().isoformat(),
        "total_templates": total_templates,
        "total_categories": len(existing),
        "total_gaps": total_gaps,
        "top_gaps": gaps[:10],
        "category_status": {}
    }

    for category, count in existing.items():
        target = CATEGORIES.get(category, {}).get("target", count)
        report["category_status"][category] = {
            "current": count,
            "target": target,
            "progress": f"{count}/{target}"
        }

    return report


def main():
    """Main execution function"""
    import argparse

    parser = argparse.ArgumentParser(description="Generate and publish LaTeX templates")
    parser.add_argument("--analyze", action="store_true", help="Analyze gaps and generate report")
    parser.add_argument("--generate", type=int, metavar="N", help="Generate N new templates")
    parser.add_argument("--compile-new", action="store_true", help="Compile newly added templates")
    parser.add_argument("--publish", action="store_true", help="Publish changes to GitHub")
    parser.add_argument("--full-workflow", type=int, metavar="N", help="Full workflow: generate N templates, compile, and publish")

    args = parser.parse_args()

    if args.analyze or not any(vars(args).values()):
        log_info("Analyzing template gaps...")
        report = generate_report()

        log_success(f"Current Status:")
        log_info(f"  Total templates: {report['total_templates']}")
        log_info(f"  Total categories: {report['total_categories']}")
        log_info(f"  Total gaps: {report['total_gaps']}")

        if report['top_gaps']:
            log_info("\nTop 10 categories needing templates:")
            for i, (category, gap) in enumerate(report['top_gaps'], 1):
                current = report['category_status'][category]['current']
                target = report['category_status'][category]['target']
                log_info(f"  {i:2d}. {category:30s} - needs {gap} more (current: {current}/{target})")

        # Save report to file
        report_file = LATEX_DIR / "generation_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        log_success(f"Report saved to {report_file}")

    if args.compile_new:
        log_info("Compiling newly added templates...")
        # Find templates without corresponding PDFs
        templates_to_compile = []
        for category_dir in TEMPLATES_DIR.iterdir():
            if category_dir.is_dir():
                for tex_file in category_dir.glob("*.tex"):
                    pdf_file = OUTPUT_DIR / tex_file.with_suffix('.pdf').name
                    if not pdf_file.exists():
                        templates_to_compile.append(tex_file)

        log_info(f"Found {len(templates_to_compile)} templates to compile")

        compiled = 0
        for tex_file in templates_to_compile:
            if compile_template(tex_file):
                compiled += 1

        log_success(f"Compiled {compiled}/{len(templates_to_compile)} templates successfully")

    if args.publish:
        log_info("Publishing changes to GitHub...")
        run_auto_publish("once")

    if args.full_workflow:
        log_info(f"Starting full workflow to generate {args.full_workflow} templates...")
        log_warning("Template generation requires additional implementation")
        log_info("Workflow would: 1) Generate templates 2) Compile them 3) Publish to GitHub")
        log_info("For now, use the existing generate scripts in latex-templates/")


if __name__ == "__main__":
    main()
