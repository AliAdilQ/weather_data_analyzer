from flask import Blueprint, render_template, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash
from ..models import User
from .forms import LoginForm

bp = Blueprint("auth", __name__, url_prefix="/admin")
_DUMMY_HASH = generate_password_hash("timing-comparison-only")


@bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data.strip()).first()
        valid = check_password_hash(
            user.password_hash if user else _DUMMY_HASH, form.password.data
        )
        if valid and user and user.role == "admin":
            session.clear()
            login_user(user)
            return redirect(url_for("admin.dashboard"))
        flash("Invalid username or password.", "danger")
    return render_template("auth/login.html", form=form)


@bp.post("/logout")
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for("main.home"))
