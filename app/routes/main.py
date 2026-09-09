from flask import Blueprint, render_template
from flask_login import login_required, current_user

main_bp = Blueprint("main", __name__)


@main_bp.route("/dashboard")
@login_required
def dashboard():
    # Dummy data for now — will be replaced with real DB queries in Task/Habit CRUD phases
    dummy_tasks = [
        {"title": "Finish LifeHub login", "status": "Completed"},
        {"title": "Build dashboard", "status": "In Progress"},
    ]

    dummy_habits = [
        {"name": "Read 20 minutes", "current_streak": 3},
        {"name": "Exercise", "current_streak": 5},
    ]

    return render_template(
        "dashboard.html",
        user=current_user.username,
        tasks=dummy_tasks,
        habits=dummy_habits,
        completed_count=1,
        pending_count=1
    )