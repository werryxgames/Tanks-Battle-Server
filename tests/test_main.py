"""Module with tests for Tanks Battle Server."""
import pytest
import mjson
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
    """Tests signleton's set_data() and get_data() with diferent data types."""
    assert singleton.set_data(config, logger, win) is None
    assert singleton.get_data() == [config, logger, win]


def test_signleton_matches():
    """Tests matches in singleton."""
    config = mjson.read("../config.json")
    singleton.set_data(config)

    assert not singleton.get_matches()
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
    """Tests clients of signleton."""
    assert not singleton.get_clients()
    singleton.st.clients[("127.0.0.1", 10000)] = None
    assert singleton.get_clients() == {("127.0.0.1", 10000): None}


@pytest.mark.parametrize("nick, result", (
    ("Allowed name", True),
    ("<name>", False),
    ("", True),
    ("Никнейм", True)
))
def test_accounts_check(nick, result):
    """Tests for AccountManager.check()."""
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
    """Tests for AccountManager.get_account_()."""
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
    """Tests for AccountManager.del_account_key_()."""
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
    """Tests for AccountManager.set_account_()."""
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
    """Tests for AccountManager.check_login_data()."""
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
        AccountManager.SUCCESSFUL
    ),
    (
        [{"ban": [0, "Тест"]}],
        {"ban": [0, "Тест"]},
        AccountManager.SUCCESSFUL
    ),
    (
        [{"ban": [-1, "Test"]}],
        {"ban": [-1, "Test"]},
        [
            AccountManager.FAILED_BAN,
            ByteBuffer(11).put_u16(8).put_32(-1).put_string("Test").to_bytes()
        ]
    ),
    (
        [{"ban": [-1]}],
        {"ban": [-1]},
        [
            AccountManager.FAILED_BAN,
            ByteBuffer(6).put_u16(8).put_32(-1).to_bytes()
        ]
    )
))
def test_accounts_get_ban_status(data, account, result):
    """Tests for AccountManager.get_ban_status()."""
    assert AccountManager.get_ban_status_(data, account) == result


@pytest.mark.parametrize("type_, text", (
    ("respawn", ["respawned"]),
    ("respawn", {"position": (1, 2, 3)}),
    ("test", "Test GlobalMessage"),
    ("тест", "Тест GlobalMessage")
))
def test_global_message(type_, text):
    """Tests for GlobalMessage."""
    assert GlobalMessage(type_, text).get() == (type_, text)


@pytest.mark.parametrize("data, result", (
    (6, bytearray((6,))),
    (-124, ByteBufferOutOfRange),
    (290, ByteBufferOutOfRange),
    (-5432, ByteBufferOutOfRange),
    (250, bytearray((250,)))
))
def test_put_u8(data, result):
    """Tests for ByteBuffer.put_u8()."""
    try:
        assert ByteBuffer(1).put_u8(data).rewind().to_bytes() == result
    except ByteBufferException as exc:
        assert isinstance(exc, result)


def test_put_u8_overflow():
    """Test for ByteBuffer.put_u8() with overflow."""
    try:
        ByteBuffer(1).put_u8(0).put_u8(8)
    except ByteBufferException:
        assert True
    else:
        assert False

    try:
        ByteBuffer(2).put_u8(0).put_u8(8)
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
    ("VERY LONG STRING VERY LONG STRING VERY LONG STRING VERY LONG STRING \
VERY LONG STRING VERY LONG STRING\nVERY LONG STRING VERY LONG STRING VERY \
LONG STRING VERY LONГ STRING VERY LONG STRING VERY LONG STRING VERY \nVERY \
LONG STRING VERY LONG STRING VERY LONG STRING VERY LONG STRING VERY LONG \
STRING VERY LONG\tSTRING VERY \nVERY LONG STRING VERY LONG STRING VERY LONG \
STRING VERY LONG STRING VERY LONG STRING VERY LONG STRING VERY \nVERY LONG \
STRING VERY LONG STRING VERY LONG STRING VERY LONG STRING VERY LONG STRING \
VERY LONG STRING VERY \r\n")
))
def test_put_get_string(data):
    """Tests for ByteBuffer.put_string() and ByteBuffer.get_string()."""
    assert ByteBuffer(bytearray(len(
        data.encode("utf8")
    ) + 1)).put_string(data).rewind().get_string() == data
