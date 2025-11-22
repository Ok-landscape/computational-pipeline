#!/usr/bin/env python3
"""
File: workflow.py
Purpose: Orchestration Controller for CoCalc Autonomous Pipeline.
Description: Manages the lifecycle of notebook creation, validation, and publishing.
"""

import subprocess
import json
import os
import sys
import datetime
import shutil
import re

try:
    import nbformat
except ImportError:
    print("Error: 'nbformat' missing. Run: pip install nbformat")
    sys.exit(1)

# --- Configuration ---
BASE_DIR = os.path.expanduser("~/computational_pipeline")
STATE_FILE = os.path.join(BASE_DIR, "orchestration/state.json")
LOG_FILE = os.path.join(BASE_DIR, "orchestration/logs.jsonl")
PROMPTS_FILE = os.path.join(BASE_DIR, "system_prompts.md")

# --- State Management ---
def load_state():
    """Loads the persistent state of the pipeline."""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {"current_stage": "idle", "active_task": None}

def save_state(stage, task):
    """Saves the current state to disk."""
    with open(STATE_FILE, 'w') as f:
        json.dump({"current_stage": stage, "active_task": task}, f)

def log(message, level="INFO"):
    """Prints a log message and writes to JSONL log."""
    timestamp = datetime.datetime.now().isoformat()
    print(f"[{level}] {message}")

    entry = {"timestamp": timestamp, "message": message, "level": level}
    with open(LOG_FILE, 'a') as f:
        f.write(json.dumps(entry) + "\n")

# --- Prompt Loading ---
def load_prompts():
    """Load persona prompts from system_prompts.md."""
    prompts = {
        "AGENT_SCIENTIST": "",
        "AGENT_REVIEWER": "",
        "AGENT_PUBLICIST": "",
        "AGENT_PUBLISHER": ""
    }

    if not os.path.exists(PROMPTS_FILE):
        log(f"Warning: {PROMPTS_FILE} not found, using defaults", "WARN")
        return get_default_prompts()

    with open(PROMPTS_FILE, 'r') as f:
        content = f.read()

    # Extract each persona section
    for persona in prompts.keys():
        # Find section starting with persona number/name
        pattern = rf"## \d+\. {persona}(.*?)(?=## \d+\.|$)"
        match = re.search(pattern, content, re.DOTALL)
        if match:
            prompts[persona] = match.group(1).strip()

    return prompts

def get_default_prompts():
    """Fallback prompts if file not found."""
    return {
        "AGENT_SCIENTIST": "Create a Jupyter Notebook with LaTeX math and Python code (numpy/scipy/matplotlib). Save to notebooks/drafts/.",
        "AGENT_REVIEWER": "Analyze the traceback and fix the code in the notebook file.",
        "AGENT_PUBLISHER": "Commit notebooks/published/ files to Git and push. Return the GitHub URL.",
        "AGENT_PUBLICIST": "Write social posts converting LaTeX to Unicode. Save to output/social_posts/."
    }

# --- The Cognitive Interface ---
def run_agent(prompt_text):
    """
    Executes the Claude Code CLI in non-interactive mode.

    Args:
        prompt_text (str): The instruction for the agent.

    Returns:
        tuple: (success: bool, output: str)
    """
    cmd = [
        "claude",
        "-p", prompt_text,
        "--dangerously-skip-permissions"
    ]

    try:
        log("Invoking Claude agent...")
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )

        if result.returncode != 0:
            error_msg = result.stderr or "Unknown error"
            log(f"Agent process error: {error_msg}", "ERROR")
            return False, error_msg

        return True, result.stdout.strip()

    except subprocess.TimeoutExpired:
        log("Agent timed out after 5 minutes", "ERROR")
        return False, "Timeout"
    except FileNotFoundError:
        log("Claude CLI not found. Is it installed and in PATH?", "ERROR")
        return False, "CLI not found"

# --- Notebook Error Extraction ---
def extract_error_from_notebook(notebook_path):
    """
    Parses a notebook to find the traceback of the failed cell.
    """
    if not os.path.exists(notebook_path):
        return "Output notebook not found"

    try:
        with open(notebook_path, 'r') as f:
            nb = nbformat.read(f, as_version=4)

        for cell in nb.cells:
            if cell.cell_type == "code" and "outputs" in cell:
                for output in cell.outputs:
                    if output.get("output_type") == "error":
                        return "\n".join(output.get("traceback", ["Unknown error"]))

        return "No error traceback found in notebook"
    except Exception as e:
        return f"Could not parse notebook: {str(e)}"

