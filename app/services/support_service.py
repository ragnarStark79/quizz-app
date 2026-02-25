from app import db
from app.models.support import SupportTicket, SupportReply

class SupportService:
    @staticmethod
    def create_ticket(user_id, subject, message):
        ticket = SupportTicket(
            user_id=user_id,
            subject=subject,
            message=message
        )
        db.session.add(ticket)
        db.session.commit()
        return ticket

    @staticmethod
    def get_user_tickets(user_id):
        return SupportTicket.query.filter_by(user_id=user_id).order_by(SupportTicket.created_at.desc()).all()

    @staticmethod
    def get_ticket(ticket_id, user_id=None, is_admin=False):
        if is_admin:
            return SupportTicket.query.get(ticket_id)
        return SupportTicket.query.filter_by(id=ticket_id, user_id=user_id).first()

    @staticmethod
    def add_reply(ticket_id, user_id, message):
        ticket = SupportTicket.query.get(ticket_id)
        if not ticket:
            return None, "Ticket not found"
            
        reply = SupportReply(
            ticket_id=ticket.id,
            user_id=user_id,
            message=message
        )
        db.session.add(reply)
        db.session.commit()
        return reply, None

    @staticmethod
    def close_ticket(ticket_id):
        ticket = SupportTicket.query.get(ticket_id)
        if ticket:
            ticket.status = 'closed'
            db.session.commit()
            return True
        return False

    @staticmethod
    def get_all_tickets(status_filter=None):
        query = SupportTicket.query
        if status_filter and status_filter != 'all':
            query = query.filter_by(status=status_filter)
        return query.order_by(SupportTicket.created_at.desc()).all()
