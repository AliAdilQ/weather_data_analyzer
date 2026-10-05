from flask import Blueprint, render_template, request
from ..models import WeatherRecord
from ..analytics.services import analyze
from ..weather.routes import SearchForm
from ..weather.services import CITIES

bp = Blueprint("main", __name__)


def filtered_records():
    query = WeatherRecord.query
    term = request.args.get("q", "").strip()[:100]
    if term:
        query = query.filter(WeatherRecord.city.ilike("%" + term + "%"))
    for field in ("city", "country", "condition", "source"):
        value = request.args.get(field, "")
        if value:
            query = query.filter(getattr(WeatherRecord, field) == value)
    sort = request.args.get("sort", "newest")
    order = {
        "oldest": WeatherRecord.recorded_at.asc(),
        "temperature": WeatherRecord.temperature.desc(),
        "city": WeatherRecord.city.asc(),
    }.get(sort, WeatherRecord.recorded_at.desc())
    return query.order_by(order, WeatherRecord.id.desc()).paginate(
        per_page=20, error_out=False
    )


@bp.get("/")
def home():
    return render_template("home.html", form=SearchForm())


@bp.get("/dashboard")
def dashboard():
    return render_template(
        "dashboard.html", data=analyze(request.args.get("city") or None)
    )


@bp.get("/history")
def history():
    return render_template("history.html", pagination=filtered_records(), admin=False)


@bp.get("/compare")
def compare():
    selected = request.args.getlist("cities") or ["Yogyakarta", "London"]
    selected = list(dict.fromkeys(selected))[:4]
    records = []
    for city in selected:
        row = (
            WeatherRecord.query.filter_by(city=city)
            .order_by(WeatherRecord.recorded_at.desc(), WeatherRecord.id.desc())
            .first()
        )
        if row:
            records.append(row)
    available = sorted(
        set(CITIES)
        | {
            r[0]
            for r in WeatherRecord.query.with_entities(WeatherRecord.city).distinct()
        }
    )
    chart = {
        "labels": [r.city for r in records],
        "values": [r.temperature for r in records],
    }
    return render_template(
        "compare.html",
        records=records,
        selected=selected,
        available=available,
        comparison_data=chart,
    )


@bp.get("/about")
def about():
    return render_template("about.html")
