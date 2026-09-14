"""
post_publisher.py - Checks for scheduled posts and publishes them
"""
from models import db, ScheduledPost
from social_media_service import publish_post
from datetime import datetime


def publish_due_posts():
    """Find all posts that are due and publish them"""
    
    now = datetime.utcnow()
    
    # Find all posts that are scheduled and the time has come
    due_posts = ScheduledPost.query.filter(
        ScheduledPost.status == 'scheduled',
        ScheduledPost.scheduled_at <= now
    ).all()
    
    if not due_posts:
        print("ℹ️  No posts due for publishing right now.")
        return
    
    print(f"🚀 Found {len(due_posts)} post(s) ready to publish!")
    
    for post in due_posts:
        print(f"\n📝 Processing post for User {post.user_id}...")
        
        # Split platforms (e.g., "twitter,facebook")
        platforms = [p.strip() for p in post.platforms.split(',')]
        
        success_count = 0
        error_messages = []
        
        for platform in platforms:
            print(f"  → Attempting to post to {platform.capitalize()}...")
            success, message = publish_post(platform, post.content, post.media_url)
            
            if success:
                success_count += 1
            else:
                error_messages.append(f"{platform}: {message}")
        
        # Update the post status in the database
        if success_count == len(platforms):
            post.status = 'posted'
            print(f"  ✅ Successfully posted to all {len(platforms)} platform(s)!")
        else:
            post.status = 'failed'
            post.notes = f"Errors: {'; '.join(error_messages)}"
            print(f"  ❌ Partial or total failure. Errors: {'; '.join(error_messages)}")
        
        db.session.commit()
    
    print("\n✅ Post publishing cycle completed!")