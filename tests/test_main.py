"""Модуль с тестами к Tanks Battle Server."""
from sys import path
from os import path as path_

try:
    path.append(
        path_.normpath(
            path_.join(
                path_.dirname(
                    path_.realpath(
                        __file__
                    )
                ),
                "..",
                "src"
            )
        )
    )
except IndexError:
    pass

import singleton
import mjson
from accounts import AccountManager
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


def test_signleton_clients():
    """Тесты клиентов синглтона."""
    assert singleton.get_clients() == {}
    singleton.st.clients[("127.0.0.1", 10000)] = None
    assert singleton.get_clients() == {("127.0.0.1", 10000): None}


@pytest.mark.parametrize("nick, result", (
    ("Allowed name", True),
    ("<name>", False),
    ("", True),
    ("Никнейм", True)
))
def test_accounts_check(nick, result):
    """Тесты AccountManager.check()."""
    assert AccountManager.check(nick) is result


@pytest.mark.parametrize("nick, data, result", (
    (
        None,
        None,
        AccountManager.FAILED_UNKNOWN
    ),
    (
        None,
        {"accounts": []},
        AccountManager.FAILED_NOT_FOUND
    ),
    (
        "test",
        {"accounts": [{"nick": "test"}]},
        {"nick": "test"}
    ),
    (
        "test",
        {"accounts": [{"nick": "test2"}]},
        AccountManager.FAILED_NOT_FOUND
    ),
    (
        "Тест",
        {"accounts": [{"nick": "Тест"}, {"nick": "test2"}]},
        {"nick": "Тест"}
    ),
    (
        "test",
        {"accounts": [{"nick": "test2"}, {"nick": "test"}]},
        {"nick": "test"}
    ),
    (
        "test2",
        {"accounts": [{"nick": "test"}]},
        AccountManager.FAILED_NOT_FOUND
    ),
    (
        "test2",
        {"accounts": [{"nick": "test"}, {"nick": "Тест"}]},
        AccountManager.FAILED_NOT_FOUND
    )
))
def test_accounts_get_account(nick, data, result):
    """Тесты AccountManager.get_account_()."""
    assert AccountManager.get_account_(nick, data) == result


@pytest.mark.parametrize("nick, key, data, result", (
    (
        "test",
        "nick",
        {"accounts": []},
        AccountManager.FAILED_NOT_FOUND
    ),
    (
        "test",
        "nick",
        None,
        AccountManager.FAILED_UNKNOWN,
    ),
    (
        "test",
        "test_field",
        {"accounts": [{"nick": "test"}]},
        AccountManager.FAILED_NOT_EXISTS,
    ),
    (
        "test",
        "nick",
        {"accounts": [{"nick": "test"}]},
        {"accounts": [{}]},
    ),
    (
        "test",
        "ban",
        {"accounts": [{
            "nick": "test",
            "ban": []
        }]},
        {"accounts": [{"nick": "test"}]},
    )
))
def test_accounts_del_account_key(nick, key, data, result):
    """Тесты AccountManager.del_account_key_()."""
    assert AccountManager.del_account_key_(nick, key, data) == result


@pytest.mark.parametrize("nick, key, value, data, result", (
    (
        "The World",
        "nick",
        "ZA WARUDO",
        {"accounts": [{"nick": "The World"}]},
        {"accounts": [{"nick": "ZA WARUDO"}]}
    ),
    (
        "test",
        "test_key",
        "test_value",
        None,
        AccountManager.FAILED_UNKNOWN
    ),
    (
        "test",
        "test_key",
        "",
        {"accounts": [{"nick": ""}]},
        AccountManager.FAILED_NOT_FOUND
    ),
    (
        "Test",
        "selected_pt",
        -1,
        {"accounts": [{"nick": "Test", "selected_pt": 0}]},
        {"accounts": [{"nick": "Test", "selected_pt": -1}]}
    )
))
def test_accounts_set_account(nick, key, value, data, result):
    """Тесты AccountManager.set_account()."""
    assert AccountManager.set_account_(nick, key, value, data) == result
