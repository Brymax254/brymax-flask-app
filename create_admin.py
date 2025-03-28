from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

app = create_app()  # Ensure app is initialized

with app.app_context():  # Create an application context
    db.create_all()  # Ensure the database is ready

    # Check if the admin user exists
    existing_user = User.query.filter_by(username="admin").first()

    if existing_user:
        print("✅ Admin user already exists!")
    else:
        # Create an admin user
        admin_user = User(username="admin", password_hash=generate_password_hash("admin123"), role="admin")

        db.session.add(admin_user)
        db.session.commit()
        print("✅ Admin user created successfully!")