# --- Main Orchestration ---
def main():
    # Verify environment
    if not os.path.exists(BASE_DIR):
        log(f"Pipeline directory not found: {BASE_DIR}", "ERROR")
        log("Run the setup first to create directory structure")
        return

    # Check for auth (Claude Code stores credentials at ~/.claude/.credentials.json)
    auth_file = os.path.expanduser("~/.claude/.credentials.json")
    if not os.path.exists(auth_file):
        log("Claude CLI not authenticated!", "ERROR")
        log(f"Credentials file not found: {auth_file}")
        return

    # Load prompts
    prompts = load_prompts()

    # Get topic from command line or user input
    if len(sys.argv) > 1:
        topic = " ".join(sys.argv[1:]).strip()
    else:
        topic = input("Enter scientific topic (e.g., 'Lotka-Volterra Simulation'): ").strip()
    if not topic:
        log("Topic cannot be empty", "ERROR")
        return

    # Sanitize topic for filename
    safe_topic = re.sub(r'[^\w\s-]', '', topic).strip().lower()
    safe_topic = re.sub(r'[-\s]+', '_', safe_topic)

    # --- Stage 1: Drafting ---
    log(f"Stage 1: Drafting notebook for '{topic}'")
    save_state("drafting", topic)

    draft_prompt = f"""You are AGENT_SCIENTIST.
{prompts['AGENT_SCIENTIST']}

Topic: {topic}
Filename: {safe_topic}.ipynb
Output directory: {BASE_DIR}/notebooks/drafts/
"""

    success, output = run_agent(draft_prompt)
    if not success:
        log("Failed to create draft notebook", "ERROR")
        return

    # --- Stage 2: Review & Testing ---
    log("Stage 2: Testing code integrity...")
    save_state("reviewing", topic)

    draft_dir = os.path.join(BASE_DIR, "notebooks/drafts")
    draft_files = [f for f in os.listdir(draft_dir) if f.endswith(".ipynb")]

    if not draft_files:
        log("No draft notebook found. Agent may have failed to create it.", "ERROR")
        return

    # Get the target file (most recently modified)
    target_file = max(
        [os.path.join(draft_dir, f) for f in draft_files],
        key=os.path.getmtime
    )
    output_file = target_file.replace(".ipynb", "_executed.ipynb")

    log(f"Testing notebook: {os.path.basename(target_file)}")

    max_retries = 3
    verified = False

    for attempt in range(1, max_retries + 1):
        log(f"Execution attempt {attempt}/{max_retries}...")

        try:
            result = subprocess.run(
                ["papermill", target_file, output_file],
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.returncode == 0:
                log("Notebook executed successfully!")
                verified = True
                break
            else:
                log("Execution failed, extracting error...", "WARN")
                error_trace = extract_error_from_notebook(output_file)

                if not error_trace or error_trace == "No error traceback found in notebook":
                    error_trace = result.stderr or "Unknown execution error"

                log(f"Error: {error_trace[:300]}...")

                # Ask agent to fix
                fix_prompt = f"""You are AGENT_REVIEWER.
{prompts['AGENT_REVIEWER']}

File to fix: {target_file}

ERROR TRACEBACK:
{error_trace}

Read the file, identify the bug, and edit it to fix the error.
"""
                success, _ = run_agent(fix_prompt)
                if not success:
                    log("Agent failed to respond", "ERROR")

        except subprocess.TimeoutExpired:
            log("Papermill execution timed out", "ERROR")
        except Exception as e:
            log(f"Execution error: {str(e)}", "ERROR")

    if not verified:
        log("Failed to verify notebook after all retries", "ERROR")
        save_state("failed", topic)
        return

    # Move to published
    pub_dir = os.path.join(BASE_DIR, "notebooks/published")
    final_path = os.path.join(pub_dir, os.path.basename(target_file))
    shutil.move(target_file, final_path)

    # Clean up executed file
    if os.path.exists(output_file):
        os.remove(output_file)

    log(f"Notebook verified and moved to: {final_path}")

    # --- Stage 3: Publishing (Git) ---
    log("Stage 3: Publishing to repository...")
    save_state("publishing", topic)

    # Check if git is configured
    git_check = subprocess.run(
        ["git", "-C", BASE_DIR, "status"],
        capture_output=True
    )

    if git_check.returncode != 0:
        log("Git not initialized in pipeline directory. Skipping publish.", "WARN")
        git_url = None
    else:
        pub_prompt = f"""You are AGENT_PUBLISHER.
{prompts['AGENT_PUBLISHER']}

Working directory: {BASE_DIR}
File to publish: {final_path}
"""
        success, output = run_agent(pub_prompt)

        # Extract URL from output
        url_match = re.search(r'https://[^\s]+', output) if output else None
        git_url = url_match.group(0) if url_match else None

        if git_url:
            log(f"Published at: {git_url}")
        elif "AUTH_ERROR" in (output or ""):
            log("Git authentication failed. Configure SSH or credentials.", "WARN")

    # --- Stage 4: Social Media Content ---
    log("Stage 4: Generating social media content...")
    save_state("promoting", topic)

    social_prompt = f"""You are AGENT_PUBLICIST.
{prompts['AGENT_PUBLICIST']}

Source notebook: {final_path}
Guidelines file: {BASE_DIR}/templates/social_guidelines.md
Output file: {BASE_DIR}/output/social_posts/{safe_topic}_posts.txt

Read the notebook, extract key findings, and create social posts.
CRITICAL: Convert ALL LaTeX to Unicode symbols.
"""

    success, _ = run_agent(social_prompt)

    if success:
        log(f"Social posts saved to: output/social_posts/{safe_topic}_posts.txt")

    # Complete
    log("Pipeline complete!")
    save_state("idle", None)

if __name__ == "__main__":
    main()
