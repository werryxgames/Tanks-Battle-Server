"""Модуль с тестами к Tanks Battle Server."""
from os import path as path_
from sys import path

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

import mjson
import pytest
import singleton

from accounts import AccountManager
from message import GlobalMessage
from reliable_udp import ByteTranslator, ByteTranslatorException


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


@pytest.mark.parametrize("data, account, result", (
    (
        [{}],
        {},
        AccountManager.SUCCESSFUL
    ),
    (
        [{"ban": [0]}],
        {"ban": [0]},
        [{}]
    ),
    (
        [{"ban": [0, "Тест"]}],
        {"ban": [0, "Тест"]},
        [{}]
    ),
    (
        [{"ban": [-1, "Test"]}],
        {"ban": [-1, "Test"]},
        [AccountManager.FAILED_BAN, -1, "Test"]
    ),
    (
        [{"ban": [-1]}],
        {"ban": [-1]},
        [AccountManager.FAILED_BAN, -1, None]
    )
))
def test_accounts_get_ban_status(data, account, result):
    """Тесты AccountManager.get_ban_status()."""
    assert AccountManager.get_ban_status_(data, account) == result


@pytest.mark.parametrize("type_, text", (
    ("respawn", ["respawned"]),
    ("respawn", {"position": (1, 2, 3)}),
    ("test", "Test GlobalMessage"),
    ("тест", "Тест GlobalMessage")
))
def test_global_message(type_, text):
    """Тесты GlobalMessage."""
    assert GlobalMessage(type_, text).get() == (type_, text)


@pytest.mark.parametrize("com, result", (
    ("something_wrong", bytearray((0, 1))),
    ("register", bytearray((0, 2))),
    ("login", bytearray((0, 3))),
    ("get_account_data", bytearray((0, 4))),
    ("client_disconnected", bytearray((0, 5))),
    ("console_command", bytearray((0, 6))),
    ("", ByteTranslatorException),
    ("Тест", ByteTranslatorException)
))
def test_get_com_bytes(com, result):
    """Тесты ByteTranslator.get_com_bytes()."""
    try:
        assert ByteTranslator.get_com_bytes(com) == result
    except ByteTranslatorException:
        assert result == ByteTranslatorException


@pytest.mark.parametrize("data, result", (
    (0, 1),
    ("", 2),
    (0.0, 3),
    ([], 4),
    ((), 4),
    ({}, 5),
    (None, 6),
    (False, 7),
    (True, 7),
    (print, ByteTranslatorException)
))
def test_get_datatype(data, result):
    """Тесты ByteTranslator.get_datatype()."""
    try:
        assert ByteTranslator.get_datatype(data) == result
    except ByteTranslatorException:
        assert result == ByteTranslatorException


@pytest.mark.parametrize("data, result", (
    (0, bytearray((1, 0, 0))),
    (999, bytearray((1, 1, 3, 231))),
    (-999, bytearray((1, 1, 252, 25))),
    ("", bytearray((2, 0))),
    ("Qwerty", bytearray((2, 81, 119, 101, 114, 116, 121, 0))),
    ("Йцукен", bytearray((
        2,
        208,
        153,
        209,
        134,
        209,
        131,
        208,
        186,
        208,
        181,
        208,
        189,
        0
    ))),
    (0.0, bytearray((3, 0, 0, 0, 0))),
    (4.8, bytearray((3, 154, 153, 153, 64))),
    (-3.2489, bytearray((3, 250, 237, 79, 192))),
    ([1, 2], bytearray((4, 2, 1, 0, 1, 1, 0, 2))),
    (("", 543), bytearray((4, 2, 2, 0, 1, 1, 2, 31))),
    ([5.7, 31, "Тест"], bytearray((
        4,
        3,
        3,
        102,
        102,
        182,
        64,
        1,
        0,
        31,
        2,
        208,
        162,
        208,
        181,
        209,
        129,
        209,
        130,
        0
    ))),
    ({"1est": 1}, bytearray((
        5,
        1,
        4,
        2,
        2,
        49,
        101,
        115,
        116,
        0,
        1,
        0,
        1
    ))),
    ({"t2st": 432, 10: 20}, bytearray((
        5,
        2,
        4,
        2,
        2,
        116,
        50,
        115,
        116,
        0,
        1,
        1,
        1,
        176,
        4,
        2,
        1,
        0,
        10,
        1,
        0,
        20
    ))),
    ({"te3t": [1, 2]}, bytearray((
        5,
        1,
        4,
        2,
        2,
        116,
        101,
        51,
        116,
        0,
        4,
        2,
        1,
        0,
        1,
        1,
        0,
        2
    ))),
    ({"tes4": [1, 2], 10: 20}, bytearray((
        5,
        2,
        4,
        2,
        2,
        116,
        101,
        115,
        52,
        0,
        4,
        2,
        1,
        0,
        1,
        1,
        0,
        2,
        4,
        2,
        1,
        0,
        10,
        1,
        0,
        20
    ))),
    (None, bytearray([6])),
    (True, bytearray([7, 1])),
    (False, bytearray([7, 0]))
))
def test_to_bytes(data, result):
    """Тесты ByteTranslator.to_bytes()."""
    try:
        assert ByteTranslator.to_bytes([data]) == result
    except ByteTranslatorException:
        assert result == ByteTranslatorException
