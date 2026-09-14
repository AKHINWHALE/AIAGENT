"""
admin.py - Admin Control Panel
This is YOUR private control room. Only you (the admin) can access this.
Think of it as the "manager's office" of your website.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db, User, SocialAccount, Product, Trigger, Post, CustomerMessage
from functools import wraps
from datetime import datetime, timedelta

# Create a Blueprint for admin routes
# All admin routes will start with /admin (like /admin/dashboard)
admin = Blueprint('admin', __name__, url_prefix='/admin')


# ============================================
# SECURITY: Admin-Only Access
# ============================================
def admin_required(f):
    """
    This is a "decorator" that protects admin pages.
    It checks if the user is logged in AND is an admin.
    If not, it kicks them out.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is logged in
        if not current_user.is_authenticated:
            flash('Please login to access this page', 'error')
            return redirect(url_for('auth.login'))
        
        # Check if user is an admin
        if not current_user.is_admin:
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('user.dashboard'))
        
        # If both checks pass, allow access
        return f(*args, **kwargs)
    
    return decorated_function


# ============================================
# ROUTE 1: ADMIN DASHBOARD (Main Control Panel)
# ============================================
@admin.route('/')
@admin_required  # Only admins can access this
def dashboard():
    """
    This is the main admin dashboard.
    It shows you statistics about your entire system.
    """
    
    # Gather statistics
    stats = {
        'total_users': User.query.count(),
        'verified_users': User.query.filter_by(email_verified=True).count(),
        'active_users': User.query.filter_by(is_active=True).count(),
        'total_products': Product.query.count(),
        'total_posts': Post.query.count(),
        'total_messages': CustomerMessage.query.count(),
        'unresolved_messages': CustomerMessage.query.filter_by(is_resolved=False).count(),
        'users_today': User.query.filter(
            User.created_at >= datetime.utcnow() - timedelta(days=1)
        ).count(),
        'users_this_week': User.query.filter(
            User.created_at >= datetime.utcnow() - timedelta(days=7)
        ).count()
    }
    
    # Get recent activity
    recent_users = User.query.order_by(User.created_at.desc()).limit(10).all()
    recent_messages = CustomerMessage.query.order_by(
        CustomerMessage.created_at.desc()
    ).limit(10).all()
    
    # Show the admin dashboard page
    return render_template(
        'admin/dashboard.html',
        stats=stats,
        recent_users=recent_users,
        recent_messages=recent_messages
    )


# ============================================
# ROUTE 2: VIEW ALL USERS
# ============================================
@admin.route('/users')
@admin_required
def users():
    """
    Show a list of all registered users.
    You can search, filter, and manage them here.
    """
    
    # Get page number for pagination
    page = request.args.get('page', 1, type=int)
    
    # Get search query
    search = request.args.get('search', '')
    
    # Start with all users
    query = User.query
    
    # If there's a search term, filter the results
    if search:
        query = query.filter(
            (User.email.ilike(f'%{search}%')) |
            (User.full_name.ilike(f'%{search}%')) |
            (User.business_name.ilike(f'%{search}%'))
        )
    
    # Get users ordered by newest first, 50 per page
    users_list = query.order_by(User.created_at.desc()).paginate(
        page=page,
        per_page=50
    )
    
    return render_template('admin/users.html', users=users_list, search=search)


# ============================================
# ROUTE 3: ACTIVATE/DEACTIVATE A USER
# ============================================
@admin.route('/users/<int:user_id>/toggle-active', methods=['POST'])
@admin_required
def toggle_user_active(user_id):
    """
    Activate or deactivate a user account.
    Deactivated users cannot login.
    """
    
    # Find the user
    user = User.query.get_or_404(user_id)
    
    # Don't let admin deactivate themselves
    if user.id == current_user.id:
        flash('You cannot deactivate your own account!', 'error')
        return redirect(url_for('admin.users'))
    
    # Toggle the active status
    user.is_active = not user.is_active
    db.session.commit()
    
    # Show success message
    status = 'activated' if user.is_active else 'deactivated'
    flash(f'User {user.email} has been {status}', 'success')
    
    return redirect(url_for('admin.users'))


# ============================================
# ROUTE 4: DELETE A USER
# ============================================
@admin.route('/users/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    """
    Permanently delete a user and all their data.
    WARNING: This cannot be undone!
    """
    
    # Find the user
    user = User.query.get_or_404(user_id)
    
    # Don't let admin delete themselves
    if user.id == current_user.id:
        flash('You cannot delete your own account!', 'error')
        return redirect(url_for('admin.users'))
    
    # Don't let admin delete other admins
    if user.is_admin:
        flash('Cannot delete another admin user', 'error')
        return redirect(url_for('admin.users'))
    
    # Delete the user (this also deletes all their related data)
    user_email = user.email
    db.session.delete(user)
    db.session.commit()
    
    flash(f'User {user_email} and all their data have been permanently deleted', 'success')
    return redirect(url_for('admin.users'))


# ============================================
# ROUTE 5: MAKE USER AN ADMIN
# ============================================
@admin.route('/users/<int:user_id>/make-admin', methods=['POST'])
@admin_required
def make_admin(user_id):
    """
    Give a regular user admin privileges.
    """
    
    user = User.query.get_or_404(user_id)
    
    if user.is_admin:
        flash(f'{user.email} is already an admin', 'info')
    else:
        user.is_admin = True
        db.session.commit()
        flash(f'{user.email} is now an admin!', 'success')
    
    return redirect(url_for('admin.users'))


# ============================================
# ROUTE 6: SYSTEM HEALTH
# ============================================
@admin.route('/system')
@admin_required
def system():
    """
    Show system health and database statistics.
    """
    
    # Count records in each table
    db_stats = {
        'users': User.query.count(),
        'social_accounts': SocialAccount.query.count(),
        'products': Product.query.count(),
        'triggers': Trigger.query.count(),
        'posts': Post.query.count(),
        'messages': CustomerMessage.query.count()
    }
    
    return render_template('admin/system.html', db_stats=db_stats)


# ============================================
# ROUTE 7: API FOR STATS (For monitoring tools)
# ============================================
@admin.route('/api/stats')
@admin_required
def api_stats():
    """
    API endpoint that returns system statistics in JSON format.
    Useful for monitoring tools or external dashboards.
    """
    return jsonify({
        'total_users': User.query.count(),
        'verified_users': User.query.filter_by(email_verified=True).count(),
        'active_users': User.query.filter_by(is_active=True).count(),
        'total_products': Product.query.count(),
        'total_posts': Post.query.count(),
        'total_messages': CustomerMessage.query.count(),
        'timestamp': datetime.utcnow().isoformat()
    })