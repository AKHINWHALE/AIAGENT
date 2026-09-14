"""
scheduler.py - Background tasks that run automatically
"""
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

scheduler = BackgroundScheduler()


def start_scheduler(app):
    """Start the background scheduler with Flask app context"""
    
    def daily_post_task():
        """The task that runs every morning to generate posts"""
        with app.app_context():
            try:
                from daily_post_generator import generate_daily_posts
                print(f"\n⏰ [{datetime.now()}] Running daily post generator...")
                generate_daily_posts()
                print(f"✅ [{datetime.now()}] Daily post generator completed!\n")
            except Exception as e:
                print(f"❌ Scheduler error (daily posts): {e}")

    def publish_posts_task():
        """The task that runs every 5 minutes to publish due posts"""
        with app.app_context():
            try:
                from post_publisher import publish_due_posts
                print(f"\n⏰ [{datetime.now()}] Checking for posts to publish...")
                publish_due_posts()
                print(f"✅ [{datetime.now()}] Post publishing check completed!\n")
            except Exception as e:
                print(f"❌ Scheduler error (publishing): {e}")
    
    # 1. Schedule daily post generation (e.g., at 07:00)
    post_time = os.getenv('DAILY_POST_TIME', '07:00')
    hour, minute = map(int, post_time.split(':'))
    
    scheduler.add_job(
        daily_post_task,
        'cron',
        hour=hour,
        minute=minute,
        id='daily_posts',
        replace_existing=True
    )
    
    # 2. Schedule post publishing (every 5 minutes)
    scheduler.add_job(
        publish_posts_task,
        'interval',
        minutes=5,
        id='publish_posts',
        replace_existing=True
    )
    
    scheduler.start()
    print(f"⏰ Scheduler started! Daily posts at {post_time}, publishing checks every 5 mins.")


def stop_scheduler():
    """Stop the scheduler"""
    if scheduler.running:
        scheduler.shutdown()