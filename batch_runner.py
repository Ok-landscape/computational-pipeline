#!/usr/bin/env python3
"""
Batch Runner for Computational Pipeline
Runs the pipeline continuously for multiple topics without stopping.
"""

import subprocess
import os
import sys
import json
import datetime
import time
import shutil

# Configuration
BASE_DIR = os.path.expanduser("~/computational_pipeline")
BATCH_LOG = os.path.join(BASE_DIR, "batch_run_log.json")

# 90 unique topics across various scientific/computational domains
TOPICS = [
    # PDEs (5)
    "Heat Equation 1D Diffusion",
    "Wave Equation Vibrating String",
    "Laplace Equation Electrostatics",
    "Advection Equation Transport",
    "Burgers Equation Shock Waves",

    # Linear Algebra (8)
    "Principal Component Analysis PCA",
    "Singular Value Decomposition SVD",
    "Eigenvalue Problems Power Method",
    "LU Matrix Factorization",
    "QR Decomposition",
    "Cholesky Decomposition",
    "Jacobi Iterative Method",
    "Gauss Seidel Method",

    # Classical Physics (8)
    "N-Body Gravitational Simulation",
    "Projectile Motion with Air Resistance",
    "Double Pendulum Chaos",
    "Simple Harmonic Oscillator",
    "Coupled Oscillators",
    "Orbital Mechanics Kepler Problem",
    "Elastic Collision Simulation",
    "Spring Mass System",

    # Quantum Physics (5)
    "Quantum Harmonic Oscillator",
    "Particle in a Box",
    "Hydrogen Atom Wavefunctions",
    "Schrodinger Equation Finite Difference",
    "Quantum Tunneling Simulation",

    # Numerical Methods (10)
    "Simpson Rule Integration",
    "Runge Kutta Fourth Order",
    "Newton Raphson Root Finding",
    "Bisection Method",
    "Trapezoidal Rule Integration",
    "Gaussian Quadrature",
    "Finite Difference Method",
    "Euler Method for ODEs",
    "Adams Bashforth Method",
    "Secant Method Root Finding",

    # Machine Learning (8)
    "Perceptron Neural Network",
    "K-Means Clustering",
    "Linear Regression Gradient Descent",
    "Logistic Regression Classification",
    "K-Nearest Neighbors",
    "Decision Tree Classifier",
    "Naive Bayes Classifier",
    "Support Vector Machine Basics",

    # Probability and Statistics (8)
    "Markov Chain Simulation",
    "Bayesian Inference Coin Flip",
    "Birthday Paradox Simulation",
    "Gamblers Ruin Problem",
    "Random Number Generation LCG",
    "Rejection Sampling Method",
    "Maximum Likelihood Estimation",
    "Hypothesis Testing Simulation",

    # Geometry and Graphics (8)
    "Voronoi Diagram Construction",
    "Convex Hull Algorithm",
    "Bezier Curve Drawing",
    "Koch Snowflake Fractal",
    "Sierpinski Triangle",
    "Dragon Curve Fractal",
    "Delaunay Triangulation",
    "Line Intersection Algorithm",

    # Finance and Economics (6)
    "Black Scholes Option Pricing",
    "Portfolio Optimization Markowitz",
    "Compound Interest Calculator",
    "Monte Carlo Option Pricing",
    "Value at Risk Simulation",
    "Geometric Brownian Motion",

    # Biology and Life Sciences (6)
    "Genetic Algorithm Optimization",
    "Simple Neural Network",
    "Population Genetics Hardy Weinberg",
    "Hodgkin Huxley Neuron Model",
    "Enzyme Kinetics Michaelis Menten",
    "Cellular Automata Game of Life",

    # Cryptography and Security (4)
    "RSA Encryption Basics",
    "Diffie Hellman Key Exchange",
    "Caesar Cipher Implementation",
    "Hash Function Visualization",

    # Game Theory (4)
    "Prisoners Dilemma Simulation",
    "Nash Equilibrium Finding",
    "Evolutionary Game Theory",
    "Auction Theory Simulation",

    # Signal Processing (5)
    "Digital Filter Design",
    "Wavelet Transform Analysis",
    "Convolution and Correlation",
    "Spectral Analysis FFT",
    "Nyquist Sampling Theorem",

    # Fluid Dynamics (3)
    "Navier Stokes Simple Flow",
    "Lattice Boltzmann Method",
    "Potential Flow Visualization",

    # Miscellaneous (2)
    "Numerical Differentiation",
    "Interpolation Methods Comparison"
]

