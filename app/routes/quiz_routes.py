from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from app.services.quiz_service import QuizService
from app.services.ai_quiz_service import AIQuizService
from app.services.activity_service import ActivityService
from datetime import datetime

quiz_bp = Blueprint('quiz', __name__)


@quiz_bp.route('/quiz/ai-generate', methods=['GET'])
@login_required
def ai_generate_page():
    _, ai_remaining = AIQuizService.get_daily_usage(current_user.id)
    ai_limit = current_app.config.get('AI_DAILY_LIMIT', 6)
    return render_template('quiz/ai_generate.html', ai_remaining=ai_remaining, ai_limit=ai_limit)


@quiz_bp.route('/quiz/ai-generate', methods=['POST'])
@login_required
def ai_generate():
    """Call Gemini to generate quiz JSON and return it to the frontend."""
    data = request.get_json(silent=True)
    if not data or not data.get('topic'):
        return jsonify({'success': False, 'error': 'Topic is required.'}), 400

    topic = data['topic']
    description = data.get('description', '')
    num_questions = min(max(int(data.get('num_questions', 10)), 5), 50)
    difficulty = data.get('difficulty', 'medium')

    # Enforce daily limit
    _, ai_remaining = AIQuizService.get_daily_usage(current_user.id)
    if ai_remaining <= 0:
        return jsonify({'success': False, 'error': 'Daily AI generation limit reached (6/day). Try again tomorrow!'}), 429

    try:
        quiz_data = AIQuizService.generate_quiz(topic, description, num_questions, difficulty)
        model_used = quiz_data.pop('model_used', 'unknown')
        # Log activity FIRST, then query usage so remaining is accurate
        ActivityService.log_activity(current_user.id, 'AI Generate', f'Generated AI quiz: "{topic}" (model: {model_used})')
        _, new_remaining = AIQuizService.get_daily_usage(current_user.id)
        return jsonify({'success': True, 'quiz': quiz_data, 'model_used': model_used, 'ai_remaining': new_remaining})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@quiz_bp.route('/quiz/ai-save', methods=['POST'])
