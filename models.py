"""
models.py - The Memory of Your App
This file defines what data we store in the database.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import secrets

# Create the database object
db = SQLAlchemy()


# ============================================
# TABLE 1: USERS (People who sign up)
# ============================================
class User(UserMixin, db.Model):
    """This is a table that stores every person who registers."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    business_name = db.Column(db.String(100))
    
    email_verified = db.Column(db.Boolean, default=False)
    verification_token = db.Column(db.String(100), unique=True)
    verification_sent_at = db.Column(db.DateTime)
    
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    subscription_tier = db.Column(db.String(20), default='free')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    social_accounts = db.relationship('SocialAccount', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    products = db.relationship('Product', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    triggers = db.relationship('Trigger', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    posts = db.relationship('Post', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    messages = db.relationship('CustomerMessage', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    scheduled_posts = db.relationship('ScheduledPost', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    media_uploads = db.relationship('MediaUpload', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    orders = db.relationship('Order', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    meetings = db.relationship('Meeting', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    settings = db.relationship('UserSettings', backref='user', uselist=False, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Scramble the password so hackers can't read it"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if password matches the scrambled one"""
        return check_password_hash(self.password_hash, password)
    
    def generate_verification_token(self):
        """Generate a random code for email verification"""
        self.verification_token = secrets.token_urlsafe(32)
        self.verification_sent_at = datetime.utcnow()
        return self.verification_token


# ============================================
# TABLE 2: SOCIAL ACCOUNTS
# ============================================
class SocialAccount(db.Model):
    """Stores each user's connected social media accounts"""
    __tablename__ = 'social_accounts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    platform = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(100), nullable=False)
    access_token = db.Column(db.Text)
    is_connected = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ============================================
# TABLE 3: PRODUCTS
# ============================================
class Product(db.Model):
    """Stores products that users sell"""
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    category = db.Column(db.String(100))
    image_url = db.Column(db.String(500))
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ============================================
# TABLE 4: TRIGGERS
# ============================================
class Trigger(db.Model):
    """Stores automated triggers"""
    __tablename__ = 'triggers'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    trigger_type = db.Column(db.String(50), nullable=False)
    trigger_value = db.Column(db.String(500), nullable=False)
    action_type = db.Column(db.String(50), nullable=False)
    action_value = db.Column(db.Text, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    execution_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ============================================
# TABLE 5: POSTS
# ============================================
class Post(db.Model):
    """Stores posts to be published"""
    __tablename__ = 'posts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    platforms = db.Column(db.String(500))
    status = db.Column(db.String(50), default='draft')
    scheduled_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ============================================
# TABLE 6: CUSTOMER MESSAGES
# ============================================
class CustomerMessage(db.Model):
    """Stores messages from customers"""
    __tablename__ = 'customer_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    customer_name = db.Column(db.String(100))
    customer_platform = db.Column(db.String(50), nullable=False)
    message_text = db.Column(db.Text, nullable=False)
    ai_response = db.Column(db.Text)
    is_resolved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ============================================
# TABLE 7: SCHEDULED POSTS (NEW!)
# ============================================
class ScheduledPost(db.Model):
    """Posts scheduled for future publication"""
    __tablename__ = 'scheduled_posts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    media_url = db.Column(db.String(500))
    media_type = db.Column(db.String(50))
    platforms = db.Column(db.String(500))
    scheduled_at = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(50), default='scheduled')
    auto_approve = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ============================================
# TABLE 8: MEDIA UPLOADS (NEW!)
# ============================================
class MediaUpload(db.Model):
    """Uploaded media files (images/videos)"""
    __tablename__ = 'media_uploads'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(50))
    file_size = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ============================================
# TABLE 9: ORDERS (NEW!)
# ============================================
class Order(db.Model):
    """Customer orders"""
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    customer_name = db.Column(db.String(100), nullable=False)
    customer_email = db.Column(db.String(120))
    customer_phone = db.Column(db.String(20))
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    quantity = db.Column(db.Integer, default=1)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='pending')
    delivery_date = db.Column(db.DateTime)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    product = db.relationship('Product', backref=db.backref('orders', lazy='dynamic'))


# ============================================
# TABLE 10: MEETINGS (NEW!)
# ============================================
class Meeting(db.Model):
    """Business meetings"""
    __tablename__ = 'meetings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    meeting_date = db.Column(db.DateTime, nullable=False)
    duration_minutes = db.Column(db.Integer, default=30)
    attendees = db.Column(db.Text)
    location = db.Column(db.String(200))
    status = db.Column(db.String(50), default='scheduled')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ============================================
# TABLE 11: USER SETTINGS (NEW!)
# ============================================
class UserSettings(db.Model):
    """User preferences and settings"""
    __tablename__ = 'user_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    
    auto_post_enabled = db.Column(db.Boolean, default=False)
    require_whatsapp_approval = db.Column(db.Boolean, default=True)
    daily_post_time = db.Column(db.String(10), default='07:00')
    
    auto_detect_trends = db.Column(db.Boolean, default=True)
    trend_categories = db.Column(db.Text)
    
    business_hours_start = db.Column(db.String(10), default='09:00')
    business_hours_end = db.Column(db.String(10), default='17:00')
    timezone = db.Column(db.String(50), default='UTC')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)



# ============================================
# TABLE 12: FLIGHT BOOKINGS (NEW!)
# ============================================
class FlightBooking(db.Model):
    """Customer flight bookings"""
    __tablename__ = 'flight_bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    customer_name = db.Column(db.String(100), nullable=False)
    customer_email = db.Column(db.String(120))
    customer_phone = db.Column(db.String(20))
    
    # Flight details
    airline = db.Column(db.String(100))
    flight_number = db.Column(db.String(50))
    departure_airport = db.Column(db.String(10))
    arrival_airport = db.Column(db.String(10))
    departure_date = db.Column(db.DateTime)
    arrival_date = db.Column(db.DateTime)
    
    # Booking info
    booking_reference = db.Column(db.String(50))
    status = db.Column(db.String(50), default='pending')  # pending, confirmed, cancelled, completed
    price = db.Column(db.Float)
    notes = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('flight_bookings', lazy='dynamic'))


# ============================================
# TABLE 13: LEADS (NEW!)
# ============================================
class Lead(db.Model):
    """Customer leads collected from social media"""
    __tablename__ = 'leads'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Contact info
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    
    # Lead details
    source = db.Column(db.String(50))  # facebook, instagram, twitter, whatsapp, etc.
    interest = db.Column(db.Text)  # What they're interested in
    best_time_to_contact = db.Column(db.String(100))
    
    # Status
    status = db.Column(db.String(50), default='new')  # new, contacted, qualified, converted, lost
    notes = db.Column(db.Text)
    follow_up_date = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('leads', lazy='dynamic'))