"""Idempotently initialize local demonstration data."""

from app import create_app
from app.seeding import seed_database

if __name__ == "__main__":
    with create_app().app_context():
        seed_database()
    print("Demo database ready. Local admin: admin / Admin123!")
