from flask import Blueprint, render_template_string
from flask_login import login_required, current_user

main_bp = Blueprint("main", __name__)


@main_bp.route("/dashboard")
@login_required
def dashboard():
    return render_template_string(
        "<h1>Welcome, {{ user }}!</h1><p>This is a temporary dashboard placeholder.</p>",
        user=current_user.username
    )