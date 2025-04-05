import sqlite3

# Connect to the database
conn = sqlite3.connect('brymax.db')
cursor = conn.cursor()

# Enable foreign keys
cursor.execute("PRAGMA foreign_keys = ON;")

# ============================
# 1. Role Table
# ============================
cursor.execute('''
CREATE TABLE IF NOT EXISTS role (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) UNIQUE NOT NULL
)
''')

# ============================
# 2. User Table
# ============================
cursor.execute('''
CREATE TABLE IF NOT EXISTS user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(128) NOT NULL
)
''')

# ============================
# 3. User Roles (Many-to-Many)
# ============================
cursor.execute('''
CREATE TABLE IF NOT EXISTS user_roles (
    user_id INTEGER NOT NULL,
    role_id INTEGER NOT NULL,
    PRIMARY KEY (user_id, role_id),
    FOREIGN KEY (user_id) REFERENCES user (id) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES role (id) ON DELETE CASCADE
)
''')

# ============================
# 4. Farmer Table
# ============================
cursor.execute('''
CREATE TABLE IF NOT EXISTS farmer (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    unique_number VARCHAR(10) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    county VARCHAR(50) NOT NULL,
    subcounty VARCHAR(50) NOT NULL,
    ward VARCHAR(50) NOT NULL,
    location VARCHAR(50) NOT NULL,
    phone_number VARCHAR(15) UNIQUE NOT NULL,
    village VARCHAR(50) NOT NULL,
    land_size FLOAT NOT NULL,
    season VARCHAR(3) NOT NULL,
    year INTEGER NOT NULL,
    farmer_number INTEGER NOT NULL,
    fertilizer_type VARCHAR(50),
    kgs_issued FLOAT,
    kgs_harvested_clean FLOAT,
    kgs_harvested_husk FLOAT,
    amount_received FLOAT
)
''')

# ============================
# 5. Harvest Table (Linked to Farmer)
# ============================
cursor.execute('''
CREATE TABLE IF NOT EXISTS harvest (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    farmer_id INTEGER NOT NULL,
    season VARCHAR(3) NOT NULL,
    year INTEGER NOT NULL,
    kgs_harvested FLOAT NOT NULL,
    FOREIGN KEY (farmer_id) REFERENCES farmer (id) ON DELETE CASCADE
)
''')

# ============================
# 6. Payment Table (Linked to Farmer)
# ============================
cursor.execute('''
CREATE TABLE IF NOT EXISTS payment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Fixed for SQLite auto-increment
    farmer_id INTEGER NOT NULL,
    amount_paid REAL NOT NULL,  -- Using REAL instead of FLOAT for better precision
    date_paid TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,  -- Ensures accurate date-time storage
    FOREIGN KEY (farmer_id) REFERENCES farmer (id) ON DELETE CASCADE
)
''')

# ============================
# 7. Seed Table (Linked to Farmer)
# ============================
cursor.execute('''
CREATE TABLE IF NOT EXISTS seed (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    farmer_id INTEGER NOT NULL,
    seed_type VARCHAR(50) NOT NULL,
    kgs_issued FLOAT NOT NULL,
    FOREIGN KEY (farmer_id) REFERENCES farmer (id) ON DELETE CASCADE
)
''')

# ============================
# 8. Payroll Table (For Employees)
# ============================
cursor.execute('''
CREATE TABLE IF NOT EXISTS payroll (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER NOT NULL,
    salary FLOAT NOT NULL,
    month VARCHAR(10) NOT NULL,
    year INTEGER NOT NULL,
    FOREIGN KEY (employee_id) REFERENCES employee (id) ON DELETE CASCADE
)
''')

# ============================
# 9. Employee Table
# ============================
cursor.execute('''
CREATE TABLE IF NOT EXISTS employee (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name VARCHAR(100) NOT NULL,
    position VARCHAR(50) NOT NULL,
    phone_number VARCHAR(15) UNIQUE NOT NULL,
    salary FLOAT NOT NULL
)
''')

# ============================
# Commit & Close Connection
# ============================
conn.commit()
conn.close()

print("✅ Database setup complete! Tables are ready.")
