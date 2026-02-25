from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or getattr(current_user, 'is_admin', False) != True:
            flash('You do not have permission to access that page.', 'error')
            # Redirecting to dashboard or explore if they are logged in but not admin
            if current_user.is_authenticated:
                return redirect(url_for('dashboard.index'))
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function
