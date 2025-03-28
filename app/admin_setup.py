from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

app = create_app()  # Ensure the Flask app is created
app.app_context().push()  # Activate Flask app context

# Check if the admin user already exists
existing_user = User.query.filter_by(username="Brymax").first()
if existing_user:
    print("Admin user already exists!")
else:
    # Create a new admin user
    admin_user = User(username="Brymax", is_admin=True)  # Fix typo in "Brymax"

    # Securely hash the password
    admin_user.password_hash = generate_password_hash("2710")  # Ensure User model has password_hash column

    db.session.add(admin_user)
    db.session.commit()
    print("Admin user created successfully!")
