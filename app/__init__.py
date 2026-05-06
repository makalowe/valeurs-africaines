import os
from flask import Flask
from flask_caching import Cache

from .data import init_store

cache = Cache(config={"CACHE_TYPE": "simple"})

def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "change-me-in-production")
    app.config["ENV"] = os.getenv("FLASK_ENV", "production")
    
    cache.init_app(app)
    init_store()

    from .routes import bp as main_bp

    app.register_blueprint(main_bp)
    return app
