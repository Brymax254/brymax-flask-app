from app import create_app, db
from app.models import User  # Import your models as needed
from werkzeug.security import generate_password_hash

app = create_app()

# Populate data in application context
with app.app_context():
    # Add a sample user
    user = User(username='BrymaxTech', password_hash=generate_password_hash('2710'), role='admin')
    db.session.add(user)

    # Commit the changes
    db.session.commit()
    print("Database populated successfully!")
