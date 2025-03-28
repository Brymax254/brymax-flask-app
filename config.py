import os

class Config:
    SECRET_KEY = '9bbfdf8356bd72490566aedb34ec7600d3397a899e64813e'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///D:/BRYMAX/BRYMAX OFFICIAL DATA MANAGEMENT SYSTEM2/brymax.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'app/uploads'
    ALLOWED_EXTENSIONS = {'xlsx'}
    WTF_CSRF_ENABLED = False  # Disable CSRF protection

# Development environment configuration
class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True  # Enable SQL query logging for debugging

# Testing environment configuration
class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test_brymax.db'  # Use a separate test database
    WTF_CSRF_ENABLED = False  # Disable CSRF during testing

# Production environment configuration
class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'sqlite:///D:/BRYMAX/BRYMAX OFFICIAL DATA MANAGEMENT SYSTEM2/brymax.db'
    )  # Default to SQLite if DATABASE_URL env var is not set
