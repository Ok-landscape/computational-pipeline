# Dual-Content, Dual-Page System - Complete Guide

## Executive Summary

The enhanced social media automation system integrates **LaTeX templates** and **computational notebooks** across **two Facebook pages** (CoCalc and SageMath), implementing intelligent routing, duplicate handling, and unified queue management.

**Key Metrics**:
- **Content Sources**: 201 templates + 7 notebooks (with posts)
- **Target Pages**: 2 (CoCalc + SageMath)
- **Posting Rate**: 2 posts/day per page = 4 posts/day total
- **Content Mix**: 50% templates, 50% notebooks
- **Duplicate Strategy**: Spread across 2+ days with tailored messaging

---

## System Architecture

### New Components (v2.0)

#### 1. `page_router.py` - Content Routing
Routes content to appropriate pages based on type and characteristics.

**Routing Rules**:
```
CoCalc Page (698630966948910):
  ✓ ALL templates
  ✓ ALL notebooks

SageMath Page (26593144945):
  ✓ Templates with SageTeX
  ✓ Templates in math categories (algebra, topology, number theory, etc.)
  ✓ Templates/notebooks with math keywords (symbolic, sage, algebra, etc.)
```

**Example Usage**:
```python
from page_router import PageRouter

router = PageRouter()

# Route a SageTeX template
template = {
    'template_name': 'group_theory.tex',
    'category': 'mathematics',
    'has_sagetex': True
}
routes = router.route_template(template)
# Result: [CoCalc, SageMath] - goes to both pages
```

#### 2. `unified_queue_manager.py` - Queue Management
Single unified queue for both content types with duplicate tracking.

**Features**:
- Per-page and per-platform filtering
- Duplicate group tracking
- Same-day duplicate validation
- Content type statistics

**Key Data Structure**:
```python
@dataclass
class QueuedContent:
    content_id: str
    content_type: str  # 'template' or 'notebook'
    page_id: str
    page_name: str
    platform: str
    content_text: str
    hashtags: List[str]
    link: str
    scheduled_time: str
    is_duplicate: bool
    duplicate_group_id: Optional[str]
```

#### 3. `duplicate_content_handler.py` - Duplicate Management
Handles content posted to multiple pages.

**Strategies**:
1. **Temporal Spreading**: Minimum 2-day gap between duplicates
2. **Message Tailoring**: Page-specific introductions
3. **Hashtag Adjustment**: Audience-appropriate tags
4. **Variation Text**: Slight variations to avoid exact duplicates

**Example**:
```
Original Schedule: Tuesday 9:00 AM
↓
CoCalc Post: Tuesday 9:00 AM
  Prefix: "Computational science templates on CoCalc."
  Tags: #CoCalc #ComputationalScience #ReproducibleResearch

SageMath Post: Thursday 9:00 AM (+2 days)
  Prefix: "Mathematical computation at its finest!"
  Tags: #SageMath #SymbolicMath #PureMath
```

#### 4. `enhanced_scheduler.py` - Main Orchestrator
Integrates all components into unified workflow.

**Process**:
```
1. Scan templates and notebooks
2. For each day:
   a. Select content based on day theme
   b. Route to appropriate pages
   c. Generate platform-specific posts
   d. Extract media
   e. Handle duplicate scheduling
3. Add to unified queue
4. Validate for conflicts
```

---

## Configuration

### Environment Variables (`.env`)

```bash
# Dual-Page Configuration
FB_PAGE_ID_COCALC=698630966948910
FB_PAGE_ID_SAGEMATH=26593144945
FB_PAGE_ID=698630966948910  # Legacy default

# Publishing Configuration
POSTS_PER_DAY_PER_PAGE=2
DRY_RUN=false

# Routing Configuration
ENABLE_DUAL_PAGE_ROUTING=true
SPREAD_DUPLICATES_ACROSS_DAYS=true
DUPLICATE_SPREAD_MIN_DAYS=2
```

