from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.db import get_db
from app.utils import login_required, generate_card
import uuid

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/dashboard')
@login_required('admin')
def dashboard():
    search = request.args.get('q', '')
    db = get_db()
    if search:
        query = "SELECT * FROM members WHERE name LIKE ? OR id LIKE ? ORDER BY expiry DESC"
        members = db.execute(query, (f'%{search}%', f'%{search}%')).fetchall()
    else:
        members = db.execute("SELECT * FROM members ORDER BY rowid DESC LIMIT 50").fetchall()
    return render_template('admin/dashboard.html', members=members)

@bp.route('/member/new', methods=['GET', 'POST'])
@login_required('admin')
def new_member():
    if request.method == 'POST':
        mid = str(uuid.uuid4())[:8].upper()
        db = get_db()
        db.execute(
            "INSERT INTO members (id, name, phone, expiry, signature, aroma, swedish, notes) VALUES (?,?,?,?,?,?,?,?)",
            (mid, request.form['name'], request.form['phone'], request.form['expiry'], 
             int(request.form['signature']), int(request.form['aroma']), int(request.form['swedish']), "")
        )
        db.commit()
        
        # Generate Card immediately
        member = db.execute("SELECT * FROM members WHERE id=?", (mid,)).fetchone()
        generate_card(member)
        
        flash("Member Created & Card Generated!", "success")
        return redirect(url_for('admin.member_detail', mid=mid))
    return render_template('admin/member_form.html')

@bp.route('/member/<mid>')
@login_required('admin')
def member_detail(mid):
    db = get_db()
    member = db.execute("SELECT * FROM members WHERE id=?", (mid,)).fetchone()
    history = db.execute("SELECT * FROM history WHERE member_id=? ORDER BY id DESC", (mid,)).fetchall()
    return render_template('admin/member_detail.html', member=member, history=history)

@bp.route('/member/<mid>/edit', methods=['POST'])
@login_required('admin')
def update_member(mid):
    db = get_db()
    db.execute("UPDATE members SET name=?, phone=?, expiry=?, notes=? WHERE id=?",
               (request.form['name'], request.form['phone'], request.form['expiry'], request.form['notes'], mid))
    db.commit()
    # Regenerate card in case name/expiry changed
    member = db.execute("SELECT * FROM members WHERE id=?", (mid,)).fetchone()
    generate_card(member)
    flash("Member details updated.", "success")
    return redirect(url_for('admin.member_detail', mid=mid))

@bp.route('/history/edit/<int:hid>', methods=['GET', 'POST'])
@login_required('admin')
def edit_history(hid):
    db = get_db()
    if request.method == 'POST':
        db.execute("UPDATE history SET therapist=?, branch=?, timestamp=? WHERE id=?",
                   (request.form['therapist'], request.form['branch'], request.form['timestamp'], hid))
        db.commit()
        
        # Get member_id to redirect back
        entry = db.execute("SELECT member_id FROM history WHERE id=?", (hid,)).fetchone()
        flash("Log entry updated successfully.", "success")
        return redirect(url_for('admin.member_detail', mid=entry['member_id']))
    
    # GET request - Show form
    entry = db.execute("SELECT * FROM history WHERE id=?", (hid,)).fetchone()
    if not entry:
        flash("Entry not found", "error")
        return redirect(url_for('admin.dashboard'))
        
    return render_template('admin/edit_history.html', history=entry)

@bp.route('/history/delete/<int:hid>', methods=['POST'])
@login_required('admin')
def delete_history(hid):
    """Reverts a session booking"""
    db = get_db()
    entry = db.execute("SELECT * FROM history WHERE id=?", (hid,)).fetchone()
    if entry:
        # Refund the session
        service_col = entry['service'].lower()
        db.execute(f"UPDATE members SET {service_col} = {service_col} + 1 WHERE id=?", (entry['member_id'],))
        db.execute("DELETE FROM history WHERE id=?", (hid,))
        db.commit()
        flash("Booking deleted and session refunded.", "info")
        return redirect(url_for('admin.member_detail', mid=entry['member_id']))
    return redirect(url_for('admin.dashboard'))
