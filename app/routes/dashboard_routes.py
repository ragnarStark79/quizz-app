from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.models.quiz import Quiz
from app.models.attempt import Attempt
from app.services.ai_quiz_service import AIQuizService
from app import db
from sqlalchemy import func

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def index():
    # Admins belong in the admin panel
    if current_user.is_admin:
        return redirect(url_for('admin.index'))

    # Quizzes created by user
    quizzes = Quiz.query.filter_by(creator_id=current_user.id).all()
    quizzes_created = len(quizzes)
    active_quizzes = sum(1 for q in quizzes if q.status == 'active')
    draft_quizzes = sum(1 for q in quizzes if q.status in ('draft', 'scheduled'))
    suspended_quizzes = sum(1 for q in quizzes if q.status == 'suspended')


    # Completed attempts
    attempts = (Attempt.query
                .filter_by(user_id=current_user.id)
                .filter(Attempt.submitted_at.isnot(None))
                .order_by(Attempt.submitted_at.desc())
                .all())

    total_attempts = len(attempts)
    avg_accuracy = sum(a.accuracy for a in attempts) / total_attempts if total_attempts else 0
    best_score = max((a.accuracy for a in attempts), default=0)

    # Recent 10 for score history chart
    score_history = list(reversed(attempts[:10]))
    score_labels = [a.quiz.title[:12] + '…' if len(a.quiz.title) > 12 else a.quiz.title for a in score_history]
    score_values = [round(a.accuracy, 1) for a in score_history]

    # Correct / wrong totals across all attempts answers
    from app.models.attempt import Answer
    all_answers = db.session.query(Answer).join(Attempt).filter(Attempt.user_id == current_user.id).all()
    correct_count = sum(1 for a in all_answers if a.is_correct)
    wrong_count = sum(1 for a in all_answers if not a.is_correct)
    total_qs = len(all_answers)

    # Per-quiz attempt counts for sidebar
    attempt_counts = dict(
        db.session.query(Attempt.quiz_id, func.count(Attempt.id))
        .filter(Attempt.user_id == current_user.id)
        .group_by(Attempt.quiz_id)
        .all()
    )

    recent_attempts = attempts[:5]

    # AI usage
    ai_used, ai_remaining = AIQuizService.get_daily_usage(current_user.id)
    from flask import current_app
    ai_limit = current_app.config.get('AI_DAILY_LIMIT', 6)

    return render_template('dashboard/index.html',
        quizzes=quizzes,
        quizzes_created=quizzes_created,
        active_quizzes=active_quizzes,
        draft_quizzes=draft_quizzes,
        suspended_quizzes=suspended_quizzes,
        total_attempts=total_attempts,
        avg_accuracy=avg_accuracy,
        best_score=best_score,
        score_history=score_history,
        score_labels=score_labels,
        score_values=score_values,
        correct_count=correct_count,
        wrong_count=wrong_count,
        total_qs=total_qs,
        attempt_counts=attempt_counts,
        recent_attempts=recent_attempts,
        ai_remaining=ai_remaining,
        ai_limit=ai_limit,
        ai_used=ai_used,
    )

