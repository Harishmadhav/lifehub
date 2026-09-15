from flask import Blueprint, render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired
from datetime import date, timedelta

from app.extensions import db
from app.models.habit import Habit
from app.models.habit_completion import HabitCompletion

habits_bp = Blueprint("habits", __name__)


class HabitForm(FlaskForm):
    name = StringField("Habit Name", validators=[DataRequired()])
    description = TextAreaField("Description")
    frequency = SelectField(
        "Frequency",
        choices=[("daily", "Daily"), ("weekly", "Weekly")],
        default="daily"
    )
    submit = SubmitField("Save Habit")


@habits_bp.route("/habits/create", methods=["GET", "POST"])
@login_required
def create_habit():
    form = HabitForm()

    if form.validate_on_submit():
        habit = Habit(
            name=form.name.data,
            description=form.description.data,
            frequency=form.frequency.data,
            user_id=current_user.id
        )
        db.session.add(habit)
        db.session.commit()

        flash("Habit created successfully.", "success")
        return redirect(url_for("habits.view_habits"))

    return render_template("habits/create_habit.html", form=form)

@habits_bp.route("/habits/<int:habit_id>/edit", methods=["GET", "POST"])
@login_required
def edit_habit(habit_id):
    habit = Habit.query.get_or_404(habit_id)

    if habit.user_id != current_user.id:
        abort(403)

    form = HabitForm(obj=habit)

    if form.validate_on_submit():
        habit.name = form.name.data
        habit.description = form.description.data
        habit.frequency = form.frequency.data
        db.session.commit()

        flash("Habit updated successfully.", "success")
        return redirect(url_for("habits.view_habits"))

    return render_template("habits/edit_habit.html", form=form, habit=habit)

@habits_bp.route("/habits")
@login_required
def view_habits():
    habits = Habit.query.filter_by(user_id=current_user.id).order_by(Habit.created_at.desc()).all()

    today = date.today()
    for habit in habits:
        completion_today = HabitCompletion.query.filter_by(
            habit_id=habit.id, completed_date=today
        ).first()
        habit.completed_today = completion_today is not None

    return render_template("habits/view_habits.html", habits=habits)


@habits_bp.route("/habits/<int:habit_id>/complete", methods=["POST"])
@login_required
def complete_habit(habit_id):
    habit = Habit.query.get_or_404(habit_id)

    if habit.user_id != current_user.id:
        abort(403)

    today = date.today()

    already_done = HabitCompletion.query.filter_by(
        habit_id=habit.id, completed_date=today
    ).first()

    if already_done:
        flash("Already marked complete for today.", "info")
        return redirect(url_for("habits.view_habits"))

    yesterday = today - timedelta(days=1)
    done_yesterday = HabitCompletion.query.filter_by(
        habit_id=habit.id, completed_date=yesterday
    ).first()

    if done_yesterday:
        habit.current_streak += 1
    else:
        habit.current_streak = 1

    if habit.current_streak > habit.longest_streak:
        habit.longest_streak = habit.current_streak

    completion = HabitCompletion(habit_id=habit.id, completed_date=today)
    db.session.add(completion)
    db.session.commit()

    flash(f"Habit marked complete! Current streak: {habit.current_streak}", "success")
    return redirect(url_for("habits.view_habits"))


@habits_bp.route("/habits/<int:habit_id>/delete", methods=["POST"])
@login_required
def delete_habit(habit_id):
    habit = Habit.query.get_or_404(habit_id)

    if habit.user_id != current_user.id:
        abort(403)

    HabitCompletion.query.filter_by(habit_id=habit.id).delete()

    db.session.delete(habit)
    db.session.commit()

    flash("Habit deleted.", "info")
    return redirect(url_for("habits.view_habits"))