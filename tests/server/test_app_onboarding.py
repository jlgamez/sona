from src.server.app import FlaskServices, create_flask_app_with
from src.server.config.entity.user_config import UserConfig


class FakeLoader:
    def __init__(self, config):
        self.config = config

    def load_config(self):
        return self.config


class FakeSaver:
    def __init__(self):
        self.saved = None

    def save_user_config(self, config):
        self.saved = config
        return True


class FakeHotKeys:
    def get_default_hot_key(self):
        return type("H", (), {"name": "ctrl_l"})()


class FakeModels:
    def get_default_model_name(self):
        return "base.en"


class FakePermissions:
    def __init__(self):
        self.requested = 0

    def input_monitoring(self):
        return "denied"

    def accessibility(self):
        return "granted"

    def request_input_monitoring(self):
        self.requested += 1


def make_client(config):
    saver = FakeSaver()
    permissions = FakePermissions()
    app = create_flask_app_with(
        FlaskServices(
            FakeModels(), FakeHotKeys(), FakeLoader(config), saver, lambda: [], permissions
        ),
        ["null"],
    )
    return app.test_client(), saver, permissions


def test_post_without_flag_keeps_saved_value():
    client, saver, _ = make_client(
        UserConfig(hot_key="ctrl_l", current_model="base.en", onboarding_completed=True)
    )
    assert client.post("/api/user-config", json={"hot_key": "ctrl_l"}).status_code == 200
    assert saver.saved.onboarding_completed is True


def test_post_sets_flag():
    client, saver, _ = make_client(UserConfig(hot_key="ctrl_l", current_model="base.en"))
    client.post("/api/user-config", json={"onboarding_completed": True})
    assert saver.saved.onboarding_completed is True


def test_post_rejects_non_bool_flag():
    client, _, _ = make_client(UserConfig(hot_key="ctrl_l", current_model="base.en"))
    response = client.post("/api/user-config", json={"onboarding_completed": "yes"})
    assert response.status_code == 400


def test_permissions_route():
    client, _, permissions = make_client(UserConfig(hot_key="ctrl_l", current_model="x"))
    assert client.get("/api/permissions").get_json() == {
        "input_monitoring": "denied",
        "accessibility": "granted",
    }
    client.post("/api/permissions/request-input-monitoring")
    assert permissions.requested == 1
