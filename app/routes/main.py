from flask import Blueprint, render_template
from flask_login import login_required, current_user

from app.models.task import Task

main_bp = Blueprint("main", __name__)


@main_bp.route("/dashboard")
@login_required
def dashboard():
    tasks = Task.query.filter_by(user_id=current_user.id).order_by(Task.created_at.desc()).limit(5).all()

    completed_count = Task.query.filter_by(user_id=current_user.id, status="completed").count()
    pending_count = Task.query.filter_by(user_id=current_user.id, status="pending").count()

    dummy_habits = [
        {"name": "Read 20 minutes", "current_streak": 3},
        {"name": "Exercise", "current_streak": 5},
    ]

    return render_template(
        "dashboard.html",
        user=current_user.username,
        tasks=tasks,
        habits=dummy_habits,
        completed_count=completed_count,
        pending_count=pending_count
    )