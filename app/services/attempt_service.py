from app import db
from app.models.quiz import Quiz
from app.models.question import Question
from app.models.attempt import Attempt, Answer
from datetime import datetime

class AttemptService:
    @staticmethod
    def start_attempt(user_id, quiz_id):
        # Check if quiz exists and is active
        quiz = Quiz.query.filter_by(id=quiz_id, status='active').first()
        if not quiz:
            return None, "Quiz is not available."
            
        # Prevent creator from taking their own quiz
        if quiz.creator_id == user_id:
            return None, "You cannot attempt your own quiz."
            
        # Create new attempt
        attempt = Attempt(user_id=user_id, quiz_id=quiz_id)
        db.session.add(attempt)
        db.session.commit()
        
        return attempt, None

    @staticmethod
    def get_attempt(attempt_id, user_id):
        return Attempt.query.filter_by(id=attempt_id, user_id=user_id).first()

    @staticmethod
    def submit_answer(attempt_id, user_id, question_id, selected_option):
        attempt = AttemptService.get_attempt(attempt_id, user_id)
        if not attempt or attempt.submitted_at is not None:
            return False, "Invalid attempt or already submitted."
            
        question = Question.query.get(question_id)
        if not question or question.quiz_id != attempt.quiz_id:
            return False, "Invalid question."
            
        # Check if answer already exists
        answer = Answer.query.filter_by(attempt_id=attempt_id, question_id=question_id).first()
        is_correct = (selected_option == question.correct_option)
        
        if answer:
            answer.selected_option = selected_option
            answer.is_correct = is_correct
        else:
            answer = Answer(
                attempt_id=attempt_id, 
                question_id=question_id, 
                selected_option=selected_option,
                is_correct=is_correct
            )
            db.session.add(answer)
            
        db.session.commit()
        return True, ""

    @staticmethod
    def finish_attempt(attempt_id, user_id):
        attempt = AttemptService.get_attempt(attempt_id, user_id)
        if not attempt or attempt.submitted_at is not None:
            return None, "Invalid attempt or already submitted."
            
        # Calculate score
        answers = attempt.answers.all()
        correct_count = sum(1 for a in answers if a.is_correct)
        total_questions = attempt.quiz.questions.count()
        
        attempt.submitted_at = datetime.utcnow()
        attempt.score = correct_count
        attempt.accuracy = (correct_count / total_questions * 100) if total_questions > 0 else 0
        
        db.session.commit()
        return attempt, None
