from app.extensions import db
from datetime import date


class HabitCompletion(db.Model):
    __tablename__ = "habit_completions"

    id = db.Column(db.Integer, primary_key=True)

    completed_date = db.Column(
        db.Date,
        default=date.today,
        nullable=False
    )

    habit_id = db.Column(
        db.Integer,
        db.ForeignKey("habits.id"),
        nullable=False
    )

    def __repr__(self):
        return f"<HabitCompletion {self.habit_id} - {self.completed_date}>"