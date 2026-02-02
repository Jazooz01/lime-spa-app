from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash, generate_password_hash
from app.db import get_db

bp = Blueprint('auth', __name__)

@bp.route('/', methods=['GET', 'POST'])
def login():
    db = get_db()

    if request.method == 'POST':
        pin = request.form.get('pin')
        branch = request.form.get('branch')
        next_url = request.args.get('next')

        # Fetch stored hashes
        admin_hash = db.execute("SELECT value FROM settings WHERE key='admin_pin'").fetchone()['value']
        staff_hash = db.execute("SELECT value FROM settings WHERE key='staff_pin'").fetchone()['value']
        
        # Verify Admin
        if check_password_hash(admin_hash, pin):
            session['user_role'] = 'admin'
            session['branch'] = 'HQ'
            return redirect(next_url or url_for('admin.dashboard'))
            
        # Verify Staff
        if check_password_hash(staff_hash, pin):
            session['user_role'] = 'staff'
            session['branch'] = branch
            return redirect(next_url or url_for('staff.home'))
            
        flash("Invalid PIN", "error")
    
    # Fetch dynamic branches for the dropdown
    branches = db.execute("SELECT name FROM branches ORDER BY name").fetchall()
    return render_template('login.html', branches=branches)

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))