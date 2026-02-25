from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.services.attempt_service import AttemptService
from app.services.quiz_service import QuizService
from app.services.activity_service import ActivityService
from datetime import datetime

attempt_bp = Blueprint('attempt', __name__)

@attempt_bp.route('/quiz/<int:quiz_id>/start', methods=['POST'])
@login_required
def start(quiz_id):
    quiz = QuizService.get_quiz(quiz_id)
    if not quiz or quiz.status != 'active':
        flash('Quiz is not available for taking.', 'error')
        return redirect(url_for('quiz.explore_quizzes'))
        
    now = datetime.now()
    if quiz.start_time and now < quiz.start_time:
        flash('This quiz has not started yet.', 'warning')
        return redirect(url_for('quiz.explore_quizzes'))
        
    if quiz.end_time and now > quiz.end_time:
        flash('This quiz has already ended.', 'warning')
        return redirect(url_for('quiz.explore_quizzes'))
        
    from app.models.attempt import Attempt
    from app import db
    attempts_count = db.session.query(Attempt).filter_by(quiz_id=quiz.id, user_id=current_user.id).count()
    if attempts_count >= 3:
        flash('You have reached the maximum number of attempts for this quiz (3 attempts max).', 'error')
        return redirect(url_for('quiz.explore_quizzes'))

    attempt, error = AttemptService.start_attempt(current_user.id, quiz_id)
    if error:
        flash(error, 'error')
        return redirect(url_for('quiz.explore_quizzes'))
        
    return redirect(url_for('attempt.take_quiz', attempt_id=attempt.id))

@attempt_bp.route('/attempt/<int:attempt_id>', methods=['GET', 'POST'])
@login_required
def take_quiz(attempt_id):
    attempt = AttemptService.get_attempt(attempt_id, current_user.id)
    if not attempt:
        flash('Invalid attempt.', 'error')
        return redirect(url_for('dashboard.index'))
        
    if attempt.submitted_at:
        return redirect(url_for('attempt.result', attempt_id=attempt.id))
        
    if request.method == 'POST':
        # Handle answer submission
        question_id = request.form.get('question_id')
        if question_id:
            question_id = int(question_id)
            
        selected_option = request.form.get('selected_option')
        
        success, error = AttemptService.submit_answer(
            attempt_id, current_user.id, question_id, selected_option
        )
        
        if request.form.get('action') == 'finish':
            finished_attempt, error = AttemptService.finish_attempt(attempt_id, current_user.id)
            if error:
                flash(error, 'error')
            else:
                ActivityService.log_activity(current_user.id, 'Attempted Quiz', f'Scored {finished_attempt.accuracy}% on quiz "{attempt.quiz.title}"')
                flash('Quiz completed successfully!', 'success')
                return redirect(url_for('attempt.result', attempt_id=attempt_id))
                
        # Redirect back to the same page for next question
        return redirect(url_for('attempt.take_quiz', attempt_id=attempt_id))
        
    # Get questions
    questions = attempt.quiz.questions.all()
    # Find next unanswered question
    answered_ids = [a.question_id for a in attempt.answers]
    
    current_question = None
    for q in questions:
        if q.id not in answered_ids:
            current_question = q
            break
            
    # Calculate time remaining
    time_remaining = None
    if attempt.quiz.time_limit:
        elapsed = (datetime.utcnow() - attempt.started_at).total_seconds()
        time_remaining = int(attempt.quiz.time_limit * 60 - elapsed)
        if time_remaining <= 0:
            # Time is up, auto submit
            finished_attempt, error = AttemptService.finish_attempt(attempt_id, current_user.id)
            if finished_attempt:
                ActivityService.log_activity(current_user.id, 'Attempted Quiz', f'Time expired. Scored {finished_attempt.accuracy}% on quiz "{attempt.quiz.title}"')
            flash('Time is up! Quiz auto-submitted.', 'info')
            return redirect(url_for('attempt.result', attempt_id=attempt_id))
            
    # If all answered but not submitted yet, show review page or submit
    is_last = (len(answered_ids) == len(questions) - 1) if current_question else True
    
    return render_template(
        'attempt/take.html', 
        attempt=attempt, 
        question=current_question,
        is_last=is_last,
        total=len(questions),
        current_index=len(answered_ids) + 1 if current_question else len(questions),
        time_remaining=time_remaining
    )

@attempt_bp.route('/attempt/<int:attempt_id>/result')
@login_required
def result(attempt_id):
    attempt = AttemptService.get_attempt(attempt_id, current_user.id)
    if not attempt or not attempt.submitted_at:
        flash('Result not available.', 'error')
        return redirect(url_for('dashboard.index'))
        
    return render_template('attempt/result.html', attempt=attempt)
