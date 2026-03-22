"""
masii Marketing Content Generator
Opus-powered copy generation for X, Instagram, Reddit
"""

import json
from datetime import datetime
from typing import List, Dict, Any

MASII_BRAND_GUIDELINES = """
# masii Brand Guidelines

## Tone & Voice
- Warm, inclusive, honest about diaspora complexities
- First-person storytelling, not corporate
- Authentic vulnerability (we get diaspora pain points)
- Conversational, not preachy

## Key Messages
- "Free matches" (vs paid apps)
- "Built by diaspora, for diaspora" (ownership)
- "Real intent" (no swiping fatigue)
- "For people who don't fit the algorithm"

## Values
- Diaspora identity matters
- Vulnerability is strength
- Community > competition
- Intent > endless options

## Visual
- Warm colors: amber, earth tones, bronze
- Human-focused photography (real people, diverse backgrounds)
- Authentic moments, not staged

## What NOT to do
- Don't oversimplify diaspora experience
- Don't "tribe" people into categories
- Don't make dating feel like a transaction
- Don't use corporate dating app language
"""

class MasiiContentGenerator:
    """Generate masii marketing content via Opus"""
    
    def __init__(self, opus_model_name="claude-opus-4-5"):
        self.model = opus_model_name
        self.brand_guidelines = MASII_BRAND_GUIDELINES
        self.system_prompt = self._build_system_prompt()
    
    def _build_system_prompt(self) -> str:
        """Build system prompt with brand guidelines"""
        return f"""You are A, the marketing partner for masii (diaspora matchmaking platform).

{self.brand_guidelines}

Your job: Generate authentic, warm, engaging social media content that resonates with diaspora users.

Tone: First-person, storytelling, conversational. Not corporate. Not preachy.

Constraints:
- X posts: 280 chars max per tweet (threads OK)
- Instagram: Captions that make people stop scrolling (curiosity + emotion)
- Reddit: Authentic, conversational, ask questions that spark discussion

Remember: Diaspora is complex. Validate that complexity. Don't oversimplify.
"""
    
    def generate_ideas(self, yesterday_performance: Dict[str, Any] = None, count: int = 10) -> List[Dict[str, str]]:
        """
        Generate content ideas for the day
        
        Input: Yesterday's top posts (what resonated?)
        Output: 5-10 ideas across X, Instagram, Reddit
        """
        
        performance_context = ""
        if yesterday_performance:
            best_posts = yesterday_performance.get('top_posts', [])
            performance_context = f"""
Yesterday's top performers (what resonated):
{json.dumps(best_posts, indent=2)}

Build on these themes but create NEW angles.
"""
        
        prompt = f"""Generate {count} social media content ideas for masii.

{performance_context}

Ideas should:
1. **X/Twitter** - Observations, questions, tips. Topics: diaspora identity, dating, intent, community
2. **Instagram** - Emotional, visual-driven. Stories about diaspora experience, matching moments, community
3. **Reddit** - Authentic questions, AMAs, discussions. Real conversations about diaspora dating

Return JSON format:
{{
    "ideas": [
        {{
            "platform": "X" | "Instagram" | "Reddit",
            "theme": "Brief theme description",
            "hook": "How you'll grab attention",
            "cta": "What you're asking people to do",
            "target_audience": "Who this speaks to"
        }}
    ]
}}
"""
        
        # In production: call Opus API
        # For now: return template
        
        return {
            "status": "ready_for_opus_generation",
            "prompt": prompt,
            "count": count,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def write_copy(self, idea: Dict[str, str]) -> Dict[str, str]:
        """
        Write full copy for an approved idea
        
        Input: Single idea (platform, theme, hook, etc.)
        Output: Full copy ready to post
        """
        
        platform = idea.get('platform', 'X')
        theme = idea.get('theme', '')
        hook = idea.get('hook', '')
        
        prompt = f"""Write compelling copy for masii's {platform} channel.

Theme: {theme}
Hook: {hook}

Requirements:
- Platform-native (respect character limits, format)
- Warm, authentic, first-person
- Include CTA (what should people do?)
- Tie to masii's mission (intent > swiping)

For {platform}:
"""
        
        if platform == "X":
            prompt += """- Thread format (multiple tweets, each <280 chars)
- Use line breaks between tweets
- Include 1-2 questions to drive replies
- Tag relevant accounts (sparingly)
"""
        elif platform == "Instagram":
            prompt += """- Engaging caption (first line hooks, then story)
- Use emojis strategically (not overdone)
- Call-to-action at end (link in bio, comment below, DM)
- Break into readable paragraphs
"""
        elif platform == "Reddit":
            prompt += """- Conversational, authentic tone
            - Ask real questions or share genuine stories
- Avoid promotional language
- Encourage discussion/comments
"""
        
        return {
            "status": "ready_for_opus_copy",
            "prompt": prompt,
            "idea": idea,
            "platform": platform,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def extract_copy_for_posting(self, opus_response: str, platform: str) -> str:
        """Extract clean copy from Opus response"""
        # In production: parse response, clean formatting, return
        return opus_response


if __name__ == "__main__":
    generator = MasiiContentGenerator()
    
    # Example: Generate ideas
    ideas_prompt = generator.generate_ideas(count=10)
    print("Ideas Generation Prompt Ready:")
    print(json.dumps(ideas_prompt, indent=2))
    
    # Example: Write copy for a single idea
    sample_idea = {
        "platform": "X",
        "theme": "Diaspora identity in dating",
        "hook": "Ask how it feels to not 'fit' conventional dating",
        "cta": "Share your story"
    }
    
    copy_prompt = generator.write_copy(sample_idea)
    print("\nCopy Writing Prompt Ready:")
    print(json.dumps(copy_prompt, indent=2))
