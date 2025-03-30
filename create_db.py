#!/usr/bin/env python
import os
from app import create_app, db
from app.models import *  # Imports all your models

def ensure_upload_folder():
    upload_folder = create_app().config.get('UPLOAD_FOLDER')
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
        print(f"Created upload folder at {upload_folder}")
    else:
        print(f"Upload folder exists at {upload_folder}")

def recreate_tables():
    app = create_app()
    with app.app_context():
        # Uncomment the next two lines if you want to drop all tables first.
        # db.drop_all()
        # print("Dropped all tables.")
        db.create_all()
        print("Created all tables.")

if __name__ == '__main__':
    ensure_upload_folder()
    recreate_tables()
