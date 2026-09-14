"""
user.py - User Dashboard Routes
This handles everything regular users can do after they login.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from stripe_service import create_checkout_session
from models import db, SocialAccount, Product, Trigger, Post, CustomerMessage, UserSettings, ScheduledPost, MediaUpload, Order, Meeting, FlightBooking, Lead

# Create a Blueprint for user routes
user = Blueprint('user', __name__, url_prefix='/dashboard')


@user.route('/')
@login_required
def dashboard():
    """Main user dashboard showing statistics."""
    stats = {
        'social_accounts': current_user.social_accounts.count(),
        'products': current_user.products.count(),
        'triggers': current_user.triggers.filter_by(is_active=True).count(),
        'pending_posts': current_user.posts.filter_by(status='pending').count(),
        'unresolved_messages': current_user.messages.filter_by(is_resolved=False).count(),
        'scheduled_posts': current_user.scheduled_posts.filter_by(status='scheduled').count()
    }
    return render_template('user/dashboard.html', stats=stats)


@user.route('/connect-social', methods=['GET', 'POST'])
@login_required
def connect_social():
    """Let users connect their social media accounts."""
    if request.method == 'POST':
        platform = request.form.get('platform')
        username = request.form.get('username')
        access_token = request.form.get('access_token', '')
        
        existing = SocialAccount.query.filter_by(
            user_id=current_user.id,
            platform=platform
        ).first()
        
        if existing:
            existing.username = username
            existing.access_token = access_token
            existing.is_connected = True
        else:
            new_account = SocialAccount(
                user_id=current_user.id,
                platform=platform,
                username=username,
                access_token=access_token,
                is_connected=True
            )
            db.session.add(new_account)
        
        db.session.commit()
        flash(f'{platform.capitalize()} connected successfully!', 'success')
        return redirect(url_for('user.connect_social'))
    
    accounts = current_user.social_accounts.all()
    return render_template('user/connect_social.html', accounts=accounts)


@user.route('/products', methods=['GET', 'POST'])
@login_required
def products():
    """Let users add and manage their products."""
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        price = float(request.form.get('price'))
        stock = int(request.form.get('stock'))
        category = request.form.get('category', 'General')
        
        new_product = Product(
            user_id=current_user.id,
            name=name,
            description=description,
            price=price,
            stock=stock,
            category=category
        )
        db.session.add(new_product)
        db.session.commit()
        
        flash('Product added successfully!', 'success')
        return redirect(url_for('user.products'))
    
    products_list = current_user.products.all()
    return render_template('user/products.html', products=products_list)


@user.route('/triggers', methods=['GET', 'POST'])
@login_required
def triggers():
    """Let users set up automated triggers."""
    if request.method == 'POST':
        name = request.form.get('name')
        trigger_type = request.form.get('trigger_type')
        trigger_value = request.form.get('trigger_value')
        action_type = request.form.get('action_type')
        action_value = request.form.get('action_value')
        
        new_trigger = Trigger(
            user_id=current_user.id,
            name=name,
            trigger_type=trigger_type,
            trigger_value=trigger_value,
            action_type=action_type,
            action_value=action_value,
            is_active=True
        )
        db.session.add(new_trigger)
        db.session.commit()
        
        flash('Trigger created successfully!', 'success')
        return redirect(url_for('user.triggers'))
    
    triggers_list = current_user.triggers.all()
    return render_template('user/triggers.html', triggers=triggers_list)


@user.route('/posts', methods=['GET', 'POST'])
@login_required
def posts():
    """Let users create posts to publish to social media."""
    if request.method == 'POST':
        content = request.form.get('content')
        platforms = request.form.getlist('platforms')
        
        new_post = Post(
            user_id=current_user.id,
            content=content,
            platforms=','.join(platforms),
            status='pending'
        )
        db.session.add(new_post)
        db.session.commit()
        
        flash('Post created and queued for approval!', 'success')
        return redirect(url_for('user.posts'))
    
    posts_list = current_user.posts.order_by(Post.created_at.desc()).all()
    accounts = current_user.social_accounts.filter_by(is_connected=True).all()
    return render_template('user/posts.html', posts=posts_list, accounts=accounts)


@user.route('/messages')
@login_required
def messages():
    """Let users view customer messages."""
    page = request.args.get('page', 1, type=int)
    
    messages_list = current_user.messages.order_by(
        CustomerMessage.created_at.desc()
    ).paginate(page=page, per_page=20)
    
    return render_template('user/messages.html', messages=messages_list)


@user.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """User settings and preferences."""
    settings = UserSettings.query.filter_by(user_id=current_user.id).first()
    
    if not settings:
        settings = UserSettings(user_id=current_user.id)
        db.session.add(settings)
        db.session.commit()
    
    if request.method == 'POST':
        settings.auto_post_enabled = 'auto_post_enabled' in request.form
        settings.require_whatsapp_approval = 'require_whatsapp_approval' in request.form
        settings.daily_post_time = request.form.get('daily_post_time', '07:00')
        settings.auto_detect_trends = 'auto_detect_trends' in request.form
        settings.business_hours_start = request.form.get('business_hours_start', '09:00')
        settings.business_hours_end = request.form.get('business_hours_end', '17:00')
        settings.timezone = request.form.get('timezone', 'UTC')
        
        db.session.commit()
        flash('Settings saved successfully!', 'success')
        return redirect(url_for('user.settings'))
    
    return render_template('user/settings.html', settings=settings)


@user.route('/schedule', methods=['GET', 'POST'])
@login_required
def schedule():
    """Schedule posts for future publication."""
    if request.method == 'POST':
        content = request.form.get('content')
        scheduled_at = request.form.get('scheduled_at')
        platforms = request.form.getlist('platforms')
        auto_approve = 'auto_approve' in request.form
        
        # Handle file upload
        media_url = None
        if 'media' in request.files:
            file = request.files['media']
            if file and file.filename != '':
                import os
                from werkzeug.utils import secure_filename
                from datetime import datetime as dt
                
                uploads_dir = os.path.join('static', 'uploads', str(current_user.id))
                os.makedirs(uploads_dir, exist_ok=True)
                
                filename = secure_filename(file.filename)
                timestamp = dt.utcnow().strftime('%Y%m%d_%H%M%S')
                unique_filename = f"{timestamp}_{filename}"
                file_path = os.path.join(uploads_dir, unique_filename)
                file.save(file_path)
                
                media_url = f"/{file_path}"
                
                media = MediaUpload(
                    user_id=current_user.id,
                    filename=filename,
                    file_path=file_path,
                    file_type='video' if file.content_type.startswith('video') else 'image',
                    file_size=os.path.getsize(file_path)
                )
                db.session.add(media)
        
        from datetime import datetime as dt
        scheduled_datetime = dt.fromisoformat(scheduled_at)
        
        new_post = ScheduledPost(
            user_id=current_user.id,
            content=content,
            media_url=media_url,
            platforms=','.join(platforms),
            scheduled_at=scheduled_datetime,
            auto_approve=auto_approve,
            status='scheduled'
        )
        db.session.add(new_post)
        db.session.commit()
        
        flash('Post scheduled successfully!', 'success')
        return redirect(url_for('user.schedule'))
    
    scheduled_posts = current_user.scheduled_posts.filter(
        ScheduledPost.status == 'scheduled'
    ).order_by(ScheduledPost.scheduled_at).all()
    
    accounts = current_user.social_accounts.filter_by(is_connected=True).all()
    
    return render_template('user/schedule.html', 
                         scheduled_posts=scheduled_posts,
                         accounts=accounts)


@user.route('/orders', methods=['GET', 'POST'])
@login_required
def orders():
    """Manage customer orders"""
    if request.method == 'POST':
        customer_name = request.form.get('customer_name')
        customer_email = request.form.get('customer_email')
        customer_phone = request.form.get('customer_phone')
        product_id = request.form.get('product_id')
        quantity = int(request.form.get('quantity', 1))
        total_price = float(request.form.get('total_price'))
        delivery_date = request.form.get('delivery_date')
        notes = request.form.get('notes')
        
        from datetime import datetime as dt
        delivery_datetime = dt.fromisoformat(delivery_date) if delivery_date else None
        
        new_order = Order(
            user_id=current_user.id,
            customer_name=customer_name,
            customer_email=customer_email,
            customer_phone=customer_phone,
            product_id=product_id if product_id else None,
            quantity=quantity,
            total_price=total_price,
            delivery_date=delivery_datetime,
            notes=notes,
            status='pending'
        )
        db.session.add(new_order)
        db.session.commit()
        
        flash('Order created successfully!', 'success')
        return redirect(url_for('user.orders'))
    
    orders_list = current_user.orders.order_by(Order.created_at.desc()).all()
    products = current_user.products.all()
    return render_template('user/orders.html', orders=orders_list, products=products)


@user.route('/meetings', methods=['GET', 'POST'])
@login_required
def meetings():
    """Schedule and manage meetings"""
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        meeting_date = request.form.get('meeting_date')
        duration = int(request.form.get('duration', 30))
        attendees = request.form.get('attendees')
        location = request.form.get('location')
        
        from datetime import datetime as dt
        meeting_datetime = dt.fromisoformat(meeting_date)
        
        new_meeting = Meeting(
            user_id=current_user.id,
            title=title,
            description=description,
            meeting_date=meeting_datetime,
            duration_minutes=duration,
            attendees=attendees,
            location=location,
            status='scheduled'
        )
        db.session.add(new_meeting)
        db.session.commit()
        
        flash('Meeting scheduled successfully!', 'success')
        return redirect(url_for('user.meetings'))
    
    meetings_list = current_user.meetings.order_by(Meeting.meeting_date.desc()).all()
    return render_template('user/meetings.html', meetings=meetings_list)


@user.route('/flights', methods=['GET', 'POST'])
@login_required
def flights():
    """Manage flight bookings"""
    if request.method == 'POST':
        customer_name = request.form.get('customer_name')
        customer_email = request.form.get('customer_email')
        customer_phone = request.form.get('customer_phone')
        airline = request.form.get('airline')
        flight_number = request.form.get('flight_number')
        departure_airport = request.form.get('departure_airport')
        arrival_airport = request.form.get('arrival_airport')
        departure_date = request.form.get('departure_date')
        arrival_date = request.form.get('arrival_date')
        booking_reference = request.form.get('booking_reference')
        price = float(request.form.get('price', 0))
        notes = request.form.get('notes')
        
        from datetime import datetime as dt
        dep_datetime = dt.fromisoformat(departure_date) if departure_date else None
        arr_datetime = dt.fromisoformat(arrival_date) if arrival_date else None
        
        new_booking = FlightBooking(
            user_id=current_user.id,
            customer_name=customer_name,
            customer_email=customer_email,
            customer_phone=customer_phone,
            airline=airline,
            flight_number=flight_number,
            departure_airport=departure_airport,
            arrival_airport=arrival_airport,
            departure_date=dep_datetime,
            arrival_date=arr_datetime,
            booking_reference=booking_reference,
            price=price,
            notes=notes,
            status='pending'
        )
        db.session.add(new_booking)
        db.session.commit()
        
        flash('Flight booking created successfully!', 'success')
        return redirect(url_for('user.flights'))
    
    flights_list = current_user.flight_bookings.order_by(FlightBooking.departure_date.desc()).all()
    return render_template('user/flights.html', flights=flights_list)


@user.route('/leads', methods=['GET', 'POST'])
@login_required
def leads():
    """Manage customer leads"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        source = request.form.get('source')
        interest = request.form.get('interest')
        best_time = request.form.get('best_time_to_contact')
        notes = request.form.get('notes')
        follow_up = request.form.get('follow_up_date')
        
        from datetime import datetime as dt
        follow_up_date = dt.fromisoformat(follow_up) if follow_up else None
        
        new_lead = Lead(
            user_id=current_user.id,
            name=name,
            email=email,
            phone=phone,
            source=source,
            interest=interest,
            best_time_to_contact=best_time,
            notes=notes,
            follow_up_date=follow_up_date,
            status='new'
        )
        db.session.add(new_lead)
        db.session.commit()
        
        flash('Lead added successfully!', 'success')
        return redirect(url_for('user.leads'))
    
    leads_list = current_user.leads.order_by(Lead.created_at.desc()).all()
    return render_template('user/leads.html', leads=leads_list)
@user.route('/billing')
@login_required
def billing():
    """Show the pricing and billing page"""
    return render_template('user/billing.html')


@user.route('/checkout')
@login_required
def checkout():
    """Redirect the user to Stripe Checkout"""
    success_url = url_for('user.billing_success', _external=True)
    cancel_url = url_for('user.billing', _external=True)
    
    checkout_url = create_checkout_session(
        user_email=current_user.email,
        user_id=current_user.id,
        success_url=success_url,
        cancel_url=cancel_url
    )
    
    if checkout_url:
        return redirect(checkout_url)
    else:
        flash('Unable to start checkout. Please try again.', 'error')
        return redirect(url_for('user.billing'))


@user.route('/billing-success')
@login_required
def billing_success():
    """Handle successful payment return from Stripe"""
    # Upgrade the user to Pro!
    current_user.subscription_tier = 'pro'
    db.session.commit()
    
    flash('🎉 Welcome to Pro! Your account has been upgraded.', 'success')
    return redirect(url_for('user.dashboard'))