"""Application factory and shared extensions."""

from pathlib import Path
import click
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect, CSRFError
from sqlalchemy.exc import SQLAlchemyError
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()


def create_app(config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)
    if config:
        app.config.update(config)
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    login_manager.login_view = "auth.login"
    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    from .main.routes import bp as main
    from .weather.routes import bp as weather
    from .auth.routes import bp as auth
    from .admin.routes import bp as admin

    for blueprint in (main, weather, auth, admin):
        app.register_blueprint(blueprint)

    @app.context_processor
    def context():
        from .weather.services import CITIES

        return {
            "demo_mode": app.config["DEMO_MODE"] or not app.config["WEATHER_API_KEY"],
            "demo_cities": list(CITIES),
        }

    @app.errorhandler(404)
    def not_found(error):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    @app.errorhandler(SQLAlchemyError)
    def server_error(error):
        db.session.rollback()
        app.logger.error("Request failed: %s", type(error).__name__)
        return render_template("500.html"), 500

    @app.errorhandler(CSRFError)
    def csrf_error(error):
        return render_template(
            "404.html", message="Your form expired. Refresh the page and try again."
        ), 400

    @app.cli.command("init-db")
    def init_db():
        db.create_all()
        click.echo("Database initialized.")

    @app.cli.command("seed-db")
    def seed_db():
        from .seeding import seed_database

        seed_database()
        click.echo("Demo records and local admin are ready.")

    return app
