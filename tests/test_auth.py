import pytest
from app import db
from app.models import User, WeatherRecord


@pytest.mark.parametrize(
    "path",
    [
        "/admin",
        "/admin/records",
        "/admin/searches",
        "/admin/users",
        "/admin/records/new",
    ],
)
def test_protected_routes(client, path):
    response = client.get(path)
    assert response.status_code == 302 and "/admin/login" in response.location


def test_login_and_logout(client):
    assert (
        client.post(
            "/admin/login", data={"username": "admin", "password": "wrong"}
        ).status_code
        == 200
    )
    assert (
        b"Invalid username or password"
        in client.post(
            "/admin/login", data={"username": "admin", "password": "wrong"}
        ).data
    )
    assert (
        client.post(
            "/admin/login", data={"username": "admin", "password": "Admin123!"}
        ).status_code
        == 302
    )
    assert client.get("/admin").status_code == 200
    assert client.get("/admin/logout").status_code == 405
    assert client.post("/admin/logout").status_code == 302
    assert client.get("/admin").status_code == 302


def test_non_admin_denied(app, client):
    user = User(username="reader", email="reader@local", role="user")
    user.set_password("reader-password")
    db.session.add(user)
    db.session.commit()
    with client.session_transaction() as session:
        session["_user_id"] = str(user.id)
        session["_fresh"] = True
    assert client.get("/admin").status_code == 403


def test_crud_and_validation(app, admin_client):
    data = {
        "city": "Test City",
        "country": "ID",
        "temperature": "0",
        "feels_like": "0",
        "temp_min": "-2",
        "temp_max": "2",
        "humidity": "50",
        "pressure": "1010",
        "wind_speed": "0",
        "visibility": "10000",
        "condition": "Clear",
        "description": "Clear sky",
        "recorded_at": "2026-10-05T12:00",
        "source": "Demo",
    }
    assert admin_client.post("/admin/records/new", data=data).status_code == 302
    record = WeatherRecord.query.filter_by(city="Test City").one()
    data["temperature"] = "1"
    assert (
        admin_client.post(f"/admin/records/{record.id}/edit", data=data).status_code
        == 302
    )
    assert db.session.get(WeatherRecord, record.id).temperature == 1
    data["humidity"] = "101"
    assert admin_client.post("/admin/records/new", data=data).status_code == 200
    record_id = record.id
    assert admin_client.get(f"/admin/records/{record_id}/delete").status_code == 405
    assert admin_client.post(f"/admin/records/{record_id}/delete").status_code == 302
    assert db.session.get(WeatherRecord, record_id) is None
    assert admin_client.post("/admin/searches/1/delete").status_code == 302


def test_csrf_required(app, client):
    app.config["WTF_CSRF_ENABLED"] = True
    assert (
        client.post(
            "/admin/login", data={"username": "admin", "password": "Admin123!"}
        ).status_code
        == 400
    )
    assert client.post("/weather", data={"city": "Tokyo"}).status_code == 400
