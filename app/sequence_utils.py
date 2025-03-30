# app/sequence_utils.py
import sys
import os

# If the module is executed directly, set up the package path.
if __name__ == '__main__' and __package__ is None:
    # Add parent directory to sys.path so that "app" can be imported.
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    __package__ = "app"

from flask import current_app
from app.extensions import db

def ensure_updates_sequence():
    """
    Ensures that the sequence 'updates_id_seq' exists and that the 'id' column
    in the 'updates' table is set to use this sequence as its default value.
    """
    with current_app.app_context():
        connection = db.engine.connect()
        trans = connection.begin()
        try:
            # Create the sequence if it doesn't exist
            connection.execute("CREATE SEQUENCE IF NOT EXISTS updates_id_seq;")
            # Alter the 'id' column in the 'updates' table to use the sequence
            connection.execute(
                "ALTER TABLE updates ALTER COLUMN id SET DEFAULT nextval('updates_id_seq');"
            )
            # Associate the sequence with the 'id' column (optional but recommended)
            connection.execute(
                "ALTER SEQUENCE updates_id_seq OWNED BY updates.id;"
            )
            trans.commit()
            print("Sequence 'updates_id_seq' is ensured and the default value is set.")
        except Exception as e:
            trans.rollback()
            print(f"Error ensuring sequence for the 'updates' table: {e}")
        finally:
            connection.close()

# Example usage: call this function once the application and tables are initialized.
if __name__ == "__main__":
    from app import create_app
    app = create_app()
    with app.app_context():
        # Uncomment if using db.create_all() for development
        # db.create_all()
        ensure_updates_sequence()
