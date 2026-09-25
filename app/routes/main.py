from flask import Blueprint, render_template
from flask_login import login_required, current_user
from datetime import datetime, date
import markdown

from app.models.task import Task
from app.models.habit import Habit
from app.models.note import Note
from app.services.ai_service import generate_daily_plan

main_bp = Blueprint("main", __name__)


@main_bp.route("/dashboard")
@login_required
def dashboard():
    all_tasks = Task.query.filter_by(user_id=current_user.id).all()
    pending_tasks = [t for t in all_tasks if t.status == "pending"]
    completed_tasks = [t for t in all_tasks if t.status == "completed"]

    completed_count = len(completed_tasks)
    pending_count = len(pending_tasks)
    total_tasks = completed_count + pending_count

    task_progress = round((completed_count / total_tasks) * 100) if total_tasks > 0 else 0

    now = datetime.utcnow()
    # Mark overdue: pending + has a due date in the past
    for t in pending_tasks:
        t.is_overdue = bool(t.due_date and t.due_date < now)

    # Upcoming tasks with due dates, soonest first, for the schedule widget
    upcoming_tasks = sorted(
        [t for t in pending_tasks if t.due_date],
        key=lambda t: t.due_date
    )[:5]

    recent_tasks = sorted(all_tasks, key=lambda t: t.created_at, reverse=True)[:5]

    # Habits: completion-today % and a 21-day "habit formed" progress bar
    habits = Habit.query.filter_by(user_id=current_user.id).order_by(Habit.created_at.desc()).all()
    today = date.today()
    for h in habits:
        h.progress_percent = min(round((h.current_streak / 21) * 100), 100)

    habits_done_today = sum(
        1 for h in habits
        if any(c.completed_date == today for c in h.completions)
    ) if habits else 0
    habit_completion_rate = round((habits_done_today / len(habits)) * 100) if habits else 0

    # Overall daily progress = average of task completion % and today's habit completion %
    overall_progress = round((task_progress + habit_completion_rate) / 2)

    # Productivity Score: simple, explainable weighted formula (not AI/ML)
    # 50% task completion rate + 30% habit completion today + 20% streak consistency bonus
    if habits:
        avg_streak_ratio = sum(min(h.current_streak / 21, 1) for h in habits) / len(habits)
    else:
        avg_streak_ratio = 0
    productivity_score = round(
        (task_progress * 0.5) + (habit_completion_rate * 0.3) + (avg_streak_ratio * 100 * 0.2)
    )

    total_notes = Note.query.filter_by(user_id=current_user.id).count()

    return render_template(
        "dashboard.html",
        user=current_user.username,
        pending_tasks=pending_tasks,
        completed_count=completed_count,
        pending_count=pending_count,
        task_progress=task_progress,
        upcoming_tasks=upcoming_tasks,
        recent_tasks=recent_tasks,
        habits=habits,
        habit_completion_rate=habit_completion_rate,
        overall_progress=overall_progress,
        productivity_score=productivity_score,
        total_notes=total_notes,
        today=today
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