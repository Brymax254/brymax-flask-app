from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    db.create_all()

    existing_user = User.query.filter_by(username="Brymax").first()
    if not existing_user:
        admin_user = User(username="Brymax", is_admin=True)
        admin_user.password_hash = generate_password_hash("2710")
        db.session.add(admin_user)
        db.session.commit()
        print("Admin user created successfully!")
    else:
        print("Admin user already exists!")
