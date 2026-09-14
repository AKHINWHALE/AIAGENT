"""
database.py - The Memory of Your App
This stores all users, their social media accounts, products, and settings.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_bcrypt import Bcrypt
from datetime import datetime

# Create the database object
db = SQLAlchemy()
bcrypt = Bcrypt()

class User(UserMixin, db.Model):
    """A user who signed up for your service"""
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    full_name = db.Column(db.String(100))
    business_name = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships (what belongs to this user)
    social_accounts = db.relationship('SocialAccount', backref='user', lazy=True)
    products = db.relationship('Product', backref='user', lazy=True)
    triggers = db.relationship('Trigger', backref='user', lazy=True)
    customer_messages = db.relationship('CustomerMessage', backref='user', lazy=True)
    
    def set_password(self, password):
        """Scramble the password so hackers can't read it"""
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        """Check if the password matches"""
        return bcrypt.check_password_hash(self.password, password)


class SocialAccount(db.Model):
    """User's connected social media accounts"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    platform = db.Column(db.String(50))  # twitter, facebook, tiktok, whatsapp, instagram
    username = db.Column(db.String(100))
    access_token = db.Column(db.String(500))  # Encrypted token from the platform
    is_connected = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Product(db.Model):
    """Products the user sells (for customer service bot)"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    image_url = db.Column(db.String(500))
    category = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Trigger(db.Model):
    """Automated triggers (e.g., "When customer says X, do Y")"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100))
    trigger_type = db.Column(db.String(50))  # keyword, time, message_received
    trigger_value = db.Column(db.String(200))  # e.g., "price", "9:00 AM"
    action_type = db.Column(db.String(50))  # send_message, post_content, show_product
    action_value = db.Column(db.Text)  # What to do
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class CustomerMessage(db.Model):
    """Messages from customers (for the AI to respond to)"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    customer_name = db.Column(db.String(100))
    customer_platform = db.Column(db.String(50))  # whatsapp, instagram, etc.
    message_text = db.Column(db.Text)
    ai_response = db.Column(db.Text)
    is_resolved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ApprovedPost(db.Model):
    """Posts that were approved and need to be published"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    platforms = db.Column(db.String(500))  # "twitter,facebook,instagram"
    status = db.Column(db.String(50), default='pending')  # pending, posted, failed
    scheduled_time = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)