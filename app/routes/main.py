from flask import Blueprint, render_template
from flask_login import login_required, current_user

from app.models.task import Task
from app.models.habit import Habit

main_bp = Blueprint("main", __name__)


@main_bp.route("/dashboard")
@login_required
def dashboard():
    tasks = Task.query.filter_by(user_id=current_user.id).order_by(Task.created_at.desc()).limit(5).all()

    completed_count = Task.query.filter_by(user_id=current_user.id, status="completed").count()
    pending_count = Task.query.filter_by(user_id=current_user.id, status="pending").count()

    habits = Habit.query.filter_by(user_id=current_user.id).order_by(Habit.created_at.desc()).limit(5).all()

    return render_template(
        "dashboard.html",
        user=current_user.username,
        tasks=tasks,
        habits=habits,
        completed_count=completed_count,
        pending_count=pending_count
    )