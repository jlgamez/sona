from flask import Flask, jsonify, request, Response
import json

from .config.repository.config_repository import ConfigRepositoryImpl
from .config.serivce.config_loader_service_impl import ConfigLoaderServiceImpl
from .config.serivce.config_saver_service_impl import ConfigSaverServiceImpl
from .config.entity.user_config import UserConfig, ClipboardBehaviour
from .models.repository.model_repository import ModelRepositoryImpl
from .models.service.local_model_service import LocalModelServiceImpl
from .hot_key.repository.hot_key_repository import HotKeyRepositoryImpl
from .hot_key.service.hot_key_service import HotKeyServiceImpl


def create_flask_app() -> Flask:
    app = Flask(__name__)

    config_repository = ConfigRepositoryImpl()
    config_loader = ConfigLoaderServiceImpl(config_repository)
    config_saver = ConfigSaverServiceImpl(config_repository)
    model_service = LocalModelServiceImpl(ModelRepositoryImpl())
    hot_key_service = HotKeyServiceImpl(HotKeyRepositoryImpl())

    @app.route("/")
    def index():
        return "Hello, World!"

    @app.route("/api/user-config", methods=["GET", "PUT", "POST"])
    def user_config():
        if request.method == "GET":
            return jsonify(config_loader.load_config())
        elif request.method == "POST":
            try:
                data = request.get_json(force=True)
                config = parse_submitted_config(data)
                if config is None:
                    return (
                        jsonify({"success": False, "error": "Malformed request"}),
                        400,
                    )
                success = config_saver.save_user_config(config)
                if success:
                    return jsonify({"success": True}), 200
                else:
                    return (
                        jsonify({"success": False, "error": "Failed to save config"}),
                        500,
                    )
            except Exception as e:
                return jsonify({"success": False, "error": str(e)}), 400

        return None

    @app.route("/api/available-models", methods=["GET"])
    def get_available_models():
        models = model_service.get_available_models()
        # Convert dataclass objects to dicts for JSON serialization
        data = [model.__dict__ for model in models]
        return Response(
            json.dumps(data, ensure_ascii=False),
            content_type="application/json; charset=utf-8",
        )

    @app.route("/api/hot-keys", methods=["GET"])
    def get_available_hot_keys():
        hot_keys = hot_key_service.list_hot_keys()
        # Convert dataclass objects to dicts for JSON serialization
        data = [hot_key.__dict__ for hot_key in hot_keys]
        return Response(
            json.dumps(data, ensure_ascii=False),
            content_type="application/json; charset=utf-8",
        )

    def parse_submitted_config(data: dict) -> UserConfig | None:
        """
        Try to construct a UserConfig from a raw dict.
        Performs strict type checks and returns None if malformed.
        """
        try:
            if not isinstance(data, dict):
                return None
            hot_key = data.get("hot_key", hot_key_service.get_default_hot_key().name)
            if not isinstance(hot_key, str) or not hot_key.strip():
                return None

            # Optional booleans
            intelligent_mode = data.get("intelligent_mode", False)
            text_selection_awareness = data.get("text_selection_awareness", False)
            if not isinstance(intelligent_mode, bool):
                return None
            if not isinstance(text_selection_awareness, bool):
                return None

            # Nested clipboard_behaviour
            clipboard_behaviour = data.get("clipboard_behaviour", {})
            clipboard_behaviour = (
                {} if clipboard_behaviour is None else clipboard_behaviour
            )
            if not isinstance(clipboard_behaviour, dict):
                return None
            autonomous_pasting = clipboard_behaviour.get("autonomous_pasting", True)
            keep_output_in_clipboard = clipboard_behaviour.get(
                "keep_output_in_clipboard", True
            )
            if not isinstance(autonomous_pasting, bool):
                return None
            if not isinstance(keep_output_in_clipboard, bool):
                return None
            clipboard_behaviour = ClipboardBehaviour(
                autonomous_pasting=autonomous_pasting,
                keep_output_in_clipboard=keep_output_in_clipboard,
            )
            # current_model
            current_model = data.get(
                "current_model", model_service.get_default_model_name()
            )
            if not isinstance(current_model, str):
                return None
            return UserConfig(
                hot_key=hot_key,
                intelligent_mode=intelligent_mode,
                text_selection_awareness=text_selection_awareness,
                clipboard_behaviour=clipboard_behaviour,
                current_model=current_model,
            )
        except Exception:
            return None

    return app
