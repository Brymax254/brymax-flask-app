import os
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from flask import Flask
from flask_migrate import Migrate, upgrade, migrate
from app import create_app, db # Replace with your actual db instance import

# Replace with your actual database URI
DATABASE_URI = os.getenv("DATABASE_URI", "postgresql://brymax_db_0rar_user:UJAUb5GwFatfUxd5CvxCCltSNEN5asAf@dpg-cvjh7a24d50c73eep780-a.oregon-postgres.render.com/brymax_db_0rar")

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
                print("Checking updates table and sequence...")

                # Check if the 'updates' table exists
                result = connection.execute(text("SELECT to_regclass('public.updates');"))
                table_exists = result.scalar() is not None

                # Check if the sequence exists
                result = connection.execute(text("SELECT to_regclass('public.updates_id_seq');"))
                sequence_exists = result.scalar() is not None

                if not table_exists:
                    print("Creating 'updates' table...")
                    connection.execute(text("""
                        CREATE TABLE updates (
                            id SERIAL PRIMARY KEY,
                            data TEXT NOT NULL
                        );
                    """))

                if not sequence_exists:
                    print("Creating 'updates_id_seq' sequence...")
                    connection.execute(text("CREATE SEQUENCE updates_id_seq;"))

                print("Table and sequence check complete.")
            except SQLAlchemyError as e:
                print(f"Error checking or creating updates table/sequence: {e}")

def run_migrations():
    with app.app_context():
        try:
            print("Running migrations...")
            migrate()  # This creates a new migration script if needed
            upgrade()  # This applies the migration
            print("Migrations applied successfully.")
        except Exception as e:
            print(f"Error applying migrations: {e}")

if __name__ == "__main__":
    check_and_create_updates_table()
    run_migrations()
