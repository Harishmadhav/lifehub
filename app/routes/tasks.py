from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DateTimeField, SubmitField
from wtforms.validators import DataRequired, Optional

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