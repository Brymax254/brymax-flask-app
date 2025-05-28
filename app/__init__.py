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

    # Dynamic environment configuration
    env = os.environ.get('FLASK_ENV', 'development')  # Default to 'development'
    if env == 'production':
        app.config.from_object(ProductionConfig)
        # Override the database URI for production using Render's PostgreSQL
        app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
            "DATABASE_URL",
            "postgresql://brymax_zra0_user:nD2AY6N2igHVYTEMYxQZszKuSDYyvCi6@dpg-d0rg54buibrs73d7881g-a.oregon-postgres.render.com/brymax_zra0"
        )
    elif env == 'testing':
        app.config.from_object(TestingConfig)
    else:
        app.config.from_object(DevelopmentConfig)

    # Determine the upload folder based on environment
    if env == 'production':
        # Production environment (Linux server)
        UPLOAD_FOLDER = "/var/www/brymax.xyz/app/uploads"
    else:
        # Local development (Windows)
        UPLOAD_FOLDER = r"D:\BRYMAX\BRYMAX OFFICIAL DATA MANAGEMENT SYSTEM2\app\uploads"

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

    # Run any additional setup (e.g., sequence utilities)
    from .sequence_utils import ensure_updates_sequence
    with app.app_context():
        ensure_updates_sequence()

    # Error handling for database initialization
    try:
        with app.app_context():
            db.create_all()  # Create tables if they don't exist (if not using migrations exclusively)
    except Exception as e:
        print(f"Error initializing database: {e}")

    return app


@login_manager.user_loader
def load_user(user_id):
    from .models import User  # Import your User model
    return User.query.get(int(user_id))
