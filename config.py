import os

# Get the directory where config.py is located
BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get(
        'SECRET_KEY',
        '9bbfdf8356bd72490566aedb34ec7600d3397a899e64813e'
    )
    WTF_CSRF_ENABLED = False
    ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg", "txt", "docx"}

    # Database Configuration: Use local SQLite database at brymax.db
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        f"sqlite:///{os.path.join(BASE_DIR, 'brymax.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Cloudflare R2 Configuration remains unchanged
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    AWS_ACCESS_KEY_ID = '12c0afa42dbcbd1f1105923a0bfa83fb'
    AWS_SECRET_ACCESS_KEY = '0c184bc9dcd72a23ff3b441e5593c9628248e59bdb1d3ff0c85a4164ecb83a1b'
    AWS_STORAGE_BUCKET_NAME = 'brymax-uploads'
    AWS_S3_ENDPOINT_URL = 'https://b02658842e315caa9e0a14f4e8e5e169.r2.cloudflarestorage.com'
    AWS_S3_ADDRESSING_STYLE = "path"


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True  # Enable SQL query logging for debugging


class ProductionConfig(Config):
    DEBUG = False
    # In production, you can still override the DB URL via environment variable if needed.
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        f"sqlite:///{os.path.join(BASE_DIR, 'brymax.db')}"
    )


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test_brymax.db'  # Use a separate test database
