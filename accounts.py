"""Модуль управления аккаунтами."""
from datetime import datetime
from mjson import append, read, write
from singleton import get_data


class AccountManager:
    """Управляет аккаунтами."""
    SUCCESSFUL = 0
    FAILED_NICK_LENGTH = 1
    FAILED_UNKNOWN = 2
    FAILED_PASSWORD_LENGTH = 3
    FAILED_NICK_ALREADY_USED = 4
    FAILED_UNSAFE_CHARACTERS = 5
    FAILED_NOT_FOUND = 6
    FAILED_PASSWORD_NOT_MATCH = 7
    FAILED_BAN = 8
    FAILED_CONSOLE = 9
    FAILED_NOT_EXISTS = 10
    DEFAULT_ALLOWED = "qwertyuiopasdfghjklzxcvbnm1234567890_ -=+*/[]:;.,\\|&%\
#@!$^()йцукенгшщзхъфывапролджэячсмитьбюё"

    @staticmethod
    def check(string, allowed=DEFAULT_ALLOWED):
        """Проверяет состоит ли string только из allowed."""
        return set(string.lower()) <= set(allowed)

    @staticmethod
    def get_account(nick):
        """Возвращает аккаунт с логином nick."""
        data = read("data.json")

        if data is None:
            return AccountManager.FAILED_UNKNOWN

        for account in data["accounts"]:
            if account["nick"] == nick:
                return account

        return AccountManager.FAILED_NOT_FOUND

    @staticmethod
    def del_account_key(nick, key):
        """Удаляет key у аккаунта с логином nick."""
        acc = AccountManager.get_account(nick)

        if acc in (
            AccountManager.FAILED_UNKNOWN,
            AccountManager.FAILED_NOT_FOUND
        ):
            return acc

        data = read("data.json")

        if data is None:
            return AccountManager.FAILED_UNKNOWN

        try:
            del data["accounts"][data["accounts"].index(acc)][key]

            if write("data.json", data):
                return AccountManager.SUCCESSFUL

            return AccountManager.FAILED_UNKNOWN
        except KeyError:
            return AccountManager.FAILED_NOT_EXISTS

    @staticmethod
    def del_account(nick):
        """Удаляет аккаунт с логином nick."""
        acc = AccountManager.get_account(nick)

        if acc in (
            AccountManager.FAILED_UNKNOWN,
            AccountManager.FAILED_NOT_FOUND
        ):
            return acc

        data = read("data.json")
        if data is None:
            return AccountManager.FAILED_UNKNOWN

        del data["accounts"][data["accounts"].index(acc)]

        if write("data.json", data):
            return AccountManager.SUCCESSFUL

        return AccountManager.FAILED_UNKNOWN

    @staticmethod
    def set_account(nick, key, value):
        """Устанавливает значение key в value для аккаунта с логином nick."""
        acc = AccountManager.get_account(nick)

        if acc in (
            AccountManager.FAILED_UNKNOWN,
            AccountManager.FAILED_NOT_FOUND
        ):
            return acc

        data = read("data.json")
        if data is None:
            return AccountManager.FAILED_UNKNOWN

        try:
            data["accounts"][data["accounts"].index(acc)][key] = value
        except (ValueError, IndexError):
            data[key] = [value]

        if write("data.json", data):
            return AccountManager.SUCCESSFUL

        return AccountManager.FAILED_UNKNOWN

    @staticmethod
    def login_account(nick, password):
        """Проверяет верные ли данные для входа."""
        if not isinstance(nick, str):
            return AccountManager.FAILED_UNKNOWN

        if not isinstance(password, str):
            return AccountManager.FAILED_UNKNOWN

        nick = nick.strip()
        password = password.strip()

        if len(nick) < 3 or len(nick) > 12:
            return AccountManager.FAILED_NICK_LENGTH

        if len(password) < 6 or len(password) > 16:
            return AccountManager.FAILED_PASSWORD_LENGTH

        if not AccountManager.check(nick):
            return AccountManager.FAILED_UNSAFE_CHARACTERS

        if not AccountManager.check(password):
            return AccountManager.FAILED_UNSAFE_CHARACTERS

        data = read("data.json")
        if data is None:
            return AccountManager.FAILED_UNKNOWN

        for account in data["accounts"]:
            if account["nick"] == nick:
                if account["password"] == password:
                    if "console" in account:
                        return AccountManager.FAILED_CONSOLE
                    if "ban" in account:
                        aban = account["ban"]

                        if aban[0] != -1 and datetime.today().timestamp() \
                                > aban[0]:
                            del account["ban"]
                            write("data.json", data)
                        else:
                            if len(aban) > 1:
                                return [
                                    AccountManager.FAILED_BAN,
                                    aban[0],
                                    aban[1]
                                ]

                            return [AccountManager.FAILED_BAN, aban[0], None]
                    return AccountManager.SUCCESSFUL
                return AccountManager.FAILED_PASSWORD_NOT_MATCH

        return AccountManager.FAILED_NOT_FOUND

    @staticmethod
    def add_account(nick, password):
        """Создаёт новый аккаунт."""
        if not isinstance(nick, str):
            return AccountManager.FAILED_UNKNOWN

        if not isinstance(password, str):
            return AccountManager.FAILED_UNKNOWN

        nick = nick.strip()
        password = password.strip()

        if len(nick) < 3 or len(nick) > 12:
            return AccountManager.FAILED_NICK_LENGTH

        if len(password) < 6 or len(password) > 16:
            return AccountManager.FAILED_PASSWORD_LENGTH

        if not AccountManager.check(nick):
            return AccountManager.FAILED_UNSAFE_CHARACTERS

        if not AccountManager.check(password):
            return AccountManager.FAILED_UNSAFE_CHARACTERS

        data = read("data.json")

        if data is None:
            return AccountManager.FAILED_UNKNOWN

        for account in data["accounts"]:
            if account["nick"] == nick:
                return AccountManager.FAILED_NICK_ALREADY_USED

        acc = {
            "nick": nick,
            "password": password,
            "xp": 0,
            "crystals": 0,
            "tanks": [1],
            "guns": [0],
            "pts": [],
            "selected_tank": 1,
            "selected_gun": 0,
            "selected_pt": -1,
            "settings": get_data()[0]["default_settings"]
        }

        if append("data.json", "accounts", acc):
            return AccountManager.SUCCESSFUL

        return AccountManager.FAILED_UNKNOWN
