from flask import Flask

from .data import init_store


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "va-dev-secret-change-me"

    init_store()

    from .routes import bp as main_bp

    app.register_blueprint(main_bp)
    return app
