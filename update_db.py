import os
import subprocess
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Flask app setup
app = Flask(__name__)

# Use environment variable for database connection
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL",
    "postgresql://brymax_zra0_user:nD2AY6N2igHVYTEMYxQZszKuSDYyvCi6@dpg-d0rg54buibrs73d7881g-a.oregon-postgres.render.com/brymax_zra0?sslmode=require"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)


def run_command(command):
    """Runs a shell command and exits if it fails."""
    print(f"Running: {' '.join(command)}")
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        print("Error:", result.stderr)
        sys.exit(result.returncode)
    print(result.stdout)


def update_database():
    """Applies migrations and upgrades the database."""

    # Ensure the correct app context
    with app.app_context():
        print("Checking for pending migrations...")

        # Generate new migration script (if changes exist)
        run_command(["flask", "db", "migrate", "-m", "Auto database update"])

        # Apply migrations
        run_command(["flask", "db", "upgrade"])

        print("Database successfully updated!")


if __name__ == "__main__":
    update_database()
