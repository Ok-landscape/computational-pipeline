# LaTeX Template Social Media Automation

Automated social media publishing system for highlighting computational LaTeX templates across Facebook, Threads, and Instagram.

## Overview

This system automatically generates and publishes engaging, platform-specific social media posts showcasing the 201 LaTeX templates from the computational-pipeline repository. Each post includes:

- Platform-optimized content (Facebook: detailed, Threads: conversational, Instagram: visual)
- Extracted visualizations from PDFs
- Direct links to CoCalc viewer for interactive exploration
- Relevant hashtags and technical details
- Intelligent scheduling to maximize engagement

## Features

### Multi-Platform Support
- **Facebook**: Educational posts with comprehensive explanations (up to 63,206 characters)
- **Threads**: Quick, engaging conversation-starters (500 characters)
- **Instagram**: Visual storytelling with plots and equations (2,200 characters)

### Intelligent Content Generation
- Platform-specific formatting and tone
- Dynamic hashtag generation based on category
- Complexity-aware descriptions
- Mathematical and computational context

### Smart Scheduling
- Optimal posting times per platform
- Category-based weekly themes (Physics Monday, Math Tuesday, etc.)
- Duplicate prevention (60-day lookback)
- Priority-based queue management

### Media Processing
- PDF-to-image extraction
- Platform-specific optimization (resolution, format, aspect ratio)
- Composite image creation (document + plots)
- Automatic alt-text generation for accessibility

## Quick Start

### 1. Installation

```bash
cd /home/user/computational-pipeline/social-media-automation

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Create `.env` file with your credentials:
```bash
FB_PAGE_ID=your_page_id
FB_PAGE_TOKEN=your_page_token
```

### 3. Validate Setup

```bash
python run_automation.py validate
```

### 4. Scan Templates

```bash
python run_automation.py scan
```

### 5. Generate Queue

```bash
python run_automation.py queue
```

### 6. Start Automation

```bash
python run_automation.py scheduler
```

## Usage

### Command-Line Interface

```bash
# Scan and index templates
python run_automation.py scan

# Generate weekly posting queue
python run_automation.py queue

# Show current queue status
python run_automation.py show

# Publish posts due now
python run_automation.py publish

# Test post generation
python run_automation.py test --template sound_propagation

# Validate credentials and setup
python run_automation.py validate

# Run continuous scheduler
python run_automation.py scheduler
```

### Python API

```python
from smart_scheduler import SmartScheduler

# Initialize scheduler
scheduler = SmartScheduler()

# Generate weekly schedule
posts = scheduler.generate_weekly_schedule()

# Add to queue
scheduler.add_to_queue(posts)

# Get queue status
status = scheduler.get_queue_status()
print(f"Queued posts: {status['total_queued']}")

# Publish due posts
due_posts = scheduler.get_posts_due(within_minutes=60)
for post in due_posts:
    scheduler.publish_post(post)
```

## Project Structure

```
social-media-automation/
├── ARCHITECTURE.md              # System architecture documentation
├── SETUP.md                     # Detailed setup instructions
├── README.md                    # This file
├── requirements.txt             # Python dependencies
│
├── run_automation.py            # Main CLI interface
├── template_scanner.py          # Template discovery and indexing
├── content_generator.py         # Platform-specific content generation
├── media_extractor.py           # PDF image extraction and optimization
├── social_publisher.py          # Multi-platform API integration
├── smart_scheduler.py           # Scheduling and queue management
│
├── config/                      # Configuration files
│   ├── platforms.yaml           # Platform settings
│   └── scheduler_config.json    # Scheduling configuration
│
├── data/                        # Generated data
│   ├── template_index.json      # Template metadata index
│   ├── post_queue.json          # Scheduled post queue
│   └── publish_history.json     # Publishing history
│
├── media/                       # Processed images
│   └── [category]_[template]_[platform].[ext]
│
└── logs/                        # Application logs
    └── scheduler.log
```

## Key Components

### 1. Template Scanner (`template_scanner.py`)
- Scans `/home/user/latex-templates/templates/`
- Extracts metadata from .tex files
- Catalogs visualizations (PDFs, plots)
- Generates searchable index

### 2. Content Generator (`content_generator.py`)
- Creates platform-specific posts
- Generates relevant hashtags
- Adapts tone and length per platform
- Highlights computational features

### 3. Media Extractor (`media_extractor.py`)
- Converts PDFs to images using PyMuPDF
- Optimizes for platform requirements
- Creates composite visualizations
- Generates accessibility alt-text

### 4. Social Publisher (`social_publisher.py`)
- Facebook Graph API integration
- Threads API support
- Instagram Business API (configured separately)
- Rate limiting and error handling

### 5. Smart Scheduler (`smart_scheduler.py`)
- Optimal posting time calculation
- Weekly theme-based scheduling
- Duplicate prevention
- Priority queue management

## Configuration

### Platform Settings (`config/platforms.yaml`)

```yaml
platforms:
  facebook:
    enabled: true
    max_posts_per_day: 3
    optimal_times: ["09:00", "13:00", "19:00"]

  threads:
    enabled: true
    max_posts_per_day: 2
    optimal_times: ["11:00", "16:00"]

  instagram:
    enabled: false
    max_posts_per_day: 1
    optimal_times: ["10:00", "18:00"]