### Day Themes

Content selection varies by weekday:

| Day | Themes |
|-----|--------|
| Monday | Physics, Quantum Physics, Engineering |
| Tuesday | Mathematics, Algebra, Calculus |
| Wednesday | Machine Learning, Data Science, AI |
| Thursday | Biology, Chemistry, Bioinformatics |
| Friday | Statistics, Numerical Analysis |
| Saturday | Mixed/Popular |
| Sunday | Introductory/Tutorials |

---

## Operational Workflows

### 1. Generate Weekly Schedule

```bash
cd /home/user/computational-pipeline/social-media-automation
python3 enhanced_scheduler.py
```

**What Happens**:
1. Scans 201 templates and 7 notebooks
2. Generates 7 days × 2 pages × 2 posts = 28 content items
3. Routes based on page criteria
4. Spreads duplicates across days
5. Saves to unified queue
6. Shows statistics

**Sample Output**:
```
Queue Statistics
================
Total queued: 35
Next 24 hours: 6
Next 7 days: 35
Duplicate items: 12

By content type:
  template: 22
  notebook: 13

By page:
  CoCalc: 29
  SageMath: 6

Sample Daily Schedule (Next 3 Days)
====================================

Tuesday, November 25, 2025:
  CoCalc:
    09:00 - template: differential_eq (Duplicate content)
    13:00 - notebook: fokker_planck_equation

Thursday, November 27, 2025:
  SageMath:
    09:00 - template: differential_eq (Duplicate content)
  CoCalc:
    09:00 - template: protein_folding
    13:00 - notebook: finite_element_method_heat_transfer
```

### 2. Monitor Queue

```python
from unified_queue_manager import UnifiedQueueManager

manager = UnifiedQueueManager()
stats = manager.get_statistics()

print(f"Total queued: {stats['total_queued']}")
print(f"Next 24 hours: {stats['next_24h']}")
print(f"Duplicates: {stats['duplicates']}")
```

### 3. Validate Queue

```python
from enhanced_scheduler import EnhancedScheduler

scheduler = EnhancedScheduler()
warnings = scheduler.validate_queue()

if warnings:
    for warning in warnings:
        print(f"⚠ {warning}")
else:
    print("✓ No issues found")
```

### 4. View Daily Schedule

```python
from unified_queue_manager import UnifiedQueueManager
from datetime import datetime, timedelta

manager = UnifiedQueueManager()
tomorrow = datetime.now() + timedelta(days=1)

daily = manager.get_daily_schedule(tomorrow)

for page_id, content_list in daily.items():
    page_info = router.get_page_info(page_id)
    print(f"\n{page_info['name']}:")
    for item in content_list:
        time = datetime.fromisoformat(item.scheduled_time)
        print(f"  {time.strftime('%H:%M')} - {item.content_type}: {item.source_name}")
```

---

## Content Flow Examples

### Example 1: SageTeX Template (Dual-Page)

**Template**: `group_theory.tex`
- Category: mathematics
- Has SageTeX: True
- Description: "Group theory proofs using symbolic algebra"

**Routing Decision**:
```python
routes = router.route_template(template)
# Returns: [CoCalc, SageMath]
```

**Scheduled Posts**:

**Post 1 - CoCalc (Tuesday 9:00 AM)**:
```
Computational science templates on CoCalc.

Explore group theory proofs using symbolic algebra.
Complete with SageMath integration for symbolic computation.

🔗 https://cocalc.com/github/.../group_theory.tex

#CoCalc #ComputationalScience #ReproducibleResearch
#LaTeX #SageTeX #Mathematics #GroupTheory
```

**Post 2 - SageMath (Thursday 9:00 AM)**:
```
Mathematical computation at its finest!

Explore group theory proofs using symbolic algebra.
Complete with SageMath integration for symbolic computation.

🔗 https://cocalc.com/github/.../group_theory.tex

#SageMath #SymbolicMath #PureMath #MathematicalComputing
#LaTeX #SageTeX #Mathematics #GroupTheory
```

