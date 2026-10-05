from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length
from .. import db
from ..models import WeatherRecord, SearchHistory
from .services import get_weather

bp = Blueprint("weather", __name__)


class SearchForm(FlaskForm):
    city = StringField("City", validators=[DataRequired(), Length(max=100)])
    submit = SubmitField("Explore weather")


@bp.route("/weather", methods=["GET", "POST"])
def search():
    form = SearchForm()
    if form.validate_on_submit():
        city = form.city.data.strip()
        try:
            data = get_weather(city)
        except ValueError as error:
            db.session.add(SearchHistory(city=city, successful=False, source="Demo"))
            db.session.commit()
            flash(str(error), "warning")
        else:
            record = WeatherRecord(**data)
            db.session.add(record)
            db.session.add(
                SearchHistory(city=city, successful=True, source=data["source"])
            )
            db.session.commit()
            return redirect(url_for("weather.result", record_id=record.id))
    elif request.method == "POST":
        flash("Enter a city name between 1 and 100 characters.", "warning")
    return render_template("home.html", form=form)


@bp.get("/weather/<int:record_id>")
def result(record_id):
    record = db.get_or_404(WeatherRecord, record_id)
    recent = (
        WeatherRecord.query.filter_by(city=record.city)
        .order_by(WeatherRecord.recorded_at.desc())
        .limit(7)
        .all()
    )
    return render_template("weather.html", record=record, recent=recent)