def run_single_topic(topic, attempt=1, max_attempts=3):
    """Run the pipeline for a single topic with retry logic."""
    import re

    # Sanitize topic for filename
    safe_topic = re.sub(r'[^\w\s-]', '', topic).strip().lower()
    safe_topic = re.sub(r'[-\s]+', '_', safe_topic)

    print(f"\n{'='*60}")
    print(f"TOPIC: {topic}")
    print(f"Attempt: {attempt}/{max_attempts}")
    print(f"{'='*60}\n")

    # Run the workflow.py with topic input
    try:
        process = subprocess.Popen(
            ["python3", os.path.join(BASE_DIR, "workflow.py")],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=BASE_DIR
        )

        stdout, stderr = process.communicate(input=topic + "\n", timeout=600)

        print(stdout)
        if stderr:
            print(f"STDERR: {stderr}")

        # Check if notebook was published
        pub_dir = os.path.join(BASE_DIR, "notebooks/published")
        expected_file = os.path.join(pub_dir, f"{safe_topic}.ipynb")

        # Also check for similar filenames (the agent might name slightly differently)
        published_files = os.listdir(pub_dir)
        topic_published = any(safe_topic in f.lower() for f in published_files)

        if process.returncode == 0 and topic_published:
            return True, "Success"
        elif process.returncode == 0:
            # Process succeeded but file not found - check if it was created
            return True, "Completed (verify file)"
        else:
            if attempt < max_attempts:
                print(f"Retrying {topic}...")
                time.sleep(2)
                return run_single_topic(topic, attempt + 1, max_attempts)
            return False, f"Failed after {max_attempts} attempts"

    except subprocess.TimeoutExpired:
        process.kill()
        if attempt < max_attempts:
            return run_single_topic(topic, attempt + 1, max_attempts)
        return False, "Timeout"
    except Exception as e:
        if attempt < max_attempts:
            return run_single_topic(topic, attempt + 1, max_attempts)
        return False, str(e)

def git_push_batch(message):
    """Push accumulated changes to GitHub."""
    try:
        # Add all changes
        subprocess.run(
            ["git", "add", "-A"],
            cwd=BASE_DIR,
            capture_output=True
        )

        # Commit
        subprocess.run(
            ["git", "commit", "-m", message],
            cwd=BASE_DIR,
            capture_output=True
        )

        # Push
        result = subprocess.run(
            ["git", "push"],
            cwd=BASE_DIR,
            capture_output=True,
            text=True
        )

        return result.returncode == 0
    except Exception as e:
        print(f"Git push error: {e}")
        return False

def main():
    """Main batch execution loop."""
    start_time = datetime.datetime.now()

    results = {
        "start_time": start_time.isoformat(),
        "completed": [],
        "failed": [],
        "skipped": []
    }

    # Check existing published notebooks to skip already completed topics
    pub_dir = os.path.join(BASE_DIR, "notebooks/published")
    existing = [f.lower() for f in os.listdir(pub_dir) if f.endswith(".ipynb")]

    print(f"Starting batch run of {len(TOPICS)} topics")
    print(f"Existing notebooks: {len(existing)}")
    print(f"Target: 100 total notebooks\n")

    push_counter = 0

    for i, topic in enumerate(TOPICS, 1):
        # Sanitize topic name for comparison
        import re
        safe_topic = re.sub(r'[^\w\s-]', '', topic).strip().lower()
        safe_topic = re.sub(r'[-\s]+', '_', safe_topic)

        # Check if already done
        if any(safe_topic in f for f in existing):
            print(f"[{i}/{len(TOPICS)}] SKIP: {topic} (already exists)")
            results["skipped"].append(topic)
            continue

        print(f"\n[{i}/{len(TOPICS)}] Processing: {topic}")

        success, message = run_single_topic(topic)

        if success:
            results["completed"].append({"topic": topic, "message": message})
            push_counter += 1

            # Push to GitHub every 5 successful notebooks
            if push_counter >= 5:
                print("\nPushing batch to GitHub...")
                git_push_batch(f"Batch: Add notebooks {i-4}-{i}")
                push_counter = 0
        else:
            results["failed"].append({"topic": topic, "error": message})
            print(f"FAILED: {topic} - {message}")

        # Brief pause between topics
        time.sleep(1)

    # Final push for remaining notebooks
    if push_counter > 0:
        print("\nFinal push to GitHub...")
        git_push_batch(f"Batch: Final notebooks push")

    # Save results
    end_time = datetime.datetime.now()
    results["end_time"] = end_time.isoformat()
    results["duration_minutes"] = (end_time - start_time).total_seconds() / 60

    with open(BATCH_LOG, 'w') as f:
        json.dump(results, f, indent=2)

    # Print summary
    print("\n" + "="*60)
    print("BATCH RUN COMPLETE")
    print("="*60)
    print(f"Duration: {results['duration_minutes']:.1f} minutes")
    print(f"Completed: {len(results['completed'])}")
    print(f"Failed: {len(results['failed'])}")
    print(f"Skipped: {len(results['skipped'])}")
    print(f"\nTotal notebooks in repository: {len(existing) + len(results['completed'])}")

    if results['failed']:
        print("\nFailed topics:")
        for item in results['failed']:
            print(f"  - {item['topic']}: {item['error']}")

    print(f"\nFull log saved to: {BATCH_LOG}")

if __name__ == "__main__":
    main()
