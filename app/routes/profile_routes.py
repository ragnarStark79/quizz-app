import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from app.services.profile_service import ProfileService
from app.models.user import User
from app.models.quiz import Quiz
from app.models.attempt import Attempt
from app.models.activity import Activity
from app.models.support import SupportTicket

profile_bp = Blueprint('profile', __name__)


@profile_bp.route('/profile')
@login_required
def index():
    """Render profile page — different context for admin vs user."""
    ctx = {}

    if current_user.is_admin:
        ctx['total_users'] = User.query.count()
        ctx['total_quizzes'] = Quiz.query.count()
        ctx['admin_activity_count'] = Activity.query.filter_by(user_id=current_user.id).count()
        ctx['total_tickets'] = SupportTicket.query.count()

    # Profile completion percentage
    fields = [current_user.full_name, current_user.email, current_user.bio, current_user.profile_image]
    ctx['completion'] = int((sum(1 for f in fields if f) / len(fields)) * 100)

    return render_template('profile/index.html', **ctx)


@profile_bp.route('/profile/update', methods=['POST'])
@login_required
def update():
    full_name = request.form.get('full_name', '')
    email = request.form.get('email', '')
    bio = request.form.get('bio', '')

    if not email:
        flash('Email is required.', 'error')
        return redirect(url_for('profile.index'))

    success, error = ProfileService.update_profile(current_user, full_name, email, bio)
    if success:
        flash('Profile updated successfully!', 'success')
    else:
        flash(error, 'error')

    return redirect(url_for('profile.index'))


@profile_bp.route('/profile/change-password', methods=['POST'])
@login_required
def change_password():
    current_pw = request.form.get('current_password', '')
    new_pw = request.form.get('new_password', '')
    confirm_pw = request.form.get('confirm_password', '')

    if new_pw != confirm_pw:
        flash('New passwords do not match.', 'error')
        return redirect(url_for('profile.index'))

    if not current_pw or not new_pw:
        flash('All password fields are required.', 'error')
        return redirect(url_for('profile.index'))

    success, error = ProfileService.change_password(current_user, current_pw, new_pw)
    if success:
        flash('Password changed successfully!', 'success')
    else:
        flash(error, 'error')

    return redirect(url_for('profile.index'))


@profile_bp.route('/profile/upload-avatar', methods=['POST'])
@login_required
def upload_avatar():
    file = request.files.get('avatar')
    upload_folder = os.path.join(current_app.static_folder, 'uploads')

    success, error = ProfileService.upload_avatar(current_user, file, upload_folder)
    if success:
        flash('Profile picture updated!', 'success')
    else:
        flash(error, 'error')

    return redirect(url_for('profile.index'))
