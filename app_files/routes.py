"""
app/routes.py - Main Routes
Handles dashboard and main pages
"""
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models import SocialPost, AgentConfig, ActivityLog
from datetime import datetime

main = Blueprint('main', __name__)


@main.route('/')
def index():
    """Landing page"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')


@main.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard"""
    # Get stats
    pending_posts = SocialPost.query.filter_by(
        user_id=current_user.id,
        status='pending'
    ).count()
    
    approved_posts = SocialPost.query.filter_by(
        user_id=current_user.id,
        status='approved'
    ).count()
    
    recent_activity = ActivityLog.query.filter_by(
        user_id=current_user.id
    ).order_by(ActivityLog.created_at.desc()).limit(10).all()
    
    stats = {
        'pending_posts': pending_posts,
        'approved_posts': approved_posts,
        'total_agents': AgentConfig.query.filter_by(user_id=current_user.id).count()
    }
    
    return render_template('dashboard.html', stats=stats, activity=recent_activity)


@main.route('/posts')
@login_required
def posts():
    """Manage social media posts"""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', 'all')
    
    query = SocialPost.query.filter_by(user_id=current_user.id)
    
    if status != 'all':
        query = query.filter_by(status=status)
    
    posts = query.order_by(SocialPost.created_at.desc()).paginate(
        page=page, per_page=20
    )
    
    return render_template('posts.html', posts=posts, status=status)


@main.route('/posts/<int:post_id>/approve', methods=['POST'])
@login_required
def approve_post(post_id):
    """Approve a post"""
    post = SocialPost.query.get_or_404(post_id)
    
    if post.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    post.status = 'approved'
    post.approved_at = datetime.utcnow()
    db.session.commit()
    
    flash('Post approved!', 'success')
    return redirect(url_for('main.posts'))


@main.route('/posts/<int:post_id>/reject', methods=['POST'])
@login_required
def reject_post(post_id):
    """Reject a post"""
    post = SocialPost.query.get_or_404(post_id)
    
    if post.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    reason = request.form.get('reason', '')
    post.status = 'rejected'
    post.rejection_reason = reason
    db.session.commit()
    
    flash('Post rejected', 'info')
    return redirect(url_for('main.posts'))


@main.route('/agents')
@login_required
def agents():
    """Manage AI agents"""
    agents = AgentConfig.query.filter_by(user_id=current_user.id).all()
    return render_template('agents.html', agents=agents)


@main.route('/settings')
@login_required
def settings():
    """User settings"""
    return render_template('settings.html')


@main.route('/billing')
@login_required
def billing():
    """Billing and subscription"""
    return render_template('billing.html', user=current_user)