from flask import Blueprint, render_template, abort
from app.db import get_db

# Create a 'public' blueprint that requires NO login
bp = Blueprint('public', __name__)

@bp.route('/portal/<mid>')
def customer_portal(mid):
    """
    Public-facing view for customers to check their own balance/history.
    This route does NOT have @login_required, so it can be accessed via QR code.
    """
    db = get_db()
    
    # 1. Fetch Member
    member = db.execute("SELECT * FROM members WHERE id=?", (mid,)).fetchone()
    
    if not member:
        # If ID doesn't exist, show a 404 error
        abort(404)
        
    # 2. Fetch recent history (limit to last 10 entries for cleanliness)
    history = db.execute(
        "SELECT * FROM history WHERE member_id=? ORDER BY id DESC LIMIT 10", 
        (mid,)
    ).fetchall()
    
    # 3. Render the beautiful customer view
    return render_template('customer_view.html', member=member, history=history)