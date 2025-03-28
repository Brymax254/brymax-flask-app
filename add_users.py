from app import create_app, db  # Import the app factory and db instance
from app.models import User, Role  # Import your models

# Create the Flask app instance
app = create_app()

# Push the application context to ensure the database is accessible
with app.app_context():
    try:
        # Ensure all tables are created
        db.create_all()

        # Create roles
        admin_role = Role.query.filter_by(name='admin').first()
        if not admin_role:
            admin_role = Role(name='admin')
            db.session.add(admin_role)
            db.session.commit()
            print("Admin role created.")

        # Create admin user
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(username='admin')
            admin_user.set_password('password')  # Set the password securely
            admin_user.roles.append(admin_role)  # Assign the admin role
            db.session.add(admin_user)
            db.session.commit()
            print("Admin user created.")

        # Create additional users (optional)
        regular_user = User.query.filter_by(username='user1').first()
        if not regular_user:
            regular_user = User(username='user1')
            regular_user.set_password('user1password')
            db.session.add(regular_user)
            db.session.commit()
            print("Regular user 'user1' created.")
    except Exception as e:
        print(f"An error occurred: {e}")