from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse
from app import db
from app.models.user import User
from app.services.auth_service import AuthService
from app.services.activity_service import ActivityService
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
        ActivityService.log_activity(user.id, 'Logged In', 'User logged in successfully')
        
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('dashboard.index')
        return redirect(next_page)
        
    return render_template('auth/login.html')

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
            flash('Registration successful! Welcome to Quizz.', 'success')
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
