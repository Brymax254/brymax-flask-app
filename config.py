import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', '9bbfdf8356bd72490566aedb34ec7600d3397a899e64813e')

    # Use PostgreSQL in production, fallback to SQLite for local development
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'postgresql://brymax_db_0rar_user:UJAUb5GwFatfUxd5CvxCCltSNEN5asAf@dpg-cvjh7a24d50c73eep780-a.oregon-postgres.render.com/brymax_db_0rar?sslmode=require'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = r"D:\BRYMAX\BRYMAX OFFICIAL DATA MANAGEMENT SYSTEM2\app\uploads"

    # Allow multiple file types
    ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'pdf', 'png', 'jpg', 'jpeg', 'docx', 'txt'}

    WTF_CSRF_ENABLED = False  # Disable CSRF protection

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True  # Enable SQL query logging for debugging


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')  # Requires PostgreSQL on Render


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test_brymax.db'  # Use a separate test database
