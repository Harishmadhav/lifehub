from app.extensions import db
from datetime import datetime


class Habit(db.Model):
    __tablename__ = "habits"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)

    frequency = db.Column(
        db.String(20),
        default="daily",
        nullable=False
    )

    current_streak = db.Column(
        db.Integer,
        default=0,
        nullable=False
    )

    longest_streak = db.Column(
        db.Integer,
        default=0,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    def __repr__(self):
        return f"<Habit {self.name}>"