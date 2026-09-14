from flask import Blueprint, render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DateTimeField, SubmitField
from wtforms.validators import DataRequired, Optional
from datetime import datetime

from app.extensions import db
from app.models.task import Task

tasks_bp = Blueprint("tasks", __name__)


class TaskForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[Optional()])
    priority = SelectField(
        "Priority",
        choices=[("low", "Low"), ("medium", "Medium"), ("high", "High")],
        default="medium"
    )
    due_date = DateTimeField(
        "Due Date",
        format="%Y-%m-%d %H:%M",
        validators=[Optional()]
    )
    submit = SubmitField("Create Task")


@tasks_bp.route("/tasks/create", methods=["GET", "POST"])
@login_required
def create_task():
    form = TaskForm()

    if form.validate_on_submit():
        task = Task(
            title=form.title.data,
            description=form.description.data,
            priority=form.priority.data,
            due_date=form.due_date.data,
            user_id=current_user.id
        )

        db.session.add(task)
        db.session.commit()

        flash("Task created successfully.", "success")
        return redirect(url_for("main.dashboard"))

    return render_template("tasks/create_task.html", form=form)


@tasks_bp.route("/tasks")
@login_required
def view_tasks():
    tasks = Task.query.filter_by(user_id=current_user.id).order_by(Task.created_at.desc()).all()
    return render_template("tasks/view_tasks.html", tasks=tasks)

@tasks_bp.route("/tasks/<int:task_id>/edit", methods=["GET", "POST"])
@login_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)

    if task.user_id != current_user.id:
        abort(403)

    form = TaskForm(obj=task)

    if form.validate_on_submit():
        task.title = form.title.data
        task.description = form.description.data
        task.priority = form.priority.data
        task.due_date = form.due_date.data

        db.session.commit()

        flash("Task updated successfully.", "success")
        return redirect(url_for("tasks.view_tasks"))

    return render_template("tasks/edit_task.html", form=form, task=task)


@tasks_bp.route("/tasks/<int:task_id>/delete", methods=["POST"])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)

    if task.user_id != current_user.id:
        abort(403)

    db.session.delete(task)
    db.session.commit()

    flash("Task deleted.", "info")
    return redirect(url_for("tasks.view_tasks"))


@tasks_bp.route("/tasks/<int:task_id>/complete", methods=["POST"])
@login_required
def complete_task(task_id):
    task = Task.query.get_or_404(task_id)

    if task.user_id != current_user.id:
        abort(403)

    task.status = "completed"
    task.completed_at = datetime.utcnow()

    db.session.commit()

    flash("Task marked as complete.", "success")
    return redirect(url_for("tasks.view_tasks"))