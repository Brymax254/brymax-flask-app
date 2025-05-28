import os
import shutil
import subprocess
import sys

def set_database_uri():
    """
    Set the DATABASE_URL environment variable to use the local SQLite database.
    Adjust the file path if necessary.
    """
    sqlite_path = r"D:/BRYMAX/BRYMAX OFFICIAL DATA MANAGEMENT SYSTEM2/brymax.db"
    # The connection string for SQLite: three slashes for file-based URIs.
    database_uri = f"sqlite:///{sqlite_path}"
    os.environ["DATABASE_URL"] = database_uri
    print(f"Set DATABASE_URL to {database_uri}")

def remove_migrations_folder():
    """
    Remove the migrations folder if it exists in the current directory.
    This step assumes you want to restart your migration history.
    """
    migrations_dir = "migrations"
    if os.path.exists(migrations_dir):
        try:
            shutil.rmtree(migrations_dir)
            print("Successfully removed existing 'migrations' folder.")
        except Exception as e:
            print(f"Error removing migrations folder: {e}")
            sys.exit(1)
    else:
        print("No 'migrations' folder found; nothing to remove.")

def run_command(command_list):
    """
    Run a command (as a list) and exit if it fails.
    """
    print("Running command:", " ".join(command_list))
    result = subprocess.run(command_list, capture_output=True, text=True)
    if result.returncode != 0:
        # Print both stdout and stderr to help diagnose issues.
        print("Command failed. STDOUT:")
        print(result.stdout)
        print("STDERR:")
        print(result.stderr)
        sys.exit(result.returncode)
    else:
        print(result.stdout)

def main():
    # Step 1: Set the DATABASE_URL environment variable
    set_database_uri()

    # Step 2: Remove existing migrations folder (restart migration history)
    remove_migrations_folder()

    # Step 3: Run Flask-Migrate commands. Ensure that 'flask' is in your PATH.
    # You may need to run these commands from the project root, where your Flask app is defined.
    # If your Flask app is not auto-detected, make sure the FLASK_APP env variable is set.
    os.environ["FLASK_APP"] = "run.py"  # Or the name of your main app module

    # Initialize migration repository
    run_command(["flask", "db", "init"])

    # Create new migration script based on the current state of the models.
    run_command(["flask", "db", "migrate", "-m", "Initial migration with SQLite"])

    # Apply the migration to update your SQLite database schema.
    run_command(["flask", "db", "upgrade"])

    print("All done! Your application is now using the SQLite database at:")
    print(os.environ["DATABASE_URL"])

if __name__ == '__main__':
    main()
