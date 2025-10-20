import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'DevBhoomiSecretKey2025')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', f'sqlite:///{os.path.join(os.path.dirname(__file__), "Instance", "devbhoomi.db")}')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_TYPE = 'filesystem'
    SESSION_FILE_DIR = os.path.join(os.path.dirname(__file__), 'Flask_Session')  # Session Files Directory
    SESSION_PERMANENT = False
    REPOSITORIES_PATH = os.path.join(os.path.dirname(__file__), 'Repositories')  # Path To Store Git Repositories
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'Uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB Max File Size

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False