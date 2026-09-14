"""
app.py - Main Application Entry Point
This connects all the pieces together and starts the web server.
Think of this as the "ignition switch" that turns on the entire system.
"""
from flask import Flask, redirect, url_for
from flask_login import LoginManager, current_user
from models import db, User
from email_service import init_mail
from auth import auth
from admin import admin
from user import user
from webhooks import webhooks
from scheduler import start_scheduler
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Start the background scheduler (only if enabled)
if os.getenv('SCHEDULER_ENABLED', 'False') == 'True':
    start_scheduler(app)

# Create the Flask application
app = Flask(__name__)

# ============================================
# CONFIGURATION
# ============================================

# Secret key for sessions and security
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Database configuration
# For production, use PostgreSQL: postgresql://user:pass@localhost/dbname
# For development, use SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///ai_assistant.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Email configuration (for sending verification emails)
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')
app.config['APP_URL'] = os.getenv('APP_URL', 'http://localhost:5000')

# ============================================
# INITIALIZE EXTENSIONS
# ============================================

# Initialize the database
db.init_app(app)

# Initialize the email service
init_mail(app)

# Initialize Flask-Login (handles user sessions)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'  # Where to redirect if not logged in
login_manager.login_message = 'Please login to access this page.'
login_manager.login_message_category = 'warning'

# This function tells Flask-Login how to load a user from the database
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# ============================================
# REGISTER BLUEPRINTS (Connect all the pieces)
# ============================================

# Register the authentication blueprint (login, register, etc.)
app.register_blueprint(auth)

# Register the admin blueprint (your control panel)
app.register_blueprint(admin)

# Register the user blueprint (customer dashboard)
app.register_blueprint(user)

# Register the webhooks blueprint
app.register_blueprint(webhooks)

# ============================================
# ROOT ROUTE (Homepage)
# ============================================

@app.route('/')
def index():
    """
    Homepage - redirect based on login status.
    - If logged in as admin → go to admin panel
    - If logged in as user → go to user dashboard
    - If not logged in → go to login page
    """
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        else:
            return redirect(url_for('user.dashboard'))
    return redirect(url_for('auth.login'))

# ============================================
# CREATE DATABASE TABLES & ADMIN USER
# ============================================

with app.app_context():
    # Create all database tables
    db.create_all()
    print("✅ Database tables created successfully!")
    
    # Check if admin user exists
    admin_email = os.getenv('ADMIN_EMAIL')
    admin_password = os.getenv('ADMIN_PASSWORD')
    
    if admin_email and admin_password:
        # Check if this admin already exists
        existing_admin = User.query.filter_by(email=admin_email).first()
        
        if not existing_admin:
            # Create the admin user
            admin_user = User(
                email=admin_email,
                full_name='System Administrator',
                business_name='AI Assistant Pro',
                email_verified=True,  # Admin is auto-verified
                is_admin=True,        # This makes them an admin
                is_active=True
            )
            admin_user.set_password(admin_password)
            
            db.session.add(admin_user)
            db.session.commit()
            
            print(f"✅ Admin user created: {admin_email}")
        else:
            print(f"✅ Admin user already exists: {admin_email}")
    else:
        print("⚠️  Warning: ADMIN_EMAIL or ADMIN_PASSWORD not set in .env file")

# ============================================
# START THE SERVER
# ============================================

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🚀 AI ASSISTANT PRO - SAAS PLATFORM")
    print("="*70)
    print(f"📍 App URL: {app.config['APP_URL']}")
    print(f"👤 Admin Login: {os.getenv('ADMIN_EMAIL', 'Not configured')}")
    print(f"📧 Email Service: {'Configured' if app.config['MAIL_USERNAME'] else 'Not configured'}")
    print("="*70)
    print("\n👉 Open your browser and go to: http://localhost:5000")
    print("📝 Users can register at: http://localhost:5000/register")
    print("👑 Admin can login at: http://localhost:5000/login")
    print("="*70 + "\n")
    
    # Start the Flask development server
    # debug=True means it reloads when you change code
    # host='0.0.0.0' means it's accessible from other computers on your network
    # port=5000 is the standard Flask port
    app.run(debug=True, host='0.0.0.0', port=5000)