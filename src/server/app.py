from flask import Flask


def create_flask_app() -> Flask:
    app = Flask(__name__)

    @app.route("/")
    def index():
        return "Hello, World!"

    return app
