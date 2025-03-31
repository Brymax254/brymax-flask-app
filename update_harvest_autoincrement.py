from sqlalchemy import text
from app import create_app, db  # Adjust this import based on your project structure

# Create your Flask application instance
app = create_app()


def update_harvest_autoincrement():
    # Push an application context so that Flask-SQLAlchemy can access the current app
    with app.app_context():
        engine = db.engine
        with engine.connect() as connection:
            trans = connection.begin()
            try:
                # Create the sequence if it does not already exist
                connection.execute(text("CREATE SEQUENCE IF NOT EXISTS harvest_id_seq"))

                # Alter the id column of the harvest table to set its default value from the sequence
                connection.execute(text("ALTER TABLE harvest ALTER COLUMN id SET DEFAULT nextval('harvest_id_seq')"))

                # Update the sequence value based on the maximum value in the table; if table is empty, start at 1.
                connection.execute(
                    text("SELECT setval('harvest_id_seq', COALESCE((SELECT MAX(id) FROM harvest) + 1, 1), false)")
                )

                trans.commit()
                print("Harvest table auto-increment updated successfully.")
            except Exception as e:
                trans.rollback()
                print("Error updating harvest auto-increment:", e)


if __name__ == "__main__":
    update_harvest_autoincrement()