```

### Scheduler Configuration (`config/scheduler_config.json`)

```json
{
  "max_posts_per_day": {
    "facebook": 3,
    "threads": 2,
    "instagram": 1
  },
  "avoid_duplicate_days": 60,
  "prioritize_visuals": true
}
```

## Scheduling Options

### Cron Jobs

```bash
# Facebook posts (9 AM, 1 PM, 7 PM)
0 9,13,19 * * * cd /home/user/computational-pipeline/social-media-automation && venv/bin/python run_automation.py publish --platform facebook

# Threads posts (11 AM, 4 PM)
0 11,16 * * * cd /home/user/computational-pipeline/social-media-automation && venv/bin/python run_automation.py publish --platform threads

# Weekly queue regeneration (Sunday midnight)
0 0 * * 0 cd /home/user/computational-pipeline/social-media-automation && venv/bin/python run_automation.py queue
```

### Systemd Service

```bash
sudo systemctl enable latex-social-automation
sudo systemctl start latex-social-automation
```

### GitHub Actions

Automate from repository updates (see SETUP.md for workflow configuration).

## Example Posts

### Facebook Post
```
📐 Sound Propagation Analysis: Wave Equations and Transmission Loss

Analysis of sound wave propagation through various media, including acoustic
impedance, transmission coefficients, and transmission loss calculations.

🔬 COMPUTATIONAL APPROACH
• Python integration via PythonTeX for numerical computations
• NumPy arrays for efficient vectorized operations
• Matplotlib for publication-quality visualizations

✨ KEY FEATURES
• Proper SI unit formatting throughout
• Interactive PDF with clickable references
• Reproducible computational results

🎯 APPLICATIONS
Technical reports, design analysis, system modeling

👉 Explore on CoCalc: [link]

#Acoustics #ComputationalPhysics #LaTeX #Python #ScientificComputing
```

### Threads Post
```
Ever wondered how to model sound propagation? 🤔

Computational analysis of acoustic wave equations through different materials.

✨ Built with Python + LaTeX
🔗 Full code + visuals available

#Acoustics #ComputationalScience #Python
```

### Instagram Post
```
🔊 Sound Propagation Analysis

📊 What you're seeing:
Analysis of sound wave propagation through various media, including acoustic
impedance, transmission coefficients, and transmission loss calculations.

🔬 Intermediate level analysis with numerical methods.

⚙️ Built with: Python • NumPy • Matplotlib • LaTeX

💡 Want to explore this yourself?
Link in bio to view the full template on CoCalc!

#Acoustics #ComputationalPhysics #LaTeX #Python #ScientificComputing
#DataScience #Research #STEM #ScienceEducation
```

## Monitoring

### View Queue Status
```bash
python run_automation.py show
```

### Check Recent Publications
```bash
python -c "from social_publisher import SocialMediaPublisher; p = SocialMediaPublisher(); r = p.get_recently_published(days=7); print(f'Published: {len(r)}')"
```

### View Logs
```bash
tail -f logs/scheduler.log
```

## Maintenance

### Daily
- Check queue status
- Verify posts published successfully
- Monitor error logs

### Weekly
- Regenerate posting queue
- Update template index
- Review engagement metrics

### Monthly
- Validate credentials
- Clean old media files
- Archive logs
- Review posting statistics

## Troubleshooting

### No Posts Publishing
1. Check if scheduler is running: `ps aux | grep smart_scheduler`
2. Verify credentials: `python run_automation.py validate`
3. Check queue: `python run_automation.py show`

### Image Extraction Failing
- Install PyMuPDF: `pip install --upgrade PyMuPDF`
- Or install ImageMagick: `sudo apt-get install imagemagick`

### Rate Limit Errors
- Reduce `max_posts_per_day` in configuration
- Increase time between posts

## Integration

### With Existing Facebook Automation
```bash
# Link credentials
ln -s /home/user/facebook-automation/.env .env

# Use existing infrastructure
python run_automation.py validate
```

### With GitHub Repository
- Templates synced from: `https://github.com/Ok-landscape/computational-pipeline`
- CoCalc viewer base: `https://cocalc.com/github/Ok-landscape/computational-pipeline`

## Requirements

- Python 3.8+
- Linux environment (CoCalc or local)
- Access to LaTeX templates directory
- Facebook Page with admin access
- Facebook Developer App credentials
- ~1GB disk space for media processing

## Dependencies

```
requests==2.31.0
python-dotenv==1.0.0
Pillow==10.1.0
PyMuPDF==1.23.0
schedule==1.2.0
pyyaml==6.0
```

## Documentation

- **ARCHITECTURE.md**: System architecture and design decisions
- **SETUP.md**: Comprehensive setup and configuration guide
- **README.md**: This file - overview and quick reference

## Statistics

- **Templates**: 201 computational LaTeX templates
- **Categories**: 66 scientific domains
- **Platforms**: 3 (Facebook, Threads, Instagram)
- **Daily Posts**: 3-6 across all platforms
- **Full Rotation**: ~67 days at 3 posts/day

## License

Part of the computational-pipeline project.

## Support

For issues or questions:
1. Check logs: `tail -f logs/scheduler.log`
2. Validate setup: `python run_automation.py validate`
3. Review SETUP.md for detailed troubleshooting

---

**Status**: Production Ready

Built with computational excellence for science communication.
