# Social Media Automation Architecture for LaTeX Templates

## Overview

This system automatically generates and publishes platform-specific social media content highlighting LaTeX computational templates from the `computational-pipeline` repository.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    LaTeX Template Source                     │
│   /home/user/latex-templates/templates (201 templates)      │
│             66 categories, PDFs + matplotlib plots           │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Template Discovery & Indexing                   │
│  • Scan categories and templates                            │
│  • Extract metadata from .tex files                         │
│  • Catalog available visualizations (PDFs, plots)           │
│  • Track posting history to avoid duplicates                │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Content Generation Engine                       │
│  • Template selection strategy (variety, rotation)          │
│  • Platform-specific content generation:                    │
│    - Facebook: Detailed educational posts (up to 63,206)    │
│    - Threads: Conversational threads (500 chars)            │
│    - Instagram: Visual storytelling (2,200 chars)           │
│  • Dynamic link generation to CoCalc viewer                  │
│  • Hashtag optimization per platform                        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Media Processing Pipeline                       │
│  • Extract first page from PDF as preview image             │
│  • Extract matplotlib plots from PDF                         │
│  • Image optimization (resize, compress for each platform)  │
│  • Alt-text generation for accessibility                    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Multi-Platform Publisher                        │
│  • Facebook Graph API (pages_manage_posts)                  │
│  • Threads API (via Facebook Graph API)                     │
│  • Instagram Graph API (business accounts)                  │
│  • Error handling and retry logic                           │
│  • Rate limiting compliance                                 │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│            Scheduling & Queue Management                     │
│  • Posting schedule (optimal times per platform)            │
│  • Content queue with priority system                       │
│  • Conflict resolution (no duplicate posts same day)        │
│  • Manual override capability                               │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│         Analytics & History Tracking                         │
│  • Track published posts per platform                       │
│  • Record engagement metrics                                │
│  • Template coverage analysis                               │
│  • Posting statistics and reports                           │
└─────────────────────────────────────────────────────────────┘
```

## Key Components

### 1. Template Discovery Module (`template_scanner.py`)
- Recursively scans `/home/user/latex-templates/templates/`
- Extracts metadata: category, template name, description
- Identifies available visualizations
- Maintains template index database

### 2. Content Synthesizer (`content_synthesizer.py`)
- **Facebook Strategy**: Educational, detailed explanations
  - Title + comprehensive description
  - Mathematical context and applications
  - Code snippet highlights
  - Link to CoCalc viewer
  - Rich hashtags (#ComputationalPhysics, #LaTeX, etc.)

- **Threads Strategy**: Conversational and engaging
  - Hook statement
  - Brief explanation
  - Practical use case
  - Call to action
  - Minimal hashtags

- **Instagram Strategy**: Visual-first storytelling
  - Eye-catching description
  - Visual elements emphasized
  - Emojis for engagement
  - Research/science hashtags

### 3. Media Extractor (`media_extractor.py`)
- Uses PyMuPDF (fitz) for PDF processing
- Extracts first page as preview (1200x1200 for Instagram)
- Extracts individual plot PDFs as PNG
- Optimizes images per platform requirements
- Generates accessibility alt-text

### 4. Multi-Platform Publisher (`social_publisher.py`)
- **Facebook**: Graph API v24.0, pages_manage_posts permission
- **Threads**: Integrated via Facebook Graph API
- **Instagram**: Business account via Graph API
- Handles authentication, token refresh
- Implements exponential backoff for rate limits

### 5. Scheduler (`smart_scheduler.py`)
- Optimal posting times:
  - Facebook: 9 AM, 1 PM, 7 PM
  - Threads: 11 AM, 4 PM
  - Instagram: 10 AM, 6 PM
- Category-based distribution (physics Monday, math Tuesday, etc.)
- Avoids duplicate templates within 60 days
- Priority queue for featured templates

## Data Flow

1. **Discovery Phase**: Scan templates, build index
2. **Selection Phase**: Choose template based on strategy
3. **Content Generation**: Create platform-specific posts
4. **Media Processing**: Extract and optimize images
5. **Queueing**: Add to scheduled queue
6. **Publishing**: Post to platforms at optimal times
7. **Tracking**: Record metrics and update history

## Configuration Files

### `/config/platforms.yaml`
```yaml
facebook:
  enabled: true
  page_id: "YOUR_PAGE_ID"
  max_chars: 63206
  optimal_times: ["09:00", "13:00", "19:00"]

threads:
  enabled: true
  max_chars: 500
  optimal_times: ["11:00", "16:00"]

instagram:
  enabled: true
  account_id: "YOUR_IG_BUSINESS_ID"
  max_chars: 2200
  optimal_times: ["10:00", "18:00"]
