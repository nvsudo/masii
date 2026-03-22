"""
masii Marketing Orchestrator
Complete pipeline: Ideas → Copy → Visuals → Posting → Tracking
"""

import json
import os
from datetime import datetime
from enum import Enum
from typing import Dict, Any, List

class PostStatus(Enum):
    IDEA_PENDING = "idea_pending"
    IDEA_APPROVED = "idea_approved"
    COPY_READY = "copy_ready"
    COPY_APPROVED = "copy_approved"
    VISUAL_READY = "visual_ready"
    VISUAL_APPROVED = "visual_approved"
    SCHEDULED = "scheduled"
    POSTED = "posted"
    FAILED = "failed"

class MasiiMarketingOrchestrator:
    """
    Master orchestrator for masii social media marketing
    
    Flow:
    1. Generate ideas (Opus)
    2. Quality check ideas (Sonnet)
    3. User approves ideas
    4. Write copy (Opus)
    5. Audit copy (Sonnet)
    6. User approves copy
    7. Generate visuals (Gemini/Nano/Veo)
    8. User approves visuals
    9. Schedule posts (X, Buffer, Reddit)
    10. Track engagement (real-time)
    11. Log learnings (event-driven)
    """
    
    def __init__(self, masii_home: str = "/Users/nikunjvora/clawd/ventures/masii"):
        self.masii_home = masii_home
        self.marketing_dir = os.path.join(masii_home, "marketing")
        self.queue_file = os.path.join(self.marketing_dir, "queue.json")
        self.lessons_file = os.path.join(masii_home, "lessons.md")
        self.dashboard_file = os.path.join(self.marketing_dir, "dashboard.json")
        
        # Ensure directories exist
        os.makedirs(self.marketing_dir, exist_ok=True)
        
        # Initialize queue if empty
        if not os.path.exists(self.queue_file):
            self._init_queue()
    
    def _init_queue(self):
        """Initialize empty content queue"""
        queue = {
            "created": datetime.utcnow().isoformat(),
            "posts": [],
            "stats": {
                "total_posts": 0,
                "posted": 0,
                "failed": 0,
                "pending_approval": 0
            }
        }
        with open(self.queue_file, 'w') as f:
            json.dump(queue, f, indent=2)
    
    def get_daily_workflow(self) -> Dict[str, Any]:
        """Return today's workflow status"""
        return {
            "date": datetime.utcnow().date().isoformat(),
            "workflow": {
                "1_ideas": {
                    "status": "ready",
                    "action": "A generates 5-10 ideas",
                    "models": "Opus (generation) + Sonnet (audit)",
                    "time_to_completion": "8 minutes",
                    "gate": "N approves which ideas to develop"
                },
                "2_copy": {
                    "status": "pending_ideas_approval",
                    "action": "A writes full copy for approved ideas",
                    "models": "Opus (writing) + Sonnet (audit)",
                    "time_to_completion": "15 minutes",
                    "gate": "N approves final wording"
                },
                "3_visuals": {
                    "status": "pending_copy_approval",
                    "action": "A generates visuals (Gemini, Nano, Veo)",
                    "models": "Google Gemini products (external API)",
                    "time_to_completion": "10 minutes",
                    "gate": "N approves visual direction"
                },
                "4_schedule": {
                    "status": "pending_visual_approval",
                    "action": "A schedules posts (X, Instagram, Reddit)",
                    "platforms": ["X (direct API)", "Instagram (Buffer)", "Reddit (PRAW)"],
                    "time_to_completion": "5 minutes",
                    "gate": "N confirms schedule"
                },
                "5_track": {
                    "status": "continuous",
                    "action": "Dashboard updates engagement in real-time",
                    "metrics": ["Likes", "Shares", "Comments", "Followers", "Conversions"],
                    "update_frequency": "Every 15 minutes"
                },
                "6_learn": {
                    "status": "continuous",
                    "action": "Log insights when posts get traction",
                    "output": "lessons.md (event-driven)",
                    "purpose": "Inform next day's ideas"
                }
            },
            "token_budget": {
                "daily_tokens": "~9.7K",
                "breakdown": {
                    "opus_ideas": "2K",
                    "opus_copy": "4K",
                    "sonnet_audit": "3K",
                    "haiku_dashboard": "0.5K",
                    "other": "0.2K"
                },
                "external_apis": ["Gemini (pay-per-image)", "Nano (pay-per-video)", "Veo (optional, premium)"]
            },
            "approval_gates": 4,
            "total_time_to_ready": "43 minutes (if N approves quickly)"
        }
    
    def add_post_to_queue(self, post: Dict[str, Any]):
        """Add a post to the content queue"""
        with open(self.queue_file, 'r') as f:
            queue = json.load(f)
        
        post['id'] = len(queue['posts']) + 1
        post['created'] = datetime.utcnow().isoformat()
        post['status'] = PostStatus.IDEA_PENDING.value
        
        queue['posts'].append(post)
        queue['stats']['total_posts'] += 1
        queue['stats']['pending_approval'] += 1
        
        with open(self.queue_file, 'w') as f:
            json.dump(queue, f, indent=2)
        
        return post
    
    def approve_idea(self, post_id: int):
        """Mark idea as approved"""
        self._update_post_status(post_id, PostStatus.IDEA_APPROVED)
    
    def approve_copy(self, post_id: int):
        """Mark copy as approved"""
        self._update_post_status(post_id, PostStatus.COPY_APPROVED)
    
    def approve_visuals(self, post_id: int):
        """Mark visuals as approved"""
        self._update_post_status(post_id, PostStatus.VISUAL_APPROVED)
    
    def schedule_posts(self, post_ids: List[int]):
        """Schedule approved posts"""
        for post_id in post_ids:
            self._update_post_status(post_id, PostStatus.SCHEDULED)
    
    def _update_post_status(self, post_id: int, status: PostStatus):
        """Update post status in queue"""
        with open(self.queue_file, 'r') as f:
            queue = json.load(f)
        
        for post in queue['posts']:
            if post['id'] == post_id:
                old_status = post.get('status')
                post['status'] = status.value
                post['updated'] = datetime.utcnow().isoformat()
                
                # Update stats
                if old_status == PostStatus.IDEA_PENDING.value:
                    queue['stats']['pending_approval'] -= 1
                
                break
        
        with open(self.queue_file, 'w') as f:
            json.dump(queue, f, indent=2)
    
    def log_learning(self, platform: str, engagement: Dict[str, Any], insight: str):
        """Log learning to lessons.md (event-driven)"""
        
        timestamp = datetime.utcnow().isoformat()
        metric = engagement.get('engagement_rate', 'N/A')
        
        lesson_entry = f"""
[{timestamp}] {platform} | {metric}% engagement | {insight}
Post: {engagement.get('post_text', 'N/A')[:50]}...
Context: Posted at {engagement.get('posted_at', 'N/A')}
Learning: {insight}
"""
        
        # Append to lessons.md
        with open(self.lessons_file, 'a') as f:
            f.write(lesson_entry)
    
    def get_queue_status(self) -> Dict[str, Any]:
        """Get current queue status"""
        with open(self.queue_file, 'r') as f:
            queue = json.load(f)
        
        return queue
    
    def get_dashboard_snapshot(self) -> Dict[str, Any]:
        """Get real-time dashboard snapshot"""
        
        # In production: pull from X/Instagram/Reddit APIs
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "x": {
                "posts_today": 0,
                "likes": 0,
                "retweets": 0,
                "quotes": 0,
                "followers": 0,
                "avg_engagement": "0%"
            },
            "instagram": {
                "posts_today": 0,
                "likes": 0,
                "comments": 0,
                "saves": 0,
                "followers": 0,
                "avg_engagement": "0%"
            },
            "reddit": {
                "posts_this_week": 0,
                "upvotes": 0,
                "comments": 0,
                "subscribers": 0
            },
            "conversions": {
                "profile_visits": 0,
                "website_clicks": 0,
                "signups": 0,
                "conversion_rate": "0%"
            },
            "total_followers": 0
        }


def main():
    """Demo: Show masii marketing orchestration"""
    
    orchestrator = MasiiMarketingOrchestrator()
    
    # Show daily workflow
    workflow = orchestrator.get_daily_workflow()
    print("📋 masii Marketing Daily Workflow")
    print("=" * 60)
    print(json.dumps(workflow, indent=2))
    
    # Show current queue
    queue = orchestrator.get_queue_status()
    print("\n📊 Content Queue Status")
    print("=" * 60)
    print(f"Total posts: {queue['stats']['total_posts']}")
    print(f"Pending approval: {queue['stats']['pending_approval']}")
    print(f"Posted: {queue['stats']['posted']}")
    print(f"Failed: {queue['stats']['failed']}")
    
    # Show dashboard
    dashboard = orchestrator.get_dashboard_snapshot()
    print("\n📈 Dashboard Snapshot")
    print("=" * 60)
    print(f"X followers: {dashboard['x']['followers']}")
    print(f"Instagram followers: {dashboard['instagram']['followers']}")
    print(f"Signups today: {dashboard['conversions']['signups']}")


if __name__ == "__main__":
    main()
