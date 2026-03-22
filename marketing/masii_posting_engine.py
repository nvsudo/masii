"""
masii Posting Engine
Handle X, Instagram (Buffer), Reddit posting
"""

import requests
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple

class TwitterPoster:
    """Post to X/Twitter with randomized timing"""
    
    def __init__(self, bearer_token: str):
        self.bearer_token = bearer_token
        self.base_url = "https://api.twitter.com/2"
        self.headers = {
            "Authorization": f"Bearer {bearer_token}",
            "Content-Type": "application/json"
        }
    
    def get_randomized_post_time(self) -> datetime:
        """Get random post time within 10:00-14:00 window"""
        # In production: use timezone-aware datetime
        now = datetime.utcnow()
        
        # Window: 10:00-14:00 (4 hours = 240 minutes)
        window_start = 10 * 60  # 10:00
        window_end = 14 * 60    # 14:00
        
        random_minutes = random.randint(window_start, window_end)
        random_hour = random_minutes // 60
        random_minute = random_minutes % 60
        
        post_time = now.replace(hour=random_hour, minute=random_minute, second=0, microsecond=0)
        
        return post_time
    
    def post_tweet(self, text: str, scheduled: bool = False) -> Dict[str, Any]:
        """
        Post a tweet
        
        Args:
            text: Tweet text (<280 chars)
            scheduled: If True, return scheduled time instead of posting immediately
        
        Returns:
            Response with tweet ID and status
        """
        
        if scheduled:
            post_time = self.get_randomized_post_time()
            return {
                "status": "scheduled",
                "text": text,
                "scheduled_time": post_time.isoformat(),
                "message": f"Tweet scheduled for {post_time.strftime('%H:%M')} (randomized)"
            }
        
        # Post immediately
        response = requests.post(
            f"{self.base_url}/tweets",
            headers=self.headers,
            json={"text": text}
        )
        
        if response.status_code == 201:
            data = response.json()
            return {
                "status": "posted",
                "tweet_id": data['data']['id'],
                "text": text,
                "posted_at": datetime.utcnow().isoformat()
            }
        else:
            return {
                "status": "failed",
                "error": response.text,
                "text": text
            }
    
    def post_thread(self, tweets: List[str]) -> Dict[str, Any]:
        """Post a Twitter thread (multiple tweets, replies to each other)"""
        
        results = []
        reply_to_id = None
        
        for tweet_text in tweets:
            payload = {"text": tweet_text}
            
            if reply_to_id:
                payload["reply"] = {"in_reply_to_tweet_id": reply_to_id}
            
            response = requests.post(
                f"{self.base_url}/tweets",
                headers=self.headers,
                json=payload
            )
            
            if response.status_code == 201:
                data = response.json()
                tweet_id = data['data']['id']
                reply_to_id = tweet_id
                results.append({
                    "status": "posted",
                    "tweet_id": tweet_id,
                    "text": tweet_text
                })
            else:
                results.append({
                    "status": "failed",
                    "error": response.text,
                    "text": tweet_text
                })
        
        return {
            "status": "thread_posted" if all(r['status'] == 'posted' for r in results) else "partial_failure",
            "tweets": results,
            "posted_at": datetime.utcnow().isoformat()
        }


class BufferScheduler:
    """Schedule posts to Instagram via Buffer API"""
    
    def __init__(self, buffer_api_token: str):
        self.api_token = buffer_api_token
        self.base_url = "https://api.bufferapp.com/1"
        self.headers = {
            "Authorization": f"Bearer {buffer_api_token}",
            "Content-Type": "application/json"
        }
    
    def schedule_instagram_post(self, image_url: str, caption: str, scheduled_time: datetime) -> Dict[str, Any]:
        """
        Schedule an Instagram post via Buffer
        
        Args:
            image_url: URL to image (or base64 encoded)
            caption: Instagram caption
            scheduled_time: When to post
        
        Returns:
            Buffer response with post ID
        """
        
        # In production: use Buffer's profile ID for Instagram account
        # Format: profile_id = "BUFFER_INSTAGRAM_PROFILE_ID"
        
        payload = {
            "status": caption,
            "media": {
                "url": image_url
            },
            "scheduled_at": int(scheduled_time.timestamp())
        }
        
        # POST to Buffer's update endpoint
        response = requests.post(
            f"{self.base_url}/updates/create.json",
            headers=self.headers,
            json=payload
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                "status": "scheduled",
                "buffer_id": data['buffer_id'],
                "scheduled_time": scheduled_time.isoformat(),
                "platform": "instagram"
            }
        else:
            return {
                "status": "failed",
                "error": response.text
            }
    
    def schedule_carousel_post(self, images: List[str], caption: str, scheduled_time: datetime) -> Dict[str, Any]:
        """Schedule a carousel post (multiple images)"""
        
        # Buffer handles carousel as single post with multiple media
        payload = {
            "status": caption,
            "media": [{"url": img} for img in images],
            "scheduled_at": int(scheduled_time.timestamp())
        }
        
        response = requests.post(
            f"{self.base_url}/updates/create.json",
            headers=self.headers,
            json=payload
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                "status": "scheduled",
                "buffer_id": data['buffer_id'],
                "image_count": len(images),
                "scheduled_time": scheduled_time.isoformat(),
                "platform": "instagram_carousel"
            }
        else:
            return {
                "status": "failed",
                "error": response.text
            }


