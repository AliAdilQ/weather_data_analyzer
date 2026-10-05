"""Non-destructive, repeatable portfolio fixtures."""

from datetime import timedelta
from . import db
from .models import User, WeatherRecord, SearchHistory, utcnow
from .weather.services import CITIES, demo_weather


def seed_database():
    db.create_all()
    if not User.query.filter_by(username="admin").first():
        user = User(username="admin", email="admin@weatherdemo.local", role="admin")
        user.set_password("Admin123!")
        db.session.add(user)
    if not WeatherRecord.query.filter_by(source="Demo").first():
        now = utcnow().replace(hour=12, minute=0, second=0, microsecond=0)
        for index, city in enumerate(CITIES):
            for day in range(14):
                when = now - timedelta(days=13 - day)
                db.session.add(WeatherRecord(**demo_weather(city, when)))
            for number in range(4 + index):
                db.session.add(
                    SearchHistory(
                        city=city,
                        successful=True,
                        source="Demo",
                        searched_at=now - timedelta(hours=number),
                    )
                )
        for city in ("Atlantis", "Unknown", "Gotham"):
            db.session.add(SearchHistory(city=city, successful=False, source="Demo"))
    db.session.commit()