import csv
import io
from flask import make_response

@bp.route('/member/<mid>/export')
@login_required('admin')
def export_member(mid):
    db = get_db()
    member = db.execute("SELECT * FROM members WHERE id=?", (mid,)).fetchone()
    history = db.execute("SELECT * FROM history WHERE member_id=? ORDER BY id DESC", (mid,)).fetchall()

    # Create an in-memory CSV file
    si = io.StringIO()
    cw = csv.writer(si)

    # 1. Write Member Details Section
    cw.writerow(['--- MEMBER PROFILE ---'])
    cw.writerow(['Member ID', member['id']])
    cw.writerow(['Name', member['name']])
    cw.writerow(['Phone', member['phone']])
    cw.writerow(['Expiry', member['expiry']])
    cw.writerow(['Notes', member['notes']])
    cw.writerow([]) # Empty line
    
    # 2. Write Balance Section
    cw.writerow(['--- CURRENT BALANCE ---'])
    cw.writerow(['Signature', member['signature']])
    cw.writerow(['Aroma', member['aroma']])
    cw.writerow(['Swedish', member['swedish']])
    cw.writerow([]) # Empty line

    # 3. Write History Headers
    cw.writerow(['--- VISIT HISTORY ---'])
    cw.writerow(['ID', 'Service', 'Therapist', 'Branch', 'Timestamp'])

    # 4. Write History Data
    for h in history:
        cw.writerow([h['id'], h['service'], h['therapist'], h['branch'], h['timestamp']])

    # Create the response
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = f"attachment; filename=member_{mid}_report.csv"
    output.headers["Content-type"] = "text/csv"
    return output
from werkzeug.security import generate_password_hash

# ... existing code ...

@bp.route('/settings')
@login_required('admin')
def settings():
    db = get_db()
    branches = db.execute("SELECT * FROM branches ORDER BY name").fetchall()
    return render_template('admin/settings.html', branches=branches)

@bp.route('/settings/branch/add', methods=['POST'])
@login_required('admin')
def add_branch():
    name = request.form.get('name').strip()
    if name:
        db = get_db()
        try:
            db.execute("INSERT INTO branches (name) VALUES (?)", (name,))
            db.commit()
            flash(f"Branch '{name}' added.", "success")
        except:
            flash("Branch already exists!", "error")
    return redirect(url_for('admin.settings'))

@bp.route('/settings/branch/delete/<int:bid>', methods=['POST'])
@login_required('admin')
def delete_branch(bid):
    db = get_db()
    db.execute("DELETE FROM branches WHERE id=?", (bid,))
    db.commit()
    flash("Branch removed.", "info")
    return redirect(url_for('admin.settings'))

@bp.route('/settings/pin/update', methods=['POST'])
@login_required('admin')
def update_pin():
    role_key = request.form.get('role_key') # 'admin_pin' or 'staff_pin'
    new_pin = request.form.get('new_pin')
    
    if len(new_pin) < 4:
        flash("PIN must be at least 4 digits.", "error")
        return redirect(url_for('admin.settings'))

    hashed = generate_password_hash(new_pin)
    db = get_db()
    db.execute("UPDATE settings SET value=? WHERE key=?", (hashed, role_key))
    db.commit()
    
    flash("Security PIN updated successfully.", "success")
    return redirect(url_for('admin.settings'))
import os
from flask import current_app

# ... existing routes ...

@bp.route('/member/delete/<mid>', methods=['POST'])
@login_required('admin')
def delete_member(mid):
    db = get_db()
    
    # 1. Delete from History first (Foreign Key cleanup)
    db.execute("DELETE FROM history WHERE member_id=?", (mid,))
    
    # 2. Delete from Members table
    db.execute("DELETE FROM members WHERE id=?", (mid,))
    db.commit()
    
    # 3. Delete the generated Card Image
    try:
        card_path = os.path.join(current_app.root_path, 'static', 'cards', f'{mid}.png')
        if os.path.exists(card_path):
            os.remove(card_path)
    except Exception as e:
        print(f"Error deleting card image: {e}")

    flash("Member permanently deleted.", "info")
    return redirect(url_for('admin.dashboard'))