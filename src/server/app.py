from flask import Flask, jsonify, request

from .config.serivce.config_loader_service_impl import ConfigLoaderServiceImpl


def create_flask_app() -> Flask:
    app = Flask(__name__)

    config_loader = ConfigLoaderServiceImpl()

    @app.route("/")
    def index():
        return "Hello, World!"

    @app.route("/api/user-config", methods=["GET", "PUT", "POST"])
    def user_config():
        if request.method == "GET":
            return jsonify(config_loader.load_config())
        return None

    return app
