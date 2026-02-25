from app import db
from datetime import datetime

class SupportTicket(db.Model):
    __tablename__ = 'support_tickets'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    subject = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='open') # open, closed

    user = db.relationship('User', backref=db.backref('support_tickets', lazy='dynamic'))
    replies = db.relationship('SupportReply', backref='ticket', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<SupportTicket {self.id} User {self.user_id}>'

class SupportReply(db.Model):
    __tablename__ = 'support_replies'

    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('support_tickets.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False) # user or admin responding
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('support_replies', lazy='dynamic'))

    def __repr__(self):
        return f'<SupportReply {self.id} Ticket {self.ticket_id}>'
