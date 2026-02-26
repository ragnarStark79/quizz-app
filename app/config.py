import os
from dotenv import load_dotenv
from sqlalchemy.pool import NullPool

basedir = os.path.abspath(os.path.dirname(__file__))
# Load .env file if it exists (for local development)
env_path = os.path.join(basedir, '../.env')
# if os.path.exists(env_path):
#     load_dotenv(env_path)
if os.environ.get("VERCEL") is None and os.path.exists(env_path):
    load_dotenv(env_path)
    
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'
    
    # Database Configuration (supports Vercel Postgres integrations automatically)
    db_uri = os.environ.get('SQLALCHEMY_DATABASE_URI') or \
             os.environ.get('POSTGRES_URL_NON_POOLING') or \
             os.environ.get('POSTGRES_URL') or \
             'sqlite:///' + os.path.join(basedir, '../app.db')
             
    # Enforce psycopg3 driver schema for SQLAlchemy
    if db_uri.startswith('postgres://'):
        db_uri = db_uri.replace('postgres://', 'postgresql+psycopg://', 1)
    elif db_uri.startswith('postgresql://'):
        db_uri = db_uri.replace('postgresql://', 'postgresql+psycopg://', 1)
        
    SQLALCHEMY_DATABASE_URI = db_uri
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configure SQLAlchemy Engine Options based on environment
    if os.environ.get('VERCEL') == '1':
        # Serverless environment (Vercel) - Disable persistent connection pooling
        SQLALCHEMY_ENGINE_OPTIONS = {'poolclass': NullPool}
    else:
        # Development/VPS environment - Enable connection pooling and ping checks
        SQLALCHEMY_ENGINE_OPTIONS = {
            'pool_pre_ping': True,
            'pool_recycle': 300,
        }
    UPLOAD_FOLDER = os.path.join(basedir, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # 2MB
    FIREBASE_API_KEY = os.environ.get('FIREBASE_API_KEY', '')
    FIREBASE_AUTH_DOMAIN = os.environ.get('FIREBASE_AUTH_DOMAIN', '')
    FIREBASE_PROJECT_ID = os.environ.get('FIREBASE_PROJECT_ID', '')
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
    GEMINI_MODELS = [
        'gemini-2.5-flash',
        'gemini-2.5-pro',
        'gemini-1.5-flash',
        'gemini-1.5-pro',
    ]
    GEMINI_FALLBACK_ENABLED = True
    GEMINI_MAX_RETRIES = 3
    GEMINI_TIMEOUT = 60          # seconds per API call
    GEMINI_COOLDOWN_MINUTES = 5  # cooldown after rate-limit hit
    AI_DAILY_LIMIT = 10          # max AI generations per user per day
    
    # Authentication mode: must be set via environment variable (no hardcoded default)
    AUTH_EMAIL_ENABLED = os.environ.get('AUTH_EMAIL_ENABLED', '').lower() == 'true'
