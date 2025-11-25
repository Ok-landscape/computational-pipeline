# Quick Start Guide - 5 Minutes to First Post

## Prerequisites
- Facebook Page with admin access
- Facebook Developer App created
- Access to `/home/user/latex-templates/templates/`

## Step-by-Step Setup

### 1. Run Automated Setup (2 minutes)
```bash
cd /home/user/computational-pipeline/social-media-automation
bash setup.sh
```

This will:
- Create virtual environment
- Install dependencies
- Create directory structure
- Generate configuration files

### 2. Configure Credentials (2 minutes)

Edit `.env` file:
```bash
nano .env
```

Add your credentials:
```env
FB_APP_ID=123456789012345
FB_APP_SECRET=abc123def456...
FB_PAGE_ID=987654321098765
FB_PAGE_TOKEN=EAABwz...  # Your permanent page token
```

**Getting Tokens:**
- Already have `/home/user/facebook-automation` setup? Copy credentials:
  ```bash
  cp /home/user/facebook-automation/.env .env
  ```

- Need to create tokens? See SETUP.md section on "Authentication Setup"

### 3. Validate Setup (30 seconds)
```bash
source venv/bin/activate
python run_automation.py validate
```

Expected output:
```
✓ All directories exist
✓ Templates found (201 files)
✓ Facebook credentials valid
✓ Setup validation passed!
```

### 4. Scan Templates (30 seconds)
```bash
python run_automation.py scan
```

Output:
```
Scanned 201 templates across 66 categories
Templates with visualizations: 180+
Index saved to data/template_index.json
```

### 5. Generate First Post (Test Mode - 30 seconds)
```bash
python run_automation.py test
```

This shows you what posts will look like WITHOUT publishing.

### 6. Publish Your First Post (30 seconds)
```bash
# Generate a single post and publish immediately
python << 'EOF'
from smart_scheduler import SmartScheduler
scheduler = SmartScheduler()

# Generate one post
posts = scheduler.generate_weekly_schedule()
if posts:
    first_post = posts[0]
    print(f"Publishing: {first_post.template.title}")
    print(f"Platform: {first_post.platform}")
    success = scheduler.publish_post(first_post)
    if success:
        print("✓ Successfully published!")
    else:
        print("✗ Publishing failed - check logs")
EOF
```

### 7. Set Up Automation (Optional)

For continuous automated posting:

**Option A: Run Scheduler Process**
```bash
# Run in background
nohup python run_automation.py scheduler > logs/scheduler.log 2>&1 &
```

**Option B: Cron Jobs**
```bash
crontab -e
```

Add:
```cron
# Facebook posts at 9 AM daily
0 9 * * * cd /home/user/computational-pipeline/social-media-automation && venv/bin/python run_automation.py publish --platform facebook >> logs/cron.log 2>&1
```

## What You Get

### Automated Posts Across Platforms

**Facebook Example:**
```
📐 Sound Propagation Analysis: Wave Equations and Transmission Loss

Analysis of sound wave propagation through various media, including
acoustic impedance and transmission coefficients.

🔬 COMPUTATIONAL APPROACH
• Python integration via PythonTeX
• NumPy for vectorized operations
• Matplotlib for visualizations

✨ KEY FEATURES
• Reproducible computational results
• Interactive PDF with references

👉 Explore on CoCalc: [link]

#Acoustics #ComputationalPhysics #LaTeX #Python
```

**Threads Example:**
```
Ever wondered how to model sound propagation? 🤔

Computational analysis of acoustic wave equations.

✨ Built with Python + LaTeX
🔗 Full code + visuals available

#Acoustics #Python #Science
```

**Instagram Example:**
```
🔊 Sound Propagation Analysis

📊 Computational visualization showing acoustic impedance
and wave propagation through different materials.

🔬 Intermediate level analysis with numerical methods.

⚙️ Built with: Python • NumPy • Matplotlib • LaTeX

💡 Link in bio to explore on CoCalc!

#Acoustics #ComputationalPhysics #LaTeX #Python #DataScience
```

## Daily Commands

```bash
# Check what's scheduled
python run_automation.py show

# Publish posts that are due
python run_automation.py publish

# Preview a post
python run_automation.py test

# Generate weekly queue
python run_automation.py queue
```

## Troubleshooting

### Error: "Missing credentials"
- Check `.env` file exists and has correct values
- Run: `python run_automation.py validate`

### Error: "Templates not found"
- Verify path: `ls /home/user/latex-templates/templates/`
- Templates should be at this location

### Error: "PyMuPDF not found"
- Install: `pip install PyMuPDF`
- Or use ImageMagick: `sudo apt-get install imagemagick`

### Posts not publishing
- Check credentials: `python run_automation.py validate`
- Check queue: `python run_automation.py show`
- Check logs: `tail -f logs/scheduler.log`

## What's Next?

1. **Generate Weekly Queue:**
   ```bash
   python run_automation.py queue
   ```
   This creates a week's worth of scheduled posts.

2. **Monitor Operations:**
   ```bash
   python run_automation.py show  # Daily
   tail -f logs/scheduler.log     # As needed
   ```

3. **Review Statistics:**
   See OPERATIONS.md for weekly/monthly procedures

## Quick Tips

- **Test before going live**: Use `test` command extensively
- **Start small**: Begin with 1-2 posts per day
- **Monitor engagement**: Check Facebook/Instagram analytics
- **Adjust hashtags**: Based on what performs well
- **Vary content**: System automatically rotates through categories

## Full Documentation

- **README.md**: Complete overview and features
- **SETUP.md**: Detailed setup instructions
- **ARCHITECTURE.md**: System design and architecture
- **OPERATIONS.md**: Day-to-day operations
- **IMPLEMENTATION_SUMMARY.md**: Technical details

## Need Help?

1. Check logs: `tail -f logs/scheduler.log`
2. Validate setup: `python run_automation.py validate`
3. Review documentation in this directory
4. Test without publishing: `python run_automation.py test`

---

**Congratulations!** You're now automating social media posts for 201 LaTeX templates across 66 scientific categories!

**Time Investment:**
- Setup: 5 minutes
- First post: Immediate
- Weekly maintenance: 5-10 minutes

**Benefits:**
- Automated daily posts
- Platform-optimized content
- Professional visuals
- Educational messaging
- Zero ongoing effort

**Start here**: `bash setup.sh`