### Example 2: Notebook (Single-Page)

**Notebook**: `fokker_planck_equation`
- Has pre-written post
- No SageMath indicators

**Routing Decision**:
```python
routes = router.route_notebook(notebook)
# Returns: [CoCalc only]
```

**Scheduled Post**:

**Post 1 - CoCalc (Tuesday 1:00 PM)**:
```
Computational notebook showcase!

[Pre-written Facebook post from post file]

🔗 https://cocalc.com/github/.../fokker_planck_equation.ipynb

#CoCalc #ComputationalNotebook #Python
```

### Example 3: Pure Math Notebook (Dual-Page)

**Notebook**: `symbolic_algebra_computations`
- Tags: ['sagemath', 'algebra']
- Description: "Symbolic algebra using SageMath"

**Routing Decision**:
```python
routes = router.route_notebook(notebook)
# Returns: [CoCalc, SageMath]
```

**Scheduled Posts**:
- CoCalc: Wednesday 1:00 PM
- SageMath: Friday 1:00 PM (+2 days)

---

## Duplicate Content Handling Details

### Identification

Content is marked as duplicate when it routes to multiple pages:
```python
if len(routes) > 1:
    is_duplicate = True
    duplicate_group_id = str(uuid.uuid4())
```

### Spreading Algorithm

```python
def schedule_duplicate_content(routes, base_time):
    schedules = []
    current_time = base_time

    for i, route in enumerate(sorted_routes):
        schedules.append({
            'page_id': route.page_id,
            'scheduled_time': current_time,
            'is_original': (i == 0)
        })

        # Add gap for next page
        if i < len(routes) - 1:
            current_time += timedelta(days=min_day_gap)

    return schedules
```

### Message Tailoring

```python
def tailor_message_for_page(content, page_name, content_type):
    if 'SageMath' in page_name:
        prefix = random.choice([
            "Mathematical computation at its finest!",
            "Symbolic mathematics made easy with SageMath.",
            "Explore pure mathematics with computational power."
        ])
    else:
        prefix = random.choice([
            "Computational science templates on CoCalc.",
            "Reproducible research made easy.",
            "Professional LaTeX templates for scientists."
        ])

    return f"{prefix}\n\n{content}"
```

### Hashtag Adjustment

```python
def adjust_hashtags_for_page(base_hashtags, page_name):
    if 'SageMath' in page_name:
        # Add math-specific tags
        sagemath_tags = ['SageMath', 'SymbolicMath', 'PureMath']
        # Remove non-math tags
        remove_tags = ['Engineering', 'Physics', 'DataScience']
    else:
        # Add broad science tags
        cocalc_tags = ['CoCalc', 'ComputationalScience']

    return adjusted_tags
```

---

## Publishing Workflow

### Updated `social_publisher.py`

**Key Changes**:
1. Added `page_id` parameter to all publish methods
2. Tracks page_id in posting history
3. Supports dual-page credentials

**Usage**:
```python
from social_publisher import SocialMediaPublisher

publisher = SocialMediaPublisher()

# Post to specific page
result = publisher.publish_to_facebook(
    content=post_text,
    link=post_link,
    image_path=image_path,
    template_name=template_name,
    page_id="698630966948910"  # CoCalc page
)

if result.success:
    print(f"✓ Posted to {result.platform}: {result.post_id}")
```

### Automated Publishing (Future)

