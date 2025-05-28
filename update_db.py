import os
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from flask import Flask
from flask_migrate import Migrate, upgrade, migrate
from app import db  # Import your actual db instance

# Use local SQLite database URI by default.
DATABASE_URI = os.getenv(
    "DATABASE_URI",
    "sqlite:///D:/BRYMAX/BRYMAX OFFICIAL DATA MANAGEMENT SYSTEM2/brymax.db"
)

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize db and migration
db.init_app(app)
migrate_obj = Migrate(app, db)


def check_and_create_updates_table():
    with app.app_context():
        engine = create_engine(DATABASE_URI)
        with engine.connect() as connection:
            try:
                print("Checking 'updates' table...")

                # SQLite uses the 'sqlite_master' table to store schema info.
                # This query checks if the 'updates' table exists.
                result = connection.execute(text(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='updates';"
                ))
                table_exists = result.fetchone() is not None

                if not table_exists:
                    print("Creating 'updates' table...")
                    connection.execute(text("""
                        CREATE TABLE updates (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            data TEXT NOT NULL
                        );
                    """))
                else:
                    print("'updates' table already exists.")

                print("Table check complete.")
            except SQLAlchemyError as e:
                print(f"Error checking or creating 'updates' table: {e}")


def run_migrations():
    with app.app_context():
        try:
            print("Running migrations...")
            migrate()  # Create a new migration script if needed.
            upgrade()  # Apply the migration.
            print("Migrations applied successfully.")
        except Exception as e:
            print(f"Error applying migrations: {e}")


if __name__ == "__main__":
    check_and_create_updates_table()
    run_migrations()