```

### `/config/content_strategy.yaml`
```yaml
categories:
  physics:
    hashtags: ["#Physics", "#ComputationalPhysics", "#Science"]
    priority: high

  mathematics:
    hashtags: ["#Mathematics", "#AppliedMath", "#MathScience"]
    priority: high

  machine-learning:
    hashtags: ["#MachineLearning", "#AI", "#DataScience"]
    priority: medium
```

## Link Generation

CoCalc viewer URLs follow this pattern:
```
https://cocalc.com/github/Ok-landscape/computational-pipeline/tree/main/latex-templates/templates/{category}/{template}.tex
```

Examples:
- `https://cocalc.com/github/Ok-landscape/computational-pipeline/tree/main/latex-templates/templates/acoustics/sound_propagation.tex`
- `https://cocalc.com/github/Ok-landscape/computational-pipeline/tree/main/latex-templates/templates/astronomy/stellar_evolution.tex`

## Scheduling Strategy

### Daily Schedule (Example)
- **Monday**: Quantum Physics templates
- **Tuesday**: Mathematical Methods
- **Wednesday**: Machine Learning
- **Thursday**: Engineering Applications
- **Friday**: Mixed/Featured templates
- **Weekend**: Popular/Introductory topics

### Posting Frequency
- Facebook: 2-3 posts/day
- Threads: 1-2 posts/day
- Instagram: 1 post/day

### Content Rotation
- 201 templates across 66 categories
- Average 3 templates per category
- Full rotation cycle: ~67 days at 3 posts/day
- Ensures content freshness and variety

## Security & Authentication

### Credentials Management
- Environment variables via `.env` file
- Separate tokens per platform
- Token refresh automation
- Secure credential storage (chmod 600)

### Required Permissions
- **Facebook**: `pages_manage_posts`, `pages_read_engagement`
- **Threads**: Included with Facebook permissions
- **Instagram**: `instagram_basic`, `instagram_content_publish`

## Monitoring & Maintenance

### Health Checks
- Token validity (daily)
- API rate limit status (real-time)
- Queue status (hourly)
- Failed post retry (automatic)

### Logging
- Post publication log
- Error and retry log
- Template selection history
- Analytics and metrics log

### Maintenance Tasks
- Weekly: Review posting performance
- Monthly: Update content strategy based on engagement
- Quarterly: Token renewal check
- Annual: System audit and optimization

## Integration Points

### GitHub Repository
- Source: `https://github.com/Ok-landscape/computational-pipeline`
- Templates path: `/latex-templates/templates/`
- Workflow triggers: Can be integrated with GitHub Actions

### CoCalc Platform
- Viewer URL base: `https://cocalc.com/github/Ok-landscape/computational-pipeline/`
- Direct template access for users
- Real-time rendering and interaction

### Existing Facebook Automation
- Located at: `/home/user/facebook-automation`
- Can be extended with new modules
- Shared authentication infrastructure

## Success Metrics

### Coverage Metrics
- Templates posted vs total templates
- Category distribution balance
- Posting frequency consistency

### Engagement Metrics
- Reach and impressions per platform
- Click-through rate to CoCalc viewer
- Engagement rate (likes, comments, shares)

### System Metrics
- Uptime and reliability
- Failed post rate
- Average processing time per post

## Future Enhancements

1. **AI-Generated Descriptions**: Use LLM to create more engaging content
2. **A/B Testing**: Test different post formats and times
3. **Interactive Content**: Polls, questions, code challenges
4. **Video Content**: Create short explainer videos from PDFs
5. **Community Management**: Automated response to common questions
6. **Cross-Platform Analytics**: Unified dashboard for all platforms
7. **Template Request System**: Let followers request specific topics
8. **Collaborative Filtering**: Recommend templates based on engagement

## Technical Requirements

### Dependencies
```
python >= 3.8
requests >= 2.31.0
PyMuPDF >= 1.23.0
Pillow >= 10.1.0
pyyaml >= 6.0
python-dotenv >= 1.0.0
schedule >= 1.2.0
```

### System Requirements
- Linux environment (CoCalc or local)
- Access to `/home/user/latex-templates/templates/`
- Network access for API calls
- Disk space for image processing (~500MB)
- Cron or systemd for scheduling

## Deployment Options

### Option 1: CoCalc Hosted
- Run directly in CoCalc environment
- Use CoCalc's scheduling features
- Leverage existing file structure

### Option 2: GitHub Actions
- Trigger from repository updates
- Serverless execution
- Automatic on new template commits

### Option 3: Dedicated Server
- VPS or cloud instance
- Full control over scheduling
- Enhanced monitoring capabilities

## Getting Started

See `SETUP.md` for detailed installation and configuration instructions.