```python
def publish_due_content():
    """Check and publish due content"""
    manager = UnifiedQueueManager()
    publisher = SocialMediaPublisher()

    due_items = manager.get_due_content(within_minutes=5)

    for item in due_items:
        result = publisher.publish_to_facebook(
            content=item.content_text,
            link=item.link,
            image_path=item.image_path,
            template_name=item.source_name,
            page_id=item.page_id  # Posts to correct page!
        )

        if result.success:
            manager.mark_posted(item, result.post_id)
            logger.info(f"✓ Posted {item.source_name} to {item.page_name}")
        else:
            logger.error(f"✗ Failed: {result.error_message}")
            # Reschedule for later
            manager.reschedule_content(
                item.content_id,
                datetime.now() + timedelta(hours=1)
            )
```

---

## Monitoring and Analytics

### Queue Health Check

```python
def check_queue_health():
    """Daily queue health check"""
    scheduler = EnhancedScheduler()

    # Get statistics
    stats = scheduler.get_queue_statistics()

    # Check thresholds
    issues = []

    if stats['total_queued'] < 14:
        issues.append("Queue low - less than 7 days of content")

    if stats['next_24h'] == 0:
        issues.append("No content scheduled for next 24 hours!")

    # Check balance
    templates = stats['by_content_type'].get('template', 0)
    notebooks = stats['by_content_type'].get('notebook', 0)

    if notebooks < templates * 0.3:
        issues.append(f"Notebook content too low ({notebooks} vs {templates} templates)")

    # Validate
    warnings = scheduler.validate_queue()
    issues.extend(warnings)

    return issues
```

### Posting History Analysis

```python
def analyze_posting_history(days=30):
    """Analyze posting patterns"""
    manager = UnifiedQueueManager()

    # Load history
    history = manager.posting_history

    # Filter to date range
    cutoff = datetime.now() - timedelta(days=days)
    recent = [h for h in history
              if datetime.fromisoformat(h['timestamp']) > cutoff]

    # Analyze
    by_page = {}
    by_type = {}

    for record in recent:
        page = record.get('page_id')
        ctype = record.get('content_type', 'unknown')

        by_page[page] = by_page.get(page, 0) + 1
        by_type[ctype] = by_type.get(ctype, 0) + 1

    return {
        'total_posts': len(recent),
        'by_page': by_page,
        'by_type': by_type,
        'avg_per_day': len(recent) / days
    }
```

---

## Testing Commands

### Test Individual Components

```bash
# Test page router
python3 page_router.py

# Test duplicate handler
python3 duplicate_content_handler.py

# Test queue manager
python3 unified_queue_manager.py

# Test full integration
python3 enhanced_scheduler.py
```

### Validate System

```python
# Validate credentials
from social_publisher import SocialMediaPublisher

publisher = SocialMediaPublisher()
validation = publisher.validate_credentials()

for platform, valid in validation.items():
    print(f"{platform}: {'✓' if valid else '✗'}")

# Validate queue
from enhanced_scheduler import EnhancedScheduler

scheduler = EnhancedScheduler()
warnings = scheduler.validate_queue()

# Validate content availability
from template_scanner import TemplateScanner
from notebook_scanner import NotebookScanner

template_scanner = TemplateScanner()
template_scanner.load_index()
print(f"Templates: {sum(len(t) for t in template_scanner.templates.values())}")

notebook_scanner = NotebookScanner(notebooks_dir, output_dir)
notebooks = notebook_scanner.get_notebooks_with_posts()
print(f"Notebooks with posts: {len(notebooks)}")
```

---

## Troubleshooting

### Issue: Not Enough Notebooks

**Symptom**: Queue has mostly templates, few notebooks

**Cause**: Only 7 notebooks have pre-written posts

**Solutions**:
1. Generate posts for more notebooks using LLM
2. Adjust content mix ratio in scheduler
3. Prioritize existing notebooks

### Issue: Duplicates on Same Day

**Symptom**: Validation warnings about same-day duplicates

