from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.utils.decorators import admin_required
from app import db
from app.models.user import User
from app.models.quiz import Quiz
from app.models.attempt import Attempt
from app.models.activity import Activity
from app.models.support import SupportTicket
from app.services.support_service import SupportService
from app.services.activity_service import ActivityService

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
@admin_required
def index():
    users = User.query.order_by(User.id.desc()).all()
    quizzes = Quiz.query.order_by(Quiz.id.desc()).all()
    
    total_users = len(users)
    total_quizzes = len(quizzes)
    total_attempts = Attempt.query.count()
    open_ticket_list = SupportTicket.query.filter_by(status='open').order_by(SupportTicket.created_at.desc()).all()
    open_tickets = len(open_ticket_list)
    
    return render_template('admin/index.html', 
        users=users, 
        quizzes=quizzes,
        total_users=total_users,
        total_quizzes=total_quizzes,
        total_attempts=total_attempts,
        open_tickets=open_tickets,
        open_ticket_list=open_ticket_list,
    )

@admin_bp.route('/user/<int:user_id>/toggle_status', methods=['POST'])
@admin_required
def toggle_user_status(user_id):
    user = User.query.get(user_id)
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('admin.index'))
        
    if user.id == current_user.id:
        flash('You cannot change your own status.', 'warning')
        return redirect(url_for('admin.index'))
        
    if user.is_suspended:
        user.is_suspended = False
        ActivityService.log_activity(current_user.id, 'Admin Action', f'Reactivated user {user.username}')
        flash(f'User {user.username} has been activated.', 'success')
    else:
        user.is_suspended = True
        ActivityService.log_activity(current_user.id, 'Admin Action', f'Suspended user {user.username}')
        flash(f'User {user.username} has been suspended.', 'warning')
        
    db.session.commit()
    return redirect(url_for('admin.index'))

@admin_bp.route('/quiz/<int:quiz_id>/toggle_status', methods=['POST'])
@admin_required
def toggle_quiz_status(quiz_id):
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        flash('Quiz not found.', 'error')
        return redirect(url_for('admin.index'))
        
    if quiz.status == 'suspended':
        quiz.status = 'draft'
        ActivityService.log_activity(current_user.id, 'Admin Action', f'Restored suspended quiz "{quiz.title}"')
        flash(f'Quiz "{quiz.title}" has been restored to draft status.', 'success')
    else:
        quiz.status = 'suspended'
        quiz.suspension_reason = request.form.get('reason', 'Violation of terms')
        ActivityService.log_activity(current_user.id, 'Admin Action', f'Suspended quiz "{quiz.title}"')
        flash(f'Quiz "{quiz.title}" has been suspended.', 'warning')
        
    db.session.commit()
    return redirect(url_for('admin.index'))

@admin_bp.route('/support')
@admin_required
def support_tickets():
    status_filter = request.args.get('status', 'open')
    tickets = SupportService.get_all_tickets(status_filter=status_filter)
    return render_template('admin/support.html', tickets=tickets, current_filter=status_filter)

@admin_bp.route('/user/<int:user_id>')
@admin_required
def user_detail(user_id):
    user = User.query.get_or_404(user_id)
    quizzes = Quiz.query.filter_by(creator_id=user.id).all()
    attempts = Attempt.query.filter_by(user_id=user.id).all()
    total_quizzes = len(quizzes)
    active_quizzes = len([q for q in quizzes if q.status == 'active'])
    completed_attempts = [a for a in attempts if a.submitted_at is not None]
    avg_accuracy = sum(a.accuracy for a in completed_attempts) / len(completed_attempts) if completed_attempts else 0
    return render_template('admin/user_detail.html', 
        user=user,
        total_quizzes=total_quizzes,
        active_quizzes=active_quizzes,
        total_attempts=len(completed_attempts),
        avg_accuracy=avg_accuracy,
        recent_attempts=completed_attempts[-5:]
    )

@admin_bp.route('/activity')
@admin_required
def activity_logs():
    page = request.args.get('page', 1, type=int)
    user_filter = request.args.get('user_id', None, type=int)
    action_filter = request.args.get('action', '', type=str)

    query = Activity.query.order_by(Activity.timestamp.desc())
    if user_filter:
        query = query.filter_by(user_id=user_filter)
    if action_filter:
        query = query.filter(Activity.action_type.ilike(f'%{action_filter}%'))

    pagination = query.paginate(page=page, per_page=50, error_out=False)
    users = User.query.order_by(User.username).all()
    return render_template('admin/activity.html',
        logs=pagination.items,
        pagination=pagination,
        users=users,
        user_filter=user_filter,
        action_filter=action_filter
    )

# ── Dedicated section pages ──────────────────────────────────────────

@admin_bp.route('/users')
@admin_required
def users_page():
    users = User.query.order_by(User.id.desc()).all()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/quizzes')
@admin_required
def quizzes_page():
    quizzes = Quiz.query.order_by(Quiz.id.desc()).all()
    return render_template('admin/quizzes.html', quizzes=quizzes)

@admin_bp.route('/tickets')
@admin_required
def tickets_page():
    status_filter = request.args.get('status', 'open')
    tickets = SupportService.get_all_tickets(status_filter=status_filter)
    return render_template('admin/tickets.html', tickets=tickets, current_filter=status_filter)
