from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    google_id = db.Column(db.String(255), unique=True, nullable=True)
    auth_provider = db.Column(db.String(50), default='email')
    is_admin = db.Column(db.Boolean, default=False)
    is_suspended = db.Column(db.Boolean, default=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    full_name = db.Column(db.String(128), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    profile_image = db.Column(db.String(256), nullable=True)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    quizzes = db.relationship('Quiz', backref='creator', lazy='dynamic')
    attempts = db.relationship('Attempt', backref='user', lazy='dynamic')
    activities = db.relationship('Activity', backref='user', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.username}>'

@login_manager.user_loader
def load_user(id):
    return db.session.get(User, int(id))
