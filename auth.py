"""
auth.py - Authentication System
This handles user registration, login, email verification, and logout.
Think of this as the "security guard" of your website.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from models import db, User
from email_service import send_verification_email, send_welcome_email
from datetime import datetime, timedelta

# Create a "Blueprint" - a modular piece of our app
# All auth routes will start with /auth (like /auth/login, /auth/register)
auth = Blueprint('auth', __name__)


# ============================================
# ROUTE 1: REGISTRATION
# ============================================
@auth.route('/register', methods=['GET', 'POST'])
def register():
    from flask_login import current_user
    if current_user.is_authenticated:
        return redirect(url_for('user.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        business_name = request.form.get('business_name')
        
        if not email or not password or not full_name:
            flash('All fields are required', 'error')
            return redirect(url_for('auth.register'))
        
        if len(password) < 6:
            flash('Password must be at least 6 characters', 'error')
            return redirect(url_for('auth.register'))
        
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('This email is already registered. Please login.', 'error')
            return redirect(url_for('auth.login'))
        
        new_user = User(
            email=email,
            full_name=full_name,
            business_name=business_name,
            email_verified=False,
            is_active=True,
            is_admin=False
        )
        new_user.set_password(password)
        
        # 🌟 CRITICAL FIX: Generate the token BEFORE committing to the database!
        new_user.generate_verification_token()
        
        # NOW save the user AND the token to the database
        db.session.add(new_user)
        db.session.commit()
        
        try:
            send_verification_email(new_user)
            flash('Account created! Please check your email to verify your account.', 'success')
        except Exception as e:
            flash(f'Account created, but email failed to send: {str(e)}', 'warning')
        
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')


# ============================================
# ROUTE 2: EMAIL VERIFICATION
# ============================================
@auth.route('/verify-email/<token>')
def verify_email(token):
    """
    When user clicks the verification link in their email,
    this route checks the token and activates their account.
    """
    # CLEAN THE TOKEN: Remove any trailing periods, spaces, or slashes 
    # that email clients might accidentally add.
    clean_token = token.strip('. /\\')
    
    # Find the user with this verification token
    user = User.query.filter_by(verification_token=clean_token).first()
    
    # If token is invalid
    if not user:
        flash('Invalid or expired verification link. Please register again.', 'error')
        return redirect(url_for('auth.register'))
    
    # Check if token expired (24 hours)
    if user.verification_sent_at:
        if datetime.utcnow() - user.verification_sent_at > timedelta(hours=24):
            flash('This verification link has expired. Please register again.', 'error')
            return redirect(url_for('auth.register'))
    
    # Mark email as verified
    user.email_verified = True
    user.verification_token = None  # Clear the token (one-time use)
    db.session.commit()
    
    # Send welcome email
    try:
        send_welcome_email(user)
    except Exception as e:
        print(f"Welcome email failed: {e}")
    
    # Show success page
    return render_template('auth/verify_success.html', user=user)
# ============================================
# ROUTE 3: LOGIN
# ============================================
@auth.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handle user login.
    """
    from flask_login import current_user
    
    # If already logged in, redirect
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('user.dashboard'))
    
    # When user SUBMITS the login form
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Find the user
        user = User.query.filter_by(email=email).first()
        
        # Check if user exists AND password is correct
        if not user or not user.check_password(password):
            flash('Invalid email or password', 'error')
            return redirect(url_for('auth.login'))
        
        # Check if email is verified
        if not user.email_verified:
            flash('Please verify your email before logging in. Check your inbox.', 'warning')
            return redirect(url_for('auth.login'))
        
        # Check if account is active
        if not user.is_active:
            flash('Your account has been deactivated. Contact support.', 'error')
            return redirect(url_for('auth.login'))
        
        # SUCCESS! Log the user in
        login_user(user)
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        flash(f'Welcome back, {user.full_name}!', 'success')
        
        # Redirect admin to admin panel, regular users to their dashboard
        if user.is_admin:
            return redirect(url_for('admin.dashboard'))
        else:
            return redirect(url_for('user.dashboard'))
    
    # Show login form
    return render_template('auth/login.html')


# ============================================
# ROUTE 4: LOGOUT
# ============================================
@auth.route('/logout')
@login_required  # Only logged-in users can logout
def logout():
    """Log the user out"""
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))


# ============================================
# ROUTE 5: RESEND VERIFICATION EMAIL
# ============================================
@auth.route('/resend-verification')
def resend_verification():
    """Resend the verification email if user didn't receive it"""
    email = request.args.get('email')
    
    if not email:
        flash('No email provided', 'error')
        return redirect(url_for('auth.login'))
    
    user = User.query.filter_by(email=email).first()
    
    if user and not user.email_verified:
        send_verification_email(user)
        flash('Verification email resent! Please check your inbox.', 'success')
    elif user and user.email_verified:
        flash('Your email is already verified. Please login.', 'info')
    else:
        flash('Email not found in our system.', 'error')
    
    return redirect(url_for('auth.login'))