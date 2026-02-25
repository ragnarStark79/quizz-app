from app import db
from app.models.user import User
from werkzeug.security import generate_password_hash

class AuthService:
    @staticmethod
    def register_user(username, email, password):
        user = User.query.filter_by(username=username).first()
        if user:
            return None, 'Username already taken'
            
        user = User.query.filter_by(email=email).first()
        if user:
            return None, 'Email already registered'
            
        try:
            new_user = User(
                username=username, 
                email=email,
                password_hash=generate_password_hash(password)
            )
            db.session.add(new_user)
            db.session.commit()
            return new_user, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)
