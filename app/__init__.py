from flask import Flask
from .config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import firebase_admin
from firebase_admin import credentials
import os

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    
    # Initialize Firebase Admin
    firebase_cred_path = os.environ.get('FIREBASE_CREDENTIALS')
    if firebase_cred_path and os.path.exists(firebase_cred_path):
        cred = credentials.Certificate(firebase_cred_path)
        try:
            firebase_admin.get_app()
        except ValueError:
            firebase_admin.initialize_app(cred)
            
    # Need to import models so they are registered with SQLAlchemy
    from app import models
            
    # Register blueprints mapping
    from app.routes.auth_routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    from app.routes.dashboard_routes import dashboard_bp
    app.register_blueprint(dashboard_bp)
    
    from app.routes.main_routes import main_bp
    app.register_blueprint(main_bp)

    from app.routes.quiz_routes import quiz_bp
    app.register_blueprint(quiz_bp)
    
    from app.routes.attempt_routes import attempt_bp
    app.register_blueprint(attempt_bp)

    from app.routes.support_routes import support_bp
    app.register_blueprint(support_bp)

    from app.routes.admin_routes import admin_bp
    app.register_blueprint(admin_bp)

    from app.routes.leaderboard_routes import leaderboard_bp
    app.register_blueprint(leaderboard_bp)

    return app
