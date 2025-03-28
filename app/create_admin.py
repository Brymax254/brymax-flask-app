from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash  # Ensure password hashing

# Create the Flask app instance
app = create_app()

# Use app context for database operations
with app.app_context():
    # Check if admin exists
    existing_user = User.query.filter_by(username="BrymaxTec").first()

    if not existing_user:
        # Create admin user
        admin = User(
            username="BrymaxTec",
            password_hash=generate_password_hash("2710"),  # Securely hash the password
            role="admin"  # Ensure 'role' exists in your User model
        )
        db.session.add(admin)
        db.session.commit()
        print("✅ Admin user created successfully!")
    else:
        print("⚠️ Admin user already exists.")
