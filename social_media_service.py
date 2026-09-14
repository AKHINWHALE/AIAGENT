"""
social_media_service.py - Handles posting to real social media platforms
"""
import os
import tweepy
from dotenv import load_dotenv

load_dotenv()

# Check if we are in simulation mode
SIMULATE = os.getenv('SIMULATE_POSTING', 'True') == 'True'


def post_to_twitter(content, media_url=None):
    """Post content to Twitter/X"""
    if SIMULATE:
        print(f"🎯 [SIMULATION] Posted to Twitter: {content[:50]}...")
        return True, "Simulated success"
    
    try:
        # Initialize Twitter Client (API v2)
        client = tweepy.Client(
            consumer_key=os.getenv('TWITTER_API_KEY'),
            consumer_secret=os.getenv('TWITTER_API_SECRET'),
            access_token=os.getenv('TWITTER_ACCESS_TOKEN'),
            access_token_secret=os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        )
        
        # Post the tweet
        response = client.create_tweet(text=content)
        print(f"✅ Successfully posted to Twitter! Tweet ID: {response.data['id']}")
        return True, "Success"
        
    except tweepy.TweepyException as e:
        print(f"❌ Twitter API Error: {e}")
        return False, str(e)
    except Exception as e:
        print(f"❌ Unexpected Twitter Error: {e}")
        return False, str(e)


def post_to_facebook(content, media_url=None):
    """Post content to Facebook Page"""
    if SIMULATE:
        print(f"🎯 [SIMULATION] Posted to Facebook: {content[:50]}...")
        return True, "Simulated success"
    
    # TODO: Add Facebook Graph API integration here
    # Requires: Page Access Token and Page ID
    print("⚠️ Facebook posting not yet fully implemented.")
    return False, "Not implemented"


def post_to_instagram(content, media_url=None):
    """Post content to Instagram"""
    if SIMULATE:
        print(f"🎯 [SIMULATION] Posted to Instagram: {content[:50]}...")
        return True, "Simulated success"
    
    # TODO: Add Instagram Graph API integration here
    # Requires: Instagram Business Account linked to Facebook Page
    print("⚠️ Instagram posting not yet fully implemented.")
    return False, "Not implemented"


def publish_post(platform, content, media_url=None):
    """
    Master function to route the post to the correct platform.
    Returns: (success: bool, message: str)
    """
    platform = platform.lower()
    
    if platform == 'twitter' or platform == 'x':
        return post_to_twitter(content, media_url)
    elif platform == 'facebook':
        return post_to_facebook(content, media_url)
    elif platform == 'instagram':
        return post_to_instagram(content, media_url)
    else:
        return False, f"Unknown platform: {platform}"