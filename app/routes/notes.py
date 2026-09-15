from flask import Blueprint, render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired

from app.extensions import db
from app.models.note import Note

notes_bp = Blueprint("notes", __name__)


class NoteForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    content = TextAreaField("Content", validators=[DataRequired()])
    submit = SubmitField("Save Note")


@notes_bp.route("/notes/create", methods=["GET", "POST"])
@login_required
def create_note():
    form = NoteForm()

    if form.validate_on_submit():
        note = Note(
            title=form.title.data,
            content=form.content.data,
            user_id=current_user.id
        )
        db.session.add(note)
        db.session.commit()

        flash("Note created successfully.", "success")
        return redirect(url_for("notes.view_notes"))

    return render_template("notes/create_note.html", form=form)


@notes_bp.route("/notes")
@login_required
def view_notes():
    notes = Note.query.filter_by(user_id=current_user.id).order_by(Note.updated_at.desc()).all()
    return render_template("notes/view_notes.html", notes=notes)


@notes_bp.route("/notes/<int:note_id>/edit", methods=["GET", "POST"])
@login_required
def edit_note(note_id):
    note = Note.query.get_or_404(note_id)

    if note.user_id != current_user.id:
        abort(403)

    form = NoteForm(obj=note)

    if form.validate_on_submit():
        note.title = form.title.data
        note.content = form.content.data
        db.session.commit()

        flash("Note updated successfully.", "success")
        return redirect(url_for("notes.view_notes"))

    return render_template("notes/edit_note.html", form=form, note=note)


@notes_bp.route("/notes/<int:note_id>/delete", methods=["POST"])
@login_required
def delete_note(note_id):
    note = Note.query.get_or_404(note_id)

    if note.user_id != current_user.id:
        abort(403)

    db.session.delete(note)
    db.session.commit()

    flash("Note deleted.", "info")
    return redirect(url_for("notes.view_notes"))