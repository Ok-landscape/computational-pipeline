#!/bin/bash
# setup.sh - Initialize the CoCalc Autonomous Pipeline
# This is a simplified setup that creates directories and templates.
# Tools (claude, papermill) are assumed to be already installed.

set -e

echo "Setting up CoCalc Autonomous Pipeline..."

BASE_DIR="$HOME/computational_pipeline"

# --- Create Directory Structure ---
echo "Creating directory structure..."
mkdir -p "$BASE_DIR/orchestration"
mkdir -p "$BASE_DIR/notebooks/drafts"
mkdir -p "$BASE_DIR/notebooks/published"
mkdir -p "$BASE_DIR/templates"
mkdir -p "$BASE_DIR/output/social_posts"

# --- Initialize State Files ---
if [ ! -f "$BASE_DIR/orchestration/state.json" ]; then
    echo '{"current_stage": "idle", "active_task": null}' > "$BASE_DIR/orchestration/state.json"
fi
touch "$BASE_DIR/orchestration/logs.jsonl"

# --- Create Auth Directory ---
mkdir -p "$HOME/.config/claude-code"

# --- Verify Tools ---
echo ""
echo "Checking required tools..."

if command -v claude &> /dev/null; then
    echo "  Claude CLI: OK"
else
    echo "  Claude CLI: NOT FOUND"
    echo "    Install with: npm install -g @anthropic-ai/claude-code"
fi

if command -v papermill &> /dev/null; then
    echo "  Papermill: OK"
else
    echo "  Papermill: NOT FOUND"
    echo "    Install with: pip install papermill nbformat"
fi

if command -v git &> /dev/null; then
    echo "  Git: OK"
else
    echo "  Git: NOT FOUND (optional, for publishing)"
fi

# --- Authentication Instructions ---
echo ""
echo "========================================"
echo "  AUTHENTICATION REQUIRED"
echo "========================================"
echo ""
echo "CoCalc is headless - 'claude login' won't work here."
echo ""
echo "To authenticate:"
echo "1. On your LOCAL machine, run: claude login"
echo "2. Locate the credentials file:"
echo "   - Mac/Linux: ~/.config/claude-code/"
echo "   - Windows: %APPDATA%/Claude/"
echo "3. Upload to CoCalc at: ~/.config/claude-code/"
echo ""
echo "========================================"
echo ""
echo "Setup complete!"
echo "Directory: $BASE_DIR"
echo ""
echo "To run the pipeline:"
echo "  cd $BASE_DIR && python3 workflow.py"
