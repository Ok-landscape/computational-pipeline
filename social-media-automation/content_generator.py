#!/usr/bin/env python3
"""
Platform-Specific Content Generator

Generates tailored social media posts for Facebook, Threads, and Instagram
based on LaTeX template metadata.
"""

import logging
import random
from typing import Dict, List, Optional
from dataclasses import dataclass
from template_scanner import TemplateMetadata

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class SocialMediaPost:
    """Container for a social media post"""
    platform: str
    template_metadata: TemplateMetadata
    content: str
    hashtags: List[str]
    link: str
    image_path: Optional[str] = None
    alt_text: Optional[str] = None
    char_count: int = 0

    def __post_init__(self):
        self.char_count = len(self.content)


class ContentGenerator:
    """Generate platform-specific social media content"""

    # Platform character limits
    PLATFORM_LIMITS = {
        'facebook': 63206,
        'threads': 500,
        'instagram': 2200
    }

    # Category-specific hashtags
    CATEGORY_HASHTAGS = {
        'physics': ['#Physics', '#ComputationalPhysics', '#TheoreticalPhysics', '#Science'],
        'quantum-physics': ['#QuantumPhysics', '#QuantumMechanics', '#QuantumComputing', '#Physics'],
        'mathematics': ['#Mathematics', '#AppliedMath', '#NumericalMethods', '#MathScience'],
        'machine-learning': ['#MachineLearning', '#AI', '#DeepLearning', '#DataScience'],
        'astronomy': ['#Astronomy', '#Astrophysics', '#Space', '#CosmicScience'],
        'engineering': ['#Engineering', '#AppliedPhysics', '#ComputationalEngineering'],
        'biology': ['#Biophysics', '#ComputationalBiology', '#LifeSciences', '#Bioinformatics'],
        'chemistry': ['#Chemistry', '#ComputationalChemistry', '#MolecularScience'],
        'economics': ['#Economics', '#QuantitativeFinance', '#EconometricModeling'],
        'robotics': ['#Robotics', '#ControlSystems', '#AutomatedSystems'],
        'neuroscience': ['#Neuroscience', '#ComputationalNeuroscience', '#BrainScience'],
        'materials-science': ['#MaterialsScience', '#NanoScience', '#ComputationalMaterials'],
        'climate-science': ['#ClimateScience', '#AtmosphericScience', '#ClimateModeling'],
        'geophysics': ['#Geophysics', '#EarthScience', '#Seismology'],
        'acoustics': ['#Acoustics', '#SoundEngineering', '#WavePhysics'],
        'optics': ['#Optics', '#Photonics', '#LaserPhysics'],
        'fluid-dynamics': ['#FluidDynamics', '#CFD', '#ComputationalFluidDynamics'],
        'thermodynamics': ['#Thermodynamics', '#StatisticalMechanics', '#HeatTransfer']
    }

    # General hashtags
    GENERAL_HASHTAGS = {
        'computational': ['#ComputationalScience', '#ScientificComputing', '#NumericalSimulation'],
        'latex': ['#LaTeX', '#ScientificWriting', '#AcademicWriting', '#TeXLive'],
        'python': ['#Python', '#PythonTeX', '#ScientificPython', '#NumPy', '#Matplotlib'],
        'research': ['#Research', '#AcademicResearch', '#ScienceCommunication', '#OpenScience'],
        'education': ['#ScienceEducation', '#STEM', '#LearnScience', '#MathEducation']
    }

    def __init__(self):
        """Initialize content generator"""
        self.templates_used = {}  # Track which templates have been used

    def generate_facebook_post(self, template: TemplateMetadata) -> SocialMediaPost:
        """
        Generate detailed educational Facebook post

        Facebook allows longer content, so we can be comprehensive and educational.

        Args:
            template: Template metadata

        Returns:
            SocialMediaPost object
        """
        # Create engaging title
        title = f"📐 {template.title}"

        # Build comprehensive content
        sections = []

        # Introduction
        sections.append(template.abstract)

        # Computational details
        comp_details = self._generate_computational_details(template)
        if comp_details:
            sections.append(f"\n🔬 COMPUTATIONAL APPROACH\n{comp_details}")

        # Key features
        features = self._generate_key_features(template)
        if features:
            sections.append(f"\n✨ KEY FEATURES\n{features}")

        # Applications
        applications = self._generate_applications(template.category, template.title)
        if applications:
            sections.append(f"\n🎯 APPLICATIONS\n{applications}")

        # Technical stack
        tech_stack = self._generate_tech_stack(template)
        if tech_stack:
            sections.append(f"\n⚙️ TECHNICAL STACK\n{tech_stack}")

        # Call to action
        cta = (
            f"\n🚀 EXPLORE THIS TEMPLATE\n"
            f"View and interact with this computational template on CoCalc. "
            f"See the full LaTeX source code, run the computations, and modify the parameters "
            f"to explore different scenarios.\n"
            f"\n👉 Link in comments or check our bio!"
        )
        sections.append(cta)

        # Combine all sections
        content = f"{title}\n\n" + "\n".join(sections)

        # Hashtags
        hashtags = self._generate_hashtags(template, platform='facebook')

        # Add hashtags to content
        hashtag_line = "\n\n" + " ".join(hashtags)
        if len(content) + len(hashtag_line) < self.PLATFORM_LIMITS['facebook']:
            content += hashtag_line

        return SocialMediaPost(
            platform='facebook',
            template_metadata=template,
            content=content,
            hashtags=hashtags,
            link=template.cocalc_url
        )

    def generate_threads_post(self, template: TemplateMetadata) -> SocialMediaPost:
        """
        Generate conversational Threads post

        Threads is Twitter-like: concise, engaging, conversation-starter

        Args:
            template: Template metadata

        Returns:
            SocialMediaPost object
        """
        # Threads posts are short and punchy
        hooks = [
            f"Ever wondered how to model {self._get_topic(template)}? 🤔",
            f"Computational {self._get_category_topic(template.category)} is fascinating! Here's why:",
            f"Just computed this {self._get_topic(template)} simulation and... wow! 📊",
            f"Breaking down {self._get_topic(template)} with code and math 🧮",
            f"Today's computational challenge: {self._get_topic(template)} ⚡"
        ]

        hook = random.choice(hooks)

        # Brief explanation (1-2 sentences)
        explanation = template.abstract.split('.')[0] + '.'
        if len(explanation) > 200:
            explanation = explanation[:200] + '...'

        # Quick highlight
        if template.has_pythontex:
            tech = "Python + LaTeX"
        elif template.has_sagetex:
            tech = "SageMath + LaTeX"
        else:
            tech = "LaTeX"

        highlight = f"\n\n✨ Built with {tech}\n🔗 Full code + visuals available"

        # Combine (must be under 500 chars)
        content = f"{hook}\n\n{explanation}{highlight}"

        # Trim if needed
        if len(content) > 480:
            # Shorten explanation
            explanation = template.abstract.split('.')[0][:150] + '...'
            content = f"{hook}\n\n{explanation}{highlight}"

        # Minimal hashtags for Threads
        hashtags = self._generate_hashtags(template, platform='threads', max_tags=3)

        # Add hashtags if space allows
        hashtag_line = " " + " ".join(hashtags)
        if len(content) + len(hashtag_line) <= 500:
            content += hashtag_line

        return SocialMediaPost(
            platform='threads',
            template_metadata=template,
            content=content,
            hashtags=hashtags,
            link=template.cocalc_url
        )

    def generate_instagram_post(self, template: TemplateMetadata) -> SocialMediaPost:
        """
        Generate visual-focused Instagram post

        Instagram is about visual storytelling with supporting text

        Args:
            template: Template metadata

        Returns:
            SocialMediaPost object
        """
        # Instagram posts start with a hook and emojis
        category_emoji = self._get_category_emoji(template.category)

        # Title with emoji
        title = f"{category_emoji} {template.title}"

        # Visual description (focus on what you SEE)
        visual_desc = self._generate_visual_description(template)

        # What it shows
        explanation = f"\n\n📊 What you're seeing:\n{template.abstract}"

        # The science
        science_bit = self._generate_science_highlight(template)

        # Built with
        tech_line = f"\n\n⚙️ Built with: "
        if template.has_pythontex:
            tech_line += "Python • NumPy • Matplotlib • LaTeX"
        elif template.has_sagetex:
            tech_line += "SageMath • SymPy • LaTeX"
        else:
            tech_line += "LaTeX • Mathematical Typesetting"

        # Call to action
        cta = (
            f"\n\n💡 Want to explore this yourself?\n"
            f"Link in bio to view the full template on CoCalc! "
            f"You can run the code, modify parameters, and create your own visualizations."
        )

        # Combine
        content = f"{title}\n{visual_desc}{explanation}\n{science_bit}{tech_line}{cta}"

        # Hashtags (Instagram loves hashtags!)
        hashtags = self._generate_hashtags(template, platform='instagram')

        # Add hashtag block
        content += "\n\n" + " ".join(hashtags)

        # Trim if over limit
        if len(content) > self.PLATFORM_LIMITS['instagram']:
            # Remove some explanation
            content = f"{title}\n{visual_desc}{explanation[:300]}...{tech_line}{cta}\n\n" + " ".join(hashtags)

        return SocialMediaPost(
            platform='instagram',
            template_metadata=template,
            content=content,
            hashtags=hashtags,
            link=template.cocalc_url
        )

    def _generate_computational_details(self, template: TemplateMetadata) -> str:
        """Generate computational approach description"""
        details = []

        if template.has_pythontex:
            details.append("• Python integration via PythonTeX for numerical computations")
            if 'numpy' in str(template.packages).lower():
                details.append("• NumPy arrays for efficient vectorized operations")
            if 'matplotlib' in str(template.packages).lower():
                details.append("• Matplotlib for publication-quality visualizations")
            if 'scipy' in str(template.packages).lower():
                details.append("• SciPy for advanced scientific algorithms")

        if template.has_sagetex:
            details.append("• SageMath integration for symbolic computation")
            details.append("• Computer algebra system for exact mathematical operations")

        if template.plot_files:
            details.append(f"• {len(template.plot_files)} computational visualization(s)")

        return "\n".join(details) if details else ""

    def _generate_key_features(self, template: TemplateMetadata) -> str:
        """Generate key features list"""
        features = []

        if 'siunitx' in template.packages:
            features.append("• Proper SI unit formatting throughout")

        if 'hyperref' in template.packages:
            features.append("• Interactive PDF with clickable references")

        if 'tikz' in template.packages or 'pgfplots' in template.packages:
            features.append("• Custom graphics and plots with TikZ")

        if template.complexity_score >= 4:
            features.append("• Advanced mathematical modeling and analysis")
        elif template.complexity_score >= 3:
            features.append("• Intermediate computational techniques")

        if template.has_pythontex or template.has_sagetex:
            features.append("• Reproducible computational results")
            features.append("• Literate programming approach")

        return "\n".join(features) if features else ""

    def _generate_applications(self, category: str, title: str) -> str:
        """Generate real-world applications"""
        applications_map = {
            'physics': "Research papers, theoretical analysis, simulation studies",
            'quantum-physics': "Quantum computing research, particle physics, quantum chemistry",
            'machine-learning': "AI research papers, model documentation, data science reports",
            'astronomy': "Observational astronomy, cosmological models, stellar evolution studies",
            'engineering': "Technical reports, design analysis, system modeling",
            'biology': "Bioinformatics studies, population dynamics, systems biology",
            'economics': "Economic modeling, financial analysis, market research",
            'chemistry': "Molecular dynamics, reaction kinetics, spectroscopy analysis",
            'robotics': "Control system design, path planning, autonomous systems",
            'neuroscience': "Neural network modeling, brain dynamics, cognitive studies"
        }

        base_category = category.split('-')[0]
        return applications_map.get(base_category, applications_map.get(category, "Scientific research and analysis"))

    def _generate_tech_stack(self, template: TemplateMetadata) -> str:
        """Generate technical stack summary"""
        stack = ["• LaTeX for professional typesetting"]

        if template.has_pythontex:
            stack.append("• Python 3 with scientific libraries")
        if template.has_sagetex:
            stack.append("• SageMath computer algebra system")
        if 'amsmath' in template.packages:
            stack.append("• AMS-LaTeX for advanced mathematics")
        if 'graphicx' in template.packages:
            stack.append("• High-resolution graphics support")

        return "\n".join(stack)

    def _generate_hashtags(self,
                          template: TemplateMetadata,
                          platform: str,
                          max_tags: int = None) -> List[str]:
        """
        Generate relevant hashtags for the post

        Args:
            template: Template metadata
            platform: Target platform
            max_tags: Maximum number of hashtags

        Returns:
            List of hashtags
        """
        hashtags = []

        # Platform-specific defaults
        if max_tags is None:
            max_tags = {
                'facebook': 10,
                'threads': 3,
                'instagram': 20
            }.get(platform, 10)

        # Category-specific hashtags
        category_clean = template.category.replace('_', '-')
        if category_clean in self.CATEGORY_HASHTAGS:
            hashtags.extend(self.CATEGORY_HASHTAGS[category_clean][:3])

        # Base category if hyphenated
        if '-' in category_clean:
            base = category_clean.split('-')[0]
            if base in self.CATEGORY_HASHTAGS:
                hashtags.extend(self.CATEGORY_HASHTAGS[base][:2])

        # General computational hashtags
        hashtags.extend(self.GENERAL_HASHTAGS['computational'][:2])

        # LaTeX hashtags
        hashtags.extend(self.GENERAL_HASHTAGS['latex'][:2])

        # Python/SageMath specific
        if template.has_pythontex:
            hashtags.extend(self.GENERAL_HASHTAGS['python'][:2])

        # Research hashtags
        if platform == 'facebook':
            hashtags.extend(self.GENERAL_HASHTAGS['research'][:2])

        # Remove duplicates and limit
        hashtags = list(dict.fromkeys(hashtags))  # Remove duplicates while preserving order
        hashtags = hashtags[:max_tags]

        return hashtags

    def _get_topic(self, template: TemplateMetadata) -> str:
        """Extract readable topic from template"""
        # Clean up template name
        topic = template.template_name.replace('_', ' ').replace('-', ' ')
        return topic

    def _get_category_topic(self, category: str) -> str:
        """Get readable category topic"""
        return category.replace('_', ' ').replace('-', ' ')

    def _get_category_emoji(self, category: str) -> str:
        """Get emoji for category"""
        emoji_map = {
            'physics': '⚛️',
            'quantum': '🌌',
            'mathematics': '📐',
            'machine-learning': '🤖',
            'astronomy': '🔭',
            'engineering': '⚙️',
            'biology': '🧬',
            'chemistry': '⚗️',
            'economics': '📈',
            'robotics': '🦾',
            'neuroscience': '🧠',
            'climate': '🌍',
            'acoustics': '🔊',
            'optics': '💡',
            'fluid': '🌊'
        }

        for key, emoji in emoji_map.items():
            if key in category.lower():
                return emoji

        return '📊'  # Default

    def _generate_visual_description(self, template: TemplateMetadata) -> str:
        """Generate description of visual elements"""
        if template.plot_files and len(template.plot_files) > 0:
            return "Swipe through to see the computational visualizations and mathematical framework! 👉"
        else:
            return "A beautifully typeset mathematical document with equations and analysis! 📄"

    def _generate_science_highlight(self, template: TemplateMetadata) -> str:
        """Generate science highlight for Instagram"""
        complexity_descriptions = {
            1: "Perfect for students and beginners exploring this topic!",
            2: "Great introduction with practical computational examples.",
            3: "Intermediate level analysis with numerical methods.",
            4: "Advanced computational techniques and modeling.",
            5: "Cutting-edge research-level computational analysis."
        }

        return f"\n\n🔬 {complexity_descriptions.get(template.complexity_score, 'Scientific computational analysis.')}"


def main():
    """Test content generation"""
    from template_scanner import TemplateScanner

    # Load template index
    scanner = TemplateScanner()
    if not scanner.load_index():
        print("Building template index...")
        scanner.scan_all_templates()
        scanner.save_index()

    # Get a random template
    template = scanner.get_random_template()

    if template:
        generator = ContentGenerator()

        print("="*60)
        print(f"Template: {template.template_name}")
        print(f"Category: {template.category}")
        print("="*60)

        # Generate for all platforms
        for platform in ['facebook', 'threads', 'instagram']:
            print(f"\n{'='*60}")
            print(f"{platform.upper()} POST")
            print("="*60)

            if platform == 'facebook':
                post = generator.generate_facebook_post(template)
            elif platform == 'threads':
                post = generator.generate_threads_post(template)
            else:
                post = generator.generate_instagram_post(template)

            print(post.content)
            print(f"\nCharacter count: {post.char_count}/{ContentGenerator.PLATFORM_LIMITS[platform]}")
            print(f"Link: {post.link}")


if __name__ == "__main__":
    main()
