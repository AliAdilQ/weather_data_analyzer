import requests
import pytest
from app import db
from app.models import User, WeatherRecord
from app.weather.services import demo_weather, get_weather
from app.seeding import seed_database
from app.analytics.services import analyze


def test_weather_model(app):
    record = WeatherRecord(**demo_weather("London"))
    db.session.add(record)
    db.session.commit()
    assert record.id and record.country == "GB"


def test_password_hash(app):
    user = User.query.filter_by(username="admin").one()
    assert user.password_hash != "Admin123!"
    assert user.check_password("Admin123!")


def test_demo_and_seed_idempotency(app):
    assert 0 <= demo_weather("Tokyo")["humidity"] <= 100
    with pytest.raises(ValueError):
        demo_weather("Not a city")
    count = WeatherRecord.query.count()
    seed_database()
    assert WeatherRecord.query.count() == count == 112
    assert analyze()["stats"]["count"] == 112
    assert len(analyze()["charts"]["temperature"]["labels"]) == 14


def test_api_failure_falls_back(app, monkeypatch):
    app.config.update(WEATHER_API_KEY="test-key", DEMO_MODE=False)

    def failure(*args, **kwargs):
        raise requests.Timeout()

    monkeypatch.setattr(requests, "get", failure)
    assert get_weather("Jakarta")["source"] == "Demo"


def test_live_api_mapping(app, monkeypatch):
    app.config.update(WEATHER_API_KEY="test-key", DEMO_MODE=False)

    class Response:
        def __init__(self, data):
            self.data = data

        def raise_for_status(self):
            pass

        def json(self):
            return self.data

    responses = iter(
        [
            Response([{"name": "London", "country": "GB", "lat": 51.5, "lon": -0.1}]),
            Response(
                {
                    "main": {
                        "temp": 17,
                        "feels_like": 16,
                        "humidity": 65,
                        "pressure": 1012,
                    },
                    "weather": [
                        {"main": "Clouds", "description": "cloudy", "icon": "03d"}
                    ],
                    "wind": {"speed": 2},
                    "dt": 1791200000,
                    "visibility": 10000,
                }
            ),
        ]
    )
    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: next(responses))
    result = get_weather("London")
    assert result["source"] == "API" and result["temp_min"] == 17
