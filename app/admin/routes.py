from flask import render_template
from flask_login import login_required
from app.admin import admin_bp

@admin_bp.route('/users')
@login_required
def admin_users():
    return render_template('pages/admin_users.html')