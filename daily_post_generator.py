"""
daily_post_generator.py - Generates daily posts for all users
"""
from models import db, User, UserSettings, Product, ScheduledPost
from weather_service import get_weather
from trends_service import get_trending_topics
from ai_engine import ai_assistant
from datetime import datetime, timedelta
from email_service import send_daily_post_approval


def generate_daily_posts():
    """Generate daily posts for all users with auto-posting enabled"""
    
    # Get all users who have auto-posting enabled
    settings_list = UserSettings.query.filter_by(auto_post_enabled=True).all()
    
    if not settings_list:
        print("ℹ️  No users have auto-posting enabled. Skipping.")
        return
    
    print(f"📝 Generating daily posts for {len(settings_list)} user(s)...")
    
    # Get weather and trends ONCE (shared across all users)
    weather = get_weather()
    trends = get_trending_topics()
    
    for settings in settings_list:
        try:
            user = settings.user
            if not user or not user.is_active:
                continue
            
            # Get user's products
            products = user.products.filter_by(is_available=True).limit(3).all()
            
            # Generate the post using AI
            post_content = _generate_post_content(user, weather, trends, products)
            
            # Check if user requires WhatsApp/email approval
            if settings.require_whatsapp_approval:
                # Send approval email
                send_daily_post_approval(user, post_content)
                print(f"📧 Sent approval email to {user.email}")
            else:
                # Auto-approve: schedule the post directly
                _schedule_post(user, post_content, settings)
                print(f"✅ Auto-scheduled post for {user.email}")
        
        except Exception as e:
            print(f"❌ Error generating post for user {settings.user_id}: {e}")


def _generate_post_content(user, weather, trends, products):
    """Use AI to generate a daily post"""
    
    # Format trends
    trends_text = "\n".join([f"- {t['title']}" for t in trends[:3]])
    
    # Format products
    products_text = "\n".join([
        f"- {p.name}: ${p.price}" for p in products
    ]) if products else "No featured products today"
    
    # Build the prompt
    prompt = f"""Generate a short, engaging social media post (under 150 words) for {user.business_name or user.full_name}'s business.

TODAY'S WEATHER in {weather.get('city', 'your city')}:
- Temperature: {weather.get('temp', 20)}°C
- Conditions: {weather.get('description', 'beautiful')}

TRENDING TOPICS TODAY:
{trends_text}

MY PRODUCTS:
{products_text}

INSTRUCTIONS:
- Combine the weather, a relevant trend, and one of my products naturally
- Make it engaging and friendly
- Include 2-3 relevant hashtags
- Don't sound robotic - sound like a real person
- Don't use quotation marks around the post
"""
    
    # Use the AI to generate the post
    try:
        response = ai_assistant.client.chat.completions.create(
            model=ai_assistant.model,
            messages=[
                {"role": "system", "content": "You are a social media expert who writes engaging posts for businesses."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=250
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"❌ AI generation error: {e}")
        return f"Good morning! ☀️ It's a {weather.get('description', 'beautiful')} day in {weather.get('city', 'your city')} at {weather.get('temp', 20)}°C. Check out our latest products!"


def _schedule_post(user, content, settings):
    """Schedule the post for today"""
    
    # Parse the daily post time
    post_time = settings.daily_post_time or '07:00'
    hour, minute = map(int, post_time.split(':'))
    
    # Schedule for today (or tomorrow if time has passed)
    now = datetime.utcnow()
    scheduled_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if scheduled_time <= now:
        scheduled_time += timedelta(days=1)
    
    # Get user's connected platforms
    accounts = user.social_accounts.filter_by(is_connected=True).all()
    platforms = ','.join([a.platform for a in accounts]) if accounts else 'all'
    
    # Create the scheduled post
    post = ScheduledPost(
        user_id=user.id,
        content=content,
        platforms=platforms,
        scheduled_at=scheduled_time,
        status='scheduled',
        auto_approve=True
    )
    db.session.add(post)
    db.session.commit()
    
    return post