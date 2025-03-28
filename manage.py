from app import create_app, db
from flask_migrate import Migrate

app = create_app()  # Create the Flask application
migrate = Migrate(app, db)  # Initialize Flask-Migrate

if __name__ == "__main__":
    app.run(debug=True)
