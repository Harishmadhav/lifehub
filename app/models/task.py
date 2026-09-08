from app.extensions import db
from datetime import datetime


class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)

    priority = db.Column(db.String(20), default="medium", nullable=False)
    status = db.Column(db.String(20), default="pending", nullable=False)

    due_date = db.Column(db.DateTime, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    completed_at = db.Column(db.DateTime, nullable=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    def __repr__(self):
        return f"<Task {self.title}>"