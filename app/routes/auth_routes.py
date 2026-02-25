from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse
from datetime import datetime
from app import db
from app.models.user import User
from app.services.auth_service import AuthService
from app.services.activity_service import ActivityService
from app.utils.firebase import verify_firebase_token
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        if user is None or not check_password_hash(user.password_hash, password):
            flash('Invalid email or password', 'error')
            return redirect(url_for('auth.login'))
            
        if user.is_suspended:
            flash('Your account has been suspended.', 'error')
            return redirect(url_for('auth.login'))
            
        login_user(user)
        user.last_login = datetime.utcnow()
        db.session.commit()
        ActivityService.log_activity(user.id, 'Logged In', 'User logged in successfully')
        
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('dashboard.index')
        return redirect(next_page)
        
    return render_template('auth/login.html')


@auth_bp.route('/google-login', methods=['POST'])
def google_login():
    """Handle Google sign-in via Firebase ID token verification."""
    data = request.get_json(silent=True)
    if not data or not data.get('idToken'):
        return jsonify({'success': False, 'error': 'Missing ID token.'}), 400

    # Verify token server-side
    decoded = verify_firebase_token(data['idToken'])
    if not decoded:
        return jsonify({'success': False, 'error': 'Invalid or expired token.'}), 401

    email = decoded.get('email')
    name = decoded.get('name', '')
    uid = decoded.get('uid')

    if not email:
        return jsonify({'success': False, 'error': 'Email not provided by Google.'}), 400

    # Find existing user by email
    user = User.query.filter_by(email=email).first()

    if user:
        # Link google_id if not already set
        if not user.google_id:
            user.google_id = uid
            user.auth_provider = 'google'
        # Check suspension
        if user.is_suspended:
            return jsonify({'success': False, 'error': 'Your account has been suspended.'}), 403
    else:
        # Create new user
        username = email.split('@')[0]
        # Ensure unique username
        base_username = username
        counter = 1
        while User.query.filter_by(username=username).first():
            username = f"{base_username}{counter}"
            counter += 1

        user = User(
            username=username,
            email=email,
            full_name=name,
            google_id=uid,
            auth_provider='google',
        )
        db.session.add(user)

    user.last_login = datetime.utcnow()
    db.session.commit()

    login_user(user)
    ActivityService.log_activity(user.id, 'Google Login', 'User logged in via Google')

    return jsonify({
        'success': True,
        'redirect': url_for('dashboard.index')
    })


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return redirect(url_for('auth.register'))
            
        if User.query.filter_by(username=username).first():
            flash('Username already taken', 'error')
            return redirect(url_for('auth.register'))
            
        user, error = AuthService.register_user(username, email, password)
        if user:
            login_user(user)
            ActivityService.log_activity(user.id, 'Registered', 'Account created successfully')
            flash('Registration successful! Welcome to QuizOasis.', 'success')
            return redirect(url_for('dashboard.index'))
        else:
            flash(error, 'error')
            return redirect(url_for('auth.register'))
        
    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    ActivityService.log_activity(current_user.id, 'Logged Out', 'User logged out')
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))
