import sqlite3
import os
from flask import g
from werkzeug.security import generate_password_hash

# 1. DEFINE DATABASE PATH
# Render will provide 'DATABASE_PATH' (e.g., /var/data/members.db).
# Local testing will default to 'members.db'.
DB_PATH = os.getenv('DATABASE_PATH', 'members.db')

def get_db():
    """Opens a new database connection if there is none for the current context."""
    if 'db' not in g:
        # 2. ENSURE DIRECTORY EXISTS (Crucial for Render)
        # If the path is /var/data/members.db, we must ensure /var/data exists.
        db_dir = os.path.dirname(DB_PATH)
        if db_dir and not os.path.exists(db_dir):
            try:
                os.makedirs(db_dir, exist_ok=True)
            except OSError as e:
                print(f"Warning: Could not create DB directory: {e}")

        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    """Closes the database again at the end of the request."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db(app):
    """Initializes the database with schema and default data."""
    with app.app_context():
        db = get_db()
        
        # --- TABLE DEFINITIONS ---

        # 1. Members Table
        db.execute("""
            CREATE TABLE IF NOT EXISTS members (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                phone TEXT,
                expiry TEXT,
                signature INTEGER DEFAULT 0,
                aroma INTEGER DEFAULT 0,
                swedish INTEGER DEFAULT 0,
                notes TEXT
            )
        """)

        # 2. History Table
        db.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                member_id TEXT,
                service TEXT,
                therapist TEXT,
                branch TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(member_id) REFERENCES members(id)
            )
        """)

        # 3. Branches Table (For Dynamic Branch Management)
        db.execute("CREATE TABLE IF NOT EXISTS branches (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE)")

        # 4. Settings Table (For Secure PIN Storage)
        db.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)")


        # --- INITIAL SEED DATA ---

        # Seed Branches if the table is empty
        if db.execute("SELECT count(*) FROM branches").fetchone()[0] == 0:
            default_branches = [
                "Central", "Iyyattil", "Nettippadam", "Mattancheri", 
                "Banglore", "Thrissur", "Kottayam", "Adoor", 
                "Varkkala", "Trivandrum", "Kaloor", "Banjara"
            ]
            for b in default_branches:
                db.execute("INSERT OR IGNORE INTO branches (name) VALUES (?)", (b,))
        
        # Seed Default PINs if the table is empty
        # This ensures you can login immediately after deployment
        if db.execute("SELECT count(*) FROM settings").fetchone()[0] == 0:
            # Default: Admin=0000, Staff=1234
            db.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", 
                       ('admin_pin', generate_password_hash('0000')))
            db.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", 
                       ('staff_pin', generate_password_hash('1234')))

        db.commit()