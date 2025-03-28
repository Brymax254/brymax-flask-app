import tempfile
import os
from flask import abort, jsonify, request
from flask_login import current_user
from functools import wraps

def generate_temp_chart(fig):
    """Generate temporary chart URL for WhatsApp"""
    temp_dir = tempfile.gettempdir()
    chart_path = os.path.join(temp_dir, 'whatsapp_chart.png')
    fig.write_image(chart_path)
    return f'file://{chart_path}'


from app.models import Farmer


def generate_farmer_id(season, year):
    """Generate a unique farmer ID based on season, year, and incremental number."""

    last_farmer = Farmer.query.filter_by(season=season, year=year).order_by(Farmer.farmer_number.desc()).first()

    if last_farmer:
        new_number = last_farmer.farmer_number + 1  # Increment farmer number
    else:
        new_number = 1  # Start at 000001

    farmer_id = f"{season}-{year}-{str(new_number).zfill(6)}"  # Format: OND-2024-000001
    return farmer_id, new_number

def admin_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated:
            # Redirect unauthenticated users to the login page
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({"error": "admin_access_only"}), 403
            abort(403)  # Forbidden for non-JSON requests
        if not hasattr(current_user, 'is_admin') or not current_user.is_admin:
            # Restrict access for non-admin users
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({"error": "admin_access_only"}), 403
            abort(403)  # Forbidden for non-JSON requests
        return func(*args, **kwargs)
    return decorated_view