@login_required
def ai_save():
    """Save AI-generated quiz and questions to the database."""
    data = request.get_json(silent=True)
    if not data or not data.get('quiz'):
        return jsonify({'success': False, 'error': 'No quiz data provided.'}), 400

    quiz_data = data['quiz']
    status = data.get('status', 'draft')
    time_limit = data.get('time_limit')

    if not quiz_data.get('questions'):
        return jsonify({'success': False, 'error': 'Quiz has no questions.'}), 400

    try:
        quiz = QuizService.create_quiz(
            user_id=current_user.id,
            title=quiz_data.get('title', 'AI Generated Quiz'),
            description=quiz_data.get('description', ''),
            time_limit=time_limit,
            status=status,
            is_ai_generated=True
        )

        letters = ['A', 'B', 'C', 'D']
        for q in quiz_data['questions']:
            correct_idx = q.get('correct_index', 0)
            QuizService.add_question(
                quiz_id=quiz.id,
                user_id=current_user.id,
                question_text=q['question'],
                options={
                    'A': q['options'][0],
                    'B': q['options'][1],
                    'C': q['options'][2],
                    'D': q['options'][3],
                },
                correct_option=letters[correct_idx]
            )

        action = 'AI Quiz Published' if status == 'active' else 'AI Quiz Saved'
        ActivityService.log_activity(current_user.id, action, f'Saved AI quiz: "{quiz.title}"')

        return jsonify({
            'success': True,
            'redirect': url_for('quiz.edit_quiz', quiz_id=quiz.id)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@quiz_bp.route('/quizzes')
@login_required
def list_quizzes():
    quizzes = QuizService.get_user_quizzes(current_user.id)
    _, ai_remaining = AIQuizService.get_daily_usage(current_user.id)
    ai_limit = current_app.config.get('AI_DAILY_LIMIT', 6)
    return render_template('quiz/list.html', quizzes=quizzes, ai_remaining=ai_remaining, ai_limit=ai_limit)

@quiz_bp.route('/explore')
def explore_quizzes():
    from app.models.quiz import Quiz
    from app.models.attempt import Attempt
    from sqlalchemy import func

    search_query = request.args.get('q', '').strip()
    filter_status = request.args.get('status', 'active')
    sort_by = request.args.get('sort', 'newest')

    query = Quiz.query

    if filter_status == 'all':
        query = query.filter(Quiz.status.in_(['active', 'scheduled', 'closed']))
    else:
        query = query.filter_by(status=filter_status)

    if search_query:
        query = query.filter(Quiz.title.ilike(f'%{search_query}%') | Quiz.description.ilike(f'%{search_query}%'))

    if sort_by == 'popular':
        query = query.outerjoin(Attempt).group_by(Quiz.id).order_by(func.count(Attempt.id).desc())
    else:
        query = query.order_by(Quiz.created_at.desc())

    public_quizzes = query.all()
    
    user_attempts = {}
    if current_user.is_authenticated:
        from app import db
        attempts = db.session.query(Attempt.quiz_id, func.count(Attempt.id)).filter_by(user_id=current_user.id).group_by(Attempt.quiz_id).all()
        user_attempts = {quiz_id: count for quiz_id, count in attempts}
        
    now = datetime.now()
    
    return render_template('quiz/explore.html', 
        quizzes=public_quizzes,
        search_query=search_query,
        current_status=filter_status,
        current_sort=sort_by,
        user_attempts=user_attempts,
        now=now
    )

@quiz_bp.route('/quiz/new', methods=['GET', 'POST'])
@login_required
def create_quiz():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        time_limit_str = request.form.get('time_limit', '').strip()
        time_limit = int(time_limit_str) if time_limit_str else None
            
        quiz = QuizService.create_quiz(
            user_id=current_user.id,
            title=title,
            description=description,
            time_limit=time_limit
        )
        
        ActivityService.log_activity(current_user.id, 'Created Quiz', f'Created quiz "{quiz.title}"')
        
        flash('Quiz created successfully! You can now add questions.', 'success')
        return redirect(url_for('quiz.edit_quiz', quiz_id=quiz.id))
        
    return render_template('quiz/create.html')

@quiz_bp.route('/quiz/<int:quiz_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_quiz(quiz_id):
    quiz = QuizService.get_quiz(quiz_id)
    if not quiz or quiz.creator_id != current_user.id:
        flash('Quiz not found or unauthorized.', 'error')
        return redirect(url_for('quiz.list_quizzes'))
        
    if request.method == 'POST':
        # Update quiz details
        action = request.form.get('action')
        
        if action == 'update_details':
            time_limit_str = request.form.get('time_limit', '').strip()
            time_limit_val = int(time_limit_str) if time_limit_str else None
            
            start_time_str = request.form.get('start_time')
            end_time_str = request.form.get('end_time')
            
            start_time_val = datetime.strptime(start_time_str, '%Y-%m-%dT%H:%M') if start_time_str else None
            end_time_val = datetime.strptime(end_time_str, '%Y-%m-%dT%H:%M') if end_time_str else None
            
            QuizService.update_quiz(
                quiz_id, current_user.id,
                title=request.form.get('title'),
                description=request.form.get('description'),
                time_limit=time_limit_val,
                start_time=start_time_val,
                end_time=end_time_val,
                status=request.form.get('status')
            )
            flash('Quiz updated.', 'success')
            
        elif action == 'add_question':
            options = {
                'A': request.form.get('option_a'),
                'B': request.form.get('option_b'),
                'C': request.form.get('option_c'),
                'D': request.form.get('option_d')
            }
            QuizService.add_question(
                quiz_id, current_user.id,
                request.form.get('question_text'),
                options,
                request.form.get('correct_option')
            )
            flash('Question added.', 'success')
            
        return redirect(url_for('quiz.edit_quiz', quiz_id=quiz.id))
        
    questions = QuizService.get_questions(quiz_id)
    return render_template('quiz/edit.html', quiz=quiz, questions=questions)

@quiz_bp.route('/quiz/<int:quiz_id>/delete', methods=['POST'])
@login_required
def delete_quiz(quiz_id):
    quiz = QuizService.get_quiz(quiz_id)
    if quiz and quiz.creator_id == current_user.id:
        quiz_title = quiz.title
        if QuizService.delete_quiz(quiz_id, current_user.id):
            ActivityService.log_activity(current_user.id, 'Deleted Quiz', f'Deleted quiz "{quiz_title}"')
            flash('Quiz deleted successfully.', 'success')
        else:
            flash('Error deleting quiz.', 'error')
    return redirect(url_for('quiz.list_quizzes'))

@quiz_bp.route('/question/<int:question_id>/delete', methods=['POST'])
@login_required
def delete_question(question_id):
    question = QuizService.get_questions(None) # Not needed here really, let's fix logic
    if QuizService.delete_question(question_id, current_user.id):
        flash('Question deleted.', 'success')
    else:
        flash('Error deleting question.', 'error')
    return redirect(request.referrer or url_for('quiz.list_quizzes'))
