import pytest
from app.models import WeatherRecord, SearchHistory


@pytest.mark.parametrize(
    "path", ["/", "/dashboard", "/history", "/compare", "/about", "/admin/login"]
)
def test_public_pages(client, path):
    assert client.get(path).status_code == 200


def test_404(client):
    assert client.get("/missing").status_code == 404


def test_weather_search_stores_observation(app, client):
    before = WeatherRecord.query.count()
    response = client.post(
        "/weather", data={"city": " jakarta "}, follow_redirects=True
    )
    assert response.status_code == 200
    assert b"Jakarta" in response.data and b"Demo Data" in response.data
    assert WeatherRecord.query.count() == before + 1
    assert SearchHistory.query.order_by(SearchHistory.id.desc()).first().successful


def test_invalid_city_and_empty_input(client):
    assert (
        b"City unavailable" in client.post("/weather", data={"city": "Atlantis"}).data
    )
    assert b"Enter a city name" in client.post("/weather", data={"city": " "}).data


def test_history_filters_and_pagination(client):
    response = client.get("/history?city=London&sort=temperature")
    assert b"London" in response.data and b"Jakarta</a>" not in response.data
    assert client.get("/history?page=2").status_code == 200


def test_compare_and_empty_data(client, app):
    assert (
        b"Temperature comparison"
        in client.get("/compare?cities=Jakarta&cities=Tokyo").data
    )
    from app import db

    WeatherRecord.query.delete()
    db.session.commit()
    assert b"Your insights start here" in client.get("/dashboard").data
    assert client.get("/compare").status_code == 200
