from werkzeug.security import generate_password_hash
from app import create_app, db
from app.models import User  # Ensure you import the User model correctly

# Create the Flask application
app = create_app()

# Wrap database operations in app context
with app.app_context():
    # Update the user's password
    username = 'BrymaxTech'
    password = '2710'

    user = User.query.filter_by(username=username).first()
    if user:
        user.password_hash = generate_password_hash(password)
        db.session.commit()
        print(f"Password for {username} updated successfully!")
    else:
        print("User not found!")
