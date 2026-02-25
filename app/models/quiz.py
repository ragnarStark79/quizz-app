from app import db
from datetime import datetime

class Quiz(db.Model):
    __tablename__ = 'quizzes'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140), nullable=False)
    description = db.Column(db.Text)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), default='draft') # draft, scheduled, active, closed, suspended
    time_limit = db.Column(db.Integer) # in minutes
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    suspension_reason = db.Column(db.String(255))
    suspension_end = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    questions = db.relationship('Question', backref='quiz', lazy='dynamic')
    attempts = db.relationship('Attempt', backref='quiz', lazy='dynamic')

    def __repr__(self):
        return f'<Quiz {self.title}>'
