import os
import re
from app import db
from app.models.user import User
from app.services.activity_service import ActivityService
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}
MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB


class ProfileService:

    @staticmethod
    def _allowed_file(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    @staticmethod
    def update_profile(user, full_name, email, bio):
        """Update user profile info. Returns (success, error_message)."""
        email = email.strip().lower()

        # Check email uniqueness (exclude current user)
        existing = User.query.filter(User.email == email, User.id != user.id).first()
        if existing:
            return False, 'That email is already in use by another account.'

        user.full_name = full_name.strip() if full_name else None
        user.email = email
        user.bio = bio.strip() if bio else None

        try:
            db.session.commit()
            ActivityService.log_activity(user.id, 'Profile Updated', 'Updated profile information')
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    @staticmethod
    def change_password(user, current_password, new_password):
        """Change password securely. Returns (success, error_message)."""
        # Google OAuth users cannot change password
        if user.google_id:
            return False, 'Google-linked accounts cannot change their password here.'

        if not user.password_hash or not check_password_hash(user.password_hash, current_password):
            return False, 'Current password is incorrect.'

        # Enforce password policy
        if len(new_password) < 8:
            return False, 'Password must be at least 8 characters.'
        if not re.search(r'\d', new_password):
            return False, 'Password must contain at least one number.'

        user.password_hash = generate_password_hash(new_password)

        try:
            db.session.commit()
            ActivityService.log_activity(user.id, 'Password Changed', 'User changed their password')
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    @staticmethod
    def upload_avatar(user, file, upload_folder):
        """Upload and save avatar. Returns (success, error_message)."""
        if not file or file.filename == '':
            return False, 'No file selected.'

        if not ProfileService._allowed_file(file.filename):
            return False, 'Only JPG, PNG, and WebP images are allowed.'

        # Check file size
        file.seek(0, os.SEEK_END)
        size = file.tell()
        file.seek(0)
        if size > MAX_FILE_SIZE:
            return False, 'File size must be under 2MB.'

        # Ensure upload directory exists
        profile_dir = os.path.join(upload_folder, 'profile')
        os.makedirs(profile_dir, exist_ok=True)

        # Delete old avatar if exists
        if user.profile_image:
            old_path = os.path.join(upload_folder, '..', user.profile_image)
            if os.path.exists(old_path):
                try:
                    os.remove(old_path)
                except OSError:
                    pass

        # Save new file
        filename = secure_filename(f"user_{user.id}_{file.filename}")
        filepath = os.path.join(profile_dir, filename)
        file.save(filepath)

        # Store relative path from static/
        user.profile_image = f"uploads/profile/{filename}"

        try:
            db.session.commit()
            ActivityService.log_activity(user.id, 'Avatar Updated', 'Updated profile picture')
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, str(e)
