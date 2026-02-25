from app import db
from app.models.quiz import Quiz
from app.models.question import Question
from datetime import datetime

class QuizService:
    @staticmethod
    def create_quiz(user_id, title, description, time_limit=None, status='draft', is_ai_generated=False):
        quiz = Quiz(
            title=title,
            description=description,
            creator_id=user_id,
            time_limit=time_limit,
            status=status,
            is_ai_generated=is_ai_generated
        )
        db.session.add(quiz)
        db.session.commit()
        return quiz

    @staticmethod
    def get_quiz(quiz_id):
        return Quiz.query.get(quiz_id)

    @staticmethod
    def get_user_quizzes(user_id):
        return Quiz.query.filter_by(creator_id=user_id).order_by(Quiz.created_at.desc()).all()

    @staticmethod
    def update_quiz(quiz_id, user_id, **kwargs):
        quiz = Quiz.query.filter_by(id=quiz_id, creator_id=user_id).first()
        if not quiz:
            return None
            
        for key, value in kwargs.items():
            if hasattr(quiz, key):
                setattr(quiz, key, value)
                
        db.session.commit()
        return quiz

    @staticmethod
    def delete_quiz(quiz_id, user_id):
        quiz = Quiz.query.filter_by(id=quiz_id, creator_id=user_id).first()
        if quiz:
            # Delete associated questions first
            Question.query.filter_by(quiz_id=quiz.id).delete()
            db.session.delete(quiz)
            db.session.commit()
            return True
        return False

    @staticmethod
    def add_question(quiz_id, user_id, question_text, options, correct_option):
        # Verify ownership
        quiz = Quiz.query.filter_by(id=quiz_id, creator_id=user_id).first()
        if not quiz:
            return None
            
        question = Question(
            quiz_id=quiz_id,
            question_text=question_text,
            option_a=options.get('A'),
            option_b=options.get('B'),
            option_c=options.get('C'),
            option_d=options.get('D'),
            correct_option=correct_option
        )
        
        db.session.add(question)
        db.session.commit()
        return question

    @staticmethod
    def get_questions(quiz_id):
        return Question.query.filter_by(quiz_id=quiz_id).all()
        
    @staticmethod
    def delete_question(question_id, user_id):
        question = Question.query.get(question_id)
        if question and question.quiz.creator_id == user_id:
            db.session.delete(question)
            db.session.commit()
            return True
        return False
