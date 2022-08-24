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
        [],
        AccountManager.FAILED_NOT_FOUND
    ),
    (
        "test",
        [{"nick": "test"}],
        {"nick": "test"}
    ),
    (
        "test",
        [{"nick": "test2"}],
        AccountManager.FAILED_NOT_FOUND
    ),
    (
        "Тест",
        [{"nick": "Тест"}, {"nick": "test2"}],
        {"nick": "Тест"}
    ),
    (
        "test",
        [{"nick": "test2"}, {"nick": "test"}],
        {"nick": "test"}
    ),
    (
        "test2",
        [{"nick": "test"}],
        AccountManager.FAILED_NOT_FOUND
    ),
    (
        "test2",
        [{"nick": "test"}, {"nick": "Тест"}],
        AccountManager.FAILED_NOT_FOUND
    )
))
def test_accounts_get_account(nick, data, result):
    """Тесты AccountManager.get_account_()."""
    print(nick, data, result)
    assert AccountManager.get_account_(nick, data) == result


@pytest.mark.parametrize("nick, key, data, result", (
    (
        "test",
        "nick",
        [],
        AccountManager.FAILED_NOT_FOUND
    ),
    (
        "test",
        "test_field",
        [{"nick": "test"}],
        AccountManager.FAILED_NOT_EXISTS,
    ),
    (
        "test",
        "nick",
        [{"nick": "test"}],
        [{}],
    ),
    (
        "test",
        "ban",
        [{
            "nick": "test",
            "ban": []
        }],
        [{"nick": "test"}],
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
        [{"nick": "The World"}],
        [{"nick": "ZA WARUDO"}]
    ),
    (
        "test",
        "test_key",
        "test_value",
        [],
        AccountManager.FAILED_NOT_FOUND
    ),
    (
        "test",
        "test_key",
        "",
        [{"nick": ""}],
        AccountManager.FAILED_NOT_FOUND
    ),
    (
        "Test",
        "selected_pt",
        -1,
        [{"nick": "Test", "selected_pt": 0}],
        [{"nick": "Test", "selected_pt": -1}]
    )
))
def test_accounts_set_account(nick, key, value, data, result):
    """Тесты AccountManager.set_account()."""
    assert AccountManager.set_account_(nick, key, value, data) == result


@pytest.mark.parametrize("data, lenfail, result", (
    (
        "test",
        AccountManager.FAILED_NICK_LENGTH,
        AccountManager.SUCCESSFUL
    ),
    (
        "<incorrect>",
        AccountManager.FAILED_NICK_LENGTH,
        AccountManager.FAILED_UNSAFE_CHARACTERS
    ),
    (
        -1,
        AccountManager.FAILED_NICK_LENGTH,
        AccountManager.FAILED_UNKNOWN
    ),
    (
        "",
        AccountManager.FAILED_NICK_LENGTH,
        AccountManager.FAILED_NICK_LENGTH
    ),
    (
        "12345678901234567890",
        AccountManager.FAILED_PASSWORD_LENGTH,
        AccountManager.FAILED_PASSWORD_LENGTH
    )
))
def test_accounts_check_login_data(data, lenfail, result):
    """Тесты AccountManager.check_login_data()."""
    assert AccountManager.check_login_data(data, lenfail) == result
