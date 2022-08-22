"""Модуль с тестами к Tanks Battle Server."""
import singleton
import mjson
import accounts
import pytest


@pytest.mark.parametrize("config", [{}, "123", 456, True, False])
@pytest.mark.parametrize("logger", [{}, "123", 456, True, False])
@pytest.mark.parametrize("win", [{}, "123", 456, True, False])
def test_signleton_setget_data(config, logger, win):
    """Тестирует установку и получения различных типов данных."""
    assert singleton.set_data(config, logger, win) is None
    assert singleton.get_data() == [config, logger, win]


def test_signleton_matches():
    """Тесты матчей синглтона."""
    config = mjson.read("config.json")
    singleton.set_data(config)

    assert singleton.get_matches() == []
    battle = singleton.add_match("Test name", 10, "Test creator")
    assert battle.pop("map", False) is not False
    exp_battle = {
        "name": "Test name",
        "max_players": 10,
        "creator": "Test creator",
        "players": [],
        "messages": []
    }
    assert battle == exp_battle
    assert singleton.get_matches() == [exp_battle]
    assert singleton.remove_match(exp_battle["name"])
    assert singleton.get_matches() == []


def test_accounts():
    """Тесты модуля аккаунтов."""
    amanager = accounts.AccountManager
    assert amanager.check("Allowed name")
    assert not amanager.check("<name>")
    assert amanager.check("")
    assert amanager.check("Никнейм")
