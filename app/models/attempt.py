from app import db
from datetime import datetime

class Attempt(db.Model):
    __tablename__ = 'attempts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    score = db.Column(db.Integer, default=0)
    accuracy = db.Column(db.Float, default=0.0)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    submitted_at = db.Column(db.DateTime)

    answers = db.relationship('Answer', backref='attempt', lazy='dynamic')

    def __repr__(self):
        return f'<Attempt {self.id} User {self.user_id} Quiz {self.quiz_id}>'

class Answer(db.Model):
    __tablename__ = 'answers'

    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey('attempts.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    selected_option = db.Column(db.String(1)) # 'A', 'B', 'C', 'D'
    is_correct = db.Column(db.Boolean, default=False)

    question = db.relationship('Question')

    def __repr__(self):
        return f'<Answer {self.id} Attempt {self.attempt_id}>'
