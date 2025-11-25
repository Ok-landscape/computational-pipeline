#!/bin/bash
# Automated setup script for social media automation system

set -e

echo "=================================================="
echo "LaTeX Template Social Media Automation Setup"
echo "=================================================="
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Step 1: Check Python version
echo "1. Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "   Found Python $python_version"

if ! command -v python3 &> /dev/null; then
    echo "   ERROR: Python 3 not found"
    exit 1
fi

# Step 2: Create virtual environment
echo ""
echo "2. Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "   Virtual environment created"
else
    echo "   Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate

# Step 3: Upgrade pip
echo ""
echo "3. Upgrading pip..."
pip install --upgrade pip --quiet

# Step 4: Install dependencies
echo ""
echo "4. Installing dependencies..."
pip install -r requirements.txt --quiet
echo "   Dependencies installed"

# Step 5: Create directory structure
echo ""
echo "5. Creating directory structure..."
mkdir -p data
mkdir -p media
mkdir -p config
mkdir -p logs
echo "   Directories created"

# Step 6: Set permissions
echo ""
echo "6. Setting permissions..."
chmod 755 data media logs
chmod 700 config
if [ -f ".env" ]; then
    chmod 600 .env
fi
chmod +x run_automation.py
echo "   Permissions set"

# Step 7: Copy example config
echo ""
echo "7. Setting up configuration..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "   .env file created from example"
    echo "   ⚠️  IMPORTANT: Edit .env and add your credentials!"
else
    echo "   .env file already exists"
fi

# Create default config files if they don't exist
if [ ! -f "config/platforms.yaml" ]; then
    cat > config/platforms.yaml << 'EOF'
platforms:
  facebook:
    enabled: true
    max_posts_per_day: 3
    optimal_times:
      - "09:00"
      - "13:00"
      - "19:00"

  threads:
    enabled: true
    max_posts_per_day: 2
    optimal_times:
      - "11:00"
      - "16:00"

  instagram:
    enabled: false
    max_posts_per_day: 1
    optimal_times:
      - "10:00"
      - "18:00"

settings:
  avoid_duplicate_days: 60
  prioritize_visuals: true
EOF
    echo "   Created config/platforms.yaml"
fi

if [ ! -f "config/scheduler_config.json" ]; then
    cat > config/scheduler_config.json << 'EOF'
{
  "max_posts_per_day": {
    "facebook": 3,
    "threads": 2,
    "instagram": 1
  },
  "avoid_duplicate_days": 60,
  "prioritize_visuals": true
}
EOF
    echo "   Created config/scheduler_config.json"
fi

# Step 8: Check template directory
echo ""
echo "8. Checking template directory..."
if [ -d "/home/user/latex-templates/templates" ]; then
    template_count=$(find /home/user/latex-templates/templates -name "*.tex" | wc -l)
    echo "   Template directory found ($template_count .tex files)"
else
    echo "   ⚠️  WARNING: Template directory not found at /home/user/latex-templates/templates"
fi

# Step 9: Optional - scan templates
echo ""
echo "9. Would you like to scan templates now? (y/n)"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    echo "   Scanning templates..."
    python run_automation.py scan
fi

# Completion
echo ""
echo "=================================================="
echo "Setup Complete!"
echo "=================================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Configure credentials:"
echo "   Edit .env and add your Facebook/Instagram credentials"
echo ""
echo "2. Validate setup:"
echo "   python run_automation.py validate"
echo ""
echo "3. Generate posting queue:"
echo "   python run_automation.py queue"
echo ""
echo "4. Start automation:"
echo "   python run_automation.py scheduler"
echo ""
echo "For detailed instructions, see SETUP.md"
echo ""