**Solution**:
```python
manager = UnifiedQueueManager()

# Find duplicates
duplicates = [c for c in manager.queue if c.is_duplicate]

# Group by duplicate_group_id
from collections import defaultdict
groups = defaultdict(list)
for dup in duplicates:
    groups[dup.duplicate_group_id].append(dup)

# Check each group
for group_id, items in groups.items():
    dates = [datetime.fromisoformat(i.scheduled_time).date()
             for i in items]
    if len(dates) != len(set(dates)):
        print(f"⚠ Group {group_id} has same-day duplicates!")
        # Reschedule
        for i, item in enumerate(sorted(items, key=lambda x: x.scheduled_time)):
            if i > 0:
                new_time = (datetime.fromisoformat(items[0].scheduled_time) +
                           timedelta(days=2*i))
                manager.reschedule_content(item.content_id, new_time)
```

### Issue: SageMath Page Gets No Content

**Symptom**: Only CoCalc posts in queue

**Check Routing**:
```python
from page_router import PageRouter
from template_scanner import TemplateScanner

router = PageRouter()
scanner = TemplateScanner()
scanner.load_index()

# Check how many templates route to SageMath
sagemath_count = 0
for category, templates in scanner.templates.items():
    for template in templates:
        routes = router.route_template(template.to_dict())
        if any(r.page_id == '26593144945' for r in routes):
            sagemath_count += 1

print(f"Templates routing to SageMath: {sagemath_count}")
```

**Solution**: If too few, adjust routing criteria in `page_router.py`:
- Add more categories to `SAGEMATH_CATEGORIES`
- Add more keywords to `SAGEMATH_KEYWORDS`
- Lower the threshold for mathematical content

---

## Best Practices

### Weekly Workflow

**Sunday**:
1. Generate new weekly schedule: `python3 enhanced_scheduler.py`
2. Review queue statistics
3. Validate for conflicts
4. Check image availability

**Daily**:
1. Monitor posting queue
2. Check for due content
3. Verify published posts
4. Track engagement

**Monthly**:
1. Analyze posting history
2. Review engagement metrics
3. Optimize day themes
4. Update hashtag strategies

### Content Quality

1. **Templates**:
   - Ensure PDFs exist and are valid
   - Verify images extract correctly
   - Check GitHub links work

2. **Notebooks**:
   - Generate posts for more notebooks (currently only 7/253)
   - Ensure notebooks render in CoCalc
   - Verify image extraction

3. **Messaging**:
   - Review tailored messages for appropriateness
   - Test hashtag effectiveness
   - Monitor duplicate variations

---

## Future Enhancements

### High Priority

1. **Generate More Notebook Posts**: Only 7/253 have posts
2. **Automated Publishing Loop**: Daemon to auto-publish due content
3. **Error Recovery**: Retry failed posts with exponential backoff
4. **Engagement Tracking**: Track likes, shares, comments per post

### Medium Priority

1. **Dynamic Scheduling**: Adjust based on engagement data
2. **A/B Testing**: Test different message variations
3. **Image Optimization**: Better image selection and cropping
4. **Multi-Platform**: Full Threads and Instagram support

### Low Priority

1. **Analytics Dashboard**: Web UI for monitoring
2. **Content Recommendations**: ML-based content selection
3. **Trend Integration**: Incorporate trending topics
4. **Audience Analysis**: Different messaging per demographic

---

## Data Files

### Queue
- **File**: `data/unified_queue.json`
- **Format**: JSON array of QueuedContent objects
- **Size**: ~2-4 MB (for weekly schedule)

### Posting History
- **File**: `data/unified_posting_history.json`
- **Format**: JSON array of posting records
- **Growth**: ~100 KB/week

### Template Index
- **File**: `data/template_index.json`
- **Format**: JSON dict of TemplateMetadata
- **Size**: ~500 KB

---

## Support

For issues or questions:
1. Check this guide
2. Review component test outputs
3. Check logs in `logs/automation.log`
4. Validate configuration in `.env`

---

**Version**: 2.0
**Last Updated**: 2025-11-25
**Status**: Production Ready ✓
