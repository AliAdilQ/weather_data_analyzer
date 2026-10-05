from flask import Blueprint, render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from .. import db
from ..models import WeatherRecord, SearchHistory, User
from ..analytics.services import analyze
from ..main.routes import filtered_records
from .forms import RecordForm

bp = Blueprint("admin", __name__, url_prefix="/admin")


@bp.before_request
@login_required
def protect_admin():
    if current_user.role != "admin":
        abort(403)


@bp.get("")
@bp.get("/")
def dashboard():
    return render_template("admin/dashboard.html", data=analyze())


@bp.get("/records")
def records():
    return render_template("history.html", pagination=filtered_records(), admin=True)


@bp.route("/records/new", methods=["GET", "POST"])
@bp.route("/records/<int:record_id>/edit", methods=["GET", "POST"])
def edit_record(record_id=None):
    record = db.get_or_404(WeatherRecord, record_id) if record_id else WeatherRecord()
    form = RecordForm(obj=record)
    if form.validate_on_submit():
        form.populate_obj(record)
        db.session.add(record)
        db.session.commit()
        flash("Observation saved.", "success")
        return redirect(url_for("admin.records"))
    return render_template("admin/record_form.html", form=form, record=record)


@bp.post("/records/<int:record_id>/delete")
def delete_record(record_id):
    db.session.delete(db.get_or_404(WeatherRecord, record_id))
    db.session.commit()
    flash("Observation deleted.", "success")
    return redirect(url_for("admin.records"))


@bp.get("/searches")
def searches():
    pagination = SearchHistory.query.order_by(
        SearchHistory.searched_at.desc()
    ).paginate(per_page=20, error_out=False)
    return render_template("admin/search_history.html", pagination=pagination)


@bp.post("/searches/<int:search_id>/delete")
def delete_search(search_id):
    db.session.delete(db.get_or_404(SearchHistory, search_id))
    db.session.commit()
    flash("Search entry deleted.", "success")
    return redirect(url_for("admin.searches"))


@bp.get("/users")
def users():
    return render_template(
        "admin/users.html", users=User.query.filter_by(role="admin").all()
    )
