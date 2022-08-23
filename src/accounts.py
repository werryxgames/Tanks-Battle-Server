"""Модуль управления аккаунтами."""
from datetime import datetime
from mjson import append
from mjson import read
from mjson import write
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
    def get_account_(nick, data):
        """Возвращает аккаунт с логином nick из data."""
        if data is None:
            return AccountManager.FAILED_UNKNOWN

        for account in data["accounts"]:
            if account["nick"] == nick:
                return account

        return AccountManager.FAILED_NOT_FOUND

    @staticmethod
    def get_account(nick):
        """Возвращает аккаунт с логином nick."""
        data = read("data.json")

        return AccountManager.get_account_(nick, data)

    @staticmethod
    def del_account_key_(nick, key, data):
        """Удаляет key у аккаунта с логином nick из data."""
        acc = AccountManager.get_account_(nick, data)

        if acc in (
            AccountManager.FAILED_UNKNOWN,
            AccountManager.FAILED_NOT_FOUND
        ):
            return acc

        try:
            del data["accounts"][data["accounts"].index(acc)][key]

            return data
        except KeyError:
            return AccountManager.FAILED_NOT_EXISTS

    @staticmethod
    def call_method(method, *args):
        """Вызывает method."""
        data = read("data.json")
        result = method(*args, data)

        if isinstance(result, int):
            return result

        if write("data.json", result):
            return AccountManager.SUCCESSFUL

        return AccountManager.FAILED_UNKNOWN

    @staticmethod
    def del_account_key(nick, key):
        """Удаляет key у аккаунта с логином nick."""
        return AccountManager.call_method(
            AccountManager.del_account_key_,
            nick,
            key
        )

    @staticmethod
    def del_account_(nick, data):
        """Удаляет аккаунт с логином nick из data."""
        acc = AccountManager.get_account_(nick, data)

        if acc in (
            AccountManager.FAILED_UNKNOWN,
            AccountManager.FAILED_NOT_FOUND
        ):
            return acc

        del data["accounts"][data["accounts"].index(acc)]

        if write("data.json", data):
            return AccountManager.SUCCESSFUL

        return AccountManager.FAILED_UNKNOWN

    @staticmethod
    def del_account(nick):
        """Удаляет аккаунт с логином nick."""
        return AccountManager.call_method(
            AccountManager.del_account_,
            nick
        )

    @staticmethod
    def set_account_(nick, key, value, data):
        """Устанавливает значение key в value для аккаунта с логином nick."""
        acc = AccountManager.get_account_(nick, data)

        if acc in (
            AccountManager.FAILED_UNKNOWN,
            AccountManager.FAILED_NOT_FOUND
        ):
            return acc

        try:
            accounts = data["accounts"]
            accounts[accounts.index(acc)][key] = value
        except (ValueError, IndexError):
            data[key] = [value]

        return data

    @staticmethod
    def set_account(nick, key, value):
        """Устанавливает значение для аккаунта."""
        return AccountManager.call_method(
            AccountManager.set_account_,
            nick,
            key,
            value
        )

    @staticmethod
    def check_login_data(data, lenfail, minlen=3, maxlen=12):
        """Проверяет данные для входа без проверки на совпадение."""
        if not isinstance(data, str):
            return AccountManager.FAILED_UNKNOWN

        data = data.strip()

        if len(data) < minlen or len(data) > maxlen:
            return lenfail

        if not AccountManager.check(data):
            return AccountManager.FAILED_UNSAFE_CHARACTERS

        return AccountManager.SUCCESSFUL

    @staticmethod
    def get_ban_status(data, account):
        """Возвращает статус бана аккаунта."""
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

    @staticmethod
    def login_account(nick, password):
        """Проверяет верные ли данные для входа."""
        nick_check = AccountManager.check_login_data(
            nick,
            AccountManager.FAILED_NICK_LENGTH
        )

        if nick_check != AccountManager.SUCCESSFUL:
            return nick_check

        pass_check = AccountManager.check_login_data(
            password,
            AccountManager.FAILED_PASSWORD_LENGTH
        )

        if pass_check != AccountManager.SUCCESSFUL:
            return pass_check

        nick = nick.strip()
        password = password.strip()

        data = read("data.json")

        if data is None:
            return AccountManager.FAILED_UNKNOWN

        for account in data["accounts"]:
            if account["nick"] == nick:
                if account["password"] == password:
                    if "console" in account:
                        return AccountManager.FAILED_CONSOLE

                    return AccountManager.get_ban_status(data, account)

                return AccountManager.FAILED_PASSWORD_NOT_MATCH

        return AccountManager.FAILED_NOT_FOUND

    @staticmethod
    def add_account(nick, password):
        """Создаёт новый аккаунт."""
        nick_check = AccountManager.check_login_data(
            nick,
            AccountManager.FAILED_NICK_LENGTH
        )

        if nick_check != AccountManager.SUCCESSFUL:
            return nick_check

        pass_check = AccountManager.check_login_data(
            password,
            AccountManager.FAILED_PASSWORD_LENGTH
        )

        if pass_check != AccountManager.SUCCESSFUL:
            return pass_check

        nick = nick.strip()
        password = password.strip()

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
