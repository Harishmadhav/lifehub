from flask import Blueprint, render_template
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length
import bcrypt

from app.extensions import db
from app.models.user import User


auth_bp = Blueprint("auth", __name__)


class RegistrationForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[DataRequired(), Length(min=3, max=80)]
    )

    email = StringField(
        "Email",
        validators=[DataRequired(), Email()]
    )

    password = PasswordField(
        "Password",
        validators=[DataRequired(), Length(min=8)]
    )

    submit = SubmitField("Create Account")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():

        existing_user = User.query.filter(
            (User.username == form.username.data) |
            (User.email == form.email.data)
        ).first()

        if existing_user:
            return "Username or email already exists."

        password_hash = bcrypt.hashpw(
            form.password.data.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

        user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=password_hash
        )

        db.session.add(user)
        db.session.commit()

        return "Registration successful!"

    return render_template(
        "auth/register.html",
        form=form
    )


@auth_bp.route("/login")
def login():
    return "Login page"