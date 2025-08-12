import os

class Config:
    SECRET_KEY = os.environ.get('SESSION_SECRET', 'dev-secret-key')
    # Use SQLite as requested by user, fallback to PostgreSQL if DATABASE_URL is set
    SQLALCHEMY_DATABASE_URI = 'sqlite:///stock_management.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Remove pool settings for SQLite
    # SQLALCHEMY_ENGINE_OPTIONS = {
    #     "pool_recycle": 300,
    #     "pool_pre_ping": True,
    # }