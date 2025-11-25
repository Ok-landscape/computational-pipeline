# Social Media Automation Setup Guide

Complete setup instructions for automating LaTeX template social media posts across Facebook, Threads, and Instagram.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Authentication Setup](#authentication-setup)
5. [Initial Template Scan](#initial-template-scan)
6. [Running the System](#running-the-system)
7. [Scheduling Options](#scheduling-options)
8. [Monitoring and Maintenance](#monitoring-and-maintenance)

---

## Prerequisites

### System Requirements
- Linux environment (CoCalc or local)
- Python 3.8 or higher
- Access to `/home/user/latex-templates/templates/` directory
- Network access for API calls
- ~1GB disk space for media processing

### Required Python Packages
```bash
pip install requests python-dotenv Pillow PyMuPDF schedule pyyaml
```

### Social Media Accounts
- **Facebook**: Page with admin access
- **Facebook Developer Account**: For API access
- **Instagram** (optional): Business account linked to Facebook Page
- **Threads**: Uses Facebook infrastructure

---

## Installation

### Step 1: Navigate to Project Directory
```bash
cd /home/user/computational-pipeline/social-media-automation
```

### Step 2: Create Python Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install --upgrade pip

# Core dependencies
pip install requests==2.31.0
pip install python-dotenv==1.0.0
pip install Pillow==10.1.0
pip install PyMuPDF==1.23.0
pip install schedule==1.2.0
pip install pyyaml==6.0
```

### Step 4: Create Directory Structure
```bash
mkdir -p data
mkdir -p media
mkdir -p config
mkdir -p logs
chmod 755 data media logs
chmod 700 config  # Restricted for credentials
```

---

## Configuration

### Step 1: Create Configuration Files

#### `/home/user/computational-pipeline/social-media-automation/config/platforms.yaml`
```yaml
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
    enabled: false  # Enable when configured
    max_posts_per_day: 1
    optimal_times:
      - "10:00"
      - "18:00"

settings:
  avoid_duplicate_days: 60
  prioritize_visuals: true
  generate_composite_images: true
```

#### `/home/user/computational-pipeline/social-media-automation/config/scheduler_config.json`
```json
{
  "max_posts_per_day": {
    "facebook": 3,
    "threads": 2,
    "instagram": 1
  },
  "avoid_duplicate_days": 60,
  "prioritize_visuals": true,
  "day_themes": {
    "monday": ["physics", "quantum-physics", "astrophysics"],
    "tuesday": ["mathematics", "numerical-analysis"],
    "wednesday": ["machine-learning", "computer-science"],
    "thursday": ["engineering", "robotics"],
    "friday": ["biology", "chemistry", "bioinformatics"],
    "saturday": ["mixed"],
    "sunday": ["mixed"]
  }
}
```

---

## Authentication Setup

### Facebook & Threads Setup

#### Step 1: Create Facebook Business App

1. Go to https://developers.facebook.com
2. Click "My Apps" → "Create App"
3. Select "Business" as app type
4. Fill in:
   - App Name: "LaTeX Template Automation"
   - App Contact Email: your-email@example.com
   - Business Account: Select or create

#### Step 2: Configure App

1. Go to Settings → Basic
2. Note your **App ID** and **App Secret**
3. Add Platform: Website → `http://localhost:8000`
4. Add Privacy Policy URL

#### Step 3: Request Permissions

1. Go to App Review → Permissions and Features
2. Request:
   - `pages_manage_posts`
   - `pages_read_engagement`
   - `pages_show_list`

#### Step 4: Get Access Tokens

##### Option 1: Using Existing Facebook Automation

If you already have the `/home/user/facebook-automation` setup:

```bash
cd /home/user/facebook-automation
source venv/bin/activate
python exchange_token.py
```

Copy the credentials to the new location:
```bash
cp /home/user/facebook-automation/.env \
   /home/user/computational-pipeline/social-media-automation/.env
```

##### Option 2: Manual Token Exchange

```bash
cd /home/user/computational-pipeline/social-media-automation
source venv/bin/activate

# Run the token exchange utility
python << 'EOF'
import requests

def get_long_lived_token(app_id, app_secret, short_token):
    url = "https://graph.facebook.com/v24.0/oauth/access_token"
    params = {
        'grant_type': 'fb_exchange_token',
        'client_id': app_id,
        'client_secret': app_secret,
        'fb_exchange_token': short_token
    }
    response = requests.get(url, params=params)
    return response.json()

# Input your credentials
app_id = input("Enter App ID: ")
app_secret = input("Enter App Secret: ")

print("\nGet short-lived token:")
print("1. Go to: https://developers.facebook.com/tools/explorer/")
print("2. Select your app")
print("3. Generate Access Token")
print("4. Copy the token\n")

short_token = input("Paste short-lived token: ")

result = get_long_lived_token(app_id, app_secret, short_token)
print(f"\nLong-lived token: {result.get('access_token', 'ERROR')}")
EOF
```

### Step 5: Create Environment File

Create `/home/user/computational-pipeline/social-media-automation/.env`:

```bash
# Facebook/Threads Credentials
FB_APP_ID=your_app_id_here
FB_APP_SECRET=your_app_secret_here
FB_PAGE_ID=your_page_id_here
FB_PAGE_TOKEN=your_permanent_page_token_here

# Instagram Credentials (optional)
IG_BUSINESS_ACCOUNT_ID=your_instagram_business_id
IG_ACCESS_TOKEN=your_instagram_token

# GitHub Repository
GITHUB_REPO=Ok-landscape/computational-pipeline
COCALC_BASE_URL=https://cocalc.com/github/Ok-landscape/computational-pipeline
```

Set secure permissions:
```bash
chmod 600 .env
```

### Step 6: Validate Credentials

```bash
source venv/bin/activate
python social_publisher.py
```

Expected output:
```
Validating credentials...
facebook: ✓ Valid
threads: ✓ Valid
instagram: ✗ Invalid
```

---

## Initial Template Scan

### Step 1: Build Template Index

```bash
source venv/bin/activate
python template_scanner.py
```

This will:
- Scan all 201 templates across 66 categories
- Extract metadata from .tex files
- Catalog visualizations
- Save index to `data/template_index.json`

Expected output:
```
Scanning templates in /home/user/latex-templates/templates
Found 66 categories
...
Total templates indexed: 201
Index saved to data/template_index.json
```

### Step 2: Test Media Extraction

```bash
python media_extractor.py
```

This tests PDF-to-image conversion for social media.

### Step 3: Test Content Generation

```bash
python content_generator.py
```

This generates sample posts for all platforms.

---

## Running the System

### Option 1: Manual Single Post

Generate and publish one post immediately:

```bash
source venv/bin/activate

python << 'EOF'
from smart_scheduler import SmartScheduler

scheduler = SmartScheduler()
posts = scheduler.generate_weekly_schedule()

# Publish first post immediately
if posts:
    first_post = posts[0]
    scheduler.publish_post(first_post)
EOF
```

### Option 2: Generate Weekly Queue

Create a week's worth of scheduled posts:

```bash
python << 'EOF'
from smart_scheduler import SmartScheduler

scheduler = SmartScheduler()
posts = scheduler.generate_weekly_schedule()
scheduler.add_to_queue(posts)

print(f"Generated {len(posts)} scheduled posts")
print("Queue saved. Run scheduler to publish automatically.")
EOF
```

### Option 3: Run Continuous Scheduler

Start the automated scheduler:

```bash
python smart_scheduler.py
```

Or run in background:

```bash
nohup python smart_scheduler.py > logs/scheduler.log 2>&1 &
```

Check it's running:
```bash
ps aux | grep smart_scheduler
tail -f logs/scheduler.log
```

---

## Scheduling Options

### Option A: Cron Job (Recommended for CoCalc)

Edit crontab:
```bash
crontab -e
```

Add entries for posting times:
```cron
# Facebook posts (9 AM, 1 PM, 7 PM)
0 9 * * * cd /home/user/computational-pipeline/social-media-automation && /home/user/computational-pipeline/social-media-automation/venv/bin/python -c "from smart_scheduler import SmartScheduler; s = SmartScheduler(); posts = s.get_posts_due(); [s.publish_post(p) for p in posts if p.platform == 'facebook']" >> logs/cron.log 2>&1

0 13 * * * cd /home/user/computational-pipeline/social-media-automation && /home/user/computational-pipeline/social-media-automation/venv/bin/python -c "from smart_scheduler import SmartScheduler; s = SmartScheduler(); posts = s.get_posts_due(); [s.publish_post(p) for p in posts if p.platform == 'facebook']" >> logs/cron.log 2>&1

# Threads posts (11 AM, 4 PM)
0 11 * * * cd /home/user/computational-pipeline/social-media-automation && /home/user/computational-pipeline/social-media-automation/venv/bin/python -c "from smart_scheduler import SmartScheduler; s = SmartScheduler(); posts = s.get_posts_due(); [s.publish_post(p) for p in posts if p.platform == 'threads']" >> logs/cron.log 2>&1

# Weekly queue regeneration (Sunday midnight)
0 0 * * 0 cd /home/user/computational-pipeline/social-media-automation && /home/user/computational-pipeline/social-media-automation/venv/bin/python -c "from smart_scheduler import SmartScheduler; s = SmartScheduler(); posts = s.generate_weekly_schedule(); s.add_to_queue(posts)" >> logs/cron.log 2>&1
```

### Option B: Systemd Service

Create `/etc/systemd/system/latex-social-automation.service`:

```ini
[Unit]
Description=LaTeX Template Social Media Automation
After=network.target

[Service]
Type=simple
User=user
WorkingDirectory=/home/user/computational-pipeline/social-media-automation
Environment="PATH=/home/user/computational-pipeline/social-media-automation/venv/bin"
ExecStart=/home/user/computational-pipeline/social-media-automation/venv/bin/python smart_scheduler.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable latex-social-automation
sudo systemctl start latex-social-automation
sudo systemctl status latex-social-automation
```

### Option C: GitHub Actions

Create `.github/workflows/social-media-post.yml` in your repository:

```yaml
name: Automated Social Media Posting

on:
  schedule:
    # Facebook posts
    - cron: '0 9,13,19 * * *'  # 9 AM, 1 PM, 7 PM UTC
    # Threads posts
    - cron: '0 11,16 * * *'    # 11 AM, 4 PM UTC
  workflow_dispatch:  # Manual trigger

jobs:
  post-to-social-media:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          cd social-media-automation
          pip install -r requirements.txt

      - name: Run publisher
        env:
          FB_PAGE_ID: ${{ secrets.FB_PAGE_ID }}
          FB_PAGE_TOKEN: ${{ secrets.FB_PAGE_TOKEN }}
        run: |
          cd social-media-automation
          python -c "from smart_scheduler import SmartScheduler; s = SmartScheduler(); posts = s.get_posts_due(within_minutes=60); [s.publish_post(p) for p in posts]"
```

Add secrets in GitHub repository settings:
- Settings → Secrets and variables → Actions
- Add: `FB_PAGE_ID`, `FB_PAGE_TOKEN`

---

## Monitoring and Maintenance

### Daily Checks

#### View Queue Status
```bash
python << 'EOF'
from smart_scheduler import SmartScheduler
scheduler = SmartScheduler()
status = scheduler.get_queue_status()

print(f"Queued posts: {status['total_queued']}")
print(f"Next 24 hours: {status['next_24_hours']}")
for platform, count in status['by_platform'].items():
    print(f"  {platform}: {count}")
EOF
```

#### Check Recent Publications
```bash
python << 'EOF'
from social_publisher import SocialMediaPublisher
publisher = SocialMediaPublisher()
recent = publisher.get_recently_published(days=7)
print(f"Published in last 7 days: {len(recent)}")
for r in recent[-5:]:
    print(f"  {r['platform']}: {r['template_name']} at {r['timestamp'][:10]}")
EOF
```

#### View Logs
```bash
tail -n 50 logs/scheduler.log
grep ERROR logs/scheduler.log | tail -n 10
```

### Weekly Maintenance

#### Regenerate Queue
```bash
python << 'EOF'
from smart_scheduler import SmartScheduler
scheduler = SmartScheduler()
scheduler.queue = []  # Clear existing
posts = scheduler.generate_weekly_schedule()
scheduler.add_to_queue(posts)
print(f"Queue refreshed with {len(posts)} posts")
EOF
```

#### Update Template Index
```bash
python template_scanner.py
```

#### Check Credential Validity
```bash
python social_publisher.py
```

### Monthly Tasks

#### Clean Old Media Files
```bash
find media/ -type f -mtime +30 -delete
```

#### Archive Logs
```bash
tar -czf logs/archive_$(date +%Y%m).tar.gz logs/*.log
echo "" > logs/scheduler.log
```

#### Review Publishing Statistics
```bash
python << 'EOF'
from social_publisher import SocialMediaPublisher
from collections import Counter

publisher = SocialMediaPublisher()
history = publisher.get_recently_published(days=30)

platforms = Counter(r['platform'] for r in history)
print("Posts by platform (last 30 days):")
for platform, count in platforms.items():
    print(f"  {platform}: {count}")

templates = Counter(r['template_name'] for r in history)
print(f"\nUnique templates posted: {len(templates)}")
print("Top 5 most posted:")
for template, count in templates.most_common(5):
    print(f"  {template}: {count}")
EOF
```

---

## Troubleshooting

### Issue: No posts being published

**Check:**
1. Is scheduler running?
   ```bash
   ps aux | grep smart_scheduler
   ```

2. Are there posts in queue?
   ```bash
   python -c "from smart_scheduler import SmartScheduler; print(len(SmartScheduler().queue))"
   ```

3. Check credentials:
   ```bash
   python social_publisher.py
   ```

### Issue: Image extraction failing

**Solution:**
Install PyMuPDF:
```bash
pip install --upgrade PyMuPDF
```

Or fallback to ImageMagick:
```bash
sudo apt-get install imagemagick
```

### Issue: Rate limit errors

**Solution:**
Reduce posting frequency in `config/platforms.yaml`:
```yaml
max_posts_per_day: 1  # Lower this
```

### Issue: Posts missing images

**Check:**
1. Do PDFs exist?
   ```bash
   ls -la /home/user/latex-templates/templates/*/*.pdf | head -10
   ```

2. Test extraction:
   ```bash
   python media_extractor.py
   ```

---

## Advanced Configuration

### Custom Content Templates

Edit `content_generator.py` to customize post formats.

### Custom Scheduling Rules

Edit `smart_scheduler.py` `DAY_THEMES` and `OPTIMAL_TIMES`.

### Integration with Existing System

Link with `/home/user/facebook-automation`:

```bash
# Share credentials
ln -s /home/user/facebook-automation/.env .env

# Share publishing history
ln -s /home/user/facebook-automation/content/generated_posts/published \
      data/legacy_posts
```

---

## Support and Documentation

- Architecture: See `ARCHITECTURE.md`
- API Documentation: https://developers.facebook.com/docs/graph-api
- CoCalc Documentation: https://doc.cocalc.com/

---

**Congratulations!** Your LaTeX template social media automation is now set up and running.

For questions or issues, check the logs first:
```bash
tail -f logs/scheduler.log
```
