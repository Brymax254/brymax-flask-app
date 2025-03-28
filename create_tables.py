import sqlite3

# Connect to the database
conn = sqlite3.connect('site.db')
cursor = conn.cursor()

# Create the 'role' table
cursor.execute('''
CREATE TABLE IF NOT EXISTS role (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) UNIQUE NOT NULL
)
''')

# Create the 'user' table
cursor.execute('''
CREATE TABLE IF NOT EXISTS user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(128) NOT NULL
)
''')

# Create the 'user_roles' association table
cursor.execute('''
CREATE TABLE IF NOT EXISTS user_roles (
    user_id INTEGER NOT NULL,
    role_id INTEGER NOT NULL,
    PRIMARY KEY (user_id, role_id),
    FOREIGN KEY (user_id) REFERENCES user (id),
    FOREIGN KEY (role_id) REFERENCES role (id)
)
''')

# Commit changes and close the connection
conn.commit()
conn.close()