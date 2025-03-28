from app import create_app, db
from app.models import User

# Create the app context
app = create_app()

with app.app_context():
    # Check if the user already exists
    if not User.query.filter_by(username="Brymax").first():
        # Create the user
        user = User(username="Brymax")
        user.set_password("2710")  # Set the initial password
        db.session.add(user)
        db.session.commit()
        print("User 'Brymax' created with password '2710'.")
    else:
        print("User 'Brymax' already exists.")