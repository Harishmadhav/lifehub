import markdown
from app.services.ai_service import generate_daily_plan
from flask import Blueprint, render_template
from flask_login import login_required, current_user

from app.models.task import Task
from app.models.habit import Habit
from app.models.note import Note

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


@main_bp.route("/analytics")
@login_required
def analytics():
    completed_tasks = Task.query.filter_by(user_id=current_user.id, status="completed").count()
    pending_tasks = Task.query.filter_by(user_id=current_user.id, status="pending").count()

    habits = Habit.query.filter_by(user_id=current_user.id).all()
    habit_names = [h.name for h in habits]
    habit_streaks = [h.current_streak for h in habits]

    total_notes = Note.query.filter_by(user_id=current_user.id).count()

    return render_template(
        "analytics.html",
        completed_tasks=completed_tasks,
        pending_tasks=pending_tasks,
        habit_names=habit_names,
        habit_streaks=habit_streaks,
        total_notes=total_notes
    )
@main_bp.route("/ai/daily-plan")
@login_required
def ai_daily_plan():
    tasks = Task.query.filter_by(user_id=current_user.id, status="pending").all()
    habits = Habit.query.filter_by(user_id=current_user.id).all()

    plan_raw = generate_daily_plan(tasks, habits)
    plan = markdown.markdown(plan_raw)

    return render_template("ai_plan.html", plan=plan)