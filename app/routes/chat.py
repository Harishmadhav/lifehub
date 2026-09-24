from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
import markdown

from app.models.task import Task
from app.models.habit import Habit
from app.services.ai_service import chat_with_assistant

chat_bp = Blueprint("chat", __name__)


@chat_bp.route("/chat", methods=["GET", "POST"])
@login_required
def chat():
    reply = None
    user_message = None

    if request.method == "POST":
        user_message = request.form.get("message")

        tasks = Task.query.filter_by(user_id=current_user.id).all()
        habits = Habit.query.filter_by(user_id=current_user.id).all()

        raw_reply = chat_with_assistant(user_message, tasks, habits)
        reply = markdown.markdown(raw_reply)

    return render_template("chat.html", reply=reply, user_message=user_message)