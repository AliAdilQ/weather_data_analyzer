"""Persistent observations, audit history, and administrator identities."""

from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from . import db


def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(254), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default="admin", nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class WeatherRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(100), nullable=False, index=True)
    country = db.Column(db.String(2), nullable=False)
    temperature = db.Column(db.Float, nullable=False)
    feels_like = db.Column(db.Float, nullable=False)
    temp_min = db.Column(db.Float, nullable=False)
    temp_max = db.Column(db.Float, nullable=False)
    humidity = db.Column(db.Integer, nullable=False)
    pressure = db.Column(db.Integer, nullable=False)
    wind_speed = db.Column(db.Float, nullable=False)
    visibility = db.Column(db.Integer, nullable=False)
    condition = db.Column(db.String(40), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    icon = db.Column(db.String(10), default="")
    recorded_at = db.Column(db.DateTime, default=utcnow, nullable=False, index=True)
    source = db.Column(db.String(10), nullable=False, default="Demo")
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)


class SearchHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(100), nullable=False)
    searched_at = db.Column(db.DateTime, default=utcnow, nullable=False)
    successful = db.Column(db.Boolean, nullable=False)
    source = db.Column(db.String(10), nullable=False)
