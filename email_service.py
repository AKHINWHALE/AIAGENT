"""
email_service.py - Email Sending Service
This handles sending verification emails and notifications.
"""
from flask_mail import Mail, Message
from flask import current_app
import threading

# Create the mail object
mail = Mail()

def init_mail(app):
    """Initialize the email system with our Flask app."""
    mail.init_app(app)

def send_async_email(app, msg):
    """
    Send email in the background.
    We pass the 'app' instance explicitly so the thread has an application context.
    """
    with app.app_context():
        try:
            mail.send(msg)
            print(f"✅ Email successfully delivered to {msg.recipients[0]}")
        except Exception as e:
            print(f"❌ Email failed to send: {e}")

def send_verification_email(user):
    """Send an email with a verification link to a new user."""
    # Read the token that was already generated and saved to the database
    token = user.verification_token
    verification_url = f"{current_app.config['APP_URL']}/verify-email/{token}"
    
    msg = Message(
        subject='Verify Your Email - AI Assistant Pro',
        recipients=[user.email],
        sender=current_app.config['MAIL_DEFAULT_SENDER']
    )
    
    msg.html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f4f4f4;">
        <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px;">
            <h2 style="color: #667eea;">Welcome to AI Assistant Pro, {user.full_name}!</h2>
            <p>Thank you for registering. Please verify your email address to activate your account.</p>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{verification_url}" 
                   style="background-color: #667eea; color: white; padding: 15px 40px; 
                          text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                    Verify Email Address
                </a>
            </div>
            
            <p style="color: #666; font-size: 14px;">
                Or copy and paste this link into your browser:<br>
                <a href="{verification_url}" style="color: #667eea;">{verification_url}</a>
            </p>
            
            <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
            <p style="color: #999; font-size: 12px;">This link will expire in 24 hours.</p>
        </div>
    </body>
    </html>
    """
    
    app = current_app._get_current_object()
    thread = threading.Thread(target=send_async_email, args=(app, msg))
    thread.start()
    
    print(f"📧 Verification email triggered for {user.email}")
    return True
    
    # Get the actual app instance to pass to the thread
    app = current_app._get_current_object()
    
    # Start the background thread, passing the app and the message
    thread = threading.Thread(target=send_async_email, args=(app, msg))
    thread.start()
    
    print(f"📧 Verification email triggered for {user.email}")
    return True

def send_welcome_email(user):
    """Send a welcome email after the user verifies their email."""
    msg = Message(
        subject='Welcome to AI Assistant Pro! 🎉',
        recipients=[user.email],
        sender=current_app.config['MAIL_DEFAULT_SENDER']
    )
    
    msg.html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f4f4f4;">
        <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px;">
            <h2 style="color: #27ae60;">Welcome aboard, {user.full_name}! 🚀</h2>
            <p>Your email has been verified and your account is now fully active!</p>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{current_app.config['APP_URL']}/dashboard" 
                   style="background-color: #667eea; color: white; padding: 15px 40px; 
                          text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                    Go to Your Dashboard
                </a>
            </div>
        </div>
    </body>
    </html>
    """
    
    app = current_app._get_current_object()
    thread = threading.Thread(target=send_async_email, args=(app, msg))
    thread.start()
    
    print(f"📧 Welcome email triggered for {user.email}")
    return True


def send_daily_post_approval(user, post_content):
    """Send an email asking the user to approve the AI-generated post"""
    msg = Message(
        subject='📝 Approve Your Daily Post - AI Assistant Pro',
        recipients=[user.email],
        sender=current_app.config['MAIL_DEFAULT_SENDER']
    )
    
    approve_url = f"{current_app.config['APP_URL']}/dashboard/approve-daily-post"
    
    msg.html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f4f4f4;">
        <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px;">
            <h2 style="color: #667eea;">📝 Your AI-Generated Post is Ready!</h2>
            <p>Hi {user.full_name},</p>
            <p>Your AI assistant has drafted today's social media post. Please review it below:</p>
            
            <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #667eea;">
                <p style="margin: 0; line-height: 1.6;">{post_content}</p>
            </div>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{approve_url}" 
                   style="background-color: #10b981; color: white; padding: 15px 40px; 
                          text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                    ✅ Approve & Post
                </a>
                &nbsp;&nbsp;
                <a href="{approve_url}?action=edit" 
                   style="background-color: #667eea; color: white; padding: 15px 40px; 
                          text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                    ✏️ Edit First
                </a>
            </div>
            
            <p style="color: #666; font-size: 14px;">
                If you don't approve, just ignore this email and the post won't be published.
            </p>
        </div>
    </body>
    </html>
    """
    
    app = current_app._get_current_object()
    thread = threading.Thread(target=send_async_email, args=(app, msg))
    thread.start()
    
    print(f"📧 Daily post approval email sent to {user.email}")
    return True