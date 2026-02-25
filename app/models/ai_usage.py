from app import db
from datetime import datetime, date


class AIModelUsage(db.Model):
    """Tracks daily success/failure counts per Gemini model."""
    __tablename__ = 'ai_model_usage'

    id = db.Column(db.Integer, primary_key=True)
    model_name = db.Column(db.String(64), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, default=date.today, index=True)
    success_count = db.Column(db.Integer, default=0, server_default='0', nullable=False)
    failure_count = db.Column(db.Integer, default=0, server_default='0', nullable=False)
    last_failure_at = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='active')  # active | degraded

    __table_args__ = (
        db.UniqueConstraint('model_name', 'date', name='uq_model_date'),
    )

    @property
    def total_calls(self):
        return self.success_count + self.failure_count

    def __repr__(self):
        return f'<AIModelUsage {self.model_name} {self.date}>'
