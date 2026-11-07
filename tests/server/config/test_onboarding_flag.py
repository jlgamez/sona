from src.server.config.serivce.ConfigLoadServiceImpl import ConfigLoadServiceImpl


class FakeRepository:
    def __init__(self, data):
        self._data = data

    def read_user_config(self):
        return self._data

    def write_user_config(self, data):
        return True


DEFAULTS = {"hot_key": "ctrl_l", "model": "base.en"}


def load(data):
    return ConfigLoadServiceImpl(FakeRepository(data), DEFAULTS).load_config()


def test_fresh_install_is_not_onboarded():
    assert load(None).onboarding_completed is False


def test_existing_config_without_flag_counts_as_onboarded():
    assert load({"hot_key": "ctrl_l", "current_model": "base.en"}).onboarding_completed


def test_saved_false_flag_is_kept():
    assert load({"onboarding_completed": False}).onboarding_completed is False
