import sqlite3
from flask import g, current_app

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect("members.db")
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None: db.close()

# app/db.py

def init_db(app):
    with app.app_context():
        db = get_db()
        
        # ... (Existing members/history tables remain here) ...

        # 1. New Table: Branches
        db.execute("CREATE TABLE IF NOT EXISTS branches (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE)")
        
        # 2. New Table: Settings (for PINs)
        db.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)")
        
        # Seed Initial Data (Run once)
        # Check if branches exist, if not, add the defaults from your image
        if db.execute("SELECT count(*) FROM branches").fetchone()[0] == 0:
            default_branches = [
                "Central", "Iyyattil", "Nettippadam", "Mattancheri", 
                "Banglore", "Thrissur", "Kottayam", "Adoor", 
                "Varkkala", "Trivandrum", "Kaloor", "Banjara"
            ]
            for b in default_branches:
                db.execute("INSERT OR IGNORE INTO branches (name) VALUES (?)", (b,))
        
        # Check if PINs exist in DB, if not, set default hashes
        if db.execute("SELECT count(*) FROM settings").fetchone()[0] == 0:
            from werkzeug.security import generate_password_hash
            # Default: Admin=0000, Staff=1234
            db.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", ('admin_pin', generate_password_hash('0000')))
            db.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", ('staff_pin', generate_password_hash('1234')))

        db.commit()