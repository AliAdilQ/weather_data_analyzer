import pytest
from app import create_app, db
from app.seeding import seed_database


@pytest.fixture
def app():
    application = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite://",
            "SECRET_KEY": "test-only-key",
            "WTF_CSRF_ENABLED": False,
            "WEATHER_API_KEY": "",
            "DEMO_MODE": True,
        }
    )
    with application.app_context():
        seed_database()
        yield application
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def admin_client(client):
    client.post("/admin/login", data={"username": "admin", "password": "Admin123!"})
    return client