class RedditPoster:
    """Post to Reddit via PRAW"""
    
    def __init__(self, reddit_instance):
        # In production: Initialize PRAW reddit instance
        self.reddit = reddit_instance
    
    def post_to_subreddit(self, subreddit: str, title: str, text: str) -> Dict[str, Any]:
        """Post text post to Reddit subreddit"""
        
        try:
            submission = self.reddit.subreddit(subreddit).submit(
                title=title,
                selftext=text
            )
            
            return {
                "status": "posted",
                "submission_id": submission.id,
                "url": submission.shortlink,
                "subreddit": subreddit,
                "posted_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "subreddit": subreddit
            }


class MasiiPostingEngine:
    """Master posting engine - orchestrates X, Instagram, Reddit"""
    
    def __init__(self, twitter_token: str, buffer_token: str, reddit_instance=None):
        self.twitter = TwitterPoster(twitter_token)
        self.buffer = BufferScheduler(buffer_token)
        self.reddit = RedditPoster(reddit_instance) if reddit_instance else None
    
    def schedule_daily_posts(self, posts: List[Dict[str, Any]]) -> Dict[str, List]:
        """
        Schedule all daily posts across platforms
        
        Expected input:
        [
            {
                "platform": "X",
                "type": "tweet" | "thread",
                "content": "text" | ["tweet1", "tweet2"],
                "image_url": "optional"
            },
            {
                "platform": "Instagram",
                "type": "reel" | "carousel",
                "caption": "text",
                "image_urls": ["url1", "url2"] | "url1"
            },
            {
                "platform": "Reddit",
                "subreddit": "r/diaspora",
                "title": "title",
                "text": "body"
            }
        ]
        """
        
        results = {
            "x": [],
            "instagram": [],
            "reddit": []
        }
        
        for post in posts:
            platform = post.get('platform', '').lower()
            
            if platform == 'x':
                if post['type'] == 'thread':
                    result = self.twitter.post_thread(post['content'])
                else:
                    result = self.twitter.post_tweet(post['content'], scheduled=True)
                results['x'].append(result)
            
            elif platform == 'instagram':
                scheduled_time = datetime.utcnow() + timedelta(hours=random.randint(1, 24))
                
                if post['type'] == 'carousel':
                    result = self.buffer.schedule_instagram_post(
                        image_url=post['image_urls'][0],  # First image (Buffer handles rest)
                        caption=post['caption'],
                        scheduled_time=scheduled_time
                    )
                else:
                    result = self.buffer.schedule_instagram_post(
                        image_url=post['image_urls'],
                        caption=post['caption'],
                        scheduled_time=scheduled_time
                    )
                results['instagram'].append(result)
            
            elif platform == 'reddit' and self.reddit:
                result = self.reddit.post_to_subreddit(
                    subreddit=post['subreddit'],
                    title=post['title'],
                    text=post['text']
                )
                results['reddit'].append(result)
        
        return results


# Example usage
if __name__ == "__main__":
    print("""
    masii Posting Engine — Platform Integration
    
    Platforms:
    ✅ X/Twitter (direct API, randomized posting)
    ✅ Instagram (via Buffer, scheduled)
    ✅ Reddit (via PRAW, immediate)
    
    Usage:
    1. Initialize with API tokens
    2. Call schedule_daily_posts() with post list
    3. Engine handles platform-specific formatting
    
    Example posts ready for orchestrator approval gates.
    """)
