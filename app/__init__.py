from flask import Flask
from config import Config
from app.extensions import db, login_manager
from app.models.user import User
from app.models.task import Task
from app.models.note import Note
from app.models.habit import Habit
from app.models.habit_completion import HabitCompletion
from app.routes.auth import auth_bp
from app.routes.main import main_bp
from app.routes.tasks import tasks_bp
from app.routes.notes import notes_bp
from app.routes.habits import habits_bp
from app.routes.chat import chat_bp


def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(notes_bp)
    app.register_blueprint(habits_bp)
    app.register_blueprint(chat_bp)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    with app.app_context():
        db.create_all()

    @app.route("/")
    def home():
        return "LifeHub is running!"

    return app