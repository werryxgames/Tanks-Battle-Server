"""Модуль управления аккаунтами."""
from datetime import datetime
from threading import Thread

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from mjson import append
from mjson import read
from mjson import write
from singleton import get_data


class Hasher:
    """Класс хеширования паролей."""

    def __init__(self):
        self.phasher = PasswordHasher()

    @staticmethod
    def rehash_password(nick, new_hash):
        """Устанавливает новый хеш в accounts.json."""
        return AccountManager.set_account(nick, "password", new_hash)

    def hash(self, password, nick):
        """Хеширует пароль."""
        result = self.phasher.hash(password + nick)
        return result

    def verify(self, hash_, password, nick):
        """Проверяет является ли hash_ хешом data."""
        try:
            self.phasher.verify(hash_, password + nick)
        except VerifyMismatchError:
            return False

        if self.phasher.check_needs_rehash(hash_):
            new_hash = self.hash(password, nick)
            self.rehash_password(nick, new_hash)

        return True


hasher = Hasher()


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
        for account in data:
            if account["nick"] == nick:
                return account

        return AccountManager.FAILED_NOT_FOUND

    @staticmethod
    def get_account(nick):
        """Возвращает аккаунт с логином nick."""
        data = read("accounts.json", [])

        return AccountManager.get_account_(nick, data)

    @staticmethod
    def del_account_key_(nick, key, data):
        """Удаляет key у аккаунта с логином nick из data."""
        acc = AccountManager.get_account_(nick, data)

        if acc == AccountManager.FAILED_NOT_FOUND:
            return acc

        try:
            del data[data.index(acc)][key]

            return data
        except KeyError:
            return AccountManager.FAILED_NOT_EXISTS

    @staticmethod
    def call_method(method, *args):
        """Вызывает method."""
        data = read("accounts.json", [])
        result = method(*args, data)

        if isinstance(result, int):
            return result

        if write("accounts.json", result):
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

        if acc == AccountManager.FAILED_NOT_FOUND:
            return acc

        del data[data.index(acc)]

        if write("accounts.json", data):
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

        if acc == AccountManager.FAILED_NOT_FOUND:
            return acc

        try:
            data[data.index(acc)][key] = value
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

        if len(data) < minlen or (maxlen != -1 and len(data) > maxlen):
            return lenfail

        if not AccountManager.check(data):
            return AccountManager.FAILED_UNSAFE_CHARACTERS

        return AccountManager.SUCCESSFUL

    @staticmethod
    def get_ban_status_(data, account):
        """Возвращает статус бана аккаунта account."""
        if "ban" in account:
            aban = account["ban"]

            if aban[0] != -1 and datetime.today().timestamp() \
                    > aban[0]:
                del data[data.index(account)]["ban"]
                return data

            if len(aban) > 1:
                return [
                    AccountManager.FAILED_BAN,
                    aban[0],
                    aban[1]
                ]

            return [AccountManager.FAILED_BAN, aban[0], None]

        return AccountManager.SUCCESSFUL

    @staticmethod
    def get_ban_status(data, account):
        """Возвращает статус бана аккаунта."""
        result = AccountManager.get_ban_status_(data, account)

        if isinstance(result, int):
            return result

        write("accounts.json", data)
        return AccountManager.SUCCESSFUL

    @staticmethod
    def login_account(nick, password, client):
        """Проверяет верные ли данные для входа синхронно."""
        nick_check = AccountManager.check_login_data(
            nick,
            AccountManager.FAILED_NICK_LENGTH
        )

        if nick_check != AccountManager.SUCCESSFUL:
            client.send(["login_fail", nick_check])
            return

        pass_check = AccountManager.check_login_data(
            password,
            AccountManager.FAILED_PASSWORD_LENGTH,
            6,
            -1
        )

        if pass_check != AccountManager.SUCCESSFUL:
            client.send(["login_fail", pass_check])
            return

        nick = nick.strip()
        password = password.strip()

        data = read("accounts.json", [])

        for account in data:
            if account["nick"] == nick:
                if hasher.verify(account["password"], password, nick):
                    if "console" in account:
                        client.send([
                            "login_fail",
                            AccountManager.FAILED_CONSOLE,
                            nick,
                            password
                        ])
                        client.console = client.CONSOLE(
                            client.sock,
                            client.addr,
                            client.rudp
                        )
                        return

                    ban_status = AccountManager.get_ban_status(data, account)

                    if isinstance(
                        ban_status,
                        list
                    ) and ban_status[0] == AccountManager.FAILED_BAN:
                        client.send(["login_fail", *ban_status])
                        return

                    if ban_status == AccountManager.SUCCESSFUL:
                        client.send(["login_successful", nick, password])
                        client.client.set_login_data(nick, password)
                        client.send_client = True
                        return

                    client.send(["login_fail", ban_status])

                client.send([
                    "login_fail",
                    AccountManager.FAILED_PASSWORD_NOT_MATCH
                ])
                return

        client.send(["login_fail", AccountManager.FAILED_NOT_FOUND])

    @staticmethod
    def login_account_async(nick, password, client):
        """Проверяет верные ли данные для входа асинхронно."""
        thread = Thread(
            target=AccountManager.login_account,
            args=(nick, password, client)
        )
        thread.start()

    @staticmethod
    def add_account(nick, password, client):
        """Создаёт новый аккаунт синхронно."""
        nick_check = AccountManager.check_login_data(
            nick,
            AccountManager.FAILED_NICK_LENGTH
        )

        if nick_check != AccountManager.SUCCESSFUL:
            client.send(["register_fail", nick_check])
            return

        pass_check = AccountManager.check_login_data(
            password,
            AccountManager.FAILED_PASSWORD_LENGTH,
            6,
            -1
        )

        if pass_check != AccountManager.SUCCESSFUL:
            client.send(["register_fail", pass_check])
            return

        nick = nick.strip()
        password = password.strip()

        data = read("accounts.json", [])

        for account in data:
            if account["nick"] == nick:
                client.send([
                    "register_fail",
                    AccountManager.FAILED_NICK_ALREADY_USED
                ])
                return

        hashed_password = hasher.hash(password, nick)

        acc = {
            "nick": nick,
            "password": hashed_password,
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

        if append("accounts.json", None, acc, []):
            client.send(["register_successful", nick, password])
            client.client.set_login_data(nick, password)
            client.send_client = True
            return

        client.send(["register_fail", AccountManager.FAILED_UNKNOWN])
        return

    @staticmethod
    def add_account_async(nick, password, client):
        """Создаёт новый аккаунт асинхронно."""
        thread = Thread(
            target=AccountManager.add_account,
            args=(nick, password, client)
        )
        thread.start()
