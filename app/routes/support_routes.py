from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.services.support_service import SupportService
from app.services.activity_service import ActivityService

support_bp = Blueprint('support', __name__, url_prefix='/support')

@support_bp.route('/')
@login_required
def list_tickets():
    tickets = SupportService.get_user_tickets(current_user.id)
    return render_template('support/list.html', tickets=tickets)

@support_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_ticket():
    # Admins manage tickets — they don't file them
    if current_user.is_admin:
        flash('Admins manage tickets, not file them. Use the admin panel.', 'info')
        return redirect(url_for('admin.tickets_page'))

    if request.method == 'POST':
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        if not subject or not message:
            flash('Subject and message are required.', 'error')
        else:
            ticket = SupportService.create_ticket(current_user.id, subject, message)
            ActivityService.log_activity(current_user.id, 'Created Support Ticket', f'Submitted issue: "{subject}"')
            flash('Support ticket created. We will get back to you soon.', 'success')
            return redirect(url_for('support.view_ticket', ticket_id=ticket.id))
            
    return render_template('support/new.html')


@support_bp.route('/<int:ticket_id>', methods=['GET', 'POST'])
@login_required
def view_ticket(ticket_id):
    ticket = SupportService.get_ticket(ticket_id, current_user.id, current_user.is_admin)
    if not ticket:
        flash('Ticket not found or unauthorized.', 'error')
        return redirect(url_for('support.list_tickets'))
        
    if request.method == 'POST':
        if request.form.get('action') == 'reply':
            message = request.form.get('message')
            if message:
                SupportService.add_reply(ticket.id, current_user.id, message)
                ActivityService.log_activity(current_user.id, 'Support Reply', f'Replied to ticket #{ticket.id}')
                flash('Reply added.', 'success')
        elif request.form.get('action') == 'close':
            SupportService.close_ticket(ticket.id)
            ActivityService.log_activity(current_user.id, 'Closed Ticket', f'Closed ticket #{ticket.id}')
            flash('Ticket closed.', 'info')
            
        return redirect(url_for('support.view_ticket', ticket_id=ticket.id))
        
    return render_template('support/view.html', ticket=ticket)
