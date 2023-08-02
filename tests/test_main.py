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
from serializer import ByteBuffer
from serializer import ByteBufferException
from serializer import ByteBufferOutOfRange


@pytest.mark.parametrize("config", [{}, "123", 456, True, False])
@pytest.mark.parametrize("logger", [{}, "123", 456, True, False])
@pytest.mark.parametrize("win", [{}, "123", 456, True, False])
def test_signleton_setget_data(config, logger, win):
    """Тестирует установку и получения различных типов данных."""
    assert singleton.set_data(config, logger, win) is None
    assert singleton.get_data() == [config, logger, win]


def test_signleton_matches():
    """Тесты матчей синглтона."""
    config = mjson.read("../config.json")
    singleton.set_data(config)

    assert singleton.get_matches() == []
    battle = singleton.add_match(0, 10)
    exp_battle = {
        "max_players": 10,
        "players": [],
        "map": 0,
        "messages": []
    }
    assert battle == exp_battle
    assert singleton.get_matches() == [exp_battle]
    assert singleton.remove_match(0)
    assert singleton.get_matches() == [None]


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


@pytest.mark.parametrize("data, result", (
    (6, bytearray((6))),
    (-124, ByteBufferOutOfRange),
    (290, ByteBufferOutOfRange),
    (-5432, ByteBufferOutOfRange),
    (250, bytearray((250)))
))
def test_put_u8(data, result):
    """Tests for ByteBuffer.put_u8()."""
    try:
        buffer = ByteBuffer(1).put_u8(data).rewind().to_bytes() == result
    except ByteBufferException as exc:
        assert isinstance(exc, result)


def test_put_u8_overflow():
    """Test for ByteBuffer.put_u8() with overflow."""
    try:
        buffer = ByteBuffer(1).put_u8(0).put_u8(8)
    except ByteBufferException:
        assert True
    else:
        assert False

    try:
        buffer = ByteBuffer(2).put_u8(0).put_u8(8)
    except ByteBufferException:
        assert False
    else:
        assert True


@pytest.mark.parametrize("data", (
    (6),
    (-124),
    (290),
    (-5432),
    (250)
))
def test_put_get_16(data):
    """Tests for ByteBuffer.put_16() and ByteBuffer.get_16()."""
    assert ByteBuffer(2).put_16(data).rewind().get_16() == data


@pytest.mark.parametrize("data", (
    ("a"),
    (""),
    ("Hello, World!"),
    ("Прывітанне, свет!"),
    ("Вы ўпэўнены?!..."),
    (" "),
    ("VERY LONG STRING VERY LONG STRING VERY LONG STRING VERY LONG STRING VERY LONG STRING VERY LONG STRING\n\
VERY LONG STRING VERY LONG STRING VERY LONG STRING VERY LONГ STRING VERY LONG STRING VERY LONG STRING VERY \n\
VERY LONG STRING VERY LONG STRING VERY LONG STRING VERY LONG STRING VERY LONG STRING VERY LONG\tSTRING VERY \n\
VERY LONG STRING VERY LONG STRING VERY LONG STRING VERY LONG STRING VERY LONG STRING VERY LONG STRING VERY \n\
VERY LONG STRING VERY LONG STRING VERY LONG STRING VERY LONG STRING VERY LONG STRING VERY LONG STRING VERY \r\n")
))
def test_put_get_string(data):
    """Tests for ByteBuffer.put_string() and ByteBuffer.get_string()."""
    assert ByteBuffer(bytearray(len(data.encode("utf8")) + 1)).put_string(data).rewind().get_string() == data
