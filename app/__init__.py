import os
from flask import Flask
from config import Config, DevelopmentConfig, ProductionConfig, TestingConfig
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from .extensions import db  # Import the single SQLAlchemy instance

login_manager = LoginManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__)

    # Dynamic Environment Configuration
    env = os.environ.get('FLASK_ENV', 'development')  # Default to 'development'
    if env == 'production':
        app.config.from_object(ProductionConfig)
    elif env == 'testing':
        app.config.from_object(TestingConfig)
    else:
        app.config.from_object(DevelopmentConfig)
    # Determine the environment (production or local)
    if os.getenv('FLASK_ENV') == 'production':
        # Production environment (Linux server)
        UPLOAD_FOLDER = "/var/www/brymax.xyz/app/uploads"
    else:
        # Local development (Windows)
        UPLOAD_FOLDER = r"D:\BRYMAX\BRYMAX OFFICIAL DATA MANAGEMENT SYSTEM2\app\uploads"

    # Apply the configuration
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    # Initialize extensions
    CSRFProtect(app)
    db.init_app(app)  # Initialize SQLAlchemy with the app
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    # Register blueprints
    from .auth import auth_bp  # Authentication blueprint
    app.register_blueprint(auth_bp, url_prefix='/auth')
    from .routes import main_bp  # Main routes blueprint
    app.register_blueprint(main_bp)
    from .employee_routes import employee_bp  # Employee routes blueprint
    app.register_blueprint(employee_bp)
    from .sequence_utils import ensure_updates_sequence
    # After initializing and creating tables
    with app.app_context():
        ensure_updates_sequence()

    # Error Handling for Database Initialization
    try:
        with app.app_context():
            db.create_all()  # Create tables if they don't exist
    except Exception as e:
        print(f"Error initializing database: {e}")

    return app

@login_manager.user_loader
def load_user(user_id):
    from .models import User  # Import your User model
    return User.query.get(int(user_id))

