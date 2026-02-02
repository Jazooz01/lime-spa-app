from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.db import get_db
from app.utils import login_required
import datetime

bp = Blueprint('staff', __name__, url_prefix='/staff')

@bp.route('/home')
@login_required('staff')
def home():
    return render_template('staff/home.html')

@bp.route('/scan/<mid>')
@login_required('staff')
def scan(mid):
    db = get_db()
    member = db.execute("SELECT * FROM members WHERE id=?", (mid,)).fetchone()
    if not member:
        flash("Member not found!", "error")
        return redirect(url_for('staff.home'))
    return render_template('staff/redeem.html', member=member)

@bp.route('/redeem/<mid>/<service>', methods=['POST'])
@login_required('staff')
def redeem(mid, service):
    therapist = request.form.get('therapist')
    db = get_db()
    
    # Check balance
    member = db.execute("SELECT * FROM members WHERE id=?", (mid,)).fetchone()
    if member[service] < 1:
        flash("Insufficient balance!", "error")
        return redirect(url_for('staff.scan', mid=mid))

    # Deduct
    db.execute(f"UPDATE members SET {service} = {service} - 1 WHERE id=?", (mid,))
    
    # Log History
    db.execute("INSERT INTO history (member_id, service, therapist, branch) VALUES (?,?,?,?)",
               (mid, service, therapist, session['branch']))
    db.commit()
    
    return render_template('staff/success.html', member=member, service=service)